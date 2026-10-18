"""N0 G15: synthetic version-13 backup, version-14 startup, restore and old startup."""

import json
import os
import shutil
import sqlite3
import subprocess
import tempfile
from pathlib import Path
from time import monotonic

ROOT = Path(__file__).resolve().parents[1]
PREVIOUS = "e7ffea2b"


def snapshot(path: Path, columns: dict[str, list[str]] | None = None) -> tuple[dict, dict]:
    with sqlite3.connect(path) as db:
        if columns is None:
            tables = [
                r[0]
                for r in db.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
                )
            ]
            columns = {t: [r[1] for r in db.execute(f'PRAGMA table_info("{t}")')] for t in tables}
        rows = {}
        for table, names in columns.items():
            projection = ",".join('"' + name + '"' for name in names)
            rows[table] = {repr(row) for row in db.execute(f'SELECT {projection} FROM "{table}"')}
        return columns, rows


def boot(source: Path, data: Path) -> dict[str, object]:
    code = """
import asyncio,json,sys
from pathlib import Path
sys.path.insert(0,sys.argv[1])
import httpx
from app.main import create_app
from app.config import Settings
async def main():
 app=create_app(Settings(data_dir=Path(sys.argv[2]),image_home=None,transcribe_home=None,
                         log_level='CRITICAL'))
 async with app.router.lifespan_context(app):
  async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://localhost') as client:
   health=await client.get('/api/health')
   version=(await app.state.store.one('PRAGMA user_version'))['user_version']
   print(json.dumps({'health_status':health.status_code,'schema_version':version}))
asyncio.run(main())
"""
    completed = subprocess.run(
        [str(ROOT / "server/.venv/bin/python"), "-c", code, str(source / "server"), str(data)],
        capture_output=True,
        text=True,
        env=os.environ.copy(),
    )
    if completed.returncode:
        raise RuntimeError(completed.stderr)  # Synthetic database only.
    return dict(json.loads(completed.stdout))


def main() -> None:
    started = monotonic()
    with tempfile.TemporaryDirectory(prefix="fake-agent-rollback-") as temporary:
        folder = Path(temporary)
        data = folder / "data"
        data.mkdir(mode=0o700)
        database = data / "workbench.db"
        shutil.copyfile(ROOT / "server/tests/fixtures/db/phase3.db", database)
        with sqlite3.connect(database) as db:
            for migration in sorted((ROOT / "server/app/db/migrations").glob("*.sql")):
                version = int(migration.name.split("_")[0])
                if 4 < version <= 13:
                    db.executescript(migration.read_text() + f"\nPRAGMA user_version={version};")
            with sqlite3.connect(folder / "before.db") as backup:
                db.backup(backup)
        columns, original = snapshot(database)
        candidate = boot(ROOT, data)
        assert all(rows <= snapshot(database, columns)[1][name] for name, rows in original.items())
        for suffix in ("", "-wal", "-shm"):
            (data / ("workbench.db" + suffix)).unlink(missing_ok=True)
        shutil.copyfile(folder / "before.db", database)
        previous = folder / "previous"
        previous.mkdir()
        # Use git's own archive with a fixed ref; extract only tracked source, never local data.
        archive = subprocess.run(
            ["git", "archive", PREVIOUS, "server/app", "shared"],
            cwd=ROOT,
            capture_output=True,
            check=True,
        ).stdout
        import io
        import tarfile

        with tarfile.open(fileobj=io.BytesIO(archive)) as handle:
            handle.extractall(previous, filter="data")
        restored = boot(previous, data)
        assert all(rows <= snapshot(database, columns)[1][name] for name, rows in original.items())
        assert candidate == {"health_status": 200, "schema_version": 14}
        assert restored == {"health_status": 200, "schema_version": 13}
        result = {
            "synthetic_only": True,
            "previous_commit": PREVIOUS,
            "candidate": candidate,
            "restored": restored,
            "original_tables_preserved": len(original),
            "production_modified": False,
            "native_calls": 0,
            "seconds": monotonic() - started,
        }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
