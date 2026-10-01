import re

from ..schemas import Passage


def chunk(url: str, text: str) -> list[Passage]:
    blocks: list[tuple[str, str]] = []
    heading = ""
    # Split table boundaries even when extraction omitted a blank line.
    lines = text.splitlines()
    groups: list[str] = []
    current: list[str] = []
    table = False
    for line in lines + [""]:
        is_table = line.lstrip().startswith("|")
        if not line.strip() or (current and is_table != table):
            if current:
                groups.append("\n".join(current))
                current = []
        if line.strip():
            current.append(line)
            table = is_table
    for block in groups:
        if re.match(r"^#{1,4}\s", block):
            heading = block.splitlines()[0].lstrip("# ")
        if block.startswith("|"):
            rows = block.splitlines()
            header = "\n".join(rows[:2])
            part = header
            for row in rows[2:]:
                if len(row) + len(header) + 1 > 3000:
                    # An enormous table cell remains bounded, rather than swallowing the page.
                    row = row[: max(1, 2999 - len(header))]
                if len(part) + len(row) + 1 > 3000:
                    blocks.append((heading, part))
                    part = header
                part += "\n" + row
            blocks.append((heading, part))
        else:
            while len(block) > 1600:
                cut = max(block.rfind(". ", 0, 1600), block.rfind("\n", 0, 1600))
                cut = cut + 1 if cut > 0 else 1600
                blocks.append((heading, block[:cut].strip()))
                block = block[cut:].strip()
            if block:
                blocks.append((heading, block))
    out: list[Passage] = []
    for heading, block in blocks:
        if out and out[-1].heading == heading and len(out[-1].text) + len(block) + 2 <= 900:
            out[-1].text += "\n\n" + block
        else:
            out.append(Passage(source_url=url, heading=heading, ord=len(out), text=block))
    return out
