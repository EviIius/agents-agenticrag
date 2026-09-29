"""Durable, bounded progress records for workbench questions."""

from __future__ import annotations

import json
import os
import sqlite3
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class WorkbenchRunStore:
    def __init__(self, path: str | Path) -> None:
        self._lock = threading.RLock()
        if str(path) != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(str(path), check_same_thread=False)
        self._db.row_factory = sqlite3.Row
        self._db.execute("PRAGMA busy_timeout=5000")
        self._db.execute("""
            CREATE TABLE IF NOT EXISTS runs (
                id TEXT PRIMARY KEY, chat_id TEXT NOT NULL, question TEXT NOT NULL,
                workflow TEXT NOT NULL, status TEXT NOT NULL, created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL, events_json TEXT NOT NULL DEFAULT '[]',
                streamed_text TEXT NOT NULL DEFAULT '', result_json TEXT,
                error TEXT, cancel_requested INTEGER NOT NULL DEFAULT 0
            )
        """)
        # A server restart cannot continue an in-flight model request. Say so explicitly.
        self._db.execute(
            "UPDATE runs SET status='interrupted', error='Server restarted during this run', "
            "updated_at=? WHERE status IN ('queued', 'running')", (_now(),)
        )
        self._db.execute(
            "DELETE FROM runs WHERE status IN ('completed','failed','stopped','interrupted') "
            "AND updated_at < ?",
            ((datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),),
        )
        self._db.commit()
        if str(path) != ":memory:" and os.name == "posix":
            Path(path).chmod(0o600)

    def create(self, run_id: str, chat_id: str, question: str, workflow: str) -> None:
        with self._lock:
            self._db.execute(
                "INSERT INTO runs(id,chat_id,question,workflow,status,created_at,updated_at) "
                "VALUES(?,?,?,?,'queued',?,?)",
                (run_id, chat_id, question, workflow, _now(), _now()),
            )
            self._db.commit()

    def get(self, run_id: str) -> dict[str, Any] | None:
        with self._lock:
            row = self._db.execute("SELECT * FROM runs WHERE id=?", (run_id,)).fetchone()
        if row is None:
            return None
        return {
            "run_id": row["id"], "chat_id": row["chat_id"], "question": row["question"],
            "workflow": row["workflow"], "status": row["status"],
            "created_at": row["created_at"], "updated_at": row["updated_at"],
            "events": json.loads(row["events_json"]), "streamed_text": row["streamed_text"],
            "result": json.loads(row["result_json"]) if row["result_json"] else None,
            "error": row["error"], "cancel_requested": bool(row["cancel_requested"]),
        }

    def update(self, run_id: str, *, status: str | None = None, event: dict[str, Any] | None = None,
               streamed_text: str | None = None, result: dict[str, Any] | None = None,
               error: str | None = None, cancel_requested: bool | None = None) -> None:
        with self._lock:
            current = self.get(run_id)
            if current is None:
                raise ValueError("Unknown run identifier")
            events = current["events"]
            if event is not None:
                events = (events + [event])[-400:]
            self._db.execute(
                "UPDATE runs SET status=?,updated_at=?,events_json=?,streamed_text=?,"
                "result_json=?,error=?,cancel_requested=? WHERE id=?",
                (status or current["status"], _now(), json.dumps(events, ensure_ascii=False),
                 (streamed_text if streamed_text is not None else current["streamed_text"])[:200_000],
                 json.dumps(result, ensure_ascii=False) if result is not None else
                 (json.dumps(current["result"], ensure_ascii=False) if current["result"] is not None else None),
                 error if error is not None else current["error"],
                 int(cancel_requested if cancel_requested is not None else current["cancel_requested"]), run_id),
            )
            self._db.commit()

    def active_for_chat(self, chat_id: str) -> dict[str, Any] | None:
        with self._lock:
            row = self._db.execute(
                "SELECT id FROM runs WHERE chat_id=? AND status IN ('queued','running') "
                "ORDER BY created_at DESC LIMIT 1", (chat_id,)
            ).fetchone()
        return self.get(row["id"]) if row else None

    def close(self) -> None:
        with self._lock:
            self._db.close()

    def __del__(self) -> None:
        try:
            self._db.close()
        except (AttributeError, sqlite3.Error):
            pass
