"""Browser-test app on the required 8787 port, with isolated temporary data."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from tempfile import mkdtemp

from fastapi import FastAPI

from app.config import Settings
from app.db import connections, settings
from app.main import create_app
from app.schemas import ConnectionCreate

app = create_app(
    Settings(
        data_dir=Path(mkdtemp(prefix="workbench-e2e-")),
        dev=True,
        web_fixtures=Path(__file__).parent / "fixtures/web",
    )
)
original = app.router.lifespan_context


@asynccontextmanager
async def lifespan(server: FastAPI) -> AsyncIterator[None]:
    async with original(server):
        await connections.create(
            server.state.store,
            ConnectionCreate(name="Fake runtime", base_url="http://127.0.0.1:18080"),
        )
        await settings.patch(server.state.store, {"auto_title": False})
        yield


app.router.lifespan_context = lifespan
