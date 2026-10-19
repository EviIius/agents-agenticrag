"""Isolated PE0 inputs. No model imports, arbitrary reference paths or fallback."""

import hashlib
import json
import os
import re
from pathlib import Path

LIMIT = 20 * 1024**2
PIXELS = 100_000_000
EDGE = 2048


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def owned(root, relative):
    root = root.resolve(strict=True)
    path = root
    for part in Path(relative).parts:
        if part in ("", ".", "..") or Path(part).is_absolute():
            raise ValueError("Invalid owned path")
        path = path / part
        if path.is_symlink():
            raise ValueError("Symlink is not an owned input")
    if not path.is_relative_to(root):
        raise ValueError("Input escaped job")
    return path


def write_new(path, data):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate request field")
        result[key] = value
    return result


def read_json(path):
    if path.stat().st_size > 32768:
        raise ValueError("Manifest too large")
    return json.loads(path.read_text(), object_pairs_hook=no_duplicates)


def normalize(root):
    """Keep original bytes; decode bounded PNG/JPEG, orient and strip metadata."""
    from PIL import Image, ImageOps

    original = owned(root, "inputs/original")
    working = owned(root, "inputs/reference.png")
    receipt = owned(root, "inputs/reference.json")
    if working.exists() or receipt.exists() or not 0 < original.stat().st_size <= LIMIT:
        raise ValueError("Invalid or already prepared reference")
    original_hash = digest(original)
    with Image.open(original) as image:
        if image.format not in ("PNG", "JPEG") or image.width * image.height > PIXELS:
            raise ValueError("Unsupported reference format or dimensions")
        dimensions = list(image.size)
        orientation = image.getexif().get(274, 1)
        if type(orientation) is not int or orientation not in range(1, 9):
            raise ValueError("Invalid orientation")
        image.load()
        oriented = ImageOps.exif_transpose(image).convert("RGB")
        oriented.thumbnail((EDGE, EDGE), Image.Resampling.LANCZOS)
        clean = Image.new("RGB", oriented.size)
        clean.paste(oriented)
        with working.open("xb") as stream:
            os.chmod(working, 0o600)
            clean.save(stream, format="PNG")
            stream.flush()
            os.fsync(stream.fileno())
        descriptor = {
            "original_sha256": original_hash,
            "original_bytes": original.stat().st_size,
            "original_format": image.format,
            "original_dimensions": dimensions,
            "exif_orientation": orientation,
            "sha256": digest(working),
            "bytes": working.stat().st_size,
            "dimensions": list(clean.size),
            "normalization": "exif-transpose; RGB; longest-edge<=2048; metadata-stripped",
        }
    if digest(original) != original_hash or working.stat().st_size > LIMIT:
        raise ValueError("Reference changed or exceeded bound")
    write_new(receipt, (json.dumps(descriptor, indent=2) + "\n").encode())
    return descriptor


def validate_reference(root, expected):
    from PIL import Image

    fields = {
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
    if not isinstance(expected, dict) or set(expected) != fields:
        raise ValueError("Missing reference descriptor")
    receipt = read_json(owned(root, "inputs/reference.json"))
    if receipt != expected:
        raise ValueError("Reference binding changed")
    for key in ("sha256", "original_sha256"):
        if not isinstance(expected.get(key), str) or not re.fullmatch(
            r"[a-f0-9]{64}", expected[key]
        ):
            raise ValueError("Invalid reference hash")
    original = owned(root, "inputs/original")
    working = owned(root, "inputs/reference.png")
    for path, size_key, hash_key in (
        (original, "original_bytes", "original_sha256"),
        (working, "bytes", "sha256"),
    ):
        if (
            type(expected.get(size_key)) is not int
            or not 0 < path.stat().st_size == expected[size_key] <= LIMIT
            or digest(path) != expected[hash_key]
        ):
            raise ValueError("Reference bytes changed")
    with Image.open(working) as image:
        if (
            image.format != "PNG"
            or image.mode != "RGB"
            or list(image.size) != expected.get("dimensions")
            or not 0 < min(image.size) <= max(image.size) <= EDGE
            or image.info
        ):
            raise ValueError("Invalid normalized reference")
        image.load()
    return working


def load_request(path, output):
    root = path.parent.resolve(strict=True)
    if path.name != "request.json" or owned(root, "request.json") != path.absolute():
        raise ValueError("Invalid manifest location")
    if output.absolute() != owned(root, "output") or not output.is_dir() or any(output.iterdir()):
        raise ValueError("Output must be a fresh owned directory")
    request = read_json(path)
    if not isinstance(request, dict) or request.get("mode") not in ("generate", "edit"):
        raise ValueError("Explicit mode required")
    keys = {"mode", "prompt", "seed"} | ({"reference"} if request["mode"] == "edit" else set())
    if set(request) != keys:
        raise ValueError("Unexpected request fields")
    if not isinstance(request["prompt"], str) or not 0 < len(request["prompt"].strip()) <= 4000:
        raise ValueError("Invalid prompt")
    if type(request["seed"]) is not int or not 0 <= request["seed"] < 2**32:
        raise ValueError("Invalid seed")
    reference = (
        validate_reference(root, request["reference"]) if request["mode"] == "edit" else None
    )
    return request, reference
