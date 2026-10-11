"""Freeze the corrected harness, identical inputs and every earlier evidence byte."""

import ast
import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
ORIGINAL = OUT.parent / "search-repair"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert not (OUT / "manifest.json").exists()
    previous = json.loads((ORIGINAL / "manifest.json").read_text())
    files = dict(previous["files"])
    for name, sha in files.items():
        assert digest(ROOT / name) == sha, name
    for name in ("cases.json", "prompts.json", "execution.json"):
        assert (OUT / name).read_bytes() == (ORIGINAL / name).read_bytes(), name
    for path in (ORIGINAL / "fixtures").rglob("*"):
        if path.is_file():
            assert path.read_bytes() == (OUT / path.relative_to(ORIGINAL)).read_bytes()
    spec = importlib.util.spec_from_file_location(
        "offline_verifier", ORIGINAL / "verify_harness.py"
    )
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    reviewed = helper.proposed_patch((ORIGINAL / "experiment.py").read_text())
    actual = (OUT / "experiment.py").read_text()
    assert ast.dump(ast.parse(reviewed)) == ast.dump(ast.parse(actual))
    evidence = subprocess.check_output(
        [
            "git",
            "ls-tree",
            "-r",
            "--name-only",
            "b5b4292",
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
        if path.is_file():
            files[str(path.relative_to(ROOT))] = digest(path)
    document = ROOT / "docs/SEARCH-REPAIR-RETEST-EXECUTION.md"
    files[str(document.relative_to(ROOT))] = digest(document)
    manifest = {
        "source": "ba51370 unchanged product tree; retest approved after b5b4292",
        "scope": "Same frozen candidate/order/targets; reviewed harness-only correction",
        "model": previous["model"],
        "declared_children": 54,
        "previous_invalid_trial_retained": True,
        "prior_committed_evidence_files": len(evidence),
        "copied_case_prompt_execution_fixture_bytes_identical": True,
        "harness_ast_matches_reviewed_patch": True,
        "files": dict(sorted(files.items())),
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(
        f"Frozen {len(files)} files, including {len(evidence)} prior evidence files; no inference."
    )


if __name__ == "__main__":
    main()
