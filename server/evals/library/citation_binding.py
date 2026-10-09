"""Local citation placement for evaluation; never repair the generated answer."""

import re


def claim_units(answer: str) -> list[str]:
    """Bind a same-line post-period reference to only the preceding sentence.

    A reference below a paragraph, bullet or table cannot cite previous units.
    Moving punctuation internally avoids lending the reference to the following
    sentence. This tests placement, not whether an arbitrary claim is true.
    """
    # A row-level Citation column supports that row, including sentences and
    # decimal punctuation inside its cells. It cannot support a neighboring row.
    # Split rows before sentence binding so a period never detaches their facts.
    prose: list[str] = []
    units: list[str] = []
    for line in answer.splitlines():
        stripped = re.sub(r"[ \t]*(?:\[\d+\][ \t]*)+$", "", line)
        if re.fullmatch(r"\s*\|.*(?<!\\)\|\s*", stripped):
            if prose:
                units.extend(_sentences("\n".join(prose)))
                prose.clear()
            units.append(stripped.strip())
        else:
            prose.append(line)
    units.extend(_sentences("\n".join(prose)))
    return units


def _sentences(answer: str) -> list[str]:
    bound = re.sub(
        r"([.!?])([ \t]*)((?:\[\d+\](?!\()[ \t]*)+)",
        lambda match: " " + match[3].rstrip() + match[1] + " ",
        answer,
    )
    return [unit for unit in re.split(r"(?<=[.!?])\s+|\n", bound) if unit.strip()]
