"""PE0 control adapter; reuses production lease, admission and owned reaping."""

import asyncio
import hashlib
import json
import os
from pathlib import Path

import httpx

from app.images.engine import Engine


class PlannedCancellation(Exception):
    pass


class EditEngine(Engine):
    async def admit(self):
        rows = await self.loaded()
        spec = json.loads(Path(__file__).with_name("trial.json").read_text())["required_chat"]
        if (
            len(rows) != 1
            or rows[0].get("digest") != spec["digest"]
            or rows[0].get("context_length") != spec["context_length"]
            or not self.qualified(rows)
        ):
            raise ValueError("PE0 requires the declared qualified chat residency")

    async def owned_run(self, manifest, output, *, cancel_at_step=None):
        if self.capacity is None:
            raise ValueError("PE0 requires the shared capacity lease")
        observed = []

        async def progress(event):
            observed.append(event)
            if event.get("type") == "denoising" and event.get("completed_steps") == cancel_at_step:
                raise PlannedCancellation()

        async with self.capacity.lease():
            # Engine.run's cancellation/failure path reaps before this lease exits.
            await self.run(manifest, output, progress)
            if not observed or observed[-1].get("type") != "finished":
                raise ValueError("Missing terminal event")
            if [e.get("completed_steps") for e in observed if e["type"] == "denoising"] != [
                0,
                1,
                2,
                3,
                4,
            ]:
                raise ValueError("Incomplete actual-step progress")
        return observed


async def health_guard(run, probe):
    """Stop the owned task through normal reaping if app responsiveness fails."""
    try:
        while not run.done():
            await probe()
            await asyncio.sleep(1)
    except BaseException:
        run.cancel()
        await asyncio.gather(run, return_exceptions=True)
        raise


async def probe_health():
    async with httpx.AsyncClient(timeout=2, trust_env=False) as client:
        response = await client.get("http://127.0.0.1:8787/api/health")
        response.raise_for_status()
        if response.json().get("ok") is not True or response.elapsed.total_seconds() > 2:
            raise ValueError("Application responsiveness bound failed")


def require_approval(root, sources):
    """Operator receipt only; an absent receipt always refuses native execution.

    A receipt records explicit human approval; creating one is not authorization.
    Offline preparation never creates it or calls a worker through this adapter.
    """
    receipt = json.loads((root / "approval.json").read_text())
    expected = {str(path.name): hashlib.sha256(path.read_bytes()).hexdigest() for path in sources}
    if receipt.get("approved_sources") != expected or receipt.get("maximum_invocations") != 6:
        raise ValueError("Approval does not match the frozen six-invocation scope")
    return receipt


def reserve(root, case_id):
    """Append-only ordered attempts; even failed admission cannot be retried."""
    here = Path(__file__).parent
    sources = [here / name for name in ("contracts.py", "worker.py", "controller.py", "trial.json")]
    require_approval(root, sources)
    plan = json.loads((here / "trial.json").read_text())
    cases = plan["cases"]
    index = next(i for i, case in enumerate(cases) if case["id"] == case_id)
    attempts = root / "attempts"
    attempts.mkdir(mode=0o700, exist_ok=True)
    existing = sorted(attempts.glob("*.reserved.json"))
    if len(existing) != index or len(existing) >= 6:
        raise ValueError("Wrong order, stopped attempt or exhausted budget")
    for previous in cases[:index]:
        outcome = json.loads((attempts / (previous["id"] + ".result.json")).read_text())
        if outcome.get("passed") is not True:
            raise ValueError("Prior required gate failed")
        if previous["id"] != "cancel":
            quality = json.loads((attempts / (previous["id"] + ".quality.json")).read_text())
            if (
                quality.get("continue") is not True
                or not quality.get("reviewer")
                or quality.get("output_sha256") != outcome.get("output_sha256")
            ):
                raise ValueError("Prior image needs a passing visual review")
    case = cases[index]
    frozen = next(c for c in cases if c["id"] == case.get("same_request_as", case_id))
    job = root / "cases" / case_id
    request = json.loads((job / "request.json").read_text())
    if any(
        request.get(key) != value
        for key, value in {
            "prompt": frozen["prompt"],
            "mode": frozen["mode"],
            "seed": 42,
        }.items()
    ):
        raise ValueError("Request differs from declared trial")
    if request["mode"] == "edit":
        if case_id == "mug":
            origin = frozen["original_sha256"]
        else:
            portrait = root / "cases/portrait/output/image.png"
            origin = hashlib.sha256(portrait.read_bytes()).hexdigest()
        if case_id == "clothing":
            derivative = json.loads((job / "inputs/derivative.json").read_text())
            if derivative != {"source_sha256": origin, "operation": frozen["reference"]}:
                raise ValueError("Non-square derivative provenance differs")
            if request["reference"]["dimensions"] != [768, 1024]:
                raise ValueError("Non-square orientation fixture differs")
        elif request.get("reference", {}).get("original_sha256") != origin:
            raise ValueError("Reference differs from declared original")
    reservation = attempts / f"{index + 1:02}-{case_id}.reserved.json"
    with reservation.open("x") as handle:
        json.dump(
            {
                "case": case_id,
                "request_sha256": hashlib.sha256((job / "request.json").read_bytes()).hexdigest(),
            },
            handle,
        )
        handle.flush()
        os.fsync(handle.fileno())
    return job, request, attempts / (case_id + ".result.json")


async def run_case(root, case_id, engine):
    """One approved call, with a permanent result and no automatic continuation."""
    job, request, outcome = reserve(root, case_id)
    run = asyncio.create_task(
        engine.owned_run(
            job / "request.json",
            job / "output",
            cancel_at_step=1 if case_id == "cancel" else None,
        )
    )
    monitor = asyncio.create_task(health_guard(run, probe_health))
    result = {
        "case": case_id,
        "passed": False,
        "quality_acceptance": "not established by protocol checks",
    }
    try:
        done, _ = await asyncio.wait({run, monitor}, return_when=asyncio.FIRST_COMPLETED)
        if monitor in done:
            await monitor
        await run
        metadata = json.loads((job / "output/metadata.json").read_text())
        spec = json.loads(Path(__file__).with_name("trial.json").read_text())
        if (
            metadata.get("sha256")
            != hashlib.sha256((job / "output/image.png").read_bytes()).hexdigest()
            or metadata.get("mode") != request["mode"]
            or metadata.get("reference") != request.get("reference")
            or metadata.get("prompt") != request["prompt"]
            or metadata.get("seed") != request["seed"]
            or metadata.get("model") != spec["model"]
            or metadata.get("revision") != spec["revision"]
            or metadata.get("generate_seconds", 61) > 60
            or metadata.get("mlx_peak_bytes", 25 * 1024**3) > 24 * 1024**3
        ):
            raise ValueError("Output contract failed")
        result.update(passed=True, output_sha256=metadata["sha256"])
    except PlannedCancellation:
        if case_id != "cancel" or (job / "output/image.png").exists():
            raise
        result.update(passed=True, planned_cancellation=True)
    except BaseException as error:
        result["failure_type"] = type(error).__name__
        raise
    finally:
        run.cancel()
        monitor.cancel()
        await asyncio.gather(run, monitor, return_exceptions=True)
        result["storage_bytes"] = sum(p.stat().st_size for p in job.rglob("*") if p.is_file())
        with outcome.open("x") as stream:
            json.dump(result, stream, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
    return result
