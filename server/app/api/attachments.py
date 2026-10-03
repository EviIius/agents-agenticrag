import asyncio
import mimetypes
import shutil
from pathlib import Path
from typing import Literal

from fastapi import APIRouter, Form, Request, UploadFile
from fastapi.responses import FileResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from ..db import attachments as records
from ..db.connections import now, uid
from ..errors import AppError, error_response
from ..schemas import Attachment
from ..transcribe.engine import AUDIO
from ..transcribe.jobs import TranscriptionManager

router = APIRouter(prefix="/api/attachments")
TEXT = {
    ".txt",
    ".md",
    ".csv",
    ".json",
    ".yaml",
    ".yml",
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".html",
    ".css",
    ".sql",
    ".sh",
    ".log",
}


AUDIO_LIMIT = 4 * 1024**3


class UploadSpaceGuard:
    """Check disk headroom before Starlette's multipart parser consumes the body."""

    def __init__(self, app: ASGIApp, data_dir: Path) -> None:
        self.app, self.data_dir = app, data_dir.expanduser()

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if (
            scope["type"] == "http"
            and scope["method"] == "POST"
            and scope["path"] == "/api/attachments"
        ):
            headers = dict(scope["headers"])
            try:
                length = int(headers.get(b"content-length", b"0"))
            except ValueError:
                length = 0
            self.data_dir.mkdir(parents=True, exist_ok=True)
            if length and shutil.disk_usage(self.data_dir).free < length + 5 * 1024**3:
                await error_response(
                    "disk_full", "There isn't enough free space on the Mac for this recording.", 507
                )(scope, receive, send)
                return
        await self.app(scope, receive, send)


@router.post("", status_code=201)
async def upload(
    file: UploadFile, request: Request, channels: Literal["mix", "split"] = Form("mix")
) -> Attachment:
    filename = Path(file.filename or "attachment").name
    suffix = Path(filename).suffix.lower()
    image = suffix in {".png", ".jpg", ".jpeg", ".webp", ".gif"}
    if suffix in AUDIO:
        manager: TranscriptionManager = request.app.state.transcription
        status = await manager.engine.status()
        if not status.ready or suffix not in status.audio_extensions:
            raise AppError(
                "transcription_unavailable", "Recordings need the transcription engine", 422
            )
        identifier = uid()
        relative = f"attachments/{identifier}{suffix}"
        target = request.app.state.config.data_dir / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        partial = target.with_suffix(target.suffix + ".part")
        total = 0
        try:
            with partial.open("xb") as destination:
                partial.chmod(0o600)
                while chunk := await file.read(1024 * 1024):
                    total += len(chunk)
                    if total > AUDIO_LIMIT:
                        raise AppError("audio_too_large", "Recordings can be up to 4 GB.", 413)
                    await asyncio.to_thread(destination.write, chunk)
            partial.replace(target)
            mime = mimetypes.guess_type("recording" + suffix)[0] or "application/octet-stream"
            await request.app.state.store.execute(
                "INSERT INTO attachments(id,kind,filename,mime_type,bytes,path,"
                "created_at) VALUES (?,'audio',?,?,?,?,?)",
                (identifier, filename, mime, total, relative, now()),
            )
            return await manager.start(identifier, channels)
        except BaseException:
            partial.unlink(missing_ok=True)
            target.unlink(missing_ok=True)
            await request.app.state.store.execute(
                "DELETE FROM attachments WHERE id=?", (identifier,)
            )
            raise
        finally:
            await file.close()
    if not image and suffix not in TEXT:
        raise AppError("unsupported_type", "PDF and Office support comes later.", 422)
    limit = 20 * 1024 * 1024 if image else 512 * 1024
    data = await file.read(limit + 1)
    if len(data) > limit:
        raise AppError("file_too_large", "Image limit is 20 MB; text file limit is 512 KB.", 413)
    mime = "text/plain"
    if image:
        signatures = [
            (b"\x89PNG\r\n\x1a\n", "image/png"),
            (b"\xff\xd8\xff", "image/jpeg"),
            (b"GIF8", "image/gif"),
        ]
        mime = next((m for signature, m in signatures if data.startswith(signature)), "")
        if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
            mime = "image/webp"
        if not mime:
            raise AppError("unsupported_type", "The file is not a supported image.", 422)
    else:
        try:
            data.decode("utf-8")
        except UnicodeError:
            raise AppError("unsupported_type", "Text files must be UTF-8.", 422) from None
    identifier = uid()
    relative = f"attachments/{identifier}{suffix}"
    path = request.app.state.config.data_dir / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    path.chmod(0o600)
    attachment = Attachment(
        id=identifier,
        kind="image" if image else "text",
        filename=filename,
        mime_type=mime,
        bytes=len(data),
    )
    await request.app.state.store.execute(
        "INSERT INTO attachments(id,kind,filename,mime_type,bytes,path,created_at"
        ") VALUES (?,?,?,?,?,?,?)",
        (identifier, attachment.kind, filename, mime, len(data), relative, now()),
    )
    return attachment


@router.get("/pending")
async def pending(request: Request) -> list[Attachment]:
    store = request.app.state.store
    return [
        await records.attachment(store, str(row["id"]))
        for row in await store.rows(
            "SELECT id FROM attachments WHERE kind='audio' AND message_id IS NU"
            "LL ORDER BY created_at DESC,id DESC"
        )
    ]


@router.delete("/{identifier}", status_code=204)
async def remove(identifier: str, request: Request) -> None:
    await request.app.state.transcription.remove(identifier)


@router.get("/{identifier}/info")
async def info(identifier: str, request: Request) -> Attachment:
    return await records.attachment(request.app.state.store, identifier)


@router.get("/{identifier}")
async def get(identifier: str, request: Request) -> FileResponse:
    row = await request.app.state.store.one("SELECT * FROM attachments WHERE id=?", (identifier,))
    if not row:
        raise AppError("not_found", "Attachment not found.", 404)
    path = request.app.state.config.data_dir / str(row["path"])
    if not row["audio_available"] or not path.is_file():
        raise AppError(
            "audio_removed", "The audio was removed; the transcript is still available.", 404
        )
    return FileResponse(
        path,
        media_type=str(row["mime_type"]),
        filename=str(row["filename"]),
    )
