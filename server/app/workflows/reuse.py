"""Conservative cross-run reuse: configuration, input, model and source identity."""

import json
import math
from typing import TYPE_CHECKING, Any

from ..errors import AppError
from .graph import CleanNode, GenerateNode, GraphDoc, ImageNode, Node, StartNode, ancestors, digest
from .graph_schemas import ReusePlan

if TYPE_CHECKING:
    from .engine import GraphRunner


def descendants(doc: GraphDoc, node_id: str) -> set[str]:
    return {n.id for n in doc.nodes if node_id in ancestors(doc, n.id)}


async def guard(manager: "GraphRunner", doc: GraphDoc, node: Node, inputs: dict[str, Any]) -> str:
    from .blocks import model_ref

    config = node.config.model_dump(by_alias=True)
    model = None
    if not node.disabled and isinstance(node, (GenerateNode, CleanNode)):
        selected = model_ref(doc, node.config.model)
        reported = await manager.legacy.runs.registry.resolve(
            selected.connection_id, selected.model_id
        )
        model = {
            "selected": selected.model_dump(),
            "context": reported.context_length,
            "metadata": {
                key: getattr(reported, key)
                for key in ["family", "params", "quant", "size_bytes", "context_max"]
            },
            "params": await manager.legacy.runs.registry.params(
                reported,
                node.config.params.model_dump(exclude_none=True)
                if isinstance(node, GenerateNode)
                else {},
            ),
            "connection": await manager.store.one(
                "SELECT base_url,kind FROM connections WHERE id=?", (selected.connection_id,)
            ),
        }
    sources = {}
    start = next(n for n in doc.nodes if isinstance(n, StartNode))
    for field in start.config.fields:
        if field.type not in {"recording", "document", "image"} or not inputs.get(field.name):
            continue
        identifier = inputs[field.name]
        item = await manager.store.one("SELECT * FROM attachments WHERE id=?", (identifier,))
        if not item:
            raise AppError(
                "workflow_reuse", "A source file is no longer available. Run with new inputs.", 409
            )
        # Audio files are temporary: durable originals below prove their identity.
        # Media uploads themselves are immutable through the existing attachment API.
        sources[field.name] = {k: item.get(k) for k in ("id", "kind", "filename", "mime_type")}
        if field.type != "recording":
            sources[field.name].update({k: item.get(k) for k in ("bytes", "path")})
    engine = (
        manager.legacy.images.engine.status().model_dump() if isinstance(node, ImageNode) else None
    )
    if engine:
        engine = {
            k: engine[k]
            for k in ("model", "model_revision", "quantization", "width", "height", "steps")
            if k in engine
        }
    incoming = sorted(
        (e.source, e.source_port, e.target_port) for e in doc.edges if e.target == node.id
    )
    return digest(
        {
            "kind": node.kind,
            "key": node.key,
            "disabled": node.disabled,
            "config": config,
            "incoming": incoming,
            "inputs": inputs,
            "model": model,
            "sources": sources,
            "image_engine": engine,
        }
    )


async def plan(
    manager: "GraphRunner",
    def_id: str,
    node_id: str,
    source_id: str | None = None,
    mode: str = "run",
    inputs: dict[str, Any] | None = None,
) -> ReusePlan:
    definition = await manager.defs.get(def_id)
    doc = definition.graph
    target = next((n for n in doc.nodes if n.id == node_id and not n.disabled), None)
    if not target or isinstance(target, StartNode):
        return ReusePlan(eligible=False, reason="Choose an enabled block after Start.")
    row = await manager.store.one(
        "SELECT id FROM workflow_graph_runs WHERE def_id=? AND mode='run' "
        "AND state IN ('complete','failed','interrupted','cancelled') "
        "AND (? IS NULL OR id=?) ORDER BY created_at DESC,id DESC LIMIT 1",
        (def_id, source_id, source_id),
    )
    if not row:
        return ReusePlan(eligible=False, reason="Run the workflow once first.")
    previous = await manager.get(row["id"])
    selected = (
        ancestors(doc, node_id)
        if mode == "test"
        else {n.id for n in doc.nodes} - descendants(doc, node_id) - {node_id}
    )
    checked = previous.inputs if inputs is None else inputs
    if checked != previous.inputs:
        return ReusePlan(eligible=False, reason="The inputs changed since the last run.")
    for source in await manager.store.rows(
        "SELECT * FROM workflow_graph_sources WHERE run_id=?", (previous.id,)
    ):
        if source["node_id"] not in selected:
            continue
        original = json.loads(source["source_json"])
        live = await manager.store.one(
            "SELECT text,raw_text,segments_json FROM transcripts WHERE attachment_id=?",
            (original["attachment_id"],),
        )
        if (
            not live
            or live["text"] != original["text"]
            or live["raw_text"] != original["raw_text"]
            or json.loads(live["segments_json"] or "[]") != original["segments"]
        ):
            return ReusePlan(
                eligible=False, reason="An original source changed. Run with current inputs."
            )
    for identifier in selected:
        node = next(n for n in doc.nodes if n.id == identifier)
        state = previous.nodes.get(identifier)
        saved = await manager.store.one(
            "SELECT guard_json FROM workflow_graph_steps WHERE run_id=? AND node_id=?",
            (previous.id, identifier),
        )
        if (
            not state
            or state.state not in {"complete", "skipped"}
            or not saved
            or not saved["guard_json"]
        ):
            return ReusePlan(eligible=False, reason="An earlier block has no reusable result.")
        try:
            matched = json.loads(saved["guard_json"]) == await guard(manager, doc, node, checked)
        except AppError:
            matched = False
        if not matched:
            return ReusePlan(
                eligible=False,
                reason="Earlier settings, inputs or sources changed. Run the workflow again.",
            )
        # Removed image outputs cannot silently become reused media.
        for image in (state.output or {}).get("images", []):
            job = await manager.legacy.images.get(image["id"])
            if job.state != "complete" or job.sha256 != image.get("sha256"):
                return ReusePlan(
                    eligible=False, reason="An earlier image was removed. Run the workflow again."
                )
    return ReusePlan(eligible=True, source_run_id=previous.id, node_ids=sorted(selected))


def rebind(value: Any, old_id: str, new_id: str) -> Any:
    """Rebind only typed source references, never user text or arbitrary strings."""
    if isinstance(value, dict):
        copied = {k: rebind(v, old_id, new_id) for k, v in value.items()}
        if value.get("run_id") == old_id and set(value) == {
            "run_id",
            "node_id",
            "source_sha256",
            "attachment_id",
        }:
            copied["run_id"] = new_id
        return copied
    if isinstance(value, list):
        return [rebind(v, old_id, new_id) for v in value]
    return value


def sample_outputs(
    doc: GraphDoc, node_id: str, samples: dict[str, Any]
) -> dict[str, dict[str, Any]]:
    from .graph import outputs
    from .templating import references

    node = next(n for n in doc.nodes if n.id == node_id)
    from .graph import OutputNode, PickNode, ReviewNode, TranscribeNode

    values_to_fill = (
        [node.config.instructions, node.config.prompt]
        if isinstance(node, GenerateNode)
        else [node.config.prompt]
        if isinstance(node, ImageNode)
        else [node.config.show]
        if isinstance(node, ReviewNode)
        else node.config.from_
        if isinstance(node, PickNode)
        else [node.config.recording]
        if isinstance(node, TranscribeNode)
        else [node.config.transcript]
        if isinstance(node, CleanNode)
        else [item.ref for item in node.config.include]
        if isinstance(node, OutputNode)
        else []
    )
    refs = [ref for text in values_to_fill for ref in references(text)]
    expected = {f"{ref.key}.{ref.field}": ref for ref in refs}
    if set(samples) != set(expected):
        raise AppError("workflow_sample", "Provide a sample for each referenced value.", 422)
    values: dict[str, dict[str, Any]] = {}
    for name, ref in expected.items():
        upstream = next(n for n in doc.nodes if n.key == ref.key)
        kind, value = outputs(upstream)[ref.field], samples[name]
        valid = (
            isinstance(value, str) and len(value) <= 20000
            if kind in {"text", "string", "short_text", "long_text", "choice"}
            else isinstance(value, bool)
            if kind == "boolean"
            else isinstance(value, (int, float)) and not isinstance(value, bool)
            if kind == "number"
            else False
        )
        if kind == "number" and valid:
            valid = math.isfinite(value)
        if not valid:
            raise AppError(
                "workflow_sample",
                (
                    "Use a saved run for file, transcript or image inputs; text"
                    " samples must match their type."
                ),
                422,
            )
        values.setdefault(upstream.id, {})[ref.field] = value
    return values
