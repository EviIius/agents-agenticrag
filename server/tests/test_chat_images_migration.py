"""G7: project every original column before and after additive migration 013."""

import shutil
import sqlite3
from pathlib import Path

import aiosqlite

from app.db.core import MIGRATIONS, migrate
from tests.test_phase4_guards import snapshot


async def test_chat_images_preserves_populated_v12_rows(tmp_path: Path) -> None:
    target = tmp_path / "fake-v12.db"
    shutil.copyfile(Path(__file__).parent / "fixtures/db/phase3.db", target)
    with sqlite3.connect(target) as db:
        for migration in sorted(MIGRATIONS.glob("*.sql")):
            version = int(migration.name.split("_")[0])
            if 4 < version <= 12:
                db.executescript(migration.read_text() + f"\nPRAGMA user_version={version};")
        db.execute(
            "INSERT INTO image_jobs(id,request_key,input_json,state,stage,created_at,"
            "updated_at) VALUES('fake-image','fake-key','{}','cancelled','Cancelled',"
            "'2026-10-13','2026-10-13')"
        )
        db.commit()
    columns, before = snapshot(target)
    async with aiosqlite.connect(target) as db:
        await db.execute("PRAGMA foreign_keys=ON")
        await migrate(db)
        assert await (await db.execute("PRAGMA user_version")).fetchone() == (14,)
        assert not await (await db.execute("PRAGMA foreign_key_check")).fetchall()
        assert await (await db.execute("PRAGMA integrity_check")).fetchone() == ("ok",)
        assert not await (await db.execute("SELECT id FROM messages WHERE kind!='text'")).fetchall()
        await migrate(db)
    assert snapshot(target, columns)[1] == before
