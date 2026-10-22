"""Actual CPU/process tests; native image generation is always replaced."""

import asyncio
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRODUCT = HERE.parent / "product"
PYTHON = Path(
    (Path.home() / ".local/share/workbench/image-worker/product/.python")
    .read_text()
    .strip()
)
sys.path[:0] = [str(HERE), str(ROOT / "server")]
from app.capacity import Capacity
from app.images.codec import ReferenceCodec
from app.images.engine import Engine
from control import digest, new_json, run_case


async def setup(tmp_path):
    home = tmp_path / "worker"
    home.mkdir()
    for name in ("reference_contract.py", "reference_codec.py", "masked_edit.py"):
        shutil.copyfile(PRODUCT / name, home / name)
    (home / ".python").write_text(str(PYTHON))
    shutil.copyfile(HERE / "trial.json", home / "trial.json")
    shutil.copyfile(HERE / "control.py", home / "control.py")
    job = tmp_path / "synthetic"
    inputs = job / "inputs"
    inputs.mkdir(parents=True)
    await asyncio.to_thread(
        subprocess.run,
        [
            str(PYTHON),
            "-c",
            "from PIL import Image;import sys;Image.new('RGB',(768,1024),'blue').save(sys.argv[1],format='PNG')",
            str(inputs / "original"),
        ],
        check=True,
    )
    codec = ReferenceCodec(home)
    reference = await codec.normalize(inputs)
    spec = json.loads((HERE / "trial.json").read_text())
    request = {
        "mode": "edit",
        "prompt": spec["cases"][0]["prompt"],
        "seed": 42,
        "reference": reference,
        "selection": spec["cases"][0]["selection"],
    }
    (job / "input.json").write_text(json.dumps(request))
    snapshot = tmp_path / spec["revision"]
    snapshot.mkdir()
    return home, job, snapshot, codec


@pytest.mark.asyncio
@pytest.mark.parametrize("mode", ["good", "bad-bits", "peak", "network", "helper"])
async def test_worker_mask_contract_helpers_resources_and_independent_composite(
    tmp_path, mode
):
    _home, job, snapshot, codec = await setup(tmp_path)
    output = job / "working"
    output.mkdir()
    child = await asyncio.create_subprocess_exec(
        str(PYTHON),
        str(HERE / "fake_worker_driver.py"),
        mode,
        str(job / "input.json"),
        str(snapshot),
        str(output),
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        start_new_session=True,
    )
    try:
        async with asyncio.timeout(10):
            raw = await child.stdout.read()
            await child.wait()
        events = [json.loads(line) for line in raw.splitlines()]
        if mode == "good":
            assert child.returncode == 0, (await child.stderr.read()).decode()
            assert [
                e["completed_steps"] for e in events if e["type"] == "denoising"
            ] == list(range(41))
            proof = await codec.verify_composite(job)
            assert proof["outside_changed_pixels"] == 0 and proof["changed_pixels"] > 0
            call = json.loads((job / "fake-call.json").read_text())
            assert call["verify"] is False and call["enhance_prompt"] is False
        else:
            assert child.returncode != 0 and events[-1]["type"] == "failed"
            assert not (output / "image.png").exists()
            if mode in {"bad-bits", "peak"}:
                assert not (job / "fake-call.json").exists()
    finally:
        await Engine.stop(child)
        child.stdin.close()
        await codec.close()


class OfflineEngine:
    def __init__(self, *, fail=False):
        self.calls, self.fail = 0, fail

    async def loaded(self):
        self.calls += 1
        return [{"name": "unexpected"}] if self.fail and self.calls > 1 else []

    async def healthy(self):
        return None

    async def swap(self):
        return 0


@pytest.mark.asyncio
async def test_controller_reaps_on_guard_failure_and_blocks_remaining_allowance(
    tmp_path,
):
    home, job, snapshot, codec = await setup(tmp_path)
    # This child holds the actual shared-lock description until it exits.
    (home / "worker.py").write_text(
        "import json,time;print(json.dumps({'type':'initializing'}),flush=True);time.sleep(30)"
    )
    files = [
        home / "worker.py",
        home / "control.py",
        home / "trial.json",
        job / "input.json",
    ]
    new_json(
        tmp_path / "frozen.json",
        {"files": {str(p.relative_to(tmp_path)): digest(p) for p in files}},
    )
    new_json(
        tmp_path / "approval.json",
        {
            "maximum_native_invocations": 2,
            "frozen_sha256": digest(tmp_path / "frozen.json"),
        },
    )
    new_json(tmp_path / "download.json", {"snapshot": str(snapshot)})
    capacity = Capacity(tmp_path / "native.lock")
    with pytest.raises(ValueError, match="empty model slot"):
        await run_case(tmp_path, "synthetic", capacity, OfflineEngine(fail=True), codec)
    result = json.loads((tmp_path / "attempts/synthetic.result.json").read_text())
    assert not result["passed"] and result["worker_reaped"]
    assert result["model_invocations_reserved"] == 1
    assert not capacity.busy and capacity.fd is None
    with pytest.raises((ValueError, FileNotFoundError)):
        await run_case(tmp_path, "private", capacity, OfflineEngine(), codec)
    assert len(list((tmp_path / "attempts").glob("*.reserved.json"))) == 1


def test_download_checks_lfs_and_git_blobs_and_rejects_corruption(tmp_path):
    module_spec = importlib.util.spec_from_file_location(
        "pe3_download", HERE / "download.py"
    )
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    import hashlib

    path = tmp_path / "fixture"
    raw = b"fixed checkpoint fixture"
    path.write_bytes(raw)
    for sha, git in [
        (hashlib.sha256(raw).hexdigest(), None),
        (
            None,
            hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest(),
        ),
    ]:
        item = {"bytes": len(raw), "sha256": sha, "git_blob_sha1": git}
        module.verify(path, item)
        path.write_bytes(raw[:-1] + b"X")
        with pytest.raises(ValueError, match="hash"):
            module.verify(path, item)
        path.write_bytes(raw)
