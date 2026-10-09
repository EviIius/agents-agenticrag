"""Reject invalid provenance; make no semantic-truth assertion."""

import json
from typing import Any

import pytest

from evals.reliability.extractive.contract import validate

SOURCES = [
    {"n": 1, "passages": [{"text": "Cedar marker is 7 cm. Cost is unknown."}]},
    {"n": 2, "passages": [{"text": "Pine marker is 9 cm."}]},
]


def test_exact_quote_accepts_only_whitespace_equivalence() -> None:
    entry = {"source": 1, "quote": "Cedar marker\nis 7 cm."}
    assert validate(json.dumps({"excerpts": [entry]}), SOURCES) == [entry]
    assert validate('{"excerpts": []}', SOURCES) == []


@pytest.mark.parametrize(
    "entry",
    [
        {"source": 1, "quote": "Cedar marker is 70 cm."},
        {"source": 1, "quote": "Pine marker is 7 cm."},
        {"source": 2, "quote": "Cedar marker is 7 cm."},
        {"source": 1, "quote": "Cedar marker is 7 CM."},
        {"source": 3, "quote": "Cedar marker is 7 cm."},
        {"source": True, "quote": "Cedar marker is 7 cm."},
        {"source": 1, "quote": "Cedar marker is 7 cm.", "answer": "Safe"},
        {"source": 1, "quote": "<script>alert(1)</script>"},
        {"source": 1, "quote": "[Cedar](https://example.com) marker is 7 cm."},
        {"source": 1, "quote": "Cedar marker is 7 cm. Pine marker is 9 cm."},
        {"source": 1, "quote": " "},
        {"source": 1, "quote": 7},
    ],
)
def test_invalid_entry_rejects_the_whole_response(entry: dict[str, Any]) -> None:
    valid = {"source": 1, "quote": "Cedar marker is 7 cm."}
    with pytest.raises(ValueError):
        validate(json.dumps({"excerpts": [valid, entry]}), SOURCES)


@pytest.mark.parametrize(
    "raw",
    ["[]", '{"answer": "7 cm"}', '{"excerpts": [], "answer": "7 cm"}', "not JSON"],
)
def test_invalid_response_shape_is_rejected(raw: str) -> None:
    with pytest.raises(ValueError):
        validate(raw, SOURCES)


def test_quote_budget_is_per_source_and_counts_repetitions() -> None:
    entry = {"source": 1, "quote": "Cedar marker is 7 cm."}
    with pytest.raises(ValueError):
        validate(json.dumps({"excerpts": [entry] * 6}), SOURCES)
    with pytest.raises(ValueError):
        validate(json.dumps({"excerpts": [entry] * 11}), SOURCES)


def test_exact_provenance_does_not_prove_relevance_or_source_truth() -> None:
    # A caller asking about Pine could still receive a genuine Cedar quote.
    # The validator deliberately does not label that answer correct or complete.
    entry = {"source": 1, "quote": "Cedar marker is 7 cm."}
    assert validate(json.dumps({"excerpts": [entry]}), SOURCES) == [entry]


@pytest.mark.parametrize(
    ("quote", "text"),
    [("7", "70"), ("24", "24.5"), ("5", "24.5"), ("24", "-24"), ("Cedar", "Cedarwood")],
)
def test_partial_word_or_number_does_not_establish_a_new_value(quote: str, text: str) -> None:
    sources = [{"n": 1, "passages": [{"text": text}]}]
    with pytest.raises(ValueError):
        validate(json.dumps({"excerpts": [{"source": 1, "quote": quote}]}), sources)


def test_real_signed_number_is_preserved() -> None:
    sources = [{"n": 1, "passages": [{"text": "Offset is -24.5 mm."}]}]
    entry = {"source": 1, "quote": "-24.5 mm."}
    assert validate(json.dumps({"excerpts": [entry]}), sources) == [entry]
