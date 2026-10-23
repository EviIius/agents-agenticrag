"""Download and cryptographically check the approved PE3 snapshot only."""

import argparse
import hashlib
import json
import os
import shutil
from pathlib import Path
from time import monotonic

HERE = Path(__file__).resolve().parent


def verify(path, item):
    if path.stat().st_size != item["bytes"]:
        raise ValueError("Checkpoint file size differs")
    digest = hashlib.sha256() if item["sha256"] else hashlib.sha1()
    if not item["sha256"]:
        digest.update(b"blob " + str(item["bytes"]).encode() + b"\0")
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024**2), b""):
            digest.update(block)
    if digest.hexdigest() != (item["sha256"] or item["git_blob_sha1"]):
        raise ValueError("Checkpoint content hash differs")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    spec = json.loads((HERE / "model-files.json").read_text())
    if not spec["authorized_to_download"] or args.receipt.exists():
        raise ValueError("Approval missing or receipt already exists")
    args.cache.mkdir(parents=True, exist_ok=True, mode=0o700)
    if shutil.disk_usage(args.cache).free < 50 * 1024**3:
        raise ValueError("Insufficient download headroom")
    os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
    from huggingface_hub import snapshot_download

    started = monotonic()
    print(
        json.dumps({"stage": "downloading", "bytes": spec["total_bytes"]}), flush=True
    )
    root = Path(
        snapshot_download(
            repo_id=spec["model"],
            revision=spec["revision"],
            cache_dir=args.cache,
            allow_patterns=[f["path"] for f in spec["files"]],
            max_workers=4,
        )
    )
    if root.name != spec["revision"]:
        raise ValueError("Unexpected model revision")
    if sorted(
        str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()
    ) != sorted(f["path"] for f in spec["files"]):
        raise ValueError("Unexpected downloaded file set")
    print(json.dumps({"stage": "verifying", "files": len(spec["files"])}), flush=True)
    for item in spec["files"]:
        verify(root / item["path"], item)
    receipt = {
        "model": spec["model"],
        "revision": spec["revision"],
        "bytes": spec["total_bytes"],
        "files_verified": len(spec["files"]),
        "elapsed_seconds": round(monotonic() - started, 3),
        "manifest_sha256": hashlib.sha256(
            (HERE / "model-files.json").read_bytes()
        ).hexdigest(),
        "snapshot": str(root),
        "packages_installed": 0,
    }
    with args.receipt.open("x") as stream:
        json.dump(receipt, stream, indent=2)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    print(json.dumps({k: v for k, v in receipt.items() if k != "snapshot"}), flush=True)


if __name__ == "__main__":
    main()
