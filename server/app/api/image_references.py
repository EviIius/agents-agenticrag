"""Explicit edit uploads. IDs are chat-owned; filenames and paths are not inputs."""

import asyncio
import hashlib

from fastapi import APIRouter, Request, UploadFile
from fastapi.responses import Response

from ..db import chats
from ..errors import AppError
from ..images.jobs import Images
from ..images.uploads import IMAGE_LIMIT
from ..schemas import ImageClear, ImageReference, ImageReferenceFromJob, ImageStorage

router = APIRouter(prefix="/api")


@router.post("/chats/{chat_id}/image-references", status_code=201)
async def upload(chat_id: str, file: UploadFile, request: Request) -> ImageReference:
    await chats.chat(request.app.state.store, chat_id)
    try:
        raw = bytearray()
        while chunk := await file.read(1024 * 1024):
            raw.extend(chunk)
            if len(raw) > IMAGE_LIMIT:
                raise AppError("file_too_large", "Choose a photo up to 20 MB.", 413)
        images: Images = request.app.state.images
        reference = await images.references.create(chat_id, bytes(raw))
        await images.reference_changed(reference.id)
        return reference
    finally:
        await file.close()


@router.post("/chats/{chat_id}/image-references/from-job", status_code=201)
async def from_job(chat_id: str, body: ImageReferenceFromJob, request: Request) -> ImageReference:
    images: Images = request.app.state.images
    await chats.chat(request.app.state.store, chat_id)
    async with images.lock:
        job = await images.get(body.source_job_id)
        source = images.path(job.id) / "output/image.png"
        if not job.sha256 or not source.is_file() or source.is_symlink():
            raise AppError("not_found", "The source image is no longer available.", 404)
        raw = await asyncio.to_thread(source.read_bytes)
        if hashlib.sha256(raw).hexdigest() != job.sha256:
            raise AppError(
                "reference_unavailable", "The source image changed. Restore it from backup.", 409
            )
    reference = await images.references.create(chat_id, raw)
    await images.reference_changed(reference.id)
    return reference


@router.get("/chats/{chat_id}/image-references/{identifier}")
async def info(chat_id: str, identifier: str, request: Request) -> ImageReference:
    await chats.chat(request.app.state.store, chat_id)
    images: Images = request.app.state.images
    return await images.references.info(identifier, chat_id)


@router.get("/chats/{chat_id}/image-references/{identifier}/preview")
async def preview(chat_id: str, identifier: str, request: Request) -> Response:
    await chats.chat(request.app.state.store, chat_id)
    images: Images = request.app.state.images
    async with images.lock:
        ref = await images.references.get(identifier, chat_id)
        raw = await asyncio.to_thread((images.references.path(ref.id) / "reference.png").read_bytes)
    return Response(
        raw,
        media_type="image/png",
        headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"},
    )


@router.get("/images/jobs/{identifier}/reference")
async def job_reference(identifier: str, request: Request) -> Response:
    images: Images = request.app.state.images
    async with images.lock:
        job = await images.get(identifier)
        if not job.reference:
            raise AppError("not_found", "This job has no photo reference.", 404)
        reference = await images.references.get(job.reference.id)
        raw = await asyncio.to_thread(
            (images.references.path(reference.id) / "reference.png").read_bytes
        )
    return Response(
        raw,
        media_type="image/png",
        headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"},
    )


@router.post("/images/references/clear")
async def clear(body: ImageClear, request: Request) -> ImageStorage:
    images: Images = request.app.state.images
    async with images.lock:
        await images.references.clear_locked()
        # Refresh affected snapshots through existing push events.
        for row in await images.store.rows("SELECT job_id FROM image_job_references"):
            await images.emit(row["job_id"])
    return await images.storage()
