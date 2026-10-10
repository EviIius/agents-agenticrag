"""Prospective named-field schema remedy; unexecuted after v13's native failure."""

import json
from typing import Any

from evals.reliability import evidence_contract_v13 as prior
from evals.reliability.evidence_contract_v10 import Catalog, no_duplicates
from evals.reliability.evidence_schema_v12 import required_columns

PROMPT = prior.PROMPT.replace(
    "selections, an array\nof objects with id and columns. For sentence units columns must be []. "
    "For rows,\ncolumns are zero-based indexes of the original fields needed by the question;\n"
    "include required_columns in their supplied order, then any additional needed columns.",
    "selections, an object keyed by supplied unit ID. For sentence units the value\n"
    "must be {}. For rows the value maps original column index strings to true:\n"
    'for example {"0":true,"2":true} selects original columns zero and two.\n'
    "Include every required_columns key and enough additional fields to answer.\n"
    "Never emit false, alternative key spellings, duplicate keys or other values.",
)


def schema(available: Catalog) -> dict[str, Any]:
    units = {}
    for group in available.units.values():
        for unit in group:
            if unit.get("unresolved_subject") or unit["kind"] == "fragment":
                continue
            row = unit["kind"] == "row"
            units[unit["id"]] = {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    str(c): {"type": "boolean", "const": True} for c in range(len(unit["header"]))
                }
                if row
                else {},
                "required": [str(c) for c in required_columns(unit)] if row else [],
            }
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["coverage", "selections"],
        "properties": {
            "coverage": {"enum": ["evidence", "partial", "unsupported"]},
            "selections": {
                "type": "object",
                "additionalProperties": False,
                "properties": units,
            },
        },
    }


def render(raw: str, available: Catalog) -> dict[str, Any]:
    try:
        if len(raw) > 65536:
            raise ValueError("Selection response too large")
        value = json.loads(raw, object_pairs_hook=no_duplicates)
        if not isinstance(value, dict) or set(value) != {"coverage", "selections"}:
            raise ValueError("Unexpected response fields")
        selections = value["selections"]
        if not isinstance(selections, dict) or len(selections) > 96:
            raise ValueError("Invalid selection count")
        owned = {u["id"]: u for group in available.units.values() for u in group}
        converted = []
        for identifier, fields in selections.items():
            if identifier not in owned:
                raise ValueError("Unknown evidence reference")
            unit = owned[identifier]
            if not isinstance(fields, dict) or any(v is not True for v in fields.values()):
                raise ValueError("Field selections must be true-valued objects")
            allowed = (
                {str(c) for c in range(len(unit["header"]))} if unit["kind"] == "row" else set()
            )
            if not set(fields).issubset(allowed):
                raise ValueError("Invalid original field reference")
            # Literal syntax conversion, not missing-field recovery: the prior
            # host still rejects omitted identity/scope, unknowns and budgets.
            converted.append({"id": identifier, "columns": [int(c) for c in fields]})
        return prior.render(
            json.dumps({"coverage": value["coverage"], "selections": converted}), available
        )
    except (TypeError, ValueError) as exc:
        return {
            "status": "rejected",
            "content": prior.DECLINE,
            "reason": str(exc),
            "verified_answer": False,
            "units": [],
        }


def build(request: Any, sources: list[Any], queries: list[str] | None = None) -> None:
    original_system = request.messages[0].content
    prior.build(request, sources, queries)
    request.messages[0].content = original_system + "\n\n" + PROMPT
    request.json_schema = schema(request._evidence_catalog)
