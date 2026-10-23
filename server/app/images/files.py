"""Private atomic files; bounded PNG validation without another server package."""

import hashlib
import json
import os
import struct
import zlib
from pathlib import Path
from typing import Any

MODEL = "black-forest-labs/FLUX.2-klein-4B"
REVISION = "e7b7dc27f91deacad38e78976d1f2b499d76a294"


def sync_directory(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def atomic_json(path: Path, value: object) -> None:
    part = path.with_suffix(".part")
    with part.open("x") as handle:
        os.chmod(part, 0o600)
        json.dump(value, handle, indent=2)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(part, path)
    sync_directory(path.parent)


def validate(folder: Path, expected: dict[str, Any]) -> tuple[str, int, int]:
    image, metadata = folder / "image.png", folder / "metadata.json"
    if image.is_symlink() or metadata.is_symlink():
        raise ValueError("Invalid output paths")
    size, meta_size = image.stat().st_size, metadata.stat().st_size
    if not 50 <= size <= 32 * 1024**2 or not 2 <= meta_size <= 32768:
        raise ValueError("Invalid output sizes")
    raw = image.read_bytes()
    dimensions = expected["reference"]["dimensions"] if expected.get("selection") else [1024, 1024]
    if (
        not isinstance(dimensions, list)
        or len(dimensions) != 2
        or any(type(n) is not int or not 1 <= n <= 2048 for n in dimensions)
    ):
        raise ValueError("Invalid expected dimensions")
    validate_png(raw, dimensions)
    digest = hashlib.sha256(raw).hexdigest()
    details = json.loads(metadata.read_text())
    for key, value in {
        **expected,
        "requested_seed": expected["seed"],
        "width": dimensions[0],
        "height": dimensions[1],
        "steps": 4,
        "guidance": 1.0,
        "quantization": 8,
        "cache_limit_bytes": 1073741824,
        "model": MODEL,
        "revision": REVISION,
        "mflux": "0.22.0",
        "sha256": digest,
    }.items():
        if details.get(key) != value:
            raise ValueError("Output metadata mismatch")
    paths = [image, metadata]
    if expected.get("selection"):
        native = folder / "native.png"
        if native.is_symlink() or not 50 <= native.stat().st_size <= 32 * 1024**2:
            raise ValueError("Invalid native image")
        native_raw = native.read_bytes()
        validate_png(native_raw, [1024, 1024])
        if (
            details.get("native_sha256") != hashlib.sha256(native_raw).hexdigest()
            or details.get("native_bytes") != len(native_raw)
            or details.get("composition", {}).get("outside_changed_pixels") != 0
        ):
            raise ValueError("Invalid composite provenance")
        paths.append(native)
    for path in paths:
        path.chmod(0o600)
        with path.open("rb") as handle:
            os.fsync(handle.fileno())
    sync_directory(folder)
    return digest, size, meta_size


def validate_png(raw: bytes, dimensions: list[int]) -> None:
    if raw[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("Invalid PNG signature")
    offset, chunks, compressed = 8, [], bytearray()
    while offset < len(raw):
        if offset + 12 > len(raw):
            raise ValueError("Truncated PNG")
        length = struct.unpack(">I", raw[offset : offset + 4])[0]
        kind = raw[offset + 4 : offset + 8]
        data = raw[offset + 8 : offset + 8 + length]
        end = offset + 12 + length
        if end > len(raw) or zlib.crc32(kind + data) != struct.unpack(">I", raw[end - 4 : end])[0]:
            raise ValueError("PNG CRC mismatch")
        chunks.append(kind)
        if kind == b"IHDR":
            if length != 13 or list(struct.unpack(">II", data[:8])) != dimensions:
                raise ValueError("Invalid image dimensions")
            # Qualified worker produces non-interlaced 8-bit RGB/RGBA.
            if data[8] != 8 or data[9] not in (2, 6) or data[10:] != b"\x00\x00\x00":
                raise ValueError("Unsupported PNG encoding")
            stride = 1 + dimensions[0] * (3 if data[9] == 2 else 4)
        if kind == b"IDAT":
            compressed.extend(data)
        offset = end
    if (
        not chunks
        or chunks[0] != b"IHDR"
        or chunks[-1] != b"IEND"
        or chunks.count(b"IHDR") != 1
        or chunks.count(b"IEND") != 1
        or not compressed
    ):
        raise ValueError("Missing PNG chunks")
    decoder = zlib.decompressobj()
    decoded = decoder.decompress(compressed, stride * dimensions[1] + 1)
    if not decoder.eof or decoder.unused_data or len(decoded) != stride * dimensions[1]:
        raise ValueError("Invalid pixel payload")
    if any(decoded[i] > 4 for i in range(0, len(decoded), stride)):
        raise ValueError("Invalid PNG filter")


def sanitize_export(folder: Path) -> tuple[str, int]:
    """Retain native PNG; remove ancillary chunks without recompressing pixels.

    Caller first validates the native 8-bit RGB/RGBA PNG with validate().
    Copying IHDR/IDAT/IEND exactly preserves its decoded pixels.
    """
    raw = (folder / "image.png").read_bytes()
    clean = bytearray(raw[:8])
    offset = 8
    while offset < len(raw):
        length = struct.unpack(">I", raw[offset : offset + 4])[0]
        end = offset + length + 12
        if raw[offset + 4 : offset + 8] in {b"IHDR", b"IDAT", b"IEND"}:
            clean.extend(raw[offset:end])
        offset = end
    part = folder / ".export.partial.png"
    with part.open("xb") as file:
        os.chmod(part, 0o600)
        file.write(clean)
        file.flush()
        os.fsync(file.fileno())
    os.replace(part, folder / "export.png")
    sync_directory(folder)
    return hashlib.sha256(clean).hexdigest(), len(clean)
