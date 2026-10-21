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
    if (folder / "decoded.json").exists():
        raw = (folder / "original").read_bytes()
        if len(raw) < 16 or raw[4:8] != b"ftyp":
            raise ValueError("Decoded source is not HEIF")
    descriptor = normalize(folder)
    print(json.dumps(descriptor), flush=True)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # Do not echo filenames, paths, metadata or native errors.
        sys.exit(1)
