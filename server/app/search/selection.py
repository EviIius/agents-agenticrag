"""Conservative selection of numeric table rows, without a model call.

The cached page remains unchanged. Returned passages persist as the exact model
evidence, including an explicit host annotation that identifies computed selection.
"""

import operator
import re
from collections.abc import Callable
from decimal import Decimal, InvalidOperation

from ..schemas import Passage
from .chunk import chunk


def literal_condition_rows(
    url: str,
    text: str,
    contract: dict[str, object] | None,
    question: str,
    source_chunk: Callable[[str, str], list[Passage]] = chunk,
) -> list[Passage]:
    """Select a supported numeric subset; unsupported conditions preserve the evidence."""
    if not contract:
        return source_chunk(url, text)
    span = contract.get("request_span")
    word = contract.get("property_word")
    operation = contract.get("operator")
    occurrence = operation in {"occurred", "not_occurred"}
    never = operation == "not_occurred"
    threshold_value = contract.get("value")
    if operation == "occurred":
        operation, threshold_value = "gt", 0
    elif operation == "not_occurred":
        operation, threshold_value = "eq", 0
    if (
        not isinstance(span, str)
        or not span.strip()
        or span.casefold() not in question.casefold()
        or not isinstance(word, str)
        or not re.fullmatch(r"[a-zA-Z]{1,40}", word)
        or operation not in {"gt", "gte", "lt", "lte", "eq", "ne"}
    ):
        return source_chunk(url, text)

    def tokens(body: str) -> set[str]:
        forms = {
            "lost": "loss",
            "lose": "loss",
            "won": "win",
            "died": "death",
            "born": "birth",
            "sold": "sale",
            "grew": "growth",
            "grown": "growth",
            "fell": "fall",
            "fallen": "fall",
        }
        result = set()
        for word in re.findall(r"[^\W_]+", body.casefold()):
            if word.endswith(("sses", "xes", "ches", "shes", "zes")):
                word = word[:-2]
            elif len(word) > 4 and word.endswith("ies"):
                word = word[:-3] + "y"
            elif len(word) > 3 and word.endswith("s") and not word.endswith(("ss", "us", "is")):
                word = word[:-1]
            result.add(forms.get(word, word))
        return result

    required = tokens(word)
    if not required or not required <= tokens(span):
        return source_chunk(url, text)
    try:
        threshold = Decimal(str(threshold_value))
    except InvalidOperation:
        return source_chunk(url, text)
    if not threshold.is_finite():
        return source_chunk(url, text)
    # An explicit threshold must bind its comparison, not just contain the number.
    # Unit conversion, dates, written-out thresholds and compound comparisons are
    # deliberately unsupported; declining leaves the original evidence intact.
    explicit = {Decimal(v) for v in re.findall(r"[-+]?\d+(?:\.\d+)?", span)}
    negative = bool(tokens(span) & {"no", "not", "never", "without", "none"})
    if occurrence:
        if explicit or negative != never:
            return source_chunk(url, text)
    elif threshold not in explicit:
        return source_chunk(url, text)
    else:
        if len(explicit) != 1 or (negative and operation != "ne") or re.search(r"\d,\d", span):
            return source_chunk(url, text)
        comparisons = {
            "gt": r"(?:more than|greater than|over|above|>)",
            "gte": r"(?:at least|greater than or equal to|>=|≥)",
            "lt": r"(?:less than|fewer than|under|below|<)",
            "lte": r"(?:at most|less than or equal to|<=|≤)",
            "eq": r"(?:exactly|equal to|=)",
            "ne": r"(?:not equal to|!=|≠)",
        }
        bound = re.findall(comparisons[str(operation)] + r"\s*([-+]?\d+(?:\.\d+)?)", span, re.I)
        if len(bound) != 1 or Decimal(bound[0]) != threshold:
            return source_chunk(url, text)
    if re.search(r"[%$€£/]|\b(?:hundred|thousand|million|billion|trillion)\b", span, re.I):
        return source_chunk(url, text)
    output: list[Passage] = []
    for passage in source_chunk(url, text):
        rows = [line for line in passage.text.splitlines() if line.startswith("|")]
        if not rows:
            output.append(passage.model_copy(update={"ord": len(output)}))
            continue
        headers = [c.strip() for c in re.split(r"(?<!\\)\|", rows[0])[1:-1]]
        matches = [header for header in headers if required <= tokens(header)]
        if len(matches) != 1:
            output.append(passage.model_copy(update={"ord": len(output)}))
            continue
        index = headers.index(matches[0])
        # Extra column words must not silently introduce a different measure or unit.
        if tokens(matches[0]) - tokens(span) - {"count", "total", "number", "of", "times"}:
            output.append(passage.model_copy(update={"ord": len(output)}))
            continue
        if re.search(r"[%$€£/]", matches[0]):
            output.append(passage.model_copy(update={"ord": len(output)}))
            continue
        cells = [[c.strip() for c in re.split(r"(?<!\\)\|", row)[1:-1]] for row in rows]
        if any(len(row) != len(headers) for row in cells):
            output.append(passage.model_copy(update={"ord": len(output)}))
            continue
        values = [row[index] for row in cells[2:]]
        known = [value for value in values if value not in {"", "-", "–", "—", "n/a", "N/A"}]
        if not known or any(
            not re.fullmatch(r"[-+]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?", value) for value in known
        ):
            output.append(passage.model_copy(update={"ord": len(output)}))
            continue
        if occurrence and any(
            Decimal(value.replace(",", "")) < 0 or Decimal(value.replace(",", "")) % 1
            for value in known
        ):
            output.append(passage.model_copy(update={"ord": len(output)}))
            continue
        selected = _numeric_table_text(
            passage.text,
            {"column": matches[0], "operator": str(operation), "value": str(threshold)},
        )
        for part in (
            chunk(url, selected)
            if len(selected) > 3000
            else [passage.model_copy(update={"text": selected})]
        ):
            output.append(
                part.model_copy(
                    update={
                        "heading": passage.heading,
                        "ord": len(output),
                        "selection_applied": selected != passage.text,
                    }
                )
            )
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
    applied = False
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
                labelled = list(cells[index])
                labelled[column] = predicate["column"] + ": " + cell
                labelled.append("[pending]")
                matched.append("| " + " | ".join(labelled) + " |")
        # The selected table is a subset. Its original attached prose may state
        # totals or conclusions about the whole population and is not subset evidence.
        # Keep the full page in the cache; provide the scoped table with host metadata.
        output = []
        applied = True
        output.append(
            f"Host selection: {len(matched)} supported rows match {predicate['column']} "
            f"{predicate['operator']} {value}. Missing values were not treated as zero. "
            "Host reference is the citation label for each selected row."
        )
        output.append("")
        output.append(rows[0].rstrip() + " Host reference |")
        if offset == 2:
            output.append(rows[1].rstrip() + " --- |")
        output.extend(matched)
        start = end
    return "\n".join(output) if applied else text


def bind_references(passage: Passage, number: int) -> Passage:
    """Bind only host-added table reference cells after sources are numbered."""
    if not passage.selection_applied:
        return passage
    lines = [
        re.sub(r"\|\s*\[pending\]\s*\|\s*$", f"| [{number}] |", line)
        if line.startswith("|")
        else line
        for line in passage.text.splitlines()
    ]
    return passage.model_copy(update={"text": "\n".join(lines)})
