"""Add existing timestamp labels without duplicating or dropping transcript text."""

from typing import Any


def timestamped(text: str, segments: list[dict[str, Any]]) -> str:
    if not segments:
        return text
    pieces: list[str] = []
    cursor = 0
    for segment in segments:
        literal = str(segment.get("text", ""))
        if not literal or not isinstance(segment.get("start"), (int, float)):
            return text
        position = text.find(literal, cursor)
        if position < 0:
            return text
        pieces.extend([text[cursor:position], f"[{segment['start']}s] ", literal])
        cursor = position + len(literal)
    pieces.append(text[cursor:])
    return "".join(pieces)
