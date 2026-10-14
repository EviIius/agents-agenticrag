"""Durable one-step jobs; persisted events, owned processes, private artifacts."""

import asyncio
import json
import os
import shutil
from collections.abc import AsyncGenerator, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from ..capacity import Capacity
from ..db.core import Store
from ..db.image_jobs import image_job
from ..errors import AppError
from ..schemas import ImageChange, ImageCreate, ImageJob, ImageSnapshot, ImageStorage
from .engine import Engine
from .files import atomic_json, sync_directory, validate

Prepared = list[tuple[str, list[tuple[str, tuple[object, ...]]]]]

ACTIVE = {"queued", "preparing", "running", "cancelling"}


def now() -> str:
    return datetime.now(UTC).isoformat()


class Images:
    def __init__(self, store: Store, data: Path, home: Path | None, capacity: Capacity) -> None:
        self.store, self.data, self.capacity = store, data, capacity
        self.engine = Engine(home, capacity)
        self.folder = data / "images"
        self.folder.mkdir(mode=0o700, exist_ok=True)
        self.folder.chmod(0o700)
        self.lock = asyncio.Lock()
        self.condition = asyncio.Condition()
        self.tasks: dict[str, asyncio.Task[None]] = {}
        self.cancelling: set[str] = set()
        self.closing = False

    def path(self, identifier: str) -> Path:
        # Internal identifiers only, never user filenames or arbitrary paths.
        if len(identifier) != 32 or any(c not in "0123456789abcdef" for c in identifier):
            raise AppError("not_found", "Image job not found.", 404)
        return self.folder / identifier

    async def get(self, identifier: str) -> ImageJob:
        self.path(identifier)
        return await image_job(self.store, identifier)

    async def list(self, before: str | None = None) -> list[ImageJob]:
        rows = await self.store.rows(
            "SELECT id FROM image_jobs WHERE (? IS NULL OR created_at < ?) "
            "ORDER BY created_at DESC,id DESC LIMIT 100",
            (before, before),
        )
        return [await self.get(row["id"]) for row in rows]

    async def storage(self) -> ImageStorage:
        row = await self.store.one(
            "SELECT COUNT(*) outputs,COALESCE(SUM(a.bytes),0) image_bytes,"
            "COALESCE(SUM(a.metadata_bytes),0) metadata_bytes,"
            "COALESCE(SUM(j.parent_id IS NOT NULL),0) versions FROM image_artifacts a "
            "JOIN image_jobs j ON j.id=a.job_id"
        )
        assert row is not None
        # Logical bytes. APFS shared extents/compression are not inferred.
        return ImageStorage(
            **row,
            manifest_bytes=sum(p.stat().st_size for p in self.folder.glob("*/input.json")),
            database_bytes=sum(p.stat().st_size for p in self.data.glob("workbench.db*")),
            backup_bytes=sum(
                p.stat().st_size for p in (self.data / "backups/images").rglob("*") if p.is_file()
            ),
            free_bytes=shutil.disk_usage(self.data).free,
        )

    async def snapshot(self) -> ImageSnapshot:
        jobs = await self.list()
        # Active older jobs must survive a snapshot gap even beyond Gallery's page.
        known = {job.id for job in jobs}
        for row in await self.store.rows(
            "SELECT id FROM image_jobs WHERE state IN "
            "('queued','preparing','running','cancelling') ORDER BY created_at,id"
        ):
            if row["id"] not in known:
                jobs.append(await self.get(row["id"]))
        return ImageSnapshot(jobs=jobs, storage=await self.storage())

    async def emit(self, identifier: str) -> None:
        async with self.condition:
            item = await self.get(identifier)
            await self.store.batch(
                [
                    (
                        "INSERT INTO image_events(job_id,data_json) VALUES(?,?)",
                        (
                            identifier,
                            ImageChange(job=item, storage=await self.storage()).model_dump_json(),
                        ),
                    ),
                    (
                        "DELETE FROM image_events WHERE id <= "
                        "(SELECT COALESCE(MAX(id),0)-1000 FROM image_events)",
                        (),
                    ),
                ]
            )
            self.condition.notify_all()

    async def update(
        self,
        identifier: str,
        state: str,
        stage: str,
        error: str | None = None,
        done: int | None = None,
    ) -> None:
        await self.store.execute(
            "UPDATE image_jobs SET state=?,stage=?,error=?,updated_at=?,"
            "completed_steps=COALESCE(?,completed_steps) WHERE id=?",
            (state, stage, error, now(), done, identifier),
        )
        await self.emit(identifier)

    async def submit(self, spec: ImageCreate) -> ImageJob:
        if not spec.prompt.strip():
            raise AppError("invalid_request", "Write an image prompt first.", 422)
        expected = {"prompt": spec.prompt, "seed": spec.seed}
        canonical = json.dumps(expected, sort_keys=True)
        async with self.lock:
            old = await self.store.one(
                "SELECT * FROM image_jobs WHERE request_key=?", (spec.request_key,)
            )
            if old:
                if old["input_json"] != canonical or old["parent_id"] != spec.parent_id:
                    raise AppError(
                        "request_conflict",
                        "This request key belongs to different image inputs.",
                        409,
                    )
                return await self.get(old["id"])
            prepared = await self.prepare([spec])
            try:
                await self.store.batch([statement for _, rows in prepared for statement in rows])
            except BaseException:
                self.discard(prepared)
                raise
            identifier = prepared[0][0]
            self.schedule(identifier)
            await self.emit(identifier)
            return await self.get(identifier)

    async def prepare(self, specs: Sequence[ImageCreate]) -> Prepared:
        """Caller owns self.lock; prepare all manifests without commits or scheduling."""
        if self.closing:
            raise AppError(
                "image_unavailable", "Image service is shutting down. Retry shortly.", 503
            )
        if not self.engine.status().available:
            raise AppError(
                "image_unavailable", "The local image worker or pinned model is unavailable.", 409
            )
        if len(self.tasks) + len(specs) > 20:
            raise AppError(
                "image_queue_full", "The image queue is full. Wait for a job to finish.", 409
            )
        if shutil.disk_usage(self.data).free < 128 * 1024**2:
            raise AppError("low_disk", "Free at least 128 MB before starting an image.", 409)
        prepared: Prepared = []
        try:
            for spec in specs:
                if not spec.prompt.strip():
                    raise AppError("invalid_request", "Write an image prompt first.", 422)
                if spec.parent_id:
                    await self.get(spec.parent_id)
                expected = {"prompt": spec.prompt, "seed": spec.seed}
                identifier, timestamp = uuid4().hex, now()
                folder = self.path(identifier)
                folder.mkdir(mode=0o700)
                rows: list[tuple[str, tuple[object, ...]]] = [
                    (
                        "INSERT INTO image_jobs(id,request_key,parent_id,input_json,state,stage,"
                        "created_at,updated_at) VALUES(?,?,?,?,'queued',"
                        "'Waiting for capacity',?,?)",
                        (
                            identifier,
                            spec.request_key,
                            spec.parent_id,
                            json.dumps(expected, sort_keys=True),
                            timestamp,
                            timestamp,
                        ),
                    ),
                    ("INSERT INTO image_steps(job_id) VALUES(?)", (identifier,)),
                ]
                prepared.append((identifier, rows))
                atomic_json(folder / "input.json", expected)
            return prepared
        except BaseException:
            self.discard(prepared)
            raise

    def discard(self, prepared: Prepared) -> None:
        for identifier, _ in prepared:
            shutil.rmtree(self.path(identifier), ignore_errors=True)

    def schedule(self, identifier: str) -> None:
        task = asyncio.create_task(self.run(identifier))
        self.tasks[identifier] = task
        task.add_done_callback(lambda _: self.tasks.pop(identifier, None))

    async def run(self, identifier: str) -> None:
        folder = self.path(identifier)
        scratch = folder / "working"
        try:
            async with self.capacity.lease(background=True):
                if self.closing or identifier in self.cancelling:
                    raise asyncio.CancelledError
                if shutil.disk_usage(self.data).free < 128 * 1024**2:
                    raise AppError(
                        "low_disk", "Free at least 128 MB before retrying this image.", 409
                    )
                await self.update(identifier, "preparing", "Initializing image model")
                await self.store.execute(
                    "UPDATE image_steps SET started_at=? WHERE job_id=?", (now(), identifier)
                )
                scratch.mkdir(mode=0o700)

                async def progress(event: dict[str, Any]) -> None:
                    kind = event["type"]
                    if identifier in self.cancelling:
                        return
                    if kind == "initializing":
                        await self.update(identifier, "preparing", "Loading image weights")
                    elif kind == "denoising":
                        done = event.get("completed_steps", 0)
                        if not isinstance(done, int) or not 0 <= done <= 4:
                            raise ValueError("Invalid progress")
                        await self.update(identifier, "running", "Generating image", done=done)
                    elif kind == "decoding":
                        await self.update(identifier, "running", "Decoding image")
                    elif kind == "failed":
                        raise ValueError("Worker failed")

                exit_code = await self.engine.run(folder / "input.json", scratch, progress)
                async with self.lock:
                    expected = json.loads((folder / "input.json").read_text())
                    digest, size, metadata_size = await asyncio.to_thread(
                        validate, scratch, expected
                    )
                    os.replace(scratch, folder / "output")
                    sync_directory(folder)
                    await self.store.batch(
                        [
                            (
                                "INSERT INTO image_artifacts(job_id,sha256,bytes,metadata_bytes) "
                                "VALUES(?,?,?,?)",
                                (identifier, digest, size, metadata_size),
                            ),
                            (
                                "UPDATE image_steps SET finished_at=?,exit_code=? WHERE job_id=?",
                                (now(), exit_code, identifier),
                            ),
                            (
                                "UPDATE image_jobs SET state='complete',stage='Image saved',"
                                "completed_steps=4,updated_at=? WHERE id=?",
                                (now(), identifier),
                            ),
                        ]
                    )
                    await self.emit(identifier)
        except asyncio.CancelledError:
            state = "interrupted" if self.closing else "cancelled"
            await self.update(
                identifier, state, "Interrupted — retry available" if self.closing else "Cancelled"
            )
        except AppError as exc:
            await self.update(identifier, "failed", "Retry available", exc.message)
        except (OSError, ValueError, KeyError, TimeoutError):
            await self.update(
                identifier,
                "failed",
                "Retry available",
                "Image could not be completed or validated. "
                "No output was accepted. Retry this job.",
            )
        finally:
            # Only remove temporary outputs after Engine.run has reaped its child.
            shutil.rmtree(scratch, ignore_errors=True)
            self.cancelling.discard(identifier)

    async def cancel(self, identifier: str) -> ImageJob:
        async with self.lock:
            item = await self.get(identifier)
            task = self.tasks.get(identifier)
            if item.state in ACTIVE and task:
                self.cancelling.add(identifier)
                if item.state == "queued":
                    await self.update(identifier, "cancelled", "Cancelled")
                else:
                    await self.update(identifier, "cancelling", "Stopping image worker")
                task.cancel()
        if task and item.state in ACTIVE:
            await task
        return await self.get(identifier)

    async def remove(self, identifier: str) -> None:
        async with self.lock:
            item = await self.get(identifier)
            if item.state in ACTIVE:
                raise AppError(
                    "image_busy",
                    "Cancel this job and wait for its worker to stop before removing files.",
                    409,
                )
            folder = self.path(identifier)
            output, trash = folder / "output", folder / "deleting"
            if output.exists():
                os.replace(output, trash)
                sync_directory(folder)
            try:
                await self.store.batch(
                    [
                        ("DELETE FROM image_artifacts WHERE job_id=?", (identifier,)),
                        ("UPDATE image_jobs SET updated_at=? WHERE id=?", (now(), identifier)),
                    ]
                )
            except BaseException:
                if trash.exists():
                    os.replace(trash, output)
                raise
            shutil.rmtree(trash, ignore_errors=True)
            await self.emit(identifier)

    async def clear(self) -> ImageStorage:
        rows = await self.store.rows("SELECT job_id FROM image_artifacts")
        for row in rows:
            await self.remove(row["job_id"])
        return await self.storage()

    async def artifact(self, identifier: str, format: str) -> Path:
        item = await self.get(identifier)
        if not item.sha256:
            raise AppError("not_found", "This image output is unavailable or was removed.", 404)
        output = self.path(identifier) / "output"
        file = output / ("image.png" if format == "png" else "metadata.json")
        if not file.is_file() or file.is_symlink():
            raise AppError(
                "not_found", "This image file is missing. Restore it from an image backup.", 404
            )
        return file

    async def recover(self) -> None:
        # A previous worker's parent pipe has closed; it exits without this new
        # server signaling any PID which might have been reused.
        rows = await self.store.rows(
            "SELECT id,state,input_json FROM image_jobs ORDER BY created_at,id"
        )
        known = {row["id"] for row in rows}
        for folder in self.folder.iterdir():
            if folder.name not in known and folder.is_dir():
                shutil.rmtree(folder)
        for row in rows:
            identifier = row["id"]
            folder = self.path(identifier)
            shutil.rmtree(folder / "working", ignore_errors=True)
            trash = folder / "deleting"
            artifact = await self.store.one(
                "SELECT * FROM image_artifacts WHERE job_id=?", (identifier,)
            )
            if trash.exists():
                if artifact and not (folder / "output").exists():
                    os.replace(trash, folder / "output")
                else:
                    shutil.rmtree(trash)
            if row["state"] in ACTIVE - {"queued"}:
                await self.update(identifier, "interrupted", "Interrupted — retry available")
            elif artifact:
                try:
                    digest, _, _ = await asyncio.to_thread(
                        validate, folder / "output", json.loads(row["input_json"])
                    )
                    if digest != artifact["sha256"]:
                        raise ValueError("Artifact digest mismatch")
                except (OSError, ValueError, KeyError):
                    await self.store.execute(
                        "DELETE FROM image_artifacts WHERE job_id=?", (identifier,)
                    )
                    await self.update(
                        identifier,
                        "failed",
                        "Output missing or invalid",
                        "Restore the output from an image backup or retry this job.",
                    )
            elif (folder / "output").exists():
                # Files moved before the completion transaction are unaccepted.
                shutil.rmtree(folder / "output")
            if not artifact and (folder / "output").exists():
                shutil.rmtree(folder / "output")
            if row["state"] == "queued" and self.engine.status().available:
                self.schedule(identifier)
            elif row["state"] == "queued":
                await self.update(
                    identifier, "interrupted", "Worker unavailable — retry after setup"
                )

    async def tail(self, after: int) -> AsyncGenerator[tuple[int, str, object], None]:
        async with self.condition:
            # Replay retained changes, then a current snapshot repairs gaps.
            replay = (
                await self.store.rows(
                    "SELECT id,data_json FROM image_events WHERE id>? ORDER BY id", (max(0, after),)
                )
                if after
                else []
            )
            maximum = await self.store.one("SELECT COALESCE(MAX(id),0) n FROM image_events")
            cursor = int(maximum["n"]) if maximum else 0
            snapshot = (await self.snapshot()).model_dump()
        for row in replay:
            yield row["id"], "image.updated", json.loads(row["data_json"])
        yield cursor, "image.snapshot", snapshot
        while True:
            async with self.condition:
                while not (
                    rows := await self.store.rows(
                        "SELECT id,data_json FROM image_events WHERE id>? ORDER BY id", (cursor,)
                    )
                ):
                    await self.condition.wait()
            for row in rows:
                cursor = row["id"]
                yield cursor, "image.updated", json.loads(row["data_json"])

    async def close(self) -> None:
        self.closing = True
        tasks = list(self.tasks.values())
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        for row in await self.store.rows(
            "SELECT id FROM image_jobs WHERE state IN ('queued','preparing','running','cancelling')"
        ):
            await self.update(row["id"], "interrupted", "Interrupted — retry available")
