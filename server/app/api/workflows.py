"""Private fixed-workflow inputs/outputs, with event replay and reviewed downloads."""

import json
from collections.abc import AsyncIterator
from typing import Literal, cast

from fastapi import APIRouter, Request
from fastapi.responses import Response
from sse_starlette import EventSourceResponse

from ..errors import AppError
from ..workflows.jobs import Workflows
from ..workflows.qualification import image_models
from ..workflows.schemas import (
    WorkflowChange,
    WorkflowCreate,
    WorkflowRecording,
    WorkflowResume,
    WorkflowRun,
    WorkflowSnapshot,
    WorkflowSource,
)

router = APIRouter(prefix="/api/workflows")


@router.get("/image-models")
async def compatible_models(request: Request) -> list[dict[str, str]]:
    return await image_models(request.app.state.registry)


def manager(request: Request) -> Workflows:
    return cast(Workflows, request.app.state.workflows)


@router.get("")
async def snapshot(request: Request) -> WorkflowSnapshot:
    return WorkflowSnapshot(runs=await manager(request).list())


@router.get("/recordings")
async def recordings(request: Request) -> list[WorkflowRecording]:
    rows = await request.app.state.store.rows(
        "SELECT a.id,a.filename,t.status FROM attachments a JOIN transcripts t "
        "ON t.attachment_id=a.id WHERE a.kind='audio' ORDER BY a.created_at DESC LIMIT 100"
    )
    return [WorkflowRecording(**row) for row in rows]


@router.post("/runs", status_code=202)
async def create(body: WorkflowCreate, request: Request) -> WorkflowRun:
    return await manager(request).submit(body)


@router.get("/runs/{identifier}")
async def detail(identifier: str, request: Request) -> WorkflowRun:
    return await manager(request).get(identifier)


@router.post("/runs/{identifier}/resume", status_code=202)
async def resume(identifier: str, body: WorkflowResume, request: Request) -> WorkflowRun:
    return await manager(request).resume(identifier, body)


@router.post("/runs/{identifier}/cancel")
async def cancel(identifier: str, request: Request) -> WorkflowRun:
    return await manager(request).cancel(identifier)


@router.get("/runs/{identifier}/source")
async def source(identifier: str, request: Request) -> WorkflowSource:
    await manager(request).get(identifier)
    row = await request.app.state.store.one(
        "SELECT source_json FROM workflow_runs WHERE id=?", (identifier,)
    )
    if not row or not row["source_json"]:
        raise AppError("not_found", "The source transcript is not ready.", 404)
    return WorkflowSource.model_validate_json(row["source_json"])


@router.get("/runs/{identifier}/export")
async def export(
    identifier: str, request: Request, format: Literal["md", "json"] = "md"
) -> Response:
    run = await manager(request).get(identifier)
    row = await request.app.state.store.one(
        "SELECT source_json FROM workflow_runs WHERE id=?", (identifier,)
    )
    source_data = json.loads(row["source_json"]) if row and row["source_json"] else None
    if format == "json":
        body = json.dumps(
            {"run": run.model_dump(), "source": source_data, "review_required": True},
            ensure_ascii=False,
            indent=2,
        )
    else:
        blocks = ["# Atelier workflow — draft for review", f"State: {run.state}"]
        for step in run.steps:
            blocks.append(f"## {step.label}\n\n{step.state}")
            if step.output:
                if step.output.get("text"):
                    blocks.append(str(step.output["text"]))
                if step.output.get("image_job_id"):
                    blocks.append("Image job: " + step.output["image_job_id"])
        if source_data:
            blocks.extend(["## Original transcript", source_data["text"]])
            if source_data["segments"]:
                blocks.append("## Original source timestamps")
                blocks.extend(
                    f"[{segment['start']}s–{segment['end']}s] "
                    + (f"{segment['speaker']}: " if segment.get("speaker") else "")
                    + segment["text"]
                    for segment in source_data["segments"]
                )
        body = "\n\n".join(blocks)
    return Response(
        body,
        media_type="application/json" if format == "json" else "text/markdown",
        headers={
            "Content-Disposition": "attachment; "
            f'filename="Atelier-workflow-{identifier[:8]}.{format}"',
            "Cache-Control": "no-store",
        },
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


@router.get("/_schema/change", response_model=WorkflowChange | None)
async def change_schema() -> None:
    return None
