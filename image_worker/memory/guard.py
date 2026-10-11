"""Bounded trial measurements and owned-worker safety termination."""

import os
import re
import signal


def swap_mib(text: str) -> float:
    match = re.search(r"\bused\s*=\s*(\d+(?:\.\d+)?)M\b", text)
    if match is None:
        raise ValueError("Unrecognized macOS swap measurement")
    return float(match.group(1))


def probe_ok(answer: object, elapsed: float, policy: dict, loaded: bool) -> bool:
    if not isinstance(answer, dict) or not isinstance(answer.get("message"), dict):
        return False
    content = answer["message"].get("content")
    return (
        isinstance(content, str)
        and content.strip() == "READY"
        and elapsed <= policy["maximum_chat_seconds"]
        and loaded
    )


def violations(sample: dict, baseline_swap: float, policy: dict) -> list[str]:
    problems = []
    if swap_mib(sample["swap"]) - baseline_swap > policy["maximum_stage_swap_growth_mib"]:
        problems.append("stage_swap_growth")
    health = sample["app_health"]
    if (
        health.get("status") != 200
        or health.get("seconds", float("inf")) > policy["maximum_health_seconds"]
    ):
        problems.append("application_health")
    if sample.get("human_work_active") or sample.get("activity_error"):
        problems.append("human_work_or_monitoring_failure")
    return problems


class ResourceSampler:
    """Adapt the unchanged I0 sampler; never signal a process outside our session."""

    def __init__(self, original, baseline_swap: float, policy: dict):
        self.original = original
        self.baseline_swap = baseline_swap
        self.policy = policy
        self.problems: list[str] = []
        self.signal_sent = False

    def __call__(self, pid: int) -> dict:
        sample = self.original(pid)
        problems = violations(sample, self.baseline_swap, self.policy)
        sample["swap_used_mib"] = swap_mib(sample["swap"])
        sample["safety_violations"] = problems
        self.problems.extend(problem for problem in problems if problem not in self.problems)
        if problems and not self.signal_sent:
            # supervise() created this owned session, drains its events and reaps
            # its process before returning. Do not release capacity on a signal.
            try:
                if os.getpgid(pid) != pid:
                    raise RuntimeError("Refusing to signal an unowned process group")
                os.killpg(pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            else:
                self.signal_sent = True
        return sample
