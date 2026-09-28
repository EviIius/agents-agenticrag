"""Opt-in public web search for local models, limited to result snippets."""

from __future__ import annotations

import time
from http.client import HTTPException
from importlib.util import find_spec
from urllib.parse import urlsplit

from .domain import ExternalSource
from .errors import ProviderError, WorkflowError
from .providers.openai_responses import WebSearchResult
from .web_pages import fetch_public_page


def local_web_search_available() -> bool:
    return find_spec("ddgs") is not None


class LocalWebSearch:
    def __init__(self, search=None, fetch_page=None) -> None:  # type: ignore[no-untyped-def]
        self._search = search
        # Injected search stubs stay offline unless a page fetcher is also supplied.
        self._fetch_page = fetch_page if fetch_page is not None else (fetch_public_page if search is None else None)

    def search(self, query: str) -> WebSearchResult:
        query = query.split("Assigned research task:")[-1].strip()
        if not 1 <= len(query) <= 500:
            raise WorkflowError("Web search query must contain 1 to 500 characters")
        if self._search is None:
            try:
                from ddgs import DDGS
            except ImportError as exc:
                raise ProviderError("Local web search is not installed; install agenticrag[web]") from exc
            search = lambda value: DDGS(timeout=12).text(value, max_results=5)
        else:
            search = self._search
        started = time.perf_counter()
        try:
            rows = search(query)
        except Exception as exc:
            raise ProviderError(f"Web search failed: {type(exc).__name__}") from exc
        if not isinstance(rows, list):
            raise ProviderError("Web search returned an invalid result list")
        sources: list[ExternalSource] = []
        snippets: list[str] = []
        for row in rows[:5]:
            if not isinstance(row, dict):
                continue
            url = str(row.get("href") or row.get("url") or "")[:2_048]
            if urlsplit(url).scheme not in {"http", "https"} or not urlsplit(url).netloc:
                continue
            title = str(row.get("title") or url)[:200]
            body = str(row.get("body") or row.get("content") or "")[:1_200]
            page_text = ""
            if self._fetch_page is not None and len(sources) < 2:
                try:
                    final_url, extracted = self._fetch_page(url)
                    url = final_url
                    page_text = extracted[:3_500]
                except (OSError, ValueError, TimeoutError, HTTPException):
                    pass
            source_id = f"web_{len(sources) + 1}"
            sources.append(ExternalSource(id=source_id, title=title, url=url))
            snippet = f"[{len(sources)}] {title}\nURL: {url}\nSearch excerpt: {body}"
            if page_text:
                snippet += f"\nFetched page text (untrusted): {page_text}"
            snippets.append(snippet)
        if not sources:
            raise ProviderError("Web search returned no usable results")
        return WebSearchResult(
            answer="\n\n".join(snippets),
            sources=tuple(sources),
            elapsed_ms=max(0, round((time.perf_counter() - started) * 1_000)),
        )
