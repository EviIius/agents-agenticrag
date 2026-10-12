import json
from collections.abc import AsyncIterator
from typing import cast

from fastapi import APIRouter, Request
from sse_starlette import EventSourceResponse

from ..errors import AppError
from ..schemas import ActiveRun, RunEvent

router = APIRouter(prefix="/api")


@router.get("/runs/active")
async def active(request: Request) -> list[ActiveRun]:
    return cast(list[ActiveRun], await request.app.state.runs.active())


@router.get("/runs/{identifier}/events")
async def events(identifier: str, request: Request) -> EventSourceResponse:
    run = request.app.state.runs.runs.get(identifier)
    if not run:
        raise AppError("not_found", "Run expired; reload the persisted chat.", 404)
    try:
        after = int(request.headers.get("last-event-id", "0"))
    except ValueError:
        after = 0

    async def stream() -> AsyncIterator[dict[str, str]]:
        async for seq, event in run.tail(after):
            yield {
                "id": str(seq),
                "event": event.type,
                "data": json.dumps(event.data),
            }

    return EventSourceResponse(
        stream(), ping=15, headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )


@router.post("/runs/{identifier}/cancel", status_code=202)
async def cancel(identifier: str, request: Request) -> dict[str, bool]:
    await request.app.state.runs.cancel(identifier)
    return {"ok": True}


@router.get("/_schema/run-event", response_model=RunEvent)
async def schema() -> RunEvent:
    return RunEvent.model_validate({"type": "run.closed", "data": {}})
