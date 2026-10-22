"""Selection acceptance/replay/retry/backup; fake inference, durable real API."""

import asyncio
import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

import httpx
import pytest
from fastapi import FastAPI

from app.backup import Backups
from app.images.backup import restore
from tests.test_chat import chat_app as chat_app
from tests.test_chat_images import inputs, new
from tests.test_photo_references import setup

SELECTION = {"version": 1, "strokes": [{"radius": 0.08, "points": [[0.3, 0.2], [0.4, 0.3]]}]}


async def test_selection_is_owned_atomic_replayable_and_retried_unchanged(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI],
) -> None:
    app, client, runtime = chat_app
    cid, ref = await setup(app, client)
    body = inputs(1, reference_id=ref["id"], selection=SELECTION)
    response = await client.post(f"/api/chats/{cid}/images", json=body)
    assert response.status_code == 202, response.text
    accepted = response.json()
    image = accepted["assistant"]["images"][0]
    assert image["selection"] == SELECTION
    assert [image["width"], image["height"]] == [1024, 1024]
    manifest = json.loads((app.state.images.path(image["id"]) / "input.json").read_text())
    assert manifest["selection"] == SELECTION
    replay = await client.post(f"/api/chats/{cid}/images", json=body)
    assert replay.json()["assistant"]["id"] == accepted["assistant"]["id"]
    changed = {
        **body,
        "selection": {"version": 1, "strokes": [{"radius": 0.1, "points": [[0.5, 0.5]]}]},
    }
    assert (await client.post(f"/api/chats/{cid}/images", json=changed)).status_code == 409
    app.state.images.engine.release.set()
    await asyncio.gather(*list(app.state.images.tasks.values()))
    assert (await app.state.images.get(image["id"])).state == "complete"
    assert (await app.state.images.storage()).native_bytes > 0
    retried = await client.post(
        f"/api/chats/{cid}/messages/{accepted['assistant']['id']}/images/retry",
        json={"request_key": uuid4().hex, "seeds": [52]},
    )
    assert retried.status_code == 202
    assert retried.json()["assistant"]["images"][0]["selection"] == SELECTION
    await asyncio.gather(*list(app.state.images.tasks.values()))
    assert not [c for c in runtime.state.captures if c.get("messages")]
    other = await new(client)
    assert (
        await client.post(
            f"/api/chats/{other}/images",
            json=inputs(1, reference_id=ref["id"], selection=SELECTION),
        )
    ).status_code == 404


@pytest.mark.parametrize(
    "change",
    [
        {"reference_id": None},
        {"selection": {"version": 1, "strokes": []}},
        {"selection": {"version": 1, "strokes": [{"radius": 0.1, "points": [[2, 0.5]]}]}},
        {"selection": {"version": 1, "strokes": [{"radius": 0.1, "points": [[0.5, 0.5]] * 129}]}},
        {
            "selection": {
                "version": 1,
                "strokes": [{"radius": 0.1, "points": [[0.5, 0.5]] * 128}] * 5,
            }
        },
    ],
)
async def test_invalid_selection_never_schedules(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI], change: dict[str, Any]
) -> None:
    app, client, _ = chat_app
    cid, ref = await setup(app, client)
    result = await client.post(
        f"/api/chats/{cid}/images",
        json={**inputs(1, reference_id=ref["id"], selection=SELECTION), **change},
    )
    assert result.status_code == 422
    assert not app.state.images.tasks and not await app.state.store.rows("SELECT * FROM image_jobs")


async def test_backup_round_trip_retains_mask_native_and_composite(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI], tmp_path: Path
) -> None:
    app, client, _ = chat_app
    cid, ref = await setup(app, client)
    app.state.images.engine.release.set()
    response = await client.post(
        f"/api/chats/{cid}/images", json=inputs(1, reference_id=ref["id"], selection=SELECTION)
    )
    assert response.status_code == 202
    image = response.json()["assistant"]["images"][0]
    await asyncio.gather(*list(app.state.images.tasks.values()))
    images = app.state.images
    backups = Backups(
        images.store, images.data, images=images, clock=lambda: datetime(2026, 10, 21, tzinfo=UTC)
    )
    assert (await backups.make()).warning is None
    database = next(backups.folder.glob("auto-20261021-0000-*.db"))
    restored = tmp_path / "restored"
    assert restore(database, restored) == 1
    for name in ("native.png", "image.png", "export.png", "metadata.json"):
        assert (restored / "images" / image["id"] / "output" / name).read_bytes() == (
            images.path(image["id"]) / "output" / name
        ).read_bytes()
    with sqlite3.connect(restored / "workbench.db") as db:
        manifest = json.loads(db.execute("SELECT input_json FROM image_jobs").fetchone()[0])
    assert manifest["selection"] == SELECTION
    assert (await images.storage()).native_bytes > 0
    await images.remove(image["id"])
    assert (await images.storage()).native_bytes == 0
