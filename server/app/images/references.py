"""Durable chat-owned pixel inputs; callers pin under the image acceptance lock."""

import asyncio
import json
import os
import shutil
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from uuid import uuid4

from ..db import chats
from ..db.core import Store
from ..errors import AppError
from ..schemas import ImageReference
from .codec import ReferenceCodec
from .files import atomic_json, sync_directory
from .reference_files import bind, owned, validate_reference
from .storage import StorageMeter
from .uploads import IMAGE_LIMIT, ImageUploads, is_heif

TOUCH_REFERENCE_JOBS = (
    "UPDATE image_jobs SET updated_at=? WHERE id IN "
    "(SELECT job_id FROM image_job_references WHERE reference_id=?)"
)


@dataclass(frozen=True)
class Reference:
    id: str
    descriptor: dict[str, Any]


def projection(row: dict[str, Any]) -> ImageReference:
    meta = json.loads(row["descriptor_json"])
    return ImageReference(
        id=row["id"],
        chat_id=row["chat_id"],
        available=bool(row["available"]),
        original_bytes=meta["original_bytes"],
        working_bytes=meta["bytes"],
        width=meta["dimensions"][0],
        height=meta["dimensions"][1],
        original_format=meta["original_format"],
        created_at=row["created_at"],
    )


class References:
    def __init__(self, store: Store, data: Path, home: Path | None, lock: asyncio.Lock) -> None:
        self.store, self.lock = store, lock
        self.folder = data / "image-references"
        self.folder.mkdir(mode=0o700, exist_ok=True)
        self.folder.chmod(0o700)
        self.codec = ReferenceCodec(home)
        self.uploads = ImageUploads()
        self.slots = asyncio.Semaphore(2)

    def path(self, identifier: str) -> Path:
        try:
            return owned(self.folder, identifier)
        except ValueError:
            raise AppError("not_found", "Photo reference not found.", 404) from None

    async def get(self, identifier: str, chat_id: str | None = None) -> Reference:
        folder = self.path(identifier)
        row = await self.store.one("SELECT * FROM image_references WHERE id=?", (identifier,))
        if not row or (chat_id is not None and row["chat_id"] != chat_id):
            raise AppError("not_found", "Photo reference not found in this chat.", 404)
        if not row["available"]:
            raise AppError(
                "reference_unavailable",
                "The photo input was cleared. Attach it again to edit or retry.",
                409,
            )
        descriptor = json.loads(row["descriptor_json"])
        try:
            await asyncio.to_thread(validate_reference, folder, descriptor)
        except (OSError, ValueError, KeyError, TypeError):
            raise AppError(
                "reference_unavailable",
                "The photo input is missing or changed. Attach it again.",
                409,
            ) from None
        return Reference(identifier, descriptor)

    async def info(self, identifier: str, chat_id: str) -> ImageReference:
        self.path(identifier)
        row = await self.store.one(
            "SELECT * FROM image_references WHERE id=? AND chat_id=?", (identifier, chat_id)
        )
        if not row:
            raise AppError("not_found", "Photo reference not found in this chat.", 404)
        return projection(row)

    async def create(
        self,
        chat_id: str,
        raw: bytes,
        browser_preview: bytes | None = None,
        dimensions: tuple[int, int] | None = None,
    ) -> ImageReference:
        await chats.chat(self.store, chat_id)
        if not 0 < len(raw) <= IMAGE_LIMIT:
            raise AppError("file_too_large", "Choose a photo up to 20 MB.", 413)
        heif = is_heif(raw)
        if not (heif or raw.startswith(b"\x89PNG\r\n\x1a\n") or raw.startswith(b"\xff\xd8\xff")):
            raise AppError(
                "unsupported_type", "Photo editing accepts PNG, JPEG or HEIC photos.", 422
            )
        if browser_preview is not None and (
            not 0 < len(browser_preview) <= IMAGE_LIMIT
            or not browser_preview.startswith(b"\x89PNG\r\n\x1a\n")
            or not dimensions
            or any(type(n) is not int or n < 1 for n in dimensions)
            or dimensions[0] * dimensions[1] > 100_000_000
            or len(browser_preview) < 24
            or any(
                not 1 <= int.from_bytes(browser_preview[start : start + 4], "big") <= 2048
                for start in (16, 20)
            )
        ):
            raise AppError("image_unreadable", "Invalid photo conversion. Try again.", 422)
        if shutil.disk_usage(self.folder).free < (
            128 * 1024**2 + len(raw) + len(browser_preview or b"")
        ):
            raise AppError("low_disk", "Free at least 128 MB before attaching an edit photo.", 409)
        async with self.slots:
            identifier = uuid4().hex
            temporary = self.folder / (".preparing-" + identifier)
            temporary.mkdir(mode=0o700)
            meter = StorageMeter(temporary)
            meter.sample()
            sampling = asyncio.create_task(self.sample(meter))
            promoted = False
            try:
                with (temporary / "original").open("xb") as file:
                    os.chmod(file.name, 0o600)
                    file.write(raw)
                    file.flush()
                    os.fsync(file.fileno())
                meter.sample()
                if browser_preview is not None:
                    (temporary / "decoded.png").write_bytes(browser_preview)
                    (temporary / "decoded.png").chmod(0o600)
                    atomic_json(
                        temporary / "decoded.json",
                        {"dimensions": dimensions, "source": "browser"},
                    )
                    meter.sample()
                elif heif:
                    props: dict[str, int] = {}
                    decoded = await self.uploads.convert(raw, temporary, properties=props)
                    (temporary / "decoded.png").write_bytes(decoded)
                    (temporary / "decoded.png").chmod(0o600)
                    atomic_json(
                        temporary / "decoded.json",
                        {"dimensions": [props["width"], props["height"]]},
                    )
                    meter.sample()
                descriptor = await self.codec.normalize(temporary)
                if sampling.done():
                    await sampling
                await asyncio.to_thread(validate_reference, temporary, descriptor)
                meter.sample()
                for name in ("decoded.png", "decoded.json"):
                    (temporary / name).unlink(missing_ok=True)
                meter.sample()
                sampling.cancel()
                await asyncio.gather(sampling, return_exceptions=True)
                atomic_json(temporary / "storage.json", meter.report())
                async with self.lock:
                    await chats.chat(self.store, chat_id)
                    old = await self.store.one(
                        "SELECT * FROM image_references WHERE chat_id=? AND original_sha256=?",
                        (chat_id, descriptor["original_sha256"]),
                    )
                    if old and old["available"]:
                        await self.get(old["id"], chat_id)
                        return projection(old)
                    if old:
                        identifier = old["id"]
                        shutil.rmtree(self.path(identifier), ignore_errors=True)
                    final = self.path(identifier)
                    os.replace(temporary, final)
                    sync_directory(self.folder)
                    try:
                        date = datetime.now(UTC).isoformat()
                        await self.store.batch(
                            [
                                (
                                    "INSERT INTO image_references(id,chat_id,original_sha256,"
                                    "descriptor_json,"
                                    "available,created_at) VALUES(?,?,?,?,1,?) ON CONFLICT(id) "
                                    "DO UPDATE SET "
                                    "descriptor_json=excluded.descriptor_json,available=1,"
                                    "created_at=excluded.created_at,cleared_at=NULL",
                                    (
                                        identifier,
                                        chat_id,
                                        descriptor["original_sha256"],
                                        json.dumps(descriptor, sort_keys=True),
                                        date,
                                    ),
                                ),
                                (
                                    TOUCH_REFERENCE_JOBS,
                                    (date, identifier),
                                ),
                            ]
                        )
                    except BaseException:
                        shutil.rmtree(final)
                        raise
                    promoted = True
                    return await self.info(identifier, chat_id)
            finally:
                sampling.cancel()
                await asyncio.gather(sampling, return_exceptions=True)
                if not promoted:
                    shutil.rmtree(temporary, ignore_errors=True)

    @staticmethod
    async def sample(meter: StorageMeter) -> None:
        while True:
            await asyncio.sleep(0.1)
            meter.sample()

    def bind(self, reference: Reference, job: Path) -> None:
        bind(self.path(reference.id), job / "inputs", reference.descriptor)

    async def clear_locked(self) -> None:
        rows = await self.store.rows("SELECT id FROM image_references")
        active = await self.store.one(
            "SELECT r.job_id FROM image_job_references r JOIN image_jobs j "
            "ON j.id=r.job_id WHERE j.state IN "
            "('queued','preparing','running','cancelling') LIMIT 1"
        )
        if active:
            raise AppError(
                "image_busy", "Wait for photo edits to stop before clearing their inputs.", 409
            )
        # Mark first: interrupted clearing can never leave a retry claiming missing files.
        date = datetime.now(UTC).isoformat()
        await self.store.batch(
            [
                ("UPDATE image_references SET available=0,cleared_at=?", (date,)),
                (
                    "UPDATE image_jobs SET updated_at=? WHERE id IN "
                    "(SELECT job_id FROM image_job_references)",
                    (date,),
                ),
            ]
        )
        for row in rows:
            for pin in await self.store.rows(
                "SELECT job_id FROM image_job_references WHERE reference_id=?", (row["id"],)
            ):
                shutil.rmtree(
                    self.folder.parent / "images" / pin["job_id"] / "inputs", ignore_errors=True
                )
            shutil.rmtree(self.path(row["id"]), ignore_errors=True)

    async def recover_locked(self) -> None:
        rows = await self.store.rows("SELECT * FROM image_references")
        known = {row["id"] for row in rows}
        for folder in self.folder.iterdir():
            if folder.is_dir() and not folder.is_symlink() and folder.name not in known:
                shutil.rmtree(folder)
        for row in rows:
            pins = await self.store.rows(
                "SELECT job_id FROM image_job_references WHERE reference_id=?", (row["id"],)
            )
            expired = not pins and datetime.fromisoformat(row["created_at"]) < datetime.now(
                UTC
            ) - timedelta(days=7)
            if row["cleared_at"] or expired:
                await self.store.execute(
                    "UPDATE image_references SET available=0,cleared_at=? WHERE id=?",
                    (datetime.now(UTC).isoformat(), row["id"]),
                )
                shutil.rmtree(self.path(row["id"]), ignore_errors=True)
                for pin in pins:
                    shutil.rmtree(
                        self.folder.parent / "images" / pin["job_id"] / "inputs", ignore_errors=True
                    )
                continue
            if not row["available"]:
                # Damaged input is not a user deletion. Preserve recoverable originals.
                continue
            try:
                await self.get(row["id"])
            except AppError:
                await self.store.execute(
                    "UPDATE image_references SET available=0 WHERE id=?", (row["id"],)
                )

    async def close(self) -> None:
        await self.codec.close()
        await self.uploads.close()
