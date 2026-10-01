import json
import socket
from pathlib import Path
from typing import Any
from unittest.mock import Mock

import httpx
import pytest
from fastapi import FastAPI

from app.providers.base import ChatRequest, ProviderMessage
from app.providers.ollama import Ollama
from app.schemas import Passage, SearchResult
from app.search import cache, citations, planner, prompt
from app.search.chunk import chunk
from app.search.extract import _Text, extract
from app.search.fetch import RawPage, _public_address, fetch_public
from app.search.fixtures import Fixtures
from app.search.merge import canonical, merge
from app.search.providers import Providers
from app.search.rank import bm25, cosine, rank, select
from tests.test_chat import finish

VECTORS = json.loads((Path(__file__).parents[2] / "shared/citation_cases.json").read_text())


@pytest.mark.parametrize("vector", VECTORS)
def test_citations(vector: dict[str, Any]) -> None:
    assert citations.normalize(vector["in"], vector["n"]) == vector["out"]


def test_cited_ignores_code_and_links() -> None:
    assert citations.cited("Fact [1][2] `arr[9]` [3](https://x.y)") == {1, 2}


@pytest.mark.parametrize(
    "url",
    [
        "http://example.org",
        "https://localhost",
        "https://127.0.0.1",
        "https://[::1]",
        "https://10.0.0.1",
        "https://192.168.1.2",
        "https://169.254.169.254",
        "https://a.local",
        "https://a.internal",
        "https://u:p@example.org",
        "https://example.org:8443",
    ],
)
def test_ssrf_denies(url: str, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(socket, "getaddrinfo", lambda *a, **k: [(2, 1, 6, "", ("127.0.0.1", 443))])
    with pytest.raises(ValueError):
        _public_address(url)


def test_dns_all_addresses_and_unicode_path(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        socket, "getaddrinfo", lambda *a, **k: [(2, 1, 6, "", ("93.184.216.34", 443))]
    )
    host, ip, path = _public_address("https://example.org/café–tea?q=日")
    assert host == "example.org" and ip == "93.184.216.34" and path.isascii()
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda *a, **k: [(2, 1, 6, "", ("93.184.216.34", 443)), (2, 1, 6, "", ("127.0.0.1", 443))],
    )
    with pytest.raises(ValueError):
        _public_address("https://example.org")


@pytest.mark.parametrize(
    "location", ["http://example.org", "https://localhost", "https://example.org:8080"]
)
def test_redirect_revalidates(location: str, monkeypatch: pytest.MonkeyPatch) -> None:
    from app.search import fetch

    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda host, *a, **k: [
            (2, 1, 6, "", ("127.0.0.1" if host == "localhost" else "93.184.216.34", 443))
        ],
    )
    response = Mock(status=302)
    response.getheader.return_value = location
    conn = Mock()
    conn.getresponse.return_value = response
    monkeypatch.setattr(fetch, "_PinnedHTTPS", lambda *a: conn)
    with pytest.raises(ValueError, match="not a public address"):
        fetch_public("https://example.org")
    assert conn.close.called


def test_fetch_gzip_and_caps(monkeypatch: pytest.MonkeyPatch) -> None:
    import gzip

    from app.search import fetch

    monkeypatch.setattr(fetch, "_public_address", lambda u: ("example.org", "93.184.216.34", "/"))
    response = Mock(status=200)
    response.getheader.side_effect = lambda key, default="": {
        "Content-Encoding": "gzip",
        "Content-Type": "text/plain",
    }.get(key, default)
    response.read.return_value = gzip.compress(b"word " * 100)
    conn = Mock()
    conn.getresponse.return_value = response
    monkeypatch.setattr(fetch, "_PinnedHTTPS", lambda *a: conn)
    assert fetch_public("https://example.org").data == b"word " * 100
    response.read.return_value = gzip.compress(b"x" * 10_000_001)
    with pytest.raises(ValueError, match="too large"):
        fetch_public("https://example.org")
    response.read.return_value = b"x" * 3_000_001
    with pytest.raises(ValueError, match="too large"):
        fetch_public("https://example.org")


def test_merge_security_rrf_and_domain_cap() -> None:
    assert (
        canonical("HTTP://WWW.Example.org/a/?utm_source=x&v=1#hash") == "https://example.org/a?v=1"
    )
    assert canonical("https://u:p@example.org") == ""
    batches = [
        [
            SearchResult(url=u, title=u)
            for u in [
                "https://a.org/1",
                "https://a.org/2",
                "https://a.org/3",
                "https://b.org/file.zip",
                "https://blocked.org/page",
                "javascript:alert(1)",
            ]
        ],
        [SearchResult(url="http://a.org/2#hash", title="duplicate")],
    ]
    assert [r.url for r in merge(batches, ["blocked.org"])] == [
        "https://a.org/2",
        "https://a.org/1",
    ]


def test_chunk_tables_repeat_headers_and_bound_prose() -> None:
    table = "| Year | Result |\n| --- | --- |\n" + "\n".join(
        f"| {i} | {'A' * 100} |" for i in range(100)
    )
    ps = chunk("https://x.org", "# Results\n\n" + table + "\n\n" + "Sentence. " * 500)
    tables = [p for p in ps if p.text.startswith("|")]
    assert len(tables) > 1 and all(
        p.text.startswith("| Year | Result |") and len(p.text) <= 3000 for p in tables
    )
    assert all(p.heading == "Results" for p in ps)
    assert all(len(p.text) <= 1600 for p in ps if not p.text.startswith("|"))
    assert list(range(len(ps))) == [p.ord for p in ps]
    assert "| 99 |" in "\n".join(p.text for p in tables)


def test_extract_html_metadata_tables_and_rejects() -> None:
    html = (
        '<html><head><title>Results</title><meta charset="utf-8"></head>'
        "<body><article><h1>Results</h1><p>"
        + "Basketball finals scores. "
        * 60
        + "</p><table><tr><th>Year</th><th>Winner</th></tr>"
        "<tr><td>2021</td><td>Bucks</td></tr></table></article></body></html>"
    )
    page = extract(RawPage("https://example.org", html.encode(), "text/html"))
    assert "2021" in page.text and "Bucks" in page.text and "|" in page.text
    assert len(page.text) <= 80000
    with pytest.raises(ValueError, match="blocked or needs JavaScript"):
        extract(
            RawPage(
                "https://example.org", b"Please enable JavaScript and cookies policy", "text/plain"
            )
        )
    with pytest.raises(ValueError, match="unsupported type"):
        extract(RawPage("https://example.org", b"binary", "image/png"))
    with pytest.raises(ValueError, match="too little"):
        extract(RawPage("https://example.org", b"short", "text/plain"))
    parser = _Text()
    parser.feed(html)
    assert "Basketball" in "".join(parser.main_parts)


def test_rank_keyword_select_diversity_and_budget() -> None:
    ps = [
        Passage(source_url="https://a.org", ord=i, text="Basketball NBA Finals Bucks Suns " * 20)
        for i in range(5)
    ] + [Passage(source_url="https://b.org", ord=0, text="Basketball NBA Finals results " * 20)]
    assert bm25("NBA", ["NBA Finals", "cooking recipes"])[0] > 0
    assert bm25("NBA", ["NBA Finals", "cooking recipes"])[1] == 0
    ranked = rank(ps, "NBA Finals", ["https://a.org", "https://b.org"])
    chosen = select(ranked, 1500, 4)
    assert len(chosen) == 2 and max(len(g) for g in chosen) <= 3
    assert sum(round(len(p.text) * 0.3) + 20 for g in chosen for p in g) <= 1500
    assert cosine([1, 0], [1, 0]) == 1 and cosine([0, 0], [1, 0]) == 0
    with pytest.raises(ValueError):
        cosine([1], [1, 2])
    hybrid = rank(
        ps, "NBA", ["https://a.org", "https://b.org"], [[1.0, 0.0]] + [[1.0, 0.0]] * len(ps)
    )
    assert len(hybrid) == len(ps)
    assert select([], 1500, 6) == []


async def test_planner_schema_transcript_and_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    adapter = Mock()
    captured: list[ChatRequest] = []

    async def complete(req: ChatRequest) -> dict[str, Any]:
        captured.append(req)
        return {"search": True, "queries": ["NBA Finals", " nba finals ", ""], "freshness": "any"}

    adapter.complete_json = complete
    # Empty strings from an imperfect runtime are trimmed as the spec requires.
    result, fallback = await planner.plan(
        adapter,
        "m",
        "what about 2020?",
        [ProviderMessage("user", "Who won 2021 NBA Finals?")],
        True,
        8192,
    )
    assert result.queries == ["NBA Finals"] and not fallback
    assert (
        captured[0].params == {"temperature": 0.2, "max_tokens": 256}
        and captured[0].json_schema == planner.SCHEMA
    )
    assert "Conversation so far:" in captured[0].messages[1].content

    async def bad(req: ChatRequest) -> dict[str, Any]:
        raise ValueError("invalid JSON")

    adapter.complete_json = bad
    result, fallback = await planner.plan(
        adapter,
        "m",
        "and the year before?",
        [ProviderMessage("user", "Who won 2021 NBA Finals?")],
        False,
        8192,
    )
    assert fallback and "Who won 2021" in result.queries[0] and result.freshness == "any"
    assert (
        planner.heuristic("long standalone question with many different words", [])
        == "long standalone question with many different words"
    )


async def test_pipeline_cites_exact_sources_and_skips_without_traffic(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI], monkeypatch: pytest.MonkeyPatch
) -> None:
    app, client, runtime = chat_app
    calls: list[str] = []

    async def complete(self: Ollama, req: ChatRequest) -> dict[str, Any]:
        latest = req.messages[-1].content.split("Latest user message:\n")[-1]
        return {
            "search": latest != "thanks!",
            "queries": ["NBA Finals 2021"] if latest != "thanks!" else [],
            "freshness": "month",
        }

    monkeypatch.setattr(Ollama, "complete_json", complete)

    async def search(self: Providers, provider: str, q: str, f: str) -> list[SearchResult]:
        assert f == "month"
        calls.append(q)
        return [
            SearchResult(
                url="https://example.org/2021",
                title="NBA Finals",
                snippet="Bucks beat Suns.",
                provider="DuckDuckGo",
            )
        ]

    monkeypatch.setattr(Providers, "request", search)
    from app.search.extract import Page

    async def read(*a: Any, **k: Any) -> Page:
        return Page(
            "https://example.org/2021",
            "NBA Finals",
            "NBA",
            None,
            "Milwaukee Bucks defeated Phoenix Suns 4–2 in the 2021 NBA Finals. " * 20,
        )

    monkeypatch.setattr(cache, "read", read)
    conn = (await client.get("/api/connections")).json()[0]["id"]
    chat = (
        await client.post(
            "/api/chats", json={"connection_id": conn, "model_id": "fake-chat", "web_enabled": True}
        )
    ).json()
    response = (
        await client.post(
            f"/api/chats/{chat['id']}/messages",
            json={"content": "#cite Who lost the 2021 NBA Finals?"},
        )
    ).json()
    run = await finish(app, response)
    assert run.message.status == "complete", run.message.error
    detail = (await client.get("/api/chats/" + chat["id"])).json()
    assert detail["messages"][-1]["web"]["freshness"] == "month"
    assert run.message.id in detail["sources"], run.message.web
    source = detail["sources"][run.message.id][0]
    assert source["cited"] and "Phoenix Suns" in source["passages"][0]["text"]
    assert "[9]" not in run.message.content
    answer_request = runtime.state.captures[-1]
    assert "<search_results" in answer_request["messages"][-1]["content"]
    assert "web search results" in answer_request["messages"][0]["content"]
    count = len(calls)
    response = (
        await client.post(
            f"/api/chats/{chat['id']}/messages",
            json={"content": "thanks!", "parent_id": run.message.id},
        )
    ).json()
    run = await finish(app, response)
    assert run.message.web.status == "skipped" and len(calls) == count
    assert "<search_results" not in runtime.state.captures[-1]["messages"][-1]["content"]
    assert all(
        "<search_results" not in m["content"] for m in runtime.state.captures[-1]["messages"]
    )
    replay = (await client.get("/api/runs/" + run.id + "/events")).text
    assert "search.skipped" in replay


async def test_provider_fallback_cache_and_failure(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI], monkeypatch: pytest.MonkeyPatch
) -> None:
    app, _, _ = chat_app
    values = {
        "web.provider_order": ["searxng", "ddgs", "brave"],
        "web.searxng_url": "http://fake",
        "web.brave_api_key": None,
    }
    p = Providers(app.state.store, values, Fixtures())
    called: list[str] = []

    async def request(provider: str, q: str, f: str) -> list[SearchResult]:
        called.append(provider)
        if provider == "searxng":
            raise ValueError("not running")
        return [SearchResult(url="https://example.org", title="Example", provider="DuckDuckGo")]

    monkeypatch.setattr(p, "request", request)
    batches, errors = await p.search(["Example"], "any")
    assert not errors and called == ["searxng", "ddgs"] and batches[0][0].provider == "DuckDuckGo"
    await p.search(["Example"], "any")
    assert called == ["searxng", "ddgs"]

    async def fail(*a: Any) -> list[SearchResult]:
        raise ValueError("failed")

    monkeypatch.setattr(p, "request", fail)
    rows, error = await p.query("other", "any")
    assert not rows and error


async def test_fixture_replay_and_page_cache(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI], tmp_path: Path
) -> None:
    app, _, _ = chat_app
    recording = Fixtures(recording=tmp_path)
    raw = RawPage(
        "https://example.org", b"Facts about scientific measurements. " * 30, "text/plain"
    )
    recording.save_page(raw.url, raw)
    result = SearchResult(url=raw.url, title="Facts")
    recording.save_search("ddgs", "facts", "any", [result])
    replay = Fixtures(tmp_path)
    assert replay.search("ddgs", "facts", "any") == [result]
    page = await cache.read(app.state.store, raw.url, 7, replay)
    assert len(page.text) > 300
    again = await cache.read(app.state.store, raw.url, 7, Fixtures())
    assert again.text == page.text
    with pytest.raises(ValueError):
        replay.search("ddgs", "missing", "any")


def test_prompts_are_exact_spec_and_escape_source_attributes() -> None:
    spec = (Path(__file__).parents[2] / "docs/SPEC.md").read_text()
    for text in (planner.PROMPT, prompt.PROMPT):
        assert text in spec


async def test_live_provider_parsers_and_specific_errors(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI], monkeypatch: pytest.MonkeyPatch
) -> None:
    import respx

    app, _, _ = chat_app
    values = {
        "web.provider_order": ["searxng", "ddgs", "brave"],
        "web.searxng_url": "http://searx.test",
        "web.brave_api_key": "test-not-secret",
    }
    service = Providers(app.state.store, values, Fixtures())
    with respx.mock:
        searx = respx.get("http://searx.test/search").mock(
            return_value=httpx.Response(
                200,
                json={
                    "results": [
                        {
                            "url": "https://x.org",
                            "title": "X",
                            "content": "A fact",
                            "publishedDate": "2026-01-01",
                        }
                    ]
                },
            )
        )
        brave = respx.get("https://api.search.brave.com/res/v1/web/search").mock(
            return_value=httpx.Response(
                200,
                json={
                    "web": {
                        "results": [
                            {
                                "url": "https://b.org",
                                "title": "B",
                                "description": "Fact",
                                "page_age": "2026-01-02",
                            }
                        ]
                    }
                },
            )
        )
        respx.get("http://searx.test/config").mock(return_value=httpx.Response(200, json={}))
        assert (await service.request("searxng", "fact", "week"))[0].provider == "SearXNG"
        assert "time_range=week" in str(searx.calls[-1].request.url)
        assert (await service.request("brave", "fact", "day"))[0].provider == "Brave"
        assert brave.calls[-1].request.headers["X-Subscription-Token"] == "test-not-secret"
        assert all(s.reachable for s in await service.status())
        searx.mock(
            return_value=httpx.Response(
                200,
                json={
                    "results": [],
                    "unresponsive_engines": [
                        ["google cse", "too many requests"],
                        ["yahoo", "HTTP error"],
                    ],
                },
            )
        )
        with pytest.raises(ValueError, match="engines unavailable.*too many requests"):
            await service.request("searxng", "fact", "any")
        searx.mock(
            return_value=httpx.Response(
                200,
                json={
                    "results": [{"url": "https://working.org", "title": "Available source"}],
                    "unresponsive_engines": [["google cse", "too many requests"]],
                },
            )
        )
        assert (await service.request("searxng", "fact", "any"))[0].url == "https://working.org"
        searx.mock(return_value=httpx.Response(403))
        with pytest.raises(ValueError, match="JSON output is disabled"):
            await service.request("searxng", "fact", "any")
        for status, reason in [(401, "key rejected"), (429, "rate limit")]:
            brave.mock(return_value=httpx.Response(status))
            with pytest.raises(ValueError, match=reason):
                await service.request("brave", "fact", "any")
        searx.mock(side_effect=httpx.ConnectError("connection failed"))
        with pytest.raises(ValueError, match="isn't running"):
            await service.request("searxng", "fact", "any")
        brave.mock(side_effect=httpx.ReadTimeout("timeout"))
        with pytest.raises(ValueError, match="timed out"):
            await service.request("brave", "fact", "any")
        brave.mock(return_value=httpx.Response(500))
        with pytest.raises(ValueError, match="returned an error"):
            await service.request("brave", "fact", "any")
    from app.search import providers as provider_module

    class FakeDDGS:
        def __init__(self, timeout: int) -> None:
            assert timeout == 8

        def text(self, *a: Any, **k: Any) -> list[dict[str, str]]:
            assert k["backend"] == "duckduckgo" and k["timelimit"] == "m"
            return [{"href": "https://d.org", "title": "D", "body": "Fact"}]

    monkeypatch.setattr(provider_module, "DDGS", FakeDDGS)
    assert (await service.request("ddgs", "fact", "month"))[0].provider == "DuckDuckGo"

    class RateDDGS(FakeDDGS):
        def text(self, *a: Any, **k: Any) -> list[dict[str, str]]:
            raise ValueError("429 rate limit")

    monkeypatch.setattr(provider_module, "DDGS", RateDDGS)
    with pytest.raises(ValueError, match="rate-limited"):
        await service.request("ddgs", "fact", "any")
    service.values["web.brave_api_key"] = None
    with pytest.raises(ValueError, match="not configured"):
        await service.request("brave", "fact", "any")


async def test_embedding_cache_dedup_and_validation(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI],
) -> None:
    app, _, _ = chat_app
    adapter = Mock()
    calls = []

    async def embed(model: str, texts: list[str]) -> list[list[float]]:
        calls.append(texts)
        return [[1.0, float(i)] for i in range(len(texts))]

    adapter.embed = embed
    first = await cache.embed(app.state.store, adapter, "embedding", ["a", "b", "a"])
    second = await cache.embed(app.state.store, adapter, "embedding", ["a", "b", "a"])
    assert first == second and len(calls) == 1 and first[0] == first[2]

    async def bad(model: str, texts: list[str]) -> list[list[float]]:
        return []

    adapter.embed = bad
    with pytest.raises(ValueError, match="wrong length"):
        await cache.embed(app.state.store, adapter, "embedding", ["missing"])


@pytest.mark.parametrize(
    "mode",
    [
        "no-results",
        "error",
        "unreadable",
        "snippets",
        "uncited",
        "embedding-fails",
        "utility-missing",
    ],
)
async def test_pipeline_failures_still_answer(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI], monkeypatch: pytest.MonkeyPatch, mode: str
) -> None:
    app, client, _ = chat_app

    async def complete(self: Ollama, req: ChatRequest) -> dict[str, Any]:
        return {"search": True, "queries": ["Public facts"], "freshness": "any"}

    monkeypatch.setattr(Ollama, "complete_json", complete)

    async def request(self: Providers, provider: str, q: str, f: str) -> list[SearchResult]:
        if mode == "error":
            raise ValueError("all unavailable")
        if mode == "no-results":
            return []
        return [
            SearchResult(
                url="https://example.org",
                title="Facts",
                snippet="A useful public fact about measurements." if mode == "snippets" else "",
                provider="DuckDuckGo",
            )
        ]

    monkeypatch.setattr(Providers, "request", request)
    from app.search.extract import Page

    async def read(*a: Any, **k: Any) -> Page:
        if mode in ("unreadable", "snippets"):
            raise ValueError("HTTP 403")
        return Page(
            "https://example.org",
            "Facts",
            "Example",
            "2026-01-01",
            "The useful public fact about measurements is cited. " * 20,
        )

    monkeypatch.setattr(cache, "read", read)
    conn = (await client.get("/api/connections")).json()[0]["id"]
    if mode == "utility-missing":
        await client.patch(
            "/api/settings", json={"utility_model": {"connection_id": conn, "model_id": "missing"}}
        )
    if mode == "embedding-fails":
        await client.patch(
            "/api/settings",
            json={"web.embedding": {"connection_id": conn, "model_id": "not-installed"}},
        )
    chat = (
        await client.post(
            "/api/chats", json={"connection_id": conn, "model_id": "fake-chat", "web_enabled": True}
        )
    ).json()
    response = (
        await client.post(
            "/api/chats/" + chat["id"] + "/messages", json={"content": "#uncited Public facts"}
        )
    ).json()
    run = await finish(app, response)
    assert run.message.status == "complete" and run.message.content
    info = run.message.web
    assert info is not None
    expected = {
        "no-results": "search_no_results",
        "error": "search_failed",
        "unreadable": "pages_unreadable",
    }
    if mode in expected:
        assert info.notice and info.notice.code == expected[mode]
    else:
        assert info.notice and info.notice.code == "uncited"
    if mode == "embedding-fails":
        assert "unavailable" in info.ranking
    if mode == "snippets":
        detail = (await client.get("/api/chats/" + chat["id"])).json()
        assert detail["sources"][run.message.id][0]["kind"] == "snippet"
    assert "This answer uses" not in run.message.content
