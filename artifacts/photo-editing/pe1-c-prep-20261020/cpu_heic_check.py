"""Real CPU-only photo preparation against synthetic files. No model call."""

import asyncio
import hashlib
import json
import struct
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "server"))

from app.config import Settings
from app.main import create_app

OUT = Path(__file__).resolve().parent
PRIVATE = Path.home() / ".local/share/workbench/qa/photo-editing-pe1-c-prep-20261020"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def chunks(raw):
    result, offset = [], 8
    assert raw.startswith(b"\x89PNG\r\n\x1a\n")
    while offset < len(raw):
        length = struct.unpack(">I", raw[offset:offset + 4])[0]
        result.append(raw[offset + 4:offset + 8].decode("ascii"))
        offset += length + 12
    assert offset == len(raw)
    return result


async def main():
    data = PRIVATE / "cpu-data"
    if data.exists():
        raise ValueError("Preserve previous CPU evidence; choose another recorded attempt")
    app = create_app(Settings(data_dir=data, dev=True, image_home=None,
                              transcribe_home=None, legacy_db=PRIVATE / "missing.db"))
    rows = []
    async with app.router.lifespan_context(app), httpx.AsyncClient(
        transport=httpx.ASGITransport(app), base_url="http://localhost"
    ) as client:
        app.state.images.references.codec.home = PRIVATE / "codec-home"
        chat = (await client.post("/api/chats", json={})).json()["id"]
        for extension, advertised in [("heic", "renamed.png"), ("png", "synthetic.png")]:
            source = ROOT / f"server/tests/fixtures/images/fake-synthetic.{extension}"
            raw = source.read_bytes()
            response = await client.post(f"/api/chats/{chat}/image-references",
                                         files={"file": (advertised, raw, "image/png")})
            assert response.status_code == 201, response.text
            item = response.json()
            folder = app.state.images.references.path(item["id"])
            assert (folder / "original").read_bytes() == raw
            receipt = json.loads((folder / "reference.json").read_text())
            assert receipt["original_sha256"] == sha(raw)
            assert receipt["original_format"] == ("HEIF" if extension == "heic" else "PNG")
            preview = await client.get(f"/api/chats/{chat}/image-references/{item['id']}/preview")
            assert preview.status_code == 200 and preview.headers["cache-control"] == "no-store"
            raw_preview = preview.content
            assert sha(raw_preview) == receipt["sha256"]
            types = chunks(raw_preview)
            assert not {"eXIf", "tEXt", "iTXt", "zTXt"}.intersection(types)
            assert max(item["width"], item["height"]) <= 2048
            assert not (folder / "decoded.png").exists()
            assert not (folder / "decoded.json").exists()
            assert not app.state.images.references.codec.processes
            assert not app.state.images.references.uploads.processes
            rows.append({"fixture": str(source.relative_to(ROOT)), "original_preserved": True,
                         "actual_cpu_decode": True, "format": receipt["original_format"],
                         "original_bytes": len(raw), "preview_bytes": len(raw_preview),
                         "dimensions": [item["width"], item["height"]], "png_chunks": types,
                         "metadata_removed": True, "children_reaped": True,
                         "storage": json.loads((folder / "storage.json").read_text())})
        invalid = await client.post(f"/api/chats/{chat}/image-references",
                                    files={"file": ("synthetic.png", b"\x89PNG\r\n\x1a\ninvalid")})
        assert invalid.status_code == 422
        assert not list((data / "image-references").glob(".preparing-*"))
        assert not app.state.images.tasks
    result = {"passed": True, "model_calls": 0, "real_converter": "/usr/bin/sips",
              "real_codec": "pinned image interpreter / Pillow; native imports forbidden",
              "cases": rows, "invalid_decode_refused": True,
              "limits": "CPU/reference preparation only; no HEIC-to-generated-edit or GPU qualification"}
    (OUT / "cpu-heic.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"passed": True, "actual_cpu_cases": len(rows), "model_calls": 0}))


asyncio.run(main())
