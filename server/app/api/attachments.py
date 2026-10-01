from pathlib import Path

from fastapi import APIRouter, Request, UploadFile
from fastapi.responses import FileResponse

from ..db.connections import now, uid
from ..errors import AppError
from ..schemas import Attachment

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


@router.post("", status_code=201)
async def upload(file: UploadFile, request: Request) -> Attachment:
    filename = Path(file.filename or "attachment").name
    suffix = Path(filename).suffix.lower()
    image = suffix in {".png", ".jpg", ".jpeg", ".webp", ".gif"}
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


@router.get("/{identifier}")
async def get(identifier: str, request: Request) -> FileResponse:
    row = await request.app.state.store.one("SELECT * FROM attachments WHERE id=?", (identifier,))
    if not row:
        raise AppError("not_found", "Attachment not found.", 404)
    return FileResponse(
        request.app.state.config.data_dir / str(row["path"]),
        media_type=str(row["mime_type"]),
        filename=str(row["filename"]),
    )
