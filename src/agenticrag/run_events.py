"""Timestamp and publish the events a workflow records."""

from __future__ import annotations

import time
from dataclasses import replace
from typing import Callable, Iterable

from .domain import RunEvent


class EventLog(list[RunEvent]):
    def __init__(self, started: float, on_event: Callable[[RunEvent], None] | None = None,
                 initial: Iterable[RunEvent] = ()) -> None:
        super().__init__()
        self.started = started
        self.on_event = on_event
        for event in initial:
            self.append(event)

    def append(self, event: RunEvent) -> None:
        timed = replace(event, at_ms=max(0, round((time.perf_counter() - self.started) * 1000)))
        super().append(timed)
        if self.on_event is not None:
            self.on_event(timed)


def evidence_summary(evidence: Iterable[object]) -> list[dict[str, str | None]]:
    items: list[dict[str, str | None]] = []
    for ranked in evidence:
        chunk = ranked.chunk  # type: ignore[attr-defined]
        items.append({"chunk_id": chunk.id, "logical_path": chunk.logical_path, "heading": chunk.heading})
        if len(items) >= 32:
            break
    return items
