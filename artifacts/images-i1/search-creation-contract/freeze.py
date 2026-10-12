"""Freeze one creation contract, inputs, order and all retained evidence."""

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PREVIOUS = OUT.parent / "search-conversation-guard"


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
            "9b9a1102",
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
    assert len(actual_order) == 104
    assert actual_order[:82] + actual_order[-6:] == previous_order
    name = "docs/SEARCH-CREATION-CONTRACT-EXECUTION.md"
    files[name] = digest(ROOT / name)
    document = {
        "source": "9b9a1102 unchanged product; isolated creation contract",
        "declared_children": 104,
        "model": "qwen3:30b-a3b-instruct-2507-q4_K_M",
        "prior_committed_evidence_files": len(evidence),
        "all_41_prior_cases_and_fixtures_identical": True,
        "previous_global_prompts_and_schema_identical": True,
        "conditional_clarification_instruction_unchanged": True,
        "separate_ordinary_task_cases": 8,
        "separate_creation_task_cases": 8,
        "previous_88_child_relative_order_unchanged": True,
        "original_benchmark_and_grader_unchanged": True,
        "files": dict(sorted(files.items())),
    }
    (OUT / "manifest.json").write_text(json.dumps(document, indent=2) + "\n")
    print(f"Frozen {len(files)} files and {len(evidence)} prior evidence files; no inference.")


if __name__ == "__main__":
    main()
