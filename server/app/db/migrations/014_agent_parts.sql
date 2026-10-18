ALTER TABLE messages ADD COLUMN parts_json TEXT NOT NULL DEFAULT '[]';
ALTER TABLE messages ADD COLUMN agent_json TEXT;
