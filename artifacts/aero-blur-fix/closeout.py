"""Verify this isolated run and preserve regenerated historical evidence."""

import hashlib
import json
import re
import shutil
import subprocess
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "artifacts/aero-blur-fix"
PRIVATE = Path.home() / ".local/share/workbench/qa/aero-blur-fix-20261025/full-complete"
ORIGINAL = Path("/Users/evilius/Documents/GitHub/agents-agenticrag")


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(name: str, data: object) -> None:
    (OUT / name).write_text(json.dumps(data, indent=2) + "\n")


def main() -> None:
    log = (OUT / "make-e2e.log").read_text()
    log = re.sub(r"\x1b\[[0-9;]*m", "", log)
    assert re.search(r"^\s*900 passed\b", log, re.M), "Complete browser gate not green"
    assert re.search(r"^\s*4 skipped\b", log, re.M), "Existing skips changed"
    assert not re.search(r"^\s*\d+ (failed|interrupted)\b", log, re.M)
    frozen = json.loads((OUT / "executed-source.json").read_text())
    assert all(sha(ROOT / name) == digest for name, digest in frozen.items())
    before = json.loads((OUT / "preservation-before.json").read_text())
    installed = Path.home() / ".local/share/workbench/app"
    assert all(
        sha(installed / name) == digest
        for name, digest in before["installed_public_files"].items()
    )
    assert all(
        sha(ORIGINAL / "docs/next/design-critique" / name) == digest
        for name, digest in before["supplied_files"].items()
    )
    assert git("rev-parse", "main").strip() == before["base"]
    assert subprocess.check_output(
        ["git", "-C", str(ORIGINAL), "rev-parse", "HEAD"], text=True
    ).strip() == "8f38ef7bebdf970ed4cae03a52e8b94cf23c5bc8"
    assert not git("diff", "main", "--name-only", "--", "server/app", "shared", "server/pyproject.toml", "server/uv.lock").strip()

    PRIVATE.mkdir(parents=True, exist_ok=True)
    # The shared suite writes its historical paths. Retain current bytes first,
    # then restore the old tracked evidence exactly from Git in this worktree.
    changed = git("diff", "--name-only", "HEAD", "--", "artifacts").splitlines()
    archived = {}
    metrics = OUT / "metrics"
    metrics.mkdir(exist_ok=True)
    for name in changed:
        path = ROOT / name
        assert path.is_file(), name
        target = PRIVATE / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
        archived[name] = sha(target)
        if path.suffix == ".json" and (
            "performance-" in path.name
            or "first-token-" in path.name
            or "frame" in path.name
            or name == "artifacts/coverage.json"
        ):
            shutil.copyfile(path, metrics / name.replace("/", "__"))
    for pos in range(0, len(changed), 100):
        subprocess.run(
            ["git", "restore", "--source=HEAD", "--worktree", "--", *changed[pos:pos+100]],
            cwd=ROOT, check=True,
        )
    assert not git("diff", "--name-only", "HEAD", "--", "artifacts").strip()
    new = git("ls-files", "--others", "--exclude-standard", "--", "artifacts").splitlines()
    extras = {}
    for name in new:
        if name.startswith("artifacts/aero-blur-fix/"):
            continue
        path = ROOT / name
        if not path.is_file():
            continue
        target = PRIVATE / "new-captures" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
        extras[name] = sha(target)
        path.unlink()
    save("historical-evidence-preserved.json", {
        "tracked_outputs_restored": len(archived),
        "fresh_output_sha256": archived,
        "additional_captures_archived": len(extras),
        "additional_capture_sha256": extras,
        "fresh_archive": str(PRIVATE),
        "old_tracked_evidence_restored_exactly": True,
    })

    cases = []
    for path in sorted((OUT / "browser").glob("*-result.json")):
        cases.append({"case": path.stem, **json.loads(path.read_text())})
    assert len(cases) == 8
    keys = ["toolsContrast", "settingsContrast", "fallbackContrast"]
    assert all(not row[key]["failures"] for row in cases for key in keys)
    save("production-rollup.json", {
        "cases": 8,
        "engines": ["chromium", "webkit"], "widths": [390, 1440],
        "themes": ["light", "dark"],
        "sampled_text_runs": sum(row[key]["sampled_text_runs"] for row in cases for key in keys),
        "minimum_normal_contrast": min(row[key]["minimum"] for row in cases for key in keys[:2]),
        "minimum_without_blur": min(row["fallbackContrast"]["minimum"] for row in cases),
        "results": cases,
        "physical_iphone_tested": False, "safari_application_tested": False,
        "native_model_calls": 0,
    })
    with urllib.request.urlopen("http://127.0.0.1:8787/api/health", timeout=10) as response:
        assert response.status == 200
    save("verification.json", {
        "passed": True, "source_files_unchanged": len(frozen),
        "installed_public_files_unchanged": len(before["installed_public_files"]),
        "supplied_input_files_unchanged": len(before["supplied_files"]),
        "original_worktree_head_unchanged": True, "main_unchanged": True,
        "backend_and_dependency_sources_unchanged": True,
        "browser_passed": 900, "existing_browser_skips": 4,
        "native_model_calls": 0, "live_api_mutations": 0,
        "installed_health": 200, "merged_or_deployed": False,
    })
    print(json.dumps({"verified": True, "browser_passed": 900, "historical_outputs_preserved": len(archived)}))


if __name__ == "__main__":
    main()
