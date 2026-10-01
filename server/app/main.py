import logging
import re
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .api import attachments, chats, connections, messages, models, runs, search
from .api import settings as settings_api
from .api.health import router as health_router
from .config import APP_NAME, VERSION, Settings
from .db.core import Store, connect
from .errors import AppError, register_handlers
from .providers.registry import Registry
from .runs.manager import RunManager
from .search.pipeline import Pipeline
from .security import SecurityMiddleware


def create_app(settings: Settings | None = None, static_dir: Path | None = None) -> FastAPI:
    config = settings or Settings()
    static = (static_dir or Path(__file__).parent / "static").resolve()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        logging.basicConfig(level=config.log_level, format="%(levelname)s %(name)s: %(message)s")
        async with connect(config.data_dir) as db:
            app.state.db = db
            app.state.store = Store(db)
            app.state.config = config
            app.state.registry = Registry(app.state.store)
            app.state.runs = RunManager(app.state.store, app.state.registry, config.data_dir)
            app.state.search = Pipeline(app.state.runs, config.web_fixtures)
            app.state.runs.web_hook = app.state.search
            app.state.runs.web_finalize = app.state.search.finalize
            await app.state.runs.recover()
            try:
                yield
            finally:
                await app.state.runs.close()
                await app.state.registry.close()

    app = FastAPI(
        title=APP_NAME,
        version=VERSION,
        lifespan=lifespan,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    register_handlers(app)
    if config.dev:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
            allow_methods=["*"],
            allow_headers=["*"],
        )
    app.add_middleware(SecurityMiddleware, settings=config)

    app.include_router(health_router)
    for router in (
        attachments.router,
        chats.router,
        connections.router,
        messages.router,
        models.router,
        runs.router,
        settings_api.router,
        search.router,
    ):
        app.include_router(router)

    @app.get("/{path:path}", include_in_schema=False)
    async def asset(path: str) -> FileResponse:
        if (
            path == "api"
            or path.startswith("api/")
            or ((path == "design" or path.startswith("design/")) and not config.dev)
        ):
            raise AppError("not_found", "Not found.", 404)
        candidate = (static / path).resolve()
        if not candidate.is_relative_to(static):
            raise AppError("not_found", "Not found.", 404)
        if candidate.is_file():
            cache = (
                "public, max-age=31536000, immutable"
                if path.startswith("assets/")
                and re.search(r"[-.][A-Za-z0-9_-]{8,}\.", candidate.name)
                else "no-cache"
            )
            return FileResponse(
                candidate,
                headers={"Cache-Control": "no-cache" if candidate.name == "index.html" else cache},
            )
        index = static / "index.html"
        if not index.exists():
            raise AppError("not_found", "Build the web app before serving it.", 404)
        return FileResponse(index, headers={"Cache-Control": "no-cache"})

    return app


app = create_app()
