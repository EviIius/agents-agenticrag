"""Short-lived existing-image-interpreter CPU codec; cancellation owns its child."""

import asyncio
import json
from pathlib import Path
from typing import Any

from ..errors import AppError
from .engine import Engine


class ReferenceCodec:
    def __init__(self, home: Path | None) -> None:
        self.home = home.expanduser().resolve() if home else None
        self.slots = asyncio.Semaphore(2)
        self.processes: set[asyncio.subprocess.Process] = set()

    async def normalize(self, folder: Path) -> dict[str, Any]:
        child = None
        async with self.slots:
            try:
                if not self.home:
                    raise ValueError("Codec unavailable")
                python = Path((self.home / ".python").read_text().strip())
                codec = self.home / "reference_codec.py"
                if not codec.is_file() or not python.is_file():
                    raise ValueError("Codec unavailable")
                spawning = asyncio.create_task(
                    asyncio.create_subprocess_exec(
                        str(python),
                        str(codec),
                        str(folder),
                        stdin=asyncio.subprocess.PIPE,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.DEVNULL,
                        start_new_session=True,
                        limit=32768,
                        env={
                            "PATH": "/usr/bin:/bin",
                            "HF_HUB_OFFLINE": "1",
                            "TRANSFORMERS_OFFLINE": "1",
                        },
                    )
                )
                try:
                    child = await asyncio.shield(spawning)
                except asyncio.CancelledError:
                    child = await spawning
                    raise
                self.processes.add(child)

                async def collect() -> bytes:
                    assert child is not None and child.stdout is not None
                    raw = await child.stdout.readline()
                    if await child.stdout.read(1):
                        raise ValueError("Unexpected codec output")
                    await child.wait()
                    return raw

                raw = await asyncio.wait_for(collect(), 20)
                if child.returncode or len(raw) > 32768:
                    raise ValueError("Invalid codec response")
                result: dict[str, Any] = json.loads(raw)
                if not isinstance(result, dict):
                    raise ValueError("Invalid codec response")
                return result
            except (OSError, ValueError, TimeoutError):
                raise AppError(
                    "image_unreadable",
                    "Couldn't prepare this photo. Use a PNG or JPEG and try again.",
                    422,
                ) from None
            finally:
                if child:
                    stopping = asyncio.create_task(Engine.stop(child))
                    try:
                        await asyncio.shield(stopping)
                    except asyncio.CancelledError:
                        await stopping
                        raise
                    finally:
                        if child.stdin:
                            child.stdin.close()
                        self.processes.discard(child)

    async def close(self) -> None:
        await asyncio.gather(*(Engine.stop(child) for child in list(self.processes)))
        for child in self.processes:
            if child.stdin:
                child.stdin.close()
