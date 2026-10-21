"""Prepared controller gate checks. No worker, network, preload or GPU invocation."""

import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from native_trial import (
    Budget,
    CASES,
    CandidateEngine,
    EDIT_DIGEST,
    check_approval,
    execute,
)


def test_maximum_four_ordered_image_reservations_and_one_preload(tmp_path):
    budget = Budget(tmp_path)
    budget.reserve("image", CASES[0]["id"])
    budget.reserve("preload", "resident-setup")
    for case in CASES[1:]:
        budget.reserve("image", case["id"])
    for kind, case in [
        ("image", "recovery-heic"),
        ("preload", "resident-setup"),
        ("chat", "other"),
    ]:
        with pytest.raises(ValueError):
            budget.reserve(kind, case)
    assert len(budget.rows()) == 5
    assert all(row["reserved_before_request"] for row in budget.rows())


@pytest.mark.parametrize(
    "kind,case", [("image", "cancel"), ("preload", "resident-setup")]
)
def test_out_of_order_request_never_reserved(tmp_path, kind, case):
    budget = Budget(tmp_path)
    with pytest.raises(ValueError):
        budget.reserve(kind, case)
    assert budget.rows() == []


def test_halted_trial_cannot_continue(tmp_path):
    budget = Budget(tmp_path)
    budget.halt.write_text("Synthetic failure")
    with pytest.raises(ValueError, match="Prior failure"):
        budget.reserve("image", "empty-heic")
    assert not budget.path.exists()


@pytest.mark.parametrize(
    "rows,expected",
    [
        ([], True),
        ([{"digest": EDIT_DIGEST, "context_length": 32768, "size_vram": 100}], True),
        ([{"digest": EDIT_DIGEST, "context_length": 65536, "size_vram": 100}], False),
        ([{"digest": "unknown", "context_length": 32768, "size_vram": 100}], False),
        ([{"digest": EDIT_DIGEST, "context_length": 32768, "size_vram": True}], False),
        (
            [
                {
                    "digest": EDIT_DIGEST,
                    "context_length": 32768,
                    "size_vram": 21827095101,
                }
            ],
            False,
        ),
        (
            [{"digest": EDIT_DIGEST, "context_length": 32768, "size_vram": 100}] * 2,
            False,
        ),
    ],
)
def test_only_prospective_empty_or_existing_strict_residency(rows, expected):
    assert CandidateEngine.qualified_edit(rows) is expected


def test_missing_approval_refused_before_any_execution_folder(tmp_path):
    with pytest.raises(FileNotFoundError):
        check_approval(tmp_path / "absent.json")


def test_wrong_approval_refused(tmp_path):
    receipt = tmp_path / "approval.json"
    receipt.write_text(json.dumps({"scope": "other"}))
    # The manifest is needed only to compute an expected hash, not to make calls.
    from unittest.mock import patch

    with patch("native_trial.sha", return_value="synthetic"):
        with pytest.raises(ValueError, match="Missing or mismatched"):
            check_approval(receipt)


@pytest.mark.asyncio
async def test_full_controller_stops_on_first_job_failure_without_third_dispatch(
    tmp_path, monkeypatch
):
    import shutil
    import native_trial
    from tests.test_photo_references import EditFake

    fixture_root = native_trial.PRIVATE / "fixtures"
    shutil.copytree(fixture_root, tmp_path / "fixtures")
    monkeypatch.setattr(native_trial, "PRIVATE", tmp_path)
    original = EditFake.run_edit
    calls = []

    async def fail_second(self, manifest, scratch, progress):
        calls.append(manifest)
        if len(calls) == 2:
            raise ValueError("Synthetic protocol failure; no third dispatch")
        return await original(self, manifest, scratch, progress)

    monkeypatch.setattr(EditFake, "run_edit", fail_second)
    with pytest.raises(AssertionError):
        await execute(False, None)
    folder = tmp_path / "offline-controller"
    result = json.loads((folder / "summary.json").read_text())
    assert len(calls) == 2 and result["fake_image_requests"] == 2
    assert result["native_image_requests"] == result["preload_requests"] == 0
    assert result["capacity_released"] and not result["passed"]
    assert [r["case"] for r in Budget(folder).rows()] == ["empty-heic", "resident-jpeg"]
    assert Budget(folder).halt.exists()
    with pytest.raises(ValueError, match="Prior failure"):
        Budget(folder).reserve("image", "cancel")


@pytest.mark.asyncio
async def test_empty_case_rejects_residency_change_even_to_qualified_model(monkeypatch):
    from app.capacity import Capacity
    from native_trial import Measured

    async def loaded(self):
        return [{"digest": EDIT_DIGEST, "context_length": 32768, "size_vram": 100}]

    monkeypatch.setattr(CandidateEngine, "loaded", loaded)
    engine = Measured(None, Capacity())
    engine.expected_resident = False
    with pytest.raises(AssertionError, match="Residency changed"):
        await engine.loaded()
    engine.expected_resident = True
    assert len(await engine.loaded()) == 1
