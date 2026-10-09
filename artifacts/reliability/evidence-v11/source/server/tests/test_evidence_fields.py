"""Novel field/context and reference attacks against the isolated v11 contract."""

import json
from typing import Any

import pytest

from app.providers.base import ChatRequest, ProviderMessage
from evals.reliability.evidence_contract_v11 import DECLINE, build, catalog, render


def source(text: str, kind: str = "page", **metadata: Any) -> dict[str, Any]:
    return {
        "n": 1,
        "kind": kind,
        "title": "Invented Fern record",
        "published_at": "2025-03-04",
        "fetched_at": "2026-10-09",
        "passages": [{"heading": "Fern 2031", "text": text}],
        **metadata,
    }


def selection(identifier: str, *columns: int, coverage: str = "evidence") -> str:
    return json.dumps(
        {"coverage": coverage, "selections": [{"id": identifier, "columns": list(columns)}]}
    )


def test_row_projection_keeps_original_property_and_blank_without_relabeling() -> None:
    available = catalog(
        [source("| Item | Height | Occupied |\n| --- | --- | --- |\n| Fern | 720 | |")]
    )
    row = available.units["source_1"][0]
    outcome = render(selection(row["id"], 0, 2), available)
    assert outcome["status"] == "evidence"
    assert (
        "| Item | Occupied | Citation |\n| --- | --- | --- |\n| Fern |  | [1] |"
        in outcome["content"]
    )
    assert "720" not in outcome["content"] and "Height" not in outcome["content"]
    assert outcome["units"][0]["original_cells"] == ["Fern", "720", ""]
    assert available.units["source_1"][0]["cells"] == ["Fern", "720", ""]
    assert not outcome["verified_answer"]


@pytest.mark.parametrize("columns", [[1], [1, 2], [0, 3], [0, -1], [0, 1, 1], [0, True]])
def test_omitted_identity_forged_duplicate_or_boolean_columns_decline(columns: list[int]) -> None:
    available = catalog(
        [source("| Item | Value | Unit |\n| --- | --- | --- |\n| Fern | -5.5 | mm |")]
    )
    result = render(selection(available.units["source_1"][0]["id"], *columns), available)
    assert result["status"] == "rejected" and result["content"] == DECLINE


def test_cannot_remove_explicit_time_or_qualification_to_fit_a_narrow_answer() -> None:
    available = catalog(
        [
            source(
                "| Item | Days | Valid until | Condition |\n| --- | --- | --- | --- |\n"
                "| Fern | 7 | 2031 | Dry use only |"
            )
        ]
    )
    row = available.units["source_1"][0]
    assert render(selection(row["id"], 0, 1), available)["status"] == "rejected"
    assert render(selection(row["id"], 0, 1, 2, 3), available)["status"] == "evidence"


def test_user_owned_file_is_not_rejected_by_public_prose_limit() -> None:
    text = " ".join(["Invented"] * 26) + "."
    web = catalog([source(text)])
    library = catalog([source(text, kind="document")])
    assert render(selection(web.units["source_1"][0]["id"]), web)["status"] == "rejected"
    assert render(selection(library.units["source_1"][0]["id"]), library)["status"] == "evidence"


def test_compact_data_can_cover_many_rows_but_descriptive_prose_stays_capped() -> None:
    text = "| Item | Value |\n| --- | --- |\n" + "\n".join(f"| Fern-{i} | {i} |" for i in range(20))
    available = catalog([source(text)])
    raw = json.dumps(
        {
            "coverage": "evidence",
            "selections": [{"id": u["id"], "columns": [0, 1]} for u in available.units["source_1"]],
        }
    )
    outcome = render(raw, available)
    assert outcome["status"] == "evidence" and outcome["content"].count("| [1] |") == 20
    descriptive = catalog(
        [
            source(
                "| Item | Description |\n| --- | --- |\n| Fern | "
                + " ".join(["Invented"] * 26)
                + " |"
            )
        ]
    )
    assert (
        render(selection(descriptive.units["source_1"][0]["id"], 0, 1), descriptive)["status"]
        == "rejected"
    )


def test_strict_ids_sentence_columns_and_extra_model_prose_cannot_enter_answer() -> None:
    available = catalog([source("Fern costs 7 dollars.")])
    for raw in (
        selection("S99-P0-U0"),
        selection("S1-P0-U0", 0),
        '{"coverage":"unsupported","selections":[],"answer":"Fern is safe"}',
        '{"coverage":"unsupported","coverage":"evidence","selections":[]}',
    ):
        assert render(raw, available)["status"] == "rejected"


def test_compact_payload_keeps_dates_and_auditable_source_without_repeated_paragraphs() -> None:
    request = ChatRequest(
        "fake",
        [ProviderMessage("system", "Original"), ProviderMessage("user", "What is Fern's offset?")],
    )
    original = source("Fern is not waterproof. It has offset -5.5 mm.")
    build(request, [original])
    payload = json.loads(request.messages[-1].content)
    assert payload["source_metadata"]["source_1"]["published_at"] == "2025-03-04"
    assert payload["source_metadata"]["source_1"]["fetched_at"] == "2026-10-09"
    assert all("paragraph" not in u for u in payload["units"])
    assert payload["units"][1]["required_context"] == "Fern 2031\nFern is not waterproof."
    original["passages"][0]["text"] = "Mutated"
    assert getattr(request, "_evidence_catalog").sources["source_1"]["passages"][0]["text"] != "Mutated"
    assert request.params == {}


def test_public_author_does_not_establish_personal_speaker_identity() -> None:
    available = catalog([source("I drank tea.")], "What did I drink yesterday?")
    assert (
        render(selection(available.units["source_1"][0]["id"]), available)["status"]
        == "unsupported_subject"
    )
