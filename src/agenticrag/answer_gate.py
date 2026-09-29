"""Deterministic final checks shared by corpus-grounded answer paths.

The gate proves citation provenance and simple numeric consistency. It does not
claim semantic entailment; that requires an independently labelled evaluation.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Sequence

from .citation_markers import repair_markers
from .domain import Citation, RankedChunk
from .errors import WorkflowError


_NUMBER = re.compile(r"\b\d+(?:[.,]\d+)?\b")
_CODE = re.compile(r"(```[\s\S]*?```|`[^`\n]*`)")
_WORDS = {"zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
          "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
          "ten": "10", "eleven": "11", "twelve": "12"}


@dataclass(frozen=True)
class GateResult:
    answer: str
    marker_repairs: int
    checks: dict[str, str]


def normalize_quote(value: str) -> str:
    return " ".join(value.casefold().split())


def _visible_text(answer: str) -> str:
    """Code is data, so bracket indexes and numeric literals are not claims."""
    return _CODE.sub("", answer)


def validate_grounded_numbers(
    answer: str, citations: Sequence[Citation], evidence: Sequence[RankedChunk],
) -> None:
    cited = {citation.chunk_id for citation in citations}
    source_text = " ".join(item.chunk.text for item in evidence if item.chunk.id in cited).casefold()
    available = set(_NUMBER.findall(source_text))
    available.update(value for word, value in _WORDS.items()
                     if re.search(rf"\b{word}\b", source_text))
    clean = re.sub(r"\[\d+\]", "", _visible_text(answer))
    clean = re.sub(r"(?m)^[ \t]*\d+[.)][ \t]+", "", clean)
    for number in set(_NUMBER.findall(clean)):
        if number not in available:
            raise WorkflowError(f"Answer includes {number}, which is absent from cited evidence")


def check_answer(
    answer: str, abstained: bool, citations: Sequence[Citation],
    evidence: Sequence[RankedChunk], *, external_sources: bool = False,
) -> GateResult:
    """Check the answer once, in a stable order, before it reaches the UI."""
    checks: dict[str, str] = {}
    by_id = {item.chunk.id: item.chunk for item in evidence}
    if any(citation.chunk_id not in by_id for citation in citations):
        raise WorkflowError("Answer cites evidence outside the authorized retrieval set")
    checks["citation_resolution"] = "passed"

    for citation in citations:
        if not citation.quotes:
            raise WorkflowError(f"Citation {citation.chunk_id} has no supporting quote")
        content = normalize_quote(by_id[citation.chunk_id].text)
        for quote in citation.quotes:
            if not isinstance(quote, str) or not quote.strip() or len(quote) > 200:
                raise WorkflowError(f"Citation {citation.chunk_id} has an invalid supporting quote")
            if normalize_quote(quote) not in content:
                raise WorkflowError(f"Citation {citation.chunk_id} quote is absent from cited evidence")
    checks["quote_verification"] = "passed" if citations else "not_applicable"

    if citations and not abstained:
        validate_grounded_numbers(answer, citations, evidence)
        checks["numeric_grounding"] = "passed"
    else:
        checks["numeric_grounding"] = "not_applicable" if not external_sources else "external_unverified"

    answer, marker_repairs = repair_markers(
        answer, len(citations), tuple(citation.chunk_id for citation in citations)
    )
    visible = _visible_text(answer)
    present = {int(value) for value in re.findall(r"\[(\d+)\]", visible)}
    if citations and not abstained and len(citations) == 1 and not present:
        answer = answer.rstrip() + " [1]"
        marker_repairs += 1
        present = {1}
    missing = set(range(1, len(citations) + 1)) - present
    if missing and not abstained:
        raise WorkflowError("Answer omits inline markers for cited sources: " +
                            ", ".join(str(number) for number in sorted(missing)))
    checks["marker_coverage"] = "passed" if citations else "not_applicable"

    if abstained and citations:
        raise WorkflowError("An abstained answer cannot carry corpus citations")
    if not abstained and not citations and not external_sources:
        raise WorkflowError("A sourced answer needs verified citations")
    checks["abstention_consistency"] = "passed"
    return GateResult(answer=answer, marker_repairs=marker_repairs, checks=checks)
