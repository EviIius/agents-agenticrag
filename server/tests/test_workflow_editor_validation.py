"""The browser and server share literal validation vectors."""

import json
from pathlib import Path
from typing import Any

import pytest

from app.workflows.graph import GraphDoc, validate

CASES = json.loads(
    (Path(__file__).resolve().parents[2] / "shared/workflow_graph_cases.json").read_text()
)


@pytest.mark.parametrize("case", CASES, ids=lambda case: case["name"])
def test_shared_editor_validation(case: dict[str, Any]) -> None:
    doc = GraphDoc.model_validate(case["graph"])
    assert [i.model_dump() for i in validate(doc)] == case["issues"]
