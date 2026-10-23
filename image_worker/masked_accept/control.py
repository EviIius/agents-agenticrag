"""Single-invocation acceptance control: shared lease, strict budget, event stream and owned reaping."""

import asyncio
import hashlib
import json
import os
from pathlib import Path
from time import monotonic

from app.images.engine import Engine
from app.images.files import sanitize_export, validate_png
from app.images.storage import StorageMeter


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def new_json(path, value):
    with path.open("x") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


async def empty(engine):
    if await engine.loaded() != []:
        raise ValueError(
            "The comparison requires an empty model slot; nothing was unloaded"
        )
    await engine.healthy()


async def run_case(root, case, capacity, engine, codec):
    pair = json.loads((root / "worker/pair.json").read_text())
    if case not in pair["order"]:
        raise ValueError("Undeclared case")
    spec = pair["engines"][case]
    limits = spec["limits"]
    frozen = json.loads((root / "frozen.json").read_text())
    if digest(Path(__file__)) != digest(root / "worker/control.py"):
        raise ValueError("Controller differs from the frozen executed source")
    approval = json.loads((root / "approval.json").read_text())
    if approval.get("maximum_native_invocations") != 1 or approval.get(
        "frozen_sha256"
    ) != digest(root / "frozen.json"):
        raise ValueError("Approval receipt does not bind the frozen scope")
    for name, expected in frozen["files"].items():
        if digest(root / name) != expected:
            raise ValueError("Executed source/input changed after freezing")
    for name, expected in frozen.get("engine_files", {}).items():
        if digest(Path(name)) != expected:
            raise ValueError("Installed engine source changed after freezing")
    attempts = root / "attempts"
    attempts.mkdir(mode=0o700, exist_ok=True)
    index = pair["order"].index(case)
    if len(list(attempts.glob("*.reserved.json"))) != index:
        raise ValueError("Prior failure, wrong order or exhausted allowance")
    job = root / case
    request = json.loads((job / "input.json").read_text())
    output = job / "working"
    output.mkdir(mode=0o700, exist_ok=False)
    snapshot = Path(json.loads((root / "model-locations.json").read_text())[case])
    result = {
        "case": case,
        "passed": False,
        "quality": "pending separate visual review",
    }
    meter, events, health = StorageMeter(job), [], []
    child = None
    started = monotonic()
    tasks = []
    try:
        async with capacity.lease(background=True):
            await empty(engine)
            baseline = await engine.swap()
            # Reserve durably before launch. Any failed invocation consumes this slot.
            new_json(
                attempts / f"{index + 1:02}-{case}.reserved.json",
                {
                    "case": case,
                    "request_sha256": digest(job / "input.json"),
                    "worker_sha256": digest(root / "worker" / spec["worker"]),
                },
            )
            state = {"initialized": None, "failed": False}
            python = (root / "worker/.python").read_text().strip()
            spawning = asyncio.create_task(
                asyncio.create_subprocess_exec(
                    python,
                    str(root / "worker" / spec["worker"]),
                    str(job / "input.json"),
                    str(snapshot),
                    str(output),
                    cwd=root / "worker",
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.DEVNULL,
                    start_new_session=True,
                    pass_fds=(capacity.fd,),
                    limit=32768,
                    env={
                        "HOME": str(Path.home()),
                        "PATH": "/usr/bin:/bin",
                        "HF_HUB_OFFLINE": "1",
                        "TRANSFORMERS_OFFLINE": "1",
                        "TOKENIZERS_PARALLELISM": "false",
                    },
                )
            )
            try:
                child = await asyncio.shield(spawning)
            except asyncio.CancelledError:
                child = await spawning
                await Engine.stop(child)
                raise

            async def consume():
                while raw := await child.stdout.readline():
                    event = json.loads(raw)
                    if not isinstance(event, dict) or event.get("type") not in {
                        "initializing",
                        "initialized",
                        "denoising",
                        "decoding",
                        "finished",
                        "failed",
                    }:
                        raise ValueError("Unexpected trial event")
                    event["observed_seconds"] = round(monotonic() - started, 3)
                    if event["type"] == "initialized":
                        state["initialized"] = monotonic()
                    if event["type"] == "failed":
                        state["failed"] = True
                    events.append(event)
                    # No prompt, image path or private content is echoed.
                    print(json.dumps({"case": case, **event}), flush=True)

            async def guard():
                while True:
                    sample_started = monotonic()
                    await empty(engine)
                    health.append(monotonic() - sample_started)
                    if await engine.swap() - baseline > limits["swap_growth_mib"]:
                        raise ValueError("Host swap-growth bound exceeded")
                    elapsed = monotonic() - (state["initialized"] or started)
                    bound = (
                        limits["generation_decode_seconds"]
                        if state["initialized"]
                        else limits["initialization_seconds"]
                    )
                    if elapsed > bound:
                        raise TimeoutError("Candidate stage allowance exceeded")
                    meter.sample()
                    await asyncio.sleep(0.25)

            consuming = asyncio.create_task(consume())
            guarding = asyncio.create_task(guard())
            waiting = asyncio.create_task(child.wait())
            tasks = [consuming, guarding, waiting]
            try:
                async with asyncio.timeout(limits["worker_wall_seconds"]):
                    pending = set(tasks)
                    while not waiting.done():
                        done, pending = await asyncio.wait(
                            pending, return_when=asyncio.FIRST_COMPLETED
                        )
                        for task in done:
                            await task
                        if guarding in done:
                            raise ValueError("Resource guard ended")
                    await consuming
                    if child.returncode != 0 or state["failed"]:
                        raise ValueError("Native worker failed; no retry permitted")
                    if (
                        not events
                        or events[-1]["type"] != "finished"
                        or [
                            e.get("completed_steps")
                            for e in events
                            if e["type"] == "denoising"
                        ]
                        != list(range(spec["steps"] + 1))
                    ):
                        raise ValueError("Incomplete actual-step protocol")
                    if sum(e["type"] == "initialized" for e in events) != 1:
                        raise ValueError("Missing or repeated initialization event")
                    meta = json.loads((output / "metadata.json").read_text())
                    for key in ("prompt", "reference", "selection", "seed"):
                        if meta.get(key) != request[key]:
                            raise ValueError("Output binding differs")
                    if (
                        meta.get("model") != spec["model"]
                        or meta.get("revision") != spec["revision"]
                        or meta.get("parameters") != spec["parameters"]
                    ):
                        raise ValueError("Candidate settings differ")
                    if (
                        meta.get("mlx_peak_bytes", limits["mlx_peak_bytes"] + 1)
                        > limits["mlx_peak_bytes"]
                    ):
                        raise ValueError("Candidate allocation bound exceeded")
                    for field, bound in (
                        ("initialization_seconds", limits["initialization_seconds"]),
                        ("generate_seconds", limits["generation_decode_seconds"]),
                    ):
                        value = meta.get(field)
                        if type(value) not in (int, float) or not 0 <= value <= bound:
                            raise ValueError("Candidate timing contract differs")
                    if (
                        meta.get("sha256") != digest(output / "image.png")
                        or meta.get("auxiliary_model_calls") != 0
                        or meta.get("worker_sha256")
                        != digest(root / "worker" / spec["worker"])
                    ):
                        raise ValueError("Output hash/helper count differs")
                    validate_png((output / "native.png").read_bytes(), [1024, 1024])
                    validate_png(
                        (output / "image.png").read_bytes(),
                        request["reference"]["dimensions"],
                    )
                    proof = await codec.verify_composite(job)
                    if (
                        proof["outside_changed_pixels"] != 0
                        or proof["changed_pixels"] <= 0
                    ):
                        raise ValueError("Preservation/changed-content proof failed")
                    _, export_bytes = sanitize_export(output)
                    result.update(
                        passed=True,
                        output_sha256=meta["sha256"],
                        seconds=round(monotonic() - started, 3),
                        initialization_seconds=meta["initialization_seconds"],
                        generate_seconds=meta["generate_seconds"],
                        mlx_peak_bytes=meta["mlx_peak_bytes"],
                        quantization=meta["quantization"],
                        protected_pixels=proof["protected_pixels"],
                        outside_changed_pixels=0,
                        changed_pixels=proof["changed_pixels"],
                        dimensions=request["reference"]["dimensions"],
                        native_bytes=meta["native_bytes"],
                        composite_bytes=(output / "image.png").stat().st_size,
                        export_bytes=export_bytes,
                    )
            finally:
                stopping = asyncio.create_task(Engine.stop(child))
                try:
                    await asyncio.shield(stopping)
                except asyncio.CancelledError:
                    await stopping
                    raise
                for task in tasks:
                    task.cancel()
                await asyncio.gather(*tasks, return_exceptions=True)
                if child.stdin:
                    child.stdin.close()
                result["worker_reaped"] = child.returncode is not None
                result["swap_growth_mib"] = await engine.swap() - baseline
                await empty(engine)
                if result["swap_growth_mib"] > limits["swap_growth_mib"]:
                    result["passed"] = False
                    raise ValueError("Final swap-growth guard failed")
    except BaseException as error:
        result["passed"] = False
        result["failure_type"] = type(error).__name__
        raise
    finally:
        meter.sample()
        result["storage"] = meter.report()
        result["events"] = events
        result["maximum_health_guard_seconds"] = max(health, default=None)
        result["model_invocations_reserved"] = len(
            list(attempts.glob("*.reserved.json"))
        )
        new_json(attempts / f"{case}.result.json", result)
    return result
