"""Freeze active prompt templates and T2's unimplemented design prompt."""

import ast
import hashlib
import json
import re
from pathlib import Path

from app.db.settings import DEFAULTS
from app.library.prompt import PROMPT as LIBRARY
from app.runs.research import ANSWER_PROMPT as RESEARCH_ANSWER
from app.runs.research import PROMPT as RESEARCH
from app.runs.research import PROMPT_V1 as RESEARCH_V1
from app.runs.research import PROMPT_V2 as RESEARCH_V2
from app.search.planner import PROMPT as PLANNER
from app.search.prompt import PROMPT as ANSWER

ROOT = Path(__file__).resolve().parents[2]


def test_library_prompt_v3_hash() -> None:
    # Approved 6 October; before/after reports are linked in PHASE-7-REPORT.md.
    # Original baseline: evals/library/reports/2026-10-06-114229-full.json.
    assert (
        hashlib.sha256(LIBRARY.encode()).hexdigest()
        == "1e2b0f1e7a08ddf7ee4628b96165bbd24b7b73fbfae3020559f3e4d902fcfbc1"
    ), "Prompt edits require linked before/after eval evidence and an intentional hash update."


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


def test_research_prompt_v1_hash() -> None:
    # 8A uses the approved plan's exact v1 prompt. Prototype reports are retained.
    assert (
        hashlib.sha256(RESEARCH_V1.encode()).hexdigest()
        == "3219a0a3564f120f404a28c6bc4eef6be1ff3e569521684ae4eade454da5b48f"
    )


def test_research_prompt_v2_hash() -> None:
    assert (
        hashlib.sha256(RESEARCH_V2.encode()).hexdigest()
        == "a6120a09fe98bcbb96beefd4e3d47a56157038bab7f350aeb8c001e8ce06a164"
    )


def test_research_refinement_prompt_hashes() -> None:
    assert hashlib.sha256(RESEARCH.encode()).hexdigest() == (
        "1c4c14794cb1cf522907030903b8f6052ac0e8889ef1eb697ca63d77c3b8e7c7"
    )
    assert hashlib.sha256(RESEARCH_ANSWER.encode()).hexdigest() == (
        "d6a58dc8b356a5edfe75ab65e7af4f987cc1b671746bc5558c31395b61d193f1"
    )
