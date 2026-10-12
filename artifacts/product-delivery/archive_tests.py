"""Retain fresh fake test evidence and restore historical committed bytes."""

import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
BASE = "90132558"
METRICS = (
    "first-token",
    "frames",
    "activity-latency",
    "performance",
    "overlay",
    "cold-handoff",
    "send",
    "sidebar",
    "upload-memory",
    "axe",
)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    browser = (OUT / "make-e2e-release.log").read_text()
    assert "485 passed" in browser and "3 skipped" in browser
    changed = subprocess.check_output(
        ["git", "diff", "--name-only", BASE, "--", "artifacts"], cwd=ROOT, text=True
    ).splitlines()
    prefix = str(OUT.relative_to(ROOT)) + "/"
    changed = [name for name in changed if not name.startswith(prefix)]
    # Validate all paths before copying/restoring any. Model/fixture inputs never qualify.
    for name in changed:
        path = Path(name)
        if name == "artifacts/coverage.json":
            continue
        assert re.match(
            r"artifacts/phase-(?:[0-7]|t)/|artifacts/images-i1/browser/|"
            r"artifacts/deferred-polish/|artifacts/reliability/context-budget/|"
            r"artifacts/reliability/evidence-v10/browser/",
            name,
        ), name
        assert (
            path.suffix == ".png"
            or (path.suffix == ".json" and path.name.startswith(tuple(v + "-" for v in METRICS)))
            or name
            in {
                "artifacts/phase-1/streaming-chromium-trace.json.gz",
                "artifacts/phase-1/streaming-webkit-trace.json.gz",
            }
        ), name
    untracked = subprocess.check_output(
        ["git", "ls-files", "--others", "--exclude-standard", "--", "artifacts/phase-2"],
        cwd=ROOT,
        text=True,
    ).splitlines()
    for name in untracked:
        assert re.fullmatch(
            r"artifacts/phase-2/review-settings-(?:about|appearance|connections|data|models|"
            r"shortcuts|transcription|web search)-(?:320|390|768|1440)-(?:dark|light)\.png",
            name,
        ), name
    retained = {}
    for name in changed + untracked:
        path = ROOT / name
        target = OUT / "regenerated-test-evidence" / Path(name).relative_to("artifacts")
        target.parent.mkdir(parents=True, exist_ok=True)
        assert not target.exists(), target
        target.write_bytes(path.read_bytes())
        record = {"fresh": str(target.relative_to(ROOT)), "fresh_sha256": sha(target)}
        if name in changed:
            original = subprocess.check_output(["git", "show", BASE + ":" + name], cwd=ROOT)
            record["restored_sha256"] = hashlib.sha256(original).hexdigest()
            path.write_bytes(original)
            assert sha(path) == record["restored_sha256"]
        else:
            record["source"] = "web/tests/ui-regressions.spec.ts fake settings screenshot loop"
            path.unlink()  # The archived identical bytes are retained, never real user captures.
        retained[name] = record
    (OUT / "regenerated-test-evidence.json").write_text(
        json.dumps(
            {
                "source": "Required full fake-runtime browser and coverage regression suites",
                "base": BASE,
                "files": retained,
                "restored_tracked_files": len(changed),
                "moved_new_fake_captures": len(untracked),
                "real_phone_or_document_inputs": False,
            },
            indent=2,
        )
        + "\n"
    )
    print(f"Retained {len(retained)} fresh outputs; restored {len(changed)} historical files")


if __name__ == "__main__":
    main()
