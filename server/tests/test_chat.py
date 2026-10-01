import asyncio
import json
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any

import httpx
import pytest
import pytest_asyncio
from fastapi import FastAPI

from app.config import Settings
from app.main import create_app
from app.providers.base import ChatRequest, Finish, ProviderMessage, ReasoningDelta, TextDelta
from app.providers.ollama import Ollama, runtime_error
from app.providers.thinktags import ThinkSplitter
from tests.fake_runtime import create_fake_runtime


@pytest_asyncio.fixture
async def chat_app(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> AsyncIterator[tuple[FastAPI, httpx.AsyncClient, FastAPI]]:
    runtime = create_fake_runtime()
    original = Ollama.__init__

    def init(
        self: Ollama, connection_id: str, base_url: str, keep_alive: str = "30m", **kwargs: Any
    ) -> None:
        original(
            self,
            connection_id,
            base_url,
            keep_alive,
            client=httpx.AsyncClient(
                transport=httpx.ASGITransport(app=runtime), base_url="http://fake"
            ),
            **kwargs,
        )

    monkeypatch.setattr(Ollama, "__init__", init)
    app = create_app(Settings(data_dir=tmp_path, dev=True))
    async with (
        app.router.lifespan_context(app),
        httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://localhost"
        ) as client,
    ):
        conn = (await client.post("/api/connections", json={})).json()
        await client.patch("/api/settings", json={"auto_title": False})
        app.state.test_connection = conn["id"]
        yield app, client, runtime


async def start(
    client: httpx.AsyncClient, content: str = "#think", model: str = "fake-reasoning"
) -> dict[str, Any]:
    conn = (await client.get("/api/connections")).json()[0]["id"]
    chat = (await client.post("/api/chats", json={"connection_id": conn, "model_id": model})).json()
    response = await client.post(
        "/api/chats/" + chat["id"] + "/messages", json={"content": content, "parent_id": None}
    )
    assert response.status_code == 202, response.text
    return dict(response.json())


async def finish(app: FastAPI, response: dict[str, Any]) -> Any:
    run = app.state.runs.runs[response["run_id"]]
    await run.task
    return run


async def test_live_stream_history_reasoning_defaults_and_ftS(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI],
) -> None:
    app, client, runtime = chat_app
    response = await start(client)
    run = await finish(app, response)
    assert run.message.reasoning and run.message.status == "complete"
    assert run.message.stats.completion_tokens > 0
    content = "A follow-up"
    follow = await client.post(
        "/api/chats/" + run.message.chat_id + "/messages",
        json={"content": content, "parent_id": run.message.id},
    )
    await finish(app, follow.json())
    captures = [body for body in runtime.state.captures if body.get("messages")]
    assert captures[-1]["messages"][-2]["content"] == run.message.content
    assert "reasoning" not in json.dumps(captures[-1]["messages"])
    assert "thinking" not in json.dumps(captures[-1]["messages"])
    assert all(set(body.get("options", {})) == {"num_ctx"} for body in captures)
    assert all("think" not in body for body in captures)
    sse = await client.get(
        "/api/runs/" + response["run_id"] + "/events", headers={"last-event-id": "1"}
    )
    assert "id: 1\r\n" not in sse.text
    assert "event: message.done" in sse.text and "event: run.closed" in sse.text
    history = (await client.get("/api/chats?q=follow")).json()
    assert history["items"][0]["id"] == run.message.chat_id
    assert (await client.get("/api/chats/" + run.message.chat_id + "/export?format=json")).json()[
        "messages"
    ][-1]["content"]


async def test_branching_context_settings_and_preferences(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI],
) -> None:
    app, client, runtime = chat_app
    response = await start(client, "Hello", "fake-chat")
    run = await finish(app, response)
    chat_id = run.message.chat_id
    params = {"temperature": 0.7, "top_p": 0.8, "top_k": 20, "max_tokens": 100, "seed": 42}
    assert (
        await client.patch(
            "/api/chats/" + chat_id, json={"params": params, "system_prompt": "Custom instructions"}
        )
    ).status_code == 200
    regen = (await client.post("/api/messages/" + run.message.id + "/regenerate", json={})).json()
    sibling = await finish(app, regen)
    assert sibling.message.parent_id == run.message.parent_id
    capture = runtime.state.captures[-1]
    assert capture["options"] == {
        **{k: v for k, v in params.items() if k != "max_tokens"},
        "num_predict": 100,
        "num_ctx": 16384,
    }
    assert capture["messages"][0]["content"].startswith("Custom instructions\n\nCurrent date: ")
    assert (
        await client.patch(
            "/api/chats/" + chat_id,
            json={"current_leaf_id": run.message.id, "title": "A renamed chat", "pinned": True},
        )
    ).status_code == 200
    detail = (await client.get("/api/chats/" + chat_id)).json()
    assert len(detail["messages"]) == 3 and detail["chat"]["current_leaf_id"] == run.message.id
    context = (await client.get("/api/chats/" + chat_id + "/context")).json()
    assert context["context_length"] == 16384
    hidden = await app.state.store.one(
        "SELECT hidden FROM model_prefs WHERE model_id=?", ("llama3.3:70b-instruct-q4_K_M",)
    )
    assert hidden["hidden"] == 1
    assert (await client.delete("/api/chats/" + chat_id)).status_code == 204
    assert (await client.get("/api/chats/" + chat_id)).status_code == 404


async def test_cancel_queue_tab_disconnect_and_restart(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI],
) -> None:
    app, client, runtime = chat_app
    one = await start(client, "#long:100 #slow:10", "fake-chat")
    await asyncio.sleep(0.04)
    two = await start(client, "#long:100 #slow:10", "fake-chat")
    await asyncio.sleep(0.04)
    waiting = app.state.runs.runs[two["run_id"]]
    assert waiting.events[0].type == "run.queued"
    active = (await client.get("/api/runs/active")).json()
    assert len(active) == 2
    await client.post("/api/runs/" + one["run_id"] + "/cancel")
    run = app.state.runs.runs[one["run_id"]]
    assert run.message.status == "stopped" and runtime.state.disconnected > 0
    await client.post("/api/runs/" + two["run_id"] + "/cancel")
    await app.state.store.execute(
        "UPDATE messages SET status='streaming' WHERE id=?", (run.message.id,)
    )
    await app.state.runs.recover()
    message = (await client.get("/api/chats/" + run.message.chat_id)).json()["messages"][-1]
    assert message["status"] == "interrupted" and message["error"]["code"] == "interrupted"


async def test_attachments_images_and_preflight_overflow(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI],
) -> None:
    app, client, runtime = chat_app
    uploaded = (
        await client.post(
            "/api/attachments", files={"file": ("notes.md", b"Actual file content", "text/plain")}
        )
    ).json()
    response = await start(client, "First question", "fake-chat")
    run = await finish(app, response)
    sent = await client.post(
        "/api/chats/" + run.message.chat_id + "/messages",
        json={
            "content": "Read this",
            "parent_id": run.message.id,
            "attachment_ids": [uploaded["id"]],
        },
    )
    await finish(app, sent.json())
    assert (
        '<file name="notes.md">Actual file content</file>'
        in runtime.state.captures[-1]["messages"][-1]["content"]
    )
    assert (
        await client.get("/api/attachments/" + uploaded["id"])
    ).content == b"Actual file content"
    assert (
        await client.post("/api/attachments", files={"file": ("a.pdf", b"pdf", "application/pdf")})
    ).status_code == 422
    count = len(runtime.state.captures)
    overflow = await client.post(
        "/api/chats/" + run.message.chat_id + "/messages",
        json={"content": "X" * 100000, "parent_id": run.message.id},
    )
    assert overflow.status_code == 422 and overflow.json()["error"]["code"] == "context_overflow"
    assert len(runtime.state.captures) == count


@pytest.mark.parametrize(
    ("chunks", "thought", "text"),
    [
        (["<think>a", "b</think>", "\n\nHi"], "ab", "Hi"),
        (["<thi", "nk>x</th", "ink>y"], "x", "y"),
        (["  <think>", "r</think>t"], "r", "t"),
        (["Hello <think>no"], "", "Hello <think>no"),
        (["<think>unterminated"], "unterminated", ""),
        (["<", "b>bold</b>"], "", "<b>bold</b>"),
        (["\n", "<think>a</think>b"], "a", "b"),
        (["<think>a</think>", "", "\n", "Hi\n\nthere"], "a", "Hi\n\nthere"),
    ],
)
def test_think_vectors(chunks: list[str], thought: str, text: str) -> None:
    splitter = ThinkSplitter()
    events = []
    for chunk in chunks:
        events.extend(splitter.feed(chunk))
    events.extend(splitter.end())
    assert "".join(e.text for e in events if isinstance(e, ReasoningDelta)) == thought
    assert "".join(e.text for e in events if isinstance(e, TextDelta)) == text


async def test_ollama_adapter_replays_real_fixtures() -> None:
    root = Path(__file__).parent / "fixtures/providers"
    for name in ["plain", "reasoning", "vision", "length", "unknown"]:
        meta = json.loads((root / f"ollama-{name}.request.json").read_text())
        raw = (root / meta["raw"]).read_bytes()
        async with httpx.AsyncClient(
            transport=httpx.MockTransport(
                lambda request, meta=meta, raw=raw: httpx.Response(meta["status"], content=raw)
            )
        ) as client:
            adapter = Ollama("recorded", "http://ollama", client=client)
            events = [
                e
                async for e in adapter.stream(
                    ChatRequest(
                        meta["request"]["body"]["model"], [ProviderMessage("user", "fixture")]
                    )
                )
            ]
        assert isinstance(events[-1], Finish)
        if name == "unknown":
            assert events[-1].reason == "error" and "model_not_found" in (events[-1].detail or "")
        else:
            assert events[-1].reason == ("length" if name == "length" else "stop")
            assert any(isinstance(e, TextDelta) for e in events)
        if name in ("reasoning", "vision"):
            assert any(isinstance(e, ReasoningDelta) for e in events)


@pytest.mark.parametrize(
    ("status", "detail", "code"),
    [
        (404, "missing", "model_not_found"),
        (400, "model not found", "model_not_found"),
        (500, "out of memory", "model_load_failed"),
        (400, "context too long", "context_overflow"),
        (500, "unknown", "provider_error"),
    ],
)
def test_error_mapping(status: int, detail: str, code: str) -> None:
    assert runtime_error(status, detail).code == code


async def test_auto_title_keeps_user_renames_and_errors_are_not_content(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI],
) -> None:
    app, client, runtime = chat_app
    await client.patch("/api/settings", json={"auto_title": True})
    response = await start(client, "Please greet me.", "fake-chat")
    run = await finish(app, response)
    detail = (await client.get("/api/chats/" + run.message.chat_id)).json()
    assert detail["chat"]["title_source"] == "auto"
    assert runtime.state.captures[-1]["options"]["temperature"] == 0.2
    assert runtime.state.captures[-1]["options"]["num_predict"] == 24
    error = await start(client, "#error:stream", "fake-chat")
    failed = await finish(app, error)
    assert failed.message.status == "error" and failed.message.error.code == "provider_error"
    assert "Fake mid-stream error" not in failed.message.content
    await client.patch("/api/chats/" + failed.message.chat_id, json={"title": "My title"})
    assert (await client.get("/api/chats/" + failed.message.chat_id)).json()["chat"][
        "title"
    ] == "My title"


async def test_context_drops_history_and_handles_old_images(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI],
) -> None:
    from app.runs.context import assemble
    from app.schemas import Attachment, Chat, Message, ModelInfo

    app, client, _ = chat_app
    conn = app.state.test_connection
    data_dir = app.state.config.data_dir
    (data_dir / "test.png").write_bytes(b"image")
    await app.state.store.execute(
        "INSERT INTO attachments(id,kind,filename,mime_type,bytes,path,created_at) "
        "VALUES ('img','image','test.png','image/png',5,'test.png','now')"
    )
    history = []
    parent = None
    for i in range(8):
        message = Message(
            id=str(i),
            chat_id="chat",
            parent_id=parent,
            role="user" if i % 2 == 0 else "assistant",
            content="History " * 400,
            reasoning="never included",
            status="complete",
            created_at=str(i),
            attachments=[
                Attachment(
                    id="img", kind="image", filename="test.png", mime_type="image/png", bytes=5
                )
            ]
            if i == 0
            else [],
        )
        history.append(message)
        parent = message.id
    history[-1].content = "Recent answer [2]"
    chat = Chat(id="chat", title="test", created_at="now", updated_at="now")
    model = ModelInfo(
        connection_id=conn,
        model_id="fake-vision",
        display_name="fake",
        vision=True,
        context_length=4096,
    )
    context = await assemble(
        app.state.store,
        data_dir,
        chat,
        history,
        parent,
        model,
        {},
        {"default_system_prompt": "Be helpful", "include_current_date": False},
    )
    assert context.dropped > 0 and context.used_tokens < 4096
    assert "[2]" not in context.messages[-1].content
    model.context_length = 32768
    full = await assemble(
        app.state.store,
        data_dir,
        chat,
        history,
        parent,
        model,
        {},
        {"default_system_prompt": "Be helpful", "include_current_date": False},
    )
    assert "[image omitted]" in full.messages[1].content and not full.messages[1].images


async def test_completed_answer_allows_followup_while_title_is_pending(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI], monkeypatch: pytest.MonkeyPatch
) -> None:
    from app.runs import titles

    app, client, _ = chat_app
    started = asyncio.Event()
    released = asyncio.Event()

    async def slow_title(manager: Any, run: Any, model: Any) -> None:
        if not started.is_set():
            started.set()
            await released.wait()

    monkeypatch.setattr(titles, "title", slow_title)
    response = await start(client, "First answer", "fake-chat")
    await asyncio.wait_for(started.wait(), 2)
    first = app.state.runs.runs[response["run_id"]]
    assert first.message.status == "complete" and not first.closed
    assert (await client.get("/api/runs/active")).json() == []
    followup = await client.post(
        "/api/chats/" + first.message.chat_id + "/messages",
        json={"content": "Follow up", "parent_id": first.message.id},
    )
    assert followup.status_code == 202
    released.set()
    await finish(app, followup.json())
    await first.task


async def test_export_all_and_confirmed_delete_keep_settings_and_cancel_runs(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI],
) -> None:
    app, client, runtime = chat_app
    first = await start(client, "Original", "fake-chat")
    run = await finish(app, first)
    sibling = (await client.post("/api/messages/" + run.message.id + "/regenerate", json={})).json()
    await finish(app, sibling)
    attachment = (
        await client.post("/api/attachments", files={"file": ("notes.md", b"Private notes")})
    ).json()
    sent = (
        await client.post(
            "/api/chats/" + run.message.chat_id + "/messages",
            json={
                "content": "Read these notes",
                "parent_id": run.message.id,
                "attachment_ids": [attachment["id"]],
            },
        )
    ).json()
    await finish(app, sent)
    row = await app.state.store.one("SELECT path FROM attachments WHERE id=?", (attachment["id"],))
    file = app.state.config.data_dir / row["path"]
    assert file.exists()
    second = await start(client, "#long:100 #slow:50", "fake-chat")
    running = app.state.runs.runs[second["run_id"]]
    await asyncio.sleep(0.06)
    export = await client.get("/api/chats/export")
    assert export.status_code == 200 and "attachment" in export.headers["content-disposition"]
    chats = export.json()["chats"]
    assert len(chats) == 2
    tree = next(c for c in chats if c["chat"]["id"] == run.message.chat_id)
    assert len(tree["messages"]) == 5 and len(tree["messages"][-2]["attachments"]) == 1
    assert (
        await client.request("DELETE", "/api/chats", json={"confirmation": "delete"})
    ).status_code == 422
    assert len((await client.get("/api/chats")).json()["items"]) == 2
    assert (
        await client.request("DELETE", "/api/chats", json={"confirmation": "DELETE"})
    ).status_code == 204
    assert running.closed and not app.state.runs.runs
    assert (await client.get("/api/runs/" + second["run_id"] + "/events")).status_code == 404
    assert not file.exists()
    assert (await client.get("/api/chats")).json()["items"] == []
    assert not await app.state.store.rows("SELECT * FROM chat_search")
    assert len((await client.get("/api/connections")).json()) == 1
    assert (await client.get("/api/settings")).json()["auto_title"] is False
    bootstrap = (await client.get("/api/bootstrap")).json()
    assert bootstrap["data_dir"] == str(app.state.config.data_dir)
