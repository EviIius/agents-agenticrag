"""Fake-runtime graph durability, API compatibility, privacy and ownership."""

import asyncio
import json
from typing import Any

import pytest

from app.errors import AppError
from app.workflows.graph import GraphDoc, ImageNode, ModelRef
from app.workflows.graph_schemas import Decision, DefCreate, GraphResume, GraphSubmit
from app.workflows.template_graphs import template_graph
from app.workflows.views import stream
from tests.test_cleanup import record
from tests.test_images import FakeEngine


async def create(app: Any, graph: GraphDoc | None = None, template: str = "brief_images") -> Any:
    app.state.images.engine = FakeEngine()
    app.state.images.engine.release.set()
    graph = graph or template_graph(template)
    graph.settings.default_model = ModelRef(
        connection_id=app.state.test_connection, model_id="fake-chat"
    )
    return await app.state.workflow_graphs.defs.create(DefCreate(name="Fake workflow", graph=graph))


async def finish(app: Any, identifier: str) -> Any:
    task = app.state.workflow_graphs.tasks.get(identifier)
    if task:
        async with asyncio.timeout(8):
            await task
    await asyncio.sleep(0)
    return await app.state.workflow_graphs.get(identifier)


async def submit(
    app: Any, definition: Any, key: str = "fake-graph-request", inputs: dict[str, Any] | None = None
) -> Any:
    return await app.state.workflow_graphs.submit(
        definition.id,
        GraphSubmit(request_key=key, inputs=inputs or {"brief": "One blue circle on white"}),
    )


async def test_definition_api_concurrency_archive_and_immutable_layout_snapshots(
    chat_app: Any,
) -> None:
    app, client, _ = chat_app
    app.state.images.engine = FakeEngine()
    app.state.images.engine.release.set()
    created = (
        await client.post(
            "/api/workflows/defs",
            json={
                "graph": template_graph("brief_images", seeds=[42]).model_dump(by_alias=True),
                "default_model": {
                    "connection_id": app.state.test_connection,
                    "model_id": "fake-chat",
                },
            },
        )
    ).json()
    path = "/api/workflows/defs/" + created["id"]
    body = {
        "name": "Fake updated",
        "description": "Synthetic",
        "icon": "image",
        "graph": created["graph"],
        "version": created["version"],
    }
    first_run = await client.post(
        path + "/runs",
        json={"request_key": "fake-layout-before", "inputs": {"brief": "Fake circle"}},
    )
    assert first_run.status_code == 202
    await finish(app, first_run.json()["id"])
    body["graph"]["nodes"][0]["position"]["x"] = 888
    saved = await client.put(path, json=body)
    assert saved.status_code == 200
    assert saved.json()["version"] == 2 and saved.json()["graph_hash"] == created["graph_hash"]
    conflict = await client.put(path, json=body)
    assert conflict.status_code == 409 and conflict.json()["current"] == saved.json()
    body["force"] = True
    assert (await client.put(path, json=body)).json()["version"] == 3
    assert len((await client.get(path + "/snapshots")).json()) == 1
    second_run = await client.post(
        path + "/runs",
        json={"request_key": "fake-layout-after", "inputs": {"brief": "Fake circle"}},
    )
    assert second_run.status_code == 202
    await finish(app, second_run.json()["id"])
    snaps = (await client.get(path + "/snapshots")).json()
    assert len(snaps) == 2 and snaps[0]["id"] != snaps[1]["id"]
    assert all(s["run_count"] == 1 for s in snaps)
    assert snaps[0]["graph_hash"] == snaps[1]["graph_hash"]
    assert {s["graph"]["nodes"][0]["position"]["x"] for s in snaps} == {320, 888}
    assert (
        await client.patch(
            path + "/snapshots/" + snaps[0]["id"], json={"label": "Fake named version"}
        )
    ).json()["label"] == "Fake named version"
    duplicated = await client.post(path + "/duplicate")
    assert duplicated.status_code == 201 and duplicated.json()["id"] != created["id"]
    assert (await client.delete(path)).status_code == 204
    assert (await client.get(path)).json()["archived_at"]
    assert created["id"] not in {d["id"] for d in (await client.get("/api/workflows/defs")).json()}
    assert (
        await client.post(
            path + "/runs", json={"request_key": "fake-archived", "inputs": {"brief": "x"}}
        )
    ).status_code == 409
    assert len((await client.get("/api/workflows/blocks")).json()["blocks"]) == 7
    assert len((await client.get("/api/workflows/templates")).json()) == 2


async def test_idempotent_submission_seed_resolution_and_approval_reject_paths(
    chat_app: Any,
) -> None:
    app, client, _ = chat_app
    definition = await create(app)
    run = await submit(app, definition)
    duplicate = await submit(app, definition)
    assert duplicate.id == run.id and duplicate.graph == run.graph
    assert definition.graph.nodes[3].config.seeds == "auto"
    assert isinstance(run.graph.nodes[3].config.seeds, list)
    conflict = await client.post(
        f"/api/workflows/defs/{definition.id}/runs",
        json={"request_key": "fake-graph-request", "inputs": {"brief": "Different"}},
    )
    assert conflict.status_code == 409
    run = await finish(app, run.id)
    assert run.state == "paused" and app.state.images.engine.calls == 0
    denied = await client.post(
        f"/api/workflows/runs/{run.id}/decision", json={"node_id": "n_review", "decision": "reject"}
    )
    assert denied.status_code == 200
    run = await finish(app, run.id)
    assert run.state == "complete" and run.nodes["n_images"].state == "skipped"
    assert run.nodes["n_save"].state == "skipped" and app.state.images.engine.calls == 0
    run2 = await submit(app, definition, "fake-approved")
    await finish(app, run2.id)
    await app.state.workflow_graphs.decision(
        run2.id, Decision(node_id="n_review", decision="approve", value="Two green circles")
    )
    run2 = await finish(app, run2.id)
    assert run2.state == "complete" and run2.results[0].items[0].value == "Two green circles"
    image = await app.state.images.get(run2.results[0].items[1].value[0]["id"])
    assert image.prompt == "Two green circles" and image.seed == run2.graph.nodes[3].config.seeds[0]
    # Retrying the same decision is idempotent even after completion.
    assert (
        await app.state.workflow_graphs.decision(
            run2.id, Decision(node_id="n_review", decision="approve", value="Two green circles")
        )
    ).id == run2.id


async def test_cancel_reaps_owned_images_then_retry_reuses_text_and_seeds(chat_app: Any) -> None:
    app, _, runtime = chat_app
    definition = await create(app, template_graph("brief_images", review=False))
    app.state.images.engine.release.clear()
    run = await submit(app, definition)
    await asyncio.wait_for(app.state.images.engine.started.wait(), 5)
    stopped = await app.state.workflow_graphs.cancel(run.id)
    assert stopped.state == "cancelled" and app.state.images.engine.reaped.is_set()
    assert stopped.nodes["n_draft"].state == "complete"
    app.state.images.engine.release.set()
    await app.state.workflow_graphs.resume(run.id, GraphResume(prompt=None))
    completed = await finish(app, run.id)
    assert completed.state == "complete" and completed.graph == stopped.graph
    assert completed.nodes["n_draft"].output == stopped.nodes["n_draft"].output
    assert len([c for c in runtime.state.captures if c.get("messages")]) == 1


async def test_multi_image_failure_preserves_first_image_on_retry(chat_app: Any) -> None:
    app, _, runtime = chat_app
    definition = await create(app, template_graph("brief_images", review=False, seeds=[1, 2]))
    engine = app.state.images.engine
    original = engine.run

    async def fail_second(*args: Any, **kwargs: Any) -> int:
        engine.fail = engine.calls == 1
        return int(await original(*args, **kwargs))

    engine.run = fail_second
    run = await submit(app, definition)
    failed = await finish(app, run.id)
    assert failed.state == "failed"
    first = failed.nodes["n_images"].output["images"][0]
    engine.run = original
    engine.fail = False
    await app.state.workflow_graphs.resume(run.id, GraphResume(prompt=None))
    result = await finish(app, run.id)
    assert result.state == "complete" and result.nodes["n_images"].output["images"][0] == first
    assert engine.calls == 3
    assert len([c for c in runtime.state.captures if c.get("messages")]) == 1


async def test_disabled_cleanup_join_sources_and_exports_survive_attachment_deletion(
    chat_app: Any,
) -> None:
    app, client, _ = chat_app
    item = await record(app, client, "Alex will send the draft on Friday.")
    definition = await create(app, template="meeting_pack")
    run = await submit(app, definition, inputs={"recording": item["id"]})
    result = await finish(app, run.id)
    assert result.state == "complete" and result.nodes["n_clean"].state == "skipped"
    assert result.nodes["n_pack"].warnings == ["The output of 'clean' was skipped."]
    await app.state.transcription.remove(item["id"])
    exported = await client.get(f"/api/workflows/runs/{run.id}/v2/export?format=json")
    assert exported.json()["sources"][0]["source"]["text"] == "Alex will send the draft on Friday."
    assert exported.json()["review_required"] is True
    assert (
        "Original transcript"
        in (await client.get(f"/api/workflows/runs/{run.id}/v2/export?format=md")).text
    )
    old = await client.get("/api/workflows")
    assert old.json() == {"runs": []}  # Graph inputs never reach the legacy parser.
    assert (await client.get(f"/api/workflows/runs/{run.id}/v2")).json()["kind"] == "graph"


async def test_stream_reconnect_replays_durable_state_and_ephemeral_has_no_id(
    chat_app: Any,
) -> None:
    app, _, _ = chat_app
    definition = await create(app)
    run = await submit(app, definition)
    await finish(app, run.id)
    reader = stream(app.state.workflow_graphs, "0:1")
    initial = await anext(reader)
    assert initial["event"] == "run.snapshot"
    update = await asyncio.wait_for(anext(reader), 2)
    assert update["event"] == "run.updated" and update["id"].startswith("0:")
    assert json.loads(update["data"])["run"]["id"] == run.id
    await reader.aclose()
    reader = stream(app.state.workflow_graphs, "0:0")
    await anext(reader)
    pending = asyncio.ensure_future(anext(reader))
    await app.state.workflow_graphs.ephemeral(
        "node.progress",
        {"run_id": run.id, "node_id": "n_draft", "done": 1, "total": 2, "label": "Fake progress"},
    )
    event = await asyncio.wait_for(pending, 2)
    assert event["event"] == "node.progress" and "id" not in event
    await reader.aclose()
    assert not app.state.workflow_graphs.listeners


async def test_privacy_taint_is_checked_before_any_model_call(chat_app: Any) -> None:
    app, client, runtime = chat_app
    item = await record(app, client, "Synthetic private source.")
    definition = await create(app, template="meeting_pack")
    await app.state.store.execute(
        "UPDATE connections SET base_url=? WHERE id=?",
        ("https://remote.example.test", app.state.test_connection),
    )
    response = await client.post(
        f"/api/workflows/defs/{definition.id}/runs",
        json={"request_key": "fake-private", "inputs": {"recording": item["id"]}},
    )
    assert (
        response.status_code == 422
        and response.json()["error"]["code"] == "recording_requires_local"
    )
    assert not [c for c in runtime.state.captures if c.get("messages")]
    assert not await app.state.store.rows("SELECT * FROM workflow_graph_runs")


async def test_interruption_recovery_and_retry_do_not_repeat_finished_native_work(
    chat_app: Any,
) -> None:
    from app.workflows.engine import GraphRunner

    app, _, runtime = chat_app
    original = app.state.workflow_graphs
    definition = await create(app, template_graph("brief_images", review=False))
    app.state.images.engine.release.clear()
    run = await submit(app, definition)
    await asyncio.wait_for(app.state.images.engine.started.wait(), 5)
    await original.close()
    interrupted = await original.get(run.id)
    assert interrupted.state == "interrupted"
    assert interrupted.nodes["n_draft"].state == "complete"
    assert app.state.images.engine.reaped.is_set()
    replacement = GraphRunner(app.state.store, app.state.workflows)
    app.state.workflow_graphs = replacement
    await replacement.recover()
    app.state.images.engine.release.set()
    await replacement.resume(run.id, GraphResume(prompt=None))
    result = await finish(app, run.id)
    assert result.state == "complete"
    assert result.graph == run.graph and result.nodes["n_draft"].attempt == 1
    assert len([c for c in runtime.state.captures if c.get("messages")]) == 1
    assert (
        await app.state.store.one(
            "SELECT state FROM workflow_graph_attempts "
            "WHERE run_id=? AND node_id='n_images' AND attempt=1",
            (run.id,),
        )
    )["state"] == "interrupted"


async def test_completed_image_commit_reconciles_without_regeneration(chat_app: Any) -> None:
    app, _, _ = chat_app
    definition = await create(app, template_graph("brief_images", review=False))
    run = await submit(app, definition)
    completed = await finish(app, run.id)
    original = completed.nodes["n_images"].output
    calls = app.state.images.engine.calls
    # Simulate worker completion immediately before the graph's completion commit.
    await app.state.store.execute(
        "UPDATE workflow_graph_runs SET state='running' WHERE id=?", (run.id,)
    )
    await app.state.store.execute(
        "UPDATE workflow_graph_steps SET state='running',output_json=NULL "
        "WHERE run_id=? AND node_id='n_images'",
        (run.id,),
    )
    await app.state.workflow_graphs.recover()
    await app.state.workflow_graphs.resume(run.id, GraphResume(prompt=None))
    recovered = await finish(app, run.id)
    assert recovered.state == "complete" and recovered.nodes["n_images"].output == original
    assert app.state.images.engine.calls == calls


async def test_cleanup_guard_failure_skip_then_join_uses_original(chat_app: Any) -> None:
    app, client, runtime = chat_app
    item = await record(app, client, "FAKE-REWRITE this recording must keep its original words.")
    definition = await create(app, template_graph("meeting_pack", cleanup=True))
    run = await submit(app, definition, inputs={"recording": item["id"]})
    failed = await finish(app, run.id)
    assert failed.state == "failed" and failed.nodes["n_clean"].state == "failed"
    assert failed.nodes["n_pack"].attempt == 0
    await app.state.workflow_graphs.resume(run.id, GraphResume(skip_node_id="n_clean", prompt=None))
    result = await finish(app, run.id)
    assert result.state == "complete" and result.nodes["n_clean"].state == "skipped"
    request = [c for c in runtime.state.captures if c.get("messages")][-1]
    assert "FAKE-REWRITE" in request["messages"][1]["content"]
    assert "cleaned_reading_aid" not in request["messages"][1]["content"]


async def test_long_image_prompt_pauses_and_reuses_draft_after_explicit_edit(chat_app: Any) -> None:
    app, _, runtime = chat_app
    graph = template_graph("brief_images", review=False)
    assert isinstance(graph.nodes[2], ImageNode)
    graph.nodes[2].config.prompt = "{{draft.text}}" + "x" * 4000
    definition = await create(app, graph)
    run = await submit(app, definition)
    paused = await finish(app, run.id)
    assert paused.state == "paused" and app.state.images.engine.calls == 0
    await app.state.workflow_graphs.resume(run.id, GraphResume(prompt="One circle"))
    result = await finish(app, run.id)
    assert result.state == "complete"
    assert (
        await app.state.images.get(result.nodes["n_images"].output["images"][0]["id"])
    ).prompt == "One circle"
    assert len([c for c in runtime.state.captures if c.get("messages")]) == 1


async def test_multiple_originals_are_independent_and_sources_survive_removal(
    chat_app: Any,
) -> None:
    app, client, _ = chat_app
    a = await record(app, client, "Synthetic first original.")
    b = await record(app, client, "Synthetic second original.")
    raw = template_graph("meeting_pack").model_dump(by_alias=True)
    raw["nodes"][0]["config"]["fields"].append(
        {"name": "second", "label": "Second recording", "type": "recording", "required": True}
    )
    second = {
        **raw["nodes"][1],
        "id": "n_second",
        "key": "second",
        "config": {"recording": "{{start.second}}"},
    }
    raw["nodes"].append(second)
    raw["nodes"][3]["config"]["prompt"] += "\n{{second.text | tagged:second_original}}"
    raw["edges"].extend(
        [
            {
                "id": "e_second",
                "source": "n_start",
                "target": "n_second",
                "source_port": "out",
                "target_port": "in",
            },
            {
                "id": "e_join",
                "source": "n_second",
                "target": "n_pack",
                "source_port": "out",
                "target_port": "in",
            },
        ]
    )
    definition = await create(app, GraphDoc.model_validate(raw))
    run = await submit(app, definition, inputs={"recording": a["id"], "second": b["id"]})
    assert (await finish(app, run.id)).state == "complete"
    await app.state.transcription.remove(a["id"])
    await app.state.transcription.remove(b["id"])
    sources = (await client.get(f"/api/workflows/runs/{run.id}/v2/sources")).json()
    assert {s["source"]["text"] for s in sources} == {
        "Synthetic first original.",
        "Synthetic second original.",
    }
    assert len({s["sha256"] for s in sources}) == 2


async def test_paged_legacy_projection_and_live_legacy_stream(chat_app: Any) -> None:
    from app.workflows.schemas import WorkflowCreate
    from tests.test_workflows import finish as old_finish
    from tests.test_workflows import spec

    app, client, _ = chat_app
    definition = await create(app)
    graph_run = await submit(app, definition)
    await finish(app, graph_run.id)
    reader = stream(app.state.workflow_graphs, "0:0")
    await anext(reader)
    old = await app.state.workflows.submit(
        WorkflowCreate.model_validate(spec(app, review_prompt=False))
    )
    await old_finish(app, old.id)
    update = await asyncio.wait_for(anext(reader), 2)
    assert (
        update["event"] == "run.updated" and json.loads(update["data"])["run"]["kind"] == "template"
    )
    await reader.aclose()
    first = (await client.get("/api/workflows/runs?limit=1")).json()
    assert len(first["items"]) == 1 and first["next_cursor"]
    second = (
        await client.get("/api/workflows/runs", params={"limit": 1, "cursor": first["next_cursor"]})
    ).json()
    assert len(second["items"]) == 1 and second["items"][0]["id"] != first["items"][0]["id"]
    assert {first["items"][0]["kind"], second["items"][0]["kind"]} == {"graph", "template"}
    assert (await client.get(f"/api/workflows/runs/{old.id}/v2")).json()["nodes"]["n_save"][
        "state"
    ] == "complete"
    assert (await client.get("/api/workflows/runs?cursor=invalid")).status_code == 422


@pytest.mark.parametrize(
    "inputs", [{}, {"brief": 2}, {"brief": "x", "unknown": True}, {"brief": "x" * 20001}]
)
async def test_invalid_start_inputs_are_rejected_without_orphans(
    chat_app: Any, inputs: dict[str, Any]
) -> None:
    app, _, runtime = chat_app
    definition = await create(app)
    with pytest.raises(AppError):
        await submit(app, definition, inputs=inputs if inputs else {"brief": ""})
    assert not await app.state.store.rows("SELECT * FROM workflow_graph_runs")
    assert not [c for c in runtime.state.captures if c.get("messages")]


async def test_cancellation_after_child_acceptance_closes_the_ownership_gap(chat_app: Any) -> None:
    app, _, _ = chat_app
    definition = await create(app, template_graph("brief_images", review=False))
    engine = app.state.images.engine
    engine.release.clear()
    accepted = asyncio.Event()
    original = app.state.images.submit

    async def uncertain(body: Any) -> Any:
        image = await original(body)
        accepted.set()
        await asyncio.Event().wait()
        return image

    app.state.images.submit = uncertain
    run = await submit(app, definition)
    await asyncio.wait_for(accepted.wait(), 3)
    await asyncio.wait_for(engine.started.wait(), 3)
    cancelled = await app.state.workflow_graphs.cancel(run.id)
    assert cancelled.state == "cancelled" and engine.reaped.is_set()
    assert not await app.state.store.rows(
        "SELECT id FROM image_jobs WHERE state IN ('queued','preparing','running','cancelling')"
    )


@pytest.mark.parametrize(
    "reply,passes",
    [
        (' {"label":"Fake label","count":2,"approved":true} ', True),
        ('{"label":"Fake label","count":true,"approved":true}', False),
        ('{"label":"Fake label"}', False),
        ("not JSON", False),
    ],
)
async def test_json_fields_use_native_schema_and_strict_host_validation(
    chat_app: Any, monkeypatch: pytest.MonkeyPatch, reply: str, passes: bool
) -> None:
    from collections.abc import AsyncIterator

    from app.providers.base import ChatRequest, Finish, ProviderEvent, TextDelta
    from app.providers.ollama import Ollama

    app, _, _ = chat_app
    raw = template_graph("brief_images", review=False).model_dump(by_alias=True)
    raw["nodes"] = [raw["nodes"][0], raw["nodes"][1], raw["nodes"][-1]]
    raw["nodes"][1]["config"].update(
        {
            "format": "json",
            "json_fields": [
                {"name": "label", "type": "string"},
                {"name": "count", "type": "number"},
                {"name": "approved", "type": "boolean"},
            ],
        }
    )
    raw["nodes"][2]["config"]["include"] = [{"label": "Draft", "ref": "{{draft.text}}"}]
    raw["edges"] = [
        raw["edges"][0],
        {
            "id": "e_save",
            "source": "n_draft",
            "target": "n_save",
            "source_port": "out",
            "target_port": "in",
        },
    ]
    captured: list[ChatRequest] = []

    async def fake_stream(
        self: Ollama, req: ChatRequest, *, background: bool = False
    ) -> AsyncIterator[ProviderEvent]:
        assert background
        captured.append(req)
        yield TextDelta(reply)
        yield Finish("stop")

    monkeypatch.setattr(Ollama, "stream", fake_stream)
    definition = await create(app, GraphDoc.model_validate(raw))
    run = await submit(app, definition)
    result = await finish(app, run.id)
    assert len(captured) == 1 and captured[0].json_schema is not None
    assert captured[0].json_schema["required"] == ["label", "count", "approved"]
    assert captured[0].params == {}
    assert result.state == ("complete" if passes else "failed")
    assert result.nodes["n_draft"].output["text"] == reply
    if passes:
        assert result.nodes["n_draft"].output["count"] == 2
        assert result.nodes["n_draft"].output["approved"] is True
    else:
        assert result.nodes["n_draft"].error.startswith("The model did not return")


async def test_context_overflow_preserves_original_without_any_inference(chat_app: Any) -> None:
    app, client, runtime = chat_app
    item = await record(app, client, "Original long source. " * 2000)
    definition = await create(app, template="meeting_pack")
    run = await submit(app, definition, inputs={"recording": item["id"]})
    result = await finish(app, run.id)
    assert result.state == "failed" and "No source was truncated" in result.error
    sources = (await client.get(f"/api/workflows/runs/{run.id}/v2/sources")).json()
    assert sources[0]["source"]["text"] == "Original long source. " * 2000
    assert not [c for c in runtime.state.captures if c.get("messages")]


async def test_text_tail_and_next_block_progress_share_the_per_run_rate_limit(
    chat_app: Any,
) -> None:
    app, _, _ = chat_app
    manager = app.state.workflow_graphs
    queue: asyncio.Queue[Any] = asyncio.Queue(10)
    manager.listeners.add(queue)
    timestamps: list[float] = []
    for kind in ["node.text", "node.text", "node.progress"]:
        await manager.ephemeral(
            kind, {"run_id": "fake-rate-run", "node_id": "fake-block", "delta": "Fake text"}
        )
        await queue.get()
        timestamps.append(asyncio.get_running_loop().time())
    assert all(b - a >= 0.099 for a, b in zip(timestamps, timestamps[1:], strict=False))
    manager.listeners.discard(queue)


async def test_legacy_partial_images_keep_failed_block_and_explicit_overrides(
    chat_app: Any,
) -> None:
    from app.workflows.graph import GenerateNode
    from app.workflows.views import legacy_view
    from tests.test_workflows import finish as old_finish
    from tests.test_workflows import start as old_start

    app, client, _ = chat_app
    created = await old_start(
        app,
        client,
        review_prompt=False,
        seeds=[1, 2, 3],
        model={
            "connection_id": app.state.test_connection,
            "model_id": "fake-chat",
            "params": {"temperature": 0.4},
        },
    )
    engine = app.state.images.engine
    original = engine.run

    async def fail_second(*args: Any, **kwargs: Any) -> int:
        engine.fail = engine.calls == 1
        return int(await original(*args, **kwargs))

    engine.run = fail_second
    await old_finish(app, created["id"])
    legacy = await app.state.workflows.get(created["id"])
    assert legacy.state == "failed" and legacy.steps[-1].state == "pending"
    adapted = await legacy_view(app.state.workflow_graphs, legacy)
    assert adapted.nodes["n_images"].state == "failed" and adapted.nodes["n_images"].error
    assert adapted.nodes["n_images"].output is not None
    assert len(adapted.nodes["n_images"].output["images"]) == 1
    assert isinstance(adapted.graph.nodes[1], GenerateNode)
    assert adapted.graph.nodes[1].config.params.temperature == 0.4


async def test_legacy_skipped_cleanup_and_results_are_faithfully_projected(chat_app: Any) -> None:
    from app.workflows.graph import CleanNode, ModelRef
    from app.workflows.schemas import WorkflowResume
    from app.workflows.views import legacy_view
    from tests.test_workflows import finish as old_finish
    from tests.test_workflows import start as old_start

    app, client, _ = chat_app
    item = await record(app, client, "FAKE-REWRITE preserve this original speech.")
    created = await old_start(
        app,
        client,
        template="meeting_pack",
        brief="",
        attachment_id=item["id"],
        cleanup_model={"connection_id": app.state.test_connection, "model_id": "fake-reasoning"},
    )
    await old_finish(app, created["id"])
    assert (await app.state.workflows.get(created["id"])).state == "failed"
    await app.state.workflows.resume(created["id"], WorkflowResume(prompt=None, skip_cleanup=True))
    await old_finish(app, created["id"])
    legacy = await app.state.workflows.get(created["id"])
    adapted = await legacy_view(app.state.workflow_graphs, legacy)
    assert adapted.state == "complete"
    assert adapted.nodes["n_clean"].state == "skipped" and adapted.nodes["n_clean"].port is None
    assert (
        adapted.nodes["n_clean"].output is not None
        and adapted.nodes["n_clean"].output["text"] == ""
    )
    assert isinstance(adapted.graph.nodes[2], CleanNode)
    assert isinstance(adapted.graph.nodes[2].config.model, ModelRef)
    assert adapted.graph.nodes[2].config.model.model_id == "fake-reasoning"
    assert adapted.results[0].items[0].value == legacy.steps[-1].output["text"]


async def test_template_copy_keeps_public_description_and_icon(chat_app: Any) -> None:
    from app.workflows.template_graphs import template_list

    app, _, _ = chat_app
    for template in template_list():
        copied = await app.state.workflow_graphs.defs.create(
            DefCreate.model_validate(
                {"name": "Synthetic template copy", "template_id": template.id}
            )
        )
        assert copied.description == template.description
        assert copied.icon == template.icon
        assert copied.graph == template.graph
