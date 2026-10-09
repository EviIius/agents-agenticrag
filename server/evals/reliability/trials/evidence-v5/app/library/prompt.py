"""Frozen isolated evidence contract; not a production prompt."""

import re

from evals.reliability.evidence_contract import PROMPT, build  # noqa: F401


def sanitize(text: str) -> str:
    return re.sub(r"</(?:source|library_results)\s*>", "", text, flags=re.I)
