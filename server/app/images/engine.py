"""Private subprocess boundary. Disconnects cannot release a native lease."""

import asyncio
import json
import os
import re
import signal
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import httpx

from ..capacity import Capacity
from ..db import settings
from ..db.core import Store
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
    def __init__(
        self, home: Path | None, capacity: Capacity | None = None, store: Store | None = None
    ) -> None:
        self.home = home.expanduser().resolve() if home else None
        self.capacity = capacity
        self.store = store
        self.models_changed: Callable[[], None] | None = None

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

    async def loaded(self) -> list[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=5, trust_env=False) as client:
            try:
                response = await client.get("http://127.0.0.1:11434/api/ps")
                response.raise_for_status()
                models = response.json()["models"]
            except (httpx.HTTPError, ValueError, KeyError, TypeError) as exc:
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
        return models

    @staticmethod
    def qualified(models: list[dict[str, Any]]) -> bool:
        return not (
            any(
                row.get("digest") not in QUALIFIED_DIGESTS
                or row.get("context_length") != 32768
                or not isinstance(row.get("size_vram"), int)
                or not 0 < row["size_vram"] <= 21827095100
                for row in models
            )
            or len(models) > 1
        )

    async def admit(self) -> None:
        # Resource monitoring stays read-only; only preparation may release embeddings.
        if not self.qualified(await self.loaded()):
            raise AppError(
                "image_capacity",
                "A loaded model combination is not qualified for images. "
                "Open Settings → Models and eject other chat or unknown models, "
                "or retry after they expire.",
                409,
            )

    async def configured_embeddings(self) -> set[str]:
        if self.store is None:
            return set()
        values = await settings.get(self.store)
        names = set()
        for key in ("library.embedding", "web.embedding"):
            choice = values.get(key)
            if (
                not isinstance(choice, dict)
                or not isinstance(choice.get("connection_id"), str)
                or not isinstance(choice.get("model_id"), str)
                or not choice["model_id"]
            ):
                continue
            connection = await self.store.one(
                "SELECT base_url FROM connections WHERE id=? AND enabled=1",
                (choice.get("connection_id"),),
            )
            if connection:
                try:
                    url = urlsplit(str(connection["base_url"]))
                    port = url.port
                except ValueError:
                    continue
                if (
                    url.scheme == "http"
                    and url.hostname in {"127.0.0.1", "localhost", "::1"}
                    and port == 11434
                    and url.path in {"", "/"}
                    and not url.username
                    and not url.password
                    and not url.query
                    and not url.fragment
                    and isinstance(choice.get("model_id"), str)
                ):
                    names.add(choice["model_id"])
        return names

    async def prepare_memory(self, progress: Callable[[dict[str, Any]], Awaitable[None]]) -> None:
        models = await self.loaded()
        if self.qualified(models):
            return
        allowed = await self.configured_embeddings()
        candidates = [
            row for row in models if isinstance(row.get("name"), str) and row["name"] in allowed
        ]
        remaining = [row for row in models if row not in candidates]
        # No partial eviction if another chat/unknown profile would still block images.
        if not candidates or not self.qualified(remaining):
            await self.admit()
            return
        if self.capacity is None or not self.capacity.busy:
            raise AppError("image_capacity", "Image preparation needs the shared model slot.", 409)

        # Bind release to this exact residency snapshot, not a name or capability guess.
        def snapshot(rows: list[dict[str, Any]]) -> dict[str, tuple[Any, ...]]:
            result = {}
            for row in rows:
                name = row.get("name")
                if not isinstance(name, str) or not name or name in result:
                    raise ValueError("Invalid residency identity")
                result[name] = (row.get("digest"), row.get("context_length"), row.get("size_vram"))
            return result

        attempted = False
        try:
            original = snapshot(models)
            planned = {row["name"]: original[row["name"]] for row in candidates}
            async with httpx.AsyncClient(timeout=5, trust_env=False) as client:
                for row in candidates:
                    response = await client.post(
                        "http://127.0.0.1:11434/api/show", json={"model": row["name"]}
                    )
                    response.raise_for_status()
                    metadata = response.json()
                    caps = metadata.get("capabilities") if isinstance(metadata, dict) else None
                    # Some embedding-only architectures also report auxiliary flags.
                    # Completion support (or unknown capabilities) is never eligible.
                    if (
                        not isinstance(caps, list)
                        or "embedding" not in caps
                        or any(cap not in ("embedding", "tools", "thinking") for cap in caps)
                    ):
                        raise AppError(
                            "image_capacity",
                            "Another loaded model needs an explicit choice in Settings → Models "
                            "before images can start. Nothing was unloaded.",
                            409,
                        )
                response = await client.get("http://127.0.0.1:11434/api/tags")
                response.raise_for_status()
                tags = response.json()["models"]
                if not isinstance(tags, list) or any(not isinstance(row, dict) for row in tags):
                    raise ValueError("Invalid model identities")
                for name, identity in planned.items():
                    matches = [row for row in tags if row.get("name") == name]
                    if (
                        len(matches) != 1
                        or not isinstance(identity[0], str)
                        or not identity[0]
                        or matches[0].get("digest") != identity[0]
                    ):
                        raise ValueError("Embedding alias changed")
                if snapshot(await self.loaded()) != original:
                    raise ValueError("Loaded configuration changed")
                await progress({"type": "releasing_embeddings"})
                for row in candidates:
                    # The job owns Capacity already; adapter.unload() would acquire it twice.
                    try:
                        attempted = True
                        response = await client.post(
                            "http://127.0.0.1:11434/api/chat",
                            json={
                                "model": row["name"],
                                "messages": [],
                                "keep_alive": 0,
                                "stream": False,
                            },
                        )
                        response.raise_for_status()
                        acknowledgement = response.json()
                        if (
                            not isinstance(acknowledgement, dict)
                            or acknowledgement.get("done") is not True
                            or acknowledgement.get("done_reason") != "unload"
                        ):
                            raise ValueError("Missing unload acknowledgement")
                    finally:
                        if self.models_changed:
                            self.models_changed()
                # Ollama acknowledges expiry before asynchronous VRAM release completes.
                # Bounded resource verification; the UI still receives push/SSE progress.
                async with asyncio.timeout(5):
                    while True:
                        current = await self.loaded()
                        current_snapshot = snapshot(current)
                        if any(
                            name not in original or original[name] != identity
                            for name, identity in current_snapshot.items()
                        ):
                            raise ValueError("Unexpected loaded configuration")
                        if self.qualified(current):
                            break
                        await asyncio.sleep(0.1)
            await self.admit()
        except (httpx.HTTPError, ValueError, KeyError, TypeError, TimeoutError, AppError) as exc:
            raise AppError(
                "image_capacity",
                "Couldn’t finish freeing memory for images. Retry this image."
                if attempted
                else "Couldn’t safely prepare memory for images. Nothing was unloaded. "
                "Check Settings → Models and retry.",
                409,
            ) from exc

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
        if self.store is not None:
            await self.prepare_memory(progress)
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
