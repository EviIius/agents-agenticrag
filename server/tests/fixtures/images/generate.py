"""Regenerate the synthetic 32 x 16 gradient; never reads personal images."""

import struct
import subprocess
import zlib
from pathlib import Path


def chunk(kind: bytes, payload: bytes) -> bytes:
    return (
        struct.pack(">I", len(payload))
        + kind
        + payload
        + struct.pack(">I", zlib.crc32(kind + payload))
    )


if __name__ == "__main__":
    folder = Path(__file__).parent
    pixels = b"".join(
        b"\0" + bytes(value for x in range(32) for value in (x * 8, y * 16, 96)) for y in range(16)
    )
    png = folder / "fake-synthetic.png"
    png.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", 32, 16, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(pixels))
        + chunk(b"IEND", b"")
    )
    subprocess.run(
        [
            "/usr/bin/sips",
            "-s",
            "format",
            "heic",
            str(png),
            "--out",
            str(folder / "fake-synthetic.heic"),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
    )
