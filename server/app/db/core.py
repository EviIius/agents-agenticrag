"""One SQLite database, numbered migrations, and no legacy imports."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

import aiosqlite

MIGRATIONS = Path(__file__).parent / "migrations"


@asynccontextmanager
async def connect(data_dir: Path) -> AsyncIterator[aiosqlite.Connection]:
    data_dir = data_dir.expanduser().resolve()
    data_dir.mkdir(parents=True, exist_ok=True)
    path = data_dir / "workbench.db"
    path.touch(mode=0o600, exist_ok=True)
    path.chmod(0o600)
    async with aiosqlite.connect(path) as db:
        await db.execute("PRAGMA journal_mode=WAL")
        await db.execute("PRAGMA foreign_keys=ON")
        await db.execute("PRAGMA busy_timeout=5000")
        await migrate(db)
        yield db


async def migrate(db: aiosqlite.Connection) -> None:
    async with db.execute("PRAGMA user_version") as cursor:
        row = await cursor.fetchone()
    version = int(row[0]) if row else 0
    for migration in sorted(MIGRATIONS.glob("*.sql")):
        number = int(migration.name.split("_", 1)[0])
        if number <= version:
            continue
        script = migration.read_text()
        try:
            await db.executescript(f"BEGIN;\n{script}\nPRAGMA user_version={number};\nCOMMIT;")
        except Exception:
            await db.rollback()
            raise
        version = number
