"""Preserve fresh fake-browser metrics/captures, then restore original evidence."""

import hashlib
import re
import subprocess
from pathlib import Path

import audit

ROOT, OUT = audit.ROOT, audit.OUT
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


def main():
    browser = (OUT / "make-e2e.log").read_text()
    assert "473 passed" in browser and "3 skipped" in browser
    changed = subprocess.check_output(
        ["git", "diff", "--name-only", "cb5a1a4b", "--", "artifacts"],
        cwd=ROOT,
        text=True,
    ).splitlines()
    # Validate the complete set before restoring any file. No eval cases/raw
    # pages, model outputs or unrelated tracked changes are admitted here.
    for name in changed:
        path = Path(name)
        if name == "artifacts/coverage.json":
            continue
        assert re.match(
            r"artifacts/phase-(?:[0-7]|t)/|artifacts/images-i1/browser/|artifacts/deferred-polish/|artifacts/reliability/context-budget/|artifacts/reliability/evidence-v10/browser/",
            name,
        ), name
        assert (
            path.suffix == ".png"
            or (
                path.suffix == ".json"
                and path.name.startswith(tuple(v + "-" for v in METRICS))
            )
            or name
            in {
                "artifacts/phase-1/streaming-chromium-trace.json.gz",
                "artifacts/phase-1/streaming-webkit-trace.json.gz",
            }
        ), name
    retained = {}
    for name in changed:
        path = ROOT / name
        original = subprocess.check_output(
            ["git", "show", "cb5a1a4b:" + name], cwd=ROOT
        )
        target = OUT / "regenerated-test-evidence" / Path(name).relative_to("artifacts")
        target.parent.mkdir(parents=True, exist_ok=True)
        assert not target.exists(), target
        target.write_bytes(path.read_bytes())
        retained[name] = {
            "fresh": str(target.relative_to(ROOT)),
            "fresh_sha256": audit.sha(target),
            "restored_sha256": hashlib.sha256(original).hexdigest(),
        }
        path.write_bytes(original)
        assert audit.sha(path) == retained[name]["restored_sha256"]
    audit.write(
        "regenerated-test-evidence.json",
        {
            "source": "Required full fake-runtime browser/coverage regression suites",
            "files": retained,
            "restored_files": len(retained),
            "originals_preserved": audit.preserve_prior(),
            "no_real_recording_document_or_phone_capture": True,
        },
    )
    print(
        f"Retained {len(retained)} fresh generated files; restored every original byte"
    )


if __name__ == "__main__":
    main()
