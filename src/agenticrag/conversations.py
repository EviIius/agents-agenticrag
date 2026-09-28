"""Single-user workbench conversations persisted beside the local corpus."""

from __future__ import annotations

import json
import os
import re
import sqlite3
import threading
import time
from pathlib import Path
from uuid import uuid4

from .providers.base import ChatMessage


def conversation_title(question: str) -> str:
    """Keep the first prompt recognizable without turning it into a page heading."""
    first_line = " ".join(question.split())
    first_sentence = re.split(r"(?<=[.!?])\s+", first_line, maxsplit=1)[0]
    if len(first_sentence) <= 48:
        return first_sentence
    return first_sentence[:47].rsplit(" ", 1)[0].rstrip(" ,;:") + "…"


class ConversationStore:
    def __init__(self, path: str) -> None:
        if path != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(path, check_same_thread=False)
        self._db.row_factory = sqlite3.Row
        self._lock = threading.RLock()
        with self._db:
            self._db.execute("PRAGMA foreign_keys = ON")
            self._db.execute("PRAGMA journal_mode = WAL")
            self._db.executescript("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    collection TEXT NOT NULL,
                    scopes_json TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL
                );
                CREATE TABLE IF NOT EXISTS conversation_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
                    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
                    content TEXT NOT NULL,
                    workflow TEXT NOT NULL,
                    result_json TEXT,
                    created_at REAL NOT NULL
                );
                CREATE INDEX IF NOT EXISTS conversation_messages_by_chat
                    ON conversation_messages(conversation_id, id);
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    collection TEXT NOT NULL UNIQUE,
                    scopes_json TEXT NOT NULL,
                    created_at REAL NOT NULL
                );
                CREATE TABLE IF NOT EXISTS project_notes (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                    content TEXT NOT NULL,
                    source_chat_id TEXT REFERENCES conversations(id) ON DELETE SET NULL,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL
                );
                CREATE INDEX IF NOT EXISTS project_notes_by_project
                    ON project_notes(project_id, updated_at DESC);
                CREATE TABLE IF NOT EXISTS project_note_audit (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                    note_id TEXT NOT NULL,
                    action TEXT NOT NULL CHECK (action IN ('created', 'edited', 'deleted')),
                    created_at REAL NOT NULL
                );
            """)
            self._db.execute(
                "INSERT OR IGNORE INTO projects VALUES (?, ?, ?, ?, ?)",
                ("default", "My library", "research", '["private"]', time.time()),
            )
        if path != ":memory:" and os.name == "posix":
            # SQLite's WAL and shared-memory files can contain transcript text too.
            for suffix in ("", "-wal", "-shm"):
                sidecar = Path(path + suffix)
                if sidecar.exists():
                    sidecar.chmod(0o600)

    def create(self, collection: str, scopes: list[str]) -> dict[str, object]:
        now = time.time()
        chat_id = uuid4().hex
        with self._lock, self._db:
            self._db.execute(
                "INSERT INTO conversations VALUES (?, ?, ?, ?, ?, ?)",
                (chat_id, "New conversation", collection, json.dumps(scopes), now, now),
            )
        return self.get(chat_id)

    def list(self, *, collection: str | None = None, query: str | None = None) -> list[dict[str, object]]:
        conditions: list[str] = []
        arguments: list[object] = []
        if collection:
            conditions.append("c.collection = ?")
            arguments.append(collection)
        if query:
            conditions.append("(c.title LIKE ? ESCAPE '\\' OR EXISTS (SELECT 1 FROM conversation_messages s "
                              "WHERE s.conversation_id = c.id AND s.content LIKE ? ESCAPE '\\'))")
            pattern = "%" + query.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"
            arguments.extend((pattern, pattern))
        where = "WHERE " + " AND ".join(conditions) if conditions else ""
        with self._lock:
            rows = self._db.execute(
                f"""SELECT c.*, COUNT(m.id) AS message_count FROM conversations c
                   LEFT JOIN conversation_messages m ON m.conversation_id = c.id
                   {where} GROUP BY c.id ORDER BY c.updated_at DESC LIMIT 100""",
                arguments,
            ).fetchall()
        return [self._summary(row) for row in rows]

    def create_project(self, name: str) -> dict[str, object]:
        clean = " ".join(name.split())
        if not 1 <= len(clean) <= 64:
            raise ValueError("Project name must contain 1 to 64 characters")
        project_id = uuid4().hex
        collection = "project-" + project_id[:16]
        with self._lock, self._db:
            self._db.execute(
                "INSERT INTO projects VALUES (?, ?, ?, ?, ?)",
                (project_id, clean, collection, '["private"]', time.time()),
            )
        return self.get_project(project_id)

    def list_projects(self) -> list[dict[str, object]]:
        with self._lock:
            rows = self._db.execute(
                "SELECT * FROM projects ORDER BY CASE WHEN id = 'default' THEN 0 ELSE 1 END, created_at"
            ).fetchall()
        return [self._project(row) for row in rows]

    def get_project(self, project_id: str) -> dict[str, object]:
        with self._lock:
            row = self._db.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
        if row is None:
            raise ValueError("Project was not found")
        return self._project(row)

    def project_for_context(self, collection: str, scopes: list[str]) -> dict[str, object] | None:
        with self._lock:
            row = self._db.execute("SELECT * FROM projects WHERE collection = ?", (collection,)).fetchone()
        if row is None or set(json.loads(row["scopes_json"])) != set(scopes):
            return None
        return self._project(row)

    def list_project_notes(self, project_id: str) -> list[dict[str, object]]:
        self.get_project(project_id)
        with self._lock:
            rows = self._db.execute(
                "SELECT n.*, c.title AS source_chat_title FROM project_notes n "
                "LEFT JOIN conversations c ON c.id = n.source_chat_id "
                "WHERE n.project_id = ? ORDER BY n.updated_at DESC LIMIT 50", (project_id,)
            ).fetchall()
        return [self._note(row) for row in rows]

    def list_project_note_activity(self, project_id: str) -> list[dict[str, object]]:
        self.get_project(project_id)
        with self._lock:
            rows = self._db.execute(
                "SELECT note_id, action, created_at FROM project_note_audit "
                "WHERE project_id = ? ORDER BY id DESC LIMIT 50", (project_id,)
            ).fetchall()
        return [dict(row) for row in rows]

    def create_project_note(self, project_id: str, content: str, source_chat_id: str | None = None) -> dict[str, object]:
        project = self.get_project(project_id)
        clean = content.strip()
        if not 1 <= len(clean) <= 1_000:
            raise ValueError("Memory note must contain 1 to 1,000 characters")
        with self._lock, self._db:
            count = self._db.execute("SELECT COUNT(*) FROM project_notes WHERE project_id = ?", (project_id,)).fetchone()[0]
            if count >= 50:
                raise ValueError("Project memory is full (50 notes)")
            if source_chat_id:
                chat = self._db.execute(
                    "SELECT collection, scopes_json FROM conversations WHERE id = ?", (source_chat_id,)
                ).fetchone()
                if chat is None or chat["collection"] != project["collection"] or set(json.loads(chat["scopes_json"])) != set(project["scopes"]):
                    raise ValueError("Source conversation is outside this project")
            note_id = uuid4().hex
            now = time.time()
            self._db.execute(
                "INSERT INTO project_notes VALUES (?, ?, ?, ?, ?, ?)",
                (note_id, project_id, clean, source_chat_id, now, now),
            )
            self._db.execute(
                "INSERT INTO project_note_audit(project_id, note_id, action, created_at) VALUES (?, ?, 'created', ?)",
                (project_id, note_id, now),
            )
        return next(note for note in self.list_project_notes(project_id) if note["id"] == note_id)

    def update_project_note(self, note_id: str, content: str) -> dict[str, object]:
        clean = content.strip()
        if not 1 <= len(clean) <= 1_000:
            raise ValueError("Memory note must contain 1 to 1,000 characters")
        with self._lock, self._db:
            row = self._db.execute("SELECT project_id FROM project_notes WHERE id = ?", (note_id,)).fetchone()
            if row is None:
                raise ValueError("Memory note was not found")
            self._db.execute(
                "UPDATE project_notes SET content = ?, updated_at = ? WHERE id = ?",
                (clean, time.time(), note_id),
            )
            self._db.execute(
                "INSERT INTO project_note_audit(project_id, note_id, action, created_at) VALUES (?, ?, 'edited', ?)",
                (row["project_id"], note_id, time.time()),
            )
        return next(note for note in self.list_project_notes(row["project_id"]) if note["id"] == note_id)

    def delete_project_note(self, note_id: str) -> None:
        with self._lock, self._db:
            row = self._db.execute("SELECT project_id FROM project_notes WHERE id = ?", (note_id,)).fetchone()
            if row is None:
                raise ValueError("Memory note was not found")
            deleted = self._db.execute("DELETE FROM project_notes WHERE id = ?", (note_id,)).rowcount
            if deleted:
                self._db.execute(
                    "INSERT INTO project_note_audit(project_id, note_id, action, created_at) VALUES (?, ?, 'deleted', ?)",
                    (row["project_id"], note_id, time.time()),
                )

    def get(self, chat_id: str) -> dict[str, object]:
        with self._lock:
            row = self._db.execute(
                "SELECT * FROM conversations WHERE id = ?", (chat_id,)
            ).fetchone()
            if row is None:
                raise ValueError("Conversation was not found")
            messages = self._db.execute(
                "SELECT role, content, workflow, result_json, created_at FROM conversation_messages "
                "WHERE conversation_id = ? ORDER BY id", (chat_id,)
            ).fetchall()
        summary = self._summary(row)
        summary["messages"] = [
            {
                "role": item["role"], "content": item["content"],
                "workflow": item["workflow"],
                "result": json.loads(item["result_json"]) if item["result_json"] else None,
                "created_at": item["created_at"],
            }
            for item in messages
        ]
        return summary

    def history(self, chat_id: str, collection: str, scopes: list[str]) -> list[ChatMessage]:
        with self._lock:
            chat = self._db.execute(
                "SELECT collection, scopes_json FROM conversations WHERE id = ?", (chat_id,)
            ).fetchone()
            if chat is None:
                raise ValueError("Conversation was not found")
            messages = self._db.execute(
                "SELECT role, SUBSTR(content, 1, 1500) AS content FROM conversation_messages "
                "WHERE conversation_id = ? ORDER BY id DESC LIMIT 40", (chat_id,)
            ).fetchall()
        if chat["collection"] != collection or set(json.loads(chat["scopes_json"])) != set(scopes):
            raise ValueError("This conversation uses another knowledge base or access label")
        return [ChatMessage(item["role"], item["content"]) for item in reversed(messages)]

    def close(self) -> None:
        with self._lock:
            self._db.close()

    def __del__(self) -> None:
        try:
            self._db.close()
        except (AttributeError, sqlite3.Error):
            pass

    def record(self, chat_id: str, question: str, result: dict[str, object], workflow: str) -> None:
        answer = str(result["answer"])
        compact_result = {
            "workflow": result["workflow"],
            "abstained": result["abstained"],
            "elapsed_ms": result["elapsed_ms"],
            "citations": result["citations"],
            "external_sources": result.get("external_sources", []),
            "events": result.get("events", [])[:50],
            "retrieved_count": len(result.get("evidence", [])),
        }
        cited_ids = {
            item.get("chunk_id") for item in result.get("citations", [])
            if isinstance(item, dict)
        }
        compact_result["evidence"] = [
            {"chunk": {
                "id": chunk["id"],
                "text": str(chunk.get("text", ""))[:4_000] if chunk.get("id") in cited_ids else "",
                "heading": chunk.get("heading"),
                "logical_path": chunk.get("logical_path"),
                "section_path": chunk.get("section_path", []),
            }}
            for item in result.get("evidence", [])
            if isinstance(item, dict) and isinstance((chunk := item.get("chunk")), dict)
        ][:32]
        if result["workflow"] == "web_research":
            compact_result["events"] = [
                event for event in result.get("events", [])
                if isinstance(event, dict)
                and event.get("kind") in {"web_search_completed", "generation_completed"}
            ][:2]
        now = time.time()
        with self._lock, self._db:
            row = self._db.execute(
                "SELECT title FROM conversations WHERE id = ?", (chat_id,)
            ).fetchone()
            if row is None:
                raise ValueError("Conversation was not found")
            title = row["title"]
            if title == "New conversation":
                title = conversation_title(question) or title
            self._db.execute(
                "INSERT INTO conversation_messages(conversation_id, role, content, workflow, result_json, created_at) "
                "VALUES (?, 'user', ?, ?, NULL, ?)", (chat_id, question, workflow, now)
            )
            self._db.execute(
                "INSERT INTO conversation_messages(conversation_id, role, content, workflow, result_json, created_at) "
                "VALUES (?, 'assistant', ?, ?, ?, ?)",
                (chat_id, answer, workflow, json.dumps(compact_result, ensure_ascii=False), now),
            )
            self._db.execute(
                "UPDATE conversations SET title = ?, updated_at = ? WHERE id = ?",
                (title, now, chat_id),
            )

    def delete(self, chat_id: str) -> None:
        with self._lock, self._db:
            deleted = self._db.execute(
                "DELETE FROM conversations WHERE id = ?", (chat_id,)
            ).rowcount
        if not deleted:
            raise ValueError("Conversation was not found")

    @staticmethod
    def _summary(row: sqlite3.Row) -> dict[str, object]:
        return {
            "id": row["id"], "title": row["title"], "collection": row["collection"],
            "scopes": json.loads(row["scopes_json"]), "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            "message_count": row["message_count"] if "message_count" in row.keys() else None,
        }

    @staticmethod
    def _project(row: sqlite3.Row) -> dict[str, object]:
        return {
            "id": row["id"], "name": row["name"], "collection": row["collection"],
            "scopes": json.loads(row["scopes_json"]), "created_at": row["created_at"],
        }

    @staticmethod
    def _note(row: sqlite3.Row) -> dict[str, object]:
        return {
            "id": row["id"], "project_id": row["project_id"], "content": row["content"],
            "source_chat_id": row["source_chat_id"], "source_chat_title": row["source_chat_title"],
            "created_at": row["created_at"], "updated_at": row["updated_at"],
        }
