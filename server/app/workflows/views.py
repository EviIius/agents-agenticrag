"""Read-only legacy projection and a replayable merged stream, without polling."""

import asyncio
import base64
import json
from collections.abc import AsyncGenerator
from typing import Any, cast

from ..errors import AppError
from .engine import GraphRunner
from .graph import CleanNode, GenerateNode, ModelRef, canonical
from .graph_schemas import NodeState, ResultSection, RunPage, RunV2
from .schemas import WorkflowRun
from .source import timestamped
from .template_graphs import template_graph


async def legacy_view(manager: GraphRunner, run: WorkflowRun) -> RunV2:
    spec = run.input
    graph = template_graph(
        spec.template, cleanup=bool(spec.cleanup_model), review=spec.review_prompt, seeds=spec.seeds
    )
    graph.settings.default_model = ModelRef(
        connection_id=spec.model.connection_id, model_id=spec.model.model_id
    )
    for node in graph.nodes:
        if isinstance(node, GenerateNode):
            node.config.params = spec.model.params.model_copy(deep=True)
        elif isinstance(node, CleanNode) and spec.cleanup_model:
            node.config.model = ModelRef(
                connection_id=spec.cleanup_model.connection_id, model_id=spec.cleanup_model.model_id
            )
    nodes: dict[str, NodeState] = {}
    for node in graph.nodes:
        nodes[node.id] = NodeState(
            state="skipped" if node.disabled else "pending",
            attempt=0,
            port=None,
            output=None,
            error=None,
            started_at=None,
            finished_at=None,
        )
    nodes["n_start"] = NodeState(
        state="complete",
        attempt=0,
        port="out",
        output={"brief": spec.brief}
        if spec.template == "brief_images"
        else {"recording": spec.attachment_id},
        error=None,
        started_at=None,
        finished_at=None,
    )
    mapping = {
        "prompt": "n_draft",
        "transcribe": "n_transcript",
        "cleanup": "n_clean",
        "pack": "n_pack",
        "image": "n_images",
    }
    for step in run.steps:
        key = mapping[step.kind]
        if step.kind == "image" and nodes[key].state not in {"pending", "complete"}:
            continue
        nodes[key] = NodeState(
            state=cast(Any, step.state),
            attempt=step.attempt,
            port="out" if step.state == "complete" else None,
            output=step.output,
            error=step.error,
            started_at=None,
            finished_at=None,
        )
        if step.kind == "cleanup" and (step.output or {}).get("skipped"):
            nodes[key].state = "skipped"
            nodes[key].port = None
            nodes[key].output = {"text": "", "skipped": True}
            nodes[key].warnings = ["User chose the original transcript."]
    if spec.template == "brief_images":
        images = [
            s.output for s in run.steps if s.kind == "image" and s.state == "complete" and s.output
        ]
        nodes["n_images"].output = {
            "images": [{"id": i["image_job_id"], "sha256": i.get("sha256")} for i in images],
            "prompt": run.edited_prompt or str((run.steps[0].output or {}).get("text", "")),
        }
        if spec.review_prompt:
            nodes["n_review"] = NodeState(
                state="complete"
                if run.edited_prompt
                else "paused"
                if run.state == "paused"
                else "pending",
                attempt=0,
                port="approved" if run.edited_prompt else None,
                output={
                    "value": run.edited_prompt or str((run.steps[0].output or {}).get("text", ""))
                },
                error=None,
                started_at=None,
                finished_at=None,
            )
        elif run.state == "paused":
            nodes["n_images"].state = "paused"
    else:
        row = await manager.store.one("SELECT source_json FROM workflow_runs WHERE id=?", (run.id,))
        if row and row["source_json"]:
            source = json.loads(row["source_json"])
            nodes["n_transcript"].output = {
                "text": source["text"],
                "timestamped_text": timestamped(source["text"], source["segments"]),
                "transcript": source,
                "segments": source["segments"],
                "filename": source["filename"],
            }
            if spec.cleanup_model and source.get("cleaned_text"):
                nodes["n_clean"].output = {"text": source["cleaned_text"]}
    results: list[ResultSection] = []
    if run.state == "complete":
        nodes["n_save"].state = "complete"
        nodes["n_save"].port = "out"
        image_output = (nodes["n_images"].output or {}) if spec.template == "brief_images" else {}
        items = (
            [
                {"label": "Prompt", "type": "text", "value": image_output["prompt"]},
                {
                    "label": "Images",
                    "type": "image_list",
                    "value": image_output["images"],
                },
            ]
            if spec.template == "brief_images"
            else [
                {
                    "label": "Meeting pack",
                    "type": "text",
                    "value": (nodes["n_pack"].output or {}).get("text", ""),
                }
            ]
        )
        nodes["n_save"].output = {
            "items": items,
            "formats": ["md", "json"],
            "include_sources": run.source_available,
        }
        results = [
            ResultSection.model_validate(
                {"node_id": "n_save", "label": "Save results", "items": items}
            )
        ]
    return RunV2(
        id=run.id,
        kind="template",
        def_id=None,
        def_name="Brief to images"
        if spec.template == "brief_images"
        else "Recording to meeting pack",
        graph_hash=None,
        state=cast(Any, run.state),
        stage=run.stage,
        error=run.error,
        created_at=run.created_at,
        updated_at=run.updated_at,
        inputs=nodes["n_start"].output or {},
        graph=graph,
        nodes=nodes,
        results=results,
        source_available=run.source_available,
    )


async def detail(manager: GraphRunner, identifier: str) -> RunV2:
    row = await manager.store.one("SELECT id FROM workflow_graph_runs WHERE id=?", (identifier,))
    return (
        await manager.get(identifier)
        if row
        else await legacy_view(manager, await manager.legacy.get(identifier))
    )


async def page(
    manager: GraphRunner,
    def_id: str | None = None,
    state: str | None = None,
    cursor: str | None = None,
    limit: int = 50,
) -> RunPage:
    before_time, before_id = "9999", "~"
    if cursor:
        try:
            decoded = json.loads(base64.urlsafe_b64decode(cursor.encode()))
            before_time, before_id = decoded["time"], decoded["id"]
            if not isinstance(before_time, str) or not isinstance(before_id, str):
                raise ValueError("cursor")
        except (ValueError, KeyError, TypeError):
            raise AppError("workflow_cursor", "This run-list cursor is invalid.", 422) from None
    rows = await manager.store.rows(
        (
            "SELECT id,created_at FROM workflow_graph_runs WHERE (? IS NULL OR"
            " def_id=?) AND (? IS NULL OR state=?) AND (created_at<? OR (creat"
            "ed_at=? AND id<?)) ORDER BY created_at DESC,id DESC LIMIT ?"
        ),
        (def_id, def_id, state, state, before_time, before_time, before_id, limit + 1),
    )
    if def_id is None:
        rows += await manager.store.rows(
            (
                "SELECT id,created_at FROM workflow_runs WHERE (? IS NULL OR state"
                "=?) AND (created_at<? OR (created_at=? AND id<?)) ORDER BY create"
                "d_at DESC,id DESC LIMIT ?"
            ),
            (state, state, before_time, before_time, before_id, limit + 1),
        )
    rows.sort(key=lambda r: (r["created_at"], r["id"]), reverse=True)
    selected = rows[:limit]
    next_cursor = (
        base64.urlsafe_b64encode(
            canonical({"time": selected[-1]["created_at"], "id": selected[-1]["id"]}).encode()
        ).decode()
        if len(rows) > limit
        else None
    )
    return RunPage(
        items=[await detail(manager, row["id"]) for row in selected], next_cursor=next_cursor
    )


async def stream(manager: GraphRunner, cursor: str) -> AsyncGenerator[dict[str, str], None]:
    """Two durable journals use a composite cursor; ephemeral events have no ID."""
    try:
        legacy_after, graph_after = [max(0, int(value)) for value in cursor.split(":")]
    except ValueError:
        legacy_after = graph_after = 0
    queue: asyncio.Queue[tuple[str, Any]] = asyncio.Queue(100)
    live: asyncio.Queue[tuple[str, dict[str, Any]]] = asyncio.Queue(100)
    manager.listeners.add(live)
    legacy_max = await manager.store.one("SELECT COALESCE(MAX(id),0) n FROM workflow_events")
    graph_max = await manager.store.one("SELECT COALESCE(MAX(id),0) n FROM workflow_graph_events")
    legacy_latest, graph_latest = int(legacy_max["n"]), int(graph_max["n"])  # type: ignore[index]
    # A malformed/future cursor starts with a complete snapshot.
    if legacy_after > legacy_latest or graph_after > graph_latest:
        legacy_after = graph_after = 0
    replay = bool(legacy_after or graph_after)
    if not replay:
        legacy_after, graph_after = legacy_latest, graph_latest

    async def legacy_events() -> None:
        after = legacy_after
        while True:
            async with manager.legacy.changed:
                records = await manager.store.rows(
                    "SELECT id,data_json FROM workflow_events WHERE id>? ORDER BY id LIMIT 100",
                    (after,),
                )
                while not records:
                    await manager.legacy.changed.wait()
                    records = await manager.store.rows(
                        "SELECT id,data_json FROM workflow_events WHERE id>? ORDER BY id LIMIT 100",
                        (after,),
                    )
            for record in records:
                after = record["id"]
                run = WorkflowRun.model_validate_json(record["data_json"])
                await queue.put(("legacy", (after, await legacy_view(manager, run))))

    async def graph_events() -> None:
        async for sequence, run in manager.tail(graph_after):
            await queue.put(("graph", (sequence, run)))

    async def ephemeral_events() -> None:
        while True:
            await queue.put(("ephemeral", await live.get()))

    tasks = [asyncio.create_task(fn()) for fn in [legacy_events, graph_events, ephemeral_events]]
    try:
        yield {
            "id": f"{legacy_after}:{graph_after}",
            "event": "run.snapshot",
            "data": (await page(manager)).model_dump_json(by_alias=True),
        }
        while True:
            kind, value = await queue.get()
            if kind == "ephemeral":
                event, data = value
                yield {"event": event, "data": canonical(data)}
            else:
                sequence, run = value
                if kind == "legacy":
                    legacy_after = sequence
                else:
                    graph_after = sequence
                yield {
                    "id": f"{legacy_after}:{graph_after}",
                    "event": "run.updated",
                    "data": canonical({"run": run.model_dump(by_alias=True)}),
                }
    finally:
        manager.listeners.discard(live)
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
