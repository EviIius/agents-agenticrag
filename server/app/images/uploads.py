"""Bounded HEIC/HEIF decoding through the Mac's existing image codec."""

import asyncio
import re
import shutil
import tempfile
from pathlib import Path

from ..errors import AppError

IMAGE_LIMIT = 20 * 1024**2
HEIF_EXTENSIONS = {".heic", ".heif"}
HEIF_BRANDS = {b"heic", b"heix", b"hevc", b"hevx", b"heim", b"heis", b"mif1", b"msf1"}


def is_heif(data: bytes) -> bool:
    if len(data) < 16 or data[4:8] != b"ftyp":
        return False
    size = int.from_bytes(data[:4], "big")
    if size < 16:
        return False
    brands = [data[8:12], *(data[i : i + 4] for i in range(16, min(size, len(data)), 4))]
    return not any(b in {b"avif", b"avis"} for b in brands) and any(
        b in HEIF_BRANDS for b in brands
    )


def unreadable() -> AppError:
    return AppError(
        "image_unreadable",
        "Couldn't open this image. Export it as a JPEG or PNG and try again.",
        422,
    )


class ImageUploads:
    def __init__(self, timeout: float = 20) -> None:
        self.timeout = timeout
        self.capacity = asyncio.Semaphore(2)
        self.processes: set[asyncio.subprocess.Process] = set()

    def recover(self, folder: Path) -> None:
        for path in folder.glob(".image-convert-*"):
            if path.is_dir() and not path.is_symlink():
                shutil.rmtree(path)

    async def command(self, *arguments: str) -> bytes:
        process = None
        try:
            spawning = asyncio.create_task(
                asyncio.create_subprocess_exec(
                    "/usr/bin/sips",
                    *arguments,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.DEVNULL,
                )
            )
            try:
                process = await asyncio.shield(spawning)
            except asyncio.CancelledError:
                process = await spawning
                raise
            self.processes.add(process)
            output, _ = await asyncio.wait_for(process.communicate(), self.timeout)
            if process.returncode:
                raise unreadable()
            return output
        except (OSError, TimeoutError):
            raise unreadable() from None
        finally:
            if process:
                if process.returncode is None:
                    process.kill()
                await asyncio.shield(process.wait())
                self.processes.discard(process)

    async def convert(self, data: bytes, folder: Path) -> bytes:
        if len(data) > IMAGE_LIMIT:
            raise AppError("file_too_large", "Image limit is 20 MB.", 413)
        folder.mkdir(parents=True, exist_ok=True)
        async with self.capacity:
            with tempfile.TemporaryDirectory(prefix=".image-convert-", dir=folder) as temporary:
                source, target = Path(temporary) / "source.heic", Path(temporary) / "image.png"
                source.touch(mode=0o600)
                source.write_bytes(data)
                properties = await self.command(
                    "-g", "pixelWidth", "-g", "pixelHeight", str(source)
                )
                values = re.findall(rb"pixel(?:Width|Height):\s*(\d+)", properties)
                if len(values) != 2:
                    raise unreadable()
                width, height = (int(value) for value in values)
                if min(width, height) <= 0 or width * height > 100_000_000:
                    raise AppError("image_dimensions", "This image is too large to open.", 413)
                resize = ["-Z", "2048"] if max(width, height) > 2048 else []
                await self.command(
                    "-s", "format", "png", *resize, str(source), "--out", str(target)
                )
                if not target.is_file() or target.stat().st_size > IMAGE_LIMIT:
                    raise unreadable()
                with target.open("rb") as image:
                    result = image.read(IMAGE_LIMIT + 1)
                if not result.startswith(b"\x89PNG\r\n\x1a\n"):
                    raise unreadable()
                return result

    async def close(self) -> None:
        for process in list(self.processes):
            if process.returncode is None:
                process.kill()
        await asyncio.gather(*(p.wait() for p in self.processes))
