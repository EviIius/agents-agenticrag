"""Local citation placement for evaluation; never repair the generated answer."""

import re


def claim_units(answer: str) -> list[str]:
    """Bind a same-line post-period reference to only the preceding sentence.

    A reference below a paragraph, bullet or table cannot cite previous units.
    Moving punctuation internally avoids lending the reference to the following
    sentence. This tests placement, not whether an arbitrary claim is true.
    """
    bound = re.sub(
        r"([.!?])([ \t]*)((?:\[\d+\](?!\()[ \t]*)+)",
        lambda match: " " + match[3].rstrip() + match[1] + " ",
        answer,
    )
    # A reference after the closing Markdown delimiter is outside its row.
    bound = re.sub(r"(?m)^(\s*\|.*\|)[ \t]*(?:\[\d+\][ \t]*)+$", r"\1", bound)
    return [unit for unit in re.split(r"(?<=[.!?])\s+|\n", bound) if unit.strip()]
