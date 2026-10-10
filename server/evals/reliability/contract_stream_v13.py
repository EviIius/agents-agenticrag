"""Evaluation-only buffering. Raw selection JSON never becomes an assistant answer."""

import json
from collections.abc import AsyncIterator
from dataclasses import asdict
from pathlib import Path
from time import monotonic
from typing import Any

from app.providers.base import ChatRequest, Finish, ProviderEvent, TextDelta
from app.providers.ollama import Ollama
from evals.reliability.evidence_contract_v13 import DECLINE, render


def install(trace: str) -> None:
    original = Ollama.stream
    failed = False

    async def selected_stream(
        adapter: Ollama, request: ChatRequest
    ) -> AsyncIterator[ProviderEvent]:
        nonlocal failed
        if failed:
            raise SystemExit("Evidence protocol failed; next model call prohibited")
        catalog = getattr(request, "_evidence_catalog", None)
        if catalog is None:
            async for event in original(adapter, request):
                yield event
            return
        raw, events, deferred = "", [], []
        terminal = None
        outcome: dict[str, Any] | None = None
        started = monotonic()
        try:
            async for event in original(adapter, request):
                events.append({"type": type(event).__name__, "value": asdict(event)})
                if isinstance(event, TextDelta):
                    raw += event.text
                    if len(raw) > 65536:
                        raise ValueError("Selection response too large")
                elif isinstance(event, Finish):
                    terminal = event
                elif type(event).__name__ != "ReasoningDelta":
                    deferred.append(event)
            if terminal is None or terminal.reason != "stop":
                outcome = {
                    "status": "rejected",
                    "content": DECLINE,
                    "reason": "Selection did not complete",
                    "verified_answer": False,
                }
            else:
                outcome = render(raw, catalog)
            failed = outcome["status"] == "rejected"
            if failed:
                raise SystemExit("Evidence protocol rejected; trial stopped automatically")
            if terminal and terminal.reason == "error":
                yield terminal
                return
            yield TextDelta(outcome["content"])
            for event in deferred:
                yield event
            if terminal:
                yield terminal
        finally:
            if outcome is None:
                failed = True
            record = {
                "payload": adapter.payload(request),
                "raw_events": events,
                "elapsed_ms": (monotonic() - started) * 1000,
                "source_snapshots": catalog.sources,
                "unit_catalog": catalog.units,
                "outcome": outcome,
                "protocol_stopped": failed,
                "limitation": "Valid provenance is not verified relevance, truth or completeness.",
            }
            with Path(trace).open("a") as output:
                output.write(json.dumps(record, ensure_ascii=False) + "\n")

    setattr(Ollama, "stream", selected_stream)  # noqa: B010 -- isolated method replacement
