"""One SQLite database, numbered migrations, and no legacy imports."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

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


class Store:
    """Serialize commits on the shared SQLite connection, including multi-row mutations."""

    def __init__(self, db: aiosqlite.Connection) -> None:
        import asyncio

        self.db = db
        self.lock = asyncio.Lock()

    async def rows(self, sql: str, params: tuple[object, ...] = ()) -> list[dict[str, Any]]:
        async with self.lock, self.db.execute(sql, params) as cursor:
            keys = [d[0] for d in cursor.description or []]
            return [dict(zip(keys, row, strict=True)) for row in await cursor.fetchall()]

    async def one(self, sql: str, params: tuple[object, ...] = ()) -> dict[str, Any] | None:
        rows = await self.rows(sql, params)
        return rows[0] if rows else None

    async def batch(self, statements: list[tuple[str, tuple[object, ...]]]) -> None:
        async with self.lock:
            try:
                await self.db.execute("BEGIN")
                for sql, params in statements:
                    await self.db.execute(sql, params)
                await self.db.commit()
            except BaseException:
                await self.db.rollback()
                raise

    async def execute(self, sql: str, params: tuple[object, ...] = ()) -> None:
        await self.batch([(sql, params)])
