"""Run after suites stop: retain fresh synthetic evidence and restore history."""

import hashlib
import json
import shutil
import subprocess
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
PREFIX = str(OUT.relative_to(ROOT)) + "/"
PRIVATE = Path.home() / ".local/share/workbench/qa/photo-editing-pe1-integration-20261021/browser-run"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(*args):
    return [p for p in subprocess.check_output(["git", *args, "-z"], cwd=ROOT).decode().split("\0") if p]


if (OUT / "browser-archive.json").exists():
    raise ValueError("This run is already archived; do not overwrite its audit record")
PRIVATE.mkdir(mode=0o700, parents=True, exist_ok=True)
rows = []
tracked = names("diff", "--name-only", "HEAD")
untracked = names("ls-files", "--others", "--exclude-standard")
for name in tracked + untracked:
    if not name.startswith("artifacts/") or name.startswith(PREFIX):
        continue
    source = ROOT / name
    if not source.is_file():
        raise ValueError("Unexpected removed artifact")
    archived = PRIVATE / name
    archived.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    shutil.copy2(source, archived)
    current = sha(source)
    assert sha(archived) == current
    row = {"path": name, "run_sha256": current, "bytes": source.stat().st_size}
    if name in tracked:
        original = subprocess.check_output(["git", "show", "HEAD:" + name], cwd=ROOT)
        source.write_bytes(original)
        row["historical_sha256"] = hashlib.sha256(original).hexdigest()
        assert sha(source) == row["historical_sha256"]
        row["historical_restored"] = True
    else:
        source.unlink()
        row["new_run_artifact"] = True
    rows.append(row)

# A small, shareable selection complements the complete private run archive.
screens = [
    "artifacts/photo-editing/pe1-b-20261020/browser/ready-390-dark-webkit-fake.png",
    "artifacts/attachments/at-a/browser/4-files-390-dark-chromium-fake.png",
    "artifacts/attachments/at-a/browser/HEIC-1440-dark-chromium-fake.png",
    "artifacts/chat-images/ci-b/browser/complete-390-dark-chromium-fake.png",
    "artifacts/chat-images/ci-b/browser/complete-390-dark-webkit-fake.png",
    "artifacts/workflow-studio/ws-d/browser/run-running-1440-dark-chromium-fake.png",
    "artifacts/workflow-studio/ws-d/browser/run-running-390-dark-webkit-fake.png",
]
selected = []
for name in screens:
    source = PRIVATE / name
    if source.is_file():
        target = OUT / "browser-screenshots" / source.name
        target.parent.mkdir(exist_ok=True)
        shutil.copy2(source, target)
        selected.append({"source": name, "path": str(target.relative_to(ROOT)), "sha256": sha(target)})
coverage = PRIVATE / "artifacts/coverage.json"
if coverage.is_file():
    shutil.copy2(coverage, OUT / "coverage-final.json")
result = {
    "archive": str(PRIVATE),
    "artifacts": rows,
    "selected_screenshots": selected,
    "tracked_historical_restored": sum(bool(r.get("historical_restored")) for r in rows),
    "new_run_artifacts_archived": sum(bool(r.get("new_run_artifact")) for r in rows),
    "limits": "Synthetic fake-runtime evidence; not real editing or physical-phone acceptance.",
}
(OUT / "browser-archive.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({k: v for k, v in result.items() if k != "artifacts"}, indent=2))
