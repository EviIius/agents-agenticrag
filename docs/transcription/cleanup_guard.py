"""Reference code for transcript clean-up (docs/TRANSCRIPTION-SPEC.md §6).

Port this into server/app/transcribe/cleanup.py. It is tested against
cleanup_guard_cases.json, which moves to shared/ and is used by the unit tests.
"""
import math
import re
from difflib import SequenceMatcher

_WORD = re.compile(r"[a-z0-9]+(?:'[a-z0-9]+)*")


def words(text: str) -> list[str]:
    """Spoken words only: lower-case, punctuation and line breaks dropped."""
    return _WORD.findall(text.lower().replace("’", "'"))


def changed_words(source: str, cleaned: str) -> int:
    a, b = words(source), words(cleaned)
    matcher = SequenceMatcher(None, a, b, autojunk=False)
    return sum(max(i2 - i1, j2 - j1) for tag, i1, i2, j1, j2 in matcher.get_opcodes()
               if tag != "equal")


def allowed_changes(source: str) -> int:
    return max(3, math.ceil(0.02 * len(words(source))))


def accept(source: str, cleaned: str) -> bool:
    return bool(words(cleaned)) and changed_words(source, cleaned) <= allowed_changes(source)


def chunks(text: str, limit: int = 2000) -> list[str]:
    """Pack paragraphs into chunks of at most `limit` characters.

    A paragraph longer than the limit is split after sentence ends; a sentence
    longer than the limit is split at spaces. Joining the result with blank
    lines gives back every word of the input in order.
    """
    out: list[str] = []
    current = ""
    for paragraph in [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]:
        pieces = [paragraph]
        if len(paragraph) > limit:
            pieces, piece = [], ""
            for sentence in re.split(r"(?<=[.!?])\s+", paragraph):
                while len(sentence) > limit:
                    cut = sentence.rfind(" ", 0, limit)
                    cut = cut if cut > 0 else limit
                    if piece:
                        pieces.append(piece)
                        piece = ""
                    pieces.append(sentence[:cut])
                    sentence = sentence[cut:].lstrip()
                if piece and len(piece) + 1 + len(sentence) > limit:
                    pieces.append(piece)
                    piece = sentence
                else:
                    piece = (piece + " " + sentence).strip()
            if piece:
                pieces.append(piece)
        for piece in pieces:
            if current and len(current) + 2 + len(piece) > limit:
                out.append(current)
                current = piece
            else:
                current = (current + "\n\n" + piece).strip()
    if current:
        out.append(current)
    return out
