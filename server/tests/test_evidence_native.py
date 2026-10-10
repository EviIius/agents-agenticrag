"""Host provenance accounting and fail-fast evaluation, without native calls."""

import json
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any

import pytest

from app.providers.base import ChatRequest, Finish, ProviderEvent, ProviderMessage, TextDelta
from app.providers.ollama import Ollama
from evals.reliability.contract_stream_v13 import install
from evals.reliability.evidence_contract_v13 import build, catalog, render

NOTE = (
    "Host selection: 1 supported rows match Value gt 0. "
    "Missing values were not treated as zero. "
    "Host reference is the citation label for each selected row."
)


def source(**changes: Any) -> dict[str, Any]:
    passage = {
        "heading": "Invented Fern measurements",
        "text": NOTE + "\n\n| Item | Value | Host reference |\n"
        "| --- | --- | --- |\n| Fern | Value: 7 | [1] |",
        "selection_applied": True,
        **changes,
    }
    return {"n": 1, "passages": [passage]}


def row_selection(available: Any) -> str:
    unit = next(u for u in available.units["source_1"] if u["kind"] == "row")
    return json.dumps(
        {"coverage": "evidence", "selections": [{"id": unit["id"], "columns": [0, 1]}]}
    )


def test_trusted_host_metadata_is_visible_but_not_source_quotation_or_selectable_fact() -> None:
    available = catalog([source()])
    outcome = render(row_selection(available), available)
    assert outcome["status"] == "evidence"
    assert NOTE in outcome["content"] and "Fern | Value: 7" in outcome["content"]
    assert not outcome["verified_answer"]
    assert all(
        u["kind"] == "fragment" for u in available.units["source_1"] if u.get("host_metadata")
    )
    assert available.sources["source_1"]["passages"][0]["text"].startswith(NOTE)


@pytest.mark.parametrize("flag", [False, None, "true", 1])
def test_page_prefix_without_boolean_host_provenance_cannot_exempt_quotation(flag: Any) -> None:
    available = catalog([source(selection_applied=flag)])
    assert render(row_selection(available), available)["status"] == "rejected"


def test_wrong_reference_and_unrecognized_generated_prefix_do_not_authenticate() -> None:
    for text in (
        source()["passages"][0]["text"].replace("[1]", "[2]"),
        source()["passages"][0]["text"].replace("were not", "were"),
    ):
        available = catalog([source(text=text)])
        assert render(row_selection(available), available)["status"] == "rejected"


def test_source_definition_and_heading_remain_charged_even_with_host_flag() -> None:
    text = source()["passages"][0]["text"].replace(
        NOTE, NOTE + " Source definition: " + " ".join(["Invented"] * 26)
    )
    available = catalog([source(text=text)])
    assert render(row_selection(available), available)["status"] == "rejected"
    available = catalog([source(heading=NOTE)])
    assert render(row_selection(available), available)["status"] == "rejected"


def test_v13_still_requires_named_subject_after_ordinal() -> None:
    available = catalog(
        [
            {
                "n": 1,
                "passages": [{"text": "| | Item | Value |\n| --- | --- | --- |\n| 1 | Fern | 7 |"}],
            }
        ]
    )
    unit = available.units["source_1"][0]
    raw = json.dumps(
        {"coverage": "evidence", "selections": [{"id": unit["id"], "columns": [0, 2]}]}
    )
    assert render(raw, available)["status"] == "rejected"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "raw,finish",
    [
        ('{"coverage":"evidence","selections":[{"id":"S99","columns":[]}]}', "stop"),
        ('{"coverage":"unsupported","selections":[]}', "length"),
    ],
)
async def test_invalid_protocol_retains_trace_and_blocks_every_next_model_call(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, raw: str, finish: str
) -> None:
    calls = []

    async def fake(adapter: Ollama, request: ChatRequest) -> AsyncIterator[ProviderEvent]:
        calls.append(request)
        yield TextDelta(raw)
        yield Finish(finish)  # type: ignore[arg-type]

    monkeypatch.setattr(Ollama, "stream", fake)
    trace = tmp_path / "trace.jsonl"
    install(str(trace))
    request = ChatRequest(
        "fake", [ProviderMessage("system", "Original"), ProviderMessage("user", "Fern?")]
    )
    build(request, [{"n": 1, "passages": [{"text": "Fern costs 7 dollars."}]}])
    adapter = Ollama("test", "http://fake")
    try:
        with pytest.raises(SystemExit, match="trial stopped automatically"):
            assert not [e async for e in adapter.stream(request)]
        ordinary = ChatRequest("fake", [ProviderMessage("user", "Hello")])
        with pytest.raises(SystemExit, match="next model call prohibited"):
            assert not [e async for e in adapter.stream(ordinary)]
    finally:
        await adapter.close()
    assert len(calls) == 1
    retained = json.loads(trace.read_text())
    assert retained["protocol_stopped"] and retained["outcome"]["status"] == "rejected"
    assert retained["raw_events"][0]["value"]["text"] == raw
    assert calls[0].params == {}
