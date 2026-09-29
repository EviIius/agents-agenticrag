from __future__ import annotations

import unittest

from _bootstrap import SRC  # noqa: F401
from agenticrag.model_routing import choose_model


def group(model: str, accuracy: float, abstention: float, latency: int, runs: int = 40) -> dict:
    return {
        "workflow": "fixed_rag", "model": model, "run_count": runs,
        "completed_count": runs, "answer_substring_accuracy": accuracy,
        "appropriate_abstention": abstention, "citation_resolution_rate": 1.0,
        "mean_latency_ms": latency,
        "metric_denominators": {"answer_cases": 30, "unanswerable_cases": 10, "citations": 40},
    }


class ModelRoutingTests(unittest.TestCase):
    def test_unlocked_pilot_does_not_override_selected_model(self) -> None:
        report = {"available": True, "groups": [
            group("fast", 0.8, 0.5, 1000), group("precise", 1.0, 1.0, 20_000),
        ]}
        self.assertEqual(choose_model("fixed", "fast", ["fast", "precise"], report)[0], "fast")

    def test_locked_gain_needs_paired_confidence_and_latency_margin(self) -> None:
        fast = group("fast", 0.8, 0.8, 1000)
        precise = group("precise", 0.81, 0.8, 20_000)
        precise.update(paired_baseline_model="fast", paired_quality_delta_ci_low=0.001)
        report = {"available": True, "split": "locked", "groups": [fast, precise]}
        self.assertEqual(choose_model("fixed", "fast", ["fast", "precise"], report)[0], "fast")
        precise["answer_substring_accuracy"] = 1.0
        self.assertEqual(choose_model("fixed", "fast", ["fast", "precise"], report)[0], "precise")
        precise["paired_quality_delta_ci_low"] = 0
        self.assertEqual(choose_model("fixed", "fast", ["fast", "precise"], report)[0], "fast")

    def test_unmeasured_and_uninstalled_models_are_not_routed(self) -> None:
        report = {"available": True, "split": "locked", "groups": [group("precise", 1.0, 1.0, 20_000)]}
        self.assertEqual(choose_model("fixed", "fast", ["fast"], report)[0], "fast")
        self.assertEqual(choose_model("supervisor", "fast", ["fast", "precise"], report)[0], "fast")

    def test_small_comparison_does_not_override_selected_model(self) -> None:
        report = {"available": True, "split": "locked", "groups": [group("precise", 1.0, 1.0, 20_000, runs=2)]}
        self.assertEqual(choose_model("fixed", "fast", ["fast", "precise"], report)[0], "fast")


if __name__ == "__main__":
    unittest.main()
