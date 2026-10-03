"""Generic table representation experiment, outside the production pipeline."""

import json
import operator
import re
from decimal import Decimal

from app.schemas import Passage
from app.search.chunk import chunk


def numeric_rows(url: str, text: str, predicate: dict[str, str]) -> list[Passage]:
    """Evaluation-only numeric selection with a human-supplied, explicit predicate."""
    output: list[Passage] = []
    # Assemble split extractor tables before inserting selection metadata;
    # otherwise those notes separate the fragments and defeat coalescing.
    for passage in chunk(url, text):
        selected = _numeric_table_text(passage.text, predicate)
        parts = (
            chunk(url, selected)
            if len(selected) > 3000
            else [passage.model_copy(update={"text": selected})]
        )
        for part in parts:
            output.append(part.model_copy(update={"ord": len(output), "heading": passage.heading}))
    return output


def _numeric_table_text(text: str, predicate: dict[str, str]) -> str:
    compare = {
        "gt": operator.gt,
        "gte": operator.ge,
        "lt": operator.lt,
        "lte": operator.le,
        "eq": operator.eq,
        "ne": operator.ne,
    }[predicate["operator"]]
    value = Decimal(str(predicate["value"]))
    target = " ".join(predicate["column"].casefold().split())
    lines = text.splitlines()
    output: list[str] = []
    start = 0
    while start < len(lines):
        if not lines[start].lstrip().startswith("|"):
            output.append(lines[start])
            start += 1
            continue
        end = start + 1
        while end < len(lines) and lines[end].lstrip().startswith("|"):
            end += 1
        rows = lines[start:end]
        cells = [[c.strip() for c in re.split(r"(?<!\\)\|", row.strip())[1:-1]] for row in rows]
        headers = [" ".join(cell.casefold().split()) for cell in cells[0]]
        if headers.count(target) != 1 or any(len(row) != len(headers) for row in cells):
            output.extend(rows)
            start = end
            continue
        column = headers.index(target)
        offset = (
            2 if len(cells) > 1 and all(re.fullmatch(r":?-+:?", cell) for cell in cells[1]) else 1
        )
        matched = []
        unknown = 0
        for index in range(offset, len(rows)):
            cell = cells[index][column]
            if not re.fullmatch(r"[-+]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?", cell):
                unknown += 1
                continue
            if compare(Decimal(cell.replace(",", "")), value):
                matched.append(rows[index])
        output.append(
            f"Host selection (evaluation proof): {predicate['column']} "
            f"{predicate['operator']} {value}; {len(matched)} of {len(rows) - offset} rows "
            f"match. {unknown} rows have no supported numeric value and are not "
            "treated as zero. The preceding source prose describes the unfiltered source."
        )
        output.append("")
        output.extend(rows[:offset] + matched)
        start = end
    return "\n".join(output)


def annotated_nulls(url: str, text: str) -> list[Passage]:
    """Make non-numeric markers explicit, without inventing their numeric meaning."""
    lines = text.splitlines()
    start = 0
    while start < len(lines):
        if not lines[start].lstrip().startswith("|"):
            start += 1
            continue
        end = start + 1
        while end < len(lines) and lines[end].lstrip().startswith("|"):
            end += 1
        cells = [
            [cell.strip() for cell in re.split(r"(?<!\\)\|", row.strip())[1:-1]]
            for row in lines[start:end]
        ]
        header = cells[0]
        offset = (
            2 if len(cells) > 1 and all(re.fullmatch(r":?-+:?", cell) for cell in cells[1]) else 1
        )
        rows = cells[offset:]
        if header and rows and all(len(row) == len(header) for row in rows):
            numeric = {
                index
                for index in range(len(header))
                if sum(bool(re.fullmatch(r"[-+]?\d+(?:[,.]\d+)*%?", row[index])) for row in rows)
                >= max(1, sum(row[index] not in {"", "-", "–", "—"} for row in rows) / 2)
            }
            for index, row in enumerate(rows, start + offset):
                updated = [
                    cell + " (no numeric value supplied)"
                    if column in numeric and cell in {"-", "–", "—"}
                    else cell
                    for column, cell in enumerate(row)
                ]
                if updated != row:
                    lines[index] = "| " + " | ".join(updated) + " |"
        start = end
    return chunk(url, "\n".join(lines))


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


def with_section_heading(passage: Passage) -> Passage:
    heading = passage.heading.strip()
    text = passage.text
    if heading and not text.lstrip("# \n").startswith(heading):
        text = heading + "\n\n" + text
    return passage.model_copy(update={"text": text})


def row_records(url: str, text: str) -> list[Passage]:
    """Label every unchanged cell in bounded JSON records; reject ambiguous headers."""
    out: list[Passage] = []

    def append_prose(passage: Passage, body: str) -> None:
        if not body.strip():
            return
        # Keep short introductory sections together so they do not occupy
        # the slots needed by a table's continuation. Retain section labels.
        label = "## " + passage.heading + "\n\n" if passage.heading else ""
        body = label + body if len(label) + len(body) <= 1600 else body
        if (
            out
            and "```jsonl" not in out[-1].text
            and "\n|" not in out[-1].text
            and not out[-1].text.startswith("|")
            and len(out[-1].text) + len(body) + 2 <= 1600
        ):
            out[-1].text += "\n\n" + body
        else:
            out.append(passage.model_copy(update={"ord": len(out), "text": body}))

    for passage in chunk(url, text):
        lines = passage.text.splitlines()
        start = next((i for i, line in enumerate(lines) if line.startswith("|")), None)
        if start is None:
            append_prose(passage, passage.text)
            continue
        rows = lines[start:]
        cells = [[cell.strip() for cell in re.split(r"(?<!\\)\|", row)[1:-1]] for row in rows]
        headers = cells[0]
        data = (
            cells[2:]
            if len(cells) > 1 and all(re.fullmatch(r":?-+:?", cell) for cell in cells[1])
            else cells[1:]
        )
        if (
            not headers
            or len(set(headers)) != len(headers)
            or any(len(row) != len(headers) for row in data)
            or any(not row.startswith("|") for row in rows)
        ):
            out.append(passage.model_copy(update={"ord": len(out)}))
            continue
        records = [
            json.dumps(dict(zip(headers, row, strict=True)), ensure_ascii=False) for row in data
        ]
        prefix = "\n".join(lines[:start]).strip()
        if any(len(row) > 2900 for row in records) or not records:
            out.append(passage.model_copy(update={"ord": len(out)}))
            continue
        append_prose(passage, prefix)
        part = "```jsonl\n"
        for record in records:
            if len(part) + len(record) + 5 > 3000:
                out.append(passage.model_copy(update={"ord": len(out), "text": part + "```"}))
                part = "```jsonl\n"
            part += record + "\n"
        out.append(passage.model_copy(update={"ord": len(out), "text": part + "```"}))
    return out
