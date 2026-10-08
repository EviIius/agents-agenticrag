import importlib
import json
import shutil
import sqlite3
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any, cast

import aiosqlite
import httpx
from fastapi import FastAPI

from app.db.core import migrate
from tests.test_chat import chat_app as chat_app
from tests.test_chat import finish, start

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
compare = cast(
    Callable[[Any, Any], list[str]], importlib.import_module("check_api_additive").compare
)
violations = cast(Callable[[Path], list[str]], importlib.import_module("check_motion").violations)


async def test_default_request_matches_phase3_golden(
    chat_app: tuple[FastAPI, httpx.AsyncClient, FastAPI],
) -> None:
    app, client, runtime = chat_app
    await client.patch("/api/settings", json={"include_current_date": False})
    response = await start(client, "Synthetic default request", "fake-chat")
    await finish(app, response)
    captured = [body for body in runtime.state.captures if body.get("messages")][-1]
    expected = json.loads((ROOT / "artifacts/baseline/ordinary-chat-phase3.json").read_text())
    assert json.dumps(captured, sort_keys=True, separators=(",", ":")) == json.dumps(
        expected, sort_keys=True, separators=(",", ":")
    )
    assert set(captured["options"]) == {"num_ctx"}
    assert "tools" not in captured


def snapshot(
    path: Path, columns: dict[str, list[str]] | None = None
) -> tuple[dict[str, list[str]], dict[str, list[Any]]]:
    with sqlite3.connect(path) as db:
        if columns is None:
            tables = [
                row[0]
                for row in db.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
                )
            ]
            columns = {
                table: [row[1] for row in db.execute(f'PRAGMA table_info("{table}")')]
                for table in tables
            }
        rows = {}
        for table, names in columns.items():
            projection = ",".join('"' + name + '"' for name in names)
            rows[table] = sorted(
                db.execute(f'SELECT {projection} FROM "{table}"').fetchall(), key=repr
            )
        return columns, rows


async def test_phase3_database_rows_survive_current_migrations(tmp_path: Path) -> None:
    target = tmp_path / "phase3.db"
    shutil.copyfile(ROOT / "server/tests/fixtures/db/phase3.db", target)
    columns, before = snapshot(target)
    async with aiosqlite.connect(target) as db:
        await db.execute("PRAGMA foreign_keys=ON")
        await migrate(db)
        assert (await (await db.execute("PRAGMA foreign_key_check")).fetchall()) == []
    assert snapshot(target, columns)[1] == before


def test_api_guard_rejects_removal_type_changes_and_new_required_fields() -> None:
    old: dict[str, Any] = {"properties": {"value": {"type": "string"}}, "required": ["value"]}
    assert not compare(
        old, {**old, "properties": {**old["properties"], "added": {"type": "number"}}}
    )
    assert compare(old, {"properties": {}, "required": ["value"]})
    assert compare(old, {"properties": {"value": {"type": "number"}}, "required": ["value"]})
    assert compare(old, {**old, "required": ["value", "added"]})
    assert compare({"properties": {}}, {"properties": {}, "required": ["added"]})
    assert not compare({"enum": ["old"]}, {"enum": ["old", "new"]})


def test_motion_guard_rejects_dead_classes_and_forbidden_keyframes(tmp_path: Path) -> None:
    (tmp_path / "styles").mkdir()
    (tmp_path / "bad.tsx").write_text("data-[state=open]:animate-in transition-all")
    (tmp_path / "styles/motion.css").write_text("@keyframes unused { from { color: red; } }")
    errors = violations(tmp_path)
    assert any("animate-in" in error for error in errors)
    assert any("transition-all" in error for error in errors)
    assert any("forbidden color" in error for error in errors)
    assert any("unused keyframe" in error for error in errors)
    (tmp_path / "bad.tsx").unlink()
    (tmp_path / "styles/motion.css").write_text(
        "@keyframes reveal { from { opacity: 0; transform: translateY(4px); } } "
        "[data-live] { animation: reveal 200ms; }"
    )
    assert violations(tmp_path) == []
