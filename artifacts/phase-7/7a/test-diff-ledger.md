# 7A test-diff ledger

| Existing file/test | Edit | Reason | Original behavior retained? |
|---|---|---|---|
| `test_foundation.py`: migration idempotence | Exact schema version 7 → 8 | New additive migration | Yes: exact version, WAL and private permissions remain asserted |
| `test_documents.py`: Phase 5A migration | Exact schema version 7 → 8 | New additive migration | Yes: every pre-existing projected row and nullable metadata remain asserted |
| `test_folders_backups.py`: Phase 5B migration | Exact schema version 7 → 8 | New additive migration | Yes: projected rows, empty folders and nullable folder assignments remain asserted |
| `fake_runtime.py` (fixture, not assertions) | Explicit embedding-only models, deterministic `/api/embed` | Library tests need runtime-reported capabilities and embeddings | Existing chat models retain capabilities/responses; requests for embedding on existing chat models still fail, preserving the search fallback test |

No existing browser test was edited. No assertion, performance threshold or timeout was loosened; no new skip. Library tests are new. The 180-second timeout on each new 24-state axe matrix covers multiple analyses; existing performance budgets and the 45-second interaction timeout remain intact.

QA G-2: the unchanged existing WebKit copy-feedback test failed its viewport click in the first full run and passed all original assertions in the second full run. It is listed in the report and `failure-disposition.json`; its root cause remains unresolved. No fix or test edit is claimed.
