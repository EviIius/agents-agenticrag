"""Named-field contract stage/stream boundaries; no native calls or private data."""

import json
from collections.abc import AsyncIterator
from pathlib import Path

import pytest

from app.providers.base import ChatRequest, Finish, ProviderEvent, ProviderMessage, TextDelta
from app.providers.ollama import Ollama
from evals.reliability import run_contract_v14 as driver
from evals.reliability.contract_stream_v14 import install
from evals.reliability.evidence_object_v14 import build


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "raw,finish",
    [
        ('{"coverage":"evidence","selections":{"S99":{}}}', "stop"),
        ('{"coverage":"unsupported","selections":{}}', "length"),
    ],
)
async def test_rejected_object_emits_nothing_and_blocks_next_call(
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
    emitted = []
    adapter = Ollama("test", "http://fake")
    try:
        with pytest.raises(SystemExit, match="trial stopped automatically"):
            async for event in adapter.stream(request):
                emitted.append(event)
        with pytest.raises(SystemExit, match="next model call prohibited"):
            async for event in adapter.stream(ChatRequest("fake", [])):
                emitted.append(event)
    finally:
        await adapter.close()
    assert not emitted and len(calls) == 1 and calls[0].params == {}
    retained = json.loads(trace.read_text())
    assert retained["protocol_stopped"] and retained["outcome"]["status"] == "rejected"
    assert retained["raw_events"][0]["value"]["text"] == raw


@pytest.mark.parametrize("missing", ["protocol_pass", "rubric_pass", "semantic_pass"])
def test_remainder_cannot_run_without_all_smoke_gates(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, missing: str
) -> None:
    monkeypatch.setattr(driver, "FOLDER", tmp_path)
    review = {"protocol_pass": True, "rubric_pass": True, "semantic_pass": True}
    review[missing] = False
    (tmp_path / "smoke-review.json").write_text(json.dumps(review))
    with pytest.raises(RuntimeError, match="subsequent stages prohibited"):
        driver.check_gate("remaining-web")


def test_library_requires_web_review_separately(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(driver, "FOLDER", tmp_path)
    (tmp_path / "smoke-review.json").write_text(
        json.dumps({"protocol_pass": True, "rubric_pass": True, "semantic_pass": True})
    )
    driver.check_gate("remaining-web")
    (tmp_path / "web-review.json").write_text(json.dumps({"all_release_and_semantic_gates": False}))
    with pytest.raises(RuntimeError, match="Library prohibited"):
        driver.check_gate("library")
