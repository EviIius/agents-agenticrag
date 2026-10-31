"""Migration 011 preserves all old tables, including populated legacy workflows."""

import shutil
import sqlite3
from pathlib import Path

import aiosqlite

from app.db.core import MIGRATIONS, migrate
from tests.test_phase4_guards import snapshot


async def test_workflow_graph_migration_preserves_every_preexisting_column(tmp_path: Path) -> None:
    target = tmp_path / "fake-workflow-migration.db"
    shutil.copyfile(Path(__file__).parent / "fixtures/db/phase3.db", target)
    with sqlite3.connect(target) as db:
        for migration in sorted(MIGRATIONS.glob("*.sql")):
            number = int(migration.name.split("_", 1)[0])
            if 4 < number <= 10:
                db.executescript(migration.read_text() + f"\nPRAGMA user_version={number};")
        db.execute(
            "INSERT INTO workflow_runs(id,request_key,input_json,state,stage,s"
            "ource_json,edited_prompt,created_at,updated_at) "
            "VALUES('fake-run','fake-key','{}','paused','Fake "
            "stage','{}','Fake prompt','2026-10-12','2026-10-12')"
        )
        db.execute(
            "INSERT INTO workflow_steps(run_id,position,kind,label,state,attem"
            "pt,output_json) VALUES('fake-run',0,'prompt','Fake "
            "prompt','complete',1,'{\"text\":\"Fake result\"}')"
        )
        db.execute(
            "INSERT INTO workflow_attempts(run_id,position,attempt,input_json,"
            "output_json,state,started_at,finished_at) "
            "VALUES('fake-run',0,1,'{}','{}','complete','2026-10-12','2026-10-"
            "12')"
        )
        db.execute("INSERT INTO workflow_events(run_id,data_json) VALUES('fake-run','{}')")
        db.commit()
    columns, before = snapshot(target)
    async with aiosqlite.connect(target) as db:
        await db.execute("PRAGMA foreign_keys=ON")
        await migrate(db)
        assert (await (await db.execute("PRAGMA foreign_key_check")).fetchall()) == []
        integrity = await (await db.execute("PRAGMA integrity_check")).fetchone()
        version = await (await db.execute("PRAGMA user_version")).fetchone()
        assert integrity and integrity[0] == "ok"
        assert version and version[0] == 15
    assert snapshot(target, columns)[1] == before
    with sqlite3.connect(target) as db:
        assert db.execute("SELECT COUNT(*) FROM workflow_graph_runs").fetchone()[0] == 0
        assert db.execute("SELECT COUNT(*) FROM workflow_graph_sources").fetchone()[0] == 0
