CREATE TABLE image_jobs (
 id TEXT PRIMARY KEY, request_key TEXT NOT NULL UNIQUE,
 parent_id TEXT REFERENCES image_jobs(id), input_json TEXT NOT NULL,
 state TEXT NOT NULL CHECK(state IN ('queued','preparing','running','cancelling','cancelled','complete','failed','interrupted')),
 stage TEXT NOT NULL, completed_steps INTEGER NOT NULL DEFAULT 0,
 error TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE TABLE image_steps (
 job_id TEXT PRIMARY KEY REFERENCES image_jobs(id),
 started_at TEXT, finished_at TEXT, exit_code INTEGER
);
CREATE TABLE image_artifacts (
 job_id TEXT PRIMARY KEY REFERENCES image_jobs(id),
 sha256 TEXT NOT NULL, bytes INTEGER NOT NULL, metadata_bytes INTEGER NOT NULL
);
CREATE TABLE image_events (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 job_id TEXT NOT NULL REFERENCES image_jobs(id), data_json TEXT NOT NULL
);
