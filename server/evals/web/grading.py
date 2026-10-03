"""Declared regex assertions, including alternative equivalent answer formats."""

import re
from typing import Any


def required_facts(answer: str, expect: dict[str, Any]) -> bool:
    patterns = expect.get("must_include_last", expect.get("must_include", []))
    mandatory = all(re.search(pattern, answer, re.I) for pattern in patterns)
    alternatives = expect.get("must_include_one_of", [])
    return mandatory and (
        not alternatives
        or any(all(re.search(pattern, answer, re.I) for pattern in group) for group in alternatives)
    )


def cited_list_items(answer: str) -> bool:
    """A citation in the introduction does not cite every Markdown list item."""
    items = [line for line in answer.splitlines() if re.match(r"^\s*(?:[-*+]\s+|\d+[.)]\s+)", line)]
    table = [line.strip() for line in answer.splitlines() if line.strip().startswith("|")]
    if len(table) > 1 and re.fullmatch(r"\|(?:\s*:?-+:?\s*\|)+\s*", table[1]):
        items += table[2:]
    return bool(items) and all(re.search(r"\[\d+\]", line) for line in items)


def citation_coverage(answer: str, sources: list[dict[str, Any]], expect: dict[str, Any]) -> bool:
    """Check cited claims and declared source provenance, not arbitrary diversity."""
    from app.search.citations import cited

    by_number = {source["n"]: source for source in sources}
    for pattern in expect.get("cited_claim_patterns", []):
        matching = [
            line
            for line in answer.splitlines()
            if re.search(pattern, line, re.I)
            and (not line.rstrip().endswith(":") or bool(cited(line)))
        ]
        if not matching or not all(
            cited(line) and cited(line) <= by_number.keys() for line in matching
        ):
            return False
    for pattern in expect.get("cited_url_patterns", []):
        if not any(
            n in by_number and re.search(pattern, by_number[n]["url"], re.I) for n in cited(answer)
        ):
            return False
    return True
