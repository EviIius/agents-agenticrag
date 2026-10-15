"""One approved current-profile image residency check; output must stay private."""

import argparse
import asyncio
import hashlib
import json
import plistlib
import sqlite3
import sys
import time
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "server"))
from app.capacity import Capacity  # noqa: E402
from app.images.engine import Engine  # noqa: E402
from app.images.files import validate  # noqa: E402

DIGEST = "09386c7af8487c073bfb845833462d30d0d48ad69428c301b909dc159c028b0a"
PROMPT = (
    "A realistic photograph of a red ceramic mug on a wooden table beside a closed blue notebook, "
    "morning window light, no people."
)
BASE = Path.home() / ".local/share/workbench"


async def main(output: Path) -> None:
    output = output.expanduser().resolve()
    if not output.is_relative_to(BASE / "qa") or output.exists():
        raise RuntimeError("Choose a new private QA directory; no overwrite/retry")
    output.mkdir(mode=0o700, parents=True)
    record = {
        "passed": False,
        "native_calls": 0,
        "text_calls": 0,
        "started_at": datetime.now(UTC).isoformat(),
        "expected_digest": DIGEST,
        "source_files": {
            name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
            for name in [
                "server/app/images/engine.py",
                "server/app/workflows/qualification.py",
                "scripts/probe_image_residency.py",
            ]
        },
    }
    service = plistlib.loads(
        (Path.home() / "Library/LaunchAgents/dev.agenticrag.workbench.plist").read_bytes()
    )
    home = Path(service["EnvironmentVariables"]["WORKBENCH_IMAGE_HOME"])
    capacity = Capacity(BASE / "data/native.lock")
    engine = Engine(home, capacity)
    python, worker, model = engine.paths()
    record["worker_sha256"] = hashlib.sha256(worker.read_bytes()).hexdigest()
    assert worker.read_bytes() == (ROOT / "image_worker/product/worker.py").read_bytes()
    request = {"prompt": PROMPT, "seed": 42}
    manifest = output / "manifest.json"
    manifest.write_text(json.dumps(request, indent=2) + "\n")
    scratch = output / "output"
    scratch.mkdir(mode=0o700)
    samples, events = [], []
    started = time.monotonic()
    baseline = await engine.swap()
    record["baseline_swap_mib"] = baseline

    async with httpx.AsyncClient(timeout=3, trust_env=False) as client:

        async def sample() -> dict:
            stamp = time.monotonic()
            response = await client.get("http://127.0.0.1:8787/api/health")
            response.raise_for_status()
            health_seconds = time.monotonic() - stamp
            assert response.json()["ok"] and health_seconds <= 2
            response = await client.get("http://127.0.0.1:11434/api/ps")
            response.raise_for_status()
            models = response.json()["models"]
            assert len(models) == 1
            row = models[0]
            assert row["digest"] == DIGEST and row["context_length"] == 32768
            assert type(row["size_vram"]) is int and 0 < row["size_vram"] <= 21827095100
            swap = await engine.swap()
            assert swap - baseline <= 512
            data = {
                "seconds": time.monotonic() - started,
                "health_seconds": health_seconds,
                "swap_mib": swap,
                "digest": row["digest"],
                "context_length": row["context_length"],
                "resident_bytes": row["size_vram"],
            }
            samples.append(data)
            return data

        async def progress(event: dict) -> None:
            events.append({"seconds": time.monotonic() - started, **event})
            await sample()

        async def monitor() -> None:
            while True:
                await asyncio.sleep(1)
                await sample()

        try:
            response = await client.get("http://127.0.0.1:8787/api/runs/active")
            response.raise_for_status()
            assert not response.json(), "Chat is active; no image started"
            with closing(
                sqlite3.connect((BASE / "data/workbench.db").as_uri() + "?mode=ro", uri=True)
            ) as db:
                assert (
                    db.execute(
                        "SELECT count(*) FROM image_jobs "
                        "WHERE state IN ('queued','preparing','running','cancelling')"
                    ).fetchone()[0]
                    == 0
                )
                assert (
                    db.execute(
                        "SELECT count(*) FROM workflow_graph_runs "
                        "WHERE state IN ('queued','running')"
                    ).fetchone()[0]
                    == 0
                )
            await sample()
            async with asyncio.timeout(120), capacity.lease(background=True):
                await sample()
                record["native_calls"] = 1
                async with asyncio.TaskGroup() as group:
                    watching = group.create_task(monitor())
                    code = await engine.run(manifest, scratch, progress)
                    watching.cancel()
                assert code == 0
            await sample()
            digest, image_bytes, metadata_bytes = validate(scratch, request)
            details = json.loads((scratch / "metadata.json").read_text())
            assert details["generate_seconds"] <= 60
            assert details["mlx_peak_bytes"] <= 24 * 1024**3
            assert events[-1]["type"] == "finished"
            assert any(e.get("completed_steps") == 4 for e in events)
            assert not capacity.busy and capacity.fd is None
            record.update(
                passed=True,
                elapsed_seconds=time.monotonic() - started,
                generation_seconds=details["generate_seconds"],
                mlx_peak_bytes=details["mlx_peak_bytes"],
                image_sha256=digest,
                image_bytes=image_bytes,
                metadata_bytes=metadata_bytes,
                maximum_swap_growth_mib=max(s["swap_mib"] - baseline for s in samples),
                maximum_health_seconds=max(s["health_seconds"] for s in samples),
                worker_reaped=True,
                capacity_released=True,
                resident_before_during_after=True,
            )
        except BaseException as exc:
            record["error_type"] = type(exc).__name__
            raise
        finally:
            record["samples"] = samples
            record["events"] = events
            (output / "result.json").write_text(json.dumps(record, indent=2) + "\n")
            print(
                json.dumps(
                    {
                        k: record.get(k)
                        for k in [
                            "passed",
                            "native_calls",
                            "text_calls",
                            "elapsed_seconds",
                            "generation_seconds",
                            "maximum_swap_growth_mib",
                            "error_type",
                        ]
                    }
                )
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    asyncio.run(main(args.output))
