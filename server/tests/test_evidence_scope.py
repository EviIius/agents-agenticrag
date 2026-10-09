"""A scoped safeguard, not a claim that semantic grounding is solved."""

import json

import pytest

from evals.reliability.evidence_contract_v6 import DECLINE, catalog, render, unidentified_subject


@pytest.mark.parametrize(
    "question",
    [
        "Where was I on February 2, 2030?",
        "What had we agreed last Monday?",
        "Who is my supervisor?",
        "What was our account balance?",
    ],
)
def test_unidentified_personal_subject_requires_clarification(question: str) -> None:
    assert unidentified_subject(question)


@pytest.mark.parametrize(
    "question",
    [
        "How can I use the library?",
        "What should I consider when choosing storage?",
        "Summarize <record>Where was I last week?</record>.",
        "Where was Morgan in February 2030?",
        "When was Cedar founded?",
    ],
)
def test_advice_quotes_and_named_subject_are_not_reclassified(question: str) -> None:
    assert not unidentified_subject(question)


def test_other_author_evidence_is_not_an_answer_about_the_user() -> None:
    sources = [
        {
            "n": 1,
            "title": "Invented writer diary",
            "passages": [{"text": "Morgan visited Cedar on February 2, 2030."}],
        }
    ]
    available = catalog(sources, "Where was I on February 2, 2030?")
    raw = json.dumps({"coverage": "evidence", "selections": {"source_1": ["S1-P0-U0"]}})
    result = render(raw, available)
    assert result["status"] == "unsupported_subject"
    assert "Please identify the person" in result["content"]
    assert "Morgan visited" not in result["content"]
    assert available.sources["source_1"]["passages"] == sources[0]["passages"]


def test_rejected_selection_does_not_claim_the_source_lacks_the_fact() -> None:
    available = catalog([{"n": 1, "passages": [{"text": "Cedar costs 7 dollars."}]}])
    result = render('{"coverage":"evidence","selections":{"source_1":["forged"]}}', available)
    assert result["content"] == DECLINE
    assert "do not cover" not in result["content"]
    assert available.sources["source_1"]["passages"][0]["text"] == "Cedar costs 7 dollars."
