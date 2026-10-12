"""Freeze one creation contract, inputs, order and all retained evidence."""

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PREVIOUS = OUT.parent / "search-creation-contract"


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
        "contract.py",
        "prompts.json",
        "schema.json",
        "instructions.json",
    ):
        assert (OUT / name).read_bytes() == (PREVIOUS / name).read_bytes(), name
    for path in (PREVIOUS / "fixtures").rglob("*"):
        if path.is_file():
            assert path.read_bytes() == (OUT / path.relative_to(PREVIOUS)).read_bytes()
    evidence = subprocess.check_output(
        [
            "git",
            "ls-tree",
            "-r",
            "--name-only",
            "c6f0af1d",
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
    assert len(actual_order) == 106
    assert actual_order[2:] == previous_order
    name = "docs/SEARCH-ABSTENTION-RETEST-EXECUTION.md"
    files[name] = digest(ROOT / name)
    document = {
        "source": "c6f0af1d unchanged product/policy; isolated wording correction",
        "declared_children": 106,
        "model": "qwen3:30b-a3b-instruct-2507-q4_K_M",
        "prior_committed_evidence_files": len(evidence),
        "all_49_prior_cases_and_fixtures_identical": True,
        "creation_policy_byte_identical": True,
        "previous_global_prompts_and_schema_identical": True,
        "conditional_clarification_instruction_unchanged": True,
        "separate_ordinary_task_cases": 8,
        "separate_creation_task_cases": 8,
        "previous_104_child_relative_order_unchanged": True,
        "early_code_smoke_arms": 2,
        "original_benchmark_unchanged": True,
        "isolated_equivalent_decline_correction": True,
        "files": dict(sorted(files.items())),
    }
    (OUT / "manifest.json").write_text(json.dumps(document, indent=2) + "\n")
    print(f"Frozen {len(files)} files and {len(evidence)} prior evidence files; no inference.")


if __name__ == "__main__":
    main()
