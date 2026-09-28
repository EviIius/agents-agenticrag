"""Keep inline citation numbers consistent with the validated citation list."""

from __future__ import annotations

import re


_MARKER = re.compile(r"\[(\d+)\]")


def repair_markers(answer: str, citation_count: int) -> tuple[str, int]:
    repairs = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal repairs
        number = int(match.group(1))
        if 1 <= number <= citation_count:
            return match.group(0)
        repairs += 1
        return ""

    return _MARKER.sub(replace, answer), repairs
