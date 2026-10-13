"""Browser-test app with isolated temporary data and a test-only listener."""

import asyncio
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from tempfile import mkdtemp

from fastapi import FastAPI

from app.config import Settings
from app.db import connections, settings
from app.main import create_app
from app.schemas import ConnectionCreate

data = Path(mkdtemp(prefix="workbench-e2e-"))
os.environ["FAKE_TRANSCRIBE_GLOSSARY"] = str(data / "fake-glossary.txt")
app = create_app(
    Settings(
        data_dir=data,
        dev=True,
        legacy_db=Path(mkdtemp(prefix="workbench-legacy-fixture-")) / "missing.db",
        transcribe_home=Path(__file__).parent / "fake_transcribe",
        web_fixtures=Path(__file__).parent / "fixtures/web",
    )
)
original = app.router.lifespan_context


@asynccontextmanager
async def lifespan(server: FastAPI) -> AsyncIterator[None]:
    context = original(server)
    await context.__aenter__()
    server.state.fake_lifecycle = context
    server.state.fake_restart_lock = asyncio.Lock()
    try:
        await connections.create(
            server.state.store,
            ConnectionCreate(name="Fake runtime", base_url="http://127.0.0.1:18080"),
        )
        await settings.patch(server.state.store, {"auto_title": False})
        from tests.fake_image import FakeImageEngine

        server.state.images.engine = FakeImageEngine()
        yield
    finally:
        await server.state.fake_lifecycle.__aexit__(None, None, None)


app.router.lifespan_context = lifespan


@app.post("/tests/long-chat/{chat_id}")
async def seed_long_chat(chat_id: str) -> dict[str, int]:
    """Synthetic history for the Phase 3 browser performance measurement only."""
    from app.db.connections import now, uid

    statements: list[tuple[str, tuple[object, ...]]] = []
    parent = None
    for i in range(300):
        identifier = uid()
        statements.append(
            (
                "INSERT INTO messages(id,chat_id,parent_id,role,content,status,"
                "created_at,updated_at) "
                "VALUES (?,?,?,?,?,'complete',?,?)",
                (
                    identifier,
                    chat_id,
                    parent,
                    "user" if i % 2 == 0 else "assistant",
                    f"Fake history item {i}. Synthetic.",
                    now(),
                    now(),
                ),
            )
        )
        parent = identifier
    statements.append(("UPDATE chats SET current_leaf_id=? WHERE id=?", (parent, chat_id)))
    await app.state.store.batch(statements)
    return {"messages": 300}


@app.post("/tests/restart-lifecycle")
async def restart_fake_lifecycle() -> dict[str, bool]:
    """Exercise a full app shutdown/startup against the same private fake database."""
    from tests.fake_image import FakeImageEngine

    async with app.state.fake_restart_lock:
        await app.state.fake_lifecycle.__aexit__(None, None, None)
        context = original(app)
        await context.__aenter__()
        app.state.fake_lifecycle = context
        app.state.images.engine = FakeImageEngine()
    return {"restarted": True}
