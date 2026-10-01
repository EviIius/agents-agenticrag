"""Bounded host pipeline. Search/read/rank remain usable by future tools."""

import asyncio
import json
import re
from collections import Counter
from pathlib import Path
from time import monotonic
from urllib.parse import urlsplit

from ..db import messages, settings
from ..db.connections import now
from ..errors import AppError
from ..providers.base import ChatRequest, ProviderMessage
from ..runs.context import Context, path
from ..runs.manager import Run, RunManager
from ..schemas import ErrorDetail, Passage, SearchResult, Source, WebInfo
from . import cache, citations, planner, prompt
from .chunk import chunk
from .extract import Page
from .fixtures import Fixtures
from .merge import merge
from .providers import Providers
from .rank import rank, select


class Pipeline:
    def __init__(
        self, manager: RunManager, directory: Path | None = None, recording: Path | None = None
    ) -> None:
        self.manager = manager
        self.store = manager.store
        self.fixtures = Fixtures(directory, recording)

    async def fail(self, run: Run, code: str, detail: str) -> None:
        if run.message.web:
            run.message.web.status = "failed"
            run.message.web.notice = ErrorDetail(code=code, message=detail)
        await run.emit("search.failed", {"code": code, "message": detail})

    async def __call__(self, run: Run, request: ChatRequest, context: Context, force: bool) -> None:
        info = WebInfo(status="used")
        run.message.web = info
        await run.emit("search.planning", {})
        values = await settings.get(self.store)
        model = await self.manager.registry.resolve(
            run.message.model.connection_id if run.message.model else None, request.model_id
        )
        utility = values.get("utility_model")
        raw_history = path(
            await messages.list_messages(self.store, run.message.chat_id), run.message.parent_id
        )
        latest = raw_history[-1].content
        history = [ProviderMessage(m.role, m.content) for m in raw_history[:-1]]
        clock = monotonic()
        try:
            if utility:
                model = await self.manager.registry.resolve(
                    utility["connection_id"], utility["model_id"]
                )
            adapter = await self.manager.registry.adapter(model.connection_id)
            plan, fallback = await planner.plan(
                adapter,
                model.model_id,
                latest,
                history,
                bool(model.loaded),
                model.context_length,
                force,
            )
        except AppError:
            plan = planner.Plan(
                search=True, queries=[planner.heuristic(latest, history)], freshness="any"
            )
            fallback = True
        info.timings["plan"] = (monotonic() - clock) * 1000
        info.plan_fallback = fallback
        info.freshness = plan.freshness
        if not plan.search:
            info.status = "skipped"
            await run.emit("search.skipped", {"reason": "not_needed"})
            return
        info.queries = plan.queries
        await run.emit("search.queries", {"queries": plan.queries})
        clock = monotonic()
        batches, errors = await Providers(self.store, values, self.fixtures).search(
            plan.queries, plan.freshness
        )
        info.timings["search"] = (monotonic() - clock) * 1000
        info.providers = list(dict.fromkeys(r.provider for batch in batches for r in batch))
        candidates = merge(batches, values["web.blocked_domains"])
        await run.emit(
            "search.results", {"count": len(candidates), "provider": ", ".join(info.providers)}
        )
        if not candidates:
            await self.fail(
                run,
                "search_failed" if errors else "search_no_results",
                "; ".join(errors) if errors else plan.queries[0],
            )
            return
        pages: dict[str, Page] = {}
        reasons: list[str] = []
        semaphore = asyncio.Semaphore(6)
        clock = monotonic()
        limit = int(values["web.max_sources"])

        async def fetch(result: SearchResult) -> None:
            async with semaphore:
                if len(pages) >= limit:
                    return
                await run.emit(
                    "search.reading",
                    {
                        "url": result.url,
                        "title": result.title,
                        "site_name": urlsplit(result.url).hostname,
                        "domain": urlsplit(result.url).hostname,
                    },
                )
                try:
                    page = await cache.read(
                        self.store, result.url, int(values["web.page_cache_days"]), self.fixtures
                    )
                    if len(pages) < limit:
                        pages[result.url] = page
                    await self.store.execute(
                        "INSERT INTO web_reads VALUES (?,?,?,?,?,NULL)",
                        (run.message.id, result.url, page.title, page.site_name, "unused"),
                    )
                    await run.emit("search.read", {"url": result.url, "status": "ok"})
                except asyncio.CancelledError:
                    raise
                except Exception as exc:
                    reason = (
                        "timeout"
                        if isinstance(exc, TimeoutError)
                        else str(exc)[:160] or "connection failed"
                    )
                    self.fixtures.save_page_error(result.url, reason)
                    reasons.append(reason)
                    await self.store.execute(
                        "INSERT INTO web_reads VALUES (?,?,?,?,?,?)",
                        (
                            run.message.id,
                            result.url,
                            result.title,
                            urlsplit(result.url).hostname,
                            "failed",
                            reason,
                        ),
                    )
                    await run.emit(
                        "search.read", {"url": result.url, "status": "failed", "reason": reason}
                    )

        tasks = [asyncio.create_task(fetch(r)) for r in candidates]
        try:
            async with asyncio.timeout(12):
                await asyncio.gather(*tasks)
        except TimeoutError:
            reasons.append("timeout")
            for r, task in zip(candidates, tasks, strict=True):
                if task.cancelled():
                    await self.store.execute(
                        "INSERT OR IGNORE INTO web_reads VALUES (?,?,?,?,?,?)",
                        (
                            run.message.id,
                            r.url,
                            r.title,
                            urlsplit(r.url).hostname,
                            "failed",
                            "timeout",
                        ),
                    )
                    await run.emit(
                        "search.read", {"url": r.url, "status": "failed", "reason": "timeout"}
                    )
        finally:
            for task in tasks:
                if not task.done():
                    task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
        info.timings["fetch"] = (monotonic() - clock) * 1000
        passages: list[Passage] = []
        # Order by search rank, never by nondeterministic fetch completion order.
        for r in candidates:
            if r.url in pages:
                passages.extend(await asyncio.to_thread(chunk, r.url, pages[r.url].text))
        kinds: dict[str, str] = {}
        if len(pages) < 2:
            for r in candidates:
                if r.url not in pages and r.snippet.strip():
                    passages.append(
                        Passage(source_url=r.url, ord=0, text=r.title + "\n" + r.snippet)
                    )
                    kinds[r.url] = "snippet"
        if not passages:
            await self.fail(
                run,
                "pages_unreadable",
                Counter(reasons).most_common(1)[0][0] if reasons else "no readable text",
            )
            return
        vectors = None
        embedding = values.get("web.embedding")
        if embedding:
            clock = monotonic()
            try:
                embed_adapter = await self.manager.registry.adapter(embedding["connection_id"])
                vectors = await cache.embed(
                    self.store,
                    embed_adapter,
                    embedding["model_id"],
                    [latest + " " + " ".join(plan.queries)] + [p.text for p in passages],
                    embedding["connection_id"],
                )
                info.ranking = "hybrid"
            except Exception:
                info.ranking = "keyword only (embedding model unavailable)"
            info.timings["embed"] = (monotonic() - clock) * 1000
        clock = monotonic()
        ranked = rank(
            passages, latest + " " + " ".join(plan.queries), [r.url for r in candidates], vectors
        )
        remaining = (request.context_length or 8192) - context.reserve - context.used_tokens
        budget = max(1500, min(12000, int(0.45 * remaining)))
        groups = select(ranked, budget, limit, context.ratio)
        sources: list[Source] = []
        for n, group in enumerate(groups, 1):
            url = group[0].source_url
            r = next(r for r in candidates if r.url == url)
            page = pages.get(url)
            group = [
                p.model_copy(
                    update={
                        "text": re.sub(r"</(?:source|search_results)\s*>", "", p.text, flags=re.I)
                    }
                )
                for p in group
            ]
            source = Source(
                n=n,
                url=url,
                title=page.title
                if page and page.title != (urlsplit(url).hostname or "")
                else r.title,
                site_name=page.site_name if page else urlsplit(url).hostname or "",
                domain=urlsplit(url).hostname or "",
                published_at=page.published_at if page else r.published_at,
                fetched_at=now(),
                kind="snippet" if url in kinds else "page",
                passages=group,
            )
            sources.append(source)
            await self.store.execute(
                "INSERT INTO message_sources VALUES (?,?,?,?,?,?,?,?,0)",
                (
                    run.message.id,
                    n,
                    url,
                    source.title,
                    source.site_name,
                    source.published_at,
                    source.kind,
                    json.dumps([p.model_dump() for p in group]),
                ),
            )
            await self.store.execute(
                "UPDATE web_reads SET status='used' WHERE message_id=? AND url=?",
                (run.message.id, url),
            )
        info.timings["rank"] = (monotonic() - clock) * 1000
        info.source_count = len(sources)
        if not sources:
            await self.fail(run, "pages_unreadable", "No passages fit the context budget")
            return
        prompt.build(request, sources)
        # Source metadata/tags count too. Make room by dropping oldest request history.
        maximum = (request.context_length or 8192) - context.reserve - 256

        def used() -> int:
            return sum(
                int(len(m.content) * context.ratio) + 800 * len(m.images) + 4
                for m in request.messages
            )

        while used() > maximum and len(request.messages) > 2:
            request.messages.pop(1)
            context.dropped += 1
        # If the latest question plus sources cannot fit, remove lowest-ranked sources.
        while used() > maximum and len(sources) > 1:
            removed = sources.pop()
            await self.store.execute(
                "DELETE FROM message_sources WHERE message_id=? AND n=?",
                (run.message.id, removed.n),
            )
            await self.store.execute(
                "UPDATE web_reads SET status='unused' WHERE message_id=? AND url=?",
                (run.message.id, removed.url),
            )
            # Rebuild with the raw user request and the original system, avoiding duplicate prompts.
            request.messages[-1].content = request.messages[-1].content.split(
                "</search_results>\n\n", 1
            )[-1]
            request.messages[0].content = request.messages[0].content.removesuffix(
                "\n\n" + prompt.PROMPT
            )
            prompt.build(request, sources)
        if used() > maximum:
            # Do not overflow the runtime. Fall back honestly to normal generation.
            request.messages[-1].content = request.messages[-1].content.split(
                "</search_results>\n\n", 1
            )[-1]
            request.messages[0].content = request.messages[0].content.removesuffix(
                "\n\n" + prompt.PROMPT
            )
            await self.store.execute(
                "DELETE FROM message_sources WHERE message_id=?", (run.message.id,)
            )
            sources = []
            await self.fail(run, "pages_unreadable", "The source text exceeded the context budget")
        info.source_count = len(sources)
        if run.message.stats:
            run.message.stats.dropped_message_count = context.dropped
        await run.emit(
            "search.done", {"sources": [s.model_dump() for s in sources], "timings": info.timings}
        )

    async def finalize(self, run: Run) -> None:
        info = run.message.web
        if not info or info.status != "used":
            return
        count = await self.store.one(
            "SELECT count(*) AS n FROM message_sources WHERE message_id=?", (run.message.id,)
        )
        n = int(count["n"]) if count else 0
        run.message.content = citations.normalize(run.message.content, n)
        ids = citations.cited(run.message.content)
        for i in ids:
            await self.store.execute(
                "UPDATE message_sources SET cited=1 WHERE message_id=? AND n=?", (run.message.id, i)
            )
        if n and not ids and run.message.status == "complete":
            info.notice = ErrorDetail(code="uncited", message="")
