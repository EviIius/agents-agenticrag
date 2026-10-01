-- 001_init.sql
CREATE TABLE connections (
  id TEXT PRIMARY KEY,
  kind TEXT NOT NULL CHECK (kind IN ('ollama','lmstudio','openai_compat')),
  name TEXT NOT NULL,
  base_url TEXT NOT NULL,              -- e.g. http://127.0.0.1:11434 (no /v1 for ollama), http://127.0.0.1:1234/v1
  api_key TEXT,                        -- never returned by the API
  enabled INTEGER NOT NULL DEFAULT 1,
  max_concurrent INTEGER NOT NULL DEFAULT 1,
  keep_alive TEXT NOT NULL DEFAULT '30m',  -- ollama only: '5m'|'30m'|'1h'|'-1'
  flags_json TEXT NOT NULL DEFAULT '{}',   -- learned quirks, e.g. {"no_stream_options": true}
  created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);

CREATE TABLE model_prefs (               -- user overrides per model; all optional
  connection_id TEXT NOT NULL REFERENCES connections(id) ON DELETE CASCADE,
  model_id TEXT NOT NULL,
  display_name TEXT,
  context_length INTEGER,              -- effective context the app should use/request
  params_json TEXT NOT NULL DEFAULT '{}',   -- default sampling params for this model
  vision_override INTEGER,             -- for openai_compat models whose capability is unknown
  hidden INTEGER NOT NULL DEFAULT 0,
  tokens_per_char REAL,                -- learned from usage, for budgeting
  PRIMARY KEY (connection_id, model_id)
);

CREATE TABLE chats (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL DEFAULT 'New chat',
  title_source TEXT NOT NULL DEFAULT 'fallback' CHECK (title_source IN ('fallback','auto','user')),
  connection_id TEXT, model_id TEXT,  -- last used in this chat
  system_prompt TEXT,                  -- NULL = use the global default
  params_json TEXT NOT NULL DEFAULT '{}',
  web_enabled INTEGER NOT NULL DEFAULT 0,
  current_leaf_id TEXT,
  pinned INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE INDEX chats_updated ON chats(pinned DESC, updated_at DESC);

CREATE TABLE messages (
  id TEXT PRIMARY KEY,
  chat_id TEXT NOT NULL REFERENCES chats(id) ON DELETE CASCADE,
  parent_id TEXT REFERENCES messages(id) ON DELETE CASCADE,  -- NULL = root
  role TEXT NOT NULL CHECK (role IN ('user','assistant')),
  content TEXT NOT NULL DEFAULT '',
  reasoning TEXT,
  status TEXT NOT NULL DEFAULT 'complete'
    CHECK (status IN ('complete','streaming','stopped','error','interrupted')),
  error_json TEXT,                     -- {"code":..., "message":...}
  connection_id TEXT, model_id TEXT,   -- assistant only
  params_json TEXT,                    -- params actually sent (assistant only)
  stats_json TEXT,                     -- §C9 Stats (assistant only)
  web_json TEXT,                       -- Phase 2: queries, timings, status, notices (assistant only)
  created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE INDEX messages_chat ON messages(chat_id, created_at);
CREATE INDEX messages_parent ON messages(parent_id);

CREATE TABLE attachments (
  id TEXT PRIMARY KEY,
  message_id TEXT REFERENCES messages(id) ON DELETE CASCADE,  -- NULL until sent
  kind TEXT NOT NULL CHECK (kind IN ('image','text')),
  filename TEXT NOT NULL, mime_type TEXT NOT NULL, bytes INTEGER NOT NULL,
  path TEXT NOT NULL,                  -- relative to DATA_DIR/attachments
  created_at TEXT NOT NULL
);

CREATE TABLE message_sources (           -- Phase 2
  message_id TEXT NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
  n INTEGER NOT NULL,                  -- 1..N as shown to the model
  url TEXT NOT NULL, title TEXT NOT NULL, site_name TEXT NOT NULL,
  published_at TEXT, kind TEXT NOT NULL DEFAULT 'page' CHECK (kind IN ('page','snippet')),
  passages_json TEXT NOT NULL,         -- [{"text":..., "heading":..., "score":...}] exactly as sent
  cited INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (message_id, n)
);

CREATE TABLE web_reads (                 -- Phase 2: pages read but not used, and failures (sources panel)
  message_id TEXT NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
  url TEXT NOT NULL, title TEXT, site_name TEXT,
  status TEXT NOT NULL CHECK (status IN ('used','unused','failed')),
  reason TEXT,
  PRIMARY KEY (message_id, url)
);

CREATE TABLE search_cache (key TEXT PRIMARY KEY, results_json TEXT NOT NULL, expires_at TEXT NOT NULL);
CREATE TABLE page_cache (url TEXT PRIMARY KEY, final_url TEXT NOT NULL, title TEXT, site_name TEXT,
  published_at TEXT, text TEXT, error TEXT, fetched_at TEXT NOT NULL, expires_at TEXT NOT NULL);
CREATE TABLE favicons (domain TEXT PRIMARY KEY, mime_type TEXT, data BLOB, fetched_at TEXT NOT NULL);
CREATE TABLE embed_cache (key TEXT PRIMARY KEY, vector BLOB NOT NULL);  -- key = model + sha256(text)

CREATE TABLE settings (key TEXT PRIMARY KEY, value_json TEXT NOT NULL);

CREATE VIRTUAL TABLE chat_search USING fts5(
  chat_id UNINDEXED, message_id UNINDEXED, title, content, tokenize = 'porter unicode61'
);
