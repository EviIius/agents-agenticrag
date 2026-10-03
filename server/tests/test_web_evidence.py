import json

import pytest

from app.search.chunk import chunk
from app.search.selection import bind_references, literal_condition_rows
from evals.web.table_trials import numeric_rows, row_records


def test_table_records_preserve_every_cell_and_caption_under_budget() -> None:
    rows = [f"| {i} | Café {i}\\|sale | - |" for i in range(70)]
    text = "# Inventory\n\nObserved units.\n\n|  | Product | Units |\n" + "\n".join(rows)
    passages = row_records("https://example.org", text)
    records = [
        json.loads(line)
        for passage in passages
        for line in passage.text.splitlines()
        if line.startswith("{")
    ]
    assert records == [{"": str(i), "Product": f"Café {i}\\|sale", "Units": "-"} for i in range(70)]
    assert sum("Observed units." in p.text for p in passages) == 1
    assert all(len(p.text) <= 3000 and p.heading == "Inventory" for p in passages)
    assert [p.ord for p in passages] == list(range(len(passages)))


def test_ambiguous_table_headers_and_malformed_rows_remain_original() -> None:
    for text in (
        "| Units | Units |\n| 1 | 2 |",
        "| Product | Units |\n| A | 1 | extra |",
        "Ordinary prose without a table.",
    ):
        assert row_records("https://example.org", text) == chunk("https://example.org", text)


def test_numeric_selection_assembles_fragments_and_never_treats_unknown_as_zero() -> None:
    header = "| Product | Units |"
    text = header + "\n| A | 2 |\n| B | 0 |\n\n" + header + "\n| C | - |\n| D | 5 |"
    selected = numeric_rows(
        "https://example.org", text, {"column": "Units", "operator": "gt", "value": "0"}
    )
    body = "\n".join(p.text for p in selected)
    assert "| A | 2 |" in body and "| D | 5 |" in body
    assert "| B | 0 |" not in body and "| C | - |" not in body
    assert "2 of 4 rows match" in body and "1 rows have no supported numeric value" in body
    zero = numeric_rows(
        "https://example.org", text, {"column": "Units", "operator": "eq", "value": "0"}
    )
    assert "| B | 0 |" in "\n".join(p.text for p in zero)
    assert "| C | - |" not in "\n".join(p.text for p in zero)


def test_literal_condition_binds_inflections_and_keeps_source_values() -> None:
    question = "List all products that sold, including products discontinued later."
    text = "| Product | Units Sold |\n| A | 2 |\n| B | 0 |\n| C | - |\n| D | 5 |"
    selected = literal_condition_rows(
        "https://example.org",
        text,
        {
            "request_span": "products that sold",
            "property_word": "sales",
            "operator": "occurred",
            "value": None,
        },
        question,
    )
    # An undeclared measure cannot be invented: Units is absent from the request.
    assert selected == chunk("https://example.org", text)
    question = "List products with units sold."
    selected = literal_condition_rows(
        "https://example.org",
        text,
        {
            "request_span": "units sold",
            "property_word": "sales",
            "operator": "occurred",
            "value": None,
        },
        question,
    )
    body = "\n".join(p.text for p in selected)
    assert "| A | Units Sold: 2 |" in body and "| D | Units Sold: 5 |" in body
    assert "| B | 0 |" not in body and "| C | - |" not in body
    assert "2 supported rows match" in body
    assert all(p.selection_applied for p in selected)
    assert all("[pending]" in p.text for p in selected)
    bound = bind_references(selected[0], 3)
    assert "| A | Units Sold: 2 | [3] |" in bound.text
    assert "[pending]" not in bound.text


@pytest.mark.parametrize(
    "contract,question,text",
    [
        (
            {
                "request_span": "products sold",
                "property_word": "sales",
                "operator": "occurred",
                "value": None,
            },
            "List products returned",
            "| Product | Sales |\n| A | 2 |\n| B | 0 |",
        ),
        (
            {
                "request_span": "products sold",
                "property_word": "returns",
                "operator": "occurred",
                "value": None,
            },
            "List products sold",
            "| Product | Returns |\n| A | 2 |\n| B | 0 |",
        ),
        (
            {
                "request_span": "products sold",
                "property_word": "sales",
                "operator": "occurred",
                "value": None,
            },
            "List products sold",
            "| Product | Sales | Sales |\n| A | 2 | 1 |\n| B | 0 | 0 |",
        ),
        (
            {
                "request_span": "products sold",
                "property_word": "sales",
                "operator": "occurred",
                "value": None,
            },
            "List products sold",
            "| Product | Sales USD |\n| A | 2 |\n| B | 0 |",
        ),
        (
            {
                "request_span": "products sold",
                "property_word": "sales",
                "operator": "occurred",
                "value": None,
            },
            "List products sold",
            "| Product | Sales |\n| A | -2 |\n| B | 0 |",
        ),
        (
            {
                "request_span": "products with sales over 5",
                "property_word": "sales",
                "operator": "lt",
                "value": 5,
            },
            "List products with sales over 5",
            "| Product | Sales |\n| A | 2 |\n| B | 6 |",
        ),
        (
            {
                "request_span": "products that never sold",
                "property_word": "sales",
                "operator": "occurred",
                "value": None,
            },
            "List products that never sold",
            "| Product | Sales |\n| A | 2 |\n| B | 0 |",
        ),
        (
            {
                "request_span": "products sold over 5 million",
                "property_word": "sales",
                "operator": "gt",
                "value": 5,
            },
            "List products sold over 5 million",
            "| Product | Sales |\n| A | 2 |\n| B | 6 |",
        ),
    ],
)
def test_unbound_ambiguous_or_unsupported_conditions_do_not_filter(
    contract: dict[str, object], question: str, text: str
) -> None:
    assert literal_condition_rows("https://example.org", text, contract, question) == chunk(
        "https://example.org", text
    )


def test_explicit_threshold_preserves_all_matching_rows_and_never_invents_unknown_values() -> None:
    text = (
        "| Product | Sales |\n"
        + "\n".join(f"| Café {i} | {i} |" for i in range(180))
        + "\n| Missing | - |"
    )
    question = "List products with sales at least 5."
    selected = literal_condition_rows(
        "https://example.org",
        text,
        {
            "request_span": "sales at least 5",
            "property_word": "sales",
            "operator": "gte",
            "value": 5,
        },
        question,
    )
    body = "\n".join(p.text for p in selected)
    assert all(f"| Café {i} | Sales: {i} |" in body for i in range(5, 180))
    assert all(f"| Café {i} | {i} |" not in body for i in range(5))
    assert "| Missing | - |" not in body
    assert all(len(p.text) <= 3000 for p in selected)
    assert [p.ord for p in selected] == list(range(len(selected)))


def test_defined_abbreviations_and_long_notes_keep_all_selected_rows() -> None:
    question = "List entries with losses."
    header = "| Entry | W | L | Notes |"
    rows = [f"| Entry {i} | 2 | {i} | " + "Context word " * 40 + " |" for i in range(24)]
    text = (
        "## Series\n\nThe statistics below refer to series wins and losses.\n\n"
        + header
        + "\n"
        + "\n".join(rows)
    )
    text += "\n\n## Individual records\n\n" + header + "\n| Separate | 2 | 1 | Another measure |"
    condition: dict[str, object] = {
        "request_span": question,
        "property_word": "losses",
        "operator": "occurred",
        "value": None,
    }
    selected = literal_condition_rows("https://example.org", text, condition, question)
    verified = [p for p in selected if p.selection_applied]
    body = "\n".join(p.text for p in verified)
    assert "23 supported rows" in body
    assert all(f"| Entry {i} | 2 | L (losses): {i} |" in body for i in range(1, 24))
    assert "| Entry 0 |" not in body and "| Separate |" not in body
    assert "Host projection omits long prose columns: Notes" in body
    assert len(verified) <= 3 and all(len(p.text) <= 3000 for p in selected)
    # A bare W/L table without its definition is not interpreted by guessing.
    bare = header + "\n| Unknown | 2 | 1 | Details |"
    assert literal_condition_rows("https://example.org", bare, condition, question) == chunk(
        "https://example.org", bare
    )
