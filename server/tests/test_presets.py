import json
from typing import Any

import httpx
import pytest
from fastapi import FastAPI

from tests.test_chat import finish


async def test_preset_crud_validation_order_and_clear_default(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI],
) -> None:
    _, client, _ = chat_app
    assert (await client.get("/api/presets")).json() == []
    first = (await client.post("/api/presets", json={"name": "  Synthetic Focus  "})).json()
    assert first["name"] == "Synthetic Focus" and first["params"] == {}
    conflict = await client.post("/api/presets", json={"name": "synthetic focus"})
    assert conflict.status_code == 409 and conflict.json()["error"]["code"] == "preset_name_taken"
    for body in (
        {"name": " "},
        {"name": "A", "params": {"temperature": 3}},
        {"name": "A", "params": {"reasoning": "on"}},
        {"name": "A", "params": {"context_length": 4096}},
    ):
        assert (await client.post("/api/presets", json=body)).status_code == 422
    second = (await client.post("/api/presets", json={"name": "Synthetic Second"})).json()
    assert (
        await client.patch(f"/api/presets/{second['id']}", json={"position": 0})
    ).status_code == 200
    assert (
        await client.patch(f"/api/presets/{first['id']}", json={"position": 1})
    ).status_code == 200
    assert [p["id"] for p in (await client.get("/api/presets")).json()] == [
        second["id"],
        first["id"],
    ]
    assert (
        await client.patch(f"/api/presets/{first['id']}", json={"name": second["name"]})
    ).status_code == 409
    for field in ("name", "position"):
        assert (
            await client.patch(f"/api/presets/{first['id']}", json={field: None})
        ).status_code == 422
    assert (
        await client.patch("/api/settings", json={"default_preset_id": "missing"})
    ).status_code == 422
    assert (
        await client.patch("/api/settings", json={"default_preset_id": first["id"]})
    ).status_code == 200
    assert (await client.delete(f"/api/presets/{first['id']}")).status_code == 204
    assert (await client.get("/api/settings")).json()["default_preset_id"] is None
    assert (
        await client.patch(f"/api/presets/{first['id']}", json={"name": "Missing"})
    ).status_code == 404
    assert (await client.delete(f"/api/presets/{first['id']}")).status_code == 404


async def test_presets_copy_default_explicit_none_and_do_not_change_existing_chats(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI],
) -> None:
    app, client, _ = chat_app
    preset = (
        await client.post(
            "/api/presets",
            json={
                "name": "Synthetic Capture",
                "system_prompt": "Invented preset prompt.",
                "params": {"temperature": 0.65, "top_k": 27, "seed": 42, "top_p": None},
            },
        )
    ).json()
    body = {"connection_id": app.state.test_connection, "model_id": "fake-chat"}
    await client.patch("/api/settings", json={"default_preset_id": preset["id"]})
    default = (await client.post("/api/chats", json=body)).json()
    explicit = (await client.post("/api/chats", json={**body, "preset_id": preset["id"]})).json()
    none = (await client.post("/api/chats", json={**body, "preset_id": None})).json()
    for chat in (default, explicit):
        assert chat["params"] == {"temperature": 0.65, "top_k": 27, "seed": 42}
        assert chat["system_prompt"] == "Invented preset prompt."
    assert none["params"] == {} and none["system_prompt"] is None
    assert (
        await client.post("/api/chats", json={**body, "preset_id": "missing"})
    ).status_code == 404
    before = json.dumps(default, sort_keys=True)
    await client.patch(
        f"/api/presets/{preset['id']}", json={"params": {"max_tokens": 100}, "system_prompt": None}
    )
    await client.delete(f"/api/presets/{preset['id']}")
    assert (
        json.dumps((await client.get(f"/api/chats/{default['id']}")).json()["chat"], sort_keys=True)
        == before
    )


@pytest.mark.parametrize(
    "params", [{}, {"temperature": 0.7, "top_p": 0.9, "top_k": 17, "max_tokens": 96, "seed": -4}]
)
async def test_preset_runtime_payload_exactly_matches_stored_values(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI],
    params: dict[str, Any],
) -> None:
    app, client, runtime = chat_app
    preset = (
        await client.post("/api/presets", json={"name": "Synthetic Payload", "params": params})
    ).json()
    chat = (
        await client.post(
            "/api/chats",
            json={
                "connection_id": app.state.test_connection,
                "model_id": "fake-chat",
                "preset_id": preset["id"],
            },
        )
    ).json()
    response = await client.post(
        f"/api/chats/{chat['id']}/messages", json={"content": "Synthetic preset payload"}
    )
    assert response.status_code == 202
    await finish(app, response.json())
    capture = next(body for body in reversed(runtime.state.captures) if body.get("messages"))
    expected = {
        ("num_predict" if key == "max_tokens" else key): value for key, value in params.items()
    }
    assert capture["options"] == {**expected, "num_ctx": 16384}
    assert "think" not in capture and "tools" not in capture


async def test_preset_overrides_explicit_keys_and_inherits_saved_model_defaults(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI],
) -> None:
    app, client, runtime = chat_app
    await client.put(
        "/api/models/prefs",
        json={
            "connection_id": app.state.test_connection,
            "model_id": "fake-chat",
            "params": {"temperature": 0.45, "top_k": 77},
        },
    )
    preset = (
        await client.post(
            "/api/presets",
            json={
                "name": "Synthetic Precedence",
                "params": {"top_k": 17},
            },
        )
    ).json()
    chat = (
        await client.post(
            "/api/chats",
            json={
                "connection_id": app.state.test_connection,
                "model_id": "fake-chat",
                "preset_id": preset["id"],
            },
        )
    ).json()
    assert chat["params"] == {"top_k": 17}
    response = await client.post(
        f"/api/chats/{chat['id']}/messages", json={"content": "Synthetic precedence request"}
    )
    await finish(app, response.json())
    capture = next(body for body in reversed(runtime.state.captures) if body.get("messages"))
    assert capture["options"] == {"temperature": 0.45, "top_k": 17, "num_ctx": 16384}
