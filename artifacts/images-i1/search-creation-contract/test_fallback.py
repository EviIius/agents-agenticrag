"""Offline policy checks, including the actual retained null-reference failure."""

import asyncio
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "server"), str(Path(__file__).parent)]
import contract  # noqa: E402
from app.providers.base import ChatRequest, ProviderMessage  # noqa: E402


def material(kind, text, position="0", source="synthetic"):
    return contract.Material.create(source, kind, text, position)


@pytest.mark.parametrize(
    "question,kind,text",
    [
        ("Translate bonjour into English.", "literal", "bonjour"),
        ("Translate ciao mondo into English.", "literal", "ciao mondo"),
        (
            "Rewrite 'Visit https://example.org/doc' more politely.",
            "quote",
            "Visit https://example.org/doc",
        ),
        ("Shorten: The depot closes at six.", "body", "The depot closes at six."),
        ("Translate the following into French: Good morning.", "body", "Good morning."),
        (
            "Rewrite 'Verify this: a quoted instruction' more politely.",
            "quote",
            "Verify this: a quoted instruction",
        ),
        (
            "Summarize the attached document in one sentence.",
            "document",
            "The depot has six doors.",
        ),
        (
            "Summarize the attached transcript in one sentence.",
            "transcript",
            "We approved four tasks.",
        ),
    ],
)
def test_complete_explicit_input_binding(question, kind, text):
    supplied = material(kind, text)
    assert contract.local_target(question, (supplied,)) == (supplied,)


@pytest.mark.parametrize(
    "question",
    [
        "Summarize the page about the Alpine Report.",
        "Summarize https://example.org/report.",
        "Summarize the document named 'Alpine Report'.",
        "Translate the report into French.",
        "Rewrite 'Supplied text' and verify when the site opened.",
        "Summarize this text and verify the opening year: Supplied text",
    ],
)
def test_resource_names_and_mixed_actions_are_not_literal_exemptions(question):
    inputs = (material("quote", "Alpine Report"), material("body", "Supplied text"))
    assert not contract.local_target(question, inputs)


def test_real_history_target_and_absence():
    answer = material("assistant_response", "The lab has six benches.", "1")
    assert contract.local_target("Summarize that inventory note in one sentence.", [answer]) == (
        answer,
    )
    note = material("body", "The depot opens at nine.", "0")
    ack = material("assistant_response", "I have the note.", "1")
    assert contract.local_target("Turn that note into two bullet points.", [note, ack]) == (note,)
    refusal = material("assistant_response", "The file text has not been supplied.", "1")
    assert not contract.local_target("Then summarize it now.", [refusal])
    assert contract.local_target("Rewrite your previous refusal more politely.", [refusal]) == (
        refusal,
    )


def test_no_stale_dropped_or_ambiguous_attachment_binding():
    one, two = (
        material("document", "One document.", source="one"),
        material("document", "Another document.", source="two"),
    )
    assert not contract.local_target("Summarize the attached document.", [one, two])
    assert set(contract.local_target("Summarize the attached documents.", [one, two])) == {one, two}
    token = contract.CURRENT_TURN.set("1")
    try:
        assert not contract.local_target("Summarize the attached document.", [one])
    finally:
        contract.CURRENT_TURN.reset(token)
    assert not contract.local_target("Translate bonjour into English.", [])


async def planned(monkeypatch, question, inputs, raw=None, force=False, error=None):
    requests = []
    state = {}

    class Adapter:
        async def complete_json(self, request):
            requests.append(request)
            if error:
                raise error
            return raw or {
                "task": "transform",
                "input_ref": None,
                "queries": [],
                "freshness": "any",
                "selection_condition": None,
            }

    monkeypatch.setattr(contract.planner, "schema", contract.schema)
    token, decision = contract.MATERIALS.set(tuple(inputs)), contract.DECISION.set(state)
    try:
        result, fallback = await contract.plan(
            Adapter(), "synthetic", question, [], True, 16384, force
        )
        assert len(requests) == 1
        assert requests[0].params == {"temperature": 0.2, "max_tokens": 256}
        assert requests[0].reasoning == "off"
        return result, fallback, state
    finally:
        contract.MATERIALS.reset(token)
        contract.DECISION.reset(decision)


async def test_retained_native_failure_resolves_real_literal(monkeypatch):
    previous = (
        ROOT
        / "artifacts/images-i1/search-input-contract/boundary-candidate-transform-01/trace.jsonl"
    )
    trace = next(
        json.loads(line)
        for line in previous.read_text().splitlines()
        if json.loads(line)["payload"].get("format") is not None
    )
    raw = json.loads(
        "".join(e["value"]["text"] for e in trace["events"] if e["type"] == "TextDelta")
    )
    supplied = material("literal", "bonjour")
    result, fallback, state = await planned(
        monkeypatch, "Translate bonjour into English.", [supplied], raw
    )
    assert not result.search and fallback
    assert state == {
        "mode": "local",
        "reason": "explicit supplied input",
        "refs": [supplied.ref],
        "native_reference_valid": False,
    }


async def test_invalid_reference_is_rejected_even_when_host_can_bind(monkeypatch):
    supplied = material("literal", "hola")
    raw = {
        "task": "transform",
        "input_ref": {"ref": "invented", "quote": "invented"},
        "queries": [],
        "freshness": "any",
        "selection_condition": None,
    }
    with pytest.raises(ValueError):
        contract.verified_input(raw["input_ref"], [supplied])
    result, fallback, state = await planned(
        monkeypatch, "Translate hola into English.", [supplied], raw
    )
    assert not result.search and fallback and state["refs"] == [supplied.ref]
    assert state["native_reference_valid"] is False


async def test_invalid_transform_of_absent_resource_keeps_lookup(monkeypatch):
    result, fallback, state = await planned(
        monkeypatch, "Summarize the page about an external report.", []
    )
    assert result.search and fallback and state["mode"] == "lookup"


async def test_ambiguous_target_clarifies_without_search(monkeypatch):
    result, fallback, state = await planned(
        monkeypatch, "Summarize the report.", [material("body", "Unrelated supplied text.")]
    )
    assert not result.search and fallback and state["mode"] == "clarify"


async def test_mixed_request_still_looks_up_even_with_valid_reference(monkeypatch):
    supplied = material("body", "It houses a telescope.")
    raw = {
        "task": "transform",
        "input_ref": {"ref": supplied.ref, "quote": supplied.text},
        "queries": [],
        "freshness": "any",
        "selection_condition": None,
    }
    result, fallback, state = await planned(
        monkeypatch,
        "Summarize this sentence and verify the opening year: It houses a telescope.",
        [supplied],
        raw,
    )
    assert result.search and fallback and state["mode"] == "lookup"


async def test_force_is_preserved_and_provider_failure_does_not_add_calls(monkeypatch):
    inputs = [material("literal", "hola")]
    result, fallback, _ = await planned(
        monkeypatch, "Translate hola into English.", inputs, force=True
    )
    assert result.search and fallback
    result, fallback, _ = await planned(
        monkeypatch, "Translate hola into English.", inputs, error=TimeoutError()
    )
    assert not result.search and fallback


async def test_clarification_is_an_existing_answer_instruction(monkeypatch, tmp_path):
    # Exercise the real installation wrapper against a synthetic pipeline/context.
    class Pipeline:
        def __init__(self):
            self.manager = SimpleNamespace(data_dir=tmp_path / "workbench-eval-synthetic")

        async def __call__(self, run, request, context, force):
            contract.record("clarify", "synthetic ambiguity")

    async def inventory(*args):
        return ()

    monkeypatch.setattr(contract, "inventory", inventory)
    for name in ("plan", "schema", "SCHEMA"):
        monkeypatch.setattr(contract.planner, name, getattr(contract.planner, name))
    contract.install(Pipeline)
    request = ChatRequest(
        "synthetic",
        [
            ProviderMessage("system", "Original instructions"),
            ProviderMessage("user", "Summarize that."),
        ],
        {},
        16384,
    )
    before = request.messages[-1].content
    await Pipeline()(None, request, SimpleNamespace(messages=request.messages), False)
    assert request.params == {} and request.messages[-1].content == before
    assert request.messages[1].content == contract.CLARIFY_PROMPT
    assert contract.DECISION.get() is None and contract.CURRENT_TURN.get() is None


async def test_context_state_is_independent_between_tasks():
    async def worker(ref):
        token = contract.DECISION.set({"mode": ref})
        await asyncio.sleep(0)
        try:
            return contract.DECISION.get()["mode"]
        finally:
            contract.DECISION.reset(token)

    assert await asyncio.gather(worker("one"), worker("two")) == ["one", "two"]
