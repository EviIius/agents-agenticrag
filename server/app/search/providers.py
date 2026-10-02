import asyncio
import hashlib
import json
import weakref
from datetime import UTC, datetime, timedelta
from time import monotonic
from typing import Any

import httpx
from ddgs import DDGS

from ..db.core import Store
from ..schemas import SearchResult, SearchStatus
from .fixtures import Fixtures

NAMES = {
    "ollama": "Ollama Search",
    "searxng": "SearXNG",
    "exa": "Exa",
    "ddgs": "DuckDuckGo",
    "brave": "Brave",
}
EXA_URL = "https://mcp.exa.ai/mcp?tools=web_search_advanced_exa"
_COOLDOWNS: weakref.WeakKeyDictionary[Store, dict[str, float]] = weakref.WeakKeyDictionary()


class RateLimited(ValueError):
    def __init__(self, message: str, retry_after: str | None) -> None:
        super().__init__(message)
        try:
            self.seconds = max(1, min(86400, int(retry_after or "60")))
        except ValueError:
            self.seconds = 60


async def exa_search(query: str, freshness: str) -> list[SearchResult]:
    """One bounded, keyless search call; no SDK, agent tools or generated summaries."""
    arguments: dict[str, Any] = {
        "query": query,
        "numResults": 10,
        "type": "fast",
        "enableSummary": False,
        "enableHighlights": True,
        "highlightsMaxCharacters": 1000,
        "textMaxCharacters": 1000,
    }
    if freshness != "any":
        days = {"day": 1, "week": 7, "month": 30, "year": 365}[freshness]
        arguments["startPublishedDate"] = (datetime.now(UTC) - timedelta(days=days)).isoformat()
        arguments["maxAgeHours"] = 1 if freshness == "day" else 24
    async with asyncio.timeout(8), httpx.AsyncClient(timeout=8, trust_env=False) as client:
        async with client.stream(
            "POST",
            EXA_URL,
            headers={"Accept": "application/json, text/event-stream"},
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {"name": "web_search_advanced_exa", "arguments": arguments},
            },
        ) as response:
            if response.status_code == 429:
                raise RateLimited("Exa free search rate limit", response.headers.get("Retry-After"))
            response.raise_for_status()
            data = bytearray()
            async for part in response.aiter_bytes():
                data.extend(part)
                if len(data) > 3_000_000:
                    raise ValueError("Exa response too large")
            body = data.decode("utf-8")
            if "text/event-stream" in response.headers.get("content-type", ""):
                events = [
                    "\n".join(
                        line[5:].lstrip() for line in event.splitlines() if line.startswith("data:")
                    )
                    for event in body.replace("\r\n", "\n").split("\n\n")
                ]
                payload = next(json.loads(event) for event in events if event and event != "[DONE]")
            else:
                payload = json.loads(body)
    result = payload.get("result", {})
    if payload.get("error") or result.get("isError"):
        raise ValueError("Exa search returned an error")
    structured = result.get("structuredContent")
    if structured is None:
        structured = json.loads(
            next(c["text"] for c in result.get("content", []) if c.get("type") == "text")
        )
    return [
        SearchResult(
            url=row["url"],
            title=row.get("title", row["url"]),
            snippet="\n".join(row.get("highlights", [])) or row.get("text", ""),
            published_at=row.get("publishedDate"),
            provider="Exa",
        )
        for row in structured.get("results", [])[:10]
    ]


class Providers:
    def __init__(self, store: Store, values: dict[str, Any], fixtures: Fixtures) -> None:
        self.store, self.values, self.fixtures = store, values, fixtures
        self.cooldowns = _COOLDOWNS.setdefault(store, {})

    def cooldown_key(self, provider: str) -> str:
        key = str(self.values.get("web.ollama_api_key", "")) if provider == "ollama" else ""
        return provider + ":" + hashlib.sha256(key.encode()).hexdigest()

    def limited(self, provider: str) -> bool:
        return self.cooldowns.get(self.cooldown_key(provider), 0) > monotonic()

    def cache_key(self, queries: list[str] | str, freshness: str) -> str:
        config = {
            k: v
            for k, v in self.values.items()
            if k
            in ("web.provider_order", "web.searxng_url", "web.brave_api_key", "web.ollama_api_key")
        }
        return hashlib.sha256(
            json.dumps([queries, freshness, config], sort_keys=True).encode()
        ).hexdigest()

    def configured(self, provider: str) -> bool:
        return (
            bool(self.values.get("web.ollama_api_key"))
            if provider == "ollama"
            else bool(self.values.get("web.searxng_url"))
            if provider == "searxng"
            else bool(self.values.get("web.brave_api_key"))
            if provider == "brave"
            else provider in ("ddgs", "exa")
        )

    async def status(self) -> list[SearchStatus]:
        out: list[SearchStatus] = []
        for p in self.values["web.provider_order"]:
            configured = self.configured(p)
            reachable = configured
            error = None
            if self.limited(p):
                reachable = False
                error = NAMES[p] + " is rate-limited; using another provider until retry time"
            if p == "searxng" and configured and not self.fixtures.directory:
                try:
                    async with httpx.AsyncClient(timeout=2, trust_env=False) as client:
                        response = await client.get(
                            str(self.values["web.searxng_url"]).rstrip("/") + "/config"
                        )
                        response.raise_for_status()
                except httpx.HTTPError:
                    reachable = False
                    error = "SearXNG isn't running"
            out.append(
                SearchStatus(provider=p, configured=configured, reachable=reachable, error=error)
            )
        return out

    async def request(self, provider: str, query: str, freshness: str) -> list[SearchResult]:
        replay = self.fixtures.search(provider, query, freshness)
        if replay is not None:
            return replay
        if not self.configured(provider):
            raise ValueError(NAMES[provider] + " is not configured")
        if self.limited(provider):
            raise ValueError(NAMES[provider] + " is rate-limited; waiting for retry time")
        time_range = {} if freshness == "any" else {"time_range": freshness}
        try:
            if provider == "exa":
                out = await exa_search(query, freshness)
            elif provider == "ddgs":

                def search() -> list[SearchResult]:
                    raw = DDGS(timeout=8).text(
                        query,
                        region="us-en",
                        safesearch="moderate",
                        timelimit=None if freshness == "any" else freshness[0],
                        max_results=10,
                        backend="duckduckgo",
                    )
                    return [
                        SearchResult(
                            url=r["href"],
                            title=r["title"],
                            snippet=r.get("body", ""),
                            provider=NAMES[provider],
                        )
                        for r in raw
                    ]

                async with asyncio.timeout(8):
                    out = await asyncio.to_thread(search)
            else:
                async with httpx.AsyncClient(timeout=8, trust_env=False) as client:
                    if provider == "ollama":
                        response = await client.post(
                            "https://ollama.com/api/web_search",
                            json={"query": query, "max_results": 10},
                            headers={
                                "Authorization": "Bearer " + str(self.values["web.ollama_api_key"])
                            },
                        )
                        if response.status_code in (401, 403, 429):
                            if response.status_code == 429:
                                raise RateLimited(
                                    "Ollama search usage limit reached",
                                    response.headers.get("Retry-After"),
                                )
                            raise ValueError(
                                "Ollama search key rejected"
                                if response.status_code in (401, 403)
                                else "Ollama search usage limit reached"
                            )
                    elif provider == "searxng":
                        response = await client.get(
                            str(self.values["web.searxng_url"]).rstrip("/") + "/search",
                            params={
                                "q": query,
                                "format": "json",
                                "categories": "general",
                                "safesearch": "0",
                                "language": "en",
                                **time_range,
                            },
                        )
                        if response.status_code == 403:
                            raise ValueError(
                                "SearXNG JSON output is disabled (add json to search.formats)"
                            )
                    else:
                        fresh = {} if freshness == "any" else {"freshness": "p" + freshness[0]}
                        response = await client.get(
                            "https://api.search.brave.com/res/v1/web/search",
                            params={"q": query, "count": "10", **fresh},
                            headers={"X-Subscription-Token": str(self.values["web.brave_api_key"])},
                        )
                        if response.status_code in (401, 429):
                            raise ValueError(
                                "Brave key rejected"
                                if response.status_code == 401
                                else "Brave rate limit"
                            )
                    response.raise_for_status()
                    raw = response.json()
                    rows = (
                        raw.get("results", [])
                        if provider in ("searxng", "ollama")
                        else raw.get("web", {}).get("results", [])
                    )
                    if provider == "searxng" and not rows and raw.get("unresponsive_engines"):
                        reasons = "; ".join(
                            str(engine[0]) + ": " + str(engine[1])
                            for engine in raw["unresponsive_engines"]
                            if isinstance(engine, list) and len(engine) >= 2
                        )
                        raise ValueError("SearXNG engines unavailable: " + reasons[:160])
                    out = [
                        SearchResult(
                            url=r["url"],
                            title=r.get("title", r["url"]),
                            snippet=r.get("content", r.get("description", "")),
                            published_at=r.get("publishedDate", r.get("page_age")),
                            provider=NAMES[provider],
                        )
                        for r in rows[:10]
                    ]
            self.fixtures.save_search(provider, query, freshness, out)
            return out
        except RateLimited as exc:
            self.cooldowns[self.cooldown_key(provider)] = monotonic() + exc.seconds
            raise
        except httpx.ConnectError as exc:
            raise ValueError(
                "SearXNG isn't running" if provider == "searxng" else "connection failed"
            ) from exc
        except (TimeoutError, httpx.TimeoutException) as exc:
            raise ValueError(NAMES[provider] + " timed out") from exc
        except httpx.HTTPError as exc:
            raise ValueError(NAMES[provider] + " returned an error") from exc
        except Exception as exc:
            detail = str(exc).lower()
            if provider == "ddgs" and any(w in detail for w in ("ratelimit", "rate limit", "429")):
                raise ValueError("DuckDuckGo rate-limited this request") from exc
            raise

    async def query(self, query: str, freshness: str) -> tuple[list[SearchResult], str | None]:
        key = self.cache_key(query, freshness)
        cached = await self.store.one(
            "SELECT results_json FROM search_cache WHERE key=? AND expires_at>?",
            (key, datetime.now(UTC).isoformat()),
        )
        if cached and not self.fixtures.recording:
            return [
                SearchResult.model_validate(r) for r in json.loads(str(cached["results_json"]))
            ], None
        errors: list[str] = []
        successful = False
        for p in self.values["web.provider_order"]:
            if not self.configured(p):
                continue
            try:
                results = await self.request(p, query, freshness)
                successful = True
                if results:
                    await self.store.execute(
                        "INSERT OR REPLACE INTO search_cache VALUES (?,?,?)",
                        (
                            key,
                            json.dumps([r.model_dump() for r in results]),
                            (datetime.now(UTC) + timedelta(minutes=30)).isoformat(),
                        ),
                    )
                    return results, None
            except Exception as exc:
                self.fixtures.save_error(p, query, freshness, str(exc)[:200])
                errors.append(str(exc)[:200])
        return [], None if successful else "; ".join(errors) or "No search provider configured"

    async def search(
        self, queries: list[str], freshness: str
    ) -> tuple[list[list[SearchResult]], list[str]]:
        key = self.cache_key(queries, freshness)
        date = datetime.now(UTC)
        cached = await self.store.one(
            "SELECT results_json FROM search_cache WHERE key=? AND expires_at>?",
            (key, date.isoformat()),
        )
        if cached and not self.fixtures.recording:
            return [
                [SearchResult.model_validate(r) for r in batch]
                for batch in json.loads(str(cached["results_json"]))
            ], []
        batches = await asyncio.gather(*(self.query(q, freshness) for q in queries))
        results = [r for r, _ in batches]
        errors = [e for _, e in batches if e]
        if any(results):
            await self.store.execute(
                "INSERT OR REPLACE INTO search_cache VALUES (?,?,?)",
                (
                    key,
                    json.dumps([[r.model_dump() for r in batch] for batch in results]),
                    (date + timedelta(minutes=30)).isoformat(),
                ),
            )
        return results, errors
