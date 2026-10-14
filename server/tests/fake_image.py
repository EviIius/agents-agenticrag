"""Synthetic image engine for the browser fixture server only."""

import asyncio
import json
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

from app.schemas import ImageStatus
from tests.test_images import output


class FakeImageEngine:
    def __init__(self) -> None:
        self.failed_once: set[tuple[str, int]] = set()
        self.release = asyncio.Event()

    def status(self) -> ImageStatus:
        return ImageStatus(available=True)

    async def run(
        self,
        manifest: Path,
        scratch: Path,
        progress: Callable[[dict[str, Any]], Awaitable[None]],
    ) -> int:
        expected = json.loads(manifest.read_text())
        await asyncio.sleep(0.1)
        key = (expected["prompt"], expected["seed"])
        if "#fail-once" in expected["prompt"] and key not in self.failed_once:
            self.failed_once.add(key)
            raise ValueError("Synthetic failure")
        if "#fail" in expected["prompt"] and "#fail-once" not in expected["prompt"]:
            raise ValueError("Synthetic failure")
        for i in range(4):
            await progress({"type": "denoising", "completed_steps": i + 1})
            if "#pause-step" in expected["prompt"] and i == 1:
                await self.release.wait()
            await asyncio.sleep(
                1
                if "#restart" in expected["prompt"]
                else 0.4
                if "#slow" in expected["prompt"]
                else 0.02
            )
        await progress({"type": "decoding"})
        output(scratch, expected)
        return 0
