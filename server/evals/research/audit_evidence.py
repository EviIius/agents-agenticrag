"""Audit compressed public fixtures and native streams as well as text evidence."""

import gzip
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "artifacts/phase-8/gate"
KEY = re.compile(r"\b(?:sk-[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{30,}|AKIA[A-Z0-9]{16})\b")
MEDIA = {".wav", ".m4a", ".mp3", ".flac", ".aiff", ".caf", ".mp4", ".mov"}


def main() -> None:
    failures = []
    compressed, streams, files = 0, 0, 0
    for path in sorted(OUT.rglob("*")):
        if not path.is_file():
            continue
        files += 1
        if path.suffix in MEDIA:
            failures.append({"path": str(path.relative_to(ROOT)), "reason": "media"})
        data = path.read_bytes()
        if path.suffix == ".gz":
            data = gzip.decompress(data)
            compressed += 1
        if path.suffix == ".ndjson":
            streams += 1
            for line in data.decode().splitlines():
                json.loads(line)
        if KEY.search(data.decode(errors="replace")):
            failures.append({"path": str(path.relative_to(ROOT)), "reason": "key-shaped text"})
    frozen = json.loads((OUT / "frozen-inputs.json").read_text())
    mismatches = [
        filename
        for filename, digest in frozen["files"].items()
        if hashlib.sha256((ROOT / filename).read_bytes()).hexdigest() != digest
    ]
    pages = json.loads((OUT / "web-fixtures/pages-manifest.json").read_text())
    for page in pages:
        data = gzip.decompress((OUT / "web-fixtures" / page["file"]).read_bytes())
        assert hashlib.sha256(data).hexdigest() == page["sha256"]
    assert streams == 240
    result = {
        "files": files,
        "compressed_public_pages_checked": compressed,
        "native_streams_checked": streams,
        "recorded_search_pages_verified": len(pages),
        "failures": failures,
        "frozen_input_source_mismatches": mismatches,
        "discipline": (
            "Only authored synthetic prompts and public web pages were read. "
            "No real recordings, Library files or private phone screenshots were accessed."
        ),
        "limits": (
            "A scanner cannot prove public-page provenance or semantic privacy; "
            "URL manifests and the collection boundary provide that evidence. "
            "No private-marker corpus was read."
        ),
    }
    (OUT / "gate-evidence-audit.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    if failures or mismatches:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
