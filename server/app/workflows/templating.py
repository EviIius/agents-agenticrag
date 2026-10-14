"""Literal interpolation with typed references; no expressions or hidden prompts."""

import json
import re
from dataclasses import dataclass
from html import escape
from typing import Any

from ..errors import AppError

TOKEN = re.compile(r"(?<!\\)\{\{(.*?)\}\}", re.DOTALL)
GRAMMAR = re.compile(
    "\\s*([a-z][a-z0-9_]{0,31})\\.([a-z][a-z0-9_]{0,31})(?:\\s*\\|\\s*tagge"
    "d:([a-z][a-z0-9_]{0,31}))?\\s*"
)


@dataclass(frozen=True)
class Reference:
    key: str
    field: str
    tag: str | None = None


def references(text: str) -> list[Reference]:
    refs: list[Reference] = []
    plain = re.sub(r"\\\{\{", "", text)
    consumed = TOKEN.sub("", plain)
    if "{{" in consumed:
        raise ValueError("Unclosed reference")
    for match in TOKEN.finditer(text):
        parsed = GRAMMAR.fullmatch(match[1])
        if not parsed:
            raise ValueError("Invalid reference")
        refs.append(Reference(*parsed.groups()))
    return refs


def exact_reference(text: str) -> Reference:
    matches = list(TOKEN.finditer(text.strip()))
    refs = references(text)
    if len(refs) != 1 or len(matches) != 1 or matches[0].group(0) != text.strip() or refs[0].tag:
        raise AppError("reference_type", "Choose one typed output reference.", 422)
    return refs[0]


def resolve(
    ref: Reference, values: dict[str, dict[str, Any]], skipped: set[str], warnings: list[str]
) -> Any:
    if ref.key in skipped:
        warning = f"The output of '{ref.key}' was skipped."
        if warning not in warnings:
            warnings.append(warning)
        return ""
    if ref.key not in values or ref.field not in values[ref.key]:
        raise AppError("reference_missing", "A referenced output is not available.", 422)
    return values[ref.key][ref.field]


def render(
    text: str,
    values: dict[str, dict[str, Any]],
    skipped: set[str],
    warnings: list[str],
    required: bool = False,
) -> str:
    references(text)
    empty_marker = "\x00EMPTY_TAG\x00"
    if "\x00" in text:
        raise AppError("reference_text", "Text cannot contain null characters.", 422)

    def replace(match: re.Match[str]) -> str:
        parsed = GRAMMAR.fullmatch(match[1])
        assert parsed
        ref = Reference(*parsed.groups())
        value = resolve(ref, values, skipped, warnings)
        if not isinstance(value, (str, int, float, bool, list, dict, type(None))):
            raise AppError("reference_type", "This value cannot be inserted as text.", 422)
        literal = (
            value
            if isinstance(value, str)
            else ""
            if value is None
            else json.dumps(value, ensure_ascii=False, separators=(",", ":"))
        )
        if "\x00" in literal:
            raise AppError("reference_text", "Text cannot contain null characters.", 422)
        if ref.tag:
            return f"<{ref.tag}>\n{escape(literal)}\n</{ref.tag}>" if literal else empty_marker
        return literal

    result = TOKEN.sub(replace, text)
    result = re.sub(r"^(?:[ \t]*" + re.escape(empty_marker) + r"[ \t]*\n)+", "", result)
    result = re.sub(r"(?:\n)?[ \t]*" + re.escape(empty_marker) + r"[ \t]*(?=\n|$)", "", result)
    result = result.replace(empty_marker, "").replace("\\{{", "{{")
    if required and not result.strip():
        raise AppError(
            "reference_empty", "A required input is empty; check skipped upstream blocks.", 422
        )
    return result
