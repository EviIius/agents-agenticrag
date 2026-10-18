"""G7: migration 014 adds nullable/default metadata without changing old rows."""

import shutil
import sqlite3
from pathlib import Path

import aiosqlite

from app.db.core import MIGRATIONS, migrate
from tests.test_phase4_guards import snapshot


async def test_agent_migration_keeps_all_v13_columns_and_rows(tmp_path: Path) -> None:
    target = tmp_path / "fake-agent-v13.db"
    shutil.copyfile(Path(__file__).parent / "fixtures/db/phase3.db", target)
    with sqlite3.connect(target) as db:
        for migration in sorted(MIGRATIONS.glob("*.sql")):
            version = int(migration.name.split("_")[0])
            if 4 < version <= 13:
                db.executescript(migration.read_text() + f"\nPRAGMA user_version={version};")
    columns, before = snapshot(target)
    async with aiosqlite.connect(target) as db:
        await db.execute("PRAGMA foreign_keys=ON")
        await migrate(db)
        assert await (await db.execute("PRAGMA user_version")).fetchone() == (14,)
        assert not await (await db.execute("PRAGMA foreign_key_check")).fetchall()
        assert await (await db.execute("PRAGMA integrity_check")).fetchone() == ("ok",)
        assert all(
            row == ("[]", None)
            for row in await (
                await db.execute("SELECT parts_json,agent_json FROM messages")
            ).fetchall()
        )
        await migrate(db)
    assert snapshot(target, columns)[1] == before
