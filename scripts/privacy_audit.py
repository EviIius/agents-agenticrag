"""Audit changed text and new evidence; synthetic capture discipline is still required."""

import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIO = {".wav", ".mp3", ".m4a", ".flac", ".aif", ".aiff", ".aac", ".amr", ".caf", ".mka", ".mov", ".mp4", ".oga", ".opus", ".ogg", ".wma"}
KEY = re.compile(r"\b(?:sk-[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{30,}|AKIA[A-Z0-9]{16})\b")


def main() -> None:
    changed = subprocess.check_output(
        ["git", "diff", "--name-only", "HEAD"], cwd=ROOT, text=True
    ).splitlines()
    untracked = subprocess.check_output(
        ["git", "ls-files", "--others", "--exclude-standard"], cwd=ROOT, text=True
    ).splitlines()
    paths = set(changed + untracked)
    paths.update(
        str(p.relative_to(ROOT)) for p in (ROOT / "artifacts/phase-4").rglob("*") if p.is_file()
    )
    marker_file = os.environ.get("WORKBENCH_PRIVACY_MARKERS_FILE")
    markers = Path(marker_file).read_text().splitlines() if marker_file else []
    failures = []
    for name in sorted(paths):
        path = ROOT / name
        if not path.is_file():
            continue
        if path.suffix.lower() in AUDIO:
            failures.append({"path": name, "reason": "audio must not be committed"})
        if (
            name.startswith("artifacts/phase-4/")
            and path.suffix.lower() in {".png", ".webm", ".jpg"}
            and not re.search(r"fake|synthetic", path.name)
        ):
            failures.append({"path": name, "reason": "evidence lacks synthetic filename"})
        if path.suffix.lower() in {
            ".md",
            ".py",
            ".ts",
            ".tsx",
            ".css",
            ".json",
            ".txt",
            ".sql",
            ".sh",
            ".toml",
        }:
            text = path.read_text(errors="replace")
            if KEY.search(text) or any(marker and marker in text for marker in markers):
                failures.append({"path": name, "reason": "secret or private marker"})
    print(
        json.dumps(
            {
                "scanned": len(paths),
                "failures": failures,
                "limits": "Changed files and Phase 4 evidence only; images require human review; optional local private-marker file.",
            },
            indent=2,
        )
    )
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
