"""Rehearse the new schema and previous app on a private copy, never production data."""
import argparse
import hashlib
import json
import shutil
import sqlite3
import subprocess
import tarfile
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(path: Path) -> dict[str, str]:
    result = {}
    with sqlite3.connect(path) as db:
        tables = [r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        for table in tables:
            rows = sorted(repr(r) for r in db.execute('SELECT * FROM "' + table.replace('"', '""') + '"'))
            result[table] = hashlib.sha256("\n".join(rows).encode()).hexdigest()
    return result


def boot(source: Path, data: Path) -> dict[str, object]:
    code = """
import asyncio,json,logging,sys
from pathlib import Path
sys.path.insert(0,sys.argv[1])
import httpx
from app.main import create_app
from app.config import Settings
async def main():
 app=create_app(Settings(data_dir=Path(sys.argv[2]),transcribe_home=None,log_level='CRITICAL'))
 async with app.router.lifespan_context(app):
  async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://localhost') as client:
   health=await client.get('/api/health')
   shell=await client.get('/')
   version=(await app.state.store.one('PRAGMA user_version'))['user_version']
   print(json.dumps({'health_status':health.status_code,'shell_status':shell.status_code,'schema_version':version}))
asyncio.run(main())
"""
    completed = subprocess.run([str(ROOT / "server/.venv/bin/python"), "-c", code,
                                str(source / "server"), str(data)], capture_output=True, text=True)
    if completed.returncode:
        raise RuntimeError("Copied app startup failed; private output suppressed")
    return dict(json.loads(completed.stdout))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--previous", required=True)
    args = parser.parse_args()
    start = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="workbench-preset-rollback-") as temp:
        private = Path(temp)
        data = private / "data"
        data.mkdir(mode=0o700)
        original = Path.home() / ".local/share/workbench/data"
        for source in original.iterdir():
            if source.name.startswith("workbench.db") or source.name == "backups":
                continue
            if source.is_dir():
                shutil.copytree(source, data / source.name)
            else:
                shutil.copy2(source, data / source.name)
        before = private / "before.db"
        with sqlite3.connect(f"file:{original / 'workbench.db'}?mode=ro", uri=True) as db:
            with sqlite3.connect(before) as target:
                db.backup(target)
        before.chmod(0o600)
        shutil.copy2(before, data / "workbench.db")
        hashes = digest(before)
        old = private / "previous"
        old.mkdir()
        archive = private / "source.tar"
        with archive.open("wb") as handle:
            subprocess.run(["git", "archive", args.previous], cwd=ROOT, stdout=handle, check=True)
        with tarfile.open(archive) as handle:
            handle.extractall(old, filter="data")
        shutil.copytree(Path.home()/".local/share/workbench/app/server/app/static", old/"server/app/static", dirs_exist_ok=True)
        upgraded = boot(ROOT, data)
        with sqlite3.connect(data / "workbench.db") as db:
            db.execute("INSERT INTO presets VALUES ('synthetic-rehearsal','Synthetic rehearsal',NULL,'{}',0,'2026-10-05','2026-10-05')")
            db.commit()
        for suffix in ("", "-wal", "-shm"):
            (data / ("workbench.db" + suffix)).unlink(missing_ok=True)
        shutil.copy2(before, data / "workbench.db")
        restored = boot(old, data)
        preserved = hashes == digest(data / "workbench.db")
        result = {"previous_commit":args.previous,"new_app":upgraded,"restored_app":restored,
                  "old_row_hashes_identical":preserved,"seconds":round(time.monotonic()-start,3),
                  "method":"Private data-folder copy; SQLite online backup; current app boot and synthetic preset; restore backup without WAL/SHM; previous app boot",
                  "production_modified":False,"private_copy_removed":True}
        if (not preserved or upgraded["schema_version"] != 5 or restored["schema_version"] != 4
            or any(v["health_status"] != 200 or v["shell_status"] != 200 for v in (upgraded,restored))):
            raise RuntimeError("Rollback verification failed; private data suppressed")
        print(json.dumps(result,indent=2))


if __name__ == "__main__":
    main()
