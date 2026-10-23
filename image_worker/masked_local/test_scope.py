"""CPU-only scope rejection tests. The unchanged native controller has its own tests."""

import importlib.util
import json
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("focused_scope", HERE / "scope.py")
scope = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scope)


def prepared(root):
    (root / "bound.json").write_text("{}")
    (root / "scope.json").write_text(
        json.dumps(
            {
                "maximum_native_invocations": 6,
                "order": [list(pair) for pair in scope.ORDER],
                "scope_source_sha256": scope.sha(HERE / "scope.py"),
                "files": {"bound.json": scope.sha(root / "bound.json")},
            }
        )
    )


def previous(root, *, technical_pass=True, review_bound=True):
    attempts = root / "hat/attempts"
    attempts.mkdir(parents=True)
    (attempts / "01-flux.reserved.json").write_text("{}")
    (attempts / "flux.result.json").write_text(
        json.dumps(
            {
                "passed": technical_pass,
                "worker_reaped": True,
                "output_sha256": "bound",
            }
        )
    )
    (attempts / "flux.quality.json").write_text(
        json.dumps(
            {
                "reviewed": True,
                "passed": False,
                "output_sha256": "bound" if review_bound else "stale",
            }
        )
    )


def test_frozen_input_and_cross_region_order_refuse_before_launch(tmp_path):
    prepared(tmp_path)
    scope.admitted(tmp_path, "hat", "flux")
    with pytest.raises(ValueError, match="order"):
        scope.admitted(tmp_path, "rear", "flux")
    (tmp_path / "bound.json").write_text('{"changed":true}')
    with pytest.raises(ValueError, match="changed"):
        scope.admitted(tmp_path, "hat", "flux")


@pytest.mark.parametrize(
    "technical_pass,review_bound", [(True, True), (False, True), (True, False)]
)
def test_only_bound_visual_miss_can_continue(tmp_path, technical_pass, review_bound):
    prepared(tmp_path)
    previous(tmp_path, technical_pass=technical_pass, review_bound=review_bound)
    if technical_pass and review_bound:
        scope.admitted(tmp_path, "hat", "qwen")
    else:
        with pytest.raises(ValueError, match="technical pass"):
            scope.admitted(tmp_path, "hat", "qwen")


def test_six_consumed_slots_cannot_be_reused(tmp_path):
    prepared(tmp_path)
    for index, (part, engine) in enumerate(scope.ORDER):
        attempts = tmp_path / part / "attempts"
        attempts.mkdir(parents=True, exist_ok=True)
        (attempts / f"{index:02}-{engine}.reserved.json").write_text("{}")
    for part, engine in scope.ORDER:
        with pytest.raises(ValueError, match="allowance"):
            scope.admitted(tmp_path, part, engine)
