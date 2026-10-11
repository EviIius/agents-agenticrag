"""Rehearse migration and previous-build startup using synthetic data only."""
import asyncio
import hashlib
import json
import shutil
import sqlite3
import subprocess
import sys
import tarfile
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "server"))
from app.db.core import migrate
import aiosqlite


def rows(path):
    with sqlite3.connect(path) as db:
        return {name: hashlib.sha256(repr(sorted(db.execute(f'SELECT * FROM "{name}"').fetchall(),key=repr)).encode()).hexdigest() for (name,) in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE '%fts%' AND name NOT LIKE 'sqlite_%'")}


async def main():
    started=time.monotonic()
    with tempfile.TemporaryDirectory(prefix="atelier-images-rollback-") as temporary:
        folder=Path(temporary)
        data=folder/"data";data.mkdir()
        source=ROOT/"server/tests/fixtures/db/phase3.db"
        database=data/"workbench.db"
        shutil.copyfile(source,database)
        with sqlite3.connect(database) as db:
            for p in sorted((ROOT/"server/app/db/migrations").glob("*.sql")):
                number=int(p.name.split("_",1)[0])
                if 4<number<=8: db.executescript(p.read_text()+f'\nPRAGMA user_version={number};')
        before=rows(database)
        backup=folder/"before.db";shutil.copyfile(database,backup)
        async with aiosqlite.connect(database) as db: await migrate(db)
        after=rows(database)
        assert all(after[name]==digest for name,digest in before.items())
        shutil.copyfile(backup,database)
        archive=folder/"previous.tar"
        with archive.open("wb") as handle:
            subprocess.run(["git","archive","ba75e28","server/app","shared"],cwd=ROOT,stdout=handle,check=True)
        previous=folder/"previous";previous.mkdir()
        with tarfile.open(archive) as handle: handle.extractall(previous,filter="data")
        code='import asyncio,sys\nfrom pathlib import Path\nfrom app.main import create_app\nfrom app.config import Settings\nasync def main():\n app=create_app(Settings(data_dir=Path(sys.argv[1])))\n async with app.router.lifespan_context(app):\n  row=await app.state.store.one("PRAGMA user_version")\n  assert row["user_version"]==8\nasyncio.run(main())\n'
        result=subprocess.run([sys.executable,"-c",code,str(data)],cwd=previous/"server",capture_output=True,text=True)
        assert result.returncode==0, result.stderr
        report={"synthetic_only":True,"previous_commit":"ba75e28","old_tables_preserved_on_migration":len(before),"restored_version":8,"previous_build_started":True,"seconds":time.monotonic()-started}
    print(json.dumps(report,indent=2))


if __name__=="__main__": asyncio.run(main())
