"""Retain the finished fake browser recordings outside Git with exact hashes."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
TARGET = Path.home() / ".local/share/workbench/qa/chat-images/ci-a/videos"


def main():
    assert "573 passed" in (OUT / "e2e-final.log").read_text()
    files = []
    for source_root, group in ((ROOT / "web/test-results", "final"), (OUT / "attempts", "attempts")):
        for source in sorted(source_root.rglob("*.webm")):
            target = TARGET / group / source.relative_to(source_root)
            assert not target.exists(), target
            target.parent.mkdir(parents=True, exist_ok=True)
            data = source.read_bytes()
            target.write_bytes(data)
            digest = hashlib.sha256(data).hexdigest()
            assert hashlib.sha256(target.read_bytes()).hexdigest() == digest
            files.append({"path": str(target), "bytes": len(data), "sha256": digest})
            source.unlink()
    result = {"synthetic_only": True, "in_git": False, "files": files,
              "count": len(files), "total_bytes": sum(f["bytes"] for f in files),
              "limits": "Available synthetic recordings from the complete run are retained; earlier attempts have separate manifests."}
    (OUT / "motion-videos-outside-git.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "files"}, indent=2))


if __name__ == "__main__":
    main()
