-- Graph runs are separate: legacy input/output parsers remain unchanged.
CREATE TABLE workflow_defs (
 id TEXT PRIMARY KEY, name TEXT NOT NULL, description TEXT NOT NULL DEFAULT '',
 icon TEXT NOT NULL DEFAULT 'workflow', graph_json TEXT NOT NULL, graph_hash TEXT NOT NULL,
 version INTEGER NOT NULL DEFAULT 1, template_id TEXT, archived_at TEXT,
 created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE TABLE workflow_def_snapshots (
 id TEXT PRIMARY KEY, def_id TEXT NOT NULL REFERENCES workflow_defs(id),
 graph_hash TEXT NOT NULL, graph_json TEXT NOT NULL, label TEXT, created_at TEXT NOT NULL
);
CREATE TABLE workflow_graph_runs (
 id TEXT PRIMARY KEY, request_key TEXT NOT NULL UNIQUE, request_json TEXT NOT NULL,
 def_id TEXT NOT NULL REFERENCES workflow_defs(id), def_name TEXT NOT NULL,
 snapshot_id TEXT NOT NULL REFERENCES workflow_def_snapshots(id), graph_hash TEXT NOT NULL,
 inputs_json TEXT NOT NULL, state TEXT NOT NULL, stage TEXT NOT NULL, error TEXT,
 created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE TABLE workflow_graph_steps (
 run_id TEXT NOT NULL REFERENCES workflow_graph_runs(id), node_id TEXT NOT NULL,
 state TEXT NOT NULL, attempt INTEGER NOT NULL DEFAULT 0, port TEXT, output_json TEXT,
 error TEXT, warnings_json TEXT NOT NULL DEFAULT '[]', started_at TEXT, finished_at TEXT,
 PRIMARY KEY(run_id,node_id)
);
CREATE TABLE workflow_graph_attempts (
 run_id TEXT NOT NULL, node_id TEXT NOT NULL, attempt INTEGER NOT NULL,
 input_json TEXT NOT NULL, output_json TEXT, state TEXT NOT NULL,
 started_at TEXT NOT NULL, finished_at TEXT,
 PRIMARY KEY(run_id,node_id,attempt),
 FOREIGN KEY(run_id,node_id) REFERENCES workflow_graph_steps(run_id,node_id)
);
CREATE TABLE workflow_graph_sources (
 run_id TEXT NOT NULL, node_id TEXT NOT NULL, source_json TEXT NOT NULL,
 sha256 TEXT NOT NULL, PRIMARY KEY(run_id,node_id),
 FOREIGN KEY(run_id,node_id) REFERENCES workflow_graph_steps(run_id,node_id)
);
CREATE TABLE workflow_graph_events (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 run_id TEXT NOT NULL REFERENCES workflow_graph_runs(id), data_json TEXT NOT NULL
);
CREATE INDEX workflow_graph_runs_def ON workflow_graph_runs(def_id,created_at,id);
CREATE INDEX workflow_def_snapshots_def ON workflow_def_snapshots(def_id,created_at,id);
