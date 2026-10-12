CREATE TABLE workflow_runs (
 id TEXT PRIMARY KEY, request_key TEXT NOT NULL UNIQUE,
 input_json TEXT NOT NULL, version INTEGER NOT NULL DEFAULT 1,
 state TEXT NOT NULL, stage TEXT NOT NULL,
 source_json TEXT, edited_prompt TEXT,
 error TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE TABLE workflow_steps (
 run_id TEXT NOT NULL REFERENCES workflow_runs(id) ON DELETE CASCADE,
 position INTEGER NOT NULL, kind TEXT NOT NULL, label TEXT NOT NULL,
 state TEXT NOT NULL DEFAULT 'pending', attempt INTEGER NOT NULL DEFAULT 0,
 output_json TEXT, error TEXT,
 PRIMARY KEY(run_id,position)
);
CREATE TABLE workflow_attempts (
 run_id TEXT NOT NULL, position INTEGER NOT NULL, attempt INTEGER NOT NULL,
 input_json TEXT NOT NULL, output_json TEXT, state TEXT NOT NULL,
 started_at TEXT NOT NULL, finished_at TEXT,
 PRIMARY KEY(run_id,position,attempt),
 FOREIGN KEY(run_id,position) REFERENCES workflow_steps(run_id,position) ON DELETE CASCADE
);
CREATE TABLE workflow_events (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 run_id TEXT NOT NULL REFERENCES workflow_runs(id) ON DELETE CASCADE,
 data_json TEXT NOT NULL
);
