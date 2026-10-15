"""Measured image coexistence, identified by reported digest/context only."""

from urllib.parse import urlsplit

from ..errors import AppError
from ..images.engine import QUALIFIED_DIGESTS
from ..providers.registry import Registry


async def image_models(registry: Registry) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    models = await registry.models()
    for connection in {m.connection_id for m in models}:
        adapter = await registry.adapter(connection)
        url = urlsplit(adapter.base_url)
        if url.hostname not in {"127.0.0.1", "localhost", "::1"} or url.port != 11434:
            continue
        try:
            tags = await adapter.json("GET", "/api/tags")
        except AppError:
            continue
        qualified = {
            row.get("name")
            for row in tags.get("models", [])
            if row.get("digest") in QUALIFIED_DIGESTS
        }
        result.extend(
            {"connection_id": m.connection_id, "model_id": m.model_id}
            for m in models
            if m.connection_id == connection
            and m.model_id in qualified
            and m.context_length == 32768
        )
    return result
