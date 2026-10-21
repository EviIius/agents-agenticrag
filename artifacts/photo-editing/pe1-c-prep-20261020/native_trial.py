"""Prepared PE1-C controller. Default/offline uses CPU codec + fake inference only.

--native requires a separately written matching approval receipt; none is supplied
by this preparation. Four ordered image launches maximum, one empty-message load,
no retry/continuation after failure. Live data is never opened for modification.
"""

import argparse
import asyncio
import hashlib
import json
import os
import shutil
import struct
import sys
import time
from pathlib import Path
from uuid import uuid4

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
BASE = Path.home() / ".local/share/workbench"
PRIVATE = BASE / "qa/photo-editing-pe1-c-prep-20261020"
sys.path[:0] = [str(ROOT / "server"), str(OUT)]
import httpx
from app.capacity import Capacity
from app.config import Settings
from app.main import create_app
from app.images.engine import EDIT_DIGEST
from app.images.storage import StorageMeter
from native_candidate import CandidateEngine

CASES = [
    {
        "id": "empty-heic",
        "fixture": "large-synthetic.heic",
        "seed": 420101,
        "resident": False,
    },
    {
        "id": "resident-jpeg",
        "fixture": "oriented-synthetic.jpeg",
        "seed": 420102,
        "resident": True,
    },
    {
        "id": "cancel",
        "fixture": "oriented-synthetic.jpeg",
        "seed": 420103,
        "resident": True,
        "cancel": True,
    },
    {
        "id": "recovery-heic",
        "fixture": "large-synthetic.heic",
        "seed": 420104,
        "resident": True,
    },
]
PROMPT = "Change the shirt to vivid green. Preserve the person, pose and background as closely as possible."
PROFILE = "qwen3.8:27b-atelier-eval-32k"
PRELOAD = {
    "model": PROFILE,
    "messages": [],
    "stream": False,
    "keep_alive": "15m",
    "options": {"num_ctx": 32768},
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exclusive(path, value):
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    with path.open("x") as file:
        os.chmod(path, 0o600)
        json.dump(value, file, indent=2)
        file.write("\n")
        file.flush()
        os.fsync(file.fileno())


class Budget:
    def __init__(self, folder):
        self.folder = folder
        self.path = folder / "launches.jsonl"
        self.halt = folder / "HALTED"

    def rows(self):
        return (
            [json.loads(line) for line in self.path.read_text().splitlines()]
            if self.path.exists()
            else []
        )

    def reserve(self, kind, case):
        if self.halt.exists():
            raise ValueError("Prior failure; no continuation authorized")
        rows = self.rows()
        images = [r for r in rows if r["kind"] == "image"]
        if kind == "image":
            if len(images) >= 4 or case != CASES[len(images)]["id"]:
                raise ValueError("Image order/budget exhausted")
        elif kind == "preload":
            if any(r["kind"] == "preload" for r in rows) or [
                r["case"] for r in images
            ] != ["empty-heic"]:
                raise ValueError("Preload order/budget exhausted")
        else:
            raise ValueError("Unknown native request forbidden")
        row = {"kind": kind, "case": case, "reserved_before_request": True}
        with self.path.open("a") as file:
            os.chmod(self.path, 0o600)
            file.write(json.dumps(row) + "\n")
            file.flush()
            os.fsync(file.fileno())
        return row


def check_approval(path):
    receipt = json.loads(path.read_text())
    if receipt != {
        "scope": "PE1-C",
        "maximum_images": 4,
        "maximum_preloads": 1,
        "frozen_manifest_sha256": sha(OUT / "native-execution-manifest.json"),
    }:
        raise ValueError("Missing or mismatched separately reviewed approval")
    verify_frozen()


def verify_frozen():
    frozen = json.loads((OUT / "native-execution-manifest.json").read_text())
    for name, digest in frozen["files"].items():
        if sha(ROOT / name) != digest:
            raise ValueError("Frozen candidate changed")
    for name, digest in frozen["installed_worker_selectors"].items():
        if sha(BASE / "image-worker/product" / name) != digest:
            raise ValueError("Installed selector changed")


def critical_png(raw):
    assert raw[:8] == b"\x89PNG\r\n\x1a\n"
    chunks = []
    offset = 8
    while offset < len(raw):
        size = struct.unpack(">I", raw[offset : offset + 4])[0]
        end = offset + size + 12
        assert end <= len(raw)
        chunks.append((raw[offset + 4 : offset + 8].decode(), raw[offset:end]))
        offset = end
    assert offset == len(raw)
    return chunks


async def runtime_preflight(engine, resident):
    engine.expected_resident = resident
    async with httpx.AsyncClient(timeout=5, trust_env=False) as client:
        version = await client.get("http://127.0.0.1:11434/api/version")
        version.raise_for_status()
        assert version.json() == {"version": "0.35.0"}
        active = await client.get("http://127.0.0.1:8787/api/runs/active")
        active.raise_for_status()
        assert active.json() == [], "Human chat is active; stop without unloading"
    await engine.healthy()
    models = await engine.loaded()
    assert CandidateEngine.qualified_edit(models)
    assert bool(models) == resident, "Wrong residency; no automatic eject or refresh"
    return [
        {
            "digest": r["digest"],
            "context_length": r["context_length"],
            "resident_bytes": r["size_vram"],
        }
        for r in models
    ]


class Measured(CandidateEngine):
    def __init__(self, home, capacity):
        # No store: the trial never performs embedding unloads or extra /show calls.
        super().__init__(home, capacity, None)
        self.events = []
        self.residency = []
        self.swaps = []
        self.reaps = []
        self.health = []
        self.started = time.monotonic()
        self.cancel_at_step = asyncio.Event()
        self.case = None
        self.expected_resident = None

    async def loaded(self):
        rows = await super().loaded()
        self.residency.append(
            {
                "seconds": time.monotonic() - self.started,
                "models": [
                    {
                        "digest": r.get("digest"),
                        "context_length": r.get("context_length"),
                        "resident_bytes": r.get("size_vram"),
                    }
                    for r in rows
                ],
            }
        )
        if self.expected_resident is not None:
            assert bool(rows) == self.expected_resident, (
                "Residency changed during the case"
            )
        return rows

    async def healthy(self):
        start = time.monotonic()
        await super().healthy()
        self.health.append(time.monotonic() - start)

    async def swap(self):
        value = await super().swap()
        self.swaps.append(value)
        return value

    async def run_edit(self, manifest, scratch, progress):
        async def observe(event):
            self.events.append(event)
            await progress(event)
            if event.get("type") == "denoising" and event.get("completed_steps") == 1:
                self.cancel_at_step.set()

        return await super().run_edit(manifest, scratch, observe)

    async def stop(self, child):
        await super().stop(child)
        try:
            os.kill(child.pid, 0)
            absent = False
        except ProcessLookupError:
            absent = True
        self.reaps.append(
            {
                "reaped": child.returncode is not None,
                "process_absent": absent,
                "lease_held": self.capacity.busy,
            }
        )
        assert absent and child.returncode is not None and self.capacity.busy


async def execute(native, receipt):
    if native:
        check_approval(receipt)
    folder = PRIVATE / ("native" if native else "offline-controller")
    if folder.exists():
        raise ValueError("Retain prior run; no automatic retry")
    folder.mkdir(mode=0o700)
    data = folder / "data"
    home = folder / "worker"
    home.mkdir(mode=0o700)
    selectors = BASE / "image-worker/product"
    for name in [
        "worker.py",
        "edit_worker.py",
        "reference_contract.py",
        "reference_codec.py",
    ]:
        shutil.copy2(ROOT / "image_worker/product" / name, home / name)
    for name in [".python", "config.json"]:
        shutil.copy2(selectors / name, home / name)
    manifest = json.loads((OUT / "fixture-manifest.json").read_text())
    for name, entry in manifest["files"].items():
        assert sha(PRIVATE / "fixtures" / name) == entry["sha256"]
    budget = Budget(folder)
    capacity = Capacity(
        BASE / "data/native.lock" if native else folder / "offline-native.lock"
    )
    engine = Measured(home, capacity)
    if not native:
        from tests.test_photo_references import EditFake

        fake = EditFake()
        fake.case = None
        fake.events = []
        fake.cancel_at_step = asyncio.Event()
        real_fake = fake.run_edit

        async def fake_edit(manifest, scratch, progress):
            fake.cancel_at_step.clear()
            if fake.case.get("cancel"):
                fake.release.clear()
            else:
                fake.release.set()

            async def observe(event):
                fake.events.append(event)
                await progress(event)
                fake.cancel_at_step.set()

            return await real_fake(manifest, scratch, observe)

        fake.run_edit = fake_edit
        engine = fake
    original_spawn = asyncio.create_subprocess_exec
    current = {"case": None}

    async def spawning(*args, **kwargs):
        worker = len(args) > 1 and str(args[1]) == str(home / "edit_worker.py")
        if any(str(a) == str(home / "worker.py") for a in args):
            raise ValueError("Plain generation forbidden")
        if worker:
            if not native:
                raise ValueError("Offline native worker forbidden")
            verify_frozen()
            budget.reserve("image", current["case"]["id"])
        return await original_spawn(*args, **kwargs)

    asyncio.create_subprocess_exec = spawning
    # Block unintended controller HTTP calls. ASGI operations are in process.
    original_send = httpx.AsyncClient.send

    async def send(client, request, *args, **kwargs):
        if isinstance(client._transport, httpx.ASGITransport):
            return await original_send(client, request, *args, **kwargs)
        allowed = {
            ("GET", 11434, "/api/version"),
            ("GET", 11434, "/api/ps"),
            ("GET", 11434, "/api/tags"),
            ("POST", 11434, "/api/show"),
            ("GET", 8787, "/api/health"),
            ("GET", 8787, "/api/runs/active"),
        }
        key = (request.method, request.url.port, request.url.path)
        if not native or request.url.host != "127.0.0.1":
            raise ValueError("Unapproved network request")
        if key == ("POST", 11434, "/api/chat"):
            if json.loads(request.content) != PRELOAD:
                raise ValueError("Only approved empty-message preload allowed")
            budget.reserve("preload", "resident-setup")
        elif key not in allowed:
            raise ValueError("Unapproved HTTP request")
        return await original_send(client, request, *args, **kwargs)

    httpx.AsyncClient.send = send
    results = []
    meter = None
    sampler = None
    try:
        app = create_app(
            Settings(
                data_dir=data,
                dev=False,
                image_home=home,
                transcribe_home=None,
                legacy_db=folder / "missing.db",
                allowed_hosts="",
            )
        )
        async with (
            asyncio.timeout(720),
            app.router.lifespan_context(app),
            httpx.AsyncClient(
                transport=httpx.ASGITransport(app), base_url="http://localhost"
            ) as client,
        ):
            app.state.images.capacity = capacity
            app.state.images.engine = engine
            meter = StorageMeter(data)
            meter.sample()

            async def sample():
                while True:
                    await asyncio.sleep(0.25)
                    meter.sample()

            sampler = asyncio.create_task(sample())
            for index, case in enumerate(CASES):
                current["case"] = case
                engine.case = case
                engine.cancel_at_step.clear()
                if native and index == 1:
                    # Exactly one approved preload, under the same cross-process lease.
                    async with capacity.lease():
                        await runtime_preflight(engine, False)
                        async with httpx.AsyncClient(
                            timeout=180, trust_env=False
                        ) as ollama:
                            tags = await ollama.get("http://127.0.0.1:11434/api/tags")
                            tags.raise_for_status()
                            assert any(
                                r.get("name") == PROFILE
                                and r.get("digest") == EDIT_DIGEST
                                for r in tags.json()["models"]
                            )
                            show = await ollama.post(
                                "http://127.0.0.1:11434/api/show",
                                json={"model": PROFILE},
                            )
                            show.raise_for_status()
                            assert (
                                "num_ctx" in show.json().get("parameters", "")
                                and "32768" in show.json()["parameters"]
                            )
                            response = await ollama.post(
                                "http://127.0.0.1:11434/api/chat", json=PRELOAD
                            )
                            response.raise_for_status()
                            assert response.json().get("done") is True
                            assert response.json().get("done_reason") == "load"
                            assert (
                                response.json().get("message", {}).get("content", "")
                                == ""
                            )
                before = (
                    await runtime_preflight(engine, case["resident"]) if native else []
                )
                if not native:
                    budget.reserve("image", case["id"])
                chat = await client.post("/api/chats", json={})
                assert chat.status_code == 201, chat.text
                cid = chat.json()["id"]
                raw = (PRIVATE / "fixtures" / case["fixture"]).read_bytes()
                upload = await client.post(
                    f"/api/chats/{cid}/image-references",
                    files={
                        "file": ("synthetic-upload", raw, "application/octet-stream")
                    },
                )
                assert upload.status_code == 201, upload.text
                ref = upload.json()
                ref_folder = app.state.images.references.path(ref["id"])
                assert (ref_folder / "original").read_bytes() == raw
                descriptor = json.loads((ref_folder / "reference.json").read_text())
                expected = manifest["expected"][case["fixture"]]
                assert (
                    descriptor["original_dimensions"] == expected["original_dimensions"]
                )
                assert descriptor["dimensions"] == expected["working_dimensions"]
                if "exif_orientation" in expected:
                    assert (
                        descriptor["exif_orientation"] == expected["exif_orientation"]
                    )
                assert not {"eXIf", "tEXt", "iTXt", "zTXt"}.intersection(
                    t
                    for t, _ in critical_png(
                        (ref_folder / "reference.png").read_bytes()
                    )
                )
                meter.sample()
                response = await client.post(
                    f"/api/chats/{cid}/images",
                    json={
                        "request_key": uuid4().hex,
                        "prompt": PROMPT,
                        "count": 1,
                        "seeds": [case["seed"]],
                        "reference_id": ref["id"],
                    },
                )
                assert response.status_code == 202, response.text
                job = response.json()["assistant"]["images"][0]["id"]
                task = app.state.images.tasks.get(job)
                assert task is not None
                if case.get("cancel"):
                    reached = asyncio.create_task(engine.cancel_at_step.wait())
                    try:
                        done, _ = await asyncio.wait(
                            {reached, task},
                            timeout=300,
                            return_when=asyncio.FIRST_COMPLETED,
                        )
                        assert (
                            reached in done and reached.result() and not task.done()
                        ), "Worker ended before cancellation checkpoint"
                    finally:
                        reached.cancel()
                        await asyncio.gather(reached, return_exceptions=True)
                    cancel = await client.post(
                        f"/api/images/jobs/{job}/cancel", json={}
                    )
                    assert cancel.status_code == 200, cancel.text
                await asyncio.wait_for(asyncio.shield(task), 330)
                item = await app.state.images.get(job)
                assert item.state == (
                    "cancelled" if case.get("cancel") else "complete"
                ), item.model_dump()
                job_folder = app.state.images.path(job)
                output = job_folder / "output"
                if case.get("cancel"):
                    assert not output.exists() and not (job_folder / "working").exists()
                else:
                    native_png = critical_png((output / "image.png").read_bytes())
                    export_png = critical_png((output / "export.png").read_bytes())
                    assert all(t in {"IHDR", "IDAT", "IEND"} for t, _ in export_png)
                    assert [
                        r for t, r in native_png if t in {"IHDR", "IDAT", "IEND"}
                    ] == [r for _, r in export_png]
                    download = await client.get(f"/api/images/jobs/{job}/output/png")
                    assert download.content == (output / "export.png").read_bytes()
                    meta = json.loads((output / "metadata.json").read_text())
                    assert meta["reference"] == descriptor
                    if native:
                        assert (
                            meta["generate_seconds"] <= 60
                            and meta["mlx_peak_bytes"] <= 24 * 1024**3
                            and meta["mlx_cache_bytes"] <= 1024**3
                        )
                        assert meta["worker_sha256"] == sha(home / "edit_worker.py")
                assert (
                    ref_folder / "original"
                ).read_bytes() == raw and not capacity.busy
                after = (
                    await runtime_preflight(engine, case["resident"]) if native else []
                )
                meter.sample()
                results.append(
                    {
                        "case": case["id"],
                        "job_id": job,
                        "native": native,
                        "state": item.state,
                        "before": before,
                        "after": after,
                        "reference": descriptor,
                        "storage": json.loads(
                            (job_folder / "storage.json").read_text()
                        ),
                        "original_preserved": True,
                        "sanitized_export": not case.get("cancel"),
                    }
                )
                exclusive(folder / (case["id"] + ".json"), results[-1])
                if sampler.done():
                    await sampler
            if native:
                assert [r["case"] for r in budget.rows() if r["kind"] == "image"] == [
                    c["id"] for c in CASES
                ]
    except BaseException as error:
        exclusive(
            budget.halt,
            {"failure_type": type(error).__name__, "completed_cases": len(results)},
        )
        raise
    finally:
        if sampler:
            sampler.cancel()
            await asyncio.gather(sampler, return_exceptions=True)
        asyncio.create_subprocess_exec = original_spawn
        httpx.AsyncClient.send = original_send
        if meter:
            meter.sample()
            exclusive(folder / "storage.json", meter.report())
        record = {
            "passed": len(results) == 4,
            "native": native,
            "native_image_requests": len(
                [r for r in budget.rows() if r["kind"] == "image"]
            )
            if native
            else 0,
            "fake_image_requests": 0
            if native
            else len([r for r in budget.rows() if r["kind"] == "image"]),
            "preload_requests": len(
                [r for r in budget.rows() if r["kind"] == "preload"]
            ),
            "cases": results,
            "capacity_released": not capacity.busy,
        }
        if native:
            record.update(
                events=engine.events,
                residency=engine.residency,
                swap_mib=engine.swaps,
                reaping=engine.reaps,
                health_seconds=engine.health,
            )
        exclusive(folder / "summary.json", record)
        print(
            json.dumps(
                {
                    k: v
                    for k, v in record.items()
                    if k != "cases"
                    and k
                    not in {
                        "events",
                        "residency",
                        "swap_mib",
                        "reaping",
                        "health_seconds",
                    }
                }
            )
        )
    if not native:
        (OUT / "offline-controller.json").write_text(
            json.dumps(json.loads((folder / "summary.json").read_text()), indent=2)
            + "\n"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--native", action="store_true")
    parser.add_argument("--approval", type=Path)
    args = parser.parse_args()
    if args.native and args.approval is None:
        parser.error("--native requires separate --approval receipt")
    asyncio.run(execute(args.native, args.approval))
