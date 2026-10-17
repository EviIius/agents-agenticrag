"""Synthetic image handoff; no real unload, weights, inference or private data."""

import asyncio
import json
import sys
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any

import httpx
import pytest
import respx

from app.capacity import Capacity
from app.db.core import Store, connect
from app.errors import AppError
from app.images.engine import Engine
from app.images.jobs import Images
from app.providers.ollama import Ollama
from tests.test_images import FakeEngine, spec

CURRENT = "09386c7af8487c073bfb845833462d30d0d48ad69428c301b909dc159c028b0a"
EMBED = "e" * 64


def daily(**changes: Any) -> dict[str, Any]:
    return {
        "name": "synthetic-daily",
        "digest": CURRENT,
        "context_length": 32768,
        "size_vram": 19508609678,
        **changes,
    }


def embedding(**changes: Any) -> dict[str, Any]:
    return {
        "name": "synthetic-files",
        "digest": EMBED,
        "context_length": 32768,
        "size_vram": 5776426925,
        **changes,
    }


@pytest.fixture
async def engine(tmp_path: Path) -> AsyncIterator[Engine]:
    async with connect(tmp_path / "data") as db:
        store = Store(db)
        await store.execute(
            "INSERT INTO connections(id,kind,name,base_url,enabled,created_at,updated_at) "
            "VALUES(?,?,?,?,?,?,?)",
            (
                "local",
                "ollama",
                "Synthetic local",
                "http://127.0.0.1:11434",
                1,
                "synthetic",
                "synthetic",
            ),
        )
        await store.execute(
            "INSERT INTO settings VALUES(?,?)",
            (
                "library.embedding",
                json.dumps({"connection_id": "local", "model_id": "synthetic-files"}),
            ),
        )
        yield Engine(tmp_path, Capacity(), store)


def metadata(loaded: list[dict[str, Any]]) -> None:
    respx.get("http://127.0.0.1:11434/api/ps").mock(
        side_effect=lambda _: httpx.Response(200, json={"models": loaded})
    )
    respx.get("http://127.0.0.1:11434/api/tags").respond(200, json={"models": loaded})
    respx.post("http://127.0.0.1:11434/api/show").respond(200, json={"capabilities": ["embedding"]})


async def progress(_: dict[str, Any]) -> None:
    pass


def no_unload() -> None:
    assert not any(call.request.url.path == "/api/chat" for call in respx.calls)


@respx.mock
async def test_image_handoff_releases_embedding_and_keeps_daily_model(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    engine: Engine,
) -> None:
    worker = tmp_path / "fake-worker.py"
    worker.write_text("import json\nprint(json.dumps({'type':'finished'}),flush=True)\n")
    capacity = engine.capacity
    assert capacity
    monkeypatch.setattr(engine, "paths", lambda: (Path(sys.executable), worker, tmp_path))

    async def stable_swap() -> float:
        return 0

    monkeypatch.setattr(engine, "swap", stable_swap)
    loaded = [daily(), embedding()]
    metadata(loaded)
    unloads: list[str] = []

    def release(request: Any) -> Any:
        body = json.loads(request.content)
        unloads.append(body["model"])
        assert body == {
            "model": "synthetic-files",
            "messages": [],
            "keep_alive": 0,
            "stream": False,
        }
        assert capacity.busy
        loaded[:] = [daily()]
        return httpx.Response(200, json={"done": True, "done_reason": "unload"})

    respx.post("http://127.0.0.1:11434/api/chat").mock(side_effect=release)
    events: list[dict[str, Any]] = []

    async def progress(event: dict[str, Any]) -> None:
        events.append(event)

    async with capacity.lease(background=True), asyncio.timeout(5):
        assert await engine.run(tmp_path / "request.json", tmp_path, progress) == 0
    assert unloads == ["synthetic-files"]
    assert loaded == [daily()]
    assert any(event["type"] == "releasing_embeddings" for event in events)
    assert not capacity.busy


@pytest.mark.parametrize("loaded", [[], [daily()]])
@respx.mock
async def test_qualified_setup_needs_no_management(
    engine: Engine, loaded: list[dict[str, Any]]
) -> None:
    metadata(loaded)
    await engine.prepare_memory(progress)
    assert len(respx.calls) == 1
    no_unload()


@pytest.mark.parametrize(
    "remaining",
    [daily(digest="unknown"), daily(context_length=65536), daily(size_vram=21827095101)],
)
@respx.mock
async def test_no_partial_eviction_when_chat_would_still_block(
    engine: Engine, remaining: dict[str, Any]
) -> None:
    metadata([remaining, embedding()])
    with pytest.raises(AppError, match="not qualified"):
        await engine.prepare_memory(progress)
    assert all(call.request.method == "GET" for call in respx.calls)
    no_unload()


@pytest.mark.parametrize(
    "url",
    [
        "https://remote.example",
        "http://127.0.0.1:18080",
        "http://127.0.0.1:bad",
        "http://name:secret@127.0.0.1:11434",
        "http://127.0.0.1:11434/path",
    ],
)
@respx.mock
async def test_remote_or_different_runtime_is_not_released(engine: Engine, url: str) -> None:
    assert engine.store
    await engine.store.execute("UPDATE connections SET base_url=?", (url,))
    metadata([daily(), embedding()])
    with pytest.raises(AppError, match="not qualified"):
        await engine.prepare_memory(progress)
    no_unload()


@respx.mock
async def test_only_configured_embedding_identity_is_eligible(engine: Engine) -> None:
    metadata([daily(), embedding(name="unconfigured-embedding")])
    with pytest.raises(AppError, match="not qualified"):
        await engine.prepare_memory(progress)
    no_unload()


@pytest.mark.parametrize(
    "show",
    [
        {"capabilities": ["embedding", "completion"]},
        {"capabilities": ["completion"]},
        {"capabilities": []},
        [],
        None,
    ],
)
@respx.mock
async def test_fresh_embedding_only_capability_required(engine: Engine, show: Any) -> None:
    assert engine.capacity
    metadata([daily(), embedding()])
    respx.post("http://127.0.0.1:11434/api/show").respond(200, json=show)
    async with engine.capacity.lease():
        with pytest.raises(AppError, match="Nothing was unloaded"):
            await engine.prepare_memory(progress)
    no_unload()


@respx.mock
async def test_release_requires_scheduler_lease(engine: Engine) -> None:
    metadata([daily(), embedding()])
    with pytest.raises(AppError, match="shared model slot"):
        await engine.prepare_memory(progress)
    no_unload()


@pytest.mark.parametrize("race", ["alias", "residency", "duplicate", "malformed", "tags"])
@respx.mock
async def test_identity_or_residency_changes_fail_before_release(engine: Engine, race: str) -> None:
    assert engine.capacity
    loaded = [daily(), embedding()]
    metadata(loaded)
    if race == "alias":
        respx.get("http://127.0.0.1:11434/api/tags").respond(
            200, json={"models": [embedding(digest="changed")]}
        )
    elif race == "residency":
        respx.get("http://127.0.0.1:11434/api/ps").mock(
            side_effect=[
                httpx.Response(200, json={"models": loaded}),
                httpx.Response(200, json={"models": [embedding()]}),
            ]
        )
    elif race == "duplicate":
        loaded.append(embedding())
    elif race == "tags":
        respx.get("http://127.0.0.1:11434/api/tags").respond(200, json={"models": [None]})
    else:
        loaded[0]["name"] = []
    async with engine.capacity.lease():
        with pytest.raises(AppError, match="Nothing was unloaded"):
            await engine.prepare_memory(progress)
    no_unload()


@pytest.mark.parametrize("ack", [{}, {"done": True, "done_reason": "stop"}, [], None])
@respx.mock
async def test_release_failure_invalidates_model_cache_and_never_launches_worker(
    engine: Engine, ack: Any
) -> None:
    assert engine.capacity
    metadata([daily(), embedding()])
    invalidations = []
    engine.models_changed = lambda: invalidations.append(True)
    respx.post("http://127.0.0.1:11434/api/chat").respond(200, json=ack)
    async with engine.capacity.lease():
        with pytest.raises(AppError, match="Couldn’t finish"):
            await engine.prepare_memory(progress)
    assert invalidations == [True]
    assert not engine.capacity.busy


@respx.mock
async def test_delayed_unload_waits_and_library_reloads_without_losing_configuration(
    engine: Engine,
) -> None:
    assert engine.store and engine.capacity
    loaded = [daily(), embedding()]
    metadata(loaded)
    before = await engine.store.rows("SELECT * FROM settings")
    release_sent = asyncio.Event()
    ps_after = 0

    def ps(_: httpx.Request) -> httpx.Response:
        nonlocal ps_after
        if release_sent.is_set():
            ps_after += 1
            if ps_after >= 3:
                loaded[:] = [daily()]
        return httpx.Response(200, json={"models": loaded})

    def release(_: httpx.Request) -> httpx.Response:
        release_sent.set()
        return httpx.Response(200, json={"done": True, "done_reason": "unload"})

    respx.get("http://127.0.0.1:11434/api/ps").mock(side_effect=ps)
    respx.post("http://127.0.0.1:11434/api/chat").mock(side_effect=release)
    adapter = Ollama("local", "http://127.0.0.1:11434")
    adapter.capacity = engine.capacity
    embed_started = asyncio.Event()
    embed_continue = asyncio.Event()

    async def embed(request: httpx.Request) -> httpx.Response:
        assert engine.capacity and engine.capacity.busy
        assert json.loads(request.content)["model"] == "synthetic-files"
        embed_started.set()
        await embed_continue.wait()
        return httpx.Response(200, json={"embeddings": [[0.1, 0.2]]})

    respx.post("http://127.0.0.1:11434/api/embed").mock(side_effect=embed)
    existing = asyncio.create_task(adapter.embed("synthetic-files", ["Synthetic text"]))
    await embed_started.wait()

    async def image() -> None:
        assert engine.capacity
        async with engine.capacity.lease(background=True):
            await engine.prepare_memory(progress)
            assert loaded == [daily()]

    queued = asyncio.create_task(image())
    await asyncio.sleep(0)
    assert not release_sent.is_set()
    embed_continue.set()
    await asyncio.wait_for(asyncio.gather(existing, queued), 5)
    assert ps_after >= 3
    assert await adapter.embed("synthetic-files", ["Synthetic next query"]) == [[0.1, 0.2]]
    await adapter.close()
    assert await engine.store.rows("SELECT * FROM settings") == before
    assert not engine.capacity.busy


@respx.mock
async def test_cancel_during_memory_handoff_releases_slot(engine: Engine) -> None:
    assert engine.capacity
    metadata([daily(), embedding()])
    started = asyncio.Event()
    invalidations = []
    engine.models_changed = lambda: invalidations.append(True)

    async def pending(_: httpx.Request) -> httpx.Response:
        started.set()
        await asyncio.Event().wait()
        return httpx.Response(200)

    respx.post("http://127.0.0.1:11434/api/chat").mock(side_effect=pending)

    async def image() -> None:
        assert engine.capacity
        async with engine.capacity.lease():
            await engine.prepare_memory(progress)

    task = asyncio.create_task(image())
    await asyncio.wait_for(started.wait(), 2)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert invalidations == [True]
    assert not engine.capacity.busy


@respx.mock
async def test_unload_timeout_never_qualifies_still_resident_embedding(
    engine: Engine, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert engine.capacity
    metadata([daily(), embedding()])
    respx.post("http://127.0.0.1:11434/api/chat").respond(
        200, json={"done": True, "done_reason": "unload"}
    )
    original_timeout = asyncio.timeout
    monkeypatch.setattr(asyncio, "timeout", lambda _: original_timeout(0.02))
    async with engine.capacity.lease():
        with pytest.raises(AppError, match="Couldn’t finish"):
            await engine.prepare_memory(progress)
    assert not engine.capacity.busy


@respx.mock
async def test_new_model_after_release_aborts_without_another_unload(engine: Engine) -> None:
    assert engine.capacity
    loaded = [daily(), embedding()]
    metadata(loaded)

    def release(_: httpx.Request) -> httpx.Response:
        loaded[:] = [daily(name="unexpected-new-alias")]
        return httpx.Response(200, json={"done": True, "done_reason": "unload"})

    respx.post("http://127.0.0.1:11434/api/chat").mock(side_effect=release)
    async with engine.capacity.lease():
        with pytest.raises(AppError, match="Couldn’t finish"):
            await engine.prepare_memory(progress)
    assert sum(call.request.url.path == "/api/chat" for call in respx.calls) == 1


@respx.mock
async def test_entire_plan_must_be_embedding_only_before_any_release(engine: Engine) -> None:
    assert engine.store and engine.capacity
    await engine.store.execute(
        "INSERT INTO settings VALUES(?,?)",
        (
            "web.embedding",
            json.dumps({"connection_id": "local", "model_id": "synthetic-search"}),
        ),
    )
    metadata([daily(), embedding(), embedding(name="synthetic-search")])
    respx.post("http://127.0.0.1:11434/api/show").mock(
        side_effect=[
            httpx.Response(200, json={"capabilities": ["embedding"]}),
            httpx.Response(200, json={"capabilities": ["embedding", "completion"]}),
        ]
    )
    async with engine.capacity.lease():
        with pytest.raises(AppError, match="Nothing was unloaded"):
            await engine.prepare_memory(progress)
    no_unload()


@respx.mock
async def test_handoff_progress_is_durable_and_pushes_to_existing_image_stream(
    engine: Engine, tmp_path: Path
) -> None:
    assert engine.store and engine.capacity
    service = Images(engine.store, tmp_path, None, engine.capacity)
    fake = FakeEngine()
    original = fake.run
    stages = []

    async def run(manifest: Path, scratch: Path, notify: Any) -> int:
        assert engine.store
        await notify({"type": "releasing_embeddings"})
        job = (await service.list())[0]
        stages.append((job.state, job.stage))
        events = await engine.store.rows("SELECT data_json FROM image_events")
        assert any("Making room for images" in row["data_json"] for row in events)
        fake.release.set()
        return await original(manifest, scratch, notify)

    fake.run = run  # type: ignore[method-assign,assignment]
    service.engine = fake  # type: ignore[assignment]
    job = await service.submit(spec())
    await asyncio.wait_for(service.tasks[job.id], 5)
    assert (await service.get(job.id)).state == "complete"
    assert stages == [("preparing", "Making room for images")]
    await service.close()
