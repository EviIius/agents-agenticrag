"""Conservative per-run model selection from local, measured evaluations."""

from __future__ import annotations

from typing import Any, Sequence


def choose_model(
    workflow: str, configured_model: str, installed_models: Sequence[str],
    report: dict[str, Any],
) -> tuple[str, str]:
    """Use tested quality for Fixed RAG; otherwise retain the selected model."""
    if workflow != "fixed":
        return configured_model, "No comparable quality results for this workflow"
    if not report.get("available") or configured_model not in installed_models:
        return configured_model, "No usable local comparison"

    # Only a held-out, paired comparison can override the user's model. Older
    # workbench reports are practice sets and have no split or confidence band.
    if report.get("split") != "locked":
        return configured_model, "No held-out model comparison"

    candidates: list[tuple[float, float, str]] = []
    for group in report.get("groups", []):
        if not isinstance(group, dict) or group.get("workflow") != "fixed_rag":
            continue
        model = group.get("model")
        runs = group.get("run_count", 0)
        completed = group.get("completed_count", 0)
        denominators = group.get("metric_denominators") or {}
        if (not isinstance(model, str) or model not in installed_models
                or not isinstance(runs, int) or not isinstance(completed, int)
                or runs < 5 or completed < runs * 0.8
                or not isinstance(denominators, dict)
                or denominators.get("answer_cases", 0) < 30
                or denominators.get("unanswerable_cases", 0) < 10
                or denominators.get("citations", 0) < 1):
            continue
        accuracy = group.get("answer_substring_accuracy")
        abstention = group.get("appropriate_abstention")
        resolution = group.get("citation_resolution_rate")
        marker_coverage = group.get("inline_citation_coverage")
        latency = group.get("mean_latency_ms")
        if not all(isinstance(value, (int, float)) and 0 <= value <= 1
                   for value in (accuracy, abstention, resolution)):
            continue
        if not isinstance(latency, (int, float)) or latency < 0:
            continue
        if marker_coverage is not None and (not isinstance(marker_coverage, (int, float)) or marker_coverage < 0.9):
            continue
        quality = (0.5 * accuracy + 0.3 * abstention + 0.2 * resolution) * completed / runs
        candidates.append((quality, -float(latency), model))
    if not candidates:
        return configured_model, "No comparable quality results"
    baseline = next((item for item in candidates if item[2] == configured_model), None)
    if baseline is None:
        return configured_model, "Selected model has no comparable held-out result"
    eligible = [baseline]
    for candidate in candidates:
        if candidate[2] == configured_model:
            continue
        group = next(item for item in report["groups"] if item.get("workflow") == "fixed_rag" and item.get("model") == candidate[2])
        lower = group.get("paired_quality_delta_ci_low")
        if group.get("paired_baseline_model") != configured_model or not isinstance(lower, (int, float)) or lower <= 0:
            continue
        if candidate[1] < baseline[1] * 3 and candidate[0] - baseline[0] < 0.05:
            continue
        eligible.append(candidate)
    winner = max(eligible)
    if winner[2] == configured_model:
        return configured_model, "No proven quality gain over selected model"
    return winner[2], "Held-out paired quality gain over selected model"
