# WS-D test-diff ledger

Base: `96bfcbfd`. Existing browser tests, assertions, skips, retries and timeouts
are unchanged. New browser cases use the existing 45-second test timeout; state
matrices are divided by width/theme rather than increasing that limit.

| Existing file / test | Change | Reason | Original behavior retained |
|---|---|---|---|
| `server/tests/test_workflow_graph_engine.py` / definition API | Catalog count 7 → 8; assert Pick favorites exists | WS-D adds the eighth executable kind | All concurrency, immutable snapshot, archive and template assertions retained |
| `server/tests/test_workflow_graph_storage.py` / migration | Expected final schema 11 → 12 | New additive run-mode migration | Every pre-existing column/row hash, integrity and FK assertions retained |
| `server/tests/test_documents.py` / Phase 5A migration | Expected final schema 11 → 12 | Same migration | Nullable metadata and unchanged original-row checks retained |
| `server/tests/test_folders_backups.py` / Phase 5B migration | Expected final schema 11 → 12 | Same migration | Existing-column hash checks retained |
| `server/tests/test_foundation.py` / idempotent migration | Expected version `(11,)` → `(12,)` | Same migration | Repeated migration and private database checks retained |
| `server/tests/fake_image.py` | Add deterministic `#fail-once` and `#restart` markers | Exercise retry and lifecycle recovery with fake images | Existing ordinary, `#fail` and `#slow` paths unchanged; no product engine edit |
| `server/tests/serve_app.py` | Keep lifecycle handle; test-only full shutdown/startup route | Restart all app resources against the same synthetic database | Same temporary data isolation, runtime, fixtures and production route exclusion |

New tests cover strict discriminator extension with negative cases, populated
v11 migration preservation, provenance/changed defaults/inputs/sources/media,
idempotent acceptance and decisions, sample isolation/typing, test retention,
source pointer rebinding, live text/progress snapshots and paused history beyond
50 rows. Frontend tests cover cumulative-event ordering, attempt identities,
truthful labels and taken connections. New browser tests cover the WS-D run flow,
phone decisions, reuse, tests, versions, immutable history, failure/retry,
notifications, lifecycle recovery and every run state in both widths/themes.

## Retained development failures

Logs under `artifacts/workflow-studio/ws-d/` retain lint/type/setup failures,
three obsolete schema-version assertions, the initial navigation-name regression,
zero-height synthetic design controls, premature fake-stream completion assertion,
invalid synthetic fixture references after removing Review, Escape closing both
menu and Inspector, mismatched expected public image error, notification startup
race, the block-test HTTP/SSE reload race, and incorrect fixture restart URL/import.
The accidentally broad `vitest run` invocation discovered Playwright files; its
failed log is retained, and verification uses the repository's `vitest run src`.

Failed browser traces available at each archive point are under `attempts/`.
The fourth running attempt's log is retained; its trace was replaced during a
failed archive/setup script before the fifth attempt. Do not claim that trace was
preserved. Every supplied design/reference byte remains preserved independently.
No failed full regression invocation is silently combined with focused passes.
