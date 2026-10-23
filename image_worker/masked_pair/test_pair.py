"""CPU/subprocess checks for the new pair; no real model import or inference."""

import asyncio
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(HERE), str(ROOT / "server")]
from app.capacity import Capacity
from app.images.codec import ReferenceCodec
from app.images.engine import Engine
from control import digest, new_json, run_case

PYTHON = (
    (Path.home() / ".local/share/workbench/image-worker/product/.python")
    .read_text()
    .strip()
)


async def setup(root):
    home = root / "worker"
    home.mkdir()
    for name in ("pair.json", "trial.json", "control.py"):
        shutil.copyfile(HERE / name, home / name)
    for name in ("masked_edit.py", "reference_codec.py", "reference_contract.py"):
        shutil.copyfile(HERE.parent / "product" / name, home / name)
    (home / ".python").write_text(PYTHON)
    codec = ReferenceCodec(home)
    for case in ("flux", "qwen"):
        inputs = root / case / "inputs"
        inputs.mkdir(parents=True)
        await asyncio.to_thread(
            subprocess.run,
            [
                PYTHON,
                "-c",
                "from PIL import Image;import sys;Image.new('RGB',(768,1024),'blue').save(sys.argv[1],format='PNG')",
                str(inputs / "original"),
            ],
            check=True,
        )
        reference = await codec.normalize(inputs)
        request = {
            "mode": "edit",
            "prompt": "Change the selected area to yellow.",
            "seed": 42,
            "reference": reference,
            "selection": {
                "version": 1,
                "strokes": [
                    {"radius": 0.15, "points": [[0.5, 0.5]]},
                    {"operation": "erase", "radius": 0.03, "points": [[0.5, 0.5]]},
                ],
            },
        }
        (root / case / "input.json").write_text(json.dumps(request))
    spec = json.loads((home / "pair.json").read_text())
    locations = {c: str(root / spec["engines"][c]["revision"]) for c in spec["order"]}
    for path in locations.values():
        Path(path).mkdir()
    new_json(root / "model-locations.json", locations)
    return home, codec


def freeze(root):
    files = [p for p in root.rglob("*") if p.is_file()]
    new_json(
        root / "frozen.json",
        {"files": {str(p.relative_to(root)): digest(p) for p in files}},
    )
    new_json(
        root / "approval.json",
        {
            "maximum_native_invocations": 2,
            "frozen_sha256": digest(root / "frozen.json"),
        },
    )


class OfflineEngine:
    def __init__(self, fail=False):
        self.calls, self.fail = 0, fail

    async def loaded(self):
        self.calls += 1
        return [{"name": "unexpected"}] if self.fail and self.calls > 1 else []

    async def healthy(self):
        return None

    async def swap(self):
        return 0


@pytest.mark.asyncio
async def test_guard_failure_reaps_and_consumes_slot_without_qwen_continuation(
    tmp_path,
):
    home, codec = await setup(tmp_path)
    (home / "flux_worker.py").write_text(
        "import json,time;print(json.dumps({'type':'initializing'}),flush=True);time.sleep(30)"
    )
    (home / "qwen_worker.py").write_text("raise AssertionError('must not run')")
    freeze(tmp_path)
    capacity = Capacity(tmp_path / "native.lock")
    try:
        with pytest.raises(ValueError, match="empty model slot"):
            await run_case(tmp_path, "flux", capacity, OfflineEngine(True), codec)
        result = json.loads((tmp_path / "attempts/flux.result.json").read_text())
        assert result["worker_reaped"] and not result["passed"]
        assert not capacity.busy and capacity.fd is None
        with pytest.raises((ValueError, FileNotFoundError)):
            await run_case(tmp_path, "qwen", capacity, OfflineEngine(), codec)
        with pytest.raises(ValueError, match="allowance"):
            await run_case(tmp_path, "flux", capacity, OfflineEngine(), codec)
        assert len(list((tmp_path / "attempts").glob("*.reserved.json"))) == 1
    finally:
        await codec.close()


@pytest.mark.asyncio
async def test_frozen_input_tamper_refuses_before_reservation(tmp_path):
    _home, codec = await setup(tmp_path)
    freeze(tmp_path)
    (tmp_path / "flux/input.json").write_text("{}")
    try:
        with pytest.raises(ValueError, match="changed after freezing"):
            await run_case(
                tmp_path,
                "flux",
                Capacity(tmp_path / "native.lock"),
                OfflineEngine(),
                codec,
            )
        assert not (tmp_path / "attempts").exists()
    finally:
        await codec.close()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "engine,mode",
    [(e, m) for e in ("flux", "qwen") for m in ("good", "bad-bits", "peak", "network")]
    + [("qwen", "helper")],
)
async def test_actual_workers_with_cpu_model_doubles(tmp_path, engine, mode):
    home, codec = await setup(tmp_path)
    job = tmp_path / engine
    output = job / "working"
    output.mkdir()
    spec = json.loads((home / "pair.json").read_text())["engines"][engine]
    args = [PYTHON, str(HERE / f"fake_{engine}.py")]
    if engine == "qwen":
        args.append(mode)
    else:
        (job / "fake-mode").write_text("normal" if mode == "good" else mode)
    args.extend(
        [str(job / "input.json"), str(tmp_path / spec["revision"]), str(output)]
    )
    child = await asyncio.create_subprocess_exec(
        *args,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        start_new_session=True,
    )
    try:
        async with asyncio.timeout(15):
            raw = await child.stdout.read()
            await child.wait()
        events = [json.loads(line) for line in raw.splitlines()]
        if mode == "good":
            assert child.returncode == 0, (await child.stderr.read()).decode()
            assert [
                e["completed_steps"] for e in events if e["type"] == "denoising"
            ] == list(range(spec["steps"] + 1))
            proof = await codec.verify_composite(job)
            assert proof["outside_changed_pixels"] == 0 and proof["changed_pixels"] > 0
        else:
            assert child.returncode != 0 and events[-1]["type"] == "failed"
            assert not (output / "image.png").exists()
    finally:
        await Engine.stop(child)
        child.stdin.close()
        await codec.close()


@pytest.mark.asyncio
@pytest.mark.parametrize("bound_review", [True, False])
async def test_visual_failure_allows_second_engine_only_with_bound_review(
    tmp_path, bound_review
):
    home, codec = await setup(tmp_path)
    for name in ("flux_worker.py", "qwen_worker.py"):
        shutil.copyfile(HERE / "fake_control_worker.py", home / name)
    assert digest(tmp_path / "flux/input.json") == digest(tmp_path / "qwen/input.json")
    freeze(tmp_path)
    capacity = Capacity(tmp_path / "native.lock")
    try:
        first = await run_case(tmp_path, "flux", capacity, OfflineEngine(), codec)
        assert first["passed"] and first["worker_reaped"]
        new_json(
            tmp_path / "attempts/flux.quality.json",
            {
                "reviewed": True,
                "passed": False,
                "output_sha256": first["output_sha256"] if bound_review else "wrong",
            },
        )
        if bound_review:
            second = await run_case(tmp_path, "qwen", capacity, OfflineEngine(), codec)
            assert second["passed"] and second["worker_reaped"]
            with pytest.raises(ValueError, match="allowance"):
                await run_case(tmp_path, "qwen", capacity, OfflineEngine(), codec)
            assert len(list((tmp_path / "attempts").glob("*.reserved.json"))) == 2
        else:
            with pytest.raises(ValueError, match="bound visual review"):
                await run_case(tmp_path, "qwen", capacity, OfflineEngine(), codec)
            assert len(list((tmp_path / "attempts").glob("*.reserved.json"))) == 1
        assert not capacity.busy and capacity.fd is None
    finally:
        await codec.close()
