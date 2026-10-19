"""Content-addressed image companions to existing database backups; offline restore."""

import hashlib
import json
import os
import shutil
import sqlite3
from pathlib import Path
from typing import Any

from .files import atomic_json, sync_directory, validate
from .reference_files import FILES, bind, owned, validate_reference


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


def reference_rows(database: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    with sqlite3.connect(f"file:{database}?mode=ro", uri=True) as db:
        db.row_factory = sqlite3.Row
        if not db.execute("SELECT 1 FROM sqlite_master WHERE name='image_references'").fetchone():
            return [], []
        refs = [
            dict(row)
            for row in db.execute("SELECT * FROM image_references WHERE cleared_at IS NULL")
        ]
        pins = [
            dict(row)
            for row in db.execute(
                "SELECT p.*,j.input_json FROM image_job_references p JOIN "
                "image_jobs j ON j.id=p.job_id"
            )
        ]
        return refs, pins


def put_blob(source: Path, blobs: Path) -> str:
    if source.is_symlink() or not source.is_file():
        raise ValueError("Invalid backup source")
    raw = source.read_bytes()
    key = hashlib.sha256(raw).hexdigest()
    target = blobs / key
    if not target.is_file() or target.is_symlink() or digest(target) != key:
        if target.is_symlink():
            raise ValueError("Invalid backup target")
        part = target.with_suffix(".part")
        part.unlink(missing_ok=True)
        with part.open("xb") as file:
            part.chmod(0o600)
            file.write(raw)
            file.flush()
            os.fsync(file.fileno())
        os.replace(part, target)
    return key


def copy_blob(blobs: Path, key: str, destination: Path) -> None:
    if len(key) != 64 or any(c not in "0123456789abcdef" for c in key):
        raise ValueError("Invalid backup digest")
    source = blobs / key
    if source.is_symlink() or digest(source) != key:
        raise ValueError("Corrupt image backup")
    shutil.copyfile(source, destination)
    destination.chmod(0o600)


def companion(database: Path, data: Path) -> None:
    root = database.parent / "images"
    blobs = root / "blobs"
    blobs.mkdir(parents=True, mode=0o700, exist_ok=True)
    entries = []
    references, pins = reference_rows(database)
    by_job = {pin["job_id"]: pin for pin in pins}
    for row in snapshot_rows(database):
        folder = data / "images" / row["id"] / "output"
        expected = json.loads(row["input_json"])
        sha, _, _ = validate(folder, expected)
        if sha != row["sha256"]:
            raise ValueError("Image backup digest mismatch")
        files = {}
        for name in ("image.png", "metadata.json"):
            source = folder / name
            files[name] = put_blob(source, blobs)
        if row["id"] in by_job:
            files["export.png"] = put_blob(folder / "export.png", blobs)
            if files["export.png"] != by_job[row["id"]]["export_sha256"]:
                raise ValueError("Export backup digest mismatch")
        entries.append({"id": row["id"], "expected": expected, "files": files})
    reference_entries = []
    for row in references:
        folder = owned(data / "image-references", row["id"])
        descriptor = json.loads(row["descriptor_json"])
        validate_reference(folder, descriptor)
        files = {name: put_blob(folder / name, blobs) for name in FILES}
        if (folder / "storage.json").is_file():
            files["storage.json"] = put_blob(folder / "storage.json", blobs)
        reference_entries.append({"id": row["id"], "descriptor": descriptor, "files": files})
    pin_entries = []
    for pin in pins:
        item = {
            "id": pin["job_id"],
            "reference_id": pin["reference_id"],
            "expected": json.loads(pin["input_json"]),
        }
        measurement = data / "images" / pin["job_id"] / "storage.json"
        if measurement.is_file():
            item["storage_blob"] = put_blob(measurement, blobs)
        pin_entries.append(item)
    sync_directory(blobs)
    manifest = root / (database.stem + ".json")
    manifest.with_suffix(".part").unlink(missing_ok=True)
    spec: dict[str, Any] = {"database_sha256": digest(database), "images": entries}
    if references or pins:
        spec.update(version=2, references=reference_entries, reference_jobs=pin_entries)
    atomic_json(manifest, spec)


def prune(folder: Path) -> None:
    root = folder / "images"
    if not root.exists():
        return
    retained: set[str] = set()
    for manifest in root.glob("auto-*.json"):
        if not (folder / (manifest.stem + ".db")).exists():
            manifest.unlink()
        else:
            spec = json.loads(manifest.read_text())
            for entry in spec["images"] + spec.get("references", []):
                retained.update(entry["files"].values())
            retained.update(
                entry["storage_blob"]
                for entry in spec.get("reference_jobs", [])
                if entry.get("storage_blob")
            )
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
    references, pins = reference_rows(database)
    expected_refs = {row["id"]: row for row in references}
    expected_pins = {row["job_id"]: row for row in pins}
    if set(expected_refs) != {entry["id"] for entry in spec.get("references", [])} or set(
        expected_pins
    ) != {entry["id"] for entry in spec.get("reference_jobs", [])}:
        raise ValueError("Backup manifest does not cover the reference graph")
    if len(expected_refs) != len(spec.get("references", [])) or len(expected_pins) != len(
        spec.get("reference_jobs", [])
    ):
        raise ValueError("Duplicate reference backup entries")
    if set(rows) != {entry["id"] for entry in spec["images"]}:
        raise ValueError("Backup manifest does not cover the database artifacts")
    destination.mkdir(mode=0o700, parents=True)
    try:
        shutil.copyfile(database, destination / "workbench.db")
        (destination / "workbench.db").chmod(0o600)
        (destination / "images").mkdir(mode=0o700)
        if spec.get("references"):
            (destination / "image-references").mkdir(mode=0o700)
        for entry in spec.get("references", []):
            reference = expected_refs[entry["id"]]
            descriptor = json.loads(reference["descriptor_json"])
            if entry["descriptor"] != descriptor or not set(FILES) <= set(entry["files"]) <= set(
                FILES
            ) | {"storage.json"}:
                raise ValueError("Reference backup descriptor mismatch")
            folder = owned(destination / "image-references", reference["id"])
            folder.mkdir(mode=0o700, parents=True)
            for name, key in entry["files"].items():
                copy_blob(manifest.parent / "blobs", key, folder / name)
            validate_reference(folder, descriptor)
        for entry in spec.get("reference_jobs", []):
            pin = expected_pins[entry["id"]]
            expected = json.loads(pin["input_json"])
            if entry["reference_id"] != pin["reference_id"] or entry["expected"] != expected:
                raise ValueError("Pinned reference backup mismatch")
            folder = owned(destination / "images", entry["id"])
            folder.mkdir(mode=0o700, parents=True)
            atomic_json(folder / "input.json", expected)
            if pin["reference_id"] in expected_refs:
                bind(
                    owned(destination / "image-references", pin["reference_id"]),
                    folder / "inputs",
                    expected["reference"],
                )
            if entry.get("storage_blob"):
                copy_blob(manifest.parent / "blobs", entry["storage_blob"], folder / "storage.json")
        for entry in spec["images"]:
            identifier = entry["id"]
            if len(identifier) != 32 or any(c not in "0123456789abcdef" for c in identifier):
                raise ValueError("Invalid backup identifier")
            expected = json.loads(rows[identifier]["input_json"])
            if expected != entry["expected"]:
                raise ValueError("Backup input mismatch")
            folder = destination / "images" / identifier
            output = folder / "output"
            folder.mkdir(mode=0o700, parents=True, exist_ok=True)
            output.mkdir(mode=0o700, parents=True)
            if not (folder / "input.json").exists():
                atomic_json(folder / "input.json", expected)
            names = {"image.png", "metadata.json"} | (
                {"export.png"} if identifier in expected_pins else set()
            )
            if set(entry["files"]) != names:
                raise ValueError("Unexpected image backup files")
            for name in names:
                key = entry["files"][name]
                copy_blob(manifest.parent / "blobs", key, output / name)
                if name == "export.png" and key != expected_pins[identifier]["export_sha256"]:
                    raise ValueError("Export backup mismatch")
            sha, _, _ = validate(output, expected)
            if sha != rows[identifier]["sha256"]:
                raise ValueError("Restored image digest mismatch")
        sync_directory(destination)
        return len(rows)
    except BaseException:
        shutil.rmtree(destination)
        raise
