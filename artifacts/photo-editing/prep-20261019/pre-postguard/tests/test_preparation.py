"""No-inference PE0: real CPU codecs, fake native modules, actual owned processes."""

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
sys.path[:0] = [str(HERE), str(ROOT / "server")]
from controller import (  # noqa: E402
    EditEngine,
    PlannedCancellation,
    health_guard,
    require_approval,
    reserve,
    run_case,
)

from app.capacity import Capacity  # noqa: E402

PYTHON = Path(
    (Path.home() / ".local/share/workbench/image-worker/product/.python").read_text().strip()
)
REVISION = "e7b7dc27f91deacad38e78976d1f2b499d76a294"


def cpu(root, kind="png"):
    result = subprocess.run(
        [str(PYTHON), str(HERE / "tests/cpu_fixture.py"), str(root), kind],
        capture_output=True,
        text=True,
    )
    return result, json.loads(result.stdout)


def job(tmp_path, mode="generate", kind="png"):
    root = tmp_path.resolve()
    root.mkdir(exist_ok=True)
    (root / "output").mkdir()
    (root / REVISION).mkdir()
    request = {"mode": mode, "seed": 42, "prompt": "Synthetic offline fixture only"}
    if mode == "edit":
        result, descriptor = cpu(root, kind)
        assert result.returncode == 0, result.stderr
        request["reference"] = descriptor
    (root / "request.json").write_text(json.dumps(request))
    return root, request


def spawn(root, fake_mode="normal"):
    return subprocess.Popen(
        [
            str(PYTHON),
            str(HERE / "tests/fake_driver.py"),
            str(root / "request.json"),
            str(root / REVISION),
            str(root / "output"),
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={
            **os.environ,
            "PE0_FAKE_MODE": fake_mode,
            "HF_HUB_OFFLINE": "1",
            "TRANSFORMERS_OFFLINE": "1",
        },
    )


def finish(process):
    try:
        process.wait(timeout=12)
        output, errors = process.stdout.read(), process.stderr.read()
        return process.returncode, [json.loads(line) for line in output.splitlines()], errors
    finally:
        if process.poll() is None:
            process.kill()
            process.wait()
        process.stdin.close()
        process.stdout.close()
        process.stderr.close()


def test_generation_payload_matches_existing_worker(tmp_path):
    root, request = job(tmp_path)
    code, events, errors = finish(spawn(root))
    assert code == 0 and not errors
    call = json.loads((root / "fake-call.json").read_text())
    assert call == {
        "class": "Generate",
        "kwargs": {
            "seed": 42,
            "prompt": request["prompt"],
            "width": 1024,
            "height": 1024,
            "num_inference_steps": 4,
            "guidance": 1.0,
        },
    }
    assert [e["completed_steps"] for e in events if e["type"] == "denoising"] == [0, 1, 2, 3, 4]
    assert events[-1]["type"] == "finished"
    assert (root / "output/metadata.json").is_file()
    assert not list((root / "output").glob(".*partial*"))


def test_edit_passes_bound_actual_pixels_without_touching_original(tmp_path):
    root, request = job(tmp_path, "edit")
    original = (root / "inputs/original").read_bytes()
    code, events, errors = finish(spawn(root))
    assert code == 0 and not errors and events[-1]["type"] == "finished"
    call = json.loads((root / "fake-call.json").read_text())
    assert call["class"] == "Edit"
    assert call["kwargs"]["image_paths"] == [str(root / "inputs/reference.png")]
    metadata = json.loads((root / "output/metadata.json").read_text())
    assert metadata["mode"] == "edit" and metadata["reference"] == request["reference"]
    assert (root / "inputs/original").read_bytes() == original


@pytest.mark.parametrize(
    "kind,dimensions,orientation",
    [("png", [1024, 768], 1), ("oriented", [768, 1024], 6), ("large", [2048, 1024], 1)],
)
def test_cpu_normalization_is_bounded_oriented_and_strips_metadata(
    tmp_path, kind, dimensions, orientation
):
    result, descriptor = cpu(tmp_path, kind)
    assert result.returncode == 0
    assert descriptor["dimensions"] == dimensions
    assert descriptor["exif_orientation"] == orientation
    assert (
        descriptor["original_sha256"]
        == hashlib.sha256((tmp_path / "inputs/original").read_bytes()).hexdigest()
    )
    # Worker validation additionally decodes the normalized image and rejects any metadata.
    root = tmp_path
    (root / "output").mkdir()
    (root / REVISION).mkdir()
    (root / "request.json").write_text(
        json.dumps({"mode": "edit", "prompt": "Synthetic", "seed": 42, "reference": descriptor})
    )
    assert finish(spawn(root))[0] == 0


@pytest.mark.parametrize(
    "mutation",
    [
        "mode",
        "seed-bool",
        "seed-float",
        "seed-large",
        "empty-prompt",
        "extra-path",
        "missing-reference",
        "generate-reference",
        "duplicate",
        "output-existing",
        "request-symlink",
        "input-symlink",
        "directory-symlink",
        "original-changed",
        "working-changed",
        "receipt-changed",
    ],
)
def test_invalid_input_refuses_before_model_initialization(tmp_path, mutation):
    root, request = job(
        tmp_path,
        "edit"
        if mutation not in {"generate-reference", "request-symlink", "output-existing"}
        else "generate",
    )
    if mutation == "mode":
        request["mode"] = "automatic"
    elif mutation == "seed-bool":
        request["seed"] = True
    elif mutation == "seed-float":
        request["seed"] = 42.0
    elif mutation == "seed-large":
        request["seed"] = 2**32
    elif mutation == "empty-prompt":
        request["prompt"] = " "
    elif mutation == "extra-path":
        request["image_paths"] = ["/not-owned/secret.png"]
    elif mutation == "missing-reference":
        request.pop("reference")
    elif mutation == "generate-reference":
        request["reference"] = {}
    elif mutation == "output-existing":
        (root / "output/previous.png").write_bytes(b"preserved")
    elif mutation == "input-symlink":
        target = root / "inputs/reference.png"
        target.rename(root / "external.png")
        target.symlink_to(root / "external.png")
    elif mutation == "directory-symlink":
        (root / "inputs").rename(root / "other-inputs")
        (root / "inputs").symlink_to(root / "other-inputs")
    elif mutation == "original-changed":
        (root / "inputs/original").write_bytes(b"changed")
    elif mutation == "working-changed":
        (root / "inputs/reference.png").write_bytes(b"changed")
    elif mutation == "receipt-changed":
        (root / "inputs/reference.json").write_text("{}")
    path = root / "request.json"
    path.write_text(json.dumps(request))
    if mutation == "duplicate":
        path.write_text('{"mode":"generate","mode":"edit"}')
    if mutation == "request-symlink":
        path.rename(root / "other.json")
        path.symlink_to(root / "other.json")
    code, events, errors = finish(spawn(root))
    assert code != 0 and events == [{"type": "failed"}]
    assert b"not-owned" not in errors and request["prompt"].encode() not in errors
    assert not (root / "fake-call.json").exists()


@pytest.mark.parametrize(
    "mode", ["bad-bits", "peak", "bad-output", "mutate-reference", "mutate-original"]
)
def test_failed_native_contract_cannot_commit_completed_output(tmp_path, mode):
    root, _ = job(tmp_path, "edit")
    code, events, _ = finish(spawn(root, mode))
    assert code != 0 and events[-1]["type"] == "failed"
    assert not any(e["type"] == "finished" for e in events)
    assert not (root / "output/image.png").exists()
    assert not (root / "output/metadata.json").exists()


def test_parent_pipe_eof_exits_the_actual_worker(tmp_path):
    root, _ = job(tmp_path, "edit")
    process = spawn(root, "stall")
    while True:
        event = json.loads(process.stdout.readline())
        if event.get("completed_steps") == 1:
            break
    process.stdin.close()
    process.wait(timeout=3)
    assert process.returncode == 71
    process.stdout.close()
    process.stderr.close()
    assert not (root / "output/metadata.json").exists()


class OfflineEngine(EditEngine):
    def __init__(self, root, capacity, mode="normal"):
        super().__init__(root, capacity)
        self.root = root
        self.mode = mode
        self.calls = 0

    def paths(self):
        self.calls += 1
        return PYTHON, HERE / "tests/fake_driver.py", self.root / REVISION

    async def loaded(self):
        return [
            {
                "digest": "09386c7af8487c073bfb845833462d30d0d48ad69428c301b909dc159c028b0a",
                "context_length": 32768,
                "size_vram": 19508609678,
            }
        ]

    async def swap(self):
        return 0


@pytest.mark.asyncio
async def test_shared_lease_cancel_reaps_and_next_edit_recovers(tmp_path):
    root, _ = job(tmp_path / "cancel", "edit")
    capacity = Capacity(tmp_path / "native.lock")
    engine = OfflineEngine(root, capacity)
    (root / "fake-mode").write_text("stall")
    with pytest.raises(PlannedCancellation):
        await engine.owned_run(root / "request.json", root / "output", cancel_at_step=1)
    with pytest.raises(ProcessLookupError):
        os.kill(int((root / "fake-pid").read_text()), 0)
    assert not capacity.busy and capacity.fd is None
    assert not (root / "output/metadata.json").exists()
    recovered, _ = job(tmp_path / "recover", "edit")
    next_engine = OfflineEngine(recovered, capacity)
    events = await next_engine.owned_run(recovered / "request.json", recovered / "output")
    assert events[-1]["type"] == "finished" and not capacity.busy
    assert not (root / "output/metadata.json").exists()


@pytest.mark.asyncio
@pytest.mark.parametrize("mutation", ["missing", "second", "digest", "context"])
async def test_trial_requires_exact_daily_chat_residency(tmp_path, mutation):
    root, _ = job(tmp_path)
    engine = OfflineEngine(root, Capacity())

    original = await engine.loaded()

    async def missing():
        if mutation == "missing":
            return []
        if mutation == "second":
            return original * 2
        original[0]["digest" if mutation == "digest" else "context_length"] = "unknown"
        return original

    engine.loaded = missing
    with pytest.raises(ValueError, match="residency"):
        await engine.owned_run(root / "request.json", root / "output")
    assert not (root / "fake-call.json").exists()


@pytest.mark.asyncio
async def test_health_failure_waits_for_owned_task_cleanup():
    reaped = asyncio.Event()

    async def owned_task():
        try:
            await asyncio.sleep(60)
        finally:
            reaped.set()

    task = asyncio.create_task(owned_task())
    await asyncio.sleep(0)

    async def failed_probe():
        raise ValueError("health failed")

    with pytest.raises(ValueError):
        await health_guard(task, failed_probe)
    assert task.done() and reaped.is_set()


def test_missing_native_approval_refuses_before_any_invocation(tmp_path):
    with pytest.raises(FileNotFoundError):
        require_approval(tmp_path, [HERE / "worker.py"])
    assert not (tmp_path / "attempts").exists()


def test_frozen_mug_fixture_matches_original_trial():
    plan = json.loads((HERE / "trial.json").read_text())
    mug = plan["cases"][3]
    assert (
        hashlib.sha256((ROOT / mug["reference"]).read_bytes()).hexdigest() == mug["original_sha256"]
    )
    assert len(plan["cases"]) == plan["maximum_worker_invocations"] == 6
    assert (
        plan["cases"][4]["same_request_as"] == plan["cases"][5]["same_request_as"] == "background"
    )


def synthetic_approval(root):
    sources = {
        name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
        for name in ("contracts.py", "worker.py", "controller.py", "trial.json")
    }
    (root / "approval.json").write_text(
        json.dumps({"approved_sources": sources, "maximum_invocations": 6})
    )


def declared_portrait(root):
    folder = root / "cases/portrait"
    folder.mkdir(parents=True)
    (folder / "output").mkdir()
    portrait = json.loads((HERE / "trial.json").read_text())["cases"][0]
    (folder / "request.json").write_text(
        json.dumps({"mode": "generate", "seed": 42, "prompt": portrait["prompt"]})
    )
    return folder


def test_changed_source_receipt_or_call_limit_rejects(tmp_path):
    synthetic_approval(tmp_path)
    path = tmp_path / "approval.json"
    receipt = json.loads(path.read_text())
    receipt["maximum_invocations"] = 7
    path.write_text(json.dumps(receipt))
    with pytest.raises(ValueError):
        reserve(tmp_path, "portrait")
    receipt["maximum_invocations"] = 6
    receipt["approved_sources"]["worker.py"] = "changed"
    path.write_text(json.dumps(receipt))
    with pytest.raises(ValueError):
        reserve(tmp_path, "portrait")
    assert not (tmp_path / "attempts").exists()


def test_budget_refuses_repeat_and_out_of_order(tmp_path):
    synthetic_approval(tmp_path)
    declared_portrait(tmp_path)
    with pytest.raises(ValueError):
        reserve(tmp_path, "background")
    reserve(tmp_path, "portrait")
    with pytest.raises(ValueError):
        reserve(tmp_path, "portrait")
    with pytest.raises(FileNotFoundError):
        reserve(tmp_path, "background")
    assert len(list((tmp_path / "attempts").glob("*.reserved.json"))) == 1


@pytest.mark.parametrize("prior", ["failed", "missing-review", "rejected-review", "wrong-hash"])
def test_required_failure_or_visual_review_blocks_next_case(tmp_path, prior):
    synthetic_approval(tmp_path)
    declared_portrait(tmp_path)
    reserve(tmp_path, "portrait")
    attempts = tmp_path / "attempts"
    (attempts / "portrait.result.json").write_text(
        json.dumps({"passed": prior != "failed", "output_sha256": "frozen-output"})
    )
    if prior not in {"failed", "missing-review"}:
        (attempts / "portrait.quality.json").write_text(
            json.dumps(
                {
                    "continue": prior != "rejected-review",
                    "reviewer": "Synthetic reviewer",
                    "output_sha256": "wrong" if prior == "wrong-hash" else "frozen-output",
                }
            )
        )
    with pytest.raises((ValueError, FileNotFoundError)):
        reserve(tmp_path, "background")
    assert len(list(attempts.glob("*.reserved.json"))) == 1


def test_six_attempt_budget_cannot_be_extended(tmp_path):
    synthetic_approval(tmp_path)
    attempts = tmp_path / "attempts"
    attempts.mkdir()
    for index in range(6):
        (attempts / f"{index}.reserved.json").write_text("{}")
    with pytest.raises(ValueError, match="budget"):
        reserve(tmp_path, "portrait")


@pytest.mark.asyncio
async def test_failed_reserved_case_is_recorded_and_cannot_repeat(tmp_path, monkeypatch):
    synthetic_approval(tmp_path)
    declared_portrait(tmp_path)

    async def healthy():
        return None

    monkeypatch.setattr(sys.modules["controller"], "probe_health", healthy)

    class FailedEngine:
        async def owned_run(self, *args, **kwargs):
            raise ValueError("Synthetic failure")

    with pytest.raises(ValueError):
        await run_case(tmp_path, "portrait", FailedEngine())
    outcome = json.loads((tmp_path / "attempts/portrait.result.json").read_text())
    assert outcome["passed"] is False and outcome["failure_type"] == "ValueError"
    with pytest.raises(ValueError):
        await run_case(tmp_path, "portrait", FailedEngine())


@pytest.mark.asyncio
async def test_approved_case_adapter_completes_with_fake_worker_only(tmp_path, monkeypatch):
    synthetic_approval(tmp_path)
    (tmp_path / "cases").mkdir()
    root, request = job(tmp_path / "cases/portrait")
    request["prompt"] = json.loads((HERE / "trial.json").read_text())["cases"][0]["prompt"]
    (root / "request.json").write_text(json.dumps(request))

    async def healthy():
        return None

    monkeypatch.setattr(sys.modules["controller"], "probe_health", healthy)
    engine = OfflineEngine(root, Capacity(tmp_path / "native.lock"))
    result = await run_case(tmp_path, "portrait", engine)
    assert result["passed"] and result["storage_bytes"] > 0
    assert (
        result["output_sha256"]
        == hashlib.sha256((root / "output/image.png").read_bytes()).hexdigest()
    )
    assert "not established" in result["quality_acceptance"]
    with pytest.raises(FileNotFoundError):
        reserve(tmp_path, "background")


def test_reference_descriptor_rejects_unknown_fields(tmp_path):
    root, request = job(tmp_path, "edit")
    request["reference"]["user_filename"] = "synthetic-extra.png"
    (root / "request.json").write_text(json.dumps(request))
    (root / "inputs/reference.json").write_text(json.dumps(request["reference"]))
    code, events, _ = finish(spawn(root))
    assert code != 0 and events == [{"type": "failed"}]
    assert not (root / "fake-call.json").exists()
