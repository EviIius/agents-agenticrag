"""Replay all historical native streams, preserving invalid outcomes and old payloads."""

import hashlib
import json
from pathlib import Path
from typing import Any

import httpx

from app.providers.base import ChatRequest, Finish, ProviderMessage, ToolCall
from app.providers.ollama import Ollama

ROOT = Path(__file__).resolve().parents[2]


async def test_all_240_native_probe_streams_parse_without_inference() -> None:
    report = json.loads((ROOT / "artifacts/phase-8/gate/tool-probe.json").read_text())
    parsed = 0
    hashes = {}
    for model in report["models"]:
        for case in model["cases"]:
            file = ROOT / model["fixture_folder"] / (case["id"] + ".ndjson")
            raw = file.read_bytes()
            hashes[str(file.relative_to(ROOT))] = hashlib.sha256(raw).hexdigest()
            async with httpx.AsyncClient(
                transport=httpx.MockTransport(
                    lambda req, data=raw: httpx.Response(200, content=data)
                )
            ) as client:
                adapter = Ollama("fake", "http://fake", client=client)
                request = ChatRequest(
                    model["model_id"], [ProviderMessage("user", "fake replay")], tools=[]
                )
                events = [event async for event in adapter.stream(request)]
            expected = [
                call
                for line in raw.splitlines()
                if line
                for call in json.loads(line).get("message", {}).get("tool_calls", [])
            ]
            calls = [e for e in events if isinstance(e, ToolCall)]
            assert len(calls) == len(expected), (model["model_id"], case["id"])
            for actual, value in zip(calls, expected, strict=True):
                function = value.get("function", {})
                assert actual.name == function.get("name", "")
                args = function.get("arguments")
                assert actual.arguments == (args if isinstance(args, str) else json.dumps(args))
            assert any(isinstance(event, Finish) for event in events)
            parsed += 1
    assert parsed == 240
    # Structured provenance of a parser replay, not a new validity or model qualification score.
    target = ROOT / "artifacts/agent-loop/n0/recorded-stream-replay.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps({"streams": parsed, "native_calls": 0, "source_sha256": hashes}, indent=2) + "\n"
    )


async def test_unsolicited_tools_do_not_change_plain_chat_events() -> None:
    raw = (
        json.dumps(
            {
                "message": {
                    "content": "Plain",
                    "tool_calls": [{"function": {"name": "terminal", "arguments": {}}}],
                }
            }
        )
        + "\n"
        + json.dumps({"done": True})
        + "\n"
    ).encode()
    async with httpx.AsyncClient(
        transport=httpx.MockTransport(lambda req: httpx.Response(200, content=raw))
    ) as client:
        adapter = Ollama("fake", "http://fake", client=client)
        request = ChatRequest("opaque-id", [ProviderMessage("user", "fake")])
        assert "tools" not in adapter.payload(request)
        events = [event async for event in adapter.stream(request)]
        assert not any(isinstance(event, ToolCall) for event in events)


async def test_invalid_native_frame_returns_error_instead_of_crashing() -> None:
    raw = b'{"message":{"tool_calls":[null]}}\n'
    async with httpx.AsyncClient(
        transport=httpx.MockTransport(lambda req: httpx.Response(200, content=raw))
    ) as client:
        adapter = Ollama("fake", "http://fake", client=client)
        request = ChatRequest("opaque-id", [ProviderMessage("user", "fake")], tools=[])
        events: list[Any] = [event async for event in adapter.stream(request)]
        assert isinstance(events[-1], Finish) and events[-1].reason == "error"
