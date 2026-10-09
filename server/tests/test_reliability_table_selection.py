"""Intact requested data gets priority; unrelated prose/tables do not."""

import pytest

from app.schemas import Passage
from app.search.rank import select
from evals.reliability.table_selection import prioritize_tables


def test_large_requested_table_survives_the_budget_ahead_of_introductory_prose() -> None:
    captions = [
        Passage(source_url="https://example.org", ord=i, text="Inventory item state overview.")
        for i in range(3)
    ]
    table = Passage(
        source_url="https://example.org",
        ord=3,
        text="| Item | State |\n| --- | --- |\n"
        + "\n".join(f"| Invented item {i} | queued |" for i in range(40)),
    )
    assert len(table.text) > 900
    ranked = [(p, 0.1) for p in captions] + [(table, 0.09)]
    original = select(ranked, 1500, 6)
    assert table not in original[0]
    repaired = prioritize_tables(ranked, "List every inventory item and state.")
    selected = select(repaired, 1500, 6)
    assert table in selected[0]
    assert selected[0][-1].text == table.text
    assert sorted((id(p), score) for p, score in repaired) == sorted(
        (id(p), score) for p, score in ranked
    )


@pytest.mark.parametrize(
    ("question", "text", "score"),
    [
        ("Explain item and state.", "| Item | State |\n| --- | --- |\n| A | queued |", 0.1),
        ("List items and states.", "Item state prose with a pipe | in it.", 0.1),
        ("List items and states.", "| Item | State |\n| --- | --- |\n| A | queued |", 0.0),
        ("List items and states.", "| Region | Cost |\n| --- | --- |\n| A | 9 |", 0.1),
        ("List items and states.", "| Item | Cost |\n| --- | --- |\n| A | 9 |", 0.1),
        ("List items and states.", "| Item | State |\nnot a delimiter\n| A | queued |", 0.1),
    ],
)
def test_only_relevant_positive_scored_structured_tables_are_prioritized(
    question: str, text: str, score: float
) -> None:
    first = Passage(source_url="https://example.org/a", ord=0, text="Ordinary paragraph")
    table = Passage(source_url="https://example.org/b", ord=0, text=text)
    ranked = [(first, 0.2), (table, score)]
    assert prioritize_tables(ranked, question) == ranked
