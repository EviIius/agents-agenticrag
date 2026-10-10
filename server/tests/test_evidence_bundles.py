"""Synthetic admission parity and original source preservation; no inference."""

import json
from itertools import combinations
from typing import Any

import pytest

from app.providers.base import ChatRequest, ProviderMessage
from evals.reliability import evidence_contract_v13 as host
from evals.reliability.evidence_bundles_v15 import build, bundles, render, schema


def evidence(text: str, **source: Any) -> Any:
    return host.catalog([{"n": 1, "passages": [{"text": text}], **source}])


def selection(identifier: str, bundle: Any, coverage: str = "evidence") -> str:
    return json.dumps({"coverage": coverage, "selections": {identifier: bundle}})


def test_identity_only_fields_are_not_offered_and_complete_fields_render() -> None:
    available = evidence("| Item | Value | Units |\n| --- | --- | --- |\n| Fern | 7 | grams |")
    options = bundles(available)["S1-P0-U0"]
    assert set(options) == {"fields_0_1", "fields_0_2", "fields_0_1_2"}
    assert render(selection("S1-P0-U0", "fields_0"), available)["status"] == "rejected"
    result = render(selection("S1-P0-U0", "fields_0_1_2"), available)
    assert result["status"] == "evidence" and "Fern | 7 | grams" in result["content"]
    assert not result["verified_answer"]


def test_ordinal_subject_date_and_qualification_are_preserved_in_every_bundle() -> None:
    available = evidence(
        "| | Item | Date | Value | Condition |\n| --- | --- | --- | --- | --- |\n"
        "| 1 | Fern | 2026 | -7.25 | only indoors |"
    )
    options = bundles(available)["S1-P0-U0"]
    assert set(options) == {"fields_0_1_2_3_4"}
    selected = render(selection("S1-P0-U0", next(iter(options))), available)
    assert "1 | Fern | 2026 | -7.25 | only indoors" in selected["content"]
    assert selected["units"][0]["original_cells"] == ["1", "Fern", "2026", "-7.25", "only indoors"]


def test_each_offered_bundle_passes_the_final_host_validator_without_added_fields() -> None:
    available = evidence(
        "Context.\n\n| Item | Value | Loss | Date |\n| --- | --- | --- | --- |\n"
        "| Fern | 7 | | 2026 |\n| Moss | 2 | -3 | 2026 |"
    )
    options = bundles(available)
    grammar = schema(available)["properties"]["selections"]["properties"]
    assert set(options) == set(grammar)
    for identifier, choices in options.items():
        assert grammar[identifier] == {"type": "string", "enum": list(choices)}
        for name, choice in choices.items():
            _, chosen = host.validate(
                json.dumps(
                    {
                        "coverage": "evidence",
                        "selections": [{"id": identifier, "columns": choice["columns"]}],
                    }
                ),
                available,
            )
            outcome = render(selection(identifier, name), available)
            assert outcome["status"] == "evidence"
            assert outcome["units"] == chosen
            assert set(choice["standalone_word_cost"]) == {"prose", "data", "file"}
    # Exhaust all subsets for this small row: every structurally rejected subset
    # is absent, including blank ordinal/identity-only and omitted date variants.
    unit = available.units["source_1"][1]
    for count in range(5):
        for columns in combinations(range(4), count):
            raw = json.dumps(
                {"coverage": "evidence", "selections": [{"id": unit["id"], "columns": columns}]}
            )
            try:
                host.validate(raw, available)
            except ValueError:
                assert all(c["columns"] != list(columns) for c in options[unit["id"]].values())


def test_over_budget_prose_is_unselectable_without_trimming_the_saved_source() -> None:
    long = " ".join(["Fern"] + ["growth"] * 25) + "."
    available = evidence(long)
    assert bundles(available) == {}
    assert schema(available)["properties"]["selections"]["properties"] == {}
    assert available.sources["source_1"]["passages"][0]["text"] == long
    assert available.units["source_1"][0]["text"] == long
    assert render(selection("S1-P0-U0", "text"), available)["status"] == "rejected"


def test_heading_and_referent_are_included_in_admission_cost() -> None:
    available = host.catalog(
        [
            {
                "n": 1,
                "passages": [
                    {"heading": " ".join(["context"] * 24), "text": "Fern costs 7 dollars."}
                ],
            }
        ]
    )
    assert bundles(available) == {}
    available = evidence("Fern costs 7 dollars. It grows only indoors.")
    options = bundles(available)
    assert options["S1-P0-U1"]["text"]["standalone_word_cost"]["prose"] == 8
    selected = render(selection("S1-P0-U1", "text"), available)
    assert "Fern costs 7 dollars. / It grows only indoors." in selected["content"]


def test_aggregate_costs_still_reject_individually_legal_selections() -> None:
    available = evidence("Fern " + "grows " * 12 + "indoors.\n\nMoss " + "grows " * 12 + "outside.")
    assert len(bundles(available)) == 2
    raw = json.dumps(
        {
            "coverage": "evidence",
            "selections": {u["id"]: "text" for u in available.units["source_1"]},
        }
    )
    outcome = render(raw, available)
    assert outcome["status"] == "rejected" and "budget" in outcome["reason"]


def test_shared_context_is_charged_once_and_library_allowance_is_distinct() -> None:
    available = host.catalog(
        [
            {
                "n": 1,
                "passages": [
                    {"heading": " ".join(["scope"] * 19), "text": "Fern grows. Moss grows."}
                ],
            }
        ]
    )
    raw = json.dumps(
        {
            "coverage": "evidence",
            "selections": {u["id"]: "text" for u in available.units["source_1"]},
        }
    )
    assert render(raw, available)["status"] == "evidence"
    long = " ".join(["Fern"] + ["growth"] * 25) + "."
    library = evidence(long, kind="document")
    assert bundles(library)["S1-P0-U0"]["text"]["standalone_word_cost"] == {
        "prose": 0,
        "data": 0,
        "file": 26,
    }
    assert render(selection("S1-P0-U0", "text"), library)["status"] == "evidence"


@pytest.mark.parametrize("bundle", ["fields_0", "fields_1_2", "fields_01_2", True, {}, None])
def test_unknown_missing_or_forged_fields_are_never_recovered(bundle: Any) -> None:
    available = evidence("| Item | Value |\n| --- | --- |\n| Fern | 7 |")
    assert render(selection("S1-P0-U0", bundle), available)["status"] == "rejected"


def test_duplicate_keys_unowned_units_coverage_and_backticks_fail_closed() -> None:
    available = evidence("Fern costs 7 dollars.")
    for raw in (
        '{"coverage":"evidence","selections":{"S1-P0-U0":"text","S1-P0-U0":"text"}}',
        selection("S99-P0-U0", "text"),
        selection("S1-P0-U0", "text", "unsupported"),
        selection("S1-P0-U0", "text", "invented"),
    ):
        assert render(raw, available)["status"] == "rejected"
    assert bundles(evidence("Fern costs `7` dollars.")) == {}
    assert bundles(evidence("It costs 7 dollars.")) == {}


def test_build_supplies_only_admitted_options_but_preserves_original_catalogue() -> None:
    request = ChatRequest(
        "fake", [ProviderMessage("system", "Original"), ProviderMessage("user", "Fern?")]
    )
    long = " ".join(["Moss"] + ["grows"] * 25) + "."
    original = [{"n": 1, "passages": [{"text": "Fern costs 7 dollars.\n\n" + long}]}]
    build(request, original)
    payload = json.loads(request.messages[-1].content)
    assert len(payload["units"]) == 1
    assert payload["units"][0]["bundles"]["text"]["standalone_word_cost"]["prose"] == 4
    assert request._evidence_catalog.sources["source_1"] == original[0]  # type: ignore[attr-defined]
    assert request.params == {}
    grammar = request.json_schema
    assert grammar is not None
    assert set(grammar["properties"]["selections"]["properties"]) == {"S1-P0-U0"}
