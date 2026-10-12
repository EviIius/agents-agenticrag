"""Freeze one creation contract, inputs, order and all retained evidence."""

import ast
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PREVIOUS = OUT.parent / "search-abstention-retest"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert not (OUT / "manifest.json").exists()
    files = dict(json.loads((PREVIOUS / "manifest.json").read_text())["files"])
    for name, expected in files.items():
        assert digest(ROOT / name) == expected, name
    for name in (
        "cases.json",
        "supplemental-cases.json",
        "ordinary-cases.json",
        "creation-cases.json",
        "boundary-cases.json",
        "wording.py",
        "retained-answer-audit.json",
        "prompts.json",
        "schema.json",
        "instructions.json",
    ):
        assert (OUT / name).read_bytes() == (PREVIOUS / name).read_bytes(), name

    def other_policy(path):
        return [
            ast.dump(node)
            for node in ast.parse(path.read_text()).body
            if getattr(node, "name", "") not in {"literals", "local_target", "scope_target"}
        ]

    assert other_policy(OUT / "contract.py") == other_policy(PREVIOUS / "contract.py")
    for path in (PREVIOUS / "fixtures").rglob("*"):
        if path.is_file():
            assert path.read_bytes() == (OUT / path.relative_to(PREVIOUS)).read_bytes()
    evidence = subprocess.check_output(
        [
            "git",
            "ls-tree",
            "-r",
            "--name-only",
            "f046d9b8",
            "--",
            "artifacts",
            "server/evals/web/reports",
        ],
        cwd=ROOT,
        text=True,
    ).splitlines()
    for name in evidence:
        files[name] = digest(ROOT / name)
    for path in OUT.rglob("*"):
        if (
            path.is_file()
            and path.name != "freeze.log"
            and "__pycache__" not in path.parts
            and ".pytest_cache" not in path.parts
        ):
            files[str(path.relative_to(ROOT))] = digest(path)
    previous_order = json.loads((PREVIOUS / "execution.json").read_text())["order"]
    actual_order = json.loads((OUT / "execution.json").read_text())["order"]
    assert len(actual_order) == 108
    assert actual_order[2:] == previous_order
    name = "docs/SEARCH-SCOPED-INPUT-EXECUTION.md"
    files[name] = digest(ROOT / name)
    document = {
        "source": "f046d9b8 unchanged product/wording; isolated scope binding",
        "declared_children": 108,
        "model": "qwen3:30b-a3b-instruct-2507-q4_K_M",
        "prior_committed_evidence_files": len(evidence),
        "all_49_prior_cases_and_fixtures_identical": True,
        "policy_change": "bounded leading scope-modifier normalization only",
        "all_other_policy_ast_unchanged": True,
        "previous_global_prompts_and_schema_identical": True,
        "conditional_clarification_instruction_unchanged": True,
        "separate_ordinary_task_cases": 8,
        "separate_creation_task_cases": 8,
        "previous_106_child_relative_order_unchanged": True,
        "early_scope_and_code_smoke_arms": 4,
        "original_benchmark_unchanged": True,
        "isolated_equivalent_decline_correction": True,
        "files": dict(sorted(files.items())),
    }
    (OUT / "manifest.json").write_text(json.dumps(document, indent=2) + "\n")
    print(f"Frozen {len(files)} files and {len(evidence)} prior evidence files; no inference.")


if __name__ == "__main__":
    main()
