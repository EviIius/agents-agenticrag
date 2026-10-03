"""Rendering segments as plain text and SRT."""
from __future__ import annotations

from typing import Dict, List


def srt_time(seconds: float) -> str:
    ms = max(0, int(round(seconds * 1000)))
    hours, ms = divmod(ms, 3600000)
    minutes, ms = divmod(ms, 60000)
    secs, ms = divmod(ms, 1000)
    return "%02d:%02d:%02d,%03d" % (hours, minutes, secs, ms)


def to_srt(segments: List[Dict], key: str = "text") -> str:
    blocks = []
    for index, seg in enumerate(segments, 1):
        text = seg[key]
        if seg.get("speaker"):
            text = "%s: %s" % (seg["speaker"], text)
        blocks.append("%d\n%s --> %s\n%s\n" % (
            index, srt_time(seg["start"]), srt_time(seg["end"]), text))
    return "\n".join(blocks)


def to_text(segments: List[Dict], paragraph_gap: float, key: str = "text") -> str:
    """Plain text. A new paragraph starts at a long pause or a speaker change."""
    paragraphs: List[str] = []
    current: List[str] = []
    current_speaker = None
    last_end = None
    for seg in segments:
        speaker = seg.get("speaker")
        gap = (seg["start"] - last_end) if last_end is not None else 0.0
        new_para = bool(current) and (speaker != current_speaker or gap >= paragraph_gap)
        if new_para:
            paragraphs.append(_paragraph(current, current_speaker))
            current = []
        current.append(seg[key])
        current_speaker = speaker
        last_end = seg["end"]
    if current:
        paragraphs.append(_paragraph(current, current_speaker))
    return "\n\n".join(paragraphs) + ("\n" if paragraphs else "")


def _paragraph(parts: List[str], speaker) -> str:
    body = " ".join(parts)
    return "%s: %s" % (speaker, body) if speaker else body
