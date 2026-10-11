"""Synthetic image engine for the browser fixture server only."""

import asyncio
import json
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

from app.schemas import ImageStatus
from tests.test_images import output


class FakeImageEngine:
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
        if "#fail" in expected["prompt"]:
            raise ValueError("Synthetic failure")
        for i in range(4):
            await progress({"type": "denoising", "completed_steps": i + 1})
            await asyncio.sleep(0.4 if "#slow" in expected["prompt"] else 0.02)
        await progress({"type": "decoding"})
        output(scratch, expected)
        return 0
