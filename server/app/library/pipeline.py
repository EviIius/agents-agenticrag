"""One deterministic Library retrieval before the existing answer call."""

import asyncio
import json
from time import monotonic

from ..db import chats, messages, settings
from ..errors import AppError
from ..providers.base import ChatRequest, ProviderMessage
from ..runs.context import Context, path
from ..runs.manager import Run, RunManager
from ..schemas import ErrorDetail, LibraryInfo
from ..search import citations, planner
from . import prompt
from .ingest import Library
from .privacy import guard
from .retrieve import retrieve


class Pipeline:
    def __init__(self, manager: RunManager, library: Library) -> None:
        self.manager, self.library, self.store = manager, library, manager.store

    async def fail(self, run: Run, code: str, reason: str) -> None:
        run.message.library = LibraryInfo(
            status="failed" if code != "library_empty" else "skipped",
            notice=ErrorDetail(code=code, message=reason),
        )
        await run.emit("library.failed", {"code": code, "message": reason})

    async def __call__(self, run: Run, request: ChatRequest, context: Context) -> None:
        values = await settings.get(self.store)
        if not run.message.model:
            return
        await guard(self.store, run.message.model.connection_id, values)
        chat = await chats.chat(self.store, run.message.chat_id)
        where = "status='ready'"
        params: tuple[object, ...] = ()
        if chat.library_scope is not None:
            ids = chat.library_scope.collection_ids
            if not ids:
                await self.fail(run, "library_empty", "No ready files in this scope.")
                return
            where += " AND collection_id IN (" + ",".join("?" for _ in ids) + ")"
            params = tuple(ids)
        if not await self.store.one(
            "SELECT id FROM library_documents WHERE " + where + " LIMIT 1", params
        ):
            await self.fail(run, "library_empty", "No ready files in this scope.")
            return
        run.message.library = LibraryInfo(status="used")
        await run.emit("library.searching", {})
        clock = monotonic()
        try:
            choice = values["library.embedding"]
            if not choice or not self.library.available:
                raise AppError("library_unavailable", "Choose an available embedding model.", 422)
            connection = await self.library.model(choice, values["library.requires_local"])
            adapter = await self.manager.registry.adapter(choice["connection_id"])
            raw = path(await messages.list_messages(self.store, chat.id), run.message.parent_id)
            history = [ProviderMessage(m.role, m.content) for m in raw[:-1]]
            query = planner.heuristic(raw[-1].content, history)
            remaining = (request.context_length or 8192) - context.reserve - context.used_tokens
            budget = max(1500, min(12000, int(0.45 * remaining)))
            # Generation already holds the answer connection's semaphore. Reuse
            # that slot for embedding on the same connection rather than deadlock.
            if choice["connection_id"] == run.message.model.connection_id:
                sources, info = await retrieve(
                    self.store, adapter, values, query, chat.library_scope, budget, context.ratio
                )
            else:
                conn = choice["connection_id"]
                if conn not in self.manager.semaphores:
                    limit = int(connection["max_concurrent"])
                    self.manager.semaphores[conn] = asyncio.Semaphore(limit)
                    self.manager.limits[conn] = limit
                async with asyncio.timeout(60), self.manager.semaphores[conn]:
                    sources, info = await retrieve(
                        self.store,
                        adapter,
                        values,
                        query,
                        chat.library_scope,
                        budget,
                        context.ratio,
                    )
            if not sources:
                await self.fail(run, "library_failed", "No passages fit the context budget.")
                return
        except asyncio.CancelledError:
            raise
        except Exception:
            # Provider/SQLite exceptions may contain private query text or paths.
            await self.fail(run, "library_failed", "The Library retrieval was unavailable.")
            return
        system, latest = request.messages[0].content, request.messages[-1].content
        maximum = (request.context_length or 8192) - context.reserve - 256

        def rebuild() -> int:
            request.messages[0].content = system
            request.messages[-1].content = latest
            prompt.build(request, sources)
            return sum(
                int(len(m.content) * context.ratio) + 800 * len(m.images) + 4
                for m in request.messages
            )

        used = rebuild()
        while used > maximum and len(request.messages) > 2:
            request.messages.pop(1)
            context.dropped += 1
            used = rebuild()
        while used > maximum and sources:
            sources.pop()
            used = rebuild() if sources else maximum + 1
        if not sources:
            request.messages[0].content, request.messages[-1].content = system, latest
            await self.fail(run, "library_failed", "The passages exceeded the context budget.")
            return
        await self.store.batch(
            [
                (
                    "INSERT INTO message_library_sources(message_id,n,document_id,filename,"
                    "page_start,page_end,passages_json) "
                    "VALUES (?,?,(SELECT id FROM library_documents WHERE id=?),?,?,?,?)",
                    (
                        run.message.id,
                        s.n,
                        s.document_id,
                        s.title,
                        s.page_start,
                        s.page_end,
                        json.dumps([p.model_dump() for p in s.passages]),
                    ),
                )
                for s in sources
            ]
        )
        # A deletion can finish after candidate selection but before this
        # transaction. Keep exactly what the model saw, without a dangling
        # original-file link in either the durable snapshot or initial SSE.
        originals = {
            row["n"]: row["document_id"]
            for row in await self.store.rows(
                "SELECT n,document_id FROM message_library_sources WHERE message_id=?",
                (run.message.id,),
            )
        }
        for source in sources:
            if originals.get(source.n) is None:
                source.document_id, source.url = None, ""
        info.source_count, info.passage_count = len(sources), sum(len(s.passages) for s in sources)
        info.timings["total"] = (monotonic() - clock) * 1000
        run.message.library = info
        if run.message.stats:
            run.message.stats.dropped_message_count = context.dropped
        await messages.save(self.store, run.message)
        await run.emit(
            "library.results", {"count": info.source_count, "passage_count": info.passage_count}
        )
        await run.emit(
            "library.done",
            {"sources": [s.model_dump() for s in sources], "library": info.model_dump()},
        )

    async def finalize(self, run: Run) -> None:
        if not run.message.library or run.message.library.status != "used":
            return
        row = await self.store.one(
            "SELECT count(*) AS n FROM message_library_sources WHERE message_id=?",
            (run.message.id,),
        )
        n = int(row["n"]) if row else 0
        run.message.content = citations.normalize(run.message.content, n)
        ids = citations.cited(run.message.content)
        await self.store.batch(
            [
                (
                    "UPDATE message_library_sources SET cited=1 WHERE message_id=? AND n=?",
                    (run.message.id, i),
                )
                for i in ids
            ]
        )
        if n and not ids and run.message.status == "complete":
            run.message.library.notice = ErrorDetail(code="uncited", message="")
