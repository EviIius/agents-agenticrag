"""Initial block performers, composed from the existing native job managers."""

import asyncio
import json
import math
from ipaddress import ip_address
from typing import TYPE_CHECKING, Any
from urllib.parse import urlsplit

from ..db import attachments
from ..errors import AppError
from ..schemas import ImageCreate, ImageJob
from .graph import (
    CleanNode,
    GenerateNode,
    GraphDoc,
    ImageNode,
    ModelChoice,
    ModelRef,
    Node,
    OutputNode,
    ReviewNode,
    StartNode,
    TranscribeNode,
    ancestors,
    canonical,
    digest,
    outputs,
)
from .graph_schemas import RunV2
from .schemas import WorkflowCreate, WorkflowModel, WorkflowRun, WorkflowStep
from .source import timestamped
from .templating import exact_reference, render, resolve
from .text import write_text

if TYPE_CHECKING:
    from .engine import GraphRunner


def model_ref(doc: GraphDoc, choice: ModelChoice) -> ModelRef:
    value = doc.settings.default_model if choice == "workflow_default" else choice
    if value is None:
        raise AppError(
            "workflow_model", "Choose a workflow default model or a model for this block.", 422
        )
    return value


async def check_models(manager: "GraphRunner", doc: GraphDoc) -> None:
    private: set[str] = set()
    for node in doc.nodes:
        if (
            isinstance(node, (TranscribeNode, CleanNode))
            or isinstance(node, StartNode)
            and any(f.type in {"recording", "document", "image"} for f in node.config.fields)
        ):
            private.add(node.id)
    for node in doc.nodes:
        if node.disabled:
            continue
        if isinstance(node, ImageNode) and not manager.legacy.images.engine.status().available:
            raise AppError(
                "image_unavailable", "The image engine is not ready. Settings → Images.", 409
            )
        if isinstance(node, (GenerateNode, CleanNode)):
            selected = model_ref(doc, node.config.model)
            model = await manager.legacy.runs.registry.resolve(
                selected.connection_id, selected.model_id
            )
            if isinstance(node, GenerateNode) and node.config.params.reasoning is not None:
                if (
                    not model.reasoning
                    or node.config.params.reasoning not in model.reasoning.options
                ):
                    raise AppError(
                        "workflow_reasoning",
                        "Choose a thinking option reported by this model.",
                        422,
                    )
            if private & (ancestors(doc, node.id) | {node.id}):
                row = await manager.store.one(
                    "SELECT base_url FROM connections WHERE id=?", (selected.connection_id,)
                )
                host = urlsplit(str(row["base_url"])).hostname if row else None
                local = host == "localhost"
                try:
                    local = local or bool(host and ip_address(host).is_loopback)
                except ValueError:
                    pass
                if not local:
                    raise AppError(
                        "recording_requires_local",
                        "Private-source workflows need a local Ollama connection.",
                        422,
                    )


async def checked_inputs(
    manager: "GraphRunner", doc: GraphDoc, supplied: dict[str, Any]
) -> dict[str, Any]:
    start = next(n for n in doc.nodes if isinstance(n, StartNode))
    if set(supplied) - {f.name for f in start.config.fields}:
        raise AppError("workflow_inputs", "An input does not belong to this workflow.", 422)
    values: dict[str, Any] = {}
    for field in start.config.fields:
        value = supplied.get(field.name, field.default)
        if value is None or value == "":
            if field.required:
                raise AppError("workflow_inputs", "A required Start input is missing.", 422)
            values[field.name] = ""
            continue
        valid = True
        if field.type in {"short_text", "long_text", "choice", "recording", "document", "image"}:
            valid = isinstance(value, str) and len(value) <= (
                500 if field.type == "short_text" else 20000
            )
        elif field.type == "boolean":
            valid = isinstance(value, bool)
        elif field.type == "number":
            valid = isinstance(value, (int, float)) and not isinstance(value, bool)
            if valid:
                import math

                valid = math.isfinite(value)
        if field.type == "choice":
            valid = valid and value in field.choices
        if not valid:
            raise AppError("workflow_inputs", "A Start input has the wrong type or size.", 422)
        if field.type in {"recording", "document", "image"}:
            item = await attachments.attachment(manager.store, value)
            expected = "audio" if field.type == "recording" else field.type
            if item.kind != expected:
                raise AppError(
                    "workflow_inputs", "Choose the file type requested by this input.", 422
                )
        values[field.name] = value
    return values


class GraphTextHost:
    """Adapt shared text persistence to graph attempts without altering requests."""

    def __init__(
        self, manager: "GraphRunner", run: RunV2, node: GenerateNode, warnings: list[str]
    ) -> None:
        self.manager, self.node, self.run, self.warnings = manager, node, run, warnings
        self.store, self.runs = manager.store, manager.legacy.runs
        self.pending = ""
        self.last = 0.0

    async def state(
        self, identifier: str, state: str, stage: str, error: str | None = None
    ) -> None:
        await self.manager.state(identifier, state, stage, error)

    async def save_step(
        self,
        identifier: str,
        step: WorkflowStep,
        state: str,
        output: dict[str, Any] | None = None,
        error: str | None = None,
    ) -> None:
        await self.manager.save(
            identifier, self.node.id, state, output, error, warnings=self.warnings
        )

    async def record_text_request(
        self, run: WorkflowRun, step: WorkflowStep, body: dict[str, Any]
    ) -> None:
        row = await self.store.one(
            (
                "SELECT input_json FROM workflow_graph_attempts WHERE run_id=? AND"
                " node_id=? AND attempt=?"
            ),
            (run.id, self.node.id, step.attempt),
        )
        previous = json.loads(row["input_json"]) if row else {}
        previous["request"] = body
        previous["request_sha256"] = digest(body)
        await self.store.execute(
            (
                "UPDATE workflow_graph_attempts SET input_json=? WHERE run_id=? AN"
                "D node_id=? AND attempt=?"
            ),
            (canonical(previous), run.id, self.node.id, step.attempt),
        )

    async def text_delta(self, identifier: str, step: WorkflowStep, text: str) -> None:
        self.pending += text
        clock = asyncio.get_running_loop().time()
        if clock - self.last >= 0.1:
            await self.flush()
            self.last = clock

    async def flush(self) -> None:
        if self.pending:
            await self.manager.ephemeral(
                "node.text", {"run_id": self.run.id, "node_id": self.node.id, "delta": self.pending}
            )
            self.pending = ""


def image_key(run_id: str, node_id: str, index: int, attempt: int) -> str:
    return f"workflow-{run_id}-{digest(node_id)[:16]}-{index}-{attempt}"


async def progress_job(manager: "GraphRunner", run_id: str, node_id: str, job: Any) -> None:
    last = 0.0
    async for _, event in job.tail(0):
        if event.type.endswith(".progress"):
            clock = asyncio.get_running_loop().time()
            if clock - last >= 0.1:
                await manager.ephemeral(
                    "node.progress",
                    {
                        "run_id": run_id,
                        "node_id": node_id,
                        "done": event.data.get("done", 0),
                        "total": event.data.get("total", 0),
                        "label": "Processing recording",
                    },
                )
                last = clock


async def wait_job(manager: "GraphRunner", run: RunV2, node: Node, job: Any) -> None:
    watcher = asyncio.create_task(progress_job(manager, run.id, node.id, job))
    try:
        if job.task:
            await asyncio.shield(job.task)
    finally:
        watcher.cancel()
        await asyncio.gather(watcher, return_exceptions=True)


async def perform(manager: "GraphRunner", run: RunV2, node: Node) -> None:
    warnings: list[str] = []
    values = {n.key: run.nodes[n.id].output or {} for n in run.graph.nodes}
    skipped = {n.key for n in run.graph.nodes if run.nodes[n.id].state == "skipped"}

    def text(value: str, required: bool = False) -> str:
        return render(value, values, skipped, warnings, required)

    def typed(value: str) -> Any:
        return resolve(exact_reference(value), values, skipped, warnings)

    output: dict[str, Any]
    if isinstance(node, StartNode):
        output = run.inputs
    elif isinstance(node, GenerateNode):
        chosen = model_ref(run.graph, node.config.model)
        legacy_input = WorkflowCreate(
            request_key="graph-text-bridge",
            template="brief_images",
            brief="Graph text invocation",
            model=WorkflowModel(
                connection_id=chosen.connection_id,
                model_id=chosen.model_id,
                params=node.config.params,
            ),
        )
        bridge_run = WorkflowRun(
            id=run.id,
            version=1,
            input=legacy_input,
            state=run.state,
            stage=run.stage,
            steps=[],
            source_available=run.source_available,
            created_at=run.created_at,
            updated_at=run.updated_at,
        )
        bridge_step = WorkflowStep(
            position=0,
            kind="prompt",
            label=node.title,
            state="running",
            attempt=run.nodes[node.id].attempt,
        )
        host = GraphTextHost(manager, run, node, warnings)
        schema: dict[str, Any] | None = None
        if node.config.format == "json":
            schema = {
                "type": "object",
                "properties": {
                    field.name: {"type": field.type, "description": field.description}
                    for field in node.config.json_fields
                },
                "required": [field.name for field in node.config.json_fields],
                "additionalProperties": False,
            }
        try:
            output = await write_text(
                host,
                bridge_run,
                bridge_step,
                text(node.config.instructions),
                text(node.config.prompt, True),
                json_schema=schema,
            )
        finally:
            await host.flush()
        if schema is not None:
            try:
                parsed = json.loads(output["text"])
                if not isinstance(parsed, dict) or set(parsed) != set(schema["required"]):
                    raise ValueError("fields")
                for json_field in node.config.json_fields:
                    value = parsed[json_field.name]
                    valid = (
                        isinstance(value, str)
                        if json_field.type == "string"
                        else isinstance(value, bool)
                        if json_field.type == "boolean"
                        else isinstance(value, (int, float)) and not isinstance(value, bool)
                    )
                    if json_field.type == "number" and valid:
                        valid = math.isfinite(value)
                    if not valid:
                        raise ValueError("type")
                output.update(parsed)
            except (ValueError, TypeError):
                raise AppError(
                    "workflow_json",
                    "The model did not return the requested JSON fields. Retry this block.",
                    409,
                ) from None
    elif isinstance(node, TranscribeNode):
        identifier = typed(node.config.recording)
        if not isinstance(identifier, str) or not identifier:
            raise AppError("workflow_inputs", "Choose a recording for this block.", 422)
        item = await attachments.attachment(manager.store, identifier)
        if item.kind != "audio":
            raise AppError("workflow_inputs", "Choose a recording for this block.", 422)
        if not item.transcript or item.transcript.status != "ready":
            job = manager.legacy.transcription.jobs.get(identifier)
            if job is None or job.closed:
                await manager.legacy.transcription.start(identifier)
                job = manager.legacy.transcription.jobs[identifier]
            await wait_job(manager, run, node, job)
        source = await attachments.transcript(manager.store, identifier)
        if not source.attachment.transcript or source.attachment.transcript.status != "ready":
            raise AppError(
                "transcript_failed", "Transcription did not finish. Retry this block.", 409
            )
        original = {
            "attachment_id": identifier,
            "filename": item.filename,
            "text": source.text,
            "raw_text": source.raw_text,
            "segments": [s.model_dump() for s in source.segments],
            "cleaned_text": None,
        }
        await manager.store.execute(
            (
                "INSERT OR IGNORE INTO workflow_graph_sources(run_id,node_id,sourc"
                "e_json,sha256) VALUES(?,?,?,?)"
            ),
            (run.id, node.id, canonical(original), digest(original)),
        )
        saved = await manager.store.one(
            "SELECT source_json FROM workflow_graph_sources WHERE run_id=? AND node_id=?",
            (run.id, node.id),
        )
        assert saved
        original = json.loads(saved["source_json"])
        output = {
            "transcript": {
                "run_id": run.id,
                "node_id": node.id,
                "attachment_id": original["attachment_id"],
                "source_sha256": digest(original),
            },
            "text": original["text"],
            "timestamped_text": timestamped(original["text"], original["segments"]),
            "segments": original["segments"],
            "filename": original["filename"],
        }
    elif isinstance(node, CleanNode):
        reference = typed(node.config.transcript)
        if not isinstance(reference, dict) or reference.get("run_id") != run.id:
            raise AppError("workflow_source", "Choose an original transcript from this run.", 422)
        row = await manager.store.one(
            "SELECT source_json,sha256 FROM workflow_graph_sources WHERE run_id=? AND node_id=?",
            (run.id, reference.get("node_id")),
        )
        if not row or row["sha256"] != reference.get("source_sha256"):
            raise AppError(
                "workflow_source", "The original transcript reference does not match.", 422
            )
        original = json.loads(row["source_json"])
        identifier = original["attachment_id"]
        live = await attachments.transcript(manager.store, identifier)
        if live.text != original["text"]:
            raise AppError(
                "workflow_source_changed",
                "The transcript changed. Continue with the saved original.",
                409,
            )
        chosen = model_ref(run.graph, node.config.model)
        acceptance = asyncio.create_task(
            manager.legacy.cleanup.start(identifier, chosen.connection_id, chosen.model_id)
        )
        try:
            await asyncio.shield(acceptance)
        except asyncio.CancelledError:
            outcome = await asyncio.gather(acceptance, return_exceptions=True)
            if not isinstance(outcome[0], BaseException):
                manager.owned_cleanup[run.id] = manager.legacy.transcription.jobs[identifier]
            raise
        job = manager.legacy.transcription.jobs[identifier]
        manager.owned_cleanup[run.id] = job
        await wait_job(manager, run, node, job)
        value = await attachments.transcript(manager.store, identifier)
        if value.text != original["text"] or value.cleaned_text is None:
            raise AppError(
                "cleanup_failed",
                "Clean-up was rejected or the source changed. Retry or continue with the original.",
                409,
            )
        output = {"text": value.cleaned_text, "source": reference}
    elif isinstance(node, ReviewNode):
        await manager.save(
            run.id, node.id, "paused", {"value": text(node.config.show, True)}, warnings=warnings
        )
        return
    elif isinstance(node, ImageNode):
        output = await create_images(manager, run, node, text(node.config.prompt, True), warnings)
        if output.get("paused"):
            return
    else:
        assert isinstance(node, OutputNode)
        items: list[dict[str, Any]] = []
        for included in node.config.include:
            ref = exact_reference(included.ref)
            upstream = next(n for n in run.graph.nodes if n.key == ref.key)
            value = typed(included.ref)
            items.append(
                {"label": included.label, "type": outputs(upstream)[ref.field], "value": value}
            )
        if not node.config.include:
            for upstream in run.graph.nodes:
                if (
                    upstream.id in ancestors(run.graph, node.id)
                    and run.nodes[upstream.id].state == "complete"
                    and not any(
                        e.source == upstream.id and e.target != node.id for e in run.graph.edges
                    )
                ):
                    for field, kind in outputs(upstream).items():
                        if field in {"text", "value", "images"}:
                            items.append(
                                {
                                    "label": upstream.title,
                                    "type": kind,
                                    "value": values[upstream.key].get(field),
                                }
                            )
        output = {
            "items": items,
            "formats": node.config.formats,
            "include_sources": node.config.include_sources,
        }
    await manager.save(run.id, node.id, "complete", output, port="out", warnings=warnings)


async def create_images(
    manager: "GraphRunner", run: RunV2, node: ImageNode, prompt: str, warnings: list[str]
) -> dict[str, Any]:
    previous = run.nodes[node.id].output or {}
    prompt = previous.get("prompt", prompt)
    if len(prompt) > 4000:
        await manager.save(
            run.id, node.id, "paused", {"prompt": prompt, "paused": True}, warnings=warnings
        )
        return {"paused": True}
    images = list(previous.get("images", []))
    assert isinstance(node.config.seeds, list)
    image: ImageJob | None
    for index, seed in enumerate(node.config.seeds):
        if index < len(images):
            image = await manager.legacy.images.get(images[index]["id"])
            if image.state == "complete" and image.sha256:
                continue
        prefix = image_key(run.id, node.id, index, 0).rsplit("-", 1)[0] + "-%"
        rows = await manager.store.rows(
            "SELECT id FROM image_jobs WHERE request_key LIKE ? ORDER BY created_at DESC,id DESC",
            (prefix,),
        )
        image = None
        for row in rows:
            candidate = await manager.legacy.images.get(row["id"])
            if (
                candidate.state == "complete"
                and candidate.sha256
                or candidate.state in {"queued", "preparing", "running", "cancelling"}
            ):
                image = candidate
                break
        if image is None:
            image = await manager.legacy.images.submit(
                ImageCreate(
                    request_key=image_key(run.id, node.id, index, run.nodes[node.id].attempt),
                    prompt=prompt,
                    seed=seed,
                    parent_id=None,
                )
            )
        manager.owned_images[run.id] = image.id
        partial = {"images": images, "prompt": prompt, "active_image_id": image.id}
        await manager.save(run.id, node.id, "running", partial, warnings=warnings)
        watcher = asyncio.create_task(image_progress(manager, run.id, node.id, image.id))
        try:
            task = manager.legacy.images.tasks.get(image.id)
            if task:
                await asyncio.shield(task)
        finally:
            watcher.cancel()
            await asyncio.gather(watcher, return_exceptions=True)
        image = await manager.legacy.images.get(image.id)
        if image.state != "complete" or not image.sha256:
            raise AppError(
                "workflow_image",
                image.error or "Image generation did not finish. Retry this block.",
                409,
            )
        manager.owned_images.pop(run.id, None)
        images.append({"id": image.id, "sha256": image.sha256, "seed": image.seed})
        await manager.save(
            run.id, node.id, "running", {"images": images, "prompt": prompt}, warnings=warnings
        )
    return {"images": images, "prompt": prompt}


async def image_progress(manager: "GraphRunner", run_id: str, node_id: str, image_id: str) -> None:
    last = 0.0
    async for _, kind, data in manager.legacy.images.tail(0):
        if (
            kind != "image.updated"
            or not isinstance(data, dict)
            or data.get("job", {}).get("id") != image_id
        ):
            continue
        clock = asyncio.get_running_loop().time()
        if clock - last >= 0.1:
            job = data["job"]
            await manager.ephemeral(
                "node.progress",
                {
                    "run_id": run_id,
                    "node_id": node_id,
                    "done": job["completed_steps"],
                    "total": job["steps"],
                    "label": job["stage"],
                },
            )
            last = clock


async def reconcile_images(manager: "GraphRunner", run: RunV2) -> None:
    for node in run.graph.nodes:
        if isinstance(node, ImageNode) and run.nodes[node.id].state == "interrupted":
            # Execution performs the same keyed lookup, never submits before checking.
            await manager.save(
                run.id,
                node.id,
                "pending",
                run.nodes[node.id].output,
                warnings=run.nodes[node.id].warnings,
            )
