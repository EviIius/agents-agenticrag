"""Actual missing-reference scope failure and source/ambiguity counterexamples."""

import json

import pytest
from test_fallback import ROOT, contract, material, planned


def comparison():
    return material(
        "assistant_response",
        "Celadon weighs 7 kilograms. Brindle weighs 9 kilograms.",
        "1",
        "seed-history-06-1",
    )


async def test_actual_null_reference_comparison_replay_binds_original_material(monkeypatch):
    prior = ROOT / "artifacts/images-i1/search-abstention-retest/boundary-candidate-history-06"
    trace = next(
        json.loads(line)
        for line in (prior / "trace.jsonl").read_text().splitlines()
        if json.loads(line)["payload"].get("format") is not None
    )
    raw = json.loads(
        "".join(e["value"]["text"] for e in trace["events"] if e["type"] == "TextDelta")
    )
    assert raw["task"] == "transform" and raw["input_ref"] is None
    supplied = comparison()
    assert supplied.ref in trace["payload"]["messages"][-1]["content"]
    token = contract.CURRENT_TURN.set("2")
    try:
        result, fallback, state = await planned(
            monkeypatch, "Summarize only that provided comparison.", [supplied], raw
        )
    finally:
        contract.CURRENT_TURN.reset(token)
    assert not result.search and fallback and state["mode"] == "local"
    assert state["refs"] == [supplied.ref] and not state["native_reference_valid"]


@pytest.mark.parametrize(
    "question",
    [
        "Summarize only that provided comparison.",
        "Summarize just that provided comparison.",
        "Please summarize only that comparison in one sentence.",
        "Shorten just your previous response.",
    ],
)
def test_complete_scoped_history_targets(question):
    assert contract.local_target(question, [comparison()]) == (comparison(),)


@pytest.mark.parametrize(
    "question,expected",
    [
        ("Translate only bonjour into English.", "bonjour"),
        ("Translate just ciao mondo into English.", "ciao mondo"),
        ("Rewrite only 'Provided text' more politely.", "Provided text"),
        ("Rewrite just these words 'Hello' more politely.", "Hello"),
        (
            "Summarize only this text: Two fictional devices weigh 7 and 9 kilograms.",
            "Two fictional devices weigh 7 and 9 kilograms.",
        ),
    ],
)
def test_scope_inventory_and_binding_agree_without_invented_material(question, expected):
    from types import SimpleNamespace

    message = SimpleNamespace(id="synthetic", role="user", content=question)
    inputs = contract.text_materials([message], question)
    target = contract.local_target(question, inputs)
    assert len(target) == 1 and target[0].text == expected
    assert target[0] in inputs


@pytest.mark.parametrize(
    "question",
    [
        "Summarize only if that comparison is current.",
        "Summarize only when that comparison is ready.",
        "Summarize just after that comparison is approved.",
        "Summarize only just that comparison.",
        "Summarize only the missing report.",
        "Summarize only https://example.org/report.",
        "Summarize only the document named 'Report'.",
        "Summarize only that comparison and verify which device is current.",
        "Summarize only that comparison and look up its release date.",
        "Translate only if bonjour is supplied into English.",
    ],
)
def test_scope_does_not_make_conditions_resources_or_external_checks_local(question):
    assert not contract.local_target(question, [comparison()])


def test_unavailable_response_and_dropped_material_are_not_supplied_comparison():
    refusal = material("assistant_response", "The file text has not been supplied.", "1")
    assert not contract.local_target("Summarize only that provided comparison.", [refusal])
    assert not contract.local_target("Summarize only that provided comparison.", [])
    assert contract.local_target("Rewrite only your previous refusal politely.", [refusal]) == (
        refusal,
    )


def test_scope_does_not_collapse_ambiguous_actual_attachments():
    one = material("document", "First actual document.", source="one")
    two = material("document", "Second actual document.", source="two")
    assert not contract.local_target("Summarize only the attached document.", [one, two])
    assert set(contract.local_target("Summarize only the attached documents.", [one, two])) == {
        one,
        two,
    }


async def test_force_search_mixed_check_and_missing_resource_preserved(monkeypatch):
    result, fallback, _ = await planned(
        monkeypatch, "Summarize only that provided comparison.", [comparison()], force=True
    )
    assert result.search and fallback
    result, fallback, state = await planned(
        monkeypatch, "Summarize only that comparison and verify the release date.", [comparison()]
    )
    assert result.search and fallback and state["mode"] == "lookup"
    result, fallback, state = await planned(monkeypatch, "Summarize only the missing report.", [])
    assert result.search and fallback and state["mode"] == "lookup"


async def test_scope_keeps_true_ambiguity_clarification(monkeypatch):
    inputs = [
        material("document", "One file.", source="one"),
        material("document", "Another file.", source="two"),
    ]
    result, fallback, state = await planned(
        monkeypatch, "Summarize only the attached document.", inputs
    )
    assert not result.search and fallback and state["mode"] == "clarify"
