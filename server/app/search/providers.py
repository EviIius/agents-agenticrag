import asyncio
import hashlib
import json
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx
from ddgs import DDGS

from ..db.core import Store
from ..schemas import SearchResult, SearchStatus
from .fixtures import Fixtures

NAMES = {"searxng": "SearXNG", "ddgs": "DuckDuckGo", "brave": "Brave"}


class Providers:
    def __init__(self, store: Store, values: dict[str, Any], fixtures: Fixtures) -> None:
        self.store, self.values, self.fixtures = store, values, fixtures

    def configured(self, provider: str) -> bool:
        return (
            bool(self.values.get("web.searxng_url"))
            if provider == "searxng"
            else bool(self.values.get("web.brave_api_key"))
            if provider == "brave"
            else provider == "ddgs"
        )

    async def status(self) -> list[SearchStatus]:
        out: list[SearchStatus] = []
        for p in self.values["web.provider_order"]:
            configured = self.configured(p)
            reachable = configured
            error = None
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
        time_range = {} if freshness == "any" else {"time_range": freshness}
        try:
            if provider == "ddgs":

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
                    if provider == "searxng":
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
                        if provider == "searxng"
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
        errors: list[str] = []
        successful = False
        for p in self.values["web.provider_order"]:
            if not self.configured(p):
                continue
            try:
                results = await self.request(p, query, freshness)
                successful = True
                if results:
                    return results, None
            except Exception as exc:
                self.fixtures.save_error(p, query, freshness, str(exc)[:200])
                errors.append(str(exc)[:200])
        return [], None if successful else "; ".join(errors) or "No search provider configured"

    async def search(
        self, queries: list[str], freshness: str
    ) -> tuple[list[list[SearchResult]], list[str]]:
        config = {
            k: v
            for k, v in self.values.items()
            if k in ("web.provider_order", "web.searxng_url", "web.brave_api_key")
        }
        key = hashlib.sha256(
            json.dumps([queries, freshness, config], sort_keys=True).encode()
        ).hexdigest()
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
