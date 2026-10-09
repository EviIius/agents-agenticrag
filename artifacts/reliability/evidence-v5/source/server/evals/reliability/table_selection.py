"""Offline table-priority experiment; production ranking remains unchanged."""

import re

from app.schemas import Passage
from app.search.rank import tokenize


def prioritize_tables(
    ranked: list[tuple[Passage, float]], question: str
) -> list[tuple[Passage, float]]:
    """Prefer intact tables whose headers cover literal requested fields.

    Caller supplies the actual user task, excluding untrusted quoted material.
    No values, scores, rows, sources or predicates are created. This is a
    coverage experiment, not semantic filtering or answer verification.
    """
    terms = set(tokenize(question))
    if not terms & {"list", "table", "tabulate", "compare", "comprehensive"}:
        return list(ranked)
    preferred: list[tuple[Passage, float]] = []
    ordinary: list[tuple[Passage, float]] = []
    for entry in ranked:
        passage, score = entry
        lines = passage.text.splitlines()
        matching = False
        for i, line in enumerate(lines[:-1]):
            if line.strip().startswith("|") and re.fullmatch(
                r"\s*\|(?:\s*:?-+:?\s*\|)+\s*", lines[i + 1]
            ):
                # Require two distinct requested header terms, not body-name hits.
                matching = len(set(tokenize(line)) & terms) >= 2
                if matching:
                    break
        (preferred if matching and score > 0 else ordinary).append(entry)
    return preferred + ordinary
