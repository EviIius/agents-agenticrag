"""Reconnect snapshots preserve actual text/progress, independent of timers."""

import asyncio
import json
from typing import Any

from app.workflows.views import stream
from tests.test_workflow_graph_engine import create, finish, submit


async def test_snapshot_contains_cumulative_text_and_actual_progress(chat_app: Any) -> None:
    app, _, _ = chat_app
    manager = app.state.workflow_graphs
    definition = await create(app)
    run = await submit(app, definition)
    await finish(app, run.id)
    await app.state.store.execute(
        "UPDATE workflow_graph_steps SET state='running' WHERE run_id=? AND node_id='n_draft'",
        (run.id,),
    )
    await manager.ephemeral(
        "node.text",
        {
            "run_id": run.id,
            "node_id": "n_draft",
            "delta": "tail",
            "text": "Synthetic prefix and tail",
        },
    )
    await manager.ephemeral(
        "node.progress",
        {
            "run_id": run.id,
            "node_id": "n_draft",
            "done": 2,
            "total": 4,
            "label": "Synthetic actual progress",
        },
    )
    snapshot = await manager.get(run.id)
    assert snapshot.nodes["n_draft"].output["text"] == "Synthetic prefix and tail"
    assert snapshot.nodes["n_draft"].progress == {
        "done": 2,
        "total": 4,
        "label": "Synthetic actual progress",
    }
    reader = stream(manager, "0:1")
    initial = await anext(reader)
    saved = json.loads(initial["data"])["items"][0]
    assert saved["nodes"]["n_draft"]["output"]["text"] == "Synthetic prefix and tail"
    latest = await app.state.store.one("SELECT MAX(id) n FROM workflow_graph_events")
    assert initial["id"] == f"0:{latest['n']}"
    await reader.aclose()
    assert not manager.listeners
    await app.state.store.execute(
        "UPDATE workflow_graph_steps SET state='complete' WHERE run_id=? AND node_id='n_draft'",
        (run.id,),
    )
    assert (await manager.get(run.id)).nodes["n_draft"].output[
        "text"
    ] != "Synthetic prefix and tail"


async def test_restart_keeps_durable_partial_and_clears_ephemeral_projections(
    chat_app: Any,
) -> None:
    from app.workflows.engine import GraphRunner

    app, _, _ = chat_app
    definition = await create(app)
    run = await submit(app, definition)
    await finish(app, run.id)
    await app.state.store.execute(
        "UPDATE workflow_graph_runs SET state='running' WHERE id=?", (run.id,)
    )
    await app.state.store.execute(
        "UPDATE workflow_graph_steps SET state='running',output_json=?"
        " WHERE run_id=? AND node_id='n_draft'",
        (json.dumps({"text": "Durable synthetic partial"}), run.id),
    )
    replacement = GraphRunner(app.state.store, app.state.workflows)
    await replacement.recover()
    saved = await replacement.get(run.id)
    assert saved.state == "interrupted"
    assert saved.nodes["n_draft"].state == "interrupted"
    assert saved.nodes["n_draft"].output == {"text": "Durable synthetic partial"}
    assert saved.nodes["n_draft"].progress is None
    await replacement.close()
    await asyncio.sleep(0)


async def test_paused_summary_includes_runs_beyond_the_latest_fifty(chat_app: Any) -> None:
    from app.workflows.graph_schemas import DefCreate, GraphSubmit
    from app.workflows.views import page

    app, _, _ = chat_app
    manager = app.state.workflow_graphs
    definition = await create(app)
    paused = await finish(app, (await submit(app, definition)).id)
    assert paused.state == "paused"
    blank = await manager.defs.create(DefCreate(name="Synthetic history row"))
    for index in range(51):
        fresh = await manager.submit(blank.id, GraphSubmit(request_key=f"fake-history-{index}"))
        await finish(app, fresh.id)
    first = await page(manager)
    assert len(first.items) == 50 and all(run.id != paused.id for run in first.items)
    assert first.paused_count == 1
    second = await page(manager, cursor=first.next_cursor)
    assert len(second.items) == 2 and any(run.id == paused.id for run in second.items)
    reader = stream(manager, "0:0")
    assert json.loads((await anext(reader))["data"])["paused_count"] == 1
    await reader.aclose()
