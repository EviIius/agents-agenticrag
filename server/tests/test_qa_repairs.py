"""Regression evidence for the pasted QA review; synthetic data and fake runtimes."""

from pathlib import Path
from typing import Any

import pytest

from app.errors import AppError
from app.providers.base import ChatRequest, ProviderMessage
from app.providers.ollama import Ollama
from app.schemas import ModelInfo, ReasoningCaps
from app.workflows.blocks import checked_inputs
from app.workflows.graph import GraphDoc
from app.workflows.graph_schemas import DefCreate
from tests.test_workflow_graph_engine import finish


def document_graph() -> GraphDoc:
    return GraphDoc.model_validate(
        {
            "schema": "atelier.workflow/1",
            "nodes": [
                {
                    "id": "start",
                    "key": "start",
                    "kind": "start",
                    "title": "Start",
                    "config": {
                        "fields": [
                            {
                                "name": "document",
                                "label": "Document",
                                "type": "document",
                                "required": True,
                            }
                        ]
                    },
                },
                {
                    "id": "save",
                    "key": "save",
                    "kind": "output",
                    "title": "Save results",
                    "config": {
                        "include": [{"label": "Document reference", "ref": "{{start.document}}"}]
                    },
                },
            ],
            "edges": [{"id": "start_save", "source": "start", "target": "save"}],
        }
    )


@pytest.mark.parametrize("level", ["high", "unknown"])
async def test_invalid_explicit_thinking_never_becomes_off(level: str) -> None:
    adapter = Ollama("fake", "http://fake")
    adapter.models["fake-levels"] = ModelInfo(
        connection_id="fake",
        model_id="fake-levels",
        display_name="Fake levels",
        reasoning=ReasoningCaps(options=["off", "low", "medium", "xhigh"], default="medium"),
    )
    try:
        with pytest.raises(AppError) as caught:
            adapter.payload(
                ChatRequest("fake-levels", [ProviderMessage("user", "Synthetic")], reasoning=level)
            )
        assert caught.value.code == "reasoning_unsupported"
    finally:
        await adapter.close()


async def test_invalid_thinking_rejects_before_saving_or_starting_answer(chat_app: Any) -> None:
    app, client, runtime = chat_app
    chat = (
        await client.post(
            "/api/chats",
            json={
                "connection_id": app.state.test_connection,
                "model_id": "fake-reasoning",
            },
        )
    ).json()
    assert (
        await client.patch(f"/api/chats/{chat['id']}", json={"params": {"reasoning": "high"}})
    ).status_code == 200
    before = len([c for c in runtime.state.captures if c.get("messages")])
    response = await client.post(
        f"/api/chats/{chat['id']}/messages", json={"content": "Synthetic question"}
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "reasoning_unsupported"
    assert (await client.get(f"/api/chats/{chat['id']}")).json()["messages"] == []
    assert len([c for c in runtime.state.captures if c.get("messages")]) == before


@pytest.mark.parametrize("name", ["two-pages.pdf", "table.docx"])
async def test_extracted_document_start_input_runs_end_to_end(chat_app: Any, name: str) -> None:
    app, client, runtime = chat_app
    response = await client.post(
        "/api/attachments",
        files={"file": (name, (Path(__file__).parent / "fixtures/documents" / name).read_bytes())},
    )
    assert response.status_code == 201
    item = response.json()
    assert item["kind"] == "text" and item["document"]
    graph = document_graph()
    definition = await app.state.workflow_graphs.defs.create(
        DefCreate(name="Synthetic document workflow", graph=graph)
    )
    response = await client.post(
        f"/api/workflows/defs/{definition.id}/runs",
        json={
            "request_key": "synthetic-document-" + name.replace(".", "-"),
            "inputs": {"document": item["id"]},
        },
    )
    assert response.status_code == 202, response.text
    run = await finish(app, response.json()["id"])
    assert run.state == "complete"
    assert run.results[0].items[0].value == item["id"]
    assert not [c for c in runtime.state.captures if c.get("messages")]


async def test_document_start_rejects_plain_text_without_document_metadata(chat_app: Any) -> None:
    app, client, _ = chat_app
    item = (
        await client.post(
            "/api/attachments", files={"file": ("synthetic.txt", b"Synthetic plain text")}
        )
    ).json()
    with pytest.raises(AppError, match="file type"):
        await checked_inputs(app.state.workflow_graphs, document_graph(), {"document": item["id"]})


@pytest.mark.parametrize("level", [None, "off", "low", "medium", "xhigh"])
async def test_supported_thinking_preserves_exact_wire_values_and_default_omission(
    level: str | None,
) -> None:
    adapter = Ollama("fake", "http://fake")
    adapter.models["fake-levels"] = ModelInfo(
        connection_id="fake",
        model_id="fake-levels",
        display_name="Fake levels",
        reasoning=ReasoningCaps(options=["off", "low", "medium", "xhigh"], default="medium"),
    )
    try:
        payload = adapter.payload(
            ChatRequest("fake-levels", [ProviderMessage("user", "Synthetic")], reasoning=level)
        )
        if level is None:
            assert "think" not in payload
        else:
            assert payload["think"] == (False if level == "off" else level)
        assert "options" not in payload
    finally:
        await adapter.close()


async def test_invalid_saved_thinking_does_not_overwrite_preferences(chat_app: Any) -> None:
    app, client, _ = chat_app
    body = {
        "connection_id": app.state.test_connection,
        "model_id": "fake-reasoning",
        "params": {"reasoning": "off"},
    }
    assert (await client.put("/api/models/prefs", json=body)).status_code == 200
    body["params"] = {"reasoning": "high"}
    assert (await client.put("/api/models/prefs", json=body)).status_code == 422
    model = next(
        m for m in (await client.get("/api/models")).json() if m["model_id"] == "fake-reasoning"
    )
    assert model["params_defaults"] == {"reasoning": "off"}


async def test_hidden_embedding_eject_keeps_library_configuration_and_visibility(
    chat_app: Any,
) -> None:
    app, client, runtime = chat_app
    runtime.state.loaded["fake-embedding"] = 8192
    body = {"connection_id": app.state.test_connection, "model_id": "fake-embedding"}
    assert (await client.put("/api/models/prefs", json={**body, "hidden": True})).status_code == 200
    before = (await client.get("/api/bootstrap")).json()["settings"]
    response = await client.post("/api/models/unload", json=body)
    assert response.status_code == 200
    all_models = (await client.get("/api/models?include_hidden=true&refresh=true")).json()
    model = next(m for m in all_models if m["model_id"] == "fake-embedding")
    assert (
        model["hidden"] and not model["loaded"] and model["embedding"] and not model["chat_capable"]
    )
    assert (await client.get("/api/bootstrap")).json()["settings"] == before
    assert "fake-chat" in runtime.state.loaded
    assert not [c for c in runtime.state.captures if c.get("messages")]
