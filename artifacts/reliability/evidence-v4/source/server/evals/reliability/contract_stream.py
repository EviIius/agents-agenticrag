"""Evaluation-only buffering. Raw selection JSON never becomes an assistant answer."""

import json
from dataclasses import asdict
from pathlib import Path
from time import monotonic

from app.providers.base import Finish, TextDelta
from app.providers.ollama import Ollama
from evals.reliability.evidence_contract import DECLINE, render


def install(trace: str) -> None:
    original = Ollama.stream

    async def selected_stream(adapter, request):
        catalog = getattr(request, "_evidence_catalog", None)
        if catalog is None:
            async for event in original(adapter, request):
                yield event
            return
        raw, events, deferred = "", [], []
        terminal = None
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
            if terminal and terminal.reason == "error":
                yield terminal
                return
            yield TextDelta(outcome["content"])
            for event in deferred:
                yield event
            if terminal:
                yield terminal
        finally:
            record = {
                "payload": adapter.payload(request),
                "raw_events": events,
                "elapsed_ms": (monotonic() - started) * 1000,
                "source_snapshots": catalog.sources,
                "unit_catalog": catalog.units,
                "outcome": locals().get("outcome"),
                "limitation": "Valid provenance is not verified relevance, truth or completeness.",
            }
            with Path(trace).open("a") as output:
                output.write(json.dumps(record, ensure_ascii=False) + "\n")

    Ollama.stream = selected_stream
