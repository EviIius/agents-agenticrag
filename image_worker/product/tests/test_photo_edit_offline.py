"""Real Pillow/owned processes with native imports/network blocked by children."""

import asyncio
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "server"))
from app.capacity import Capacity  # noqa: E402
from app.images.codec import ReferenceCodec  # noqa: E402
from app.images.engine import EDIT_DIGEST, Engine  # noqa: E402

PYTHON = Path(
    (Path.home() / ".local/share/workbench/image-worker/product/.python").read_text().strip()
)
REVISION = "e7b7dc27f91deacad38e78976d1f2b499d76a294"


def fixture(folder, kind="oriented"):
    folder.mkdir()
    code = """
import importlib.abc,json,sys
from pathlib import Path
class NoNative(importlib.abc.MetaPathFinder):
 def find_spec(self,fullname,path=None,target=None):
  if fullname.split('.')[0] in {'mlx','mflux','torch','transformers'}:
   raise RuntimeError('Native import forbidden')
sys.meta_path.insert(0,NoNative())
from PIL import Image
root=Path(sys.argv[1]); kind=sys.argv[2]
if kind=='invalid': (root/'original').write_bytes(b'not an image')
elif kind=='bomb':
 im=Image.new('RGB',(1,1),'red');im.save(root/'original',format='PNG')
 import struct,zlib
 raw=bytearray((root/'original').read_bytes());raw[16:24]=struct.pack('>II',100000,100000);raw[29:33]=struct.pack('>I',zlib.crc32(raw[12:29]));(root/'original').write_bytes(raw)
else:
 image=Image.new('RGB',(1024,768) if kind=='oriented' else (3200,1600),'red')
 exif=Image.Exif();exif[274]=6;exif[270]='synthetic metadata only'
 image.save(root/'original',format='JPEG',exif=exif)
"""
    subprocess.run([str(PYTHON), "-c", code, str(folder), kind], check=True)


async def codec(tmp_path, kind="oriented"):
    home = tmp_path / "home"
    home.mkdir()
    (home / ".python").write_text(str(PYTHON))
    for name in ("reference_codec.py", "reference_contract.py"):
        (home / name).write_bytes((HERE / name).read_bytes())
    folder = tmp_path / "reference"
    fixture(folder, kind)
    service = ReferenceCodec(home)
    result = await service.normalize(folder)
    return folder, result


@pytest.mark.asyncio
async def test_real_cpu_codec_orientation_resize_metadata_original_hash(tmp_path):
    folder, result = await codec(tmp_path)
    assert result["original_dimensions"] == [1024, 768]
    assert result["dimensions"] == [768, 1024] and result["exif_orientation"] == 6
    assert (
        result["original_sha256"] == hashlib.sha256((folder / "original").read_bytes()).hexdigest()
    )
    probe = await asyncio.to_thread(
        subprocess.check_output,
        [
            str(PYTHON),
            "-c",
            "from PIL import Image;import sys,json;im=Image.open(sys.argv[1]);im.load();"
            "print(json.dumps({'mode':im.mode,'info':list(im.info)}))",
            str(folder / "reference.png"),
        ],
        text=True,
    )
    assert json.loads(probe) == {"mode": "RGB", "info": []}


@pytest.mark.asyncio
async def test_real_cpu_codec_longest_edge_limit(tmp_path):
    _, result = await codec(tmp_path, "large")
    assert max(result["dimensions"]) == 2048


@pytest.mark.asyncio
@pytest.mark.parametrize("kind", ["invalid", "bomb"])
async def test_real_cpu_codec_rejects_unreadable_or_decompression_bomb(tmp_path, kind):
    with pytest.raises(Exception, match="Couldn't prepare this photo"):
        await codec(tmp_path, kind)


async def job(tmp_path):
    folder, descriptor = await codec(tmp_path)
    root = tmp_path / "job"
    root.mkdir()
    (root / "working").mkdir()
    (root / "inputs").mkdir()
    for name in ("original", "reference.png", "reference.json"):
        os.link(folder / name, root / "inputs" / name)
    request = {
        "mode": "edit",
        "prompt": "Synthetic red shirt",
        "seed": 42,
        "reference": descriptor,
    }
    (root / "input.json").write_text(json.dumps(request))
    (root / REVISION).mkdir()
    return root, request


def spawn(root, mode="normal"):
    return subprocess.Popen(
        [
            str(PYTHON),
            str(HERE / "tests/fake_edit_driver.py"),
            str(root / "input.json"),
            str(root / REVISION),
            str(root / "working"),
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**os.environ, "PE1_FAKE_MODE": mode},
    )


def finish(child):
    try:
        child.wait(timeout=12)
        events = [json.loads(line) for line in child.stdout.read().splitlines()]
        return child.returncode, events
    finally:
        if child.poll() is None:
            child.kill()
            child.wait()
        child.stdin.close()
        child.stdout.close()
        child.stderr.close()


@pytest.mark.asyncio
async def test_product_edit_calls_pixel_class_and_actual_reference(tmp_path):
    root, request = await job(tmp_path)
    code, events = await asyncio.to_thread(finish, spawn(root))
    assert code == 0
    call = json.loads((root / "fake-call.json").read_text())
    assert call["class"] == "Edit"
    assert call["kwargs"] == {
        "prompt": request["prompt"],
        "seed": 42,
        "width": 1024,
        "height": 1024,
        "num_inference_steps": 4,
        "guidance": 1.0,
        "image_paths": [str(root / "inputs/reference.png")],
    }
    assert [e.get("completed_steps") for e in events if e["type"] == "denoising"] == [
        0,
        1,
        2,
        3,
        4,
    ]
    assert events[-1]["type"] == "finished"
    meta = json.loads((root / "working/metadata.json").read_text())
    assert meta["reference"] == request["reference"] and meta["mode"] == "edit"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "mode", ["bad-bits", "peak", "bad-output", "mutate-original", "mutate-reference"]
)
async def test_product_edit_stops_bad_contract_or_resource_without_completion(tmp_path, mode):
    root, _ = await job(tmp_path)
    code, events = await asyncio.to_thread(finish, spawn(root, mode))
    assert code != 0 and events[-1]["type"] == "failed"
    assert not (root / "working/image.png").exists()


@pytest.mark.asyncio
async def test_product_edit_refuses_generation_fallback_before_native_import(tmp_path):
    root, request = await job(tmp_path)
    request.pop("reference")
    request["mode"] = "generate"
    (root / "input.json").write_text(json.dumps(request))
    code, events = await asyncio.to_thread(finish, spawn(root))
    assert code != 0 and events == [{"type": "failed"}]
    assert not (root / "fake-call.json").exists()


@pytest.mark.asyncio
async def test_product_edit_parent_death_stops_owned_process(tmp_path):
    root, _ = await job(tmp_path)
    child = spawn(root, "stall")
    try:
        child.stdin.close()
        await asyncio.to_thread(child.wait, 4)
        assert child.returncode == 71
        assert not (root / "working/image.png").exists()
    finally:
        if child.poll() is None:
            child.kill()
            child.wait()
        child.stdout.close()
        child.stderr.close()


@pytest.mark.asyncio
async def test_cpu_codec_cancellation_reaps_process(tmp_path):
    home = tmp_path / "slow-codec"
    home.mkdir()
    (home / ".python").write_text(str(PYTHON))
    (home / "reference_codec.py").write_text("import time;time.sleep(60)\n")
    service = ReferenceCodec(home)
    task = asyncio.create_task(service.normalize(tmp_path))
    async with asyncio.timeout(4):
        while not service.processes:
            await asyncio.sleep(0.01)
    child = next(iter(service.processes))
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert child.returncode is not None and not service.processes
    with pytest.raises(ProcessLookupError):
        os.kill(child.pid, 0)


@pytest.mark.asyncio
async def test_edit_cancellation_reaps_under_lease_and_runs_final_guard(tmp_path, monkeypatch):
    root, _ = await job(tmp_path)
    home = tmp_path / "fake-engine-home"
    home.mkdir()
    # This owned child injects fake MLX/MFLUX before importing the product worker.
    (home / "edit_worker.py").write_text(
        "import runpy;runpy.run_path(" + repr(str(HERE / "tests/fake_edit_driver.py")) + ")\n"
    )
    capacity = Capacity(tmp_path / "native.lock")
    engine = Engine(home, capacity)
    monkeypatch.setattr(engine, "paths", lambda: (PYTHON, home / "worker.py", root / REVISION))
    states = []
    stopping = []

    async def loaded():
        states.append("loaded")
        return [{"digest": EDIT_DIGEST, "context_length": 32768, "size_vram": 19508609678}]

    async def swap():
        return 0.0

    async def healthy():
        states.append("health")

    async def stop(child):
        await Engine.stop(child)
        assert capacity.busy and child.returncode is not None
        stopping.append(child.pid)
        states.append("reaped")

    async def progress(event):
        if event.get("completed_steps") == 1:
            raise asyncio.CancelledError

    monkeypatch.setattr(engine, "loaded", loaded)
    monkeypatch.setattr(engine, "swap", swap)
    monkeypatch.setattr(engine, "healthy", healthy)
    monkeypatch.setattr(engine, "stop", stop)
    async with capacity.lease():
        with pytest.raises(asyncio.CancelledError):
            await engine.run_edit(root / "input.json", root / "working", progress)
    assert len(stopping) == 1 and not capacity.busy
    after_reap = states[states.index("reaped") + 1 :]
    assert "loaded" in after_reap and "health" in after_reap
    with pytest.raises(ProcessLookupError):
        os.kill(stopping[0], 0)
