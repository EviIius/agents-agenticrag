"""Retain outcome and verify protocol, frozen bytes and unchanged app health."""

import hashlib
import importlib.util
import json
import subprocess
from collections import Counter
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, value):
    destination = OUT / name
    assert not destination.exists(), name
    destination.write_text(json.dumps(value, indent=2) + "\n")


def main():
    manifest = json.loads((OUT / "manifest.json").read_text())
    frozen_commit = subprocess.check_output(
        ["git", "log", "-1", "--format=%H", "--", str(OUT / "manifest.json")],
        cwd=ROOT,
        text=True,
    ).strip()
    assert frozen_commit
    for name, expected in manifest["files"].items():
        assert sha(ROOT / name) == expected, name
    spec = importlib.util.spec_from_file_location("frozen_experiment", OUT / "experiment.py")
    harness = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(harness)
    index = json.loads((OUT / "ordered-results.json").read_text())
    assert index["stop"] or index.get("completed_phase") == "full-3"
    rows = []
    calls = Counter()
    for expected, run in zip(
        index["declared_order"][: len(index["runs"])], index["runs"], strict=True
    ):
        assert expected == [
            run["label"],
            run["arm"],
            "" if run["case"] == "original full suite" else run["case"],
        ]
        document = json.loads((ROOT / run["report"]).read_text())
        assert sha(ROOT / run["report"]) == run["report_sha256"]
        folder = OUT / run["label"]
        assert harness.protocol_verified(folder, document)
        native = []
        for line in (folder / "trace.jsonl").read_text().splitlines():
            trace = json.loads(line)
            utility = trace["payload"].get("format") is not None
            calls["planner" if utility else "answer"] += 1
            assert trace["error"] is None and trace["capacity_enabled"]
            assert trace["payload"]["options"] == (
                {"temperature": 0.2, "num_predict": 256, "num_ctx": 16384}
                if utility
                else {"num_ctx": 16384}
            )
            assert not any(e["type"] == "ToolCall" for e in trace["events"])
            if utility:
                raw = "".join(
                    e["value"]["text"] for e in trace["events"] if e["type"] == "TextDelta"
                )
                try:
                    native.append(json.loads(raw))
                except ValueError:
                    native.append({"invalid_json_retained_in_trace": True})
        turns = [turn for result in document["results"] for turn in result["turns"]]
        rows.append(
            {
                "label": run["label"],
                "arm": run["arm"],
                "case": run["case"],
                "passed": all(result["passed"] for result in document["results"]),
                "report": run["report"],
                "report_sha256": run["report_sha256"],
                "protocol_verified": True,
                "native_plans": native,
                "search_status": [t["web"]["status"] for t in turns],
                "fallback": [t["web"]["plan_fallback"] for t in turns],
                "attack_exposed": run["attack_exposed"],
                "host_decisions": [
                    json.loads(line)
                    for line in (folder / "host-decisions.jsonl").read_text().splitlines()
                ]
                if (folder / "host-decisions.jsonl").exists()
                else [],
            }
        )
    totals = {}
    for arm in ("baseline", "candidate"):
        original = [r for r in rows if r["arm"] == arm and r["label"].startswith("boundary-")]
        supplemental = [
            r for r in rows if r["arm"] == arm and r["label"].startswith("supplemental-")
        ]
        totals[arm] = {
            "original_executed": len(original),
            "original_passed": sum(r["passed"] for r in original),
            "supplemental_executed": len(supplemental),
            "supplemental_passed": sum(r["passed"] for r in supplemental),
        }
    write(
        "results-summary.json",
        {
            "status": "Stopped at declared failure gate; not qualified"
            if index["stop"]
            else "Replay complete; release gates remain",
            "frozen_commit": frozen_commit,
            "totals": totals,
            "native_model_calls": dict(calls),
            "stop": index["stop"],
            "unexecuted": index["declared_order"][len(rows) :],
            "runs": rows,
        },
    )
    earlier = subprocess.check_output(
        ["git", "ls-tree", "-r", "-z", "a243774", "--", "artifacts", "server/evals/web/reports"],
        cwd=ROOT,
    )
    preserved = 0
    for row in earlier.split(b"\0"):
        if not row:
            continue
        head, name = row.split(b"\t", 1)
        expected = head.split()[2].decode()
        data = (ROOT / name.decode()).read_bytes()
        assert (
            hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest() == expected
        ), name
        preserved += 1
    changes = subprocess.check_output(
        [
            "git",
            "diff",
            "--name-only",
            "a243774",
            "--",
            "server",
            "web",
            "shared",
            "scripts",
            "image_worker",
            "transcribe",
        ],
        cwd=ROOT,
        text=True,
    ).splitlines()
    assert not changes, changes
    health = {}
    for address in (
        "http://127.0.0.1:8787/api/health",
        "https://jakes-mac-mini.tailc4d343.ts.net/api/health",
    ):
        with urlopen(address, timeout=15) as response:
            assert response.status == 200
            health[address] = response.status
    with urlopen("http://127.0.0.1:11434/api/version", timeout=15) as response:
        runtime = json.load(response)
    assert runtime["version"] == "0.35.0"
    write(
        "verification.json",
        {
            "frozen_files_preserved": len(manifest["files"]),
            "prior_committed_evidence_files_preserved": preserved,
            "product_source_changes": changes,
            "health": health,
            "runtime": runtime,
            "deployment": False,
            "research_calls": 0,
            "image_calls": 0,
            "workflow_calls": 0,
            "limit": "Manual semantic support review is a separate required record.",
        },
    )
    print(
        json.dumps(
            {
                "totals": totals,
                "native_calls": dict(calls),
                "stop": index["stop"],
                "unexecuted_children": len(index["declared_order"]) - len(rows),
                "preserved_evidence": preserved,
                "healthy": True,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
