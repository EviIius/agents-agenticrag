"""Actual CPU codecs and API; synthetic evidence only. No inference or downloads."""

import asyncio
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "server"))
from app.config import Settings
from app.main import create_app

OUT = Path(__file__).resolve().parent
ATTEMPT = "final" if "--final" in sys.argv else "initial"
PRIVATE = Path.home() / ".local/share/workbench/qa/heic-preparation-20261021" / ("candidate-cpu-" + ATTEMPT)


async def main():
    PRIVATE.mkdir(mode=0o700, parents=True, exist_ok=False)
    home = PRIVATE / "codec-home"
    home.mkdir(mode=0o700)
    installed = Path.home() / ".local/share/workbench/image-worker/product"
    shutil.copyfile(installed / ".python", home / ".python")
    for name in ("reference_codec.py", "reference_contract.py"):
        shutil.copyfile(ROOT / "image_worker/product" / name, home / name)
    app = create_app(Settings(data_dir=PRIVATE / "data", dev=True,
                              image_home=None, transcribe_home=None,
                              legacy_db=PRIVATE / "missing.db"))
    cases = []
    async with app.router.lifespan_context(app), httpx.AsyncClient(
        transport=httpx.ASGITransport(app), base_url="http://localhost"
    ) as client:
        app.state.images.references.codec.home = home
        png = (ROOT / "server/tests/fixtures/images/fake-synthetic.png").read_bytes()
        heic = (ROOT / "server/tests/fixtures/images/fake-synthetic.heic").read_bytes()
        for label, raw, fallback in [
            ("synthetic-png", png, False), ("synthetic-heic", heic, False),
            ("browser-heic", heic, True), ("browser-png", png, True),
        ]:
            cid = (await client.post("/api/chats", json={})).json()["id"]
            files = {"file": ("photo", raw)}
            data = {}
            if fallback:
                files["browser_preview"] = ("preview.png", png)
                data = {"original_width": "32", "original_height": "16"}
            response = await client.post(f"/api/chats/{cid}/image-references", files=files, data=data)
            assert response.status_code == 201, response.status_code
            ref = response.json()
            folder = app.state.images.references.path(ref["id"])
            assert (folder / "original").read_bytes() == raw
            descriptor = json.loads((folder / "reference.json").read_text())
            assert descriptor["original_sha256"] == hashlib.sha256(raw).hexdigest()
            assert descriptor["normalization"].startswith("browser-oriented" if fallback else "exif-transpose")
            assert ref["available"] and max(ref["width"], ref["height"]) <= 2048
            assert not list(folder.glob("decoded.*"))
            preview = await client.get(f"/api/chats/{cid}/image-references/{ref['id']}/preview")
            assert preview.status_code == 200 and preview.headers["cache-control"] == "no-store"
            assert hashlib.sha256(preview.content).hexdigest() == descriptor["sha256"]
            # The product worker validates/binds the exact same pixels before inference.
            process = await asyncio.create_subprocess_exec(
                (home / ".python").read_text().strip(), "-c",
                "import sys,json;sys.path.insert(0,sys.argv[1]);from reference_contract import validate_reference;"
                "from pathlib import Path;p=Path(sys.argv[2]);validate_reference(p,json.loads((p/'reference.json').read_text()))",
                str(home), str(folder), stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            assert await process.wait() == 0
            cases.append({"case": label, "ready": True, "original_preserved": True,
                          "actual_cpu_codec": True, "worker_contract_valid": True,
                          "dimensions": [ref["width"], ref["height"]]})
        cid = (await client.post("/api/chats", json={})).json()["id"]
        bad = await client.post(f"/api/chats/{cid}/image-references",
            files={"file": ("photo", heic), "browser_preview": ("preview.png", png[:24])},
            data={"original_width": "32", "original_height": "16"})
        assert bad.status_code == 422
        assert not list(app.state.images.references.folder.glob(".preparing-*"))
        assert not app.state.images.references.codec.processes
        assert not app.state.images.references.uploads.processes
        assert not app.state.images.tasks
    result = {"passed": True, "model_calls": 0, "cases": cases,
              "invalid_png_refused": True, "children_reaped": True,
              "limits": "Synthetic CPU normalization and worker input validation; no generation or phone claim"}
    (OUT / ("cpu-check-" + ATTEMPT + ".json")).write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


asyncio.run(main())
