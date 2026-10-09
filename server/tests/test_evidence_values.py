"""Original values survive Markdown rendering without accepting active source markup."""

import json

from app.search.citations import normalize
from evals.reliability.evidence_contract_v7 import catalog, render, safe_text


def test_decimal_negative_sign_and_literal_identifier_are_not_escaped() -> None:
    available = catalog([{"n": 1, "passages": [{"text": "Offset is -24.5 mm. Code is CEDAR-42."}]}])
    ids = [u["id"] for u in available.units["source_1"]]
    raw = json.dumps({"coverage": "evidence", "selections": {"source_1": ids}})
    text = render(raw, available)["content"]
    assert "-24.5" in text and "CEDAR-42" in text
    assert r"24\.5" not in text and r"CEDAR\-42" not in text


def test_source_backticks_html_and_links_stay_inside_a_literal_span() -> None:
    original = "`<img src=x> [label](https://example.invalid) ``"
    text = safe_text(original)
    assert text == "``` " + original + " ```"


def test_table_request_keeps_original_prose_units_and_per_row_citations() -> None:
    available = catalog(
        [{"n": 1, "passages": [{"text": "Cedar costs 7 dollars. Pine costs 9 dollars."}]}],
        "Show the prices in a table.",
    )
    ids = [u["id"] for u in available.units["source_1"]]
    text = render(json.dumps({"coverage": "evidence", "selections": {"source_1": ids}}), available)[
        "content"
    ]
    assert "| Evidence | Citation |" in text
    assert "Cedar costs 7 dollars." in text and "Pine costs 9 dollars." in text
    assert text.count("| [1] |") == 2
    assert available.units["source_1"][0]["text"] == "Cedar costs 7 dollars."


def test_backticks_are_rejected_before_the_legacy_citation_scanner() -> None:
    available = catalog([{"n": 1, "passages": [{"text": "Literal `value` [1]."}]}])
    ids = [u["id"] for u in available.units["source_1"]]
    outcome = render(
        json.dumps({"coverage": "evidence", "selections": {"source_1": ids}}), available
    )
    assert outcome["status"] == "rejected"
    assert outcome["units"] == []
    assert "backticks" in outcome["reason"]


def test_source_bracket_numbers_remain_literal_after_citation_normalization() -> None:
    available = catalog([{"n": 1, "passages": [{"text": "Offset is -24.5 mm. Label is [900]."}]}])
    ids = [u["id"] for u in available.units["source_1"]]
    text = render(json.dumps({"coverage": "evidence", "selections": {"source_1": ids}}), available)[
        "content"
    ]
    assert normalize(text, 1) == text
    assert "-24.5" in text and "[900]" in text
