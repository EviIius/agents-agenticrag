"""Isolated original-passage admission; no production import or inference."""

from __future__ import annotations

import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "server"))

from app.schemas import Passage
from app.search.rank import select as original_select
from app.search.rank import tokenize


def _cells(line: str) -> list[str]:
    return [cell.strip() for cell in re.split(r"(?<!\\)\|", line)[1:-1]]


def relevant_table(text: str, question: str) -> bool:
    """Require aligned Markdown data and multiple literal requested header tokens.

    This is structural admission, not semantic entailment. It rejects numerical
    first data rows masquerading as headers and ambiguous/unrelated labels;
    it cannot certify extraction provenance or every possible natural-language
    interpretation. Original bytes are never normalized in the emitted passage.
    """
    requested = set(tokenize(question))
    groups: list[list[str]] = []
    rows: list[str] = []
    fenced = False
    for line in text.splitlines() + [""]:
        if re.match(r"^\s*(?:```|~~~)", line):
            fenced = not fenced
        if not fenced and line.strip().startswith("|") and line.strip().endswith("|"):
            rows.append(line.strip())
        elif rows:
            groups.append(rows)
            rows = []
    for group in groups:
        if len(group) < 3:
            continue
        header = _cells(group[0])
        separator = _cells(group[1])
        body = [_cells(line) for line in group[2:]]
        if (
            len(header) < 2
            or len(separator) != len(header)
            or not all(re.fullmatch(r":?-{3,}:?", cell) for cell in separator)
            or not all(len(row) == len(header) for row in body)
            or not any(any(cell for cell in row) for row in body)
        ):
            continue
        labels = [re.sub(r"[*_]", "", cell).strip() for cell in header]
        present = [label.casefold() for label in labels if label]
        if (
            len(present) < 2
            or sum(not label for label in labels) > 1
            or len(present) != len(set(present))
            or any(
                len(label) > 120
                or not re.search(r"[a-zA-Z]", label)
                or re.search(r"\d|[<>`\[\]{}]|https?://", label)
                for label in labels
                if label
            )
        ):
            continue
        matched: set[str] = set()
        for label in labels:
            words = set(tokenize(label))
            if words and words <= requested:
                matched.update(words)
        if len(matched) >= 2:
            return True
    return False


def cost(passage: Passage, ratio: float) -> int:
    return math.ceil(len(passage.text) * ratio) + 20


def select(
    ranked: list[tuple[Passage, float]],
    budget: int,
    maximum: int,
    ratio: float = 0.3,
    *,
    question: str,
) -> list[list[Passage]]:
    """Give a relevant original data unit one slot in an already eligible source.

    Source eligibility/order and limits come from the existing selector. At most
    one lower-ranked non-table passage is replaced per source. Existing tables,
    code, selection annotations and all original passage bytes remain intact.
    """
    if budget < 0 or maximum < 0 or not math.isfinite(ratio) or not 0 < ratio <= 1:
        raise ValueError("Invalid evidence budget, source limit or token ratio")
    groups = original_select(ranked, budget, maximum, ratio)
    if not question.strip() or not groups:
        return groups
    scores = {(p.source_url, p.ord): score for p, score in ranked}
    if len(scores) != len(ranked):
        return groups
    used = sum(cost(p, ratio) for group in groups for p in group)
    result = []
    for group in groups:
        url = group[0].source_url
        if any(relevant_table(p.text, question) for p in group):
            result.append(group)
            continue
        candidates = [
            p
            for p, score in ranked
            if p.source_url == url
            and p not in group
            and score > 0
            and math.isfinite(score)
            and len(p.text) <= 3000
            and p.selection_applied == group[0].selection_applied
            and relevant_table(p.text, question)
        ]
        removable = [
            p
            for p in group
            if not re.search(r"(?m)^\s*(?:\||```|~~~)", p.text) and not p.selection_applied
        ]
        replacement = None
        if removable:
            old = min(removable, key=lambda p: (scores[(url, p.ord)], -p.ord))
            for new in candidates:
                if used - cost(old, ratio) + cost(new, ratio) <= budget:
                    replacement = old, new
                    break
        if replacement is not None:
            old, new = replacement
            group = [new if p is old else p for p in group]
            used += cost(new, ratio) - cost(old, ratio)
            group = sorted(group, key=lambda p: p.ord)
        result.append(group)
    assert sum(cost(p, ratio) for group in result for p in group) <= budget
    assert len(result) <= maximum and all(len(group) <= 3 for group in result)
    return result
