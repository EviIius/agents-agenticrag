from urllib.parse import urlsplit

import httpx
from fastapi import APIRouter, Request

from ..db import connections
from ..errors import AppError
from ..providers.ollama import Ollama
from ..schemas import Connection, ConnectionCreate, ConnectionPatch, Detection

router = APIRouter(prefix="/api/connections")


async def probe(url: str) -> Detection:
    parsed = urlsplit(url)
    if (
        parsed.scheme not in ("http", "https")
        or not parsed.hostname
        or parsed.username
        or parsed.password
    ):
        raise AppError("validation_error", "Use a runtime HTTP URL without credentials.", 422)
    adapter = Ollama("probe", url)
    adapter.client.timeout = httpx.Timeout(2)
    try:
        body = await adapter.json("GET", "/api/tags")
        return Detection(base_url=url, reachable=True, model_count=len(body.get("models", [])))
    except AppError as exc:
        return Detection(base_url=url, reachable=False, error=exc.message)
    finally:
        await adapter.close()


@router.get("")
async def listing(request: Request) -> list[Connection]:
    out = await connections.list_connections(request.app.state.store)
    models = await request.app.state.registry.models(include_hidden=True)
    for connection in out:
        if connection.enabled:
            connection.reachable = connection.id not in request.app.state.registry.errors
            connection.model_count = sum(m.connection_id == connection.id for m in models)
            connection.latency_ms = request.app.state.registry.latencies.get(connection.id)
    return out


@router.post("/detect")
async def detect() -> list[Detection]:
    return [await probe("http://127.0.0.1:11434")]


@router.post("", status_code=201)
async def create(body: ConnectionCreate, request: Request) -> Connection:
    result = await probe(body.base_url)
    if not result.reachable and not body.force:
        raise AppError("runtime_unreachable", result.error or "Ollama is unreachable.", 422)
    existing = next(
        (c for c in await listing(request) if c.base_url.rstrip("/") == body.base_url.rstrip("/")),
        None,
    )
    if existing:
        return existing
    result_connection = await connections.create(request.app.state.store, body)
    request.app.state.registry.updated = 0
    return result_connection


@router.patch("/{identifier}")
async def patch(identifier: str, body: ConnectionPatch, request: Request) -> Connection:
    values = body.model_dump(exclude_unset=True)
    if "base_url" in values:
        await probe(values["base_url"])
    values["updated_at"] = connections.now()
    await request.app.state.store.execute(
        "UPDATE connections SET " + ",".join(k + "=?" for k in values) + " WHERE id=?",
        (*values.values(), identifier),
    )
    request.app.state.registry.updated = 0
    connection = next((c for c in await listing(request) if c.id == identifier), None)
    if not connection:
        raise AppError("not_found", "Connection not found.", 404)
    return connection


@router.delete("/{identifier}", status_code=204)
async def delete(identifier: str, request: Request) -> None:
    await request.app.state.store.execute("DELETE FROM connections WHERE id=?", (identifier,))
    request.app.state.registry.updated = 0
