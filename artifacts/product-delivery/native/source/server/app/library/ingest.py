"""One durable ingestion queue, private progress events and shared runtime capacity."""

import asyncio
import json
import math
from array import array
from collections.abc import AsyncIterator
from ipaddress import ip_address
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import sqlite_vec  # type: ignore[import-untyped]

from ..db import settings
from ..db.connections import now
from ..db.core import Store
from ..documents.extract import ERRORS, error
from ..errors import AppError
from ..runs.manager import RunManager
from .extract import extract, passages


class Library:
    def __init__(self, store: Store, runs: RunManager, data_dir: Path) -> None:
        self.store, self.runs = store, runs
        self.folder = data_dir.expanduser().resolve() / "library"
        self.control = asyncio.Lock()
        self.changed = asyncio.Condition()
        self.wake = asyncio.Event()
        self.worker: asyncio.Task[None] | None = None
        self.available = False
        self.active: str | None = None

    async def start(self) -> None:
        self.folder.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.folder.chmod(0o700)
        for pattern in ("*.part", "*.result"):
            for path in self.folder.glob(pattern):
                path.unlink(missing_ok=True)
        try:
            await self.store.db.enable_load_extension(True)
            try:
                await self.store.db.load_extension(sqlite_vec.loadable_path())
            finally:
                await self.store.db.enable_load_extension(False)
            self.available = True
        except Exception:
            # Keep ordinary chat available if a future interpreter lacks extension support.
            self.available = False
        values = await settings.get(self.store)
        if self.available and values["library.embedding"]:
            await self.vector_table(values["library.embedding"]["dim"])
        await self.store.execute(
            "UPDATE library_documents SET status='queued',progress_done=0 "
            "WHERE status IN ('extracting','embedding')"
        )
        self.resume()

    def resume(self) -> None:
        if self.worker is None or self.worker.done():
            self.worker = asyncio.create_task(self.work(), name="library-ingestion")
        self.wake.set()

    async def close(self) -> None:
        if self.worker:
            self.worker.cancel()
            await asyncio.gather(self.worker, return_exceptions=True)
            self.worker = None

    async def vector_table(self, dim: int) -> None:
        if type(dim) is not int or not 1 <= dim <= 8192:
            raise AppError("library_dimension", "Unsupported embedding dimensions.", 422)
        await self.store.execute(
            f"CREATE VIRTUAL TABLE IF NOT EXISTS library_vectors USING vec0("
            f"chunk_id INTEGER PRIMARY KEY, embedding FLOAT[{dim}] distance_metric=cosine)"
        )

    async def model(self, choice: dict[str, Any], local_only: bool) -> Any:
        connection = await self.store.one(
            "SELECT * FROM connections WHERE id=? AND enabled=1", (choice["connection_id"],)
        )
        if not connection:
            raise AppError("runtime_unreachable", "Choose an enabled Ollama connection.", 422)
        host = urlsplit(connection["base_url"]).hostname
        local = host == "localhost"
        try:
            local = local or bool(host and ip_address(host).is_loopback)
        except ValueError:
            pass
        if local_only and not local:
            raise AppError(
                "library_requires_local", "Library text can only go to local Ollama.", 422
            )
        models = await self.runs.registry.models(include_hidden=True)
        if not any(
            m.connection_id == choice["connection_id"]
            and m.model_id == choice["model_id"]
            and m.embedding
            for m in models
        ):
            raise AppError(
                "model_not_found", "Choose a model reported as supporting embedding.", 422
            )
        return connection

    async def embed(
        self, choice: dict[str, Any], texts: list[str], local_only: bool
    ) -> list[bytes]:
        connection = await self.model(choice, local_only)
        conn = choice["connection_id"]
        # Chat's existing capacity is shared; no independent runtime semaphore.
        if conn not in self.runs.semaphores:
            limit = int(connection["max_concurrent"])
            self.runs.semaphores[conn] = asyncio.Semaphore(limit)
            self.runs.limits[conn] = limit
        adapter = await self.runs.registry.adapter(conn)
        async with self.runs.semaphores[conn]:
            vectors = await asyncio.wait_for(adapter.embed(choice["model_id"], texts), 60)
        dim = choice.get("dim")
        if len(vectors) != len(texts) or not vectors:
            raise AppError(
                "library_embedding_failed", "The runtime returned incomplete embeddings.", 502
            )
        output: list[bytes] = []
        for vector in vectors:
            if (
                not vector
                or len(vector) != (dim or len(vectors[0]))
                or any(not math.isfinite(v) for v in vector)
                or not any(vector)
            ):
                raise AppError(
                    "library_embedding_failed", "The runtime returned invalid embeddings.", 502
                )
            packed = array("f", vector)
            if any(not math.isfinite(v) for v in packed):
                raise AppError(
                    "library_embedding_failed", "The runtime returned invalid embeddings.", 502
                )
            output.append(packed.tobytes())
        return output

    async def configure(self, choice: dict[str, str] | None) -> dict[str, Any]:
        if not self.available:
            raise AppError("library_unavailable", "Library needs SQLite extension support.", 503)
        async with self.control:
            values = await settings.get(self.store)
            if choice:
                # Probe only a public synthetic string; dimensions are measured, never inferred.
                probe = await self.embed(
                    choice, ["Library dimension check."], values["library.requires_local"]
                )
                selected: dict[str, Any] | None = {**choice, "dim": len(probe[0]) // 4}
            else:
                selected = None
            if selected == values["library.embedding"]:
                return await self.snapshot()
            if selected and not 1 <= selected["dim"] <= 8192:
                raise AppError("library_dimension", "Unsupported embedding dimensions.", 422)
            await self.close()
            try:
                new_status = (
                    "'stale'"
                    if values["library.embedding"]
                    else ("CASE WHEN status='queued' THEN 'queued' ELSE 'stale' END")
                )
                # Only the Library-owned vector index is replaceable.
                statements: list[tuple[str, tuple[object, ...]]] = [
                    ("DROP TABLE IF EXISTS library_vectors", ()),
                    (
                        "INSERT INTO settings VALUES ('library.embedding',?) ON CONFLICT(key) "
                        "DO UPDATE SET value_json=excluded.value_json",
                        (json.dumps(selected),),
                    ),
                    (
                        f"UPDATE library_documents SET status={new_status},progress_done=0,"
                        "error_json=NULL",
                        (),
                    ),
                ]
                if selected:
                    dim = selected["dim"]
                    statements.append(
                        (
                            f"CREATE VIRTUAL TABLE library_vectors USING vec0("
                            f"chunk_id INTEGER PRIMARY KEY, embedding FLOAT[{dim}] "
                            "distance_metric=cosine)",
                            (),
                        )
                    )
                await self.store.batch(statements)
                await self.emit("library.changed", {})
            finally:
                self.resume()
            return await self.snapshot()

    async def preferences(self, body: dict[str, Any]) -> None:
        async with self.control:
            before = await settings.get(self.store)
            await settings.patch(self.store, body)  # Validate before interrupting any job.
            if any(
                k in body and body[k] != before[k]
                for k in ("library.document_prefix", "library.requires_local")
            ):
                await self.close()
                try:
                    if "library.document_prefix" in body:
                        await self.store.execute("UPDATE library_documents SET status='stale'")
                    else:
                        await self.store.execute(
                            "UPDATE library_documents SET status='queued' "
                            "WHERE status IN ('extracting','embedding')"
                        )
                    await self.emit("library.changed", {})
                finally:
                    self.resume()

    async def snapshot(self) -> dict[str, Any]:
        values = await settings.get(self.store)
        docs = await self.store.rows(
            "SELECT id,collection_id,filename,mime_type,bytes,status,error_json,pages,chunk_count,"
            "token_estimate,embedding_model,progress_done,progress_total,created_at,updated_at "
            "FROM library_documents ORDER BY created_at DESC,id"
        )
        for document in docs:
            raw = document.pop("error_json")
            document["error"] = json.loads(raw) if raw else None
        counts: dict[str, int] = {}
        for document in docs:
            counts[document["status"]] = counts.get(document["status"], 0) + 1
        last = await self.store.one("SELECT COALESCE(MAX(id),0) AS id FROM library_events")
        return {
            "available": self.available,
            "embedding": values["library.embedding"],
            "requires_local": values["library.requires_local"],
            "query_prefix": values["library.query_prefix"],
            "document_prefix": values["library.document_prefix"],
            "counts": counts,
            "bytes": sum(d["bytes"] for d in docs),
            "documents": docs,
            "collections": await self.store.rows(
                "SELECT * FROM library_collections ORDER BY name COLLATE NOCASE"
            ),
            "event_id": last["id"] if last else 0,
        }

    async def emit(self, kind: str, data: dict[str, Any]) -> None:
        async with self.changed:
            await self.store.batch(
                [
                    (
                        "INSERT INTO library_events(kind,data_json) VALUES (?,?)",
                        (kind, json.dumps(data)),
                    ),
                    (
                        "DELETE FROM library_events WHERE id<(SELECT MAX(id)-2000 FROM "
                        "library_events)",
                        (),
                    ),
                ]
            )
            self.changed.notify_all()

    async def events(self, after: int) -> AsyncIterator[dict[str, Any]]:
        while True:
            async with self.changed:
                rows = await self.store.rows(
                    "SELECT * FROM library_events WHERE id>? ORDER BY id", (after,)
                )
                if not rows:
                    await self.changed.wait()
                    continue
            if after and rows[0]["id"] > after + 1:
                yield {"id": str(rows[0]["id"] - 1), "event": "library.changed", "data": "{}"}
            for row in rows:
                after = row["id"]
                yield {"id": str(after), "event": row["kind"], "data": row["data_json"]}

    async def status(self, identifier: str, status: str, done: int = 0, total: int = 0) -> None:
        await self.store.execute(
            (
                "UPDATE library_documents SET "
                "status=?,progress_done=?,progress_total=?,updated_at=? WHERE "
                "id=?"
            ),
            (status, done, total, now(), identifier),
        )
        await self.emit(
            "document." + status, {"id": identifier, "status": status, "done": done, "total": total}
        )

    async def work(self) -> None:
        while True:
            await self.wake.wait()
            self.wake.clear()
            while self.available:
                values = await settings.get(self.store)
                choice = values["library.embedding"]
                if not choice:
                    break
                row = await self.store.one(
                    "SELECT * FROM library_documents WHERE status='queued' ORDER BY "
                    "created_at,id LIMIT 1"
                )
                if not row:
                    break
                self.active = row["id"]
                try:
                    await self.ingest(row, values)
                except asyncio.CancelledError:
                    # Persist unfinished work for recovery without losing the original.
                    await self.store.execute(
                        "UPDATE library_documents SET status='queued',progress_done=0 WHERE id=?",
                        (row["id"],),
                    )
                    raise
                except Exception as exc:
                    code = exc.code if isinstance(exc, AppError) else "library_embedding_failed"
                    safe = {
                        "code": code,
                        "message": ERRORS.get(
                            code,
                            "Couldn't index this file. Retry or choose another embedding model.",
                        ),
                    }
                    if code == "document_too_large":
                        safe["message"] = (
                            "This file exceeds 1,500 pages or 2 million text characters."
                        )
                    await self.store.execute(
                        "UPDATE library_documents SET status='failed',error_json=?,"
                        "updated_at=? WHERE id=?",
                        (json.dumps(safe), now(), row["id"]),
                    )
                    await self.emit(
                        "document.failed", {"id": row["id"], "status": "failed", "error": safe}
                    )
                finally:
                    self.active = None

    async def ingest(self, row: dict[str, Any], values: dict[str, Any]) -> None:
        identifier = row["id"]
        # Reindex and interrupted vector work reuse any durable passages.
        chunks = await self.store.rows(
            "SELECT * FROM library_chunks WHERE document_id=? ORDER BY ord", (identifier,)
        )
        pages = row["pages"]
        full_text = row["extracted_text"]
        if not chunks:
            await self.status(identifier, "extracting")
            value = await extract(self.folder / Path(row["path"]).name)
            pages = value.pages
            full_text = value.text
            chunks = passages(identifier, value)
            if not chunks:
                raise error("document_unreadable")
        await self.status(identifier, "embedding", 0, len(chunks))
        vectors: list[bytes] = []
        for offset in range(0, len(chunks), 32):
            batch = chunks[offset : offset + 32]
            vectors.extend(
                await self.embed(
                    values["library.embedding"],
                    [values["library.document_prefix"] + c["text"] for c in batch],
                    values["library.requires_local"],
                )
            )
            await self.status(identifier, "embedding", len(vectors), len(chunks))
            await asyncio.sleep(0)  # Give queued chat work the released connection capacity.
        choice = values["library.embedding"]
        statements: list[tuple[str, tuple[object, ...]]] = [
            (
                (
                    "DELETE FROM library_vectors WHERE chunk_id IN (SELECT id FROM "
                    "library_chunks WHERE document_id=?)"
                ),
                (identifier,),
            ),
            ("DELETE FROM library_chunks WHERE document_id=?", (identifier,)),
        ]
        # SQLite assigns fresh row ids within the transaction; vector inserts refer
        # to last_insert_rowid immediately after each passage insertion.
        for item, vector in zip(chunks, vectors, strict=True):
            statements.extend(
                [
                    (
                        (
                            "INSERT INTO "
                            "library_chunks(document_id,ord,heading,page_start,page_end,text) "
                            "VALUES (?,?,?,?,?,?)"
                        ),
                        (
                            identifier,
                            item["ord"],
                            item["heading"],
                            item["page_start"],
                            item["page_end"],
                            item["text"],
                        ),
                    ),
                    (
                        "INSERT INTO library_vectors(chunk_id,embedding) VALUES "
                        "(last_insert_rowid(),?)",
                        (vector,),
                    ),
                ]
            )
        statements.append(
            (
                (
                    "UPDATE library_documents SET "
                    "status='ready',error_json=NULL,extracted_text=?,pages=?,chunk_count=?,"
                    "token_estimate=?,embedding_model=?,progress_done=?,"
                    "progress_total=?,updated_at=? "
                    "WHERE id=?"
                ),
                (
                    full_text,
                    pages,
                    len(chunks),
                    sum((len(c["text"]) + 3) // 4 for c in chunks),
                    choice["connection_id"] + ":" + choice["model_id"],
                    len(chunks),
                    len(chunks),
                    now(),
                    identifier,
                ),
            )
        )
        await self.store.batch(statements)
        await self.emit("document.ready", {"id": identifier, "status": "ready"})

    async def reindex(self, identifier: str | None = None) -> None:
        async with self.control:
            if identifier:
                row = await self.store.one(
                    "SELECT status FROM library_documents WHERE id=?", (identifier,)
                )
                if not row:
                    raise AppError("not_found", "File not found.", 404)
                if row["status"] in ("queued", "extracting", "embedding"):
                    raise AppError("library_active", "This file is already being indexed.", 409)
                await self.store.execute(
                    "UPDATE library_documents SET status='queued',error_json=NULL WHERE id=?",
                    (identifier,),
                )
            else:
                await self.store.execute(
                    "UPDATE library_documents SET status='queued',error_json=NULL "
                    "WHERE status='stale'"
                )
            await self.emit("document.queued", {"id": identifier, "status": "queued"})
            self.resume()

    async def delete(self, identifier: str | None = None) -> None:
        async with self.control:
            await self.close()
            try:
                rows = await self.store.rows(
                    "SELECT id,path FROM library_documents" + (" WHERE id=?" if identifier else ""),
                    (identifier,) if identifier else (),
                )
                if identifier and not rows:
                    raise AppError("not_found", "File not found.", 404)
                statements: list[tuple[str, tuple[object, ...]]] = []
                for row in rows:
                    statements.append(
                        (
                            "UPDATE message_library_sources SET document_id=NULL WHERE "
                            "document_id=?",
                            (row["id"],),
                        )
                    )
                    if self.available and await self.store.one(
                        "SELECT name FROM sqlite_master WHERE name='library_vectors'"
                    ):
                        statements.append(
                            (
                                (
                                    "DELETE FROM library_vectors WHERE chunk_id IN (SELECT id FROM "
                                    "library_chunks WHERE document_id=?)"
                                ),
                                (row["id"],),
                            )
                        )
                    statements.append(("DELETE FROM library_documents WHERE id=?", (row["id"],)))
                if not identifier:
                    statements.extend(
                        [
                            ("DELETE FROM library_collections", ()),
                            ("DELETE FROM library_events", ()),
                        ]
                    )
                await self.store.batch(statements)
                for row in rows:
                    (self.folder / Path(row["path"]).name).unlink(missing_ok=True)
                await self.emit("library.changed", {})
            finally:
                self.resume()
