"""Stricter prospective grammar and row-identity regression; no native inference."""

import json

from evals.reliability.evidence_contract_v11 import catalog
from evals.reliability.evidence_schema_v12 import render, required_columns, schema


def test_sentence_schema_cannot_request_columns_and_ambiguous_fragments_are_excluded() -> None:
    available = catalog(
        [
            {
                "n": 1,
                "passages": [
                    {"text": "Fern is dry.\n\n| Year | 2031 |\n| --- | --- |\n| Winner | Fern |"}
                ],
            }
        ]
    )
    branches = schema(available)["properties"]["selections"]["items"]["anyOf"]
    assert len(branches) == 1
    assert branches[0]["properties"]["columns"]["maxItems"] == 0
    assert branches[0]["properties"]["id"]["enum"] == ["S1-P0-U0"]


def test_ordinal_column_cannot_substitute_for_named_subject() -> None:
    available = catalog(
        [
            {
                "n": 1,
                "passages": [
                    {"text": "| | Item | Value |\n| --- | --- | --- |\n| 1. | Fern | 7 |"}
                ],
            }
        ]
    )
    unit = available.units["source_1"][0]
    assert required_columns(unit) == [0, 1]
    missing = json.dumps(
        {"coverage": "evidence", "selections": [{"id": unit["id"], "columns": [0, 2]}]}
    )
    assert render(missing, available)["status"] == "rejected"
    complete = json.dumps(
        {"coverage": "evidence", "selections": [{"id": unit["id"], "columns": [0, 1, 2]}]}
    )
    assert "Fern" in render(complete, available)["content"]
    columns = schema(available)["properties"]["selections"]["items"]["anyOf"][0]["properties"][
        "columns"
    ]
    assert columns["prefixItems"] == [{"const": 0}, {"const": 1}]
    assert columns["items"]["enum"] == [2]
