"""Conservative list/table diagnostics. Not a Markdown parser or support verifier."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

LIST = re.compile(r"^( *)(?:[-+*]|\d{1,9}[.)])\s+(.*)$")
FENCE = re.compile(r"^\s*(`{3,}|~{3,})")
REFERENCE = re.compile(r"\[(\d+)\]")
DEFINITION = re.compile(r"^ {0,3}\[([^\]\n]+)\]:")


@dataclass(frozen=True)
class Unit:
    kind: str
    line: int
    text: str


@dataclass(frozen=True)
class Gap:
    kind: str
    line: int
    reason: str = "No issued inline citation in this item or row"


@dataclass(frozen=True)
class Report:
    status: str
    checked_units: int
    gaps: tuple[Gap, ...]
    unchecked_prose: bool
    claim_support_checked: bool = False
    sentence_coverage_checked: bool = False


@dataclass
class Item:
    indent: int
    content_indent: int
    line: int
    lines: list[str] = field(default_factory=list)


def escaped(text: str, at: int) -> bool:
    before = at
    while before > 0 and text[before - 1] == "\\":
        before -= 1
    return (at - before) % 2 == 1


def without_inline_code(text: str) -> str:
    """Remove paired equal-length backtick runs, including multiline spans."""
    at = 0
    parts = []
    while at < len(text):
        found = re.search(r"`+", text[at:])
        if not found:
            parts.append(text[at:])
            break
        start, end = at + found.start(), at + found.end()
        if escaped(text, start):
            parts.append(text[at:end])
            at = end
            continue
        parts.append(text[at:start])
        run = text[start:end]
        close = end
        while True:
            close = text.find(run, close)
            if close < 0:
                parts.append(text[start:])
                return "".join(parts)
            if (close == 0 or text[close - 1] != "`") and (
                close + len(run) == len(text) or text[close + len(run)] != "`"
            ):
                break
            close += len(run)
        parts.append(" ")
        at = close + len(run)
    return "".join(parts)


def visible_lines(text: str) -> list[str]:
    """Exclude fenced examples and block quotes without granting their citations."""
    out = []
    fence = ""
    for raw in text.expandtabs(4).splitlines():
        probe = LIST.match(raw)
        body = probe[2] if probe else raw
        if fence:
            if re.fullmatch(r"\s*" + re.escape(fence[0]) + "{" + str(len(fence)) + r",}\s*", raw):
                fence = ""
            out.append("")
        elif match := FENCE.match(body):
            fence = match[1]
            out.append("")
        elif raw.lstrip().startswith(">"):
            out.append("")
        else:
            out.append(raw)
    return out


def cells(line: str) -> list[str]:
    line = line.strip()
    cuts = [at for at, char in enumerate(line) if char == "|" and not escaped(line, at)]
    starts, ends = [0, *(at + 1 for at in cuts)], [*cuts, len(line)]
    values = [line[start:end] for start, end in zip(starts, ends, strict=True)]
    if values and not values[0]:
        values = values[1:]
    if values and not values[-1]:
        values = values[:-1]
    return [v.strip() for v in values]


def units(text: str) -> tuple[list[Unit], bool, set[str]]:
    lines = visible_lines(text)
    definitions = {m[1].strip().casefold() for raw in lines if (m := DEFINITION.match(raw))}
    result: list[Unit] = []
    stack: list[Item] = []
    unchecked = False
    blank = False
    table = False

    def flush(item: Item) -> None:
        if any(line.strip() for line in item.lines):
            result.append(Unit("list_item", item.line, "\n".join(item.lines)))
            item.lines.clear()

    at = 0
    while at < len(lines):
        raw = lines[at]
        line = at + 1
        at += 1
        stripped = raw.strip()
        if not stripped:
            if stack:
                flush(stack[-1])
            blank, table = True, False
            continue
        if DEFINITION.match(raw) or re.match(r"^#{1,6}(?:\s|$)", stripped):
            for item in stack:
                flush(item)
            stack.clear()
            table = False
            continue
        if re.fullmatch(r"(?:-\s*){3,}|(?:\*\s*){3,}|(?:_\s*){3,}", stripped):
            continue
        if at < len(lines) and "|" in raw + lines[at]:
            separator = cells(lines[at])
            if (
                separator
                and len(separator) == len(cells(raw))
                and all(re.fullmatch(r":?-+:?", cell) for cell in separator)
            ):
                for item in stack:
                    flush(item)
                stack.clear()
                at += 1  # Header/delimiter citations cannot cover data rows.
                table = True
                continue
        if table and "|" in raw:
            result.append(Unit("table_row", line, raw))
            continue
        table = False
        marker = LIST.match(raw)
        indent = len(raw) - len(raw.lstrip())
        if marker and (indent < 4 or stack):
            while stack and indent <= stack[-1].indent:
                flush(stack.pop())
            if stack:
                flush(stack[-1])  # A child cannot cite its parent's own text.
            stack.append(Item(indent, marker.start(2), line, [marker[2]]))
            blank = False
            continue
        if stack:
            while stack and indent < stack[-1].content_indent and (blank or len(stack) > 1):
                flush(stack.pop())
            if stack and indent < stack[-1].content_indent + 4:
                if not stack[-1].lines:
                    stack[-1].line = line
                stack[-1].lines.append(raw)
                blank = False
                continue
            if stack:
                continue  # Indented example: never grants a citation.
        if indent < 4:
            unchecked = True
        blank = False
    for item in stack:
        flush(item)
    return sorted(result, key=lambda unit: unit.line), unchecked, definitions


def check(text: str, source_count: int) -> Report:
    if type(source_count) is not int or source_count < 0:
        raise ValueError("Source count must be a nonnegative integer")
    found, prose, definitions = units(text)
    if not source_count:
        return Report("not_checked", 0, (), prose)
    gaps = []
    for unit in found:
        visible = without_inline_code(unit.text)
        references = {
            int(m[1])
            for m in REFERENCE.finditer(visible)
            if not escaped(visible, m.start())
            and m[1] not in definitions
            and not visible[m.end() :].startswith("(")
            and not (
                (link := re.match(r"\s*\[([^\]]+)\]", visible[m.end() :]))
                and link[1].strip().casefold() in definitions
            )
            and 1 <= int(m[1]) <= source_count
        }
        if not references:
            gaps.append(Gap(unit.kind, unit.line))
    status = "gaps_detected" if gaps else "no_obvious_gaps" if found else "not_checked"
    return Report(status, len(found), tuple(gaps), prose)


def warn_copy(message, source_count: int):
    """Demonstrate future metadata wiring on a COPY; no live hook or content repair."""
    from app.schemas import ErrorDetail

    result = check(message.content, source_count)
    copy = message.model_copy(deep=True)
    if result.gaps and copy.agent and copy.status == "complete" and copy.agent.notice is None:
        copy.agent.notice = ErrorDetail(
            code="citation_coverage",
            message="Some list items or table rows have no source citation.",
        )
    return copy, result
