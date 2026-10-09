"""Unexecuted stricter schema remedy after v11's retained protocol failure."""

import json
import re
from typing import Any

from evals.reliability import evidence_contract_v11 as prior
from evals.reliability.evidence_contract_v10 import Catalog, no_duplicates

PROMPT = prior.PROMPT.replace(
    "include column 0 to preserve the row identity and at least one other column.",
    "include the supplied required_columns and at least one additional field if needed.",
)


def required_columns(unit: dict[str, Any]) -> list[int]:
    """Preserve ordinal/year plus the first labeled textual field when present.

    A blank ordinal header is not the named subject of its row. This conservative
    structural rule does not prove that any other field has the requested meaning.
    """
    required = {0} | prior.scope_columns(unit)
    for index, (header, cell) in enumerate(zip(unit["header"], unit["cells"], strict=True)):
        if header.strip() and re.search(r"[^\W\d_]", cell, re.UNICODE):
            required.add(index)
            break
    return sorted(required)


def schema(available: Catalog) -> dict[str, Any]:
    sentences, alternatives = [], []
    for group in available.units.values():
        for unit in group:
            if unit.get("unresolved_subject") or unit["kind"] == "fragment":
                continue
            if unit["kind"] != "row":
                sentences.append(unit["id"])
                continue
            mandatory = required_columns(unit)
            # Prefixes put row identity/scope before optional original fields.
            # Per-ID enums prohibit references to another row's column positions.
            alternatives.append(
                {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["id", "columns"],
                    "properties": {
                        "id": {"const": unit["id"]},
                        "columns": {
                            "type": "array",
                            "uniqueItems": True,
                            "minItems": max(2, len(mandatory)),
                            "maxItems": len(unit["header"]),
                            "prefixItems": [{"const": c} for c in mandatory],
                            "items": {
                                "type": "integer",
                                "enum": [
                                    c for c in range(len(unit["header"])) if c not in mandatory
                                ],
                            },
                        },
                    },
                }
            )
    if sentences:
        alternatives.append(
            {
                "type": "object",
                "additionalProperties": False,
                "required": ["id", "columns"],
                "properties": {
                    "id": {"type": "string", "enum": sentences},
                    "columns": {"type": "array", "maxItems": 0},
                },
            }
        )
    result = prior.schema(available)
    result["properties"]["selections"] = (
        {"type": "array", "maxItems": 96, "items": {"anyOf": alternatives}}
        if alternatives
        else {"type": "array", "maxItems": 0}
    )
    return result


def render(raw: str, available: Catalog) -> dict[str, Any]:
    # Use the same strict shape/ownership/quotation validation first.
    try:
        prior.validate(raw, available)
        value = json.loads(raw, object_pairs_hook=no_duplicates)
        owned = {u["id"]: u for group in available.units.values() for u in group}
        for selection in value["selections"]:
            unit = owned[selection["id"]]
            if unit["kind"] == "row" and not set(required_columns(unit)).issubset(
                selection["columns"]
            ):
                raise ValueError("Selected fields lost the labeled row subject")
    except (TypeError, ValueError) as exc:
        return {
            "status": "rejected",
            "content": prior.DECLINE,
            "reason": str(exc),
            "verified_answer": False,
            "units": [],
        }
    return prior.render(raw, available)


def build(request: Any, sources: list[Any], queries: list[str] | None = None) -> None:
    original_system = request.messages[0].content
    prior.build(request, sources, queries)
    available = request._evidence_catalog
    payload = json.loads(request.messages[-1].content)
    for unit in payload["units"]:
        if unit["kind"] == "row":
            unit["required_columns"] = required_columns(unit)
    request.messages[-1].content = (
        json.dumps(payload, ensure_ascii=False).replace("<", r"\u003c").replace(">", r"\u003e")
    )
    request.messages[0].content = original_system + "\n\n" + PROMPT
    request.json_schema = schema(available)
