"""Safety-stop and non-attribution checks, with a synthetic owned worker."""

import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import control  # noqa: E402
from guard import ResourceSampler, probe_ok, swap_mib, violations  # noqa: E402

POLICY = {"maximum_stage_swap_growth_mib": 512, "maximum_health_seconds": 2}


def measurement(swap=100, status=200, seconds=0.001):
    return {
        "swap": f"vm.swapusage: total = 4096.00M  used = {swap:.2f}M  free = 0M (encrypted)",
        "app_health": {"status": status, "seconds": seconds},
        "rss_bytes": 0,
    }


def test_swap_growth_uses_starting_stage_value_not_host_total():
    assert violations(measurement(5512), 5000, POLICY) == []
    assert violations(measurement(5512.01), 5000, POLICY) == ["stage_swap_growth"]
    assert violations(measurement(4900), 5000, POLICY) == []


@pytest.mark.parametrize("status,seconds", [(500, 0.1), (200, 2.01)])
def test_health_failure_and_delay_stop(status, seconds):
    assert violations(measurement(status=status, seconds=seconds), 100, POLICY) == [
        "application_health"
    ]


def test_human_work_or_monitoring_failure_stops_without_private_data():
    for extra in [{"human_work_active": True}, {"activity_error": "TimeoutError"}]:
        assert violations({**measurement(), **extra}, 100, POLICY) == [
            "human_work_or_monitoring_failure"
        ]


def test_unknown_os_units_are_not_assumed_to_be_zero():
    with pytest.raises(ValueError):
        swap_mib("unavailable")


def test_resource_signal_is_followed_by_reaping_and_never_success(tmp_path, monkeypatch):
    sampler = ResourceSampler(lambda pid: measurement(613), 100, POLICY)
    monkeypatch.setattr(control, "sample", sampler)
    result = control.supervise(
        [sys.executable, "-u", "-c", "import time; time.sleep(30)"],
        tmp_path / "session",
        cwd=tmp_path,
        env=dict(os.environ),
        timeout=2,
        grace=1,
    )
    assert sampler.signal_sent and sampler.problems == ["stage_swap_growth"]
    assert result["worker_reaped"] and result["process_absent_after_reap"]
    assert not result["success"] and not result["completed_jobs"]
    assert result["exit_code"] != 0


def test_unowned_group_is_never_signalled(monkeypatch):
    sampler = ResourceSampler(lambda pid: measurement(613), 100, POLICY)
    monkeypatch.setattr(os, "getpgid", lambda pid: pid + 1)
    sent = []
    monkeypatch.setattr(os, "killpg", lambda *args: sent.append(args))
    with pytest.raises(RuntimeError, match="unowned"):
        sampler(123)
    assert sent == []


@pytest.mark.parametrize(
    "answer",
    [
        None,
        [],
        {},
        {"message": None},
        {"message": {"content": 42}},
        {"message": {"content": "Not ready"}},
    ],
)
def test_invalid_probe_response_cannot_pass(answer):
    assert not probe_ok(answer, 1, {"maximum_chat_seconds": 10}, True)


def test_probe_requires_acceptable_latency_and_loaded_residency():
    answer = {"message": {"content": "READY"}}
    policy = {"maximum_chat_seconds": 10}
    assert probe_ok(answer, 10, policy, True)
    assert not probe_ok(answer, 10.01, policy, True)
    assert not probe_ok(answer, 1, policy, False)
