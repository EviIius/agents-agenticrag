"""Studio cross-run provenance, single-block isolation, picks and retention."""

import json
from typing import Any

import pytest

from app.errors import AppError
from app.workflows.graph import GenerateNode, GraphDoc, ModelRef
from app.workflows.graph_schemas import Decision, DefCreate, DefSave, GraphSubmit
from app.workflows.reuse import plan
from app.workflows.template_graphs import template_graph
from app.workflows.views import page
from tests.test_cleanup import record
from tests.test_workflow_graph_engine import create, finish, submit


async def test_run_from_here_is_idempotent_and_reuses_only_verified_upstream(chat_app: Any) -> None:
    app, _, runtime = chat_app
    manager = app.state.workflow_graphs
    definition = await create(app, template_graph("brief_images", review=False, seeds=[17]))
    original = await finish(app, (await submit(app, definition)).id)
    reuse = await plan(manager, definition.id, "n_images")
    assert reuse.eligible and reuse.source_run_id == original.id
    body = GraphSubmit(
        request_key="fake-run-from-here", node_id="n_images", source_run_id=original.id
    )
    run = await manager.submit(definition.id, body)
    duplicate = await manager.submit(definition.id, body)
    result = await finish(app, run.id)
    assert duplicate.id == run.id and result.state == "complete"
    assert result.nodes["n_draft"].reused_from == original.id
    assert result.nodes["n_draft"].output == original.nodes["n_draft"].output
    assert result.nodes["n_draft"].attempt == 0 and result.nodes["n_images"].attempt == 1
    assert len([c for c in runtime.state.captures if c.get("messages")]) == 1
    assert app.state.images.engine.calls == 2
    assert result.parent_run_id == original.id
    changed = definition.graph.model_copy(deep=True)
    changed.nodes[1].config.prompt += " changed"
    await manager.defs.save(
        definition.id,
        DefSave(name=definition.name, description="", graph=changed, version=definition.version),
    )
    assert not (await plan(manager, definition.id, "n_images")).eligible
    with pytest.raises(AppError, match="changed"):
        await manager.submit(
            definition.id,
            GraphSubmit(
                request_key="fake-invalid-reuse", node_id="n_images", source_run_id=original.id
            ),
        )


async def test_changed_saved_defaults_and_inputs_refuse_reuse(chat_app: Any) -> None:
    app, _, _ = chat_app
    manager = app.state.workflow_graphs
    definition = await create(app, template_graph("brief_images", review=False))
    original = await finish(app, (await submit(app, definition)).id)
    assert not (
        await plan(manager, definition.id, "n_images", inputs={"brief": "different"})
    ).eligible
    await app.state.store.execute(
        (
            "INSERT INTO model_prefs(connection_id,model_id,params_json)"
            " VALUES(?,?,?) ON CONFLICT(connection_id,model_id) DO UPDATE SET"
            " params_json=excluded.params_json"
        ),
        (app.state.test_connection, "fake-chat", '{"temperature":0.7}'),
    )
    assert not (await plan(manager, definition.id, "n_images", original.id)).eligible


async def test_disabled_cleanup_needs_no_model_and_still_qualifies_saved_upstream(
    chat_app: Any,
) -> None:
    app, client, runtime = chat_app
    item = await record(app, client, "Synthetic original meeting.")
    graph = template_graph("meeting_pack", cleanup=False)
    assert graph.settings.default_model is None
    pack = next(node for node in graph.nodes if isinstance(node, GenerateNode))
    pack.config.model = ModelRef(connection_id=app.state.test_connection, model_id="fake-chat")
    manager = app.state.workflow_graphs
    definition = await manager.defs.create(
        DefCreate(name="Synthetic disabled cleanup", graph=graph)
    )
    run = await submit(app, definition, inputs={"recording": item["id"]})
    result = await finish(app, run.id)
    assert result.state == "complete"
    assert result.nodes["n_clean"].state == "skipped"
    assert len([c for c in runtime.state.captures if c.get("messages")]) == 1
    reuse = await plan(manager, definition.id, "n_pack", result.id)
    assert reuse.eligible and "n_clean" in reuse.node_ids


async def test_single_block_samples_and_saved_upstream_are_hidden_and_durable(
    chat_app: Any,
) -> None:
    app, _, runtime = chat_app
    manager = app.state.workflow_graphs
    definition = await create(app, template_graph("brief_images", review=False, seeds=[19]))
    tested = await manager.submit(
        definition.id,
        GraphSubmit(
            request_key="fake-sample-test",
            mode="test",
            node_id="n_draft",
            samples={"start.brief": "Synthetic blue square"},
        ),
    )
    result = await finish(app, tested.id)
    assert result.state == "complete" and result.mode == "test"
    assert result.nodes["n_draft"].attempt == 1
    assert result.nodes["n_images"].attempt == 0 and app.state.images.engine.calls == 0
    assert result.id not in {r.id for r in (await page(manager)).items}
    assert "Synthetic blue square" in runtime.state.captures[-1]["messages"][1]["content"]
    original = await finish(app, (await submit(app, definition)).id)
    tested2 = await manager.submit(
        definition.id,
        GraphSubmit(
            request_key="fake-image-test",
            mode="test",
            node_id="n_images",
            source_run_id=original.id,
        ),
    )
    result2 = await finish(app, tested2.id)
    assert (
        result2.nodes["n_draft"].reused_from == original.id
        and result2.nodes["n_save"].state == "skipped"
    )
    assert result2.id not in {r.id for r in (await page(manager)).items}
    await app.state.store.execute(
        "UPDATE workflow_graph_runs SET expires_at='2000-01-01' WHERE id=?", (result2.id,)
    )
    await page(manager)
    assert not await app.state.store.one(
        "SELECT id FROM workflow_graph_runs WHERE id=?", (result2.id,)
    )
    assert len(await app.state.images.list()) == 2


async def test_source_reuse_rebinds_typed_reference_and_refuses_changed_original(
    chat_app: Any,
) -> None:
    app, client, _ = chat_app
    item = await record(app, client, "Synthetic original speech.")
    definition = await create(app, template="meeting_pack")
    original = await finish(
        app, (await submit(app, definition, inputs={"recording": item["id"]})).id
    )
    manager = app.state.workflow_graphs
    assert (await plan(manager, definition.id, "n_pack")).eligible
    rerun = await manager.submit(
        definition.id,
        GraphSubmit(request_key="fake-source-reuse", node_id="n_pack", source_run_id=original.id),
    )
    result = await finish(app, rerun.id)
    assert result.nodes["n_transcript"].output["transcript"]["run_id"] == result.id
    sources = await app.state.store.rows(
        "SELECT source_json FROM workflow_graph_sources WHERE run_id=?", (result.id,)
    )
    assert json.loads(sources[0]["source_json"])["text"] == "Synthetic original speech."
    await app.state.store.execute(
        "UPDATE transcripts SET text='Changed original' WHERE attachment_id=?", (item["id"],)
    )
    assert not (await plan(manager, definition.id, "n_pack")).eligible


@pytest.mark.parametrize("kind", ["text", "image_list"])
async def test_pick_pauses_validates_selection_and_retries_decision_idempotently(
    chat_app: Any, kind: str
) -> None:
    app, _, _ = chat_app
    raw = template_graph("brief_images", review=False, seeds=[3, 4]).model_dump(by_alias=True)
    raw["nodes"].insert(
        -1,
        {
            "id": "n_pick",
            "key": "favorites",
            "kind": "pick",
            "title": "Pick favorites",
            "config": {
                "from": ["{{images.images}}" if kind == "image_list" else "{{draft.text}}"],
                "type": kind,
                "maximum": 1,
            },
        },
    )
    raw["edges"][-1]["target"] = "n_pick"
    raw["edges"].append({"id": "e_pick", "source": "n_pick", "target": "n_save"})
    raw["nodes"][-1]["config"]["include"] = [{"label": "Favorites", "ref": "{{favorites.chosen}}"}]
    definition = await create(app, GraphDoc.model_validate(raw))
    run = await finish(app, (await submit(app, definition)).id)
    assert run.state == "paused"
    with pytest.raises(AppError):
        await app.state.workflow_graphs.decision(
            run.id, Decision(node_id="n_pick", decision="approve", chosen=[99])
        )
    body = Decision(node_id="n_pick", decision="approve", chosen=[0])
    await app.state.workflow_graphs.decision(run.id, body)
    result = await finish(app, run.id)
    assert result.state == "complete"
    assert (await app.state.workflow_graphs.decision(run.id, body)).id == run.id
    value = result.results[0].items[0].value
    assert len(value) == 1 if kind == "image_list" else isinstance(value, str) and value


async def test_test_scope_does_not_call_unrelated_missing_models(chat_app: Any) -> None:
    app, _, runtime = chat_app
    raw = template_graph("brief_images", review=False).model_dump(by_alias=True)
    raw["nodes"].append(
        {
            "id": "n_unused",
            "key": "unused",
            "kind": "generate",
            "title": "Unconfigured later block",
            "config": {"prompt": "", "model": {"connection_id": "missing", "model_id": "missing"}},
        }
    )
    raw["edges"].append({"id": "e_unused", "source": "n_images", "target": "n_unused"})
    definition = await create(app, GraphDoc.model_validate(raw))
    run = await app.state.workflow_graphs.submit(
        definition.id,
        GraphSubmit(
            request_key="fake-scoped-test",
            mode="test",
            node_id="n_draft",
            samples={"start.brief": "Synthetic test scope"},
        ),
    )
    result = await finish(app, run.id)
    assert result.state == "complete" and result.nodes["n_unused"].attempt == 0
    assert len([c for c in runtime.state.captures if c.get("messages")]) == 1


async def test_explicit_samples_cannot_fabricate_media_or_mix_saved_and_sample_values(
    chat_app: Any,
) -> None:
    app, _, _ = chat_app
    definition = await create(app, template_graph("brief_images", review=False))
    with pytest.raises(AppError):
        await app.state.workflow_graphs.submit(
            definition.id,
            GraphSubmit(
                request_key="fake-mixed-test",
                mode="test",
                node_id="n_draft",
                source_run_id="fake-old",
                samples={"start.brief": "Fake"},
            ),
        )
    with pytest.raises(AppError):
        await app.state.workflow_graphs.submit(
            definition.id,
            GraphSubmit(
                request_key="fake-media-test",
                mode="test",
                node_id="n_save",
                samples={"images.images": [{"id": "fake-image"}], "images.prompt": "Fake"},
            ),
        )
    assert not await app.state.store.rows("SELECT * FROM workflow_graph_runs")


async def test_removed_image_prevents_downstream_reuse(chat_app: Any) -> None:
    app, _, _ = chat_app
    definition = await create(app, template_graph("brief_images", review=False))
    run = await finish(app, (await submit(app, definition)).id)
    assert (await plan(app.state.workflow_graphs, definition.id, "n_save")).eligible
    image = run.nodes["n_images"].output["images"][0]["id"]
    await app.state.images.remove(image)
    assert not (await plan(app.state.workflow_graphs, definition.id, "n_save")).eligible


def test_rebinding_source_pointers_never_rewrites_user_text_or_generated_fields() -> None:
    from app.workflows.reuse import rebind

    pointer = {
        "run_id": "old",
        "node_id": "n_transcript",
        "attachment_id": "fake",
        "source_sha256": "fake-sha",
    }
    assert rebind(pointer, "old", "new") == {**pointer, "run_id": "new"}
    generated = {**pointer, "text": "Literal old run_id in user-authored content"}
    assert rebind(generated, "old", "new") == generated
    assert rebind({"value": "old"}, "old", "new") == {"value": "old"}
