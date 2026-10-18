"""G9 zero-inference transport replay; no new factual-answer qualification."""

import hashlib
import json
import types
from pathlib import Path
from typing import Any

import httpx

from app.providers.base import ChatRequest, ProviderMessage
from app.providers.ollama import Ollama
from app.schemas import Source
from app.search.prompt import build

ROOT = Path(__file__).resolve().parents[2]


async def test_25_saved_web_cases_have_identical_payloads_and_answer_events() -> None:
    file = ROOT / "server/tests/fixtures/agent/ollama-main-e7ffea2b.py.txt"
    assert (
        hashlib.sha256(file.read_bytes()).hexdigest()
        == "d44b20a4a82297dc8d26afe0a77ef6409e2ff2db8598621aebd9bb2d141a6488"
    )
    module = types.ModuleType("app.providers.n0_previous")
    module.__package__ = "app.providers"
    exec(compile(file.read_text(), str(file), "exec"), module.__dict__)
    baseline = module.Ollama
    report_file = ROOT / (
        "artifacts/phase-8/gate/release-live/reports/"
        "2026-10-06-212915-qwen3-30b-a3b-workbench-32k-live-keyword.json"
    )
    saved = json.loads(report_file.read_text())
    compared = []
    for case in saved["results"]:
        for turn in case["turns"]:
            answer = turn["raw_answer"]
            raw = (
                "".join(
                    json.dumps({"message": {"content": answer[i : i + 19]}}) + "\n"
                    for i in range(0, len(answer), 19)
                )
                + '{"done":true}\n'
            )
            request = ChatRequest(
                "fake-replay",
                [
                    ProviderMessage("system", "Fake system"),
                    ProviderMessage("user", turn["question"]),
                ],
                context_length=32768,
            )
            sources = [
                Source.model_validate({"fetched_at": "2026-10-06", **s}) for s in turn["sources"]
            ]
            build(request, sources)
            outputs: list[Any] = []
            payloads = []
            for implementation in (baseline, Ollama):
                async with httpx.AsyncClient(
                    transport=httpx.MockTransport(
                        lambda req, body=raw: httpx.Response(200, content=body)
                    )
                ) as client:
                    adapter = implementation("fake", "http://fake", client=client)
                    payloads.append(json.dumps(adapter.payload(request), sort_keys=True))
                    outputs.append([event async for event in adapter.stream(request)])
            assert payloads[0] == payloads[1] and outputs[0] == outputs[1], case["id"]
            compared.append(case["id"])
    assert len(set(compared)) == 25
    target = ROOT / "artifacts/agent-loop/n0/web-replay-parity.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(
            {
                "case_count": 25,
                "turn_count": len(compared),
                "payload_and_event_parity": True,
                "native_calls": 0,
                "meaning": "Saved-answer transport replay, not fresh model-quality evaluation",
            },
            indent=2,
        )
        + "\n"
    )
