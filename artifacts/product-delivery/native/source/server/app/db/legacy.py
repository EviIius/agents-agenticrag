"""Read-only, idempotent import of Chat & Web 0.5 conversations."""

import asyncio
import json
import shutil
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import NAMESPACE_URL, uuid5

from .core import Store


def read_legacy(source: Path) -> list[dict[str, object]]:
    source = source.expanduser().resolve(strict=True)
    wal = source.with_name(source.name + "-wal")

    def fingerprint() -> tuple[tuple[int, int, int] | None, ...]:
        return tuple(
            (p.stat().st_ino, p.stat().st_size, p.stat().st_mtime_ns) if p.exists() else None
            for p in (source, wal)
        )

    # SQLite mode=ro can still create/update shared-memory sidecars for a WAL.
    # Read the source files into a private temporary snapshot, including committed
    # WAL frames, and let SQLite open only that copy. Refuse a moving source.
    with TemporaryDirectory(prefix="workbench-legacy-") as directory:
        copy = Path(directory) / "legacy.db"
        before = fingerprint()
        copy.touch(mode=0o600)
        shutil.copyfile(source, copy)
        if wal.exists():
            copy_wal = copy.with_name(copy.name + "-wal")
            copy_wal.touch(mode=0o600)
            shutil.copyfile(wal, copy_wal)
        if fingerprint() != before:
            raise ValueError("The old database changed during import. Stop its service and retry.")
        return read_snapshot(copy)


def read_snapshot(source: Path) -> list[dict[str, object]]:
    with sqlite3.connect(source.as_uri() + "?mode=ro", uri=True) as db:
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA query_only=ON")
        result: list[dict[str, object]] = []
        for row in db.execute(
            "SELECT id,title,created_at,updated_at FROM conversations ORDER BY created_at,id"
        ):
            messages = []
            for message in db.execute(
                "SELECT id,role,content,result_json,created_at FROM conversation_messages "
                "WHERE conversation_id=? ORDER BY id",
                (row["id"],),
            ):
                content = message["content"]
                if message["role"] == "assistant" and message["result_json"]:
                    try:
                        answer = json.loads(message["result_json"]).get("answer")
                        if isinstance(answer, str):
                            content = answer
                    except (ValueError, AttributeError):
                        pass
                messages.append(
                    {
                        "id": message["id"],
                        "role": message["role"],
                        "content": content,
                        "created_at": message["created_at"],
                    }
                )
            result.append({**dict(row), "messages": messages})
        return result


def timestamp(value: object) -> str:
    return datetime.fromtimestamp(float(str(value)), UTC).isoformat()


def identifier(kind: str, value: str) -> str:
    return uuid5(NAMESPACE_URL, "workbench:legacy:" + kind + ":" + value).hex


async def import_legacy(store: Store, source: Path) -> tuple[int, int]:
    rows = await asyncio.to_thread(read_legacy, source)
    imported = skipped = 0
    # Hold the same transaction lock as regular writes, making concurrent API/CLI
    # imports atomic. The unique legacy mapping protects repeated imports.
    async with store.lock:
        await store.db.execute("BEGIN")
        try:
            for row in rows:
                old_id = str(row["id"])
                async with store.db.execute(
                    "SELECT 1 FROM legacy_imports WHERE legacy_id=?", (old_id,)
                ) as cursor:
                    if await cursor.fetchone():
                        skipped += 1
                        continue
                chat_id = identifier("chat", old_id)
                title = str(row["title"]) + " · Imported"
                await store.db.execute(
                    "INSERT INTO chats(id,title,title_source,created_at,updated_at) "
                    "VALUES (?,?,'user',?,?)",
                    (chat_id, title, timestamp(row["created_at"]), timestamp(row["updated_at"])),
                )
                parent = None
                old_messages = row["messages"]
                assert isinstance(old_messages, list)
                for message in old_messages:
                    assert isinstance(message, dict)
                    mid = identifier("message", old_id + ":" + str(message["id"]))
                    date = timestamp(message["created_at"])
                    await store.db.execute(
                        "INSERT INTO messages(id,chat_id,parent_id,role,content,"
                        "created_at,updated_at) "
                        "VALUES (?,?,?,?,?,?,?)",
                        (mid, chat_id, parent, message["role"], message["content"], date, date),
                    )
                    await store.db.execute(
                        "INSERT INTO chat_search(chat_id,message_id,title,content) "
                        "VALUES (?,?,?,?)",
                        (chat_id, mid, title, message["content"]),
                    )
                    parent = mid
                await store.db.execute(
                    "UPDATE chats SET current_leaf_id=? WHERE id=?", (parent, chat_id)
                )
                await store.db.execute(
                    "INSERT INTO legacy_imports(legacy_id,chat_id) VALUES (?,?)", (old_id, chat_id)
                )
                imported += 1
            await store.db.commit()
        except BaseException:
            await store.db.rollback()
            raise
    return imported, skipped
