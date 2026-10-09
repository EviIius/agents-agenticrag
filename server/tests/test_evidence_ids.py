"""IDs cannot forge source text or move a unit to a different source."""

import json

import pytest

from evals.reliability.extractive.ids_contract import units, validate

SOURCES = [
    {"n": 1, "passages": [{"text": "Offset is -24.5 mm. It is not waterproof."}]},
    {"n": 2, "passages": [{"text": "| Model | Cost |\n| --- | --- |\n| Birch | |\n| Pine | 0 |"}]},
]


def test_host_owns_the_exact_text_negation_values_and_table_header() -> None:
    available = units(SOURCES)
    first = available["source_1"][0]
    row = next(u for u in available["source_2"] if "| Birch |" in u["text"])
    raw = json.dumps({"source_1": first["id"], "source_2": row["id"]})
    accepted = validate(raw, available)
    assert accepted[0]["text"] == "Offset is -24.5 mm. It is not waterproof."
    assert accepted[1]["text"] == "| Birch | |"
    assert accepted[1]["table_header"] == "| Model | Cost |"
    assert validate('{"source_1": null, "source_2": null}', available) == []


@pytest.mark.parametrize(
    "raw",
    [
        '{"source_1": "S2-P0-U0", "source_2": null}',
        '{"source_1": "S1-P0-U999", "source_2": null}',
        '{"source_1": null, "source_2": null, "answer": "Waterproof"}',
        '{"source_1": {"text": "Waterproof"}, "source_2": null}',
        '{"source_1": null}',
        "[]",
    ],
)
def test_forged_reference_or_answer_rejects_everything(raw: str) -> None:
    with pytest.raises(ValueError):
        validate(raw, units(SOURCES))


def test_an_id_does_not_prove_the_unit_answers_the_question() -> None:
    available = units(SOURCES)
    wrong_for_offset = available["source_2"][0]["id"]
    assert validate(json.dumps({"source_1": None, "source_2": wrong_for_offset}), available)
