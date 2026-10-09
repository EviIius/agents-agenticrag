"""Novel synthetic fields/context; semantic completeness remains an eval gate."""

import json
from typing import Any

import pytest

from evals.reliability.evidence_contract import DECLINE, catalog, render, validate


def source(text: str, **metadata: Any) -> dict[str, Any]:
    return {
        "n": 1,
        "title": "Invented Cedar sheet",
        "published_at": "2025-02-03",
        "fetched_at": "2026-10-09",
        "passages": [{"heading": "", "text": text}],
        **metadata,
    }


def response(*ids: str, coverage: str = "evidence") -> str:
    return json.dumps({"coverage": coverage, "selections": {"source_1": list(ids)}})


def test_pronoun_keeps_subject_negative_property_and_original_decimal() -> None:
    text = "Cedar is not waterproof. It has offset -24.5 mm."
    available = catalog([source(text)])
    unit = available.units["source_1"][1]
    assert unit["paragraph"] == text
    assert unit["required_context"] == "Cedar is not waterproof."
    result = render(response(unit["id"]), available)
    assert "not waterproof" in result["content"] and "24\\.5 mm" in result["content"]
    assert result["verified_answer"] is False


def test_first_sentence_pronoun_is_not_assigned_a_subject_from_a_title() -> None:
    available = catalog([source("They are both retired.")])
    assert render(response(available.units["source_1"][0]["id"]), available)["status"] == "rejected"


def test_table_fields_blanks_repeated_headers_and_caption_stay_bound() -> None:
    text = (
        "Permit ends in 2031.\n\n| Item | Cost | Year |\n| --- | --- | --- |\n"
        "| Cedar | | 2030 |\n| Item | Cost | Year |\n| --- | --- | --- |\n"
        "| Pine | -2.5 | 2031 |"
    )
    available = catalog([source(text)])
    rows = [u for u in available.units["source_1"] if u["kind"] == "row"]
    assert len(rows) == 2
    assert rows[0]["cells"] == ["Cedar", "", "2030"]
    assert rows[1]["cells"] == ["Pine", "-2.5", "2031"]
    assert rows[0]["header"] == ["Item", "Cost", "Year"]
    assert "Permit ends in 2031." in rows[0]["required_context"]
    assert available.sources["source_1"]["passages"][0]["text"] == text


def test_two_requested_rows_can_be_selected_without_one_unit_per_source_limit() -> None:
    available = catalog([source("| Item | Value |\n| --- | --- |\n| Cedar | 0 |\n| Pine | 3 |")])
    rows = available.units["source_1"]
    result = render(response(*(u["id"] for u in rows)), available)
    assert result["status"] == "evidence"
    assert "Cedar" in result["content"] and "Pine" in result["content"]
    assert result["content"].count("| [1] |") == 2


def test_extracted_infobox_value_cannot_become_a_column_label_for_other_rows() -> None:
    available = catalog(
        [source("| Dates | 2030 |\n| --- | --- |\n| Winner | Pine |\n| Offset | -24.5 |")]
    )
    assert render(response(available.units["source_1"][0]["id"]), available)["status"] == "rejected"


def test_publication_retrieval_dates_and_full_context_are_distinct() -> None:
    original = source("Cedar allows 7 days only before July 2030.")
    available = catalog([original])
    original["passages"][0]["text"] = "Mutated"
    assert available.sources["source_1"]["published_at"] == "2025-02-03"
    assert available.sources["source_1"]["fetched_at"] == "2026-10-09"
    assert "only before July 2030" in available.units["source_1"][0]["text"]


@pytest.mark.parametrize(
    "raw",
    [
        '{"coverage":"evidence","selections":{"source_1":["S2-P0-U0"]}}',
        '{"coverage":"evidence","selections":{"source_1":["S1-P0-U0","S1-P0-U0"]}}',
        '{"coverage":"unsupported","selections":{"source_1":["S1-P0-U0"]}}',
        '{"coverage":"evidence","selections":{"source_1":[]}}',
        '{"coverage":"evidence","coverage":"unsupported","selections":{"source_1":[]}}',
        '{"coverage":"unsupported","selections":{"source_1":[]},"answer":"Cedar is safe"}',
    ],
)
def test_wrong_source_duplicate_forged_or_contradictory_output_declines(raw: str) -> None:
    available = catalog([source("Cedar permits 7 days.")])
    result = render(raw, available)
    assert result["status"] == "rejected" and result["content"] == DECLINE
    assert result["units"] == []


def test_unsupported_partial_and_valid_selection_are_not_verified_answers() -> None:
    available = catalog([source("Cedar costs 7 dollars.")])
    unit = available.units["source_1"][0]
    missing = render(response(coverage="unsupported"), available)
    assert missing["status"] == "unsupported" and missing["content"] == DECLINE
    partial = render(response(unit["id"], coverage="partial"), available)
    assert "unsupported details remain unknown" in partial["content"]
    assert partial["verified_answer"] is False
    # A real Cedar ID can still be irrelevant to a question about Pine.
    assert validate(response(unit["id"]), available)[0] == "evidence"


def test_source_markup_cannot_inject_links_html_or_reference_numbers() -> None:
    available = catalog([source("Cedar label [900](https://example.invalid) <img src=x>.")])
    unit = available.units["source_1"][0]
    result = render(response(unit["id"]), available)
    assert "\\[900\\]" in result["content"]
    assert "&lt;img" in result["content"] and "<img" not in result["content"]
    assert result["content"].endswith("[1]")


def test_budget_failure_is_explicit_and_never_silently_drops_units() -> None:
    available = catalog([source(" ".join(["Cedar"] * 26) + ".")])
    result = render(response(available.units["source_1"][0]["id"]), available)
    assert result["status"] == "rejected"
    assert result["reason"] == "Source quotation budget exceeded"
