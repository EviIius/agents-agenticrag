"""Explicit isolated QA server; never imported by the installed app."""

import json
import logging
from contextlib import asynccontextmanager
from pathlib import Path

import httpx

from app.config import Settings
from app.db import connections, settings
from app.main import create_app
from app.assistant.mac_probe import private_read, private_write

TRIAL_HOME = Path.home() / ".local/share/workbench/qa/assistant-chat-open-20261108"


def build_app():
    logging.getLogger("httpx").setLevel(logging.WARNING)
    source = json.loads(private_read(TRIAL_HOME / "source-settings.json", 10000))
    app = create_app(
        Settings(
            data_dir=TRIAL_HOME / "data",
            dev=True,
            assistant_enabled=True,
            assistant_open_home=TRIAL_HOME,
            legacy_db=TRIAL_HOME / "no-legacy.db",
            image_home=None,
            transcribe_home=None,
            web_fixtures=None,
            log_level="WARNING",
        )
    )
    original = app.router.lifespan_context

    @asynccontextmanager
    async def lifespan(server):
        async with original(server):
            if not await server.state.store.one(
                "SELECT id FROM connections WHERE id=?", (source["connection_id"],)
            ):
                date = connections.now()
                await server.state.store.batch(
                    [
                        (
                            "INSERT INTO connections(id,kind,name,base_url,keep_alive,created_at,updated_at) VALUES (?,?,?,?,?,?,?)",
                            (
                                source["connection_id"],
                                "ollama",
                                "Local runtime · isolated trial",
                                source["base_url"],
                                source["keep_alive"],
                                date,
                                date,
                            ),
                        ),
                        (
                            "INSERT INTO model_prefs(connection_id,model_id,hidden) VALUES (?,?,1)",
                            (source["connection_id"], "llama3.3:70b-instruct-q4_K_M"),
                        ),
                        (
                            "INSERT INTO model_prefs(connection_id,model_id,context_length,params_json) VALUES (?,?,?,?)",
                            (
                                source["connection_id"],
                                source["model_id"],
                                source["context_length"],
                                json.dumps(source["params_defaults"]),
                            ),
                        ),
                    ]
                )
                await settings.patch(server.state.store, {"auto_title": False})
            adapter = await server.state.registry.adapter(source["connection_id"])

            async def capture(request: httpx.Request) -> None:
                if request.url.path != "/api/chat":
                    return
                ledger = TRIAL_HOME / "http-calls.json"
                calls = json.loads(private_read(ledger, 2000)) if ledger.exists() else []
                if len(calls) >= 2:
                    raise RuntimeError("The declared two-request trial is exhausted.")
                body = json.loads(request.content)
                if body.get("model") != source["model_id"] or len(body.get("messages", [])) != 2:
                    raise RuntimeError("Unexpected inference scope.")
                index = len(calls) + 1
                private_write(TRIAL_HOME / f"payload-{index}.json", request.content)
                calls.append({"request": index, "endpoint": "/api/chat"})
                temporary = TRIAL_HOME / f"http-calls-{index}.tmp"
                private_write(temporary, json.dumps(calls).encode())
                temporary.replace(ledger)

            adapter.client.event_hooks.setdefault("request", []).append(capture)
            yield

    app.router.lifespan_context = lifespan
    return app
