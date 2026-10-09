"""Evidence text stays inert without breaking exact values or citation placement."""

import json

from app.search.citations import cited, normalize
from evals.library.run_eval import grade
from evals.reliability.evidence_contract_v8 import catalog, render, safe_text


def test_exact_values_still_bind_to_their_source_citation() -> None:
    sources = [{"n": 1, "passages": [{"text": "Offset is -24.5 mm. Code is CEDAR-42."}]}]
    available = catalog(sources)
    identifiers = [unit["id"] for unit in available.units["source_1"]]
    text = render(
        json.dumps({"coverage": "evidence", "selections": {"source_1": identifiers}}), available
    )["content"]
    outcome = grade({"facts": ["-24.5", "CEDAR-42"]}, text, sources, text)
    assert outcome["facts_all"] and outcome["citation_support"]
    assert r"24\.5" not in text and r"CEDAR\-42" not in text


def test_source_html_links_and_bracket_numbers_cannot_create_active_markup() -> None:
    text = safe_text("<img src=x> [click](https://example.invalid) [900] **strong**")
    assert "<img" not in text and "[click]" not in text and "[900]" not in text
    assert "&#91;900&#93;" in text
    assert cited(text + " [1]") == {1}
    assert normalize(text, 1) == text


def test_table_pipe_and_sign_survive_with_no_extra_column() -> None:
    text = safe_text("A|B -24.5", in_table=True)
    assert text == r"A\|B -24.5"


def test_literal_source_reference_does_not_cite_a_different_source() -> None:
    sources = [{"n": 1, "passages": [{"text": "Label [2] has value 3."}]}]
    available = catalog(sources)
    identifiers = [unit["id"] for unit in available.units["source_1"]]
    text = render(
        json.dumps({"coverage": "evidence", "selections": {"source_1": identifiers}}), available
    )["content"]
    assert cited(text) == {1}
    assert "&#91;2&#93;" in text
