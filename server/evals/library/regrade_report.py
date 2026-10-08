"""Regrade an unchanged synthetic baseline without making any model calls."""

import argparse
import hashlib
import json
from pathlib import Path

from run_eval import grade


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    original = args.report.read_bytes()
    baseline = json.loads(original)
    if baseline.get("synthetic_only") is not True or baseline.get("mode") != "full":
        raise SystemExit("Only a full synthetic Library report may be regraded.")
    cases_bytes = (Path(__file__).parent / "cases.yaml").read_bytes()
    if hashlib.sha256(cases_bytes).hexdigest() != baseline["cases_sha256"]:
        raise SystemExit("The case set changed; preserve the original comparison.")
    cases = {c["id"]: c for c in json.loads(cases_bytes)}
    results = []
    for result in baseline["results"]:
        turn = result["turns"][-1]
        results.append(
            {
                "id": result["id"],
                "kind": result["kind"],
                "grade": grade(
                    cases[result["id"]],
                    turn["message"]["content"],
                    turn["sources"],
                    turn["raw_answer"],
                ),
            }
        )
    answerable = [r for r in results if r["kind"] != "absent"]
    metrics = dict(baseline["metrics"])
    metrics["citation_support"] = sum(r["grade"]["citation_support"] for r in answerable) / len(
        answerable
    )
    output = {
        "synthetic_only": True,
        "mode": "regrade-existing-answers",
        "model_calls": 0,
        "original_report": args.report.name,
        "original_report_sha256": hashlib.sha256(original).hexdigest(),
        "grader_sha256": hashlib.sha256(
            Path(__file__).with_name("run_eval.py").read_bytes()
        ).hexdigest(),
        "reason": "Correct a false negative for a fact ending at sentence punctuation in its cited passage. Decimal and larger-number mismatches remain rejected by unit tests.",
        "metrics": metrics,
        "gates": {**baseline["gates"], "citations": metrics["citation_support"] == 1},
        "results": results,
    }
    path = args.report.with_name(args.report.stem + "-regraded.json")
    path.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps({"report": str(path), "metrics": metrics, "gates": output["gates"]}, indent=2))


if __name__ == "__main__":
    main()
