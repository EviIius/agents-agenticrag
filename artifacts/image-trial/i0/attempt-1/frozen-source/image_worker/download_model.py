"""Download only the approved model's pinned inference files, outside Git."""

import argparse
import hashlib
import json
import time
from pathlib import Path


def main() -> None:
    from huggingface_hub import snapshot_download

    parser = argparse.ArgumentParser()
    parser.add_argument("--cache", required=True, type=Path)
    parser.add_argument("--receipt", required=True, type=Path)
    args = parser.parse_args()
    spec = json.loads(Path(__file__).with_name("trial.json").read_text())
    started = time.monotonic()
    snapshot = Path(
        snapshot_download(
            repo_id=spec["model"],
            revision=spec["revision"],
            cache_dir=args.cache,
            allow_patterns=[
                "vae/*.safetensors",
                "vae/*.json",
                "transformer/*.safetensors",
                "transformer/*.json",
                "text_encoder/*.safetensors",
                "text_encoder/*.json",
                "tokenizer/*",
                "LICENSE.md",
                "model_index.json",
            ],
        )
    )
    assert snapshot.name == spec["revision"], "Unexpected model revision"
    files = {}
    for path in sorted(snapshot.rglob("*")):
        if path.is_file():
            digest = hashlib.sha256()
            with path.open("rb") as stream:
                for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
                    digest.update(chunk)
            files[str(path.relative_to(snapshot))] = {
                "bytes": path.stat().st_size,
                "sha256": digest.hexdigest(),
            }
    receipt = {
        "model": spec["model"],
        "revision": spec["revision"],
        "snapshot": str(snapshot),
        "elapsed_seconds": time.monotonic() - started,
        "files": files,
        "downloaded_snapshot_bytes": sum(item["bytes"] for item in files.values()),
        "duplicate_root_checkpoint_downloaded": False,
    }
    args.receipt.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({key: value for key, value in receipt.items() if key != "files"}))


if __name__ == "__main__":
    main()
