"""Keep inline citation numbers consistent with the validated citation list."""

from __future__ import annotations

import re


_MARKER = re.compile(r"\[([^\[\]\n]+)\]")


def repair_markers(answer: str, citation_count: int, citation_ids: tuple[str, ...] = ()) -> tuple[str, int]:
    """Turn exact cited chunk IDs into display numbers and discard invalid markers."""
    repairs = 0
    positions = {chunk_id: index + 1 for index, chunk_id in enumerate(citation_ids)}

    def replace(match: re.Match[str]) -> str:
        nonlocal repairs
        value = match.group(1).strip()
        if value.isdecimal():
            number = int(value)
            if 1 <= number <= citation_count:
                return f"[{number}]"
            repairs += 1
            return ""
        if value in positions:
            repairs += 1
            return f"[{positions[value]}]"
        if value.startswith("chunk_"):
            repairs += 1
            return ""
        return match.group(0)

    # Code snippets can contain array indexes and bracketed literals. Neither
    # is a citation, even when its number is outside the citation list.
    code_span = re.compile(r"(```[\s\S]*?```|`[^`\n]*`)")
    parts = code_span.split(answer)
    return "".join(part if index % 2 else _MARKER.sub(replace, part)
                   for index, part in enumerate(parts)), repairs
