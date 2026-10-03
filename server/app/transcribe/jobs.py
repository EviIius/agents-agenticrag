"""Durable transcript rows, sequential subprocess jobs and resumable SSE."""

import asyncio
import json
import shutil
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from ..db import attachments, settings
from ..db.connections import now
from ..db.core import Store
from ..errors import AppError
from ..schemas import Attachment, AudioStorage, TranscriptionEvent
from .engine import Engine


@dataclass
class Job:
    id: str
    events: list[TranscriptionEvent] = field(default_factory=list)
    changed: asyncio.Condition = field(default_factory=asyncio.Condition)
    closed: bool = False
    interrupted: bool = False
    task: asyncio.Task[None] | None = None

    async def emit(self, kind: str, data: dict[str, Any]) -> None:
        async with self.changed:
            self.events.append(TranscriptionEvent.model_validate({"type": kind, "data": data}))
            self.closed = kind == "stream.closed"
            self.changed.notify_all()

    async def tail(self, after: int) -> AsyncIterator[tuple[int, TranscriptionEvent]]:
        index = max(0, after)
        while True:
            async with self.changed:
                while len(self.events) <= index and not self.closed:
                    await self.changed.wait()
                batch, done = self.events[index:], self.closed
            for event in batch:
                index += 1
                yield index, event
            if done:
                return


class TranscriptionManager:
    def __init__(self, store: Store, home: Path | None, data_dir: Path) -> None:
        self.store, self.engine = store, Engine(home)
        self.data_dir = data_dir.expanduser().resolve()
        self.jobs: dict[str, Job] = {}
        self.semaphore = asyncio.Semaphore(1)
        self.locks: dict[str, asyncio.Lock] = {}
        self.housekeeper: asyncio.Task[None] | None = None

    def lock(self, identifier: str) -> asyncio.Lock:
        return self.locks.setdefault(identifier, asyncio.Lock())

    async def recover(self) -> None:
        await self.store.execute(
            "UPDATE transcripts SET status='failed',error_json=?,updated_at=? W"
            "HERE status IN ('queued','transcribing')",
            (
                json.dumps(
                    {
                        "code": "transcription_interrupted",
                        "message": "Interrupted because the server restarted",
                    }
                ),
                now(),
            ),
        )
        await self.store.execute(
            "UPDATE transcripts SET cleanup_status='failed',cleanup_json=? WHER"
            "E cleanup_status='running'",
            (
                json.dumps(
                    {
                        "error": {
                            "code": "cleanup_failed",
                            "message": "Interrupted because the server restarted",
                        }
                    }
                ),
            ),
        )
        shutil.rmtree(self.data_dir / "transcribe-tmp", ignore_errors=True)
        if not (await settings.get(self.store))["transcription.keep_audio"]:
            await self.clear_audio(ready_only=True)
        await self.housekeeping()
        self.housekeeper = asyncio.create_task(self.maintain())

    async def maintain(self) -> None:
        while True:
            await asyncio.sleep(86400)
            await self.housekeeping()

    async def housekeeping(self) -> None:
        cutoff = (datetime.now(UTC) - timedelta(days=7)).isoformat()
        rows = await self.store.rows(
            "SELECT a.id,a.path FROM attachments a LEFT JOIN transcripts t ON t.attachment_id=a.id "
            "WHERE a.message_id IS NULL AND a.created_at<? "
            "AND (t.status IS NULL OR t.status!='ready')",
            (cutoff,),
        )
        for row in rows:
            await self.remove(str(row["id"]))

    async def start(self, identifier: str, channels: str = "mix") -> Attachment:
        async with self.lock(identifier):
            item = await attachments.attachment(self.store, identifier)
            if item.kind != "audio":
                raise AppError("unsupported_type", "This attachment is not a recording.", 422)
            old = self.jobs.get(identifier)
            if old and not old.closed:
                raise AppError(
                    "transcription_active", "This recording is still being processed.", 409
                )
            if not item.audio_available:
                raise AppError(
                    "audio_removed", "The audio was removed. Upload it again to transcribe.", 409
                )
            if not (await self.engine.status()).ready:
                raise AppError(
                    "transcription_unavailable", "Recordings need the transcription engine", 422
                )
            date = now()
            await self.store.execute(
                "INSERT INTO transcripts(attachment_id,status,channels,created_"
                "at,updated_at) VALUES (?,'queued',?,?,?) "
                "ON CONFLICT(attachment_id) DO UPDATE SET status='queued',chann"
                "els=excluded.channels,started_at=NULL,error_json=NULL,"
                "text=NULL,raw_text=NULL,segments_json=NULL,meta_json=NULL,duration_seconds=NULL,"
                "cleaned_text=NULL,cleanup_status=NULL,cleanup_json=NULL,update"
                "d_at=excluded.updated_at",
                (identifier, channels, date, date),
            )
            job = Job(identifier)
            self.jobs[identifier] = job
            await job.emit(
                "transcription.queued",
                {"position": 1 + sum(not j.closed for j in self.jobs.values() if j is not job)},
            )
            queued = await attachments.attachment(self.store, identifier)
            job.task = asyncio.create_task(
                self.work(job, channels), name="transcription-" + identifier
            )
            return queued

    async def work(self, job: Job, channels: str) -> None:
        scratch = self.data_dir / "transcribe-tmp" / job.id
        kind = "transcription.done"
        try:
            async with self.semaphore:
                row = await self.store.one("SELECT path FROM attachments WHERE id=?", (job.id,))
                if not row:
                    return
                await self.store.execute(
                    "UPDATE transcripts SET status='transcribing',started_at=?,"
                    "updated_at=? WHERE attachment_id=?",
                    (now(), now(), job.id),
                )
                item = await attachments.attachment(self.store, job.id)
                assert item.transcript is not None
                await job.emit("transcription.started", {"started_at": item.transcript.started_at})
                scratch.mkdir(parents=True, mode=0o700, exist_ok=True)
                result = await self.engine.run(self.data_dir / str(row["path"]), scratch, channels)
                await self.store.execute(
                    "UPDATE transcripts SET status='ready',text=?,raw_text=?,se"
                    "gments_json=?,meta_json=?,duration_seconds=?,updated_at=? "
                    "WHERE attachment_id=?",
                    (
                        result["text"],
                        result["raw_text"],
                        json.dumps(result["segments"]),
                        json.dumps(attachments.result_meta(result)),
                        result.get("source", {}).get("duration_seconds"),
                        now(),
                        job.id,
                    ),
                )
                if not (await settings.get(self.store))["transcription.keep_audio"]:
                    try:
                        await self.release_audio(job.id)
                    except OSError:
                        pass  # The durable transcript remains ready; Settings can retry cleanup.
        except asyncio.CancelledError:
            kind = "transcription.failed" if job.interrupted else "transcription.cancelled"
            await self.cancelled(job)
        except Exception as exc:
            kind = "transcription.failed"
            error = {
                "code": exc.code if isinstance(exc, AppError) else "transcription_failed",
                "message": exc.message
                if isinstance(exc, AppError)
                else "The engine could not read this recording.",
            }
            await self.store.execute(
                "UPDATE transcripts SET status='failed',error_json=?,updated_at"
                "=? WHERE attachment_id=?",
                (json.dumps(error), now(), job.id),
            )
        finally:
            shutil.rmtree(scratch, ignore_errors=True)
            if await self.store.one("SELECT id FROM attachments WHERE id=?", (job.id,)):
                await job.emit(
                    kind,
                    {"attachment": (await attachments.attachment(self.store, job.id)).model_dump()},
                )
            await job.emit("stream.closed", {})
            asyncio.get_running_loop().call_later(900, self.expire, job)

    async def release_audio(self, identifier: str) -> int:
        row = await self.store.one("SELECT path,bytes FROM attachments WHERE id=?", (identifier,))
        if not row:
            return 0
        file = (self.data_dir / str(row["path"])).resolve()
        if not file.is_relative_to(self.data_dir / "attachments"):
            raise AppError("audio_storage_error", "The audio could not be removed.", 500)
        size = file.stat().st_size if file.exists() else 0
        await asyncio.to_thread(file.unlink, missing_ok=True)
        await self.store.execute(
            "UPDATE attachments SET audio_available=0 WHERE id=?", (identifier,)
        )
        return size

    async def audio_storage(self) -> AudioStorage:
        rows = await self.store.rows(
            "SELECT a.id,a.path,t.status FROM attachments a LEFT JOIN transcripts t "
            "ON t.attachment_id=a.id WHERE a.kind='audio' AND a.audio_available=1"
        )
        result = AudioStorage()
        for row in rows:
            file = (self.data_dir / str(row["path"])).resolve()
            if file.is_relative_to(self.data_dir / "attachments") and file.is_file():
                result.files += 1
                result.bytes += file.stat().st_size
                result.active_files += row["status"] in ("queued", "transcribing")
        return result

    async def clear_audio(self, ready_only: bool = False) -> AudioStorage:
        rows = await self.store.rows(
            "SELECT id FROM attachments WHERE kind='audio' AND audio_available=1"
        )
        removed = AudioStorage()
        for row in rows:
            identifier = str(row["id"])
            async with self.lock(identifier):
                record = await self.store.one(
                    "SELECT a.audio_available,t.status FROM attachments a LEFT JOIN transcripts t "
                    "ON t.attachment_id=a.id WHERE a.id=?",
                    (identifier,),
                )
                job = self.jobs.get(identifier)
                if not record or not record["audio_available"] or (job and not job.closed):
                    continue
                state = record["status"]
                if state in ("queued", "transcribing") or (ready_only and state != "ready"):
                    continue
                removed.bytes += await self.release_audio(identifier)
                removed.files += 1
        return removed

    def expire(self, job: Job) -> None:
        if self.jobs.get(job.id) is job:
            self.jobs.pop(job.id, None)
            self.locks.pop(job.id, None)

    async def cancel(self, identifier: str) -> None:
        job = self.jobs.get(identifier)
        if job and not job.closed and job.task:
            job.task.cancel()
            await asyncio.gather(job.task, return_exceptions=True)
            # A task cancelled before its first instruction cannot emit its own final state.
            if not job.closed:
                await self.cancelled(job)
                await job.emit(
                    "transcription.failed" if job.interrupted else "transcription.cancelled",
                    {
                        "attachment": (
                            await attachments.attachment(self.store, identifier)
                        ).model_dump()
                    },
                )
                await job.emit("stream.closed", {})

    async def cancelled(self, job: Job) -> None:
        error = (
            json.dumps(
                {
                    "code": "transcription_interrupted",
                    "message": "Interrupted because the server restarted",
                }
            )
            if job.interrupted
            else None
        )
        await self.store.execute(
            "UPDATE transcripts SET status=?,error_json=?,updated_at=? WHERE attachment_id=?",
            ("failed" if job.interrupted else "cancelled", error, now(), job.id),
        )

    async def remove(self, identifier: str) -> None:
        async with self.lock(identifier):
            row = await self.store.one("SELECT * FROM attachments WHERE id=?", (identifier,))
            if not row:
                raise AppError("not_found", "Attachment not found.", 404)
            if row["message_id"]:
                raise AppError(
                    "attachment_sent", "Delete the chat to remove a sent recording.", 409
                )
            await self.cancel(identifier)
            await self.store.execute("DELETE FROM attachments WHERE id=?", (identifier,))
            file = (self.data_dir / str(row["path"])).resolve()
            if file.is_relative_to(self.data_dir / "attachments"):
                file.unlink(missing_ok=True)
            self.jobs.pop(identifier, None)

    async def cancel_chat(self, chat_id: str | None = None) -> None:
        rows = await self.store.rows(
            "SELECT attachments.id FROM attachments JOIN messages ON message_id=messages.id"
            + (" WHERE messages.chat_id=?" if chat_id else ""),
            (chat_id,) if chat_id else (),
        )
        for row in rows:
            await self.cancel(str(row["id"]))

    async def close(self) -> None:
        if self.housekeeper:
            self.housekeeper.cancel()
            await asyncio.gather(self.housekeeper, return_exceptions=True)
        for identifier in list(self.jobs):
            self.jobs[identifier].interrupted = True
            await self.cancel(identifier)
