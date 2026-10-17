"""Synthetic image handoff; no real unload, weights, inference or private data."""

import asyncio
import json
import sys
from pathlib import Path
from typing import Any

import pytest
import respx

from app.capacity import Capacity
from app.images.engine import Engine

CURRENT = "09386c7af8487c073bfb845833462d30d0d48ad69428c301b909dc159c028b0a"
EMBED = "e" * 64


def daily(**changes: Any) -> dict[str, Any]:
    return {"name": "synthetic-daily", "digest": CURRENT,
            "context_length": 32768, "size_vram": 19508609678, **changes}


def embedding(**changes: Any) -> dict[str, Any]:
    return {"name": "synthetic-files", "digest": EMBED,
            "context_length": 32768, "size_vram": 5776426925, **changes}


@respx.mock
async def test_image_handoff_releases_embedding_and_keeps_daily_model(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    worker = tmp_path / "fake-worker.py"
    worker.write_text("import json\nprint(json.dumps({'type':'finished'}),flush=True)\n")
    capacity = Capacity()
    engine = Engine(tmp_path, capacity)
    monkeypatch.setattr(engine, "paths", lambda: (Path(sys.executable), worker, tmp_path))

    async def stable_swap() -> float:
        return 0

    monkeypatch.setattr(engine, "swap", stable_swap)
    loaded = [daily(), embedding()]
    respx.get("http://127.0.0.1:11434/api/ps").mock(
        side_effect=lambda _: __import__("httpx").Response(200, json={"models": loaded})
    )
    respx.post("http://127.0.0.1:11434/api/show").respond(200, json={"capabilities": ["embedding"]})
    unloads: list[str] = []

    def release(request: Any) -> Any:
        body = json.loads(request.content)
        unloads.append(body["model"])
        assert body == {"model": "synthetic-files", "messages": [], "keep_alive": 0, "stream": False}
        assert capacity.busy
        loaded[:] = [daily()]
        return __import__("httpx").Response(200, json={"done": True, "done_reason": "unload"})

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
