"""Content-addressed image companions to existing database backups; offline restore."""

import hashlib
import json
import os
import shutil
import sqlite3
from pathlib import Path
from typing import Any

from .files import atomic_json, sync_directory, validate


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot_rows(database: Path) -> list[dict[str, Any]]:
    with sqlite3.connect(f"file:{database}?mode=ro", uri=True) as db:
        db.row_factory = sqlite3.Row
        return [
            dict(row)
            for row in db.execute(
                "SELECT j.id,j.input_json,a.sha256 FROM image_artifacts a "
                "JOIN image_jobs j ON j.id=a.job_id"
            )
        ]


def companion(database: Path, data: Path) -> None:
    root = database.parent / "images"
    blobs = root / "blobs"
    blobs.mkdir(parents=True, mode=0o700, exist_ok=True)
    entries = []
    for row in snapshot_rows(database):
        folder = data / "images" / row["id"] / "output"
        expected = json.loads(row["input_json"])
        sha, _, _ = validate(folder, expected)
        if sha != row["sha256"]:
            raise ValueError("Image backup digest mismatch")
        files = {}
        for name in ("image.png", "metadata.json"):
            source = folder / name
            key = digest(source)
            target = blobs / key
            if not target.is_file() or digest(target) != key:
                part = target.with_suffix(".part")
                shutil.copyfile(source, part)
                part.chmod(0o600)
                with part.open("rb") as handle:
                    os.fsync(handle.fileno())
                os.replace(part, target)
            files[name] = key
        entries.append({"id": row["id"], "expected": expected, "files": files})
    sync_directory(blobs)
    manifest = root / (database.stem + ".json")
    manifest.with_suffix(".part").unlink(missing_ok=True)
    atomic_json(manifest, {"database_sha256": digest(database), "images": entries})


def prune(folder: Path) -> None:
    root = folder / "images"
    if not root.exists():
        return
    retained: set[str] = set()
    for manifest in root.glob("auto-*.json"):
        if not (folder / (manifest.stem + ".db")).exists():
            manifest.unlink()
        else:
            for entry in json.loads(manifest.read_text())["images"]:
                retained.update(entry["files"].values())
    for blob in (root / "blobs").iterdir():
        if blob.name not in retained:
            blob.unlink()


def restore(database: Path, destination: Path) -> int:
    """Restore a paired backup into a NEW directory, never the running app's data."""
    manifest = database.parent / "images" / (database.stem + ".json")
    spec = json.loads(manifest.read_text())
    if spec["database_sha256"] != digest(database):
        raise ValueError("Database and image manifest do not match")
    if destination.exists():
        raise ValueError("Restore destination must not exist")
    rows = {row["id"]: row for row in snapshot_rows(database)}
    if set(rows) != {entry["id"] for entry in spec["images"]}:
        raise ValueError("Backup manifest does not cover the database artifacts")
    destination.mkdir(mode=0o700, parents=True)
    try:
        shutil.copyfile(database, destination / "workbench.db")
        (destination / "workbench.db").chmod(0o600)
        for entry in spec["images"]:
            identifier = entry["id"]
            if len(identifier) != 32 or any(c not in "0123456789abcdef" for c in identifier):
                raise ValueError("Invalid backup identifier")
            expected = json.loads(rows[identifier]["input_json"])
            if expected != entry["expected"]:
                raise ValueError("Backup input mismatch")
            folder = destination / "images" / identifier
            output = folder / "output"
            output.mkdir(mode=0o700, parents=True)
            atomic_json(folder / "input.json", expected)
            for name in ("image.png", "metadata.json"):
                key = entry["files"][name]
                if len(key) != 64 or any(c not in "0123456789abcdef" for c in key):
                    raise ValueError("Invalid backup digest")
                source = manifest.parent / "blobs" / key
                if digest(source) != key:
                    raise ValueError("Corrupt image backup")
                shutil.copyfile(source, output / name)
            sha, _, _ = validate(output, expected)
            if sha != rows[identifier]["sha256"]:
                raise ValueError("Restored image digest mismatch")
        sync_directory(destination)
        return len(rows)
    except BaseException:
        shutil.rmtree(destination)
        raise
