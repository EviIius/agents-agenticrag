import asyncio
import hashlib
import os
import sqlite3
from pathlib import Path
from urllib.parse import quote

from fastapi import APIRouter, Form, Request, Response, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from sse_starlette.sse import EventSourceResponse

from ..db.connections import now, uid
from ..errors import AppError
from ..library.ingest import Library
from ..schemas import (
    LibraryCollection,
    LibraryCollectionInfo,
    LibraryDelete,
    LibraryDocument,
    LibraryIndex,
    LibraryMove,
    LibrarySelection,
    LibraryText,
)

router = APIRouter(prefix="/api/library")
LIMIT = 100 * 1024**2
TYPES = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".txt": "text/plain",
    ".md": "text/markdown",
    ".html": "text/html",
}


def manager(request: Request) -> Library:
    return request.app.state.library  # type: ignore[no-any-return]


@router.get("")
async def index(request: Request) -> LibraryIndex:
    return LibraryIndex.model_validate(await manager(request).snapshot())


@router.post("/embedding")
async def embedding(body: LibrarySelection, request: Request) -> LibraryIndex:
    choice = body.embedding.model_dump() if body.embedding else None
    return LibraryIndex.model_validate(await manager(request).configure(choice))


@router.get("/events")
async def events(request: Request, after: int = 0) -> EventSourceResponse:
    try:
        cursor = max(0, int(request.headers.get("Last-Event-ID", str(after))))
    except ValueError:
        raise AppError("validation_error", "Invalid event cursor.", 422) from None
    return EventSourceResponse(
        manager(request).events(cursor), ping=15, headers={"Cache-Control": "no-store"}
    )


@router.post("/documents", status_code=201, response_model=LibraryDocument)
async def upload(
    file: UploadFile, request: Request, collection_id: str | None = Form(None)
) -> LibraryDocument | JSONResponse:
    library = manager(request)
    identifier = uid()
    filename = Path(file.filename or "File").name
    suffix = Path(filename).suffix.lower()
    target = library.folder / (identifier + suffix)
    partial = target.with_suffix(suffix + ".part")
    inserted = False
    try:
        if not library.available:
            raise AppError("library_unavailable", "Library needs SQLite extension support.", 503)
        if suffix not in TYPES or len(filename) > 512 or any(ord(c) < 32 for c in filename):
            raise AppError(
                "unsupported_type", "Choose PDF, Word, Markdown, UTF-8 text or HTML.", 422
            )
        # Share the mutation lock, not the background job's embedding capacity.
        async with library.control:
            if collection_id and not await library.store.one(
                "SELECT id FROM library_collections WHERE id=?", (collection_id,)
            ):
                raise AppError("not_found", "Collection not found.", 404)
            total = 0
            digest = hashlib.sha256()
            with partial.open("xb") as destination:
                partial.chmod(0o600)
                while data := await file.read(1024 * 1024):
                    total += len(data)
                    if total > LIMIT:
                        raise AppError(
                            "library_too_large", "Library files can be up to 100 MB.", 413
                        )
                    digest.update(data)
                    await asyncio.to_thread(destination.write, data)
                destination.flush()
                syncing = asyncio.create_task(asyncio.to_thread(os.fsync, destination.fileno()))
                try:
                    await asyncio.shield(syncing)
                except asyncio.CancelledError:
                    await syncing
                    raise
            duplicate = await library.store.one(
                "SELECT id FROM library_documents WHERE sha256=?", (digest.hexdigest(),)
            )
            if duplicate:
                return JSONResponse(
                    status_code=409,
                    content={
                        "error": {
                            "code": "document_duplicate",
                            "message": "This file is already in the Library.",
                            "document_id": duplicate["id"],
                        }
                    },
                )
            partial.replace(target)
            stamp = now()
            await library.store.execute(
                (
                    "INSERT INTO "
                    "library_documents(id,collection_id,filename,mime_type,bytes,"
                    "sha256,path,status,created_at,updated_at) "
                    "VALUES (?,?,?,?,?,?,?,'queued',?,?)"
                ),
                (
                    identifier,
                    collection_id,
                    filename,
                    TYPES[suffix],
                    total,
                    digest.hexdigest(),
                    "library/" + target.name,
                    stamp,
                    stamp,
                ),
            )
            inserted = True
            await library.emit("document.queued", {"id": identifier, "status": "queued"})
            library.resume()
        value = await library.snapshot()
        return LibraryDocument.model_validate(
            next(d for d in value["documents"] if d["id"] == identifier)
        )
    finally:
        partial.unlink(missing_ok=True)
        if not inserted:
            target.unlink(missing_ok=True)
        await file.close()


@router.patch("/documents/{identifier}", status_code=204)
async def move(identifier: str, body: LibraryMove, request: Request) -> None:
    library = manager(request)
    async with library.control:
        if not await library.store.one(
            "SELECT id FROM library_documents WHERE id=?", (identifier,)
        ):
            raise AppError("not_found", "File not found.", 404)
        if body.collection_id and not await library.store.one(
            "SELECT id FROM library_collections WHERE id=?", (body.collection_id,)
        ):
            raise AppError("not_found", "Collection not found.", 404)
        await library.store.execute(
            "UPDATE library_documents SET collection_id=?,updated_at=? WHERE id=?",
            (body.collection_id, now(), identifier),
        )
        await library.emit("library.changed", {})


@router.delete("/documents/{identifier}", status_code=204)
async def delete(identifier: str, request: Request) -> None:
    await manager(request).delete(identifier)


@router.post("/documents/{identifier}/reindex", status_code=204)
async def retry(identifier: str, request: Request) -> None:
    await manager(request).reindex(identifier)


@router.post("/reindex", status_code=204)
async def reindex(request: Request) -> None:
    await manager(request).reindex()


@router.get("/documents/{identifier}/file")
async def original(identifier: str, request: Request) -> FileResponse:
    library = manager(request)
    row = await library.store.one("SELECT * FROM library_documents WHERE id=?", (identifier,))
    if not row:
        raise AppError("not_found", "File not found.", 404)
    path = library.folder / Path(row["path"]).name
    if not path.is_file():
        raise AppError("not_found", "Original file unavailable.", 404)
    encoded_name = quote(row["filename"], safe="")
    disposition = "inline" if row["mime_type"] == "application/pdf" else "attachment"
    return FileResponse(
        path,
        media_type=row["mime_type"],
        headers={
            "Cache-Control": "private, no-store",
            "X-Content-Type-Options": "nosniff",
            "Content-Security-Policy": "sandbox; default-src 'none'",
            "Content-Disposition": f"{disposition}; filename*=UTF-8''{encoded_name}",
        },
    )


@router.get("/documents/{identifier}/text")
async def text(identifier: str, request: Request, response: Response) -> LibraryText:
    library = manager(request)
    row = await library.store.one(
        "SELECT extracted_text FROM library_documents WHERE id=?", (identifier,)
    )
    if not row:
        raise AppError("not_found", "File not found.", 404)
    response.headers["Cache-Control"] = "private, no-store"
    return LibraryText(text=row["extracted_text"] or "")


async def save_collection(
    body: LibraryCollection, library: Library, identifier: str | None
) -> LibraryCollectionInfo:
    name = body.name.strip()
    if not name:
        raise AppError("validation_error", "Enter a collection name.", 422)
    async with library.control:
        stamp = now()
        if identifier and not await library.store.one(
            "SELECT id FROM library_collections WHERE id=?", (identifier,)
        ):
            raise AppError("not_found", "Collection not found.", 404)
        try:
            if identifier:
                await library.store.execute(
                    "UPDATE library_collections SET name=?,updated_at=? WHERE id=?",
                    (name, stamp, identifier),
                )
            else:
                identifier = uid()
                await library.store.execute(
                    "INSERT INTO library_collections VALUES (?,?,?,?)",
                    (identifier, name, stamp, stamp),
                )
        except sqlite3.IntegrityError:
            raise AppError(
                "collection_duplicate", "A collection already uses this name.", 409
            ) from None
        await library.emit("library.changed", {})
        row = await library.store.one("SELECT * FROM library_collections WHERE id=?", (identifier,))
        return LibraryCollectionInfo.model_validate(row)


@router.post("/collections", status_code=201)
async def create_collection(body: LibraryCollection, request: Request) -> LibraryCollectionInfo:
    return await save_collection(body, manager(request), None)


@router.patch("/collections/{identifier}")
async def rename_collection(
    identifier: str, body: LibraryCollection, request: Request
) -> LibraryCollectionInfo:
    return await save_collection(body, manager(request), identifier)


@router.delete("/collections/{identifier}", status_code=204)
async def delete_collection(identifier: str, request: Request) -> None:
    library = manager(request)
    async with library.control:
        if not await library.store.one(
            "SELECT id FROM library_collections WHERE id=?", (identifier,)
        ):
            raise AppError("not_found", "Collection not found.", 404)
        await library.store.execute("DELETE FROM library_collections WHERE id=?", (identifier,))
        await library.emit("library.changed", {})


@router.delete("", status_code=204)
async def clear(body: LibraryDelete, request: Request) -> None:
    if body.confirmation != "DELETE":
        raise AppError("validation_error", "Type DELETE to remove all Library files.", 422)
    await manager(request).delete()
