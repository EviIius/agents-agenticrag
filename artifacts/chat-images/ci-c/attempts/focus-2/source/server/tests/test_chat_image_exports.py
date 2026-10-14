"""CI-C exports retain text metadata and selected image branches without bytes."""

import json
from typing import Any
from uuid import uuid4

import httpx
from fastapi import FastAPI

from tests.test_chat import chat_app as chat_app
from tests.test_chat_images import inputs, new
from tests.test_images import FakeEngine


async def test_image_iteration_lineage_and_export(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI],
) -> None:
    app, client, runtime = chat_app
    engine = FakeEngine()
    app.state.images.engine = engine
    cid = await new(client)
    first = (await client.post(f"/api/chats/{cid}/images", json=inputs(2))).json()
    source = first["assistant"]["images"][1]
    more = (
        await client.post(f"/api/chats/{cid}/images", json=inputs(1, source_job_id=source["id"]))
    ).json()
    refined_prompt = "Synthetic cobalt harbor with golden shapes"
    refined = (
        await client.post(
            f"/api/chats/{cid}/images",
            json=inputs(1, prompt=refined_prompt, source_job_id=source["id"]),
        )
    ).json()
    for response in (more, refined):
        assert response["assistant"]["images"][0]["parent_id"] == source["id"]
        stored = await app.state.store.one(
            "SELECT params_json FROM messages WHERE id=?", (response["assistant"]["id"],)
        )
        assert stored and json.loads(stored["params_json"])["source_job_id"] == source["id"]
    key = uuid4().hex
    retry = (
        await client.post(
            f"/api/chats/{cid}/messages/{refined['assistant']['id']}/images/retry",
            json={"request_key": key, "seeds": [77]},
        )
    ).json()
    assert retry["assistant"]["images"][0]["parent_id"] == source["id"]
    data: dict[str, Any] = (await client.get(f"/api/chats/{cid}/export?format=json")).json()
    exported = data["messages"]
    assert len(exported) == 6
    assert exported[-2]["kind"] == "image" and exported[-2]["prompt"] == refined_prompt
    last = exported[-1]
    assert last["prompt"] == refined_prompt and last["seeds"] == [77]
    assert last["job_ids"] == [retry["assistant"]["images"][0]["id"]]
    assert not any(row["id"] == refined["assistant"]["id"] for row in exported)
    md = (await client.get(f"/api/chats/{cid}/export?format=md")).text
    for i, job in enumerate(first["assistant"]["images"], 1):
        assert f"Image {i}: Atelier-image-{job['id'][:8]}.png · seed {job['seed']}" in md
    assert refined_prompt in md and "seed 77" in md
    assert "data:image" not in md and "data:image" not in str(data)
    assert not [body for body in runtime.state.captures if body.get("messages")]
    engine.release.set()
