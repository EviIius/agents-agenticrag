"""Freeze active prompt templates and T2's unimplemented design prompt."""

import ast
import hashlib
import json
import re
from pathlib import Path

from app.db.settings import DEFAULTS
from app.search.planner import PROMPT as PLANNER
from app.search.prompt import PROMPT as ANSWER

ROOT = Path(__file__).resolve().parents[2]


def test_phase3_prompt_hashes() -> None:
    values = {
        "search/planner.py": PLANNER,
        "search/prompt.py": ANSWER,
        "default-system": DEFAULTS["default_system_prompt"],
    }
    tree = ast.parse((ROOT / "server/app/runs/titles.py").read_text())
    message = next(
        n
        for n in ast.walk(tree)
        if isinstance(n, ast.Call)
        and isinstance(n.func, ast.Name)
        and n.func.id == "ProviderMessage"
    )
    values["runs/titles.py"] = json.dumps(
        [
            n.value
            for n in ast.walk(message.args[1])
            if isinstance(n, ast.Constant) and isinstance(n.value, str)
        ],
        ensure_ascii=False,
    )
    # Also freeze attachment/date wrapper strings; this conservatively includes error literals.
    tree = ast.parse((ROOT / "server/app/runs/context.py").read_text())
    function = next(
        n for n in tree.body if isinstance(n, ast.AsyncFunctionDef) and n.name == "assemble"
    )
    values["runs/context.py"] = json.dumps(
        [
            n.value
            for n in ast.walk(function)
            if isinstance(n, ast.Constant) and isinstance(n.value, str)
        ],
        ensure_ascii=False,
    )
    match = re.search(
        r"### 6\.2 Prompt.*?```text\n(.*?)\n```",
        (ROOT / "docs/TRANSCRIPTION-SPEC.md").read_text(),
        re.S,
    )
    assert match is not None
    values["transcription-cleanup-spec"] = match.group(1)
    actual = {name: hashlib.sha256(value.encode()).hexdigest() for name, value in values.items()}
    expected = json.loads((ROOT / "artifacts/baseline/prompt-hashes-phase3.json").read_text())
    assert actual == expected, (
        "Prompt changes require linked before/after eval evidence, "
        "then an intentional baseline update."
    )
