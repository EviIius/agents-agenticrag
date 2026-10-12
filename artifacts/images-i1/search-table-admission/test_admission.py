"""Admission safety and actual before/after evidence, without inference."""

import hashlib
import importlib.util
import json
from pathlib import Path

import admission
import pytest

from app.schemas import Passage

ROOT = admission.ROOT
TABLE = """| Entity | Recorded Weight | Unit |
| --- | --- | --- |
| Celadon | 7 | kg |
| Brindle | 9 | kg |
"""
QUESTION = "Compare the recorded weight for each entity."


def passage(text, ordinal=0, url="https://example.org/synthetic", **values):
    return Passage(source_url=url, ord=ordinal, text=text, **values)


def ranked(table=TABLE):
    return [
        (passage("Overview of the entity measurements", 0), 1.0),
        (passage("An introduction to measurement records", 1), 0.9),
        (passage("How the records were collected", 2), 0.8),
        (passage(table, 3), 0.7),
    ]


def test_data_replaces_one_caption_without_mutating_original_passages():
    rows = ranked()
    original = [p.model_dump() for p, _ in rows]
    before = admission.original_select(rows, 1500, 6)
    after = admission.select(rows, 1500, 6, question=QUESTION)
    assert [p.ord for p in before[0]] == [0, 1, 2]
    assert [p.ord for p in after[0]] == [0, 1, 3]
    assert after[0][-1] is rows[-1][0] and after[0][-1].text == TABLE
    assert [p.model_dump() for p, _ in rows] == original


@pytest.mark.parametrize(
    "text",
    [
        "| Entity | Recorded Weight |\n| --- | --- |\n| Celadon | 7 |",
        "A short exact caption.\n\n" + TABLE,
        "| Entity | Recorded Weight |\n| :--- | ---: |\n| Ash | - |\n| Dune | |",
        "| **Entity** | **Recorded Weight** |\n| --- | --- |\n| Ash | 0 |",
        "| Entity | Recorded Weight | Unit |\n| --- | --- | --- |\n| A\\|B | 4 | kg |",
    ],
)
def test_complete_literal_headers_and_values_are_admitted(text):
    assert admission.relevant_table(text, QUESTION)


@pytest.mark.parametrize(
    "text",
    [
        "A caption containing Entity and Recorded Weight but no data",
        "| Entity | Recorded Weight |",  # no separator/body
        "| Entity | Recorded Weight |\n| Ash | 3 |",  # invented header delimiter absent
        "| Entity | Recorded Weight |\n| --- | --- |",  # no rows
        "| Entity | Recorded Weight |\n| --- | --- |\n| Ash |",  # uneven row
        "| 2024 | Ash |\n| --- | --- |\n| Dune | 3 |",  # first numerical data row
        "| Entity | Entity |\n| --- | --- |\n| Ash | Dune |",  # ambiguous columns
        "| Entity | Recorded Weight | | |\n| --- | --- | --- | --- |\n| Ash | 3 | | |",
        "| Fruit | Count |\n| --- | --- |\n| Pear | 3 |",  # unrelated
        "| Entity | Notes |\n| --- | --- |\n| Ash | 3 |",  # one generic identity token
        "| Entity | [Recorded Weight](https://example.org) |\n| --- | --- |\n| Ash | 3 |",
        "| <Entity> | Recorded Weight |\n| --- | --- |\n| Ash | 3 |",
        "```text\n" + TABLE + "```",
        "~~~\n" + TABLE + "~~~",
    ],
)
def test_ambiguous_unrelated_code_and_pseudo_tables_do_not_get_preference(text):
    assert not admission.relevant_table(text, QUESTION)


def test_missing_literal_role_does_not_gain_relevance_from_row_values():
    text = "| Name | Description |\n| --- | --- |\n| Entity | Recorded Weight |"
    assert not admission.relevant_table(text, QUESTION)


def test_existing_table_and_fenced_code_are_not_displaced():
    rows = [
        (passage("| Name | Count |\n| --- | --- |\n| Ash | 3 |", i), 1 - i / 10) for i in range(3)
    ]
    rows.append((passage(TABLE, 3), 0.5))
    assert admission.select(rows, 1500, 6, question=QUESTION) == admission.original_select(
        rows, 1500, 6
    )
    code = [(passage("```python\nreturn 7\n```", i), 1 - i / 10) for i in range(3)]
    code.append((passage(TABLE, 3), 0.5))
    assert admission.select(code, 1500, 6, question=QUESTION) == admission.original_select(
        code, 1500, 6
    )


def test_already_admitted_relevant_data_keeps_existing_selection():
    rows = [
        (passage(TABLE, 0), 1),
        (passage("Background", 1), 0.9),
        (passage(TABLE, 2), 0.8),
    ]
    assert admission.select(rows, 1500, 6, question=QUESTION) == admission.original_select(
        rows, 1500, 6
    )


def test_over_budget_data_does_not_replace_other_sources_or_raise_limit():
    rows = ranked(TABLE.replace("Celadon", "C" * 2000))
    before = admission.original_select(rows, 180, 6)
    assert admission.select(rows, 180, 6, question=QUESTION) == before


def test_over_length_data_is_not_admitted_even_with_spare_budget():
    rows = ranked(TABLE.replace("Celadon", "C" * 3100))
    assert admission.select(rows, 12000, 6, question=QUESTION) == admission.original_select(
        rows, 12000, 6
    )


def test_zero_score_table_and_ambiguous_passage_ids_keep_baseline():
    rows = ranked()
    rows[-1] = rows[-1][0], 0
    assert admission.select(rows, 1500, 6, question=QUESTION) == admission.original_select(
        rows, 1500, 6
    )
    rows = ranked()
    rows[-1] = passage(TABLE, 2), 0.7
    assert admission.select(rows, 1500, 6, question=QUESTION) == admission.original_select(
        rows, 1500, 6
    )


def test_source_order_eligibility_and_source_cap_do_not_expand():
    rows = []
    for i in range(9):
        rows += [
            (
                p.model_copy(update={"source_url": f"https://example.org/{i}"}),
                score - i * 0.01,
            )
            for p, score in ranked()
        ]
    before = admission.original_select(rows, 600, 4)
    after = admission.select(rows, 600, 4, question=QUESTION)
    assert [g[0].source_url for g in after] == [g[0].source_url for g in before]
    assert len(after) <= 4 and all(len(g) <= 3 for g in after)
    assert sum(admission.cost(p, 0.3) for g in after for p in g) <= 600


def test_numeric_selection_annotations_cannot_be_replaced_by_raw_data():
    rows = [(p.model_copy(update={"selection_applied": True}), score) for p, score in ranked()[:3]]
    rows.append(ranked()[-1])
    assert admission.select(rows, 1500, 6, question=QUESTION) == admission.original_select(
        rows, 1500, 6
    )


@pytest.mark.parametrize("ratio", [0.05, 0.3, 1.0])
def test_existing_budget_is_respected_for_valid_token_estimates(ratio):
    after = admission.select(ranked(), 300, 6, ratio, question=QUESTION)
    assert sum(admission.cost(p, ratio) for group in after for p in group) <= 300


def test_prose_and_empty_selection_remain_identical():
    rows = [(passage("Plain prose.", i), 1 - i / 10) for i in range(5)]
    assert admission.select(
        rows, 1500, 6, question="Summarize the history."
    ) == admission.original_select(rows, 1500, 6)
    assert admission.select([], 1500, 6, question=QUESTION) == []


def test_actual_omitted_table_replay_preserves_all_23_positive_entries():
    module_path = ROOT / "artifacts/images-i1/search-task-evidence-audit/audit.py"
    spec = importlib.util.spec_from_file_location("original_evidence_audit", module_path)
    audit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit)
    _path, document = audit.report()
    kept = audit.retained_turns(document)[("nba-all-losses", 0)]
    with audit.no_network():
        record, pages = audit.case_trace("nba-all-losses", kept, document)
    from app.search.chunk import chunk
    from app.search.fixtures import Fixtures
    from app.search.rank import rank

    fixture, _saved, candidates = audit.recorded_candidates(
        Path(document["fixture_root"]) / "nba-all-losses/0"
    )
    assert isinstance(fixture, Fixtures)
    ps = [
        p
        for result in candidates
        if result.url in pages
        for p in chunk(result.url, pages[result.url].text)
    ]
    ranks = rank(
        ps,
        kept["turn"]["question"] + " " + " ".join(kept["turn"]["web"]["queries"]),
        [c.url for c in candidates],
    )
    after = admission.select(
        ranks,
        record["source_token_budget"],
        6,
        record["calibrated_context_ratio"],
        question=kept["turn"]["question"],
    )
    target = next(
        p for group in after for p in group if "finals_lost.htm" in p.source_url and p.ord == 3
    )
    original = next(p for p in ps if p.source_url == target.source_url and p.ord == 3)
    assert target is original and target.model_dump() == original.model_dump()
    old_trace = json.loads(
        (
            ROOT / "artifacts/images-i1/search-task-evidence-audit/nba-all-losses-trace.json"
        ).read_text()
    )
    original_sha = next(
        c["sha256"]
        for pg in old_trace["pages"]
        if pg["url"] == target.source_url
        for c in pg["chunks"]
        if c["ord"] == 3
    )
    assert hashlib.sha256(target.text.encode()).hexdigest() == original_sha
    table = audit.markdown_tables(target.text)[0]
    assert len(table["rows"]) == 28 and len(table["header"]) == 7
    column = table["header"].index("Finals Lost")
    assert sum(row[column].isdigit() and int(row[column]) > 0 for row in table["rows"]) == 23
