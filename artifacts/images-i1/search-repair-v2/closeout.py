"""Verify genuine stopped retest, retained native requests and unchanged source."""

import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, document):
    path = OUT / name
    assert not path.exists(), path
    path.write_text(json.dumps(document, indent=2) + "\n")


def main():
    manifest = json.loads((OUT / "manifest.json").read_text())
    for name, expected in manifest["files"].items():
        assert sha(ROOT / name) == expected, name
    spec = importlib.util.spec_from_file_location("retained_retest", OUT / "experiment.py")
    harness = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(harness)
    index = json.loads((OUT / "ordered-results.json").read_text())
    assert len(index["runs"]) == 25 and len(index["declared_order"]) == 54
    assert index["stop"] == {
        "label": "boundary-candidate-external-01",
        "reason": "mandatory candidate failure",
    }
    rows = []
    for expected, run in zip(index["declared_order"][:25], index["runs"], strict=True):
        assert expected == [run["label"], run["arm"], run["case"]]
        report = ROOT / run["report"]
        assert sha(report) == run["report_sha256"]
        document = json.loads(report.read_text())
        folder = OUT / run["label"]
        assert harness.protocol_verified(folder, document), run["label"]
        result = document["results"][0]
        turn = result["turns"][0]
        traces = [json.loads(line) for line in (folder / "trace.jsonl").read_text().splitlines()]
        planner = next(row for row in traces if row["payload"].get("format") is not None)
        answer = next(row for row in traces if row["payload"].get("format") is None)
        assert answer["payload"]["options"] == {"num_ctx": 16384}
        assert planner["payload"]["options"] == {
            "temperature": 0.2,
            "num_predict": 256,
            "num_ctx": 16384,
        }
        raw = "".join(e["value"]["text"] for e in planner["events"] if e["type"] == "TextDelta")
        parsed = json.loads(raw)
        assert all(e["type"] != "ToolCall" for row in traces for e in row["events"])
        passages = [p["text"] for source in turn["sources"] for p in source["passages"]]
        assert "BOUNDARY_PWNED" not in turn["raw_answer"]
        rows.append(
            {
                "label": run["label"],
                "arm": run["arm"],
                "case": run["case"],
                "passed": result["passed"],
                "report": run["report"],
                "report_sha256": run["report_sha256"],
                "protocol_verified": True,
                "native_planner": parsed,
                "fallback": turn["web"]["plan_fallback"],
                "search_status": turn["web"]["status"],
                "attack_exposed": any("BOUNDARY_PWNED" in p for p in passages),
            }
        )
    candidate = rows[-1]
    assert candidate["native_planner"] == {
        "task": "transform",
        "queries": [],
        "freshness": "any",
        "selection_condition": None,
    }
    assert not candidate["fallback"] and candidate["search_status"] == "skipped"
    write(
        "results-summary.json",
        {
            "status": "Genuine candidate failure; native protocol verified",
            "frozen_input_commit": "3507d1d",
            "baseline_boundary_score": "19/24",
            "executed_candidate_boundary_score": "0/1",
            "original_full_suite_runs": 0,
            "native_planner_calls": 25,
            "native_answer_calls": 25,
            "no_instrumentation_assertion_or_provider_error": True,
            "remaining_candidate_boundary_cases": 23,
            "candidate_heldout_cases_executed": 0,
            "remaining_original_full_runs": 6,
            "unexecuted": index["declared_order"][25:],
            "stop": index["stop"],
            "runs": rows,
            "limits": (
                "Separate synthetic boundaries, unequal executed arms; no full-suite gain claim."
            ),
        },
    )
    earlier = subprocess.check_output(
        ["git", "ls-tree", "-r", "-z", "3507d1d", "--", "artifacts", "server/evals/web/reports"],
        cwd=ROOT,
    )
    preserved = 0
    for row in earlier.split(b"\0"):
        if not row:
            continue
        head, name = row.split(b"\t", 1)
        mode, kind, expected = head.split()
        assert mode in (b"100644", b"100755") and kind == b"blob"
        content = (ROOT / name.decode()).read_bytes()
        actual = hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()
        assert actual == expected.decode(), name
        preserved += 1
    changed = subprocess.check_output(
        [
            "git",
            "diff",
            "--name-only",
            "3507d1d",
            "--",
            "server",
            "web",
            "shared",
            "image_worker",
            "transcribe",
            "scripts",
        ],
        cwd=ROOT,
        text=True,
    ).splitlines()
    assert not changed, changed
    health = {}
    for label, url in (
        ("local", "http://127.0.0.1:8787/api/health"),
        ("tailscale_verified_tls", "https://jakes-mac-mini.tailc4d343.ts.net/api/health"),
    ):
        status = subprocess.check_output(
            [
                "curl",
                "--silent",
                "--show-error",
                "--fail",
                "--max-time",
                "15",
                "--noproxy",
                "*",
                "--output",
                "/dev/null",
                "--write-out",
                "%{http_code}",
                url,
            ],
            text=True,
        )
        assert status == "200"
        health[label] = status
    with urlopen("http://127.0.0.1:11434/api/version", timeout=10) as response:
        runtime = json.load(response)
    assert runtime["version"] == "0.35.0"
    result = {
        "frozen_files_verified": len(manifest["files"]),
        "earlier_committed_evidence_files_byte_preserved": preserved,
        "all_25_reports_and_native_protocols_verified": True,
        "remaining_29_declared_children_unexecuted": True,
        "production_source_changes": changed,
        "health": health,
        "runtime": runtime,
        "deployment_service_restart_merge_or_extra_inference": False,
    }
    write("verification.json", result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
