import asyncio
import hashlib
import json
import sqlite3
from pathlib import Path

import httpx
import pytest
from fastapi import FastAPI

from app.db.core import Store, connect
from app.db.legacy import import_legacy

pytest_plugins = ["tests.test_chat"]


def legacy_file(path: Path, malformed: bool = False) -> Path:
    with sqlite3.connect(path) as db:
        db.executescript("""
        CREATE TABLE conversations (id TEXT PRIMARY KEY,title TEXT,created_at REAL,updated_at REAL);
        CREATE TABLE conversation_messages (id INTEGER PRIMARY KEY,conversation_id TEXT,role TEXT,
          content TEXT,result_json TEXT,created_at REAL);
        INSERT INTO conversations VALUES ('synthetic-old','Synthetic old chat',1,2);
        INSERT INTO conversation_messages
          VALUES (1,'synthetic-old','user','Synthetic question',NULL,1);
        """)
        db.execute(
            "INSERT INTO conversation_messages VALUES (2,'synthetic-old',?,?,?,2)",
            (
                "invalid" if malformed else "assistant",
                "Wrong legacy display",
                json.dumps({"answer": "Synthetic final answer"}),
            ),
        )
    return path


@pytest.mark.asyncio
async def test_import_is_read_only_linear_searchable_and_idempotent(tmp_path: Path) -> None:
    source = legacy_file(tmp_path / "old.db")
    before = hashlib.sha256(source.read_bytes()).hexdigest(), source.stat().st_mtime_ns
    async with connect(tmp_path / "new") as db:
        store = Store(db)
        assert await import_legacy(store, source) == (1, 0)
        chats = await store.rows("SELECT * FROM chats")
        assert chats[0]["title"] == "Synthetic old chat · Imported"
        assert chats[0]["title_source"] == "user"
        messages = await store.rows("SELECT * FROM messages ORDER BY created_at")
        assert messages[0]["parent_id"] is None
        assert messages[1]["parent_id"] == messages[0]["id"]
        assert messages[1]["content"] == "Synthetic final answer"
        assert chats[0]["current_leaf_id"] == messages[1]["id"]
        assert (
            len(await store.rows("SELECT * FROM chat_search WHERE chat_search MATCH 'final'")) == 1
        )
        assert await import_legacy(store, source) == (0, 1)
        assert len(await store.rows("SELECT * FROM messages")) == 2
    assert (hashlib.sha256(source.read_bytes()).hexdigest(), source.stat().st_mtime_ns) == before
    assert not list(tmp_path.glob("old.db-*"))


@pytest.mark.asyncio
async def test_concurrent_imports_and_invalid_input_rollback(tmp_path: Path) -> None:
    source = legacy_file(tmp_path / "old.db")
    bad = legacy_file(tmp_path / "bad.db", malformed=True)
    async with connect(tmp_path / "new") as db:
        store = Store(db)
        with pytest.raises(sqlite3.IntegrityError):
            await import_legacy(store, bad)
        assert not await store.rows("SELECT * FROM chats")
        assert not await store.rows("SELECT * FROM legacy_imports")
        results = await asyncio.gather(import_legacy(store, source), import_legacy(store, source))
        assert sorted(results) == [(0, 1), (1, 0)]
        assert len(await store.rows("SELECT * FROM chats")) == 1


async def test_legacy_import_api_preserves_source_and_reports_failure(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI],
    tmp_path: Path,
) -> None:
    app, client, _ = chat_app
    source = legacy_file(tmp_path / "legacy.db")
    app.state.config.legacy_db = source
    before = hashlib.sha256(source.read_bytes()).hexdigest()
    assert (await client.get("/api/chats/legacy-import")).json() == {"available": True}
    assert (await client.post("/api/chats/legacy-import")).json() == {"imported": 1, "skipped": 0}
    assert (await client.post("/api/chats/legacy-import")).json() == {"imported": 0, "skipped": 1}
    assert hashlib.sha256(source.read_bytes()).hexdigest() == before
    assert (await client.get("/api/chats?q=final")).json()["items"][0]["title"].endswith("Imported")
    app.state.config.legacy_db = tmp_path / "missing.db"
    assert (await client.post("/api/chats/legacy-import")).status_code == 404
    broken = tmp_path / "broken.db"
    broken.write_text("synthetic invalid sqlite")
    app.state.config.legacy_db = broken
    assert (await client.post("/api/chats/legacy-import")).status_code == 422
    assert len((await client.get("/api/chats")).json()["items"]) == 1


@pytest.mark.asyncio
async def test_wal_import_preserves_legacy_database_and_sidecars(tmp_path: Path) -> None:
    source = legacy_file(tmp_path / "old.db")
    with sqlite3.connect(source) as old:
        old.execute("PRAGMA journal_mode=WAL")
        old.execute("PRAGMA wal_autocheckpoint=0")
        old.execute("INSERT INTO conversations VALUES ('wal-chat','Synthetic WAL chat',3,4)")
        old.execute(
            "INSERT INTO conversation_messages VALUES "
            "(3,'wal-chat','user','Synthetic WAL question',NULL,3)"
        )
        old.commit()
        files = [
            source,
            source.with_name(source.name + "-wal"),
            source.with_name(source.name + "-shm"),
        ]
        before = [(hashlib.sha256(p.read_bytes()).hexdigest(), p.stat().st_mtime_ns) for p in files]
        async with connect(tmp_path / "new") as db:
            store = Store(db)
            assert await import_legacy(store, source) == (2, 0)
            assert await store.one("SELECT id FROM messages WHERE content='Synthetic WAL question'")
        assert [
            (hashlib.sha256(p.read_bytes()).hexdigest(), p.stat().st_mtime_ns) for p in files
        ] == before
