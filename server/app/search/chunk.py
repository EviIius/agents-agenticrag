import re

from ..schemas import Passage


def table_header(rows: list[str]) -> list[str]:
    if len(rows) > 1 and re.fullmatch(r"\|(?:\s*:?-+:?\s*\|)+\s*", rows[1]):
        return rows[:2]
    return rows[:1]


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
            current.append(line.strip() if is_table else line)
            table = is_table
    # Extractors can split one HTML table into adjacent Markdown tables with
    # repeated headers. Keep that data together before applying passage limits.
    joined: list[str] = []
    for group in groups:
        if group.startswith("|") and joined and joined[-1].startswith("|"):
            rows, previous = group.splitlines(), joined[-1].splitlines()
            repeated = table_header(rows)
            if repeated == table_header(previous):
                joined[-1] += "\n" + "\n".join(rows[len(repeated) :])
                continue
        joined.append(group)
    for block in joined:
        if re.match(r"^#{1,4}\s", block):
            heading = block.splitlines()[0].lstrip("# ") or heading
        if block.startswith("|"):
            rows = block.splitlines()
            header_rows = table_header(rows)
            header = "\n".join(header_rows)[:2998]
            part = header
            for row in rows[len(header_rows) :]:
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
        if (
            out
            and block.startswith("|")
            and "\n|" not in out[-1].text
            and not out[-1].text.startswith("|")
            and out[-1].heading == heading
            and len(out[-1].text) <= 900
            and len(out[-1].text) + len(block) + 2 <= 3000
        ):
            # Keep a table's short caption with its complete data. Otherwise
            # three highly ranked captions can crowd out the table itself.
            out[-1].text += "\n\n" + block
            continue
        if (
            out
            and not block.startswith("|")
            and not out[-1].text.startswith("|")
            and "\n|" not in out[-1].text
            and out[-1].heading == heading
            and len(out[-1].text) + len(block) + 2 <= 900
        ):
            out[-1].text += "\n\n" + block
        else:
            out.append(Passage(source_url=url, heading=heading, ord=len(out), text=block))
    return out
