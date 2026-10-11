"""Synthetic durable execution, resource ownership and artifact preservation tests."""

import asyncio
import hashlib
import json
import os
import shutil
import struct
import sys
import zlib
from collections.abc import AsyncIterator
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from uuid import uuid4

import httpx
import pytest
import respx
from fastapi import FastAPI

from app.backup import Backups
from app.capacity import Capacity
from app.config import Settings
from app.db.core import Store, connect
from app.errors import AppError
from app.images.backup import restore
from app.images.engine import QUALIFIED_DIGEST, Engine
from app.images.files import MODEL, REVISION, validate
from app.images.jobs import Images
from app.main import create_app
from app.schemas import ImageCreate, ImageStatus
from tests.test_chat import chat_app as chat_app
from tests.test_chat import finish as finish_chat
from tests.test_chat import start as start_chat


def png() -> bytes:
    def chunk(kind: bytes, value: bytes) -> bytes:
        return (
            struct.pack(">I", len(value))
            + kind
            + value
            + struct.pack(">I", zlib.crc32(kind + value))
        )

    pixels = (b"\x00" + b"\x33\x77\xcc" * 1024) * 1024
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", 1024, 1024, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(pixels))
        + chunk(b"IEND", b"")
    )


def output(folder: Path, expected: dict[str, Any]) -> None:
    raw = png()
    (folder / "image.png").write_bytes(raw)
    (folder / "metadata.json").write_text(
        json.dumps(
            {
                **expected,
                "requested_seed": expected["seed"],
                "width": 1024,
                "height": 1024,
                "steps": 4,
                "guidance": 1.0,
                "quantization": 8,
                "cache_limit_bytes": 1073741824,
                "model": MODEL,
                "revision": REVISION,
                "mflux": "0.22.0",
                "sha256": hashlib.sha256(raw).hexdigest(),
            }
        )
    )


class FakeEngine:
    def __init__(self) -> None:
        self.started = asyncio.Event()
        self.release = asyncio.Event()
        self.reaped = asyncio.Event()
        self.calls = 0
        self.fail = False

    def status(self) -> ImageStatus:
        return ImageStatus(available=True)

    async def run(self, manifest: Path, scratch: Path, progress: Any) -> int:
        self.calls += 1
        self.started.set()
        try:
            await progress({"type": "denoising", "completed_steps": 1})
            await self.release.wait()
            if self.fail:
                raise ValueError("Synthetic failure")
            output(scratch, json.loads(manifest.read_text()))
            return 0
        finally:
            # Demonstrate capacity is retained until asynchronous reaping ends.
            await asyncio.sleep(0.01)
            self.reaped.set()


@pytest.fixture
async def images(tmp_path: Path) -> AsyncIterator[Images]:
    async with connect(tmp_path) as db:
        service = Images(Store(db), tmp_path, None, Capacity())
        service.engine = FakeEngine()  # type: ignore[assignment]
        yield service
        await service.close()


def spec(**kwargs: Any) -> ImageCreate:
    return ImageCreate(request_key=uuid4().hex, prompt="Synthetic blue circle", seed=42, **kwargs)


async def test_enabled_capacity_preserves_default_chat_payload(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI],
) -> None:
    app, client, runtime = chat_app
    app.state.registry.capacity = app.state.capacity
    await client.patch("/api/settings", json={"include_current_date": False})
    async with app.state.capacity.lease(background=True):
        response = await start_chat(client, "Synthetic default request", "fake-chat")
        async with asyncio.timeout(2):
            while not app.state.capacity.interactive:
                await asyncio.sleep(0)
        assert not [body for body in runtime.state.captures if body.get("messages")]
    await finish_chat(app, response)
    captured = [body for body in runtime.state.captures if body.get("messages")][-1]
    root = Path(__file__).resolve().parents[2]
    expected = json.loads((root / "artifacts/baseline/ordinary-chat-phase3.json").read_text())
    assert json.dumps(captured, sort_keys=True, separators=(",", ":")) == json.dumps(
        expected, sort_keys=True, separators=(",", ":")
    )
    assert set(captured["options"]) == {"num_ctx"}
    assert "tools" not in captured
    assert not app.state.capacity.busy


async def finish(images: Images, job: str) -> None:
    task = images.tasks.get(job)
    if task:
        await asyncio.wait_for(asyncio.shield(task), 5)


async def test_duplicate_and_conflicting_keys(images: Images) -> None:
    value = spec()
    a, b = await asyncio.gather(images.submit(value), images.submit(value))
    assert a.id == b.id
    await images.engine.started.wait()  # type: ignore[attr-defined]
    assert images.engine.calls == 1  # type: ignore[attr-defined]
    with pytest.raises(AppError, match="different image inputs"):
        await images.submit(value.model_copy(update={"seed": 1337}))
    assert (images.path(a.id) / "input.json").exists()
    assert await images.store.one("SELECT * FROM image_steps WHERE job_id=?", (a.id,))


async def test_cancel_reaps_before_admitting_next(images: Images) -> None:
    first = await images.submit(spec())
    await images.engine.started.wait()  # type: ignore[attr-defined]
    second = await images.submit(spec())
    await images.cancel(first.id)
    assert images.engine.reaped.is_set()  # type: ignore[attr-defined]
    assert (await images.get(first.id)).state == "cancelled"
    images.engine.release.set()  # type: ignore[attr-defined]
    await finish(images, second.id)
    assert (await images.get(second.id)).state == "complete"


async def test_cancel_queued_before_task_starts(images: Images) -> None:
    async with images.capacity.lease():
        job = await images.submit(spec())
        await images.cancel(job.id)
        assert (await images.get(job.id)).state == "cancelled"
        assert images.engine.calls == 0  # type: ignore[attr-defined]


async def test_detached_job_and_sse_replay(images: Images) -> None:
    stream = images.tail(0)
    _, kind, _ = await anext(stream)
    assert kind == "image.snapshot"
    job = await images.submit(spec())
    sequence, kind, _ = await anext(stream)
    assert kind == "image.updated"
    await stream.aclose()  # Closing a phone does not cancel the job.
    images.engine.release.set()  # type: ignore[attr-defined]
    await finish(images, job.id)
    reconnect = images.tail(sequence)
    seen = []
    while True:
        seq, kind, data = await anext(reconnect)
        seen.append(seq)
        if kind == "image.snapshot":
            assert data["jobs"][0]["state"] == "complete"  # type: ignore[index]
            break
    assert seen[0] > sequence
    await reconnect.aclose()


async def test_versions_storage_removal_and_recovery(images: Images) -> None:
    images.engine.release.set()  # type: ignore[attr-defined]
    original = await images.submit(spec())
    await finish(images, original.id)
    version = await images.submit(spec(parent_id=original.id))
    await finish(images, version.id)
    storage = await images.storage()
    assert storage.outputs == 2 and storage.versions == 1
    assert storage.image_bytes == len(png()) * 2
    assert storage.metadata_bytes > 0 and storage.manifest_bytes > 0
    path = await images.artifact(original.id, "png")
    assert path.read_bytes() == png()
    await images.remove(version.id)
    assert path.read_bytes() == png()  # Removing a version preserves original.
    assert (await images.storage()).outputs == 1
    await images.recover()
    assert (await images.get(original.id)).state == "complete"
    await images.clear()
    assert (await images.storage()).image_bytes == 0
    assert (await images.get(original.id)).prompt == "Synthetic blue circle"


async def test_active_removal_is_rejected(images: Images) -> None:
    job = await images.submit(spec())
    with pytest.raises(AppError, match="Cancel this job"):
        await images.remove(job.id)


async def test_failed_retry_preserves_input_and_new_attempt(images: Images) -> None:
    images.engine.fail = True  # type: ignore[attr-defined]
    images.engine.release.set()  # type: ignore[attr-defined]
    failed = await images.submit(spec())
    await finish(images, failed.id)
    assert (await images.get(failed.id)).state == "failed"
    images.engine.fail = False  # type: ignore[attr-defined]
    retry = await images.submit(spec(parent_id=failed.id))
    await finish(images, retry.id)
    assert retry.id != failed.id
    assert (await images.get(retry.id)).state == "complete"
    assert (await images.get(failed.id)).state == "failed"


async def test_missing_output_recovery_and_interrupted_lease(images: Images) -> None:
    images.engine.release.set()  # type: ignore[attr-defined]
    job = await images.submit(spec())
    await finish(images, job.id)
    (await images.artifact(job.id, "png")).unlink()
    await images.recover()
    assert (await images.get(job.id)).state == "failed"
    await images.store.execute("UPDATE image_jobs SET state='running' WHERE id=?", (job.id,))
    await images.recover()
    assert (await images.get(job.id)).state == "interrupted"
    assert not images.capacity.busy


async def test_crash_between_rename_and_commit_is_not_success(images: Images) -> None:
    job = await images.submit(spec())
    await images.cancel(job.id)
    folder = images.path(job.id) / "output"
    folder.mkdir()
    output(folder, {"prompt": job.prompt, "seed": job.seed})
    await images.store.execute("UPDATE image_jobs SET state='running' WHERE id=?", (job.id,))
    await images.recover()
    assert (await images.get(job.id)).state == "interrupted"
    await images.recover()
    assert not folder.exists()


async def test_low_disk_and_unavailable(images: Images, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(shutil, "disk_usage", lambda _: shutil._ntuple_diskusage(100, 99, 1))
    with pytest.raises(AppError, match="128 MB"):
        await images.submit(spec())
    images.engine = Engine(None)
    with pytest.raises(AppError, match="unavailable"):
        await images.submit(spec())
    assert not await images.list()


async def test_backups_deduplicate_restore_and_detect_corruption(
    images: Images, tmp_path: Path
) -> None:
    images.engine.release.set()  # type: ignore[attr-defined]
    job = await images.submit(spec())
    await finish(images, job.id)
    current = datetime(2026, 10, 10, 3, 30)
    backups = Backups(images.store, images.data, clock=lambda: current, images=images)
    await backups.make()
    current += timedelta(days=1)
    await backups.make()
    blobs = images.data / "backups/images/blobs"
    assert len(list(blobs.iterdir())) == 2
    backup = backups.files()[-1]
    destination = tmp_path / "restored"
    assert restore(backup, destination) == 1
    assert (destination / "images" / job.id / "output/image.png").read_bytes() == png()
    with pytest.raises(ValueError, match="must not exist"):
        restore(backup, destination)
    await images.remove(job.id)
    assert restore(backup, tmp_path / "restored-again") == 1
    next(blobs.iterdir()).write_bytes(b"broken")
    with pytest.raises(ValueError, match="Corrupt"):
        restore(backup, tmp_path / "broken-restore")
    assert not (tmp_path / "broken-restore").exists()


@pytest.mark.parametrize(
    "damage", ["crc", "metadata", "missing", "dimensions", "truncated", "symlink"]
)
def test_invalid_files_are_rejected(tmp_path: Path, damage: str) -> None:
    expected = {"prompt": "Synthetic", "seed": 42}
    output(tmp_path, expected)
    image = tmp_path / "image.png"
    if damage == "crc":
        image.write_bytes(image.read_bytes()[:-1] + b"X")
    elif damage == "metadata":
        (tmp_path / "metadata.json").write_text("{}")
    elif damage == "missing":
        image.unlink()
    elif damage == "dimensions":
        image.write_bytes(png().replace(struct.pack(">I", 1024), struct.pack(">I", 999), 1))
    elif damage == "truncated":
        image.write_bytes(png()[:18])
    else:
        image.rename(tmp_path / "actual.png")
        image.symlink_to(tmp_path / "actual.png")
    with pytest.raises((ValueError, OSError)):
        validate(tmp_path, expected)


async def test_fairness_and_cancel_waiter() -> None:
    capacity, order = Capacity(), []

    async def work(name: str, background: bool = False) -> None:
        async with capacity.lease(background=background):
            order.append(name)
            await asyncio.sleep(0)

    async with capacity.lease():
        tasks = [asyncio.create_task(work("image", True))] + [
            asyncio.create_task(work(f"chat{i}")) for i in range(5)
        ]
        cancelled = asyncio.create_task(work("cancelled"))
        await asyncio.sleep(0)
        cancelled.cancel()
    await asyncio.gather(*tasks)
    await asyncio.gather(cancelled, return_exceptions=True)
    assert "cancelled" not in order
    assert order.index("image") <= 3
    assert not capacity.busy


@respx.mock
async def test_admission_uses_reported_digest_context_size() -> None:
    route = respx.get("http://127.0.0.1:11434/api/ps")
    engine = Engine(None)
    route.respond(
        200,
        json={
            "models": [
                {
                    "name": "arbitrary-name",
                    "digest": QUALIFIED_DIGEST,
                    "context_length": 32768,
                    "size_vram": 21827095100,
                }
            ]
        },
    )
    await engine.admit()
    route.respond(
        200,
        json={
            "models": [
                {"digest": QUALIFIED_DIGEST, "context_length": 65536, "size_vram": 21827095100}
            ]
        },
    )
    with pytest.raises(AppError, match="not qualified"):
        await engine.admit()
    route.respond(200, json={"models": []})
    await engine.admit()
    route.respond(503)
    with pytest.raises(AppError, match="Cannot verify"):
        await engine.admit()
    assert all(call.request.method == "GET" for call in respx.calls)


async def test_process_cancellation_and_parent_pipe_exit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    worker = tmp_path / "worker.py"
    worker.write_text(
        "import os,sys,time,threading\n"
        "from pathlib import Path\n"
        "Path(sys.argv[3]).joinpath('pid').write_text(str(os.getpid()))\n"
        "def lost_parent():\n"
        " sys.stdin.buffer.read()\n"
        " os._exit(71)\n"
        "threading.Thread(target=lost_parent,daemon=True).start()\n"
        'print(\'{"type":"initializing"}\',flush=True)\n'
        "time.sleep(100)\n"
    )

    capacity = Capacity(tmp_path / "native.lock")
    engine = Engine(tmp_path, capacity)
    monkeypatch.setattr(engine, "paths", lambda: (Path(sys.executable), worker, tmp_path))

    async def admitted() -> None:
        pass

    async def swap() -> float:
        return 0.0

    monkeypatch.setattr(engine, "admit", admitted)
    monkeypatch.setattr(engine, "swap", swap)
    started = asyncio.Event()

    async def progress(_: dict[str, Any]) -> None:
        started.set()

    async def run() -> None:
        async with capacity.lease(background=True):
            await engine.run(tmp_path / "request", tmp_path, progress)

    task = asyncio.create_task(run())
    await asyncio.wait_for(started.wait(), 3)
    pid = int((tmp_path / "pid").read_text())
    task.cancel()
    await asyncio.gather(task, return_exceptions=True)
    with pytest.raises(ProcessLookupError):
        os.kill(pid, 0)
    assert not capacity.busy
    child = await asyncio.create_subprocess_exec(
        sys.executable,
        str(worker),
        "request",
        "model",
        str(tmp_path),
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
    )
    assert child.stdout and child.stdin
    await child.stdout.readline()
    child.stdin.close()
    assert await asyncio.wait_for(child.wait(), 3) == 71


async def test_api_validation_and_additive_output_routes(tmp_path: Path) -> None:
    app = create_app(Settings(data_dir=tmp_path, dev=True))
    async with app.router.lifespan_context(app):
        app.state.images.engine = FakeEngine()
        app.state.images.engine.release.set()
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app), base_url="http://127.0.0.1"
        ) as client:
            assert (await client.get("/api/images/status")).json()["available"]
            assert (
                await client.post(
                    "/api/images/jobs", json={**spec().model_dump(), "command": "arbitrary"}
                )
            ).status_code == 422
            accepted = await client.post("/api/images/jobs", json=spec().model_dump())
            assert accepted.status_code == 202
            identifier = accepted.json()["id"]
            await finish(app.state.images, identifier)
            response = await client.get(f"/api/images/jobs/{identifier}/output/png")
            assert response.content == png() and response.headers["content-type"] == "image/png"
            assert (await client.get(f"/api/images/jobs/{identifier}/output/json")).json()[
                "seed"
            ] == 42
            assert (await client.get("/api/images/jobs/not-a-path")).status_code == 404
            assert (
                await client.post("/api/images/clear", json={"confirm": False})
            ).status_code == 422
            assert (await client.post("/api/images/clear", json={"confirm": True})).json()[
                "outputs"
            ] == 0


async def test_engine_success_error_and_resource_stop(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    engine = Engine(tmp_path)
    worker = tmp_path / "worker.py"
    monkeypatch.setattr(engine, "paths", lambda: (Path(sys.executable), worker, tmp_path))

    async def admitted() -> None:
        pass

    async def stable() -> float:
        return 0

    async def progress(_: dict[str, Any]) -> None:
        pass

    monkeypatch.setattr(engine, "admit", admitted)
    monkeypatch.setattr(engine, "swap", stable)
    worker.write_text('print(\'{"type":"finished"}\',flush=True)\n')
    assert await engine.run(tmp_path / "request", tmp_path, progress) == 0
    worker.write_text("import sys\nsys.exit(2)\n")
    with pytest.raises(AppError, match="exited"):
        await engine.run(tmp_path / "request", tmp_path, progress)
    worker.write_text("print('[]',flush=True)\n")
    with pytest.raises(ValueError, match="Invalid worker event"):
        await engine.run(tmp_path / "request", tmp_path, progress)
    worker.write_text("import time\ntime.sleep(10)\n")
    count = 0

    async def growth() -> float:
        nonlocal count
        count += 1
        return 0 if count == 1 else 600

    monkeypatch.setattr(engine, "swap", growth)
    with pytest.raises(AppError, match="host swap"):
        await engine.run(tmp_path / "request", tmp_path, progress)


async def test_engine_private_setup_and_swap(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    engine = Engine(tmp_path)
    assert not engine.status().available
    model = tmp_path / REVISION
    model.mkdir()
    (tmp_path / ".python").write_text(sys.executable)
    (tmp_path / "config.json").write_text(json.dumps({"model_path": str(model)}))
    (tmp_path / "worker.py").write_text("# synthetic worker")
    assert engine.status().available
    assert engine.paths()[0] == Path(sys.executable)
    import sys as platform_sys

    if platform_sys.platform == "darwin":
        assert await engine.swap() >= 0
    (tmp_path / "config.json").write_text("null")
    assert not engine.status().available


async def test_queued_restart_and_delete_recovery(images: Images) -> None:
    images.engine.release.set()  # type: ignore[attr-defined]
    original = await images.submit(spec())
    await finish(images, original.id)
    folder = images.path(original.id)
    (folder / "output").rename(folder / "deleting")
    await images.recover()
    assert (folder / "output").exists()
    orphan = images.folder / uuid4().hex
    orphan.mkdir()
    await images.recover()
    assert not orphan.exists()
    async with images.capacity.lease():
        queued = await images.submit(spec())
        task = images.tasks[queued.id]
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)
    await images.store.execute("UPDATE image_jobs SET state='queued' WHERE id=?", (queued.id,))
    await images.recover()
    await finish(images, queued.id)
    assert (await images.get(queued.id)).state == "complete"


async def test_output_backup_retention_and_failed_backup(images: Images) -> None:
    images.engine.release.set()  # type: ignore[attr-defined]
    job = await images.submit(spec())
    await finish(images, job.id)
    current = datetime(2026, 10, 10, 3, 30)
    backups = Backups(images.store, images.data, clock=lambda: current, images=images)
    await backups.make()
    await images.remove(job.id)
    for _ in range(7):
        current += timedelta(days=1)
        await backups.make()
    assert len(backups.files()) == 7
    assert not list((images.data / "backups/images/blobs").iterdir())
    assert len(list((images.data / "backups/images").glob("auto-*.json"))) == 7


async def test_parent_watch_exits_normally_with_open_control_pipe(tmp_path: Path) -> None:
    worker = tmp_path / "watch.py"
    worker.write_text(
        "import os,sys,threading,time\n"
        "threading.Thread(target=lambda:os.read(sys.stdin.fileno(),1),daemon=True).start()\n"
        "time.sleep(.1)\n"
        "print('finished',flush=True)\n"
    )
    child = await asyncio.create_subprocess_exec(
        sys.executable,
        str(worker),
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    assert child.stdout and child.stdin and child.stderr
    assert await child.stdout.readline() == b"finished\n"
    assert await asyncio.wait_for(child.wait(), 3) == 0
    assert await child.stderr.read() == b""
    child.stdin.close()
