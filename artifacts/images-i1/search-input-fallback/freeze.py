"""Freeze one fallback candidate, inputs, order and all retained evidence."""

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PREVIOUS = OUT.parent / "search-input-contract"


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
        "boundary-cases.json",
        "prompts.json",
        "schema.json",
        "execution.json",
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
            "a243774",
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
    name = "docs/SEARCH-INPUT-FALLBACK-EXECUTION.md"
    files[name] = digest(ROOT / name)
    document = {
        "source": "a243774 unchanged product; isolated supplied-input fallback",
        "declared_children": 72,
        "model": "qwen3:30b-a3b-instruct-2507-q4_K_M",
        "prior_committed_evidence_files": len(evidence),
        "all_33_boundary_cases_and_fixtures_identical": True,
        "previous_global_prompts_and_schema_identical": True,
        "new_conditional_clarification_instruction": True,
        "original_benchmark_and_grader_unchanged": True,
        "files": dict(sorted(files.items())),
    }
    (OUT / "manifest.json").write_text(json.dumps(document, indent=2) + "\n")
    print(f"Frozen {len(files)} files and {len(evidence)} prior evidence files; no inference.")


if __name__ == "__main__":
    main()
