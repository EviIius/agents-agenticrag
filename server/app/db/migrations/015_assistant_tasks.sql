-- AS0: additive task records; existing chat/provider data is unchanged.
CREATE TABLE assistant_tasks (
 id TEXT PRIMARY KEY,
 chat_id TEXT NOT NULL REFERENCES chats(id) ON DELETE CASCADE,
 parent_id TEXT REFERENCES messages(id) ON DELETE CASCADE,
 request_key TEXT NOT NULL UNIQUE,
 request_json TEXT NOT NULL,
 snapshot_json TEXT NOT NULL,
 state TEXT NOT NULL,
 updated_at TEXT NOT NULL,
 cancel_requested INTEGER NOT NULL DEFAULT 0 CHECK(cancel_requested IN (0,1))
);
CREATE INDEX assistant_tasks_chat ON assistant_tasks(chat_id,updated_at,id);
CREATE TABLE assistant_approvals (
 id TEXT PRIMARY KEY,
 task_id TEXT NOT NULL REFERENCES assistant_tasks(id) ON DELETE CASCADE,
 binding TEXT NOT NULL,
 state TEXT NOT NULL,
 expires_at REAL NOT NULL
);
CREATE TABLE assistant_events (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 task_id TEXT NOT NULL REFERENCES assistant_tasks(id) ON DELETE CASCADE,
 snapshot_json TEXT NOT NULL
);
CREATE INDEX assistant_events_task ON assistant_events(task_id,id);
