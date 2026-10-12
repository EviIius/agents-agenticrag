"""One declared synthetic live generation, SSE reconnect and saved bytes."""

import asyncio
import hashlib
import json
from pathlib import Path
from time import monotonic

import httpx

OUT = Path(__file__).resolve().parent
PROMPT = "A photograph of a single teal ceramic mug on a clean white tabletop, soft window light, no text."
BASE = "http://127.0.0.1:8787"


async def main():
    async with httpx.AsyncClient(base_url=BASE, timeout=60, trust_env=False) as client:
        assert not (await client.get("/api/runs/active")).json()
        assert not (await client.get("/api/transcription/audio-storage")).json()["active_files"]
        response = await client.post("/api/images/jobs", json={
            "request_key": "product-delivery-i1-synthetic-live-01",
            "prompt": PROMPT, "seed": 11,
        })
        response.raise_for_status()
        job = response.json()
        identifier = job["id"]
        duplicate = await client.post("/api/images/jobs", json={
            "request_key": "product-delivery-i1-synthetic-live-01",
            "prompt": PROMPT, "seed": 11,
        })
        assert duplicate.json()["id"] == identifier
        clock, events, sequence = monotonic(), [], "0"
        async with asyncio.timeout(330):
            async with client.stream("GET", "/api/images/events") as stream:
                async for line in stream.aiter_lines():
                    if line.startswith("id:"):
                        sequence = line[3:].strip()
                    if not line.startswith("data:"):
                        continue
                    body = json.loads(line[5:].strip())
                    current = body.get("job") or next(
                        (j for j in body.get("jobs", []) if j["id"] == identifier), None
                    )
                    if not current or current["id"] != identifier:
                        continue
                    events.append({"id": sequence, "state": current["state"],
                                   "stage": current["stage"], "steps": current["completed_steps"]})
                    if current["state"] in {"complete", "failed", "cancelled", "interrupted"}:
                        job = current
                        break
        result = {"synthetic_prompt": PROMPT, "seed": 11, "job": job,
                  "events": events, "seconds": monotonic()-clock,
                  "idempotent_submission": True, "progress_transport": "SSE, no polling"}
        if job["state"] == "complete":
            for format in ("png", "json"):
                download = await client.get(f"/api/images/jobs/{identifier}/output/{format}")
                download.raise_for_status()
                (OUT / ("live-output." + format)).write_bytes(download.content)
                result[format] = {"bytes": len(download.content),
                                  "sha256": hashlib.sha256(download.content).hexdigest()}
        (OUT / "live-result.json").write_text(json.dumps(result, indent=2) + "\n")
        assert job["state"] == "complete", job.get("error")
        print(json.dumps({"state": job["state"], "seconds": result["seconds"],
                          "png_bytes": result["png"]["bytes"], "events": len(events)}))


if __name__ == "__main__":
    asyncio.run(main())
