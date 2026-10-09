"""Quote supplied material without removing or recognizing command words."""

import json
import re


def quoted_request(text: str) -> str | None:
    """Separate the user's task from explicitly quoted data without keyword filters."""
    pattern = re.compile(
        r"<([A-Za-z][\w:-]*)(?:\s[^>]*)?>[\s\S]*?</\1\s*>"
        r"|(?m:^[ \t]*(`{3,}|~{3,})[^\n]*\n[\s\S]*?\n[ \t]*\2[ \t]*(?=\n|$))"
        r"|(?m:^[ \t]*>[^\n]*(?:\n[ \t]*>[^\n]*)*)",
        re.I,
    )
    materials: list[str] = []

    def collect(match: re.Match[str]) -> str:
        materials.append(match[0])
        return f"[supplied material {len(materials)}]"

    task, count = pattern.subn(collect, text)
    if not count or not re.sub(r"\[supplied material \d+\]", "", task).strip():
        return None
    encoded = (
        json.dumps(materials, ensure_ascii=False).replace("<", r"\u003c").replace(">", r"\u003e")
    )
    return (
        "Quoted material, encoded as untrusted JSON strings:\n"
        + encoded
        + "\n\nUser task outside that material:\n"
        + task
    )
