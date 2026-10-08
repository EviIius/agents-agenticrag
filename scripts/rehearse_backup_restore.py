"""5C: automatic backup restore and previous-schema rollback on a private data copy."""
import argparse
import asyncio
import json
import shutil
import sqlite3
import subprocess
import tarfile
import tempfile
import time
from pathlib import Path

from rehearse_documents_rollback import ROOT, boot, digest


def restore(source: Path, data: Path) -> None:
    for suffix in ("", "-wal", "-shm"):
        (data / ("workbench.db" + suffix)).unlink(missing_ok=True)
    shutil.copy2(source, data / "workbench.db")
    (data / "workbench.db").chmod(0o600)


async def automatic(data: Path) -> Path:
    import sys
    sys.path.insert(0, str(ROOT / "server"))
    from app.backup import Backups
    from app.db.core import Store, connect
    async with connect(data) as db:
        backups = Backups(Store(db), data)
        status = await backups.make()
        if status.warning:
            raise RuntimeError("Copied-data backup failed; private output suppressed")
        return backups.files()[-1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--previous", required=True)
    args = parser.parse_args()
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="workbench-backup-rehearsal-") as temp:
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
        baseline = digest(before)
        restore(before, data)
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
            db.execute("PRAGMA foreign_keys=ON")
            db.execute("INSERT INTO folders VALUES ('invented-folder','Invented restore folder',0,'2026-10-05','2026-10-05')")
            db.execute("INSERT INTO chats(id,title,created_at,updated_at,folder_id) VALUES ('invented-chat','Invented restore chat','2026-10-05','2026-10-05','invented-folder')")
            db.execute("INSERT INTO messages(id,chat_id,role,content,created_at,updated_at) VALUES ('invented-message','invented-chat','user','Invented restore text','2026-10-05','2026-10-05')")
            db.commit()
        backup = asyncio.run(automatic(data))
        expected = digest(backup)
        with sqlite3.connect(data / "workbench.db") as db:
            db.execute("PRAGMA foreign_keys=ON")
            db.execute("DELETE FROM chats WHERE id='invented-chat'")
            db.execute("DELETE FROM folders WHERE id='invented-folder'")
            db.commit()
        restore(backup, data)
        restored_new = boot(ROOT, data)
        auto_rows = digest(data / "workbench.db") == expected
        restore(before, data)
        restored_old = boot(old, data)
        old_rows = digest(data / "workbench.db") == baseline
        result = {"previous_commit": args.previous, "new_app": upgraded,
                  "automatic_restore_app":restored_new, "automatic_restore_rows_identical":auto_rows,
                  "restored_previous_app":restored_old,"old_rows_identical":old_rows,
                  "automatic_backup_private":backup.stat().st_mode & 0o777 == 0o600,
                  "seconds":round(time.monotonic()-started,3),
                  "method":"Private full data-folder copy; SQLite online backup; schema upgrade; invented folder/chat; real automatic backup; clean DB restore without WAL/SHM; old-schema backup restore and previous-app boot",
                  "production_modified":False,"model_calls":0,"private_copy_removed":True}
        assert auto_rows and old_rows and result["automatic_backup_private"]
        assert upgraded["schema_version"]==7 and restored_new["schema_version"]==7 and restored_old["schema_version"]==6
        assert all(r["health_status"]==200 and r["shell_status"]==200 for r in (upgraded,restored_new,restored_old))
        print(json.dumps(result,indent=2))


if __name__ == "__main__":
    main()
