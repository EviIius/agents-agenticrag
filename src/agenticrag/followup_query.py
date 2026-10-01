"""Bounded rule-based retrieval query for short conversational follow-ups."""
from __future__ import annotations

import re
from collections.abc import Sequence
from typing import Any


_FOLLOWUP = re.compile(
    r"\b(it|its|they|them|their|that|this|those|these|one|ones|same|other|another)\b"
    r"|^(and|what about|how about|also|why|when|where|which)\b",
    re.IGNORECASE,
)


def build_retrieval_query(question: str, history: Sequence[dict[str, Any]], *,
                          max_chars: int = 500) -> str:
    """Add the latest user topic to a short follow-up without changing the question.

    History is chronological and may contain assistant/tool turns. Only the last
    user question is used; no outside content or assistant instructions enter the
    retrieval query.
    """
    current = " ".join(question.split())[:max_chars]
    if not current or not _FOLLOWUP.search(current) or len(current) > max_chars // 2:
        return current
    previous = next((str(item.get("content", "")) for item in reversed(history)
                     if item.get("role") == "user" and str(item.get("content", "")).strip()), "")
    previous = " ".join(previous.split())
    if not previous or previous == current:
        return current
    available = max_chars - len(current) - len("Previous topic: . Follow-up: ")
    return f"Previous topic: {previous[:max(0, available)]}. Follow-up: {current}"
