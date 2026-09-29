"""Back up or restore the local SQLite workbench databases.

Stop the workbench before backup/restore so corpus, chats, and run records describe
the same point in time. Restore refuses to overwrite existing databases.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sqlite3
import tempfile
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path


def paths(db: Path) -> dict[str, Path]:
    return {
        "corpus": db,
        "chats": db.with_name("workbench-chats.db"),
        "runs": db.with_name("workbench-runs.db"),
    }


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def backup(db: Path, destination: Path) -> None:
    sources = paths(db)
    if not sources["corpus"].is_file():
        raise ValueError(f"Corpus database does not exist: {sources['corpus']}")
    destination.mkdir(parents=True, exist_ok=False)
    manifest = {"version": 1, "created_at": datetime.now(timezone.utc).isoformat(), "files": {}}
    for name, source in sources.items():
        if not source.is_file():
            continue
        target = destination / f"{name}.db"
        with closing(sqlite3.connect(f"file:{source.resolve()}?mode=ro", uri=True)) as input_db:
            with closing(sqlite3.connect(target)) as output_db:
                input_db.backup(output_db)
        os.chmod(target, 0o600)
        manifest["files"][name] = {"sha256": digest(target), "bytes": target.stat().st_size}
    (destination / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    os.chmod(destination / "manifest.json", 0o600)


def restore(archive: Path, db: Path) -> None:
    manifest = json.loads((archive / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("version") != 1 or not isinstance(manifest.get("files"), dict):
        raise ValueError("Unsupported backup manifest")
    destinations = paths(db)
    files = manifest["files"]
    if "corpus" not in files or not set(files).issubset(destinations):
        raise ValueError("Backup does not contain a valid corpus database")
    for name, item in files.items():
        source = archive / f"{name}.db"
        if not source.is_file() or digest(source) != item.get("sha256"):
            raise ValueError(f"Backup integrity check failed: {name}")
        if destinations[name].exists():
            raise ValueError(f"Restore destination already exists: {destinations[name]}")
    db.parent.mkdir(parents=True, exist_ok=True)
    for name in files:
        target = destinations[name]
        with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as temporary:
            temporary_path = Path(temporary.name)
        try:
            shutil.copyfile(archive / f"{name}.db", temporary_path)
            os.chmod(temporary_path, 0o600)
            os.replace(temporary_path, target)
        finally:
            temporary_path.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, required=True, help="Corpus SQLite database path")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--backup", type=Path, help="New backup directory")
    group.add_argument("--restore", type=Path, help="Existing backup directory")
    args = parser.parse_args()
    if args.backup:
        backup(args.db.expanduser().resolve(), args.backup.expanduser().resolve())
        print(f"Backup saved: {args.backup}")
    else:
        restore(args.restore.expanduser().resolve(), args.db.expanduser().resolve())
        print(f"Backup restored to: {args.db}")


if __name__ == "__main__":
    main()
