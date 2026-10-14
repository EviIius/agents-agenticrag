"""Synthetic chat turns: atomic acceptance, ancestry and exact text context."""

import asyncio
import json
from typing import Any
from uuid import uuid4

import httpx
import pytest
from fastapi import FastAPI

from app.api.chat_images import title_from_prompt
from app.db import messages, settings
from app.db.chats import chat
from app.runs.context import assemble
from tests.test_chat import chat_app as chat_app
from tests.test_chat import finish, start
from tests.test_images import FakeEngine


def inputs(count: int = 2, **changes: Any) -> dict[str, Any]:
    return {
        "request_key": uuid4().hex,
        "prompt": "Synthetic cobalt harbor",
        "count": count,
        "seeds": list(range(101, 101 + count)),
        **changes,
    }


async def new(client: httpx.AsyncClient) -> str:
    return str((await client.post("/api/chats", json={})).json()["id"])


async def test_atomic_idempotent_history_and_origins(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI],
) -> None:
    app, client, runtime = chat_app
    engine = FakeEngine()
    app.state.images.engine = engine
    cid, body = await new(client), inputs(3)
    results = await asyncio.gather(
        *(client.post(f"/api/chats/{cid}/images", json=body) for _ in range(3))
    )
    assert all(r.status_code == 202 for r in results)
    ids = [r.json()["assistant"]["id"] for r in results]
    assert len(set(ids)) == 1
    detail = (await client.get(f"/api/chats/{cid}")).json()
    assert len(detail["messages"]) == 2 and detail["chat"]["current_leaf_id"] == ids[0]
    assert detail["chat"]["title"] == body["prompt"]
    assistant = next(m for m in detail["messages"] if m["role"] == "assistant")
    assert assistant["status"] == "complete" and assistant["kind"] == "image"
    assert [j["seed"] for j in assistant["images"]] == body["seeds"]
    assert all(j["origin"]["message_id"] == ids[0] for j in assistant["images"])
    assert len(await app.state.store.rows("SELECT id FROM image_jobs")) == 3
    conflict = await client.post(f"/api/chats/{cid}/images", json={**body, "seeds": [4, 5, 6]})
    assert conflict.status_code == 409
    cross = await client.post(f"/api/chats/{await new(client)}/images", json=body)
    assert cross.status_code == 409
    engine.release.set()
    await asyncio.gather(*list(app.state.images.tasks.values()))
    assert engine.calls == 3
    assert not [body for body in runtime.state.captures if body.get("messages")]
    await client.delete(f"/api/chats/{cid}")
    assert not await app.state.store.rows("SELECT * FROM message_images")
    gallery = (await client.get("/api/images/jobs")).json()
    assert all(j["image_bytes"] > 0 and j["origin"]["deleted"] for j in gallery)
    assert (await client.post(f"/api/chats/{cid}/images", json=body)).status_code == 404


async def test_retry_branches_and_cancel_only_its_jobs(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI],
) -> None:
    app, client, _ = chat_app
    app.state.images.engine = FakeEngine()
    cid = await new(client)
    first = (await client.post(f"/api/chats/{cid}/images", json=inputs())).json()
    old = first["assistant"]
    retry_body = {"request_key": uuid4().hex, "seeds": [201, 202]}
    route = f"/api/chats/{cid}/messages/{old['id']}/images/retry"
    retry = (await client.post(route, json=retry_body)).json()["assistant"]
    assert retry["parent_id"] == old["parent_id"]
    assert [j["seed"] for j in retry["images"]] == [201, 202]
    assert (await client.post(route, json=retry_body)).json()["assistant"]["id"] == retry["id"]
    cancel = await client.post(f"/api/chats/{cid}/messages/{retry['id']}/images/cancel")
    assert all(j["state"] == "cancelled" for j in cancel.json()["assistant"]["images"])
    assert all(
        [
            (await app.state.images.get(j["id"])).state in {"queued", "preparing", "running"}
            for j in old["images"]
        ]
    )
    assert (
        await client.post(route, json={"request_key": uuid4().hex, "seeds": [1]})
    ).status_code == 422
    assert (await client.post(f"/api/messages/{old['id']}/regenerate", json={})).status_code == 422
    assert (
        await client.post(f"/api/chats/{await new(client)}/messages/{old['id']}/images/cancel")
    ).status_code == 404


async def test_failed_atomic_commit_discards_all_manifests(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI], monkeypatch: pytest.MonkeyPatch
) -> None:
    app, client, _ = chat_app
    app.state.images.engine = FakeEngine()
    cid = await new(client)
    batch = app.state.store.batch

    async def fail(rows: Any) -> None:
        if any("INSERT INTO chat_image_requests" in sql for sql, _ in rows):
            # A late FK failure proves even the preceding message/job rows roll back.
            rows = [*rows, ("INSERT INTO message_images VALUES('missing',0,'missing')", ())]
        await batch(rows)

    monkeypatch.setattr(app.state.store, "batch", fail)
    with pytest.raises(Exception, match="FOREIGN KEY"):
        await client.post(f"/api/chats/{cid}/images", json=inputs(3))
    for table in (
        "messages",
        "image_jobs",
        "image_steps",
        "message_images",
        "chat_image_requests",
        "chat_image_origins",
    ):
        assert not await app.state.store.rows(f"SELECT * FROM {table}")
    assert not list(app.state.images.folder.iterdir()) and not app.state.images.tasks


async def test_image_turns_absent_from_exact_context(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI],
) -> None:
    app, client, runtime = chat_app
    app.state.images.engine = FakeEngine()
    first = await start(client, "Synthetic text before", "fake-chat")
    await finish(app, first)
    cid = first["assistant_message"]["chat_id"]
    image = (await client.post(f"/api/chats/{cid}/images", json=inputs(1))).json()
    second = await client.post(
        f"/api/chats/{cid}/messages",
        json={"content": "Synthetic text after", "parent_id": image["assistant"]["id"]},
    )
    assert second.status_code == 202
    await finish(app, second.json())
    all_messages = await messages.list_messages(app.state.store, cid)
    model = await app.state.registry.resolve(app.state.test_connection, "fake-chat")
    args = (app.state.store, app.state.config.data_dir, await chat(app.state.store, cid))
    values = await settings.get(app.state.store)
    leaf = second.json()["assistant_message"]["id"]
    mixed = await assemble(*args, all_messages, leaf, model, {}, values)
    ordinary = [m for m in all_messages if m.kind == "text"]
    ordinary[-2].parent_id = first["assistant_message"]["id"]
    expected = await assemble(*args, ordinary, leaf, model, {}, values)
    assert mixed == expected
    capture = runtime.state.captures[-1]
    assert capture["messages"] == [
        {"role": m.role, "content": m.content} for m in mixed.messages[:-1]
    ]
    assert capture["options"] == {"num_ctx": 16384}
    assert [m.content for m in mixed.messages if m.role == "user"] == [
        "Synthetic text before",
        "Synthetic text after",
    ]
    assert not any("cobalt harbor" in m.content for m in mixed.messages)
    row = await app.state.store.one(
        "SELECT params_json FROM messages WHERE id=?", (image["assistant"]["id"],)
    )
    assert json.loads(row["params_json"])["seeds"] == [101]


async def test_active_text_guard_validation_and_prompt_title(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI],
) -> None:
    app, client, _ = chat_app
    app.state.images.engine = FakeEngine()
    first = await start(client, "#slow", "fake-chat")
    cid = first["assistant_message"]["chat_id"]
    assert (await client.post(f"/api/chats/{cid}/images", json=inputs())).status_code == 409
    assert not await app.state.store.rows("SELECT * FROM image_jobs")
    await finish(app, first)
    for changes in (
        {"seeds": [1]},
        {"seeds": [True, 2]},
        {"count": 4},
        {"prompt": " "},
        {"seeds": [-1, 2]},
        {"parent_id": uuid4().hex},
    ):
        assert (
            await client.post(f"/api/chats/{cid}/images", json=inputs(**changes))
        ).status_code == 422
    assert title_from_prompt("A" * 60) == "A" * 48
    assert (
        len(
            title_from_prompt(
                "Synthetic harbor with several descriptive words beyond its title allowance"
            )
        )
        <= 48
    )
    assert title_from_prompt("  Synthetic\n harbor ") == "Synthetic harbor"
