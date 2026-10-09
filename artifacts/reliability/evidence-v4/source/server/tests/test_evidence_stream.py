"""Raw selection data cannot enter the answer, even on cancellation/error."""

import json

import pytest

from app.providers.base import ChatRequest, Finish, ProviderMessage, ReasoningDelta, TextDelta
from app.providers.ollama import Ollama
from evals.reliability.contract_stream import install
from evals.reliability.evidence_contract import DECLINE, build


@pytest.mark.asyncio
async def test_only_validated_host_text_is_emitted_without_a_second_call(monkeypatch, tmp_path):
    calls = []
    raw = json.dumps({"coverage": "evidence", "selections": {"source_1": ["S1-P0-U0"]}})

    async def fake_stream(adapter, request):
        calls.append(request)
        yield ReasoningDelta("Unvalidated deliberation")
        for fragment in (raw[:30], raw[30:]):
            yield TextDelta(fragment)
        assert not delivered
        yield Finish("stop")

    monkeypatch.setattr(Ollama, "stream", fake_stream)
    install(str(tmp_path / "trace.jsonl"))
    request = ChatRequest(
        "fake",
        [ProviderMessage("system", "Original"), ProviderMessage("user", "Cedar cost?")],
        context_length=32768,
    )
    build(request, [{"n": 1, "passages": [{"text": "Cedar costs 7 dollars."}]}])
    delivered = []
    adapter = Ollama("isolated", "http://fake")
    try:
        async for event in adapter.stream(request):
            delivered.append(event)
    finally:
        await adapter.close()
    assert len(calls) == 1
    assert not any(isinstance(e, ReasoningDelta) for e in delivered)
    assert isinstance(delivered[0], TextDelta)
    assert "Cedar costs 7 dollars" in delivered[0].text and "selections" not in delivered[0].text
    assert calls[0].params == {}
    assert json.loads((tmp_path / "trace.jsonl").read_text())["outcome"]["verified_answer"] is False


@pytest.mark.asyncio
@pytest.mark.parametrize("ending", ["length", "error"])
async def test_incomplete_or_failed_stream_cannot_display_selected_facts(
    monkeypatch, tmp_path, ending
):
    async def fake_stream(adapter, request):
        yield TextDelta('{"coverage":"evidence","selections":{"source_1":["S1-P0-U0"]}}')
        yield Finish(ending)

    monkeypatch.setattr(Ollama, "stream", fake_stream)
    install(str(tmp_path / "trace.jsonl"))
    request = ChatRequest(
        "fake", [ProviderMessage("system", "Original"), ProviderMessage("user", "Cedar cost?")]
    )
    build(request, [{"n": 1, "passages": [{"text": "Cedar costs 7 dollars."}]}])
    adapter = Ollama("isolated", "http://fake")
    try:
        events = [event async for event in adapter.stream(request)]
    finally:
        await adapter.close()
    texts = [e.text for e in events if isinstance(e, TextDelta)]
    assert texts == ([DECLINE] if ending == "length" else [])
