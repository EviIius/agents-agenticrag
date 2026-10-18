"""C1-only bindings over the frozen N1 controller. No production import or hook."""

from __future__ import annotations

import hashlib
import json
import os
import sys
from dataclasses import asdict
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "server"))
sys.path.insert(0, str(ROOT / "experiments/native_n1"))

import trial as original  # noqa: E402
from experiments.native_coverage.candidate import prompt  # noqa: E402
from experiments.native_coverage.check import check  # noqa: E402
from protocol import CountedTransport, Refused, write  # noqa: E402
from protocol import Ledger as Ledger  # noqa: E402

from app.runs import agent as agent_module  # noqa: E402

OUT = ROOT / "artifacts/agent-loop/c1"
QA = Path.home() / ".local/share/workbench/qa/native-agent-c1-20261018"
OLD_LEDGER = Path.home() / ".local/share/workbench/qa/native-agent-n1-20261018/ledger.json"
CANDIDATE = ROOT / "artifacts/agent-loop/coverage-v1/candidate-prompts.json"
N1_EXECUTE = original.execute_case


def expected_system(kind):
    frozen = json.loads(CANDIDATE.read_text())[kind]
    text = prompt(kind)
    if hashlib.sha256(text.encode()).hexdigest() != frozen["v2_sha256"]:
        raise Refused("Reviewed candidate changed")
    return original.SYSTEM + "\n\n" + text


class FrozenTransport(CountedTransport):
    async def handle_async_request(self, request):
        if request.method == "POST" and request.url.path == "/api/chat":
            body = json.loads(request.content)
            expected = {"role": "system", "content": expected_system(self.tools.kind)}
            if not body.get("messages") or body["messages"][0] != expected:
                self.ledger.stop("Frozen C1 wire prompt changed")
                raise Refused("Frozen C1 wire prompt changed")
        return await super().handle_async_request(request)


async def execute_case(*args, **kwargs):
    # Scoped to this isolated process/task. The N0/N1 files remain byte-identical.
    with (
        patch.object(agent_module, "prompt", prompt),
        patch.object(original, "CountedTransport", FrozenTransport),
    ):
        result = await N1_EXECUTE(*args, **kwargs)
    message = result["message"]
    coverage = check(message["content"], message["agent"]["source_count"])
    result["coverage"] = asdict(coverage)
    result["automatic_checks"]["no_obvious_citation_gaps"] = not coverage.gaps
    if coverage.gaps:
        args[4].stop("Required structural citation coverage failed: " + args[0])
    write(args[5] / "result.json", result)
    return result


async def prepare():
    if (OUT / "frozen.json").exists() or (QA / "ledger.json").exists():
        raise Refused("C1 preparation/ledger already exists; never reset it")
    n1 = json.loads((ROOT / "artifacts/agent-loop/n1/frozen.json").read_text())
    coverage = json.loads(
        (ROOT / "artifacts/agent-loop/coverage-v1/executed-source.json").read_text()
    )
    if original.sha(OLD_LEDGER) != coverage["stopped_N1_ledger_sha256"]:
        raise Refused("Stopped N1 ledger changed")
    files = {**n1["files"], **coverage["files"]}
    if not all(original.sha(ROOT / name) == value for name, value in files.items()):
        raise Refused("Original executed source/input changed")
    model, version, identity = await original.observed_model()
    old = n1["admission"]
    if (model.digest, version, identity) != (
        old["digest"],
        old["runtime_version"],
        old["show_hashes"],
    ):
        raise Refused("Same installed model/runtime is required")
    before = await original.sample()
    original.resource_check(before, before["swap_mib"], model.digest)
    for path in sorted(Path(__file__).parent.glob("*")):
        if path.is_file():
            files[str(path.relative_to(ROOT))] = original.sha(path)
    files[str(CANDIDATE.relative_to(ROOT))] = original.sha(CANDIDATE)
    files["docs/AGENT-C1-RETEST-PLAN.md"] = original.sha(ROOT / "docs/AGENT-C1-RETEST-PLAN.md")
    admission = {**old, "checkpoint": "C1", "swap_baseline_mib": before["swap_mib"]}
    write(
        OUT / "frozen.json",
        {
            "files": files,
            "admission": admission,
            "schedule": original.SCHEDULE,
            "scopes": original.SCOPES,
            "max_calls": 36,
            "reasoning": None,
            "params": {},
            "prepared_model": model.model_dump(),
            "before": before,
            "wire_systems": {kind: expected_system(kind) for kind in ("web", "library")},
            "old_N1_ledger_sha256": original.sha(OLD_LEDGER),
        },
    )
    write(QA / "ledger.json", {"calls": 0, "tasks": {}, "stopped": None, "active": None})
    print(json.dumps({"prepared": True, "admission": admission, "native_calls": 0}))


def main():
    os.umask(0o077)
    # Reuse unchanged order, counters, sampler, deadline, manual-review and CLI.
    with (
        patch.object(original, "OUT", OUT),
        patch.object(original, "QA", QA),
        patch.object(original, "prepare", prepare),
        patch.object(original, "execute_case", execute_case),
    ):
        original.main()


if __name__ == "__main__":
    main()
