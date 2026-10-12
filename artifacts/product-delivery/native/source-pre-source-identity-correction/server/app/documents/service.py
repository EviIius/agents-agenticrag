"""Two supervised workers; a timed-out/cancelled worker ends before capacity is released."""

import asyncio
import json
import sys
from pathlib import Path

from .extract import ERRORS, Extracted, error


class Extractor:
    def __init__(self, concurrency: int = 2, timeout: float = 30) -> None:
        self.capacity = asyncio.Semaphore(concurrency)
        self.timeout = timeout
        self.processes: set[asyncio.subprocess.Process] = set()

    def recover(self, folder: Path) -> None:
        # Only interrupted document uploads/results; completed text and audio stay intact.
        for pattern in ("*.pdf.part", "*.docx.part", "*.txt.part", "*.pdf.result", "*.docx.result"):
            for path in folder.glob(pattern):
                path.unlink(missing_ok=True)

    async def extract(self, source: Path, suffix: str) -> Extracted:
        output = source.with_suffix(".result")
        process = None
        async with self.capacity:
            try:
                spawning = asyncio.create_task(
                    asyncio.create_subprocess_exec(
                        sys.executable,
                        "-m",
                        "app.documents.worker",
                        str(source),
                        suffix,
                        str(output),
                        cwd=Path(__file__).resolve().parents[2],
                        stdout=asyncio.subprocess.DEVNULL,
                        stderr=asyncio.subprocess.DEVNULL,
                    )
                )
                try:
                    process = await asyncio.shield(spawning)
                except asyncio.CancelledError:
                    process = await spawning
                    raise
                self.processes.add(process)
                try:
                    await asyncio.wait_for(process.wait(), self.timeout)
                except TimeoutError:
                    raise error("document_timeout") from None
                if process.returncode or not output.is_file():
                    raise error("document_unreadable")
                result = json.loads(output.read_text())
                if result.get("error"):
                    raise error(
                        result["error"] if result["error"] in ERRORS else "document_unreadable"
                    )
                return Extracted(**result)
            finally:
                if process:
                    if process.returncode is None:
                        process.kill()
                    await asyncio.shield(process.wait())
                    self.processes.discard(process)
                output.unlink(missing_ok=True)

    async def close(self) -> None:
        for process in list(self.processes):
            if process.returncode is None:
                process.kill()
        await asyncio.gather(*(p.wait() for p in self.processes))
