"""Additive definition/graph APIs; original workflow endpoints stay frozen."""

import json
from typing import Any, Literal, cast

from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse, Response
from sse_starlette import EventSourceResponse

from ..workflows.blocks import check_models
from ..workflows.defs import Conflict
from ..workflows.engine import GraphRunner
from ..workflows.graph import validate
from ..workflows.graph_schemas import (
    BlockCatalog,
    BlockEntry,
    Decision,
    DefConflict,
    DefCreate,
    Definition,
    DefSave,
    GraphResume,
    GraphSubmit,
    ReusePlan,
    RunPage,
    RunV2,
    Snapshot,
    SnapshotLabel,
    Template,
    ValidationBody,
    ValidationResult,
)
from ..workflows.template_graphs import template_list
from ..workflows.views import detail, page, stream

router = APIRouter(prefix="/api/workflows")


def manager(request: Request) -> GraphRunner:
    return cast(GraphRunner, request.app.state.workflow_graphs)


@router.get("/blocks")
async def catalog(request: Request) -> BlockCatalog:
    engine = manager(request).legacy.images.engine.status()
    transcription = await manager(request).legacy.transcription.engine.status()
    saved = await manager(request).store.one(
        "SELECT 1 FROM transcripts WHERE status='ready' LIMIT 1"
    )
    availability: dict[str, tuple[bool, str | None]] = {
        "generate_image": (engine.available, engine.reason),
        "transcribe": (
            transcription.ready or bool(saved),
            None
            if transcription.ready or saved
            else "The transcription engine is not ready. Settings → Transcription.",
        ),
    }
    return BlockCatalog(
        blocks=[
            BlockEntry(
                kind=kind,
                label=label,
                category=category,
                available=availability.get(kind, (True, None))[0],
                reason=availability.get(kind, (True, None))[1],
            )
            for kind, label, category in [
                ("start", "Start", "Inputs"),
                ("generate", "Generate text", "AI"),
                ("transcribe", "Transcribe recording", "Media"),
                ("clean_transcript", "Clean up transcript", "Media"),
                ("generate_image", "Create images", "Media"),
                ("review", "Approve or edit", "Review"),
                ("pick", "Pick favorites", "Review"),
                ("output", "Save results", "Output"),
            ]
        ]
    )


@router.get("/templates")
async def templates() -> list[Template]:
    return template_list()


@router.get("/defs")
async def definitions(request: Request) -> list[Definition]:
    return await manager(request).defs.list_defs()


@router.post("/defs", status_code=201)
async def create(body: DefCreate, request: Request) -> Definition:
    return await manager(request).defs.create(body)


@router.get("/defs/{identifier}")
async def definition(identifier: str, request: Request) -> Definition:
    return await manager(request).defs.get(identifier)


@router.put(
    "/defs/{identifier}", response_model=Definition, responses={409: {"model": DefConflict}}
)
async def save(identifier: str, body: DefSave, request: Request) -> Any:
    try:
        return await manager(request).defs.save(identifier, body)
    except Conflict as exc:
        return JSONResponse(
            {
                "error": {"code": exc.code, "message": exc.message},
                "current": exc.current.model_dump(by_alias=True),
            },
            status_code=409,
        )


@router.post("/defs/{identifier}/duplicate", status_code=201)
async def duplicate(identifier: str, request: Request) -> Definition:
    return await manager(request).defs.duplicate(identifier)


@router.delete("/defs/{identifier}", status_code=204)
async def archive(identifier: str, request: Request) -> Response:
    await manager(request).defs.archive(identifier)
    return Response(status_code=204)


@router.post("/defs/{identifier}/validate")
async def validation(identifier: str, body: ValidationBody, request: Request) -> ValidationResult:
    from ..errors import AppError
    from ..workflows.graph import Issue

    graph = body.graph or (await manager(request).defs.get(identifier)).graph
    issues = validate(graph)
    if not any(i.severity == "error" for i in issues):
        try:
            await check_models(manager(request), graph)
        except AppError as exc:
            issues.append(Issue(code=exc.code, message=exc.message))
    return ValidationResult(issues=issues, graph=graph)


@router.get("/defs/{identifier}/snapshots")
async def snapshots(identifier: str, request: Request) -> list[Snapshot]:
    return await manager(request).defs.snapshots(identifier)


@router.patch("/defs/{identifier}/snapshots/{snapshot_id}")
async def label(
    identifier: str, snapshot_id: str, body: SnapshotLabel, request: Request
) -> Snapshot:
    return await manager(request).defs.label(identifier, snapshot_id, body.label)


@router.post("/defs/{identifier}/runs", status_code=202)
async def submit(identifier: str, body: GraphSubmit, request: Request) -> RunV2:
    return await manager(request).submit(identifier, body)


@router.get("/defs/{identifier}/reuse")
async def reuse_plan(
    identifier: str, request: Request, node_id: str, mode: Literal["run", "test"] = "run"
) -> ReusePlan:
    from ..workflows.reuse import plan

    return await plan(manager(request), identifier, node_id, mode=mode)


@router.get("/runs")
async def run_list(
    request: Request,
    def_id: str | None = None,
    state: str | None = None,
    mode: Literal["run"] = "run",
    cursor: str | None = None,
    limit: int = Query(50, ge=1, le=100),
) -> RunPage:
    return await page(manager(request), def_id, state, cursor, limit)


@router.get("/runs/{identifier}/v2")
async def run_detail(identifier: str, request: Request) -> RunV2:
    return await detail(manager(request), identifier)


@router.post("/runs/{identifier}/decision")
async def decision(identifier: str, body: Decision, request: Request) -> RunV2:
    return await manager(request).decision(identifier, body)


@router.post("/runs/{identifier}/v2/resume", status_code=202)
async def resume(identifier: str, body: GraphResume, request: Request) -> RunV2:
    return await manager(request).resume(identifier, body)


@router.post("/runs/{identifier}/v2/cancel")
async def cancel(identifier: str, request: Request) -> RunV2:
    return await manager(request).cancel(identifier)


@router.get("/runs/{identifier}/v2/sources")
async def sources(identifier: str, request: Request) -> list[dict[str, Any]]:
    await manager(request).get(identifier)
    return [
        {"node_id": r["node_id"], "sha256": r["sha256"], "source": json.loads(r["source_json"])}
        for r in await manager(request).store.rows(
            "SELECT * FROM workflow_graph_sources WHERE run_id=? ORDER BY node_id", (identifier,)
        )
    ]


@router.get("/runs/{identifier}/v2/export")
async def export(
    identifier: str, request: Request, format: Literal["md", "json"] = "md"
) -> Response:
    run = await manager(request).get(identifier)
    originals = await sources(identifier, request)
    if format == "json":
        body = json.dumps(
            {"run": run.model_dump(by_alias=True), "sources": originals, "review_required": True},
            ensure_ascii=False,
            indent=2,
        )
    else:
        blocks = ["# Aether workflow — draft for review", "State: " + run.state]
        for section in run.results:
            blocks.append("## " + section.label)
            for item in section.items:
                blocks.append("### " + item.label)
                blocks.append(
                    item.value
                    if isinstance(item.value, str)
                    else json.dumps(item.value, ensure_ascii=False, indent=2)
                )
        if any((state.output or {}).get("include_sources") for state in run.nodes.values()):
            for original in originals:
                source = original["source"]
                blocks.extend(
                    [
                        "## Original transcript",
                        source["text"],
                        "## Original source timestamps",
                        json.dumps(source["segments"], ensure_ascii=False, indent=2),
                    ]
                )
        body = "\n\n".join(blocks)
    return Response(
        body,
        media_type="application/json" if format == "json" else "text/markdown",
        headers={
            "Content-Disposition": (
                f'attachment; filename="Aether-workflow-{identifier[:8]}.{format}"'
            ),
            "Cache-Control": "no-store",
        },
    )


@router.get("/stream")
async def events(request: Request) -> EventSourceResponse:
    return EventSourceResponse(
        stream(manager(request), request.headers.get("last-event-id", "0:0")),
        ping=15,
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/defs/{identifier}/tests")
async def test_runs(identifier: str, request: Request, node_id: str) -> list[RunV2]:
    engine = manager(request)
    await engine.defs.get(identifier)
    await engine.expire_tests()
    rows = await engine.store.rows(
        "SELECT r.id FROM workflow_graph_runs r JOIN workflow_graph_steps s ON s.run_id=r.id "
        "WHERE r.def_id=? AND r.mode='test' AND s.node_id=? AND s.attempt>0 "
        "ORDER BY r.created_at DESC,r.id DESC LIMIT 20",
        (identifier, node_id),
    )
    return [await engine.get(row["id"]) for row in rows]
