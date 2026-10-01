import json
import re
from typing import Any
from urllib.parse import urlsplit

from .core import Store

DEFAULTS: dict[str, Any] = {
    "default_connection_id": None,
    "default_model_id": None,
    "new_chat_model": "last_used",
    "default_system_prompt": "You are a helpful assistant.",
    "include_current_date": True,
    "auto_title": True,
    "utility_model": None,
    "user_name": "",
    "web.provider_order": ["searxng", "ddgs", "brave"],
    "web.searxng_url": "http://127.0.0.1:8888",
    "web.brave_api_key": None,
    "web.default_on": False,
    "web.max_sources": 6,
    "web.embedding": None,
    "web.page_cache_days": 7,
    "web.blocked_domains": [
        "pinterest.com",
        "facebook.com",
        "instagram.com",
        "tiktok.com",
        "x.com",
        "twitter.com",
    ],
}


async def get(store: Store, public: bool = False) -> dict[str, Any]:
    values = {
        **DEFAULTS,
        **{
            str(r["key"]): json.loads(str(r["value_json"]))
            for r in await store.rows("SELECT * FROM settings")
        },
    }
    if public:
        values["web.has_brave_api_key"] = bool(values.pop("web.brave_api_key", None))
    return values


async def patch(store: Store, values: dict[str, Any]) -> None:
    allowed = set(DEFAULTS) | {
        "appearance.theme",
        "appearance.font",
        "appearance.size",
        "appearance.reduce_motion",
    }
    if set(values) - allowed:
        raise ValueError("Unknown setting")
    for key, options in {
        "new_chat_model": ("last_used", "fixed"),
        "appearance.theme": ("system", "light", "dark"),
        "appearance.font": ("serif", "sans"),
        "appearance.size": ("S", "M", "L"),
        "appearance.reduce_motion": ("system", "always"),
    }.items():
        if key in values and values[key] not in options:
            raise ValueError("Invalid preference value")
    if "web.max_sources" in values and values["web.max_sources"] not in (4, 6, 8):
        raise ValueError("Sources must be 4, 6 or 8")
    if "web.page_cache_days" in values and values["web.page_cache_days"] not in (1, 7, 30):
        raise ValueError("Cache days must be 1, 7 or 30")
    if "web.provider_order" in values and (
        set(values["web.provider_order"]) - {"searxng", "ddgs", "brave"}
    ):
        raise ValueError("Unknown search provider")
    for key in ("auto_title", "include_current_date", "web.default_on"):
        if key in values and not isinstance(values[key], bool):
            raise ValueError("Expected a boolean setting")
    for key in ("default_system_prompt", "user_name", "web.searxng_url"):
        if key in values and not isinstance(values[key], str):
            raise ValueError("Expected a text setting")
    if "web.provider_order" in values and (
        not isinstance(values["web.provider_order"], list)
        or len(values["web.provider_order"]) != len(set(values["web.provider_order"]))
    ):
        raise ValueError("Provider order must be a list without duplicates")
    if "web.blocked_domains" in values and (
        not isinstance(values["web.blocked_domains"], list)
        or any(
            not isinstance(d, str) or not re.fullmatch(r"[a-zA-Z0-9.-]{1,253}", d)
            for d in values["web.blocked_domains"]
        )
    ):
        raise ValueError("Blocked sites must be domains, one per line")
    if values.get("web.searxng_url"):
        parsed = urlsplit(values["web.searxng_url"])
        if (
            parsed.scheme not in ("http", "https")
            or not parsed.hostname
            or parsed.username
            or parsed.password
        ):
            raise ValueError("Search URL must be HTTP or HTTPS without credentials")
    if (
        "web.brave_api_key" in values
        and values["web.brave_api_key"] is not None
        and not isinstance(values["web.brave_api_key"], str)
    ):
        raise ValueError("API key must be text")
    for key in ("utility_model", "web.embedding"):
        if values.get(key) is not None and (
            not isinstance(values[key], dict)
            or set(values[key]) != {"connection_id", "model_id"}
            or any(not isinstance(v, str) or not v for v in values[key].values())
        ):
            raise ValueError("Choose a connection and model")
    await store.batch(
        [
            (
                "INSERT INTO settings VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value_j"
                "son=excluded.value_json",
                (k, json.dumps(v)),
            )
            for k, v in values.items()
        ]
    )
