"""Synthetic pixels and normalization only; no native package or network allowed."""

import importlib.abc
import json
import sys
from pathlib import Path


class NoNative(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split(".")[0] in {"mlx", "mflux", "torch", "transformers"}:
            raise RuntimeError("Native package forbidden in CPU preparation")


sys.meta_path.insert(0, NoNative())


def audit(event, args):
    if event.startswith("socket.connect"):
        raise RuntimeError("Network forbidden in CPU preparation")


sys.addaudithook(audit)
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from contracts import normalize  # noqa: E402
from PIL import Image  # noqa: E402

root = Path(sys.argv[1])
kind = sys.argv[2]
if kind != "normalize-existing":
    (root / "inputs").mkdir()
    image = Image.new("RGB", (3200, 1600) if kind == "large" else (1024, 768), "red")
    if kind == "oriented":
        exif = Image.Exif()
        exif[274] = 6
        exif[270] = "synthetic metadata to remove"
        image.save(root / "inputs/original", format="JPEG", exif=exif)
    else:
        image.save(root / "inputs/original", format="PNG")
try:
    print(json.dumps(normalize(root)))
except Exception:
    print(json.dumps({"error": "invalid synthetic reference"}))
    sys.exit(1)
