CREATE TABLE legacy_imports (
    legacy_id TEXT PRIMARY KEY,
    chat_id TEXT NOT NULL REFERENCES chats(id) ON DELETE CASCADE
);
