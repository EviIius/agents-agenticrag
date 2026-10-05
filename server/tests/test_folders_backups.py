import asyncio
import shutil
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import aiosqlite
import httpx
import pytest
from fastapi import FastAPI

from app.backup import Backups, next_delay
from app.db.core import MIGRATIONS, Store, connect, migrate
from tests.test_chat import finish, start
from tests.test_phase4_guards import snapshot


async def test_folders_crud_move_filters_search_and_delete_keeps_chats(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI],
) -> None:
    app, client, _ = chat_app
    response = await start(client, "Invented lantern discussion")
    await finish(app, response)
    chat_id = response["user_message"]["chat_id"]
    before = (await client.get("/api/chats")).json()["items"]
    assert (await client.get("/api/chats?folder=none")).json()["items"] == before
    folder = (await client.post("/api/folders", json={"name": "  Invented Orchard  "})).json()
    assert folder["name"] == "Invented Orchard" and folder["count"] == 0
    assert (await client.post("/api/folders", json={"name": " "})).status_code == 422
    assert (
        await client.patch(f"/api/chats/{chat_id}", json={"folder_id": "missing"})
    ).status_code == 404
    moved = (await client.patch(f"/api/chats/{chat_id}", json={"folder_id": folder["id"]})).json()
    assert moved["folder_id"] == folder["id"] and moved["folder_name"] == folder["name"]
    assert (await client.get("/api/folders")).json()[0]["count"] == 1
    assert not (await client.get("/api/chats?folder=none")).json()["items"]
    assert (await client.get(f"/api/chats?folder={folder['id']}")).json()["items"][0][
        "id"
    ] == chat_id
    assert (await client.get("/api/chats?q=lantern")).json()["items"][0]["folder_name"] == folder[
        "name"
    ]
    assert {c["id"] for c in (await client.get("/api/chats")).json()["items"]} == {
        c["id"] for c in before
    }
    # Absent means leave assignment; explicit null means remove it.
    assert (await client.patch(f"/api/chats/{chat_id}", json={"pinned": True})).json()[
        "folder_id"
    ] == folder["id"]
    assert (await client.patch(f"/api/chats/{chat_id}", json={"folder_id": None})).json()[
        "folder_id"
    ] is None
    await client.patch(f"/api/chats/{chat_id}", json={"folder_id": folder["id"]})
    changed = await client.patch(
        f"/api/folders/{folder['id']}", json={"name": "Invented Meadow", "position": 3}
    )
    assert changed.json()["name"] == "Invented Meadow" and changed.json()["position"] == 3
    assert (
        await client.patch(f"/api/folders/{folder['id']}", json={"name": None})
    ).status_code == 422
    assert (
        await client.patch(f"/api/folders/{folder['id']}", json={"position": None})
    ).status_code == 422
    old_messages = (await client.get(f"/api/chats/{chat_id}")).json()["messages"]
    assert (await client.delete(f"/api/folders/{folder['id']}")).status_code == 204
    detail = (await client.get(f"/api/chats/{chat_id}")).json()
    assert detail["chat"]["folder_id"] is None and detail["messages"] == old_messages
    assert (await client.get("/api/folders")).json() == []
    assert (await client.delete(f"/api/folders/{folder['id']}")).status_code == 404


async def test_folder_pagination_and_empty_chats_count(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI],
) -> None:
    app, client, _ = chat_app
    folder = (await client.post("/api/folders", json={"name": "Invented paged folder"})).json()
    statements = []
    for i in range(55):
        statements.extend(
            [
                (
                    "INSERT INTO chats(id,title,created_at,updated_at,folder_id) "
                    "VALUES (?,?,?,?,?)",
                    (
                        f"invented-{i:02}",
                        "Invented paged chat",
                        "2026-10-05",
                        f"2026-10-05T00:00:{i:02}",
                        folder["id"],
                    ),
                ),
                (
                    "INSERT INTO messages(id,chat_id,role,content,created_at,updated_at) "
                    "VALUES (?,?,'user','Invented',?,?)",
                    (f"invented-m{i}", f"invented-{i:02}", "2026-10-05", "2026-10-05"),
                ),
            ]
        )
    statements.append(
        (
            "INSERT INTO chats(id,created_at,updated_at,folder_id) "
            "VALUES ('empty','2026-10-05','2026-10-05',?)",
            (folder["id"],),
        )
    )
    await app.state.store.batch(statements)
    first = (await client.get("/api/chats", params={"folder": folder["id"]})).json()
    second = (
        await client.get(
            "/api/chats", params={"folder": folder["id"], "cursor": first["next_cursor"]}
        )
    ).json()
    assert len(first["items"]) == 50 and len(second["items"]) == 5 and second["next_cursor"] is None
    assert len({c["id"] for c in first["items"] + second["items"]}) == 55
    assert (await client.get("/api/folders")).json()[0]["count"] == 55


async def test_phase5b_migration_preserves_every_existing_column(tmp_path: Path) -> None:
    dbpath = tmp_path / "phase5b.db"
    shutil.copy2(Path(__file__).parent / "fixtures/db/phase3.db", dbpath)
    async with aiosqlite.connect(dbpath) as db:
        for p in sorted(MIGRATIONS.glob("*.sql")):
            n = int(p.name.split("_")[0])
            if 4 < n <= 6:
                await db.executescript(p.read_text() + f"\nPRAGMA user_version={n};")
        await db.commit()
        columns, before = snapshot(dbpath)
        await migrate(db)
    assert snapshot(dbpath, columns)[1] == before
    with sqlite3.connect(dbpath) as db:
        assert db.execute("PRAGMA user_version").fetchone()[0] == 7
        assert all(r[0] is None for r in db.execute("SELECT folder_id FROM chats"))
        assert db.execute("SELECT COUNT(*) FROM folders").fetchone()[0] == 0


async def test_backup_startup_online_rows_permissions_and_manual(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI],
) -> None:
    app, client, _ = chat_app
    status = (await client.get("/api/backup")).json()
    assert status["count"] == 1 and status["last_at"] and status["warning"] is None
    response = await start(client, "Invented backup conversation")
    await finish(app, response)
    result = await client.post("/api/backup", json={})
    assert result.status_code == 200 and result.json()["bytes"] > 0
    files = list((app.state.config.data_dir / "backups").glob("auto-*.db"))
    assert all(p.stat().st_mode & 0o777 == 0o600 for p in files)
    with sqlite3.connect(files[-1]) as copy:
        assert copy.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        for table in ["chats", "messages", "attachments", "transcripts", "settings", "folders"]:
            expected = (await app.state.store.one(f"SELECT COUNT(*) AS n FROM {table}"))["n"]
            assert copy.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] == expected


async def test_backup_retention_low_disk_fresh_start_and_stale_parts(tmp_path: Path) -> None:
    current = [datetime(2026, 10, 5, 12)]
    async with connect(tmp_path) as db:
        service = Backups(Store(db), tmp_path, clock=lambda: current[0], free=lambda _: 10**10)
        deploy = service.folder / "workbench-invented.db"
        deploy.write_bytes(b"invented deploy backup")
        part = service.folder / "auto-20261001-0000.part"
        part.touch()
        await service.start()
        await service.close()
        assert not part.exists()
        initial = service.files()[0].stat().st_mtime
        await service.start()
        await service.close()
        assert service.files()[0].stat().st_mtime == initial
        for _ in range(9):
            current[0] += timedelta(days=1)
            await service.make()
        assert len(service.files()) == 7 and deploy.read_bytes() == b"invented deploy backup"
        preserved = {p.name: p.read_bytes() for p in service.files()}
        current[0] += timedelta(days=1)
        service.free = lambda _: 0
        result = await service.make()
        assert "not enough free disk" in (result.warning or "")
        assert {p.name: p.read_bytes() for p in service.files()} == preserved
        service.free = lambda _: 10**10
        await service.start()
        await service.close()
        assert service.status().warning is None and len(service.files()) == 7
        assert service.files()[-1].stat().st_mtime == current[0].timestamp()


def test_daily_schedule_and_dst() -> None:
    assert next_delay(datetime(2026, 10, 5, 3, 29)) == 60
    assert next_delay(datetime(2026, 10, 5, 3, 30)) == 86400
    assert next_delay(datetime(2026, 10, 5, 23, 30)) == 14400
    zone = ZoneInfo("America/New_York")
    assert next_delay(datetime(2026, 11, 1, 0, 30, tzinfo=zone)) == 4 * 3600


async def test_backup_failure_cleanup_and_serialization(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    async with connect(tmp_path) as db:
        service = Backups(Store(db), tmp_path, free=lambda _: 10**10)
        original = db.backup

        async def fail(*args: Any, **kwargs: Any) -> None:
            raise sqlite3.OperationalError("Invented error suppressed")

        monkeypatch.setattr(db, "backup", fail)
        result = await service.make()
        assert result.warning and not list(service.folder.glob("*.part")) and not service.files()
        monkeypatch.setattr(db, "backup", original)
        await asyncio.gather(*(service.make() for _ in range(3)))
        assert service.status().count == 1 and service.status().warning is None
        assert not list(service.folder.glob("*.part"))


async def test_daily_timer_uses_local_target_and_shuts_down(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    async with connect(tmp_path) as db:
        current = [datetime(2026, 10, 5, 3, 29)]
        service = Backups(Store(db), tmp_path, clock=lambda: current[0], free=lambda _: 10**10)
        requested = []

        async def sleep(seconds: float) -> None:
            requested.append(seconds)
            if len(requested) > 1:
                raise asyncio.CancelledError
            current[0] += timedelta(seconds=seconds)

        monkeypatch.setattr("app.backup.asyncio.sleep", sleep)
        with pytest.raises(asyncio.CancelledError):
            await service.daily()
        assert requested == [60, 86400] and service.files()[0].name == "auto-20261005-0330.db"


async def test_cancelled_backup_waits_for_copy_then_cleans_part(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    async with connect(tmp_path) as db:
        service = Backups(Store(db), tmp_path, free=lambda _: 10**10)
        began, release = asyncio.Event(), asyncio.Event()
        original = db.backup

        async def slow(*args: Any, **kwargs: Any) -> None:
            began.set()
            await release.wait()
            await original(*args, **kwargs)

        monkeypatch.setattr(db, "backup", slow)
        running = asyncio.create_task(service.make())
        await began.wait()
        running.cancel()
        await asyncio.sleep(0)
        assert not running.done() and service.lock.locked() and service.store.lock.locked()
        release.set()
        with pytest.raises(asyncio.CancelledError):
            await running
        assert not list(service.folder.glob("*.part")) and not service.files()
        assert not service.lock.locked() and not service.store.lock.locked()


def test_api_guard_allows_only_optional_additional_query_parameters() -> None:
    from tests.test_phase4_guards import compare

    old = {
        "parameters": [
            {"in": "query", "name": "q", "required": False, "schema": {"type": "string"}}
        ]
    }
    extra = {"in": "query", "name": "folder", "required": False, "schema": {"type": "string"}}
    assert not compare(old, {"parameters": [extra, *old["parameters"]]})
    assert not compare({}, {"parameters": [extra]})
    assert compare(old, {"parameters": [*old["parameters"], {**extra, "required": True}]})
    assert compare({}, {"parameters": [{**extra, "required": True}]})
    assert compare(old, {"parameters": [extra]})
    assert compare(old, {"parameters": [{**old["parameters"][0], "schema": {"type": "integer"}}]})
    assert compare(old, {"parameters": [{**old["parameters"][0], "required": True}]})
    assert compare(old, {"parameters": [*old["parameters"], *old["parameters"]]})
