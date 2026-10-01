"""Capture real runtime payloads before writing adapters. Never substitute fake responses."""

import argparse
import asyncio
import base64
import json
import struct
import zlib
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from time import perf_counter

import httpx

OUTPUT = Path(__file__).resolve().parents[1] / "server/tests/fixtures/providers"


# A checksum-valid synthetic PNG; no user images are used in fixtures.
def png_chunk(kind, data):
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))


PNG = base64.b64encode(
    b"\x89PNG\r\n\x1a\n"
    + png_chunk(b"IHDR", struct.pack(">IIBBBBB", 32, 32, 8, 2, 0, 0, 0))
    + png_chunk(b"IDAT", zlib.compress((b"\x00" + b"\xff\x00\x00" * 32) * 32))
    + png_chunk(b"IEND", b"")
).decode()


async def record(client, name, method, url, body=None):
    request = {"method": method, "url": url, "body": body}
    started = datetime.now(UTC).isoformat()
    clock = perf_counter()
    first_byte = None
    async with client.stream(method, url, json=body) as response:
        raw = bytearray()
        async for chunk in response.aiter_bytes():
            if first_byte is None:
                first_byte = (perf_counter() - clock) * 1000
            raw.extend(chunk)
        suffix = "ndjson" if "/api/chat" in url else "sse" if "/chat/completions" in url else "json"
        (OUTPUT / f"{name}.{suffix}").write_bytes(raw)
        metadata = {
            "recorded_at": started,
            "request": request,
            "status": response.status_code,
            "content_type": response.headers.get("content-type"),
            "raw": f"{name}.{suffix}",
            "sha256": sha256(raw).hexdigest(),
            "first_byte_ms": first_byte,
            "total_ms": (perf_counter() - clock) * 1000,
        }
        (OUTPUT / f"{name}.request.json").write_text(json.dumps(metadata, indent=2) + "\n")
        print(f"{name}: HTTP {response.status_code}, {len(raw)} bytes", flush=True)
        return json.loads(raw) if suffix == "json" else None


async def main(only):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    timeout = httpx.Timeout(connect=5, read=300, write=30, pool=5)
    async with httpx.AsyncClient(timeout=timeout, trust_env=False) as client:
        if only in ("all", "ollama", "vision"):
            base = "http://127.0.0.1:11434"
            tags = await record(client, "ollama-tags", "GET", base + "/api/tags")
            await record(client, "ollama-ps-before", "GET", base + "/api/ps")
            shows = {}
            for i, model in enumerate(tags["models"]):
                shows[model["name"]] = await record(
                    client, f"ollama-show-{i}", "POST", base + "/api/show", {"model": model["name"]}
                )
            plain = "qwen3:30b-a3b-instruct-2507-q4_K_M"
            reasoning = "gpt-oss:20b"
            vision = "gemma4:12b-mlx"
            cases = [
                ("plain", plain, "Reply with a brief greeting.", {}, None),
                ("reasoning", reasoning, "What is 17 times 19? Explain briefly.", {}, None),
                ("vision", vision, "Describe the image briefly.", {}, PNG),
                (
                    "length",
                    plain,
                    "Count upwards from one, continuing until stopped.",
                    {"num_predict": 20},
                    None,
                ),
                ("unknown", "workbench-fixture-unknown-model", "Hello.", {}, None),
            ]
            for label, model, prompt, params, image in cases:
                if only == "vision" and label != "vision":
                    continue
                message = {"role": "user", "content": prompt}
                if image:
                    message["images"] = [image]
                body = {"model": model, "messages": [message], "stream": True, "keep_alive": "30m"}
                if params:
                    body["options"] = params
                await record(client, "ollama-" + label, "POST", base + "/api/chat", body)
                await record(client, "ollama-ps-" + label, "GET", base + "/api/ps")
                if label != "unknown":
                    await record(
                        client,
                        "ollama-unload-" + label,
                        "POST",
                        base + "/api/chat",
                        {"model": model, "messages": [], "keep_alive": 0},
                    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", choices=["all", "ollama", "vision"], default="all")
    asyncio.run(main(parser.parse_args().only))
