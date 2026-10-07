ALTER TABLE chats ADD COLUMN research_enabled INTEGER NOT NULL DEFAULT 0;
ALTER TABLE messages ADD COLUMN research_json TEXT;
ALTER TABLE messages ADD COLUMN activity_json TEXT;
