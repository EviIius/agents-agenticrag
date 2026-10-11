import json
from collections.abc import AsyncIterator
from typing import Literal, cast

from fastapi import APIRouter, Request
from fastapi.responses import FileResponse
from sse_starlette import EventSourceResponse

from ..images.jobs import Images
from ..schemas import (
    ImageChange,
    ImageClear,
    ImageCreate,
    ImageJob,
    ImageSnapshot,
    ImageStatus,
    ImageStorage,
)

router = APIRouter(prefix="/api/images")


def manager(request: Request) -> Images:
    return cast(Images, request.app.state.images)


@router.get("/status")
async def status(request: Request) -> ImageStatus:
    return manager(request).engine.status()


@router.get("")
async def snapshot(request: Request) -> ImageSnapshot:
    return await manager(request).snapshot()


@router.get("/jobs")
async def jobs(request: Request, before: str | None = None) -> list[ImageJob]:
    return await manager(request).list(before)


@router.post("/jobs", status_code=202)
async def create(body: ImageCreate, request: Request) -> ImageJob:
    return await manager(request).submit(body)


@router.get("/jobs/{identifier}")
async def job(identifier: str, request: Request) -> ImageJob:
    return await manager(request).get(identifier)


@router.post("/jobs/{identifier}/cancel")
async def cancel(identifier: str, request: Request) -> ImageJob:
    return await manager(request).cancel(identifier)


@router.delete("/jobs/{identifier}/output", status_code=204)
async def remove(identifier: str, request: Request) -> None:
    await manager(request).remove(identifier)


@router.post("/clear")
async def clear(body: ImageClear, request: Request) -> ImageStorage:
    return await manager(request).clear()


@router.get("/jobs/{identifier}/output/{format}")
async def output(identifier: str, format: Literal["png", "json"], request: Request) -> FileResponse:
    path = await manager(request).artifact(identifier, format)
    return FileResponse(
        path,
        media_type="image/png" if format == "png" else "application/json",
        filename=f"Atelier-{identifier[:8]}.{format}",
        headers={"Cache-Control": "no-store"},
    )


@router.get("/events")
async def events(request: Request) -> EventSourceResponse:
    try:
        after = int(request.headers.get("last-event-id", "0"))
    except ValueError:
        after = 0

    async def stream() -> AsyncIterator[dict[str, str]]:
        async for sequence, kind, data in manager(request).tail(after):
            yield {"id": str(sequence), "event": kind, "data": json.dumps(data)}

    return EventSourceResponse(
        stream(), ping=15, headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )


@router.get("/_schema/change", response_model=ImageChange | None)
async def change_schema() -> None:
    # Contract discovery only, mirroring the existing SSE schema endpoints.
    return None
