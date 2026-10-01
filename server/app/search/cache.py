import asyncio
import hashlib
import json
from datetime import UTC, datetime, timedelta

from ..db.core import Store
from ..providers.base import Adapter
from .extract import Page, extract_async
from .fetch import read_network
from .fixtures import Fixtures


async def read(store: Store, url: str, days: int, fixtures: Fixtures) -> Page:
    date = datetime.now(UTC)
    cached = await store.one(
        "SELECT * FROM page_cache WHERE url=? AND expires_at>? AND error IS NULL",
        (url, date.isoformat()),
    )
    if cached and not fixtures.recording:
        return Page(
            str(cached["final_url"]),
            str(cached["title"] or ""),
            str(cached["site_name"] or ""),
            str(cached["published_at"]) if cached["published_at"] else None,
            str(cached["text"]),
        )
    raw = fixtures.page(url)
    if raw is None:
        raw = await read_network(url)
    fixtures.save_page(url, raw)
    page = await extract_async(raw)
    await store.execute(
        "INSERT OR REPLACE INTO page_cache VALUES (?,?,?,?,?,?,NULL,?,?)",
        (
            url,
            page.url,
            page.title,
            page.site_name,
            page.published_at,
            page.text,
            date.isoformat(),
            (date + timedelta(days=days)).isoformat(),
        ),
    )
    return page


async def embed(
    store: Store, adapter: Adapter, model: str, texts: list[str], connection_id: str = ""
) -> list[list[float]]:
    keys = [
        connection_id + ":" + model + ":" + hashlib.sha256(t.encode()).hexdigest() for t in texts
    ]
    vectors: dict[str, list[float]] = {}
    missing: dict[str, str] = {}
    for key, text in zip(keys, texts, strict=True):
        row = await store.one("SELECT vector FROM embed_cache WHERE key=?", (key,))
        if row:
            vectors[key] = json.loads(bytes(row["vector"]).decode())
        else:
            missing.setdefault(key, text)
    pairs = list(missing.items())
    async with asyncio.timeout(8):
        for offset in range(0, len(pairs), 64):
            batch = pairs[offset : offset + 64]
            found = await adapter.embed(model, [text for _, text in batch])
            if len(found) != len(batch):
                raise ValueError("Embedding response has wrong length")
            for (key, _), vector in zip(batch, found, strict=True):
                vectors[key] = vector
                await store.execute(
                    "INSERT OR REPLACE INTO embed_cache VALUES (?,?)",
                    (key, json.dumps(vector).encode()),
                )
    return [vectors[k] for k in keys]
