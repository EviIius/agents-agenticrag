"""Generic table representation experiment, outside the production pipeline."""

import re

from app.schemas import Passage
from app.search.chunk import chunk


def named_cells(url: str, text: str) -> list[Passage]:
    """Repeat a column label beside its unchanged value; infer no missing data."""
    lines = text.splitlines()
    out = []
    headers: list[str] | None = None
    for line in lines:
        if not line.lstrip().startswith("|"):
            headers = None
            out.append(line)
            continue
        cells = re.split(r"(?<!\\)\|", line.strip())[1:-1]
        if headers is None:
            headers = [cell.strip() for cell in cells]
            out.append(line)
        elif all(re.fullmatch(r"\s*:?-+:?\s*", cell) for cell in cells):
            out.append(line)
        elif len(cells) != len(headers):
            # Complex/malformed tables remain exact, rather than guessed.
            out.append(line)
        else:
            out.append(
                "| "
                + " | ".join(
                    f"{header}: {cell.strip()}" if header else cell.strip()
                    for header, cell in zip(headers, cells, strict=True)
                )
                + " |"
            )
    return chunk(url, "\n".join(out))
