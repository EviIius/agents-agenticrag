"""Migration 012 leaves populated v11 definitions, attempts and sources intact."""

import shutil
import sqlite3
from pathlib import Path

import aiosqlite

from app.db.core import MIGRATIONS, migrate
from tests.test_phase4_guards import snapshot


async def test_run_modes_migration_preserves_populated_v11_rows(tmp_path: Path) -> None:
    target = tmp_path / "fake-v11.db"
    shutil.copyfile(Path(__file__).parent / "fixtures/db/phase3.db", target)
    with sqlite3.connect(target) as db:
        for migration in sorted(MIGRATIONS.glob("*.sql")):
            version = int(migration.name.split("_")[0])
            if 4 < version <= 11:
                db.executescript(migration.read_text() + f"\nPRAGMA user_version={version};")
        db.execute(
            "INSERT INTO workflow_defs(id,name,graph_json,graph_hash,"
            "created_at,updated_at)"
            " VALUES('fake-def','Synthetic','{}','fake-hash','2026-10-13',"
            "'2026-10-13')"
        )
        db.execute(
            "INSERT INTO workflow_def_snapshots(id,def_id,graph_hash,"
            "graph_json,created_at)"
            " VALUES('fake-snapshot','fake-def','fake-hash','{}','2026-10-13')"
        )
        db.execute(
            "INSERT INTO workflow_graph_runs(id,request_key,request_json,"
            "def_id,def_name,snapshot_id,graph_hash,inputs_json,state,stage,"
            "created_at,updated_at)"
            " VALUES('fake-run','fake-key','{}','fake-def','Synthetic',"
            "'fake-snapshot','fake-hash','{}','complete','Done','2026-10-13',"
            "'2026-10-13')"
        )
        db.execute(
            "INSERT INTO workflow_graph_steps(run_id,node_id,state,attempt,"
            "port,output_json)"
            " VALUES('fake-run','n_start','complete',1,'out',"
            '\'{"brief":"Synthetic source"}\')'
        )
        db.execute(
            "INSERT INTO workflow_graph_attempts(run_id,node_id,attempt,"
            "input_json,output_json,state,started_at,finished_at)"
            " VALUES('fake-run','n_start',1,'{}','{}','complete','2026-10-13',"
            "'2026-10-13')"
        )
        db.execute(
            "INSERT INTO workflow_graph_sources(run_id,node_id,source_json,"
            "sha256) VALUES('fake-run','n_start','{\"text\":\"Synthetic"
            " original\"}','fake-sha')"
        )
        db.execute("INSERT INTO workflow_graph_events(run_id,data_json) VALUES('fake-run','{}')")
        db.commit()
    columns, before = snapshot(target)
    async with aiosqlite.connect(target) as db:
        await db.execute("PRAGMA foreign_keys=ON")
        await migrate(db)
        assert not await (await db.execute("PRAGMA foreign_key_check")).fetchall()
        integrity = await (await db.execute("PRAGMA integrity_check")).fetchone()
        assert integrity and integrity[0] == "ok"
        assert (
            await (
                await db.execute("SELECT mode,parent_run_id,expires_at FROM workflow_graph_runs")
            ).fetchone()
        ) == ("run", None, None)
        assert (
            await (
                await db.execute("SELECT reused_from,guard_json FROM workflow_graph_steps")
            ).fetchone()
        ) == (None, None)
    assert snapshot(target, columns)[1] == before
