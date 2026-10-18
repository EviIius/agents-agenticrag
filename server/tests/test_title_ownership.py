"""User titles survive initial acceptance, including a rename during preparation."""

import asyncio
from typing import Any

import httpx
import pytest
from fastapi import FastAPI

from app.api import chats as chat_api
from app.runs.context import assemble
from tests.test_chat import finish


@pytest.mark.parametrize("auto_title", [False, True])
@pytest.mark.parametrize("during_preparation", [False, True])
async def test_first_send_preserves_user_title_and_search_index(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI],
    monkeypatch: pytest.MonkeyPatch,
    auto_title: bool,
    during_preparation: bool,
) -> None:
    app, client, runtime = chat_app
    await client.patch("/api/settings", json={"auto_title": auto_title})
    chat = (
        await client.post(
            "/api/chats",
            json={
                "connection_id": app.state.test_connection,
                "model_id": "fake-chat",
                "web_enabled": False,
            },
        )
    ).json()
    url = "/api/chats/" + chat["id"]
    title = "Synthetic user chosen title"
    entered, release = asyncio.Event(), asyncio.Event()
    original = assemble

    async def pause(*args: Any, **kwargs: Any) -> Any:
        assembled = await original(*args, **kwargs)
        entered.set()
        await release.wait()
        return assembled

    if during_preparation:
        monkeypatch.setattr(chat_api, "assemble", pause)
        pending = asyncio.create_task(
            client.post(url + "/messages", json={"content": "First synthetic question"})
        )
        try:
            await asyncio.wait_for(entered.wait(), 5)
            assert (await client.patch(url, json={"title": title})).status_code == 200
        finally:
            release.set()
        sent = await pending
    else:
        assert (await client.patch(url, json={"title": title})).status_code == 200
        sent = await client.post(url + "/messages", json={"content": "First synthetic question"})
    assert sent.status_code == 202, sent.text
    await finish(app, sent.json())
    detail = (await client.get(url)).json()
    assert detail["chat"]["title"] == title
    assert detail["chat"]["title_source"] == "user"
    matches = (await client.get("/api/chats", params={"q": title})).json()["items"]
    assert [item["id"] for item in matches] == [chat["id"]]
    assert (await client.get(url + "/export?format=md")).text.startswith("# " + title + "\n")
    captures = [body for body in runtime.state.captures if body.get("messages")]
    assert len(captures) == 1  # A user title must also suppress the utility-title call.
    assert captures[0]["options"] == {"num_ctx": 16384}
    assert "think" not in captures[0]


async def test_first_send_still_supplies_a_fallback_for_untitled_chat(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI],
) -> None:
    app, client, _ = chat_app
    chat = (
        await client.post(
            "/api/chats",
            json={"connection_id": app.state.test_connection, "model_id": "fake-chat"},
        )
    ).json()
    url = "/api/chats/" + chat["id"]
    original = "Synthetic first message title"
    first = await client.post(url + "/messages", json={"content": original})
    run = await finish(app, first.json())
    second = await client.post(
        url + "/messages", json={"content": "A different follow-up", "parent_id": run.message.id}
    )
    await finish(app, second.json())
    detail = (await client.get(url)).json()
    assert detail["chat"]["title"] == original
    assert detail["chat"]["title_source"] == "fallback"
