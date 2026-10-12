"""Audit provenance and retained non-wording failure gates without inference."""

import copy
import json

import audit
import wording


def stopped():
    prior = audit.OUT.parent / "search-creation-contract"
    run = json.loads((prior / "ordered-results.json").read_text())["runs"][-1]
    row = json.loads((audit.ROOT / run["report"]).read_text())["results"][0]
    case = next(c for c in json.loads((prior / "cases.json").read_text()) if c["id"] == row["id"])
    return row, case["expect"]


def test_retained_decline_is_only_wording_change():
    row, expect = stopped()
    answer = row["turns"][-1]["message"]["content"]
    assert not row["required_facts"] and not row["passed"]
    assert wording.required_facts(answer, expect) and audit.other_checks(row, expect)


def test_missing_lookup_or_evidence_cannot_be_regraded_to_pass():
    row, expect = stopped()
    no_lookup = copy.deepcopy(row)
    no_lookup["search_decisions_match"] = False
    assert not audit.other_checks(no_lookup, expect)
    no_evidence = copy.deepcopy(row)
    no_evidence["turns"][-1]["sources"] = []
    assert not audit.other_checks(no_evidence, expect)


def test_existing_forbidden_and_incomplete_gates_remain():
    row, expect = stopped()
    forbidden = copy.deepcopy(row)
    forbidden["forbidden"] = ["synthetic attack"]
    assert not audit.other_checks(forbidden, expect)
    incomplete = copy.deepcopy(row)
    incomplete["turns"][-1]["message"]["status"] = "interrupted"
    assert not audit.other_checks(incomplete, expect)


def test_code_failure_and_original_historical_scores_are_not_excused():
    prior = audit.OUT.parent / "search-conversation-guard"
    run = json.loads((prior / "ordered-results.json").read_text())["runs"][-1]
    row = json.loads((audit.ROOT / run["report"]).read_text())["results"][0]
    case = next(
        c for c in json.loads((prior / "ordinary-cases.json").read_text()) if c["id"] == row["id"]
    )
    assert not wording.required_facts(row["turns"][-1]["message"]["content"], case["expect"])
    assert not audit.other_checks(row, case["expect"])
    record = json.loads((audit.OUT / "retained-answer-audit.json").read_text())
    assert record["audited_rows"] == 183
    assert len(record["wording_changes"]) == len(record["case_assertion_changes"]) == 2
    assert len(record["historical_25_case_lexical_scores_unchanged"]) == 25
    assert all(
        r["original"] == r["corrected"]
        for r in record["historical_25_case_lexical_scores_unchanged"]
    )
    assert all(not r["qualified"] for r in record["unsafe_counterexamples"])
