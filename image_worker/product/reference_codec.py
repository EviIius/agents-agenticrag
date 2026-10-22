"""Bounded CPU preparation. Uses existing Pillow, never MLX or a model."""

import importlib.abc
import json
import os
import sys
import threading
from pathlib import Path


class NoNative(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split(".")[0] in {"mlx", "mflux", "torch", "transformers"}:
            raise RuntimeError("Native imports are forbidden in the image codec")


def audit(event, args):
    if event.startswith("socket.connect"):
        raise RuntimeError("Network is forbidden in the image codec")


def parent_watch():
    os.read(sys.stdin.fileno(), 1)
    os._exit(71)


def main():
    sys.meta_path.insert(0, NoNative())
    sys.addaudithook(audit)
    threading.Thread(target=parent_watch, daemon=True).start()
    from reference_contract import normalize

    folder = Path(sys.argv[1])
    if folder.is_symlink():
        raise ValueError("Invalid preparation directory")
    if sys.argv[2:] == ["--verify-composite"]:
        from masked_edit import verify_composite

        print(json.dumps(verify_composite(folder)), flush=True)
        return
    if sys.argv[2:]:
        raise ValueError("Unknown codec operation")
    if (folder / "decoded.json").exists():
        raw = (folder / "original").read_bytes()
        props = json.loads((folder / "decoded.json").read_text())
        browser = props.get("source") == "browser"
        heif = len(raw) >= 16 and raw[4:8] == b"ftyp"
        if not (heif or (browser and raw.startswith((b"\x89PNG\r\n\x1a\n", b"\xff\xd8\xff")))):
            raise ValueError("Decoded source is not HEIF")
    descriptor = normalize(folder)
    print(json.dumps(descriptor), flush=True)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # Do not echo filenames, paths, metadata or native errors.
        sys.exit(1)
