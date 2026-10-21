"""Prepare a private PE1 release/fallback bundle. This tool cannot publish it.

Run only on quiesced data. Preparation never calls a model, changes launchd,
restores running data or copies an old backend into the compatibility fallback.
"""

import argparse
import fcntl
import hashlib
import json
import os
import plistlib
import shutil
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "server"), str(ROOT / "scripts")]
from app.images.backup import companion, restore  # noqa: E402
from install_image_worker import FILES, install  # noqa: E402


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory(root: Path, excluded: set[str] | None = None) -> dict[str, str]:
    result = {}
    for path in sorted(root.rglob("*")):
        name = path.relative_to(root)
        if name.parts[0] in (excluded or set()) or "__pycache__" in name.parts:
            continue
        if path.is_symlink():
            raise ValueError("Release inputs must not contain symlinks")
        if path.is_file():
            result[str(name)] = sha(path)
    return result


def copy_files(source: Path, target: Path, files: dict[str, str]) -> None:
    target.mkdir(mode=0o700, parents=True, exist_ok=True)
    for name, digest in files.items():
        destination = target / name
        destination.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        shutil.copyfile(source / name, destination)
        destination.chmod(0o600)
        if sha(destination) != digest:
            raise ValueError("Release source changed while copying")


def app_files(root: Path) -> dict[str, str]:
    result = {}
    for directory in ("server/app", "shared"):
        result.update(
            {directory + "/" + k: v for k, v in inventory(root / directory).items()}
        )
    for name in ("server/pyproject.toml", "server/uv.lock"):
        result[name] = sha(root / name)
    return result


def sqlite_backup(source: Path, destination: Path) -> None:
    destination.touch(mode=0o600, exist_ok=False)
    with (
        sqlite3.connect(source.as_uri() + "?mode=ro", uri=True) as src,
        sqlite3.connect(destination) as dst,
    ):
        src.backup(dst)
    with destination.open("rb") as file:
        os.fsync(file.fileno())


def snapshot_data(source: Path, target: Path) -> None:
    """Caller holds source native.lock and has stopped app/CPU jobs before calling."""
    excluded = {
        "workbench.db",
        "workbench.db-wal",
        "workbench.db-shm",
        "native.lock",
        "backups",
    }
    with sqlite3.connect(
        (source / "workbench.db").as_uri() + "?mode=ro", uri=True
    ) as db:
        version = db.execute("PRAGMA user_version").fetchone()[0]
        if not 13 <= version <= 14:
            raise ValueError("Only the reviewed schema 13/14 release path is supported")
        if db.execute(
            "SELECT 1 FROM image_jobs WHERE state IN ('preparing','running','cancelling') LIMIT 1"
        ).fetchone():
            raise ValueError("Image work is active; quiesce/reap before snapshot")
        generation = db.execute("PRAGMA data_version").fetchone()[0]
        files = inventory(source, excluded)
        copy_files(source, target, files)
        sqlite_backup(source / "workbench.db", target / "workbench.db")
        if (
            generation != db.execute("PRAGMA data_version").fetchone()[0]
            or inventory(source, excluded) != files
        ):
            raise ValueError("Data changed during snapshot; no release bundle accepted")


def check_service(raw: bytes) -> dict[str, str]:
    spec = plistlib.loads(raw)
    args = spec.get("ProgramArguments", [])
    if not isinstance(spec.get("Label"), str) or not spec["Label"]:
        raise ValueError("Existing service identity required")
    for option, expected in (("--host", "127.0.0.1"), ("--port", "8787")):
        if (
            option not in args
            or args.index(option) + 1 >= len(args)
            or args[args.index(option) + 1] != expected
        ):
            raise ValueError("Service bind/port is outside the reviewed release path")
    return {"label": spec["Label"], "bind": "127.0.0.1", "port": "8787"}


def prepare(
    output: Path, data: Path, installed_app: Path, installed_worker: Path, plist: Path
) -> dict[str, object]:
    roots = [
        p.expanduser() for p in (output, data, installed_app, installed_worker, plist)
    ]
    if any(p.is_symlink() for p in roots):
        raise ValueError("Release roots must not be symlinks")
    output, data, installed_app, installed_worker, plist = [
        p.resolve(strict=index > 0) for index, p in enumerate(roots)
    ]
    if output.exists():
        raise ValueError("Bundle destination must be new")
    if any(
        output.is_relative_to(p) or p.is_relative_to(output)
        for p in (data, installed_app, installed_worker, ROOT)
    ):
        raise ValueError("Bundle destination must be separate from source/data")
    if any(p.is_symlink() for p in (data, installed_app, installed_worker, plist)):
        raise ValueError("Release roots must not be symlinks")
    service_raw = plist.read_bytes()
    service = check_service(service_raw)
    # Version-locked environments are reused, never resolved/upgraded here.
    for name in ("server/pyproject.toml", "server/uv.lock"):
        if sha(ROOT / name) != sha(installed_app / name):
            raise ValueError(
                "Server dependency files differ; runtime change needs separate review"
            )
    python = Path((installed_worker / ".python").read_text().strip())
    model = Path(
        json.loads((installed_worker / "config.json").read_text())["model_path"]
    )
    old_app = app_files(installed_app)
    old_worker = inventory(installed_worker)
    source = app_files(ROOT)
    if (data / "native.lock").is_symlink():
        raise ValueError("Native lock must not be a symlink")
    lock_fd = os.open(data / "native.lock", os.O_CREAT | os.O_RDWR, 0o600)
    created = False
    try:
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError(
                "Native work is active; stop and reap before preparation"
            ) from None
        output.mkdir(mode=0o700, parents=True)
        created = True
        copy_files(installed_app, output / "previous-app-archive", old_app)
        copy_files(installed_worker, output / "previous-worker-archive", old_worker)
        (output / "original.plist").write_bytes(service_raw)
        (output / "original.plist").chmod(0o600)
        copy_files(ROOT, output / "candidate-app", source)
        copy_files(ROOT, output / "compatibility-app", source)
        # Compatibility always keeps the NEW backend and worker; only its UI reverts.
        shutil.rmtree(output / "compatibility-app/server/app/static")
        static = inventory(installed_app / "server/app/static")
        copy_files(
            installed_app / "server/app/static",
            output / "compatibility-app/server/app/static",
            static,
        )
        snapshot_data(data, output / "data-snapshot")
        paired = output / "paired-backup/auto-release.db"
        paired.parent.mkdir(mode=0o700)
        sqlite_backup(output / "data-snapshot/workbench.db", paired)
        companion(paired, output / "data-snapshot")
        # Verify the paired reference graph with the actual restore implementation.
        restored = output / "restore-verification"
        restore(paired, restored)
        shutil.rmtree(restored)
        copy_files(
            installed_worker,
            output / "worker",
            {k: v for k, v in old_worker.items() if k in {".python", "config.json"}},
        )
        install(output / "worker", python, model, lock=output / "worker-install.lock")
        (output / "worker-install.lock").unlink()
        if (
            app_files(installed_app) != old_app
            or inventory(installed_worker) != old_worker
            or plist.read_bytes() != service_raw
        ):
            raise ValueError("Installed source or service changed during preparation")
        files = inventory(output)
        manifest: dict[str, object] = {
            "version": 1,
            "schema_supported": 14,
            "publication_authorized": False,
            "service": service,
            "original_plist_sha256": sha(plist),
            "candidate": "candidate-app",
            "compatibility": "compatibility-app",
            "worker": "worker",
            "archival_only": [
                "previous-app-archive",
                "previous-worker-archive",
                "data-snapshot",
                "paired-backup",
            ],
            "rollback_policy": (
                "Keep schema-aware backend and new worker; restore previous UI only. "
                "Never replace current data with pre-release snapshot or run previous "
                "backend on schema 14."
            ),
            "files": files,
        }
        (output / "release.json").write_text(json.dumps(manifest, indent=2) + "\n")
        (output / "release.json").chmod(0o600)
        verify(output)
        return manifest
    except BaseException:
        if created:
            shutil.rmtree(output)
        raise
    finally:
        os.close(lock_fd)


def verify(bundle: Path) -> None:
    spec = json.loads((bundle / "release.json").read_text())
    actual = inventory(bundle)
    actual.pop("release.json", None)
    if actual != spec["files"]:
        raise ValueError("Release bundle is incomplete or changed")
    if (
        spec["candidate"] != "candidate-app"
        or spec["compatibility"] != "compatibility-app"
        or spec["worker"] != "worker"
    ):
        raise ValueError("Only reviewed candidate/compatibility selections are allowed")
    left, right = (
        app_files(bundle / "candidate-app"),
        app_files(bundle / "compatibility-app"),
    )
    for name in left:
        if not name.startswith("server/app/static/") and left[name] != right.get(name):
            raise ValueError("Compatibility fallback must keep the candidate backend")
    for name in ("candidate-app", "compatibility-app"):
        if not (
            bundle / name / "server/app/db/migrations/014_image_references.sql"
        ).is_file():
            raise ValueError("Schema-aware backend is required")
    if check_service((bundle / "original.plist").read_bytes()) != spec["service"]:
        raise ValueError("Service identity changed")
    for name in FILES:
        if sha(bundle / "worker" / name) != sha(ROOT / "image_worker/product" / name):
            raise ValueError("Reviewed worker source changed")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true")
    for name in ("output", "data", "installed-app", "installed-worker", "plist"):
        parser.add_argument("--" + name, type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.verify:
        verify(args.verify.expanduser().absolute())
        print("Prepared bundle verified; nothing published.")
    elif args.prepare:
        paths = [
            args.output,
            args.data,
            args.installed_app,
            args.installed_worker,
            args.plist,
        ]
        if any(p is None for p in paths):
            parser.error(
                "--prepare requires all five explicit paths; stop/quiesce the source app first"
            )
        result = prepare(*paths)
        print(
            json.dumps(
                {
                    "prepared": True,
                    "publication_authorized": False,
                    "files": len(result["files"]),
                }
            )
        )
    else:
        print(
            "Plan only: prepare copied app/worker/data/plist and a schema-aware UI fallback. "
            "No publish operation exists."
        )


if __name__ == "__main__":
    main()
