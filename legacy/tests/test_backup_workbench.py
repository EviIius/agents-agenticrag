from __future__ import annotations

import sqlite3
import subprocess
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "backup_workbench.py"


class BackupWorkbenchTests(unittest.TestCase):
    def test_backup_restore_and_integrity_check(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            live = root / "live" / "corpus.db"
            live.parent.mkdir()
            for path in (live, live.with_name("workbench-chats.db"), live.with_name("workbench-runs.db")):
                with closing(sqlite3.connect(path)) as db:
                    db.execute("CREATE TABLE sample (value TEXT)")
                    db.execute("INSERT INTO sample VALUES (?)", (path.name,))
                    db.commit()
            archive = root / "snapshot"
            subprocess.run([sys.executable, str(SCRIPT), "--db", str(live), "--backup", str(archive)],
                           check=True, capture_output=True, text=True)
            restored = root / "restored" / "corpus.db"
            subprocess.run([sys.executable, str(SCRIPT), "--db", str(restored), "--restore", str(archive)],
                           check=True, capture_output=True, text=True)
            for path in (restored, restored.with_name("workbench-chats.db"), restored.with_name("workbench-runs.db")):
                with closing(sqlite3.connect(path)) as db:
                    self.assertEqual(db.execute("SELECT value FROM sample").fetchone()[0], path.name)
            with self.assertRaises(subprocess.CalledProcessError):
                subprocess.run([sys.executable, str(SCRIPT), "--db", str(restored), "--restore", str(archive)],
                               check=True, capture_output=True, text=True)
            (archive / "corpus.db").write_bytes(b"tampered")
            with self.assertRaises(subprocess.CalledProcessError):
                subprocess.run([sys.executable, str(SCRIPT), "--db", str(root / "another" / "corpus.db"),
                                "--restore", str(archive)], check=True, capture_output=True, text=True)
