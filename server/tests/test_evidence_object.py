"""Prospective object schema only; no new native inference or failed-case repair."""

import json
from typing import Any

import pytest

from evals.reliability.evidence_contract_v13 import catalog
from evals.reliability.evidence_object_v14 import render, schema


def available() -> Any:
    return catalog(
        [
            {
                "n": 1,
                "passages": [{"text": "| | Item | Value |\n| --- | --- | --- |\n| 1 | Fern | 7 |"}],
            }
        ]
    )


def test_required_named_fields_replace_unsupported_positional_grammar() -> None:
    evidence = available()
    unit = evidence.units["source_1"][0]
    grammar = schema(evidence)
    fields = grammar["properties"]["selections"]["properties"][unit["id"]]
    assert fields["required"] == ["0", "1"]
    assert all(p == {"type": "boolean", "const": True} for p in fields["properties"].values())
    encoded = json.dumps(grammar)
    assert "prefixItems" not in encoded and "uniqueItems" not in encoded and "anyOf" not in encoded
    raw = json.dumps(
        {"coverage": "evidence", "selections": {unit["id"]: {"0": True, "1": True, "2": True}}}
    )
    result = render(raw, evidence)
    assert result["status"] == "evidence" and "Fern | 7" in result["content"]
    assert not result["verified_answer"]


@pytest.mark.parametrize(
    "fields",
    [
        {"1": True, "2": True},
        {"0": True, "2": True},
        {"0": True, "1": 1},
        {"0": True, "1": False},
        {"01": True, "2": True},
    ],
)
def test_missing_identity_and_forged_field_syntax_still_decline(fields: dict[str, Any]) -> None:
    evidence = available()
    raw = json.dumps({"coverage": "evidence", "selections": {"S1-P0-U0": fields}})
    assert render(raw, evidence)["status"] == "rejected"


def test_duplicate_unit_or_field_keys_and_unknowns_are_rejected_without_normalization() -> None:
    for raw in (
        '{"coverage":"evidence","selections":{"S1-P0-U0":{"0":true,"1":true},"S1-P0-U0":{"0":true,"1":true}}}',
        '{"coverage":"evidence","selections":{"S1-P0-U0":{"0":true,"0":true,"1":true}}}',
        '{"coverage":"evidence","selections":{"S99":{"0":true,"1":true}}}',
    ):
        assert render(raw, available())["status"] == "rejected"


def test_sentence_fields_are_empty_and_coverage_cannot_contradict_selection() -> None:
    evidence = catalog([{"n": 1, "passages": [{"text": "Fern costs 7 dollars."}]}])
    grammar = schema(evidence)["properties"]["selections"]["properties"]["S1-P0-U0"]
    assert grammar["properties"] == {} and grammar["additionalProperties"] is False
    valid = json.dumps({"coverage": "evidence", "selections": {"S1-P0-U0": {}}})
    assert render(valid, evidence)["status"] == "evidence"
    invalid = valid.replace('"evidence"', '"unsupported"')
    assert render(invalid, evidence)["status"] == "rejected"
