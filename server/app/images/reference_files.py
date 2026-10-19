"""Private reference layout and hash binding; no CPU/native model imports."""

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from .files import sync_directory

FILES = ("original", "reference.png", "reference.json")
RECIPE = "exif-transpose; RGB; longest-edge<=2048; metadata-stripped"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def owned(root: Path, identifier: str) -> Path:
    if not re.fullmatch(r"[a-f0-9]{32}", identifier) or root.is_symlink():
        raise ValueError("Invalid reference identity")
    path = root / identifier
    if path.is_symlink():
        raise ValueError("Invalid reference path")
    return path


def validate_reference(folder: Path, descriptor: dict[str, Any]) -> None:
    if folder.is_symlink() or not folder.is_dir():
        raise ValueError("Missing reference")
    expected_keys = {
        "original_sha256",
        "original_bytes",
        "original_format",
        "original_dimensions",
        "exif_orientation",
        "sha256",
        "bytes",
        "dimensions",
        "normalization",
    }
    if set(descriptor) != expected_keys or descriptor["normalization"] != RECIPE:
        raise ValueError("Invalid reference descriptor")
    dimensions = descriptor["dimensions"]
    original_dimensions = descriptor["original_dimensions"]
    if (
        not isinstance(dimensions, list)
        or len(dimensions) != 2
        or any(type(n) is not int or not 1 <= n <= 2048 for n in dimensions)
        or not isinstance(original_dimensions, list)
        or len(original_dimensions) != 2
        or any(type(n) is not int or n < 1 for n in original_dimensions)
        or original_dimensions[0] * original_dimensions[1] > 100_000_000
        or descriptor["original_format"] not in {"PNG", "JPEG", "HEIF"}
    ):
        raise ValueError("Invalid reference dimensions/format")
    orientation = descriptor["exif_orientation"]
    if not (
        (type(orientation) is int and 1 <= orientation <= 8)
        or (orientation is None and descriptor["original_format"] == "HEIF")
    ):
        raise ValueError("Invalid reference orientation")
    for name in FILES:
        file = folder / name
        if file.is_symlink() or not file.is_file():
            raise ValueError("Invalid reference file")
    if (folder / "reference.json").stat().st_size > 32768:
        raise ValueError("Invalid reference receipt")
    if json.loads((folder / "reference.json").read_text()) != descriptor:
        raise ValueError("Reference receipt mismatch")
    for name, size, key in (
        ("original", "original_bytes", "original_sha256"),
        ("reference.png", "bytes", "sha256"),
    ):
        if (
            type(descriptor[size]) is not int
            or not 0 < descriptor[size] <= 20 * 1024**2
            or (folder / name).stat().st_size != descriptor[size]
            or not isinstance(descriptor[key], str)
            or re.fullmatch(r"[a-f0-9]{64}", descriptor[key]) is None
            or digest(folder / name) != descriptor[key]
        ):
            raise ValueError("Reference bytes changed")


def bind(source: Path, destination: Path, descriptor: dict[str, Any]) -> None:
    """Caller owns the image lock. Share owned inodes, not mutable upload paths."""
    import os

    validate_reference(source, descriptor)
    destination.mkdir(mode=0o700)
    for name in FILES:
        os.link(source / name, destination / name, follow_symlinks=False)
    sync_directory(destination)
    validate_reference(destination, descriptor)
