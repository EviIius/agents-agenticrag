-- Additive Studio run modes and provenance. Existing run/step values are unchanged.
ALTER TABLE workflow_graph_runs ADD COLUMN mode TEXT NOT NULL DEFAULT 'run';
ALTER TABLE workflow_graph_runs ADD COLUMN parent_run_id TEXT;
ALTER TABLE workflow_graph_runs ADD COLUMN expires_at TEXT;
ALTER TABLE workflow_graph_steps ADD COLUMN reused_from TEXT;
ALTER TABLE workflow_graph_steps ADD COLUMN guard_json TEXT;
CREATE INDEX workflow_test_expiry ON workflow_graph_runs(mode,expires_at);
CREATE INDEX workflow_run_state_mode ON workflow_graph_runs(mode,state);
