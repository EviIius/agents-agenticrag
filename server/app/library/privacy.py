"""Validate Library privacy before accepting an answer request."""

from ipaddress import ip_address
from urllib.parse import urlsplit

from ..db.core import Store
from ..errors import AppError


async def guard(store: Store, connection_id: str, values: dict[str, object]) -> None:
    if not values["library.requires_local"]:
        return
    connection = await store.one("SELECT base_url FROM connections WHERE id=?", (connection_id,))
    host = urlsplit(connection["base_url"]).hostname if connection else None
    local = host == "localhost"
    try:
        local = local or bool(host and ip_address(host).is_loopback)
    except ValueError:
        pass
    if not local:
        raise AppError("library_requires_local", "Library text can only go to local Ollama.", 422)
