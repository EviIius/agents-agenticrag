"""Record authoritative public reference pages before evaluating any answers."""

import asyncio
import gzip
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import httpx

SERVER = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SERVER))
from app.search.extract import extract  # noqa: E402
from app.search.fetch import RawPage  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = SERVER.parent / "artifacts/phase-8/gate/references"


async def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    cases = json.loads((HERE / "cases.yaml").read_text())
    manifest = []
    async with httpx.AsyncClient(timeout=45, follow_redirects=True) as client:
        for case in cases:
            for reference in case["research"]["references"]:
                url = reference["url"]
                key = hashlib.sha256(url.encode()).hexdigest()
                raw_file = OUT / (key + ".html.gz")
                try:
                    response = await client.get(url)
                    response.raise_for_status()
                    raw = RawPage(
                        str(response.url),
                        response.content,
                        response.headers.get("content-type", "text/html"),
                    )
                    raw_file.write_bytes(gzip.compress(raw.data, mtime=0))
                    page = extract(raw)
                    (OUT / (key + ".txt")).write_text(page.text)
                    manifest.append(
                        {
                            "case": case["id"],
                            "requested_url": url,
                            "url": raw.url,
                            "content_type": raw.content_type,
                            "sha256": hashlib.sha256(raw.data).hexdigest(),
                            "recorded_at": datetime.now(UTC).isoformat(),
                            "file": raw_file.name,
                            "title": page.title,
                            "text_characters": len(page.text),
                            "error": None,
                        }
                    )
                    print(case["id"], response.status_code, len(page.text), flush=True)
                except httpx.HTTPError as exc:
                    manifest.append(
                        {"case": case["id"], "requested_url": url, "error": type(exc).__name__}
                    )
                    print(case["id"], "ERROR", type(exc).__name__, flush=True)
                (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    asyncio.run(main())
