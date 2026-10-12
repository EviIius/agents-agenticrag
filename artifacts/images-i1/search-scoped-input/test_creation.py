"""Replay actual native code failure; test missing-source and edit boundaries."""

import json

import pytest
from test_fallback import ROOT, contract, material, planned


@pytest.mark.parametrize(
    "text",
    [
        "Write a Python function that adds two numbers.",
        "Create a JavaScript function that multiplies two numbers.",
        "Please generate a short original story about an imaginary lighthouse.",
        "Create a Python function that returns the string 'latest release'.",
        "Write a two-line poem about moonlight.",
    ],
)
def test_self_contained_new_artifacts(text):
    assert contract.self_contained_creation(text)


@pytest.mark.parametrize(
    "text",
    [
        "Rewrite: def add(a, b): return a + b",
        "Rewrite the code in the utility script.",
        "Create a Python function based on the current documentation for the API.",
        "Write a Python function and verify whether the observatory opened in 2034.",
        "Write a short story based on the attached report.",
        "Write a script using the existing code.",
        "Write a function using this file.",
        "Write an essay about a public figure.",
        "Create a report about admission prices.",
        "Write a Python function: also search for its documented API endpoint.",
        "Write a function from https://example.org/code.",
        "Write a function that retrieves the latest published measurement.",
    ],
)
def test_edits_external_sources_and_factual_tails_are_not_creation_exemptions(text):
    assert not contract.self_contained_creation(text)


def native():
    return {
        "task": "transform",
        "queries": [],
        "freshness": "any",
        "selection_condition": None,
        "input_ref": None,
    }


async def test_actual_retained_new_code_plan_is_local(monkeypatch):
    prior = ROOT / "artifacts/images-i1/search-conversation-guard/ordinary-candidate-social-06"
    trace = next(
        json.loads(line)
        for line in (prior / "trace.jsonl").read_text().splitlines()
        if json.loads(line)["payload"].get("format") is not None
    )
    raw = json.loads(
        "".join(e["value"]["text"] for e in trace["events"] if e["type"] == "TextDelta")
    )
    assert raw == native()
    result, fallback, state = await planned(
        monkeypatch, "Write a Python function that adds two numbers.", [], raw
    )
    assert not result.search and fallback and state["mode"] == "create_local"
    assert state["refs"] == []


async def test_new_code_does_not_bind_unrelated_history(monkeypatch):
    result, fallback, state = await planned(
        monkeypatch,
        "Write a Python function that adds two numbers.",
        [material("assistant_response", "The port has three gates.")],
        native(),
    )
    assert not result.search and fallback and state["mode"] == "create_local"
    assert state["refs"] == []


async def test_actual_code_edit_remains_bound(monkeypatch):
    body = material("body", "def add(a, b): return a + b")
    result, fallback, state = await planned(
        monkeypatch, "Rewrite: def add(a, b): return a + b", [body], native()
    )
    assert not result.search and fallback and state["mode"] == "local"
    assert state["refs"] == [body.ref]


@pytest.mark.parametrize("task", ["transform", "creative", "calculate", "conversation"])
async def test_creation_with_external_evidence_cannot_skip_lookup(monkeypatch, task):
    raw = {**native(), "task": task}
    result, fallback, state = await planned(
        monkeypatch,
        "Write a Python function and verify whether the observatory opened in 2034.",
        [],
        raw,
    )
    assert result.search and fallback and state["mode"] == "lookup"


async def test_force_search_and_invalid_query_remain_enforced(monkeypatch):
    result, fallback, _ = await planned(
        monkeypatch, "Write a Python function that adds two numbers.", [], native(), force=True
    )
    assert result.search and fallback
    result, fallback, _ = await planned(
        monkeypatch,
        "Write a Python function that adds two numbers.",
        [],
        {**native(), "queries": ["unexpected lookup"]},
    )
    assert result.search and fallback


async def test_invalid_creation_reference_is_not_accepted(monkeypatch):
    result, fallback, state = await planned(
        monkeypatch,
        "Write a Python function that adds two numbers.",
        [],
        {**native(), "input_ref": {"ref": "invented", "quote": "not provided"}},
    )
    assert result.search and fallback and state["mode"] == "lookup"
