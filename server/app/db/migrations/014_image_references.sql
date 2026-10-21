-- Reference ownership outlives deleted chats, as Gallery artifacts already do.
CREATE TABLE image_references (
 id TEXT PRIMARY KEY, chat_id TEXT NOT NULL, original_sha256 TEXT NOT NULL,
 descriptor_json TEXT NOT NULL, available INTEGER NOT NULL DEFAULT 1 CHECK(available IN (0,1)),
 created_at TEXT NOT NULL, cleared_at TEXT,
 UNIQUE(chat_id,original_sha256)
);
CREATE TABLE image_job_references (
 job_id TEXT PRIMARY KEY REFERENCES image_jobs(id),
 reference_id TEXT NOT NULL REFERENCES image_references(id),
 export_sha256 TEXT, export_bytes INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX image_reference_holders ON image_job_references(reference_id);
