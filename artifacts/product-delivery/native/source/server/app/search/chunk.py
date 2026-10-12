import re

from ..schemas import Passage


def table_header(rows: list[str]) -> list[str]:
    if len(rows) > 1 and re.fullmatch(r"\|(?:\s*:?-+:?\s*\|)+\s*", rows[1]):
        return rows[:2]
    return rows[:1]


def chunk(url: str, text: str) -> list[Passage]:
    blocks: list[tuple[str, str, int]] = []
    heading = ""
    consecutive_headings: list[str] = []
    section_id = 0
    navigation_level: int | None = None
    # Split table boundaries even when extraction omitted a blank line.
    lines = text.splitlines()
    groups: list[str] = []
    current: list[str] = []
    table = False
    fenced = False
    for line in lines + [""]:
        is_fence = bool(re.match(r"^\s*(?:```|~~~)", line))
        is_heading = not fenced and bool(re.match(r"^#{1,4}\s+", line))
        is_table = not fenced and line.lstrip().startswith("|")
        if not line.strip() or is_heading or (current and is_table != table):
            if current:
                groups.append("\n".join(current))
                current = []
        if line.strip() and (fenced or line.strip() != "[edit]"):
            current.append(line.strip() if is_table else line)
            table = is_table
        if is_fence:
            fenced = not fenced
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
        section = re.match(r"^(#{1,4})\s+([^\n]+)", block)
        if section:
            level = len(section[1])
            if navigation_level is not None and level <= navigation_level:
                navigation_level = None
            if section[2].strip().casefold() in {"external links", "see also"}:
                navigation_level = level
            if navigation_level is not None:
                continue
            section_id += 1
            consecutive_headings.extend(
                line.lstrip("# ").strip()
                for line in block.splitlines()
                if re.fullmatch(r"#{1,4}\s+.*", line)
            )
            heading = " / ".join(consecutive_headings) or heading
            if all(re.fullmatch(r"#{1,4}\s+.*", line) for line in block.splitlines()):
                # The heading belongs to the following evidence, not a passage
                # with no facts that can occupy one of the source's three slots.
                continue
        if navigation_level is not None:
            continue
        consecutive_headings = []
        if block.startswith("|"):
            rows = block.splitlines()
            header_rows = table_header(rows)
            data_rows = rows[len(header_rows) :]
            if len(header_rows) == 1:
                # Trafilatura may emit pipe rows without Markdown's delimiter.
                # Add only structure; retain empty cells, dashes and every value.
                cells = re.split(r"(?<!\\)\|", header_rows[0])[1:-1]
                if cells and all(
                    len(re.split(r"(?<!\\)\|", row)[1:-1]) == len(cells) for row in data_rows
                ):
                    header_rows = [header_rows[0], "| " + " | ".join("---" for _ in cells) + " |"]
            header = "\n".join(header_rows)[:2998]
            part = header
            for row in data_rows:
                if len(row) + len(header) + 1 > 3000:
                    # An enormous table cell remains bounded, rather than swallowing the page.
                    row = row[: max(1, 2999 - len(header))]
                if len(part) + len(row) + 1 > 3000:
                    blocks.append((heading, part, section_id))
                    part = header
                part += "\n" + row
            blocks.append((heading, part, section_id))
        else:
            while len(block) > 1600:
                cut = max(block.rfind(". ", 0, 1600), block.rfind("\n", 0, 1600))
                cut = cut + 1 if cut > 0 else 1600
                blocks.append((heading, block[:cut].strip(), section_id))
                block = block[cut:].strip()
            if block:
                blocks.append((heading, block, section_id))
    out: list[Passage] = []
    out_sections: list[int] = []
    for heading, block, section_id in blocks:
        if (
            out
            and out_sections[-1] == section_id
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
            and out_sections[-1] == section_id
            and not block.startswith("|")
            and not out[-1].text.startswith("|")
            and "\n|" not in out[-1].text
            and out[-1].heading == heading
            and len(out[-1].text) + len(block) + 2 <= 900
        ):
            out[-1].text += "\n\n" + block
        else:
            out.append(Passage(source_url=url, heading=heading, ord=len(out), text=block))
            out_sections.append(section_id)
    return out
