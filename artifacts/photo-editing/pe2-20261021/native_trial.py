"""Sanitized trial template. Exact executed controller and private task remain private.

Two native jobs were executed; this template is not an additional allowance.
"""

import asyncio
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from time import monotonic

import httpx

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE = Path.home() / ".local/share/workbench"
PRIVATE = BASE / "qa/photo-editing-pe2-20261021"
sys.path[:0] = [str(ROOT / "server"), str(ROOT / "scripts")]
from app.capacity import Capacity
from app.images.codec import ReferenceCodec
from app.images.engine import Engine
from app.images.files import atomic_json, sanitize_export, validate
from app.images.storage import StorageMeter
from install_image_worker import FILES
from prepare_photo_release import inventory


def retained():
    return {
        "server": inventory(BASE / "app/server/app"),
        "worker": inventory(BASE / "image-worker/product"),
        "service": hashlib.sha256((Path.home() / "Library/LaunchAgents/dev.agenticrag.workbench.plist").read_bytes()).hexdigest(),
    }


async def main():
    source = Path(os.environ["AETHER_PRIVATE_REFERENCE"])
    if PRIVATE.exists():
        raise ValueError("Preserve the previous trial; no retry is permitted")
    before = retained()
    PRIVATE.mkdir(mode=0o700, parents=True)
    home = PRIVATE / "worker"
    home.mkdir(mode=0o700)
    for name in FILES:
        shutil.copyfile(ROOT / "image_worker/product" / name, home / name)
    for name in (".python", "config.json"):
        shutil.copyfile(BASE / "image-worker/product" / name, home / name)
    python = (home / ".python").read_text().strip()
    frozen = {name: hashlib.sha256((home / name).read_bytes()).hexdigest() for name in FILES}
    atomic_json(OUT / "native-source.json", {"worker_files": frozen, "maximum_jobs": 2,
        "parameters": {"width": 1024, "height": 1024, "steps": 4, "seed": 42, "guidance": 1.0},
        "private_media": "All private inputs, masks, prompts and results remain outside Git"})
    cases = []
    codec = ReferenceCodec(home)
    for label in ("synthetic", "private"):
        job = PRIVATE / label
        inputs = job / "inputs"
        inputs.mkdir(mode=0o700, parents=True)
        if label == "synthetic":
            code = "from PIL import Image,ImageDraw;import sys;im=Image.new('RGB',(768,1024),'lightgrey');d=ImageDraw.Draw(im);d.rectangle((240,300,520,650),fill='blue');im.save(sys.argv[1],format='PNG')"
            subprocess.run([python, "-c", code, str(inputs / "original")], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            selection = {"version": 1, "strokes": [{"radius": 0.15, "points": [[0.5, 0.45]]}]}
            prompt = "Change the blue shape to yellow. Keep the rest of the picture unchanged."
        else:
            shutil.copyfile(source, inputs / "original")
            private_task = json.loads(Path(os.environ["AETHER_PRIVATE_EDIT"]).read_text())
            selection = private_task["selection"]
            prompt = private_task["prompt"]
        (inputs / "original").chmod(0o600)
        reference = await codec.normalize(inputs)
        request = {"mode": "edit", "prompt": prompt, "seed": 42, "reference": reference, "selection": selection}
        atomic_json(job / "input.json", request)
        cases.append((label, job, request))
    capacity = Capacity(BASE / "data/native.lock")
    engine = Engine(home, capacity)
    results = []
    ledger = PRIVATE / "launches.jsonl"
    async with httpx.AsyncClient(trust_env=False, timeout=5) as client:
        assert (await client.get("http://127.0.0.1:8787/api/runs/active")).json() == []
    try:
        for label, job, request in cases:
            assert all(hashlib.sha256((home / n).read_bytes()).hexdigest() == h for n, h in frozen.items())
            events = []
            meter = StorageMeter(job)
            stop = asyncio.Event()
            health = []
            async def observe():
                async with httpx.AsyncClient(trust_env=False, timeout=2) as client:
                    while not stop.is_set():
                        meter.sample()
                        started = monotonic()
                        response = await client.get("http://127.0.0.1:8787/api/health")
                        response.raise_for_status()
                        assert response.json()["ok"]
                        health.append(monotonic() - started)
                        try: await asyncio.wait_for(stop.wait(), .25)
                        except TimeoutError: pass
            async def progress(event):
                events.append(event)
            async with capacity.lease(background=True):
                await engine.admit_edit()
                assert len(ledger.read_text().splitlines()) < 2 if ledger.exists() else True
                working = job / "working"
                working.mkdir(mode=0o700)
                before_swap = await engine.swap()
                monitor = asyncio.create_task(observe())
                try:
                    with ledger.open("a") as file:
                        file.write(json.dumps({"case": label, "invocation": len(results) + 1}) + "\n")
                        file.flush(); os.fsync(file.fileno())
                    started = monotonic()
                    exit_code = await engine.run_edit(job / "input.json", working, progress)
                    assert exit_code == 0
                    proof = await codec.verify_composite(job)
                    assert proof["outside_changed_pixels"] == 0 and proof["changed_pixels"] > 0
                    validate(working, request)
                    export_sha, export_bytes = sanitize_export(working)
                    metadata = json.loads((working / "metadata.json").read_text())
                    after_swap = await engine.swap()
                    assert after_swap - before_swap <= 512
                    assert max(health) <= 2
                    assert [e["completed_steps"] for e in events if e["type"] == "denoising"] == [0, 1, 2, 3, 4]
                    result = {"case": label, "completed": True, "seconds": round(monotonic() - started, 3),
                        "dimensions": [metadata["width"], metadata["height"]], "mlx_peak_bytes": metadata["mlx_peak_bytes"],
                        "swap_growth_mib": after_swap - before_swap, "maximum_health_seconds": max(health),
                        "health_samples": len(health), "protected_pixels": proof["protected_pixels"],
                        "outside_changed_pixels": 0, "changed_pixels": proof["changed_pixels"],
                        "native_bytes": metadata["native_bytes"], "composite_bytes": (working / "image.png").stat().st_size,
                        "export_bytes": export_bytes, "storage": meter.report(), "native_calls": 1}
                    results.append(result)
                    if label == "synthetic":
                        destination = OUT / "synthetic"
                        destination.mkdir()
                        for name in ("image.png", "native.png", "export.png", "metadata.json"):
                            shutil.copyfile(working / name, destination / name)
                        shutil.copyfile(job / "inputs/reference.png", destination / "reference.png")
                    atomic_json(PRIVATE / (label + "-result.json"), {**result, "events": events, "export_sha256": export_sha})
                    print(json.dumps({k: v for k, v in result.items() if k != "storage"}), flush=True)
                finally:
                    stop.set()
                    await monitor
            assert retained() == before
        atomic_json(OUT / "native-result.json", {"passed": True, "cases": results, "native_calls": len(results),
            "production_unchanged": retained() == before, "quality": "Pending visual review; structural preservation is not content quality"})
    finally:
        await codec.close()
        assert retained() == before
        atomic_json(PRIVATE / "summary.json", {"completed_cases": len(results), "launches": len(ledger.read_text().splitlines()) if ledger.exists() else 0,
                                               "production_unchanged": retained() == before})


asyncio.run(main())
