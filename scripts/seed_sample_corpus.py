"""Publish the original example documents to a running local workbench."""

from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path
from urllib.request import Request, urlopen


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8787")
    parser.add_argument("--collection", default="research")
    parser.add_argument("--scope", default="private")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1] / "examples" / "sample-corpus"
    for path in sorted(root.glob("*.md")):
        payload = json.dumps({
            "filename": path.name,
            "content_base64": base64.b64encode(path.read_bytes()).decode("ascii"),
            "collection": args.collection,
            "scopes": [args.scope],
            "ocr": "never",
        }).encode("utf-8")
        request = Request(
            args.url.rstrip("/") + "/api/v1/ingest",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urlopen(request, timeout=180) as response:
            result = json.load(response)
        print(f"{path.name}: {result['status']} ({result['id']})")


if __name__ == "__main__":
    main()
