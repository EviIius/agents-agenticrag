import asyncio
import json
import re
import sys
from pathlib import Path
from typing import Any

from ..documents.extract import Extracted, error
from ..search.chunk import chunk


async def extract(source: Path, timeout: float = 30) -> Extracted:
    output = source.with_suffix(".result")
    process = None
    try:
        spawning = asyncio.create_task(
            asyncio.create_subprocess_exec(
                sys.executable,
                "-m",
                "app.library.worker",
                str(source),
                source.suffix,
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
        try:
            await asyncio.wait_for(process.wait(), timeout)
        except TimeoutError:
            raise error("document_timeout") from None
        if process.returncode or not output.is_file():
            raise error("document_unreadable")
        result = json.loads(output.read_text())
        if result.get("error"):
            raise error(result["error"])
        return Extracted(**result)
    finally:
        if process:
            if process.returncode is None:
                process.kill()
            await asyncio.shield(process.wait())
        output.unlink(missing_ok=True)


def passages(identifier: str, value: Extracted) -> list[dict[str, Any]]:
    # Chunk each PDF page independently: exact ranges cannot be lost when the
    # shared chunker merges small paragraphs or repeats table headers.
    pages: list[tuple[int | None, str]] = [(None, value.text)]
    if value.pages is not None:
        parts = re.split(r"(?m)^\[Page (\d+)\]\s*\n", value.text)
        pages = [(int(parts[i]), parts[i + 1]) for i in range(1, len(parts), 2)]
    output: list[dict[str, Any]] = []
    for page, text in pages:
        for passage in chunk(identifier, text):
            output.append(
                {
                    "ord": len(output),
                    "heading": passage.heading,
                    "text": passage.text,
                    "page_start": page,
                    "page_end": page,
                }
            )
    return output
