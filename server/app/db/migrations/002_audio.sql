CREATE TABLE attachments_new (
  id TEXT PRIMARY KEY,
  message_id TEXT REFERENCES messages(id) ON DELETE CASCADE,
  kind TEXT NOT NULL CHECK (kind IN ('image','text','audio')),
  filename TEXT NOT NULL, mime_type TEXT NOT NULL, bytes INTEGER NOT NULL,
  path TEXT NOT NULL,
  created_at TEXT NOT NULL
);
INSERT INTO attachments_new
  SELECT id, message_id, kind, filename, mime_type, bytes, path, created_at FROM attachments;
DROP TABLE attachments;
ALTER TABLE attachments_new RENAME TO attachments;
CREATE INDEX attachments_message ON attachments(message_id);
CREATE TABLE transcripts (
  attachment_id TEXT PRIMARY KEY REFERENCES attachments(id) ON DELETE CASCADE,
  status TEXT NOT NULL CHECK (status IN ('queued','transcribing','ready','failed','cancelled')),
  channels TEXT NOT NULL DEFAULT 'mix' CHECK (channels IN ('mix','split')),
  started_at TEXT, error_json TEXT, duration_seconds REAL,
  text TEXT, raw_text TEXT, segments_json TEXT, meta_json TEXT, cleaned_text TEXT,
  cleanup_status TEXT CHECK (cleanup_status IN ('running','ready','failed')),
  cleanup_json TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
