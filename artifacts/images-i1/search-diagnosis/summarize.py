"""Read retained diagnosis outputs; never invoke a model or rewrite a report."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "server"), str(ROOT / "server/evals/web")]
from run_eval import support  # noqa: E402


def read(path):
    return json.loads(path.read_text())


def planner_requests(label):
    requests = {}
    for line in (OUT / label / "wire.jsonl").read_text().splitlines():
        row = json.loads(line)
        body = json.loads(row["body"]) if isinstance(row["body"], str) else row["body"]
        if not body.get("format"):
            continue
        latest = body["messages"][-1]["content"].split("Latest user message:\n", 1)[1]
        requests.setdefault(latest, []).append(row["sha256"])
    return requests


def case_summary(result):
    lexical = []
    for turn in result["turns"]:
        lexical.extend(support(turn["message"]["content"], turn["sources"])
                       or ([0.0] if turn["sources"] else []))
    return {
        "passed": result["passed"],
        "required_facts": result["required_facts"],
        "search_decisions_match": result["search_decisions_match"],
        "injection_exercised": result["injection_exercised"],
        "citations": result["citations"],
        "lexical_support_mean": sum(lexical) / len(lexical) if lexical else None,
        "lexical_support_values": lexical,
        "web_statuses": [t["web"]["status"] for t in result["turns"]],
        "planner_fallbacks": [t["web"]["plan_fallback"] for t in result["turns"]],
    }


def main():
    ordered = read(OUT / "ordered-results.json")
    assert len(ordered["runs"]) == len(ordered["declared_order"]) == 8
    paths = {r["label"]: r["report"] for r in ordered["runs"]}
    paths["historical-accepted"] = (
        "server/evals/web/reports/2026-10-06-115508-"
        "qwen3-30b-a3b-instruct-2507-q4_K_M-offline-keyword.json"
    )
    paths["original-i1-failure"] = (
        "server/evals/web/reports/2026-10-11-021344-"
        "qwen3-30b-a3b-instruct-2507-q4_K_M-offline-keyword.json"
    )
    reports = {label: read(ROOT / path) for label, path in paths.items()}
    cases = {}
    for label in ("historical-accepted", "original-i1-failure", "full-baseline", "full-candidate"):
        cases[label] = {r["id"]: case_summary(r) for r in reports[label]["results"]}
    baseline, candidate = cases["full-baseline"], cases["full-candidate"]
    assert baseline.keys() == candidate.keys()
    rows = []
    for case in baseline:
        b, c = baseline[case], candidate[case]
        bs, cs = b["lexical_support_mean"], c["lexical_support_mean"]
        rows.append({"id": case, "baseline": b, "candidate": c,
                     "pass_flip": b["passed"] != c["passed"],
                     "support_delta": cs - bs if cs is not None and bs is not None else None})
    b_requests, c_requests = planner_requests("full-baseline"), planner_requests("full-candidate")
    wire_rows = [{"question": q, "baseline": b_requests[q], "candidate": c_requests.get(q),
                  "identical": b_requests[q] == c_requests.get(q)} for q in b_requests]
    result = {
        "reports": paths,
        "metrics": {label: reports[label]["metrics"] for label in cases},
        "historical_and_original_case_results": {
            label: cases[label] for label in ("historical-accepted", "original-i1-failure")
        },
        "fresh_case_comparison": rows,
        "fresh_pass_flips": [r["id"] for r in rows if r["pass_flip"]],
        "fresh_failed_cases": {
            label: [case for case, summary in cases[label].items() if not summary["passed"]]
            for label in ("full-baseline", "full-candidate")
        },
        "full_planner_request_comparison": wire_rows,
        "all_full_planner_requests_identical": all(r["identical"] for r in wire_rows),
        "limits": (
            "Lexical token overlap is the unchanged grader's heuristic, not semantic claim support. "
            "The full candidate precedes baseline; output/prompt-cache effects and uncontrolled "
            "runtime sampling prevent interpreting latency differences as native-admission causation. "
            "Both fresh runs use the same controlled date, not the historical date. "
            "No release gate, case, corpus, prompt or accepted report is changed."
        ),
        "release_held": True,
    }
    (OUT / "comparison.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"pass_flips": result["fresh_pass_flips"],
                      "failures": result["fresh_failed_cases"],
                      "identical_planner_requests": result["all_full_planner_requests_identical"],
                      "planner_request_count": len(wire_rows)}, indent=2))


if __name__ == "__main__":
    main()
