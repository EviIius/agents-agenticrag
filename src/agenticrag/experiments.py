from __future__ import annotations

import json
import math
import os
import re
import threading
import traceback
import uuid
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from statistics import mean
from typing import Any, Protocol, Sequence
from urllib.request import urlopen

from .workflows import Workflow


MANIFEST_VERSION = 2


@dataclass(frozen=True)
class ExperimentCase:
    id: str
    question: str
    collection: str
    scopes: tuple[str, ...]
    answerable: bool | None = None
    required_chunk_ids: tuple[str, ...] = ()
    expected_answer_contains: tuple[str, ...] = ()
    forbidden_answer_contains: tuple[str, ...] = ()
    category: str = "general"
    split: str = "dev"
    required_quotes: tuple[dict[str, str], ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ExperimentRecord:
    manifest_version: int
    run_id: str
    recorded_at: str
    case_id: str
    case: dict[str, Any]
    workflow: str
    provider: str
    embedding_provider: str | None
    manifest: dict[str, Any]
    status: str
    result: dict[str, Any] | None
    error_type: str | None
    error: str | None
    error_trace: str | None = None
    resources: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> ExperimentRecord:
        return cls(
            manifest_version=int(value["manifest_version"]),
            run_id=str(value["run_id"]),
            recorded_at=str(value["recorded_at"]),
            case_id=str(value["case_id"]),
            case=dict(value["case"]),
            workflow=str(value["workflow"]),
            provider=str(value["provider"]),
            embedding_provider=(
                None
                if value.get("embedding_provider") is None
                else str(value["embedding_provider"])
            ),
            manifest=dict(value["manifest"]),
            status=str(value["status"]),
            result=None if value.get("result") is None else dict(value["result"]),
            error_type=None if value.get("error_type") is None else str(value["error_type"]),
            error=None if value.get("error") is None else str(value["error"]),
            error_trace=(None if value.get("error_trace") is None else str(value["error_trace"])),
            resources=(None if value.get("resources") is None else dict(value["resources"])),
        )


class RunJournal(Protocol):
    def append(self, record: ExperimentRecord) -> None: ...


class JsonlRunJournal:
    """Append-only, fsynced local run manifest journal."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path).expanduser().resolve()
        self._lock = threading.Lock()

    def append(self, record: ExperimentRecord) -> None:
        line = json.dumps(record.to_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        with self._lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8", newline="\n") as stream:
                stream.write(line + "\n")
                stream.flush()
                os.fsync(stream.fileno())

    def read(self) -> list[ExperimentRecord]:
        if not self.path.exists():
            return []
        records: list[ExperimentRecord] = []
        for line_number, line in enumerate(
            self.path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
                if not isinstance(value, dict):
                    raise TypeError("record is not an object")
                record = ExperimentRecord.from_dict(value)
            except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
                raise ValueError(f"Invalid run journal record on line {line_number}") from exc
            if record.manifest_version not in {1, MANIFEST_VERSION}:
                raise ValueError(
                    f"Unsupported run manifest version {record.manifest_version} on line {line_number}"
                )
            records.append(record)
        return records

    def latest_records(self) -> list[ExperimentRecord]:
        latest: dict[str, ExperimentRecord] = {}
        order: list[str] = []
        for record in self.read():
            if record.run_id not in latest:
                order.append(record.run_id)
            latest[record.run_id] = record
        return [latest[run_id] for run_id in order]

    def terminal_records(self) -> list[ExperimentRecord]:
        return [
            record for record in self.latest_records() if record.status in {"completed", "failed"}
        ]


class ExperimentRunner:
    """Runs identical cases through multiple workflow/provider configurations."""

    def __init__(self, journal: RunJournal | None = None) -> None:
        self.journal = journal

    def run(
        self,
        cases: Sequence[ExperimentCase],
        workflows: Sequence[Workflow],
        *,
        repeat: int = 1,
    ) -> list[ExperimentRecord]:
        if repeat < 1:
            raise ValueError("repeat must be at least 1")
        records: list[ExperimentRecord] = []
        for workflow in workflows:
            for repeat_index in range(1, repeat + 1):
                for case in cases:
                    record = self._run_one(case, workflow, repeat_index)
                    records.append(record)
        return records

    def _run_one(
        self, case: ExperimentCase, workflow: Workflow, repeat_index: int
    ) -> ExperimentRecord:
        run_id = uuid.uuid4().hex
        started = self._record(run_id, case, workflow, status="started", repeat_index=repeat_index)
        if self.journal:
            self.journal.append(started)
        try:
            result = workflow.run(
                case.question,
                scopes=case.scopes,
                collection=case.collection,
            )
            terminal = self._record(
                run_id,
                case,
                workflow,
                status="completed",
                result=result.to_dict(),
                repeat_index=repeat_index,
                resources=_ollama_loaded_resources(workflow),
            )
        except Exception as exc:
            terminal = self._record(
                run_id,
                case,
                workflow,
                status="failed",
                error_type=type(exc).__name__,
                error=str(exc),
                error_trace=traceback.format_exc(limit=8),
                repeat_index=repeat_index,
                resources=_ollama_loaded_resources(workflow),
            )
        if self.journal:
            self.journal.append(terminal)
        return terminal

    @staticmethod
    def _record(
        run_id: str,
        case: ExperimentCase,
        workflow: Workflow,
        *,
        status: str,
        result: dict[str, Any] | None = None,
        error_type: str | None = None,
        error: str | None = None,
        error_trace: str | None = None,
        repeat_index: int = 1,
        resources: dict[str, Any] | None = None,
    ) -> ExperimentRecord:
        return ExperimentRecord(
            manifest_version=MANIFEST_VERSION,
            run_id=run_id,
            recorded_at=datetime.now(UTC).isoformat(),
            case_id=case.id,
            case=case.to_dict(),
            workflow=workflow.name,
            provider=workflow.provider_label,
            embedding_provider=workflow.embedding_provider_label,
            manifest={**workflow.manifest, "repeat_index": repeat_index},
            status=status,
            result=result,
            error_type=error_type,
            error=error,
            error_trace=error_trace,
            resources=resources,
        )


def _ollama_loaded_resources(workflow: Workflow) -> dict[str, Any] | None:
    """Best-effort loaded-model footprint, separate from process RSS or peak RAM."""
    config = getattr(getattr(workflow, "chat_provider", None), "config", None)
    if config is None or getattr(config, "runtime", None) != "ollama":
        return None
    try:
        with urlopen(f"{config.base_url.removesuffix('/v1')}/api/ps", timeout=2) as response:  # noqa: S310 - validated runtime URL
            payload = json.load(response)
        for model in payload.get("models", []):
            if model.get("name") == config.model:
                return {"model_loaded_bytes": model.get("size"), "model_gpu_bytes": model.get("size_vram")}
    except (OSError, ValueError, TypeError, KeyError):
        pass
    return None


def summarize_experiments(
    records: Sequence[ExperimentRecord],
    cases: Sequence[ExperimentCase],
) -> list[dict[str, Any]]:
    case_by_id = {case.id: case for case in cases}
    groups: dict[tuple[str, str, str | None], list[ExperimentRecord]] = {}
    for record in records:
        key = (record.workflow, record.provider, record.embedding_provider)
        groups.setdefault(key, []).append(record)

    summaries: list[dict[str, Any]] = []
    for (workflow, provider, embedding_provider), group in sorted(
        groups.items(), key=lambda item: tuple(value or "" for value in item[0])
    ):
        completed = [record for record in group if record.status == "completed"]
        latencies = [int(record.result["elapsed_ms"]) for record in completed if record.result]
        required_total = 0
        required_found = 0
        multi_hop_total = 0
        multi_hop_complete = 0
        answer_total = 0
        answer_correct = 0
        abstention_total = 0
        abstention_correct = 0
        citations_total = 0
        citations_resolved = 0
        citations_marked = 0
        tool_calls = 0
        tool_failures = 0
        reviews = 0
        review_rejections = 0
        budget_exhaustions = 0
        skill_loads = 0
        loaded_bytes: list[int] = []
        quotes_total = 0
        quotes_found = 0

        for record in group:
            case = case_by_id.get(record.case_id)
            if case is None:
                continue
            required = set(case.required_chunk_ids)
            required_total += len(required)
            quotes_total += len(case.required_quotes)
            if len(required) > 1:
                multi_hop_total += 1
            if case.answerable is True and (case.expected_answer_contains or case.forbidden_answer_contains):
                answer_total += 1
            if case.answerable is False:
                abstention_total += 1

            if record.status != "completed" or record.result is None:
                continue
            result = record.result
            if record.resources and isinstance(record.resources.get("model_loaded_bytes"), int):
                loaded_bytes.append(record.resources["model_loaded_bytes"])
            evidence_ids = {
                str(item["chunk"]["id"])
                for item in result.get("evidence", [])
                if isinstance(item, dict) and isinstance(item.get("chunk"), dict)
            }
            required_found += len(required & evidence_ids)
            for annotation in case.required_quotes:
                quote = " ".join(annotation["quote"].casefold().split())
                path = annotation["logical_path"]
                if any(
                    isinstance(item, dict) and isinstance(item.get("chunk"), dict)
                    and item["chunk"].get("logical_path") == path
                    and quote in " ".join(str(item["chunk"].get("text", "")).casefold().split())
                    for item in result.get("evidence", [])
                ):
                    quotes_found += 1
            if len(required) > 1:
                multi_hop_complete += int(required.issubset(evidence_ids))
            if case.answerable is True and (case.expected_answer_contains or case.forbidden_answer_contains):
                answer = str(result.get("answer", "")).casefold()
                answer_correct += int(
                    not bool(result.get("abstained"))
                    and all(value.casefold() in answer for value in case.expected_answer_contains)
                    and not any(value.casefold() in answer for value in case.forbidden_answer_contains)
                )
            if case.answerable is False:
                abstention_correct += int(bool(result.get("abstained")))

            answer_markers = set(re.findall(r"\[(\d+)\]", str(result.get("answer", ""))))
            for position, citation in enumerate(result.get("citations", []), start=1):
                if not isinstance(citation, dict):
                    continue
                citations_total += 1
                citations_resolved += int(str(citation.get("chunk_id")) in evidence_ids)
                citations_marked += int(str(position) in answer_markers)
            for event in result.get("events", []):
                if not isinstance(event, dict):
                    continue
                kind = event.get("kind")
                detail = event.get("detail") if isinstance(event.get("detail"), dict) else {}
                if kind == "tool_called":
                    tool_calls += 1
                    tool_failures += int(detail.get("success") is False)
                elif kind == "review_completed":
                    reviews += 1
                    review_rejections += int(detail.get("accepted") is False)
                elif kind == "budget_exhausted":
                    budget_exhaustions += 1
                elif kind == "skill_loaded":
                    skill_loads += 1

        summaries.append(
            {
                "workflow": workflow,
                "provider": provider,
                "embedding_provider": embedding_provider,
                "run_count": len(group),
                "completed_count": len(completed),
                "failed_count": sum(record.status == "failed" for record in group),
                "incomplete_count": sum(record.status == "started" for record in group),
                "failure_rate": _ratio(len(group) - len(completed), len(group)),
                "mean_latency_ms": None if not latencies else round(mean(latencies), 3),
                "p95_latency_ms": _percentile(latencies, 0.95),
                "mean_model_loaded_gb": None if not loaded_bytes else round(mean(loaded_bytes) / 1_000_000_000, 2),
                "evidence_recall": _ratio(required_found, required_total),
                "quote_evidence_recall": _ratio(quotes_found, quotes_total),
                "complete_multi_hop_evidence": _ratio(multi_hop_complete, multi_hop_total),
                "answer_substring_accuracy": _ratio(answer_correct, answer_total),
                "appropriate_abstention": _ratio(abstention_correct, abstention_total),
                "citation_resolution_rate": _ratio(citations_resolved, citations_total),
                "inline_citation_coverage": _ratio(citations_marked, citations_total),
                "tool_call_count": tool_calls,
                "tool_failure_rate": _ratio(tool_failures, tool_calls),
                "review_count": reviews,
                "review_rejection_rate": _ratio(review_rejections, reviews),
                "budget_exhaustion_rate": _ratio(budget_exhaustions, len(group)),
                "skill_load_count": skill_loads,
                "metric_denominators": {
                    "required_evidence_units": required_total,
                    "required_quotes": quotes_total,
                    "multi_hop_cases": multi_hop_total,
                    "answer_cases": answer_total,
                    "unanswerable_cases": abstention_total,
                    "citations": citations_total,
                    "tool_calls": tool_calls,
                    "reviews": reviews,
                    "runs_for_budget": len(group),
                },
            }
        )
    return summaries


def _ratio(numerator: int, denominator: int) -> float | None:
    return None if denominator == 0 else round(numerator / denominator, 6)


def _percentile(values: Sequence[int], quantile: float) -> int | None:
    if not values:
        return None
    ordered = sorted(values)
    index = max(0, math.ceil(quantile * len(ordered)) - 1)
    return ordered[index]
