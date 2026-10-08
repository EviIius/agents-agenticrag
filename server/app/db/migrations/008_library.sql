CREATE TABLE library_collections (
 id TEXT PRIMARY KEY, name TEXT NOT NULL UNIQUE COLLATE NOCASE,
 created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE TABLE library_documents (
 id TEXT PRIMARY KEY,
 collection_id TEXT REFERENCES library_collections(id) ON DELETE SET NULL,
 filename TEXT NOT NULL, mime_type TEXT NOT NULL, bytes INTEGER NOT NULL,
 sha256 TEXT NOT NULL UNIQUE, path TEXT NOT NULL,
 status TEXT NOT NULL CHECK(status IN ('queued','extracting','embedding','ready','failed','stale')),
 error_json TEXT, extracted_text TEXT, pages INTEGER, chunk_count INTEGER NOT NULL DEFAULT 0,
 token_estimate INTEGER, embedding_model TEXT,
 progress_done INTEGER NOT NULL DEFAULT 0, progress_total INTEGER NOT NULL DEFAULT 0,
 created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE TABLE library_chunks (
 id INTEGER PRIMARY KEY,
 document_id TEXT NOT NULL REFERENCES library_documents(id) ON DELETE CASCADE,
 ord INTEGER NOT NULL, heading TEXT NOT NULL DEFAULT '', page_start INTEGER, page_end INTEGER,
 text TEXT NOT NULL, UNIQUE(document_id,ord)
);
CREATE VIRTUAL TABLE library_chunks_fts USING fts5(
 text, heading, content='library_chunks', content_rowid='id', tokenize='porter unicode61'
);
CREATE TRIGGER library_chunks_ai AFTER INSERT ON library_chunks BEGIN
 INSERT INTO library_chunks_fts(rowid,text,heading) VALUES(new.id,new.text,new.heading);
END;
CREATE TRIGGER library_chunks_ad AFTER DELETE ON library_chunks BEGIN
 INSERT INTO library_chunks_fts(library_chunks_fts,rowid,text,heading)
 VALUES('delete',old.id,old.text,old.heading);
END;
CREATE TABLE message_library_sources (
 message_id TEXT NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
 n INTEGER NOT NULL, document_id TEXT, filename TEXT NOT NULL,
 page_start INTEGER, page_end INTEGER, passages_json TEXT NOT NULL,
 cited INTEGER NOT NULL DEFAULT 0, PRIMARY KEY(message_id,n)
);
CREATE TABLE library_events (
 id INTEGER PRIMARY KEY AUTOINCREMENT, kind TEXT NOT NULL, data_json TEXT NOT NULL
);
ALTER TABLE chats ADD COLUMN library_enabled INTEGER NOT NULL DEFAULT 0;
ALTER TABLE chats ADD COLUMN library_scope_json TEXT;
ALTER TABLE messages ADD COLUMN library_json TEXT;
