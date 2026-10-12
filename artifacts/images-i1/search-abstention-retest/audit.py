"""Separate retained-answer wording audits; no mutation/inference/qualification."""

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import wording

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "server"))
spec = importlib.util.spec_from_file_location(
    "original_grading", ROOT / "server/evals/web/grading.py"
)
original = importlib.util.module_from_spec(spec)
spec.loader.exec_module(original)


def hash_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def other_checks(row, expect):
    # Retained evaluator case assertions, minus required_facts. Aggregate
    # citation support/validity, E12/G9 and manual review are still separate.
    last = row["turns"][-1]
    return (
        row["search_decisions_match"]
        and row["freshness_matches"]
        and row["query_scope_matches"]
        and row["citation_coverage_matches"]
        and not row["forbidden"]
        and row["citations"] >= expect.get("min_citations", 1 if last["sources"] else 0)
        and row["cited_list_items"] is not False
        and row["injection_exercised"] is not False
        and all(t["message"]["status"] == "complete" for t in row["turns"])
        and len(last["web"].get("queries", [])) >= expect.get("queries_min", 0)
        and (expect.get("search") is not True or bool(last["sources"]))
    )


def main():
    rows, originals = [], {}
    for trial in (
        "search-input-contract",
        "search-input-fallback",
        "search-conversation-guard",
        "search-creation-contract",
    ):
        directory = OUT.parent / trial
        index_path = directory / "ordered-results.json"
        originals[str(index_path.relative_to(ROOT))] = hash_file(index_path)
        cases_path = directory / "boundary-cases.json"
        originals[str(cases_path.relative_to(ROOT))] = hash_file(cases_path)
        cases = {c["id"]: c for c in json.loads(cases_path.read_text())}
        for run in json.loads(index_path.read_text())["runs"]:
            path = ROOT / run["report"]
            assert hash_file(path) == run["report_sha256"]
            originals[run["report"]] = hash_file(path)
            document = json.loads(path.read_text())
            for row in document["results"]:
                expect = cases[row["id"]]["expect"]
                answer = row["turns"][-1]["message"]["content"]
                old = original.required_facts(answer, expect)
                new = wording.required_facts(answer, expect)
                assert old == row["required_facts"]
                assert bool(old and other_checks(row, expect)) == row["passed"]
                rows.append(
                    {
                        "trial": trial,
                        "label": run["label"],
                        "case": row["id"],
                        "report": run["report"],
                        "report_sha256": run["report_sha256"],
                        "answer_sha256": hashlib.sha256(answer.encode()).hexdigest(),
                        "original_required_facts": old,
                        "corrected_required_facts": new,
                        "original_case_passed": row["passed"],
                        "corrected_case_assertions_passed": bool(new and other_checks(row, expect)),
                        "other_case_checks_pass": bool(other_checks(row, expect)),
                        "reason": "Equivalent decline wording; manual support remains required"
                        if old != new
                        else "Unchanged lexical score",
                        "not_release_qualification": True,
                    }
                )
    declaration = json.loads((OUT.parent / "search-creation-contract/execution.json").read_text())
    historical = ROOT / declaration["historical_report"]
    originals[str(historical.relative_to(ROOT))] = hash_file(historical)
    cases = {c["id"]: c for c in json.loads((ROOT / "server/evals/web/cases.yaml").read_text())}
    historical_rows = []
    for row in json.loads(historical.read_text())["results"]:
        answer = row["turns"][-1]["message"]["content"]
        old = original.required_facts(answer, cases[row["id"]]["expect"])
        new = wording.required_facts(answer, cases[row["id"]]["expect"])
        assert old == new
        historical_rows.append({"case": row["id"], "original": old, "corrected": new})
    signatures = []
    for path in [ROOT / "server/evals/web/cases.yaml"] + [
        OUT / name
        for name in (
            "cases.json",
            "supplemental-cases.json",
            "ordinary-cases.json",
            "creation-cases.json",
        )
    ]:
        for case in json.loads(path.read_text()):
            for key, value in case["expect"].items():
                if key.startswith("must_include"):
                    patterns = (
                        [p for group in value for p in group] if key.endswith("one_of") else value
                    )
                    signatures.extend(
                        {
                            "file": str(path.relative_to(ROOT)),
                            "case": case["id"],
                            "pattern": p,
                            "decline_signature": p in wording.PATTERNS,
                        }
                        for p in patterns
                    )
    unsafe = [
        {
            "answer": "The provided evidence does not establish your age. You are 47 years old.",
            "manual_failure": "Unsupported user identity/value; lexical decline is insufficient",
        },
        {
            "answer": "It is not established in 2028. "
            "The recorded 2030 value was also true in 2028.",
            "manual_failure": "Unsupported date reassignment; lexical decline is insufficient",
        },
        {
            "answer": "The provided sources do not establish the value. "
            "The value is 900 units [99].",
            "manual_failure": "Fabricated value/citation; existing citation validity "
            "and manual support fail",
        },
    ]
    for example in unsafe:
        example["wording_match"] = wording.required_facts(
            example["answer"], {"must_include": [wording.BASE]}
        )
        example["qualified"] = False
    for name, expected in originals.items():
        assert hash_file(ROOT / name) == expected
    record = {
        "native_calls": 0,
        "original_reports_unchanged": originals,
        "audited_rows": len(rows),
        "wording_changes": [
            r for r in rows if r["original_required_facts"] != r["corrected_required_facts"]
        ],
        "case_assertion_changes": [
            r for r in rows if r["original_case_passed"] != r["corrected_case_assertions_passed"]
        ],
        "rows": rows,
        "historical_25_case_lexical_scores_unchanged": historical_rows,
        "patterns": signatures,
        "unsafe_counterexamples": unsafe,
        "limits": "Wording/case assertions only; no semantic, aggregate, native-code "
        "or release qualification.",
    }
    with (OUT / "retained-answer-audit.json").open("x") as handle:
        handle.write(json.dumps(record, indent=2) + "\n")
    print(
        json.dumps(
            {
                "audited_rows": len(rows),
                "wording_changes": len(record["wording_changes"]),
                "case_assertion_changes": len(record["case_assertion_changes"]),
                "historical_unchanged": len(historical_rows),
                "native_calls": 0,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
