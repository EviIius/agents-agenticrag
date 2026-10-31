"""Default-off AS0 fake desktop APIs; no native action or provider dispatch."""

from collections.abc import AsyncIterator
from typing import cast

from fastapi import APIRouter, Request
from sse_starlette import EventSourceResponse

from ..assistant.contracts import DesktopTask, TaskCreate, TaskDecision, TaskEvent, TaskList
from ..assistant.manager import DesktopTasks
from ..errors import AppError

router = APIRouter(prefix="/api")


def manager(request: Request) -> DesktopTasks:
    if not request.app.state.config.assistant_enabled:
        raise AppError("assistant_disabled", "Computer use is not enabled.", 403)
    value = getattr(request.app.state, "assistant", None)
    if value is None:
        raise AppError(
            "assistant_unavailable", "No qualified computer-use driver is configured.", 409
        )
    return cast(DesktopTasks, value)


@router.get("/chats/{chat_id}/assistant-tasks")
async def listing(chat_id: str, request: Request) -> TaskList:
    return TaskList(tasks=await manager(request).listing(chat_id))


@router.post("/chats/{chat_id}/assistant-tasks", status_code=202)
async def create(chat_id: str, body: TaskCreate, request: Request) -> DesktopTask:
    return await manager(request).create(chat_id, body)


@router.get("/assistant/tasks/{identifier}")
async def get(identifier: str, request: Request) -> DesktopTask:
    return await manager(request).get(identifier)


@router.post("/assistant/tasks/{identifier}/decision", status_code=202)
async def decision(identifier: str, body: TaskDecision, request: Request) -> DesktopTask:
    return await manager(request).decide(identifier, body)


@router.post("/assistant/tasks/{identifier}/cancel", status_code=202)
async def cancel(identifier: str, request: Request) -> DesktopTask:
    return await manager(request).cancel(identifier)


@router.get("/assistant/tasks/{identifier}/events")
async def events(identifier: str, request: Request) -> EventSourceResponse:
    host = manager(request)
    await host.get(identifier)
    try:
        after = max(0, int(request.headers.get("last-event-id", "0")))
    except ValueError:
        after = 0

    async def stream() -> AsyncIterator[dict[str, str]]:
        async for sequence, event in host.tail(identifier, after):
            yield {"id": str(sequence), "event": event.type, "data": event.model_dump_json()}

    return EventSourceResponse(stream(), ping=15, headers={"Cache-Control": "no-cache"})


@router.get("/_schema/assistant-event", response_model=TaskEvent)
async def event_schema() -> None:
    raise AppError("not_found", "Schema-only endpoint.", 404)
