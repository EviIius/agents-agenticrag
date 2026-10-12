"""Mandatory byte parity against the existing performers, using synthetic inputs."""

import json
from typing import Any

import pytest

from app.workflows.graph import CleanNode, GenerateNode, ModelRef
from app.workflows.graph_schemas import Decision
from app.workflows.schemas import WorkflowCreate, WorkflowResume
from app.workflows.template_graphs import template_graph
from tests.test_cleanup import record
from tests.test_workflow_graph_engine import create, finish, submit
from tests.test_workflows import finish as legacy_finish
from tests.test_workflows import spec


def request_bytes(row: dict[str, Any], graph: bool) -> bytes:
    saved = json.loads(row["input_json"])
    saved = saved["request"] if graph else saved
    return json.dumps(
        {key: saved[key] for key in ["messages", "params", "context_length"]},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode()


@pytest.mark.parametrize("review,count", [(False, 1), (True, 1), (False, 3), (True, 3)])
async def test_brief_to_images_exact_requests_prompts_and_seeds(
    chat_app: Any, review: bool, count: int
) -> None:
    app, _, runtime = chat_app
    graph = template_graph("brief_images", review=review, seeds=list(range(42, 42 + count)))
    overrides = {"temperature": 0.4, "max_tokens": 128}
    for node in graph.nodes:
        if isinstance(node, GenerateNode):
            node.config.params = node.config.params.model_validate(overrides)
    definition = await create(app, graph)
    await app.state.store.execute(
        "INSERT INTO model_prefs(connection_id,model_id,params_json) VALUES(?,?,?)",
        (app.state.test_connection, "fake-chat", '{"top_p":0.8}'),
    )
    legacy = await app.state.workflows.submit(
        WorkflowCreate.model_validate(
            spec(
                app,
                review_prompt=review,
                seeds=list(range(42, 42 + count)),
                model={
                    "connection_id": app.state.test_connection,
                    "model_id": "fake-chat",
                    "params": overrides,
                },
            )
        )
    )
    await legacy_finish(app, legacy.id)
    if review:
        await app.state.workflows.resume(legacy.id, WorkflowResume(prompt=None, skip_cleanup=False))
        await legacy_finish(app, legacy.id)
    old_captures = [c for c in runtime.state.captures if c.get("messages")]
    runtime.state.captures.clear()
    current = await submit(app, definition, inputs={"brief": legacy.input.brief})
    current = await finish(app, current.id)
    if review:
        await app.state.workflow_graphs.decision(
            current.id, Decision(node_id="n_review", decision="approve", value=None)
        )
        current = await finish(app, current.id)
    assert current.state == "complete"
    assert [c for c in runtime.state.captures if c.get("messages")] == old_captures
    old_requests = await app.state.store.rows(
        "SELECT input_json FROM workflow_attempts WHERE run_id=? AND position=0", (legacy.id,)
    )
    new_requests = await app.state.store.rows(
        "SELECT input_json FROM workflow_graph_attempts WHERE run_id=? AND node_id='n_draft'",
        (current.id,),
    )
    assert [request_bytes(r, False) for r in old_requests] == [
        request_bytes(r, True) for r in new_requests
    ]
    legacy = await app.state.workflows.get(legacy.id)
    old_images = [
        await app.state.images.get(s.output["image_job_id"])
        for s in legacy.steps
        if s.kind == "image"
    ]
    new_images = [
        await app.state.images.get(i["id"]) for i in current.nodes["n_images"].output["images"]
    ]
    assert [(i.prompt, i.seed) for i in new_images] == [(i.prompt, i.seed) for i in old_images]


@pytest.mark.parametrize("cleanup", [False, True])
async def test_meeting_pack_exact_messages_defaults_transcription_and_cleanup(
    chat_app: Any, cleanup: bool
) -> None:
    app, client, runtime = chat_app
    item = await record(
        app, client, "Alex will send the draft on Friday. No budget owner was assigned."
    )
    await app.state.store.execute(
        "UPDATE transcripts SET segments_json=? WHERE attachment_id=?",
        (
            json.dumps(
                [
                    {
                        "start": 0.25,
                        "end": 2,
                        "speaker": "Fake speaker",
                        "text": "Alex will send the draft on Friday. No budget owner was assigned.",
                        "raw_text": (
                            "Alex will send the draft on Friday. No budget owner was assigned."
                        ),
                    }
                ]
            ),
            item["id"],
        ),
    )
    graph = template_graph("meeting_pack", cleanup=cleanup)
    chosen = ModelRef(connection_id=app.state.test_connection, model_id="fake-chat")
    for node in graph.nodes:
        if isinstance(node, CleanNode):
            node.config.model = chosen
    definition = await create(app, graph)
    calls: list[tuple[str, tuple[Any, ...]]] = []
    transcription_start = app.state.transcription.start
    cleanup_start = app.state.cleanup.start

    async def tx(*args: Any, **kwargs: Any) -> Any:
        calls.append(("transcribe", args))
        return await transcription_start(*args, **kwargs)

    async def clean(*args: Any, **kwargs: Any) -> Any:
        calls.append(("cleanup", args))
        return await cleanup_start(*args, **kwargs)

    app.state.transcription.start = tx
    app.state.cleanup.start = clean
    await app.state.store.execute(
        "INSERT INTO model_prefs(connection_id,model_id,params_json) VALUES(?,?,?)",
        (app.state.test_connection, "fake-chat", '{"top_p":0.8}'),
    )
    legacy = await app.state.workflows.submit(
        WorkflowCreate.model_validate(
            spec(
                app,
                template="meeting_pack",
                brief="",
                attachment_id=item["id"],
                cleanup_model=chosen.model_dump() if cleanup else None,
            )
        )
    )
    await legacy_finish(app, legacy.id)
    legacy = await app.state.workflows.get(legacy.id)
    assert legacy.state == "complete"
    old_captures = [c for c in runtime.state.captures if c.get("messages")]
    old_calls = list(calls)
    calls.clear()
    runtime.state.captures.clear()
    current = await submit(app, definition, inputs={"recording": item["id"]})
    current = await finish(app, current.id)
    assert current.state == "complete"
    assert calls == old_calls
    assert [c for c in runtime.state.captures if c.get("messages")] == old_captures
    position = 2 if cleanup else 1
    old_request = await app.state.store.one(
        "SELECT input_json FROM workflow_attempts WHERE run_id=? AND position=?",
        (legacy.id, position),
    )
    new_request = await app.state.store.one(
        "SELECT input_json FROM workflow_graph_attempts WHERE run_id=? AND node_id='n_pack'",
        (current.id,),
    )
    assert request_bytes(old_request, False) == request_bytes(new_request, True)
    # This declaration neither alters clean-up sampling nor adds an answer call.
    assert len(old_captures) == 2 if cleanup else len(old_captures) == 1
