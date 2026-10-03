#!/usr/bin/env python3
"""Measure initial static-import JS only; lazy imports remain excluded."""

import gzip
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
static = root / "server/app/static"
manifest = json.loads((static / ".vite/manifest.json").read_text())
visited = set()


def visit(key: str) -> None:
    if key in visited:
        return
    visited.add(key)
    for child in manifest[key].get("imports", []):
        visit(child)


for key, item in manifest.items():
    if item.get("isEntry"):
        visit(key)
files = {manifest[key]["file"] for key in visited if manifest[key]["file"].endswith(".js")}
sizes = {name: len(gzip.compress((static / name).read_bytes(), mtime=0)) for name in sorted(files)}
result = {
    "method": "sum of gzip bytes of entry JS and recursive static imports; lazy imports excluded",
    "files": sizes,
    "gzip_bytes": sum(sizes.values()),
    "budget_bytes": 250 * 1024,
}
print(json.dumps(result, indent=2))
raise SystemExit(0 if result["gzip_bytes"] <= result["budget_bytes"] else 1)
