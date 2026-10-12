"""Negative evidence-role/coverage tests and exact retained offline replays."""

import copy
import json
import math
import socket

import audit
import pytest


@pytest.fixture(scope="module")
def retained():
    _path, document = audit.report()
    return document, audit.retained_turns(document)


@pytest.mark.parametrize("case", ["haiku", "fiction"])
async def test_actual_creative_query_contradiction_reproduces_host_fallback(
    retained, case
):
    _document, turns = retained
    saved = turns[(case, 0)]
    assert saved["native"]["task"] == "creative" and saved["native"]["queries"]
    with audit.no_network():
        result = await audit.replay_plan(
            audit.load_contract(), saved["turn"]["question"], saved["native"]
        )
    assert result["plan"]["search"] and result["fallback"]
    assert result["host"] == saved["host"]


@pytest.mark.parametrize("case", ["haiku", "fiction"])
async def test_empty_queries_counterfactual_is_host_admissible_not_native_proof(
    retained, case
):
    _document, turns = retained
    saved = turns[(case, 0)]
    native = copy.deepcopy(saved["native"])
    native["queries"] = []
    with audit.no_network():
        result = await audit.replay_plan(
            audit.load_contract(), saved["turn"]["question"], native
        )
    assert not result["plan"]["search"] and not result["fallback"]
    assert result["host"]["mode"] == "native_local"
    assert saved["native"]["queries"]  # Original retained plan not altered.


async def test_force_search_is_not_removed_by_creative_label(retained):
    _document, turns = retained
    native = copy.deepcopy(turns[("haiku", 0)]["native"])
    native["queries"] = []
    with audit.no_network():
        result = await audit.replay_plan(
            audit.load_contract(), "Write a new poem.", native, force=True
        )
    assert result["plan"]["search"] and result["fallback"]


@pytest.mark.parametrize(
    "question",
    [
        "Write a new poem and verify the current depot opening date.",
        "Write a new story based on the document named 'Depot Report'.",
        "Write a new function using the latest API documentation.",
    ],
)
async def test_creative_labels_do_not_exempt_detected_external_or_missing_sources(
    question, retained
):
    _document, turns = retained
    native = copy.deepcopy(turns[("haiku", 0)]["native"])
    native["queries"] = []
    with audit.no_network():
        result = await audit.replay_plan(audit.load_contract(), question, native)
    assert result["plan"]["search"]


async def test_unknown_factual_creative_label_exposes_remaining_guard_limit(retained):
    # Diagnosis of a genuine unqualified path; never claim every local label is safe.
    _document, turns = retained
    native = copy.deepcopy(turns[("haiku", 0)]["native"])
    native["queries"] = []
    with audit.no_network():
        result = await audit.replay_plan(
            audit.load_contract(), "Who founded an unknown organization?", native
        )
    assert not result["plan"]["search"]  # Existing policy trusts this task label.


TABLE = """| Year | Champion | Runner-Up |
| --- | --- | --- |
| 2024 | Celadon | Brindle |
| 2023 | Dune | Ash |
"""


def test_valid_citation_and_present_names_do_not_establish_reversed_roles():
    tables = audit.markdown_tables(TABLE)
    assert audit.exact_cell(tables, "Year", "2024", "Runner-Up", "Brindle")
    assert not audit.exact_cell(tables, "Year", "2024", "Runner-Up", "Celadon")
    assert "Celadon" in TABLE  # Token overlap alone would miss this reversal.


def test_wrong_year_and_wrong_column_fail_exact_relation():
    tables = audit.markdown_tables(TABLE)
    assert not audit.exact_cell(tables, "Year", "2023", "Runner-Up", "Brindle")
    assert not audit.exact_cell(tables, "Year", "2024", "Champion", "Brindle")


def test_flattened_cells_without_headers_are_not_a_bound_table():
    assert not audit.markdown_tables(
        "Year\nChampion\nRunner-Up\n2024\nCeladon\nBrindle"
    )


def test_captions_are_not_data_rows():
    assert not audit.markdown_tables(
        "Full results are listed below. Celadon reached the final."
    )


def test_missing_property_is_unknown_even_when_subject_and_citation_exist():
    tables = audit.markdown_tables(
        "| Place | Capital |\n| --- | --- |\n| Coast | Harbor |"
    )
    assert audit.exact_cell(tables, "Place", "Coast", "Capital", "Harbor")
    assert not audit.exact_cell(tables, "Place", "Coast", "Currency", "Credits")


def test_stage_granularity_is_not_inferred_from_related_entity():
    tables = audit.markdown_tables(
        "| Stage | Team |\n| --- | --- |\n| Semifinal | Celadon |"
    )
    assert audit.exact_cell(tables, "Stage", "Semifinal", "Team", "Celadon")
    assert not audit.exact_cell(tables, "Stage", "Final", "Team", "Celadon")


def test_duplicate_columns_do_not_bind_ambiguous_role():
    tables = audit.markdown_tables(
        "| Key | Role | Role |\n| --- | --- | --- |\n| a | b | c |"
    )
    assert not audit.exact_cell(tables, "Key", "a", "Role", "b")


def test_dash_is_retained_as_literal_not_coerced_to_zero():
    tables = audit.markdown_tables("| Team | Losses |\n| --- | --- |\n| Ash | - |")
    assert audit.exact_cell(tables, "Team", "Ash", "Losses", "-")
    assert not audit.exact_cell(tables, "Team", "Ash", "Losses", "0")


def test_escaped_pipe_and_empty_cells_retain_column_alignment():
    tables = audit.markdown_tables(
        "| Key | Label | Empty |\n| --- | --- | --- |\n| a | x\\|y | |"
    )
    assert audit.exact_cell(tables, "Key", "a", "Label", "x|y")
    assert audit.exact_cell(tables, "Key", "a", "Empty", "")


def test_malformed_row_does_not_shift_roles():
    assert not audit.markdown_tables(
        "| Year | Champion | Runner-Up |\n| 2024 | Celadon |"
    )


@pytest.mark.parametrize("case", ["nba-all-losses", "capital-compare", "table-page"])
def test_actual_extraction_chunks_and_adaptive_budget_selection_reproduce(
    retained, case
):
    document, turns = retained
    with audit.no_network():
        record, _pages = audit.case_trace(case, turns[(case, 0)], document)
    assert record["ranking_selection_reproduced"]
    assert record["all_actual_selected_passages_reproduced"]
    assert record["question_only_same_selected_ordinals"]
    assert record["calibrated_context_ratio"] != 0.3


def test_actual_full_matching_table_is_fetched_but_not_selected(retained):
    document, turns = retained
    with audit.no_network():
        record, _pages = audit.case_trace(
            "nba-all-losses", turns[("nba-all-losses", 0)], document
        )
    page = next(p for p in record["pages"] if "finals_lost.htm" in p["url"])
    table = next(c for c in page["chunks"] if c["markdown_tables"])
    assert table["ord"] == 3 and not table["selected"]
    assert page["selected_ordinals"] == [0, 1, 2]
    rows = table["markdown_tables"][0]["rows"]
    header = table["markdown_tables"][0]["header"]
    loss = header.index("Finals Lost")
    assert len(rows) == 28
    assert sum(r[loss].isdigit() and int(r[loss]) > 0 for r in rows) == 23


def test_currency_absent_from_supplied_pages_but_name_in_unfetched_menu(retained):
    document, turns = retained
    with audit.no_network():
        record, _pages = audit.case_trace(
            "capital-compare", turns[("capital-compare", 0)], document
        )
    readable = [
        p
        for p in record["archived_pages"]
        if "error" not in p and "extraction_error" not in p
    ]
    assert readable
    assert not any(
        p["australian_currency_name_or_code_literal_present"] for p in record["pages"]
    )
    literal_hits = [
        p for p in readable if p["australian_currency_name_or_code_literal_present"]
    ]
    assert (
        len(literal_hits) == 1
        and "themoneyconverter.com/JPY/USD" in literal_hits[0]["url"]
    )
    assert (
        "- AUD - Australian Dollar"
        in literal_hits[0]["australian_currency_literal_context"][0]
    )
    # Menu/name availability is not an explicit country/property assertion in
    # the actual supplied evidence. Do not equate string presence to entailment.
    assert record["native_queries"] == [
        "capital and currency of Japan",
        "capital and currency of Australia",
    ]
    assert record["recorded_provider_queries"] == [
        "capital of Japan",
        "currency of Japan",
        "capital of Australia",
    ]


def test_recent_results_corpus_is_fixed_to_three_years_not_fresh_queries(retained):
    document, turns = retained
    with audit.no_network():
        record, _pages = audit.case_trace(
            "table-page", turns[("table-page", 0)], document
        )
    assert record["recorded_provider_queries"] == [
        "NBA Finals 2022 results and scores",
        "NBA Finals 2023 results and scores",
        "NBA Finals 2024 results and scores",
    ]
    assert "2026" in record["native_queries"][0]
    assert "2026" not in " ".join(record["recorded_provider_queries"])


def test_later_game_data_exists_but_three_slot_selection_keeps_early_games(retained):
    document, turns = retained
    with audit.no_network():
        record, _pages = audit.case_trace(
            "table-page", turns[("table-page", 0)], document
        )
    page = next(p for p in record["pages"] if "2024-nba-finals-mavericks" in p["url"])
    assert page["selected_ordinals"] == [1, 3, 5]
    for ordinal, prefix in [(7, "Game 4, Jun 14"), (9, "Game 5, Jun 17")]:
        chunk = next(c for c in page["chunks"] if c["ord"] == ordinal)
        assert not chunk["selected"]
        assert chunk["markdown_tables"][0]["header"][0] == prefix


def test_unchanged_budget_can_admit_full_table_by_replacing_one_caption(retained):
    document, turns = retained
    with audit.no_network():
        record, _pages = audit.case_trace(
            "nba-all-losses", turns[("nba-all-losses", 0)], document
        )
    page = next(p for p in record["pages"] if "finals_lost.htm" in p["url"])
    selected = [c for p in record["pages"] for c in p["chunks"] if c["selected"]]
    cost = lambda c: (
        math.ceil(c["characters"] * record["calibrated_context_ratio"]) + 20
    )
    before = sum(cost(c) for c in selected)
    table, caption = page["chunks"][3], page["chunks"][2]
    after = before - cost(caption) + cost(table)
    assert (before, after, record["source_token_budget"]) == (4978, 5333, 5502)
    assert len(table["markdown_tables"][0]["rows"]) == 28
    # This is admission feasibility from original bytes, not a new answer or
    # proof that a model will interpret the admitted evidence correctly.


def test_network_is_rejected_before_any_connection():
    with (
        audit.no_network(),
        socket.socket() as sock,
        pytest.raises(AssertionError, match="forbids network"),
    ):
        sock.connect(("127.0.0.1", 11434))


def test_original_numeric_and_failure_scores_remain_retained(retained):
    document, _turns = retained
    assert sum(row["passed"] for row in document["results"]) == 22
    assert len(document["results"]) == 25
    original = json.loads((audit.PRIOR / "full-failure-analysis.json").read_text())
    assert original["automatic_failed_cases"] == ["haiku", "nba-all-losses", "fiction"]
