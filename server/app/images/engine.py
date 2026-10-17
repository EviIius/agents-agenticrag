"""Private subprocess boundary. Disconnects cannot release a native lease."""

import asyncio
import json
import os
import re
import signal
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

import httpx

from ..capacity import Capacity
from ..errors import AppError
from ..schemas import ImageStatus
from .files import REVISION

# A measured combination, identified by runtime digest/context/size, not its name.
QUALIFIED_DIGEST = "f8a791a5edd0075fb64ff3bd94a3140bfa791992db1bdda0daac587f2b6afbcb"
# Candidate extension: promote only after its separately reviewed memory probe.
# Exact runtime identities; aliases do not change admission or memory limits.
QUALIFIED_DIGESTS = (
    QUALIFIED_DIGEST,
    "09386c7af8487c073bfb845833462d30d0d48ad69428c301b909dc159c028b0a",
)


class Engine:
    def __init__(self, home: Path | None, capacity: Capacity | None = None) -> None:
        self.home = home.expanduser().resolve() if home else None
        self.capacity = capacity

    def paths(self) -> tuple[Path, Path, Path]:
        if not self.home:
            raise ValueError("Image worker is not configured")
        python = Path((self.home / ".python").read_text().strip())
        model = Path(json.loads((self.home / "config.json").read_text())["model_path"])
        worker = self.home / "worker.py"
        if not python.is_file() or not os.access(python, os.X_OK) or not worker.is_file():
            raise ValueError("Image worker is unavailable")
        if not model.is_dir() or model.name != REVISION:
            raise ValueError("Pinned model snapshot is unavailable")
        return python, worker, model

    def status(self) -> ImageStatus:
        try:
            self.paths()
            return ImageStatus(available=True)
        except (OSError, ValueError, KeyError, TypeError):
            return ImageStatus(
                available=False,
                reason="The local image worker is not installed or its pinned model is missing.",
            )

    async def admit(self) -> None:
        async with httpx.AsyncClient(timeout=5, trust_env=False) as client:
            try:
                response = await client.get("http://127.0.0.1:11434/api/ps")
                response.raise_for_status()
                models = response.json()["models"]
            except (httpx.HTTPError, ValueError, KeyError) as exc:
                raise AppError(
                    "image_capacity",
                    "Cannot verify loaded models. Retry when Ollama is reachable.",
                    409,
                ) from exc
        if not isinstance(models, list) or any(not isinstance(row, dict) for row in models):
            raise AppError(
                "image_capacity",
                "Invalid loaded-model report. Retry when Ollama is reachable.",
                409,
            )
        # No implicit unload, load, keep-alive refresh or model-name heuristic.
        if (
            any(
                row.get("digest") not in QUALIFIED_DIGESTS
                or row.get("context_length") != 32768
                or not isinstance(row.get("size_vram"), int)
                or not 0 < row["size_vram"] <= 21827095100
                for row in models
            )
            or len(models) > 1
        ):
            raise AppError(
                "image_capacity",
                "A loaded model combination is not qualified for images. "
                "Open Settings → Models and eject other loaded models, including Library/search "
                "embedding models, or retry after they expire. Nothing was unloaded.",
                409,
            )

    async def swap(self) -> float:
        child = await asyncio.create_subprocess_exec(
            "/usr/sbin/sysctl",
            "-n",
            "vm.swapusage",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
        )
        raw, _ = await child.communicate()
        match = re.search(rb"used = ([0-9.]+)M", raw)
        if child.returncode or not match:
            raise AppError("image_resource", "Cannot measure host swap safely.", 409)
        return float(match[1])

    async def run(
        self, manifest: Path, scratch: Path, progress: Callable[[dict[str, Any]], Awaitable[None]]
    ) -> int:
        python, worker, model = self.paths()
        await self.admit()
        baseline = await self.swap()
        assert self.home is not None
        child = await asyncio.create_subprocess_exec(
            str(python),
            str(worker),
            str(manifest),
            str(model),
            str(scratch),
            cwd=self.home,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
            start_new_session=True,
            env={
                "HOME": str(Path.home()),
                "PATH": "/usr/bin:/bin",
                "HF_HUB_OFFLINE": "1",
                "TRANSFORMERS_OFFLINE": "1",
                "TOKENIZERS_PARALLELISM": "false",
            },
            limit=32768,
            # Child inherits the SAME lock description. A crashed server cannot
            # admit another native call until the old worker has exited.
            pass_fds=(self.capacity.fd,) if self.capacity and self.capacity.fd is not None else (),
        )

        async def consume() -> None:
            assert child.stdout is not None
            while line := await child.stdout.readline():
                event = json.loads(line)
                if not isinstance(event, dict) or event.get("type") not in {
                    "initializing",
                    "denoising",
                    "decoding",
                    "finished",
                    "failed",
                }:
                    raise ValueError("Invalid worker event")
                await progress(event)

        async def guard() -> None:
            while True:
                await asyncio.sleep(1)
                await self.admit()
                if await self.swap() - baseline > 512:
                    raise AppError(
                        "image_resource",
                        "Image stopped because host swap exceeded the qualified margin.",
                        409,
                    )

        consuming, guarding = asyncio.create_task(consume()), asyncio.create_task(guard())
        waiting = asyncio.create_task(child.wait())
        try:
            async with asyncio.timeout(300):
                pending = {consuming, guarding, waiting}
                while not waiting.done():
                    done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)
                    for task in done:
                        await task
                    if guarding in done:
                        raise ValueError("Resource monitor ended")
                await consuming
                if child.returncode != 0:
                    raise AppError(
                        "image_worker_failed",
                        "Image worker exited before a valid output was completed. Retry this job.",
                        502,
                    )
                if await self.swap() - baseline > 512:
                    raise AppError(
                        "image_resource",
                        "Image stopped because host swap exceeded the qualified margin.",
                        409,
                    )
                return int(child.returncode)
        finally:
            # Shield reaping: task/request cancellation never frees capacity early.
            stopping = asyncio.create_task(self.stop(child))
            try:
                await asyncio.shield(stopping)
            except asyncio.CancelledError:
                await stopping
                raise
            for task in (consuming, guarding, waiting):
                task.cancel()
            await asyncio.gather(consuming, guarding, waiting, return_exceptions=True)
            if child.stdin:
                child.stdin.close()

    @staticmethod
    async def stop(child: asyncio.subprocess.Process) -> None:
        if child.returncode is None:
            try:
                os.killpg(child.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                await asyncio.wait_for(child.wait(), 5)
            except TimeoutError:
                try:
                    os.killpg(child.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
        await child.wait()
