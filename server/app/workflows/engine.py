"""Durable sequential graph execution; existing managers own every native call."""

import asyncio
import json
import secrets
from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

from ..db.core import Store
from ..errors import AppError
from .defs import Definitions
from .graph import (
    GenerateNode,
    GraphDoc,
    ImageNode,
    Node,
    StartNode,
    ancestors,
    canonical,
    digest,
    execution_hash,
    topo_order,
    validate,
)
from .graph_schemas import Decision, GraphResume, GraphSubmit, NodeState, ResultSection, RunV2
from .jobs import ACTIVE, Workflows, now

TERMINAL = {"complete", "skipped"}


class GraphRunner:
    def __init__(self, store: Store, legacy: Workflows) -> None:
        self.store, self.legacy = store, legacy
        self.defs = Definitions(store)
        self.lock = asyncio.Lock()
        self.changed = asyncio.Condition()
        self.streams_closed = asyncio.Condition()
        self.tasks: dict[str, asyncio.Task[None]] = {}
        self.owned_images: dict[str, str] = {}
        self.owned_cleanup: dict[str, Any] = {}
        self.listeners: set[asyncio.Queue[tuple[str, dict[str, Any]]]] = set()
        self.emission_locks: dict[str, asyncio.Lock] = {}
        self.last_emission: dict[str, float] = {}
        self.closing = False
        self.live: dict[str, dict[str, dict[str, Any]]] = {}

    async def get(self, identifier: str) -> RunV2:
        row = await self.store.one(
            (
                "SELECT r.*,s.graph_json FROM workflow_graph_runs r JOIN workflow_"
                "def_snapshots s ON s.id=r.snapshot_id WHERE r.id=?"
            ),
            (identifier,),
        )
        if not row:
            raise AppError("not_found", "This workflow run is not available.", 404)
        nodes: dict[str, NodeState] = {}
        results: list[ResultSection] = []
        graph = GraphDoc.model_validate_json(row["graph_json"])
        titles = {n.id: n.title for n in graph.nodes}
        for step in await self.store.rows(
            "SELECT * FROM workflow_graph_steps WHERE run_id=?", (identifier,)
        ):
            output = json.loads(step["output_json"]) if step["output_json"] else None
            if step["state"] == "running":
                live = self.live.get(identifier, {}).get(step["node_id"], {})
                if "text" in live:
                    output = {**(output or {}), "text": live["text"]}
            else:
                live = {}
            nodes[step["node_id"]] = NodeState(
                **{
                    k: step[k]
                    for k in ["state", "attempt", "port", "error", "started_at", "finished_at"]
                },
                output=output,
                reused_from=step["reused_from"],
                progress=live.get("progress"),
                warnings=json.loads(step["warnings_json"]),
            )
            if step["state"] == "complete" and output and "items" in output:
                results.append(
                    ResultSection(
                        node_id=step["node_id"],
                        label=titles[step["node_id"]],
                        items=output["items"],
                    )
                )
        sources = await self.store.one(
            "SELECT 1 FROM workflow_graph_sources WHERE run_id=? LIMIT 1", (identifier,)
        )
        return RunV2(
            **{
                k: row[k]
                for k in [
                    "id",
                    "def_id",
                    "def_name",
                    "graph_hash",
                    "snapshot_id",
                    "state",
                    "stage",
                    "error",
                    "created_at",
                    "updated_at",
                ]
            },
            kind="graph",
            mode=row["mode"],
            parent_run_id=row["parent_run_id"],
            inputs=json.loads(row["inputs_json"]),
            graph=graph,
            nodes=nodes,
            results=results,
            source_available=bool(sources),
        )

    async def emit(self, identifier: str) -> None:
        async with self.changed:
            value = await self.get(identifier)
            await self.store.execute(
                "INSERT INTO workflow_graph_events(run_id,data_json) VALUES(?,?)",
                (identifier, value.model_dump_json(by_alias=True)),
            )
            self.changed.notify_all()

    async def ephemeral(self, kind: str, data: dict[str, Any]) -> None:
        identifier = str(data["run_id"])
        node_id = str(data["node_id"])
        live = self.live.setdefault(identifier, {}).setdefault(node_id, {})
        if kind == "node.text" and "text" in data:
            live["text"] = data["text"]
        elif kind == "node.progress" and all(k in data for k in ["done", "total", "label"]):
            live["progress"] = {k: data[k] for k in ["done", "total", "label"]}
        if not self.listeners:
            return
        async with self.emission_locks.setdefault(identifier, asyncio.Lock()):
            clock = asyncio.get_running_loop()
            remaining = 0.1 - (clock.time() - self.last_emission.get(identifier, 0))
            if remaining > 0:
                await asyncio.sleep(remaining)
            self.last_emission[identifier] = clock.time()
            for queue in tuple(self.listeners):
                if not queue.full():
                    queue.put_nowait((kind, data))
                # Slow consumers reconnect to durable snapshots; never block native work.

    async def state(
        self, identifier: str, state: str, stage: str, error: str | None = None
    ) -> None:
        await self.store.execute(
            "UPDATE workflow_graph_runs SET state=?,stage=?,error=?,updated_at=? WHERE id=?",
            (state, stage, error, now(), identifier),
        )
        await self.emit(identifier)

    async def save(
        self,
        identifier: str,
        node_id: str,
        state: str,
        output: dict[str, Any] | None = None,
        error: str | None = None,
        port: str | None = None,
        warnings: list[str] | None = None,
    ) -> None:
        clock = now() if state in TERMINAL | {"failed", "cancelled", "interrupted"} else None
        encoded = canonical(output) if output is not None else None
        await self.store.batch(
            [
                (
                    (
                        "UPDATE workflow_graph_steps SET state=?,output_json=?,error=?,por"
                        "t=?,warnings_json=?,finished_at=? WHERE run_id=? AND node_id=?"
                    ),
                    (
                        state,
                        encoded,
                        error,
                        port,
                        canonical(warnings or []),
                        clock,
                        identifier,
                        node_id,
                    ),
                ),
                (
                    (
                        "UPDATE workflow_graph_attempts SET state=?,output_json=?,finished"
                        "_at=? WHERE run_id=? AND node_id=? AND attempt=(SELECT attempt FR"
                        "OM workflow_graph_steps WHERE run_id=? AND node_id=?)"
                    ),
                    (state, encoded, clock, identifier, node_id, identifier, node_id),
                ),
            ]
        )
        await self.emit(identifier)

    async def submit(self, def_id: str, body: GraphSubmit) -> RunV2:
        from .blocks import check_models, checked_inputs
        from .reuse import guard, plan, rebind, sample_outputs

        request = canonical({"def_id": def_id, **body.model_dump()})
        async with self.lock:
            existing = await self.store.one(
                "SELECT id,request_json FROM workflow_graph_runs WHERE request_key=?",
                (body.request_key,),
            )
            if existing:
                if existing["request_json"] != request:
                    raise AppError(
                        "workflow_conflict", "This request key belongs to different inputs.", 409
                    )
                return await self.get(existing["id"])
            if self.closing or len(self.tasks) >= 20:
                raise AppError(
                    "workflow_queue", "The workflow queue is full. Try again shortly.", 409
                )
            definition = await self.defs.get(def_id)
            if definition.archived_at:
                raise AppError(
                    "workflow_archived", "Duplicate this archived workflow to run it.", 409
                )
            doc = definition.graph.model_copy(deep=True)
            issues = [
                issue
                for issue in validate(doc)
                if issue.severity == "error"
                and (body.mode != "test" or issue.node_id is None or issue.node_id == body.node_id)
            ]
            if issues:
                raise AppError("workflow_invalid", issues[0].message, 422)
            if body.samples and (body.mode != "test" or body.source_run_id):
                raise AppError("workflow_test", "Choose saved outputs or samples, not both.", 422)
            previous = None
            reused: list[str] = []
            samples: dict[str, dict[str, Any]] = {}
            if body.node_id:
                if not any(n.id == body.node_id and not n.disabled for n in doc.nodes):
                    raise AppError("workflow_reuse", "Choose an enabled block.", 422)
                if body.mode == "test" and (body.samples or not body.source_run_id):
                    samples = sample_outputs(doc, body.node_id, body.samples)
                    inputs = body.inputs
                    # Samples are explicit user data; media cannot be fabricated here.
                    if any(
                        f.type in {"recording", "document", "image"}
                        for n in doc.nodes
                        if isinstance(n, StartNode)
                        for f in n.config.fields
                    ):
                        inputs = await checked_inputs(self, doc, body.inputs)
                else:
                    reuse = await plan(
                        self,
                        def_id,
                        body.node_id,
                        body.source_run_id,
                        body.mode,
                        body.inputs or None,
                    )
                    if not reuse.eligible or not reuse.source_run_id:
                        raise AppError("workflow_reuse", reuse.reason or "No reusable run.", 409)
                    previous = await self.get(reuse.source_run_id)
                    reused = reuse.node_ids
                    inputs = previous.inputs
            else:
                if body.mode == "test" or body.source_run_id or body.samples:
                    raise AppError("workflow_test", "Choose the block to test or rerun.", 422)
                inputs = await checked_inputs(self, doc, body.inputs)
            selected_ids = {body.node_id} if body.mode == "test" and body.node_id else None
            await check_models(self, doc, selected_ids)
            guards = {
                node.id: await guard(self, doc, node, inputs)
                for node in doc.nodes
                if selected_ids is None or node.id in selected_ids or node.id in reused
            }

            for node in doc.nodes:
                if isinstance(node, ImageNode) and previous and node.id in reused:
                    old_image = next(n for n in previous.graph.nodes if n.id == node.id)
                    assert isinstance(old_image, ImageNode)
                    node.config.seeds = old_image.config.seeds
                elif isinstance(node, ImageNode) and node.config.seeds == "auto":
                    node.config.seeds = [secrets.randbits(32) for _ in range(node.config.count)]
            identifier, snapshot_id, clock = uuid4().hex, uuid4().hex, now()
            hashed = execution_hash(doc)
            statements: list[tuple[str, tuple[object, ...]]] = [
                (
                    (
                        "INSERT INTO workflow_def_snapshots(id,def_id,graph_hash,graph_jso"
                        "n,created_at) VALUES(?,?,?,?,?)"
                    ),
                    (snapshot_id, def_id, hashed, canonical(doc.model_dump(by_alias=True)), clock),
                ),
                (
                    (
                        "INSERT INTO workflow_graph_runs(id,request_key,request_json,def_i"
                        "d,def_name,snapshot_id,graph_hash,inputs_json,state,stage,created"
                        "_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)"
                    ),
                    (
                        identifier,
                        body.request_key,
                        request,
                        def_id,
                        definition.name,
                        snapshot_id,
                        hashed,
                        canonical(inputs),
                        "queued",
                        "Waiting for a block",
                        clock,
                        clock,
                    ),
                ),
            ]
            expires = (
                (datetime.now(UTC) + timedelta(days=doc.settings.keep_test_runs_days)).isoformat()
                if body.mode == "test"
                else None
            )
            statements.append(
                (
                    "UPDATE workflow_graph_runs SET mode=?,parent_run_id=?,expires_at=? WHERE id=?",
                    (body.mode, previous.id if previous else None, expires, identifier),
                )
            )
            for node in doc.nodes:
                old = previous.nodes[node.id] if previous and node.id in reused else None
                state = (
                    old.state
                    if old
                    else "skipped"
                    if node.disabled or body.mode == "test" and node.id != body.node_id
                    else "pending"
                )
                output = rebind(old.output, previous.id, identifier) if old and previous else None
                if (
                    body.mode == "test"
                    and not previous
                    and body.node_id
                    and node.id in ancestors(doc, body.node_id)
                ):
                    state, output = "complete", samples.get(node.id, {})
                statements.append(
                    (
                        (
                            "INSERT INTO workflow_graph_steps(run_id,node_id,state,port,output_"
                            "json,reused_from,guard_json,warnings_json) VALUES(?,?,?,?,?,?,?,?)"
                        ),
                        (
                            identifier,
                            node.id,
                            state,
                            old.port if old else "out" if state == "complete" else None,
                            canonical(output) if output is not None else None,
                            previous.id
                            if old and previous
                            else "sample"
                            if node.id in samples
                            else None,
                            canonical(guards.get(node.id)),
                            canonical(old.warnings if old else []),
                        ),
                    )
                )
            if previous:
                for source in await self.store.rows(
                    "SELECT * FROM workflow_graph_sources WHERE run_id=?", (previous.id,)
                ):
                    if source["node_id"] in reused:
                        statements.append(
                            (
                                (
                                    "INSERT INTO workflow_graph_sources(run_id,"
                                    "node_id,source_json,sha256) VALUES(?,?,?,?)"
                                ),
                                (
                                    identifier,
                                    source["node_id"],
                                    source["source_json"],
                                    source["sha256"],
                                ),
                            )
                        )
            await self.store.batch(statements)
            await self.emit(identifier)
            self.schedule(identifier)
            return await self.get(identifier)

    def schedule(self, identifier: str) -> None:
        task = asyncio.create_task(self.execute(identifier), name="workflow-graph-" + identifier)
        self.tasks[identifier] = task

        def finished(completed: asyncio.Task[None]) -> None:
            if self.tasks.get(identifier) is completed:
                self.tasks.pop(identifier, None)

        task.add_done_callback(finished)

    async def execute(self, identifier: str) -> None:
        from .blocks import perform

        current: Node | None = None
        try:
            while True:
                run = await self.get(identifier)
                pending = [n for n in run.graph.nodes if run.nodes[n.id].state == "pending"]
                if not pending:
                    if all(n.state in TERMINAL for n in run.nodes.values()):
                        await self.state(identifier, "complete", "Ready for review")
                    return
                ready: list[Node] = []
                skipped = False
                for node in pending:
                    incoming = [e for e in run.graph.edges if e.target == node.id]
                    if isinstance(node, StartNode):
                        ready.append(node)
                    elif incoming and all(run.nodes[e.source].state in TERMINAL for e in incoming):
                        if any(
                            run.nodes[e.source].state == "complete"
                            and run.nodes[e.source].port == e.source_port
                            for e in incoming
                        ):
                            ready.append(node)
                        else:
                            await self.save(identifier, node.id, "skipped")
                            skipped = True
                if skipped:
                    continue
                if not ready:
                    return
                order = topo_order(run.graph)
                current = min(ready, key=lambda n: order.index(n.id))
                self.live.get(identifier, {}).pop(current.id, None)
                clock = now()
                attempt = run.nodes[current.id].attempt + 1
                lineage = {
                    n.key: {
                        "state": run.nodes[n.id].state,
                        "port": run.nodes[n.id].port,
                        "output": run.nodes[n.id].output,
                    }
                    for n in run.graph.nodes
                }
                await self.store.batch(
                    [
                        (
                            (
                                "UPDATE workflow_graph_steps SET state='running',attempt=?,started"
                                "_at=?,finished_at=NULL,error=NULL WHERE run_id=? AND node_id=?"
                            ),
                            (attempt, clock, identifier, current.id),
                        ),
                        (
                            (
                                "INSERT INTO workflow_graph_attempts(run_id,node_id,attempt,input_"
                                "json,state,started_at) VALUES(?,?,?,?,?,?)"
                            ),
                            (
                                identifier,
                                current.id,
                                attempt,
                                canonical(
                                    {
                                        "config": current.config.model_dump(),
                                        "inputs": run.inputs,
                                        "lineage_sha256": digest(lineage),
                                    }
                                ),
                                "running",
                                clock,
                            ),
                        ),
                    ]
                )
                if isinstance(current, GenerateNode):
                    await self.store.execute(
                        "UPDATE workflow_graph_steps SET output_json=NULL "
                        "WHERE run_id=? AND node_id=?",
                        (identifier, current.id),
                    )
                await self.state(identifier, "running", current.title)
                await perform(self, await self.get(identifier), current)
                run = await self.get(identifier)
                if run.nodes[current.id].state == "paused":
                    await self.state(identifier, "paused", "Waiting for you: " + current.title)
                    return
                current = None
        except asyncio.CancelledError:
            await self.stop_owned(identifier)
            if current:
                step = (await self.get(identifier)).nodes[current.id]
                if step.state == "running":
                    await self.save(
                        identifier,
                        current.id,
                        "interrupted" if self.closing else "cancelled",
                        step.output,
                        warnings=step.warnings,
                    )
            await self.state(
                identifier,
                "interrupted" if self.closing else "cancelled",
                "Retry unfinished blocks" if self.closing else "Cancelled",
            )
        except Exception as exc:
            message = (
                exc.message
                if isinstance(exc, AppError)
                else "This block failed. Earlier outputs are saved. Retry this block."
            )
            if current:
                step = (await self.get(identifier)).nodes[current.id]
                await self.save(
                    identifier, current.id, "failed", step.output, message, warnings=step.warnings
                )
            await self.state(identifier, "failed", "Retry available", message)
        finally:
            await self.stop_owned(identifier)
            if (await self.get(identifier)).state not in {"running", "queued"}:
                self.live.pop(identifier, None)

    async def stop_owned(self, identifier: str) -> None:
        # Acceptance may commit a child immediately before its await is cancelled.
        # The durable request-key namespace closes that ownership gap.
        children = await self.store.rows(
            "SELECT id FROM image_jobs WHERE request_key LIKE ? "
            "AND state IN ('queued','preparing','running','cancelling')",
            (f"workflow-{identifier}-%",),
        )
        for child in children:
            await self.legacy.images.cancel(child["id"])
        self.owned_images.pop(identifier, None)
        job = self.owned_cleanup.pop(identifier, None)
        if job and not job.closed and job.task:
            job.task.cancel()
            await asyncio.gather(job.task, return_exceptions=True)

    async def decision(self, identifier: str, body: Decision) -> RunV2:
        from .graph import PickNode, ReviewNode

        async with self.lock:
            run = await self.get(identifier)
            node = next((n for n in run.graph.nodes if n.id == body.node_id), None)
            if not isinstance(node, (ReviewNode, PickNode)):
                raise AppError(
                    "workflow_decision", "Choose a review block awaiting your decision.", 422
                )
            step = run.nodes[node.id]
            if isinstance(node, PickNode):
                choices = (step.output or {}).get("choices", [])
                chosen = body.chosen or []
                if (
                    body.decision != "approve"
                    or not chosen
                    or len(set(chosen)) != len(chosen)
                    or len(chosen) > node.config.maximum
                    or any(i < 0 or i >= len(choices) for i in chosen)
                ):
                    raise AppError(
                        "workflow_pick",
                        "Choose at least one result within this block's limit.",
                        422,
                    )
                selected = [choices[i] for i in chosen]
                result = {
                    "chosen": selected
                    if node.config.type == "image_list"
                    else "\n\n".join(selected),
                    "choices": choices,
                    "indices": chosen,
                }
                if step.state == "complete" and (step.output or {}).get("indices") == chosen:
                    return run
                if run.state != "paused" or step.state != "paused":
                    raise AppError(
                        "workflow_pick", "This block is not waiting for a selection.", 409
                    )
                await self.save(
                    identifier, node.id, "complete", result, port="out", warnings=step.warnings
                )
                await self.state(identifier, "queued", "Waiting for a block")
                self.schedule(identifier)
                return await self.get(identifier)
            value = body.value if body.value is not None else (step.output or {}).get("value", "")
            port = "approved" if body.decision == "approve" else "rejected"
            if (
                step.state == "complete"
                and step.port == port
                and (step.output or {}).get("value") == value
            ):
                return run
            if run.state != "paused" or step.state != "paused":
                raise AppError(
                    "workflow_decision", "This block is not awaiting your decision.", 409
                )
            if (
                body.value is not None
                and value != (step.output or {}).get("value", "")
                and not node.config.editable
            ):
                raise AppError("workflow_decision", "This review does not allow editing.", 422)
            await self.save(
                identifier, node.id, "complete", {"value": value}, port=port, warnings=step.warnings
            )
            await self.state(identifier, "queued", "Waiting for a block")
            self.schedule(identifier)
            return await self.get(identifier)

    async def resume(self, identifier: str, body: GraphResume) -> RunV2:
        from .graph import CleanNode, ImageNode

        async with self.lock:
            run = await self.get(identifier)
            if run.state in ACTIVE or identifier in self.tasks:
                raise AppError("workflow_busy", "This workflow is still running.", 409)
            if run.state == "complete":
                return run
            if body.skip_node_id:
                node = next((n for n in run.graph.nodes if n.id == body.skip_node_id), None)
                if not isinstance(node, CleanNode) or run.nodes[node.id].state not in {
                    "failed",
                    "interrupted",
                    "cancelled",
                }:
                    raise AppError(
                        "workflow_skip", "Only an unfinished optional clean-up can be skipped.", 422
                    )
                await self.save(
                    identifier,
                    node.id,
                    "skipped",
                    warnings=["User chose to continue with the original transcript."],
                )
            elif run.state == "paused":
                node = next((n for n in run.graph.nodes if run.nodes[n.id].state == "paused"), None)
                if not isinstance(node, ImageNode) or not body.prompt or not body.prompt.strip():
                    raise AppError(
                        "workflow_review",
                        "Approve the review or shorten the image prompt before continuing.",
                        422,
                    )
                saved = dict(run.nodes[node.id].output or {})
                saved["prompt"] = body.prompt
                await self.save(identifier, node.id, "pending", saved)
            await self.store.execute(
                (
                    "UPDATE workflow_graph_steps SET state='pending',error=NULL WHERE "
                    "run_id=? AND state IN ('failed','cancelled','interrupted')"
                ),
                (identifier,),
            )
            await self.state(identifier, "queued", "Waiting for a block")
            self.schedule(identifier)
            return await self.get(identifier)

    async def cancel(self, identifier: str) -> RunV2:
        async with self.lock:
            run = await self.get(identifier)
            task = self.tasks.get(identifier)
            if task and run.state in ACTIVE:
                await self.state(identifier, "cancelling", "Stopping current block")
                task.cancel()
            elif run.state == "paused":
                await self.store.execute(
                    (
                        "UPDATE workflow_graph_steps SET state='cancelled' WHERE run_id=? "
                        "AND state='paused'"
                    ),
                    (identifier,),
                )
                await self.state(identifier, "cancelled", "Cancelled")
        if task:
            await task
        return await self.get(identifier)

    async def recover(self) -> None:
        from .blocks import reconcile_images

        await self.expire_tests()
        await self.store.execute(
            "UPDATE workflow_graph_steps SET state='interrupted' WHERE state='running'"
        )
        await self.store.execute(
            (
                "UPDATE workflow_graph_attempts SET state='interrupted',finished_a"
                "t=? WHERE state='running'"
            ),
            (now(),),
        )
        for row in await self.store.rows(
            "SELECT id,state FROM workflow_graph_runs WHERE state IN ('queued'"
            ",'running','cancelling')"
        ):
            await reconcile_images(self, await self.get(row["id"]))
            run = await self.get(row["id"])
            if all(s.state in TERMINAL for s in run.nodes.values()):
                await self.state(run.id, "complete", "Ready for review")
            elif row["state"] == "queued" and all(
                s.state in TERMINAL | {"pending"} for s in run.nodes.values()
            ):
                self.schedule(run.id)
            else:
                await self.state(run.id, "interrupted", "Retry unfinished blocks")

    async def tail(self, after: int) -> AsyncIterator[tuple[int, RunV2]]:
        while True:
            async with self.changed:
                records = await self.store.rows(
                    (
                        "SELECT id,data_json FROM workflow_graph_events WHERE id>? ORDER B"
                        "Y id LIMIT 100"
                    ),
                    (after,),
                )
                while not records:
                    await self.changed.wait()
                    records = await self.store.rows(
                        (
                            "SELECT id,data_json FROM workflow_graph_events WHERE id>? ORDER B"
                            "Y id LIMIT 100"
                        ),
                        (after,),
                    )
            for record in records:
                after = record["id"]
                yield after, RunV2.model_validate_json(record["data_json"])

    async def expire_tests(self) -> None:
        # Called on startup and run-list reads. No timer or polling loop. Image files
        # remain Gallery-owned; removing a test never removes an image output.
        rows = await self.store.rows(
            (
                "SELECT id,snapshot_id FROM workflow_graph_runs WHERE mode='test' AND"
                " expires_at<? AND state NOT IN ('queued','running','paused','cancelling')"
            ),
            (now(),),
        )
        for row in rows:
            identifier = row["id"]
            if identifier in self.tasks:
                continue
            await self.store.batch(
                [
                    (f"DELETE FROM {table} WHERE run_id=?", (identifier,))
                    for table in [
                        "workflow_graph_events",
                        "workflow_graph_sources",
                        "workflow_graph_attempts",
                        "workflow_graph_steps",
                    ]
                ]
                + [
                    ("DELETE FROM workflow_graph_runs WHERE id=?", (identifier,)),
                    (
                        "DELETE FROM workflow_def_snapshots WHERE id=? AND label IS NULL "
                        "AND NOT EXISTS (SELECT 1 FROM workflow_graph_runs WHERE snapshot_id=?)",
                        (row["snapshot_id"], row["snapshot_id"]),
                    ),
                ]
            )

    async def close(self) -> None:
        self.closing = True
        tasks = list(self.tasks.values())
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        for queue in tuple(self.listeners):
            if queue.full():
                queue.get_nowait()
            queue.put_nowait(("server.closed", {}))
        # Let SSE producers release this store before the database closes.
        try:
            async with asyncio.timeout(1), self.streams_closed:
                await self.streams_closed.wait_for(lambda: not self.listeners)
        except TimeoutError:
            pass  # A blocked client cannot delay shutdown; reconnect uses SQLite.
