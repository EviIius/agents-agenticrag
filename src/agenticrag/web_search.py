"""Public result discovery; the chat pipeline separately reads source pages."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from importlib.util import find_spec
from typing import Protocol
from urllib.parse import urlsplit, urlencode
from urllib.request import Request, urlopen

from .errors import ProviderError, WorkflowError


def local_web_search_available() -> bool:
    choice = os.environ.get("AGENTICRAG_WEB_PROVIDER", "duckduckgo").lower()
    if choice == "searxng":
        try:
            SearXNGSearch(os.environ.get("AGENTICRAG_SEARXNG_URL", ""))
            return True
        except ValueError:
            return False
    if choice == "brave":
        return bool(os.environ.get("AGENTICRAG_BRAVE_API_KEY"))
    return choice == "duckduckgo" and find_spec("ddgs") is not None


def configured_search_provider() -> "SearchProvider":
    choice = os.environ.get("AGENTICRAG_WEB_PROVIDER", "duckduckgo").lower()
    if choice == "searxng":
        return SearXNGSearch(os.environ.get("AGENTICRAG_SEARXNG_URL", ""))
    if choice == "brave":
        return BraveSearch(os.environ.get("AGENTICRAG_BRAVE_API_KEY", ""))
    if choice == "duckduckgo":
        return LocalWebSearch()
    raise ValueError("AGENTICRAG_WEB_PROVIDER must be duckduckgo, searxng, or brave")


def configured_search_label() -> str:
    return {"duckduckgo": "Public web search", "searxng": "SearXNG", "brave": "Brave Search"}.get(
        os.environ.get("AGENTICRAG_WEB_PROVIDER", "duckduckgo").lower(), "Unavailable")


@dataclass(frozen=True)
class WebHit:
    title: str
    url: str
    snippet: str


class SearchProvider(Protocol):
    def search_results(self, query: str, *, max_results: int) -> tuple[WebHit, ...]: ...


class LocalWebSearch:
    label = "Public web search"
    def __init__(self, search=None) -> None:  # type: ignore[no-untyped-def]
        self._search = search

    def search_results(self, query: str, *, max_results: int = 5) -> tuple[WebHit, ...]:
        """Return ranked public results without generating an answer."""
        if not 1 <= len(query.strip()) <= 500 or not 1 <= max_results <= 10:
            raise WorkflowError("Web search query or result limit is invalid")
        if self._search is None:
            try:
                from ddgs import DDGS
            except ImportError as exc:
                raise ProviderError("Local web search is not installed; install agenticrag[web]") from exc
            # Bound metasearch to two engines instead of DDGS's entire auto pool.
            search = lambda value: DDGS(timeout=12).text(
                value, backend="duckduckgo,brave", max_results=max_results)
        else:
            search = self._search
        try:
            rows = search(query.strip())
        except Exception as exc:
            message = str(exc).lower()
            reason = ("provider rate limited the request" if "ratelimit" in message or "rate limit" in message or "429" in message else
                      "provider timed out" if "timeout" in message or "timed out" in message else
                      "provider blocked access" if "403" in message else "provider request failed")
            raise ProviderError(f"Web search failed: {reason} ({type(exc).__name__})") from exc
        if not isinstance(rows, list):
            raise ProviderError("Web search returned an invalid result list")
        hits = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            url = str(row.get("href") or row.get("url") or "")[:2_048]
            parsed = urlsplit(url)
            if parsed.scheme != "https" or not parsed.netloc:
                continue
            hits.append(WebHit(str(row.get("title") or url)[:200], url,
                               str(row.get("body") or row.get("content") or "")[:1_200]))
            if len(hits) >= max_results:
                break
        return tuple(hits)

class SearXNGSearch:
    label = "SearXNG"

    def __init__(self, base_url: str) -> None:
        parsed = urlsplit(base_url)
        if (not parsed.netloc or parsed.username or parsed.password or parsed.query or parsed.fragment
                or parsed.scheme not in {"http", "https"}
                or (parsed.scheme == "http" and parsed.hostname not in {"localhost", "127.0.0.1", "::1"})):
            raise ValueError("SearXNG URL must be HTTPS or local HTTP without credentials or query")
        self.base_url = base_url.rstrip("/")

    def search_results(self, query: str, *, max_results: int) -> tuple[WebHit, ...]:
        _validate_search_request(query, max_results)
        url = self.base_url + "/search?" + urlencode({"q": query, "format": "json"})
        payload = _search_json(Request(url, headers={"Accept": "application/json"}))
        rows = payload.get("results", [])
        if not isinstance(rows, list):
            raise ProviderError("SearXNG returned invalid results")
        return _hits(rows, max_results, "url", "content")


class BraveSearch:
    label = "Brave Search"

    def __init__(self, api_key: str) -> None:
        if not api_key.strip():
            raise ValueError("AGENTICRAG_BRAVE_API_KEY is required")
        self.api_key = api_key.strip()

    def search_results(self, query: str, *, max_results: int) -> tuple[WebHit, ...]:
        _validate_search_request(query, max_results)
        url = "https://api.search.brave.com/res/v1/web/search?" + urlencode({
            "q": query, "count": max_results,
        })
        payload = _search_json(Request(url, headers={
            "Accept": "application/json", "X-Subscription-Token": self.api_key,
        }))
        web = payload.get("web", {})
        rows = web.get("results", []) if isinstance(web, dict) else []
        if not isinstance(rows, list):
            raise ProviderError("Brave Search returned invalid results")
        return _hits(rows, max_results, "url", "description")


def _validate_search_request(query: str, max_results: int) -> None:
    if not 1 <= len(query.strip()) <= 500 or not 1 <= max_results <= 10:
        raise WorkflowError("Web search query or result limit is invalid")


def _search_json(request: Request) -> dict:
    try:
        with urlopen(request, timeout=12) as response:  # noqa: S310
            raw = response.read(1_000_001)
    except Exception as exc:
        raise ProviderError(f"Web search failed: {type(exc).__name__}") from exc
    if len(raw) > 1_000_000:
        raise ProviderError("Web search response is too large")
    try:
        payload = json.loads(raw)
    except (ValueError, UnicodeDecodeError) as exc:
        raise ProviderError("Web search returned invalid JSON") from exc
    if not isinstance(payload, dict):
        raise ProviderError("Web search returned invalid JSON")
    return payload


def _hits(rows: list, limit: int, url_key: str, snippet_key: str) -> tuple[WebHit, ...]:
    hits = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        url = str(row.get(url_key) or "")[:2048]
        parsed = urlsplit(url)
        if parsed.scheme != "https" or not parsed.netloc:
            continue
        hits.append(WebHit(str(row.get("title") or url)[:200], url,
                           str(row.get(snippet_key) or "")[:1200]))
        if len(hits) >= limit:
            break
    return tuple(hits)
