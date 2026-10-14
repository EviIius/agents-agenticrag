# Workflow Studio WS-B report

## Summary

The isolated branch adds the seven initial workflow blocks, definition APIs,
additive graph storage, durable execution, approvals, retry and merged SSE.
Both existing templates pass six exact request/setting parity cases against the
fake runtime. Image creation inside chat is recorded as a separate pending item.
This checkpoint changes no visible interface and does not publish to the live app.
Source `ebc7f41e` passes the final checks and one complete 43.4-minute browser
invocation. Evidence is archived and historical inputs are restored. Stop for
WS-B review before WS-C; main and the installed app remain unchanged.

## Done-when checklist

| Item | Status | Evidence |
| --- | --- | --- |
| WS-AC5: existing database rows preserved | Passed | `test_workflow_graph_storage.py`; existing migration guards |
| WS-AC6: CRUD, stale-version conflict, force, duplicate, archive | Passed | `test_definition_api_concurrency_archive_and_immutable_layout_snapshots` |
| WS-AC7: legacy template parity | Passed, 6 cases | `test_workflow_parity.py`; `artifacts/workflow-studio/ws-b/parity-first.log` |
| WS-AC8: joins, skip, approvals/rejection, cancellation, interruption, retry, idempotency | Passed in focused fake-runtime checks | `test_workflow_graph_engine.py` |
| WS-AC9: literal/typed references, tags, escaping, empty lines, required values, no truncation | Passed | `test_workflow_graph.py` |
| Review stop | Ready | Stop before WS-C, canvas dependency installation, merge or live deployment |

## Changed files

- Server: migration 011, `workflows/graph.py`, `graph_schemas.py`, `defs.py`,
  `template_graphs.py`, `templating.py`, `engine.py`, `blocks.py`, `views.py`,
  `text.py`, `api/workflow_graphs.py` and application startup/shutdown wiring.
- Legacy text requests delegate to the extracted shared performer; its scheduler,
  performers, API schemas and endpoints retain their existing behavior.
- Tests: graph, engine, storage, parity and frozen workflow-prompt guards. Three
  existing migration assertions now expect schema 11. The browser harness starts
  its fake runtime before its dependent test app.
- Web: generated API types only; no production component or style changes.
- Docs: authorization, implementation decisions, report and the chat image to-do.

## Deviations from the proposal

The corrections in `WORKFLOW-STUDIO-REVIEW.md` and
`WORKFLOW-STUDIO-WS-B-PLAN.md` are applied:

- Separate graph run/step/attempt/source/event tables preserve legacy JSON parsers.
  No existing table is altered by migration 011.
- Snapshot IDs identify immutable full layouts; execution hashes exclude layout.
  Snapshots are created at run acceptance, while autosave updates the current draft.
- Stable ID ties replace canvas-position-dependent execution order.
- Original sources are stored independently per source block, with provenance.
- Graph resume/cancel/sources/export have additive `/v2/` routes. Legacy routes
  keep their exact schemas. The merged stream uses `legacySequence:graphSequence`
  cursors; progress/text are ephemeral and share a 10 Hz per-run limit.
- Templates are constructed and validated in `template_graphs.py`, using the
  original frozen constants rather than duplicated prompt strings in JSON files.
- Cross-run reuse and single-block test modes remain WS-D; no config-hash-only reuse
  is implemented. Knowledge/condition/Classify blocks remain WS-E.

## Runtime observations

All new execution evidence uses fake Ollama/image workers and synthetic recordings.
No real model inference, weights, runtime, dependency, default or sampling change
is claimed. The workflow prompts, ordinary chat request construction, search,
Library, transcription engine and image engine implementations are preserved.

The first diagnostic full check found exact schema-version assertions still
expecting 10. They now expect 11, with every row-preservation/privacy assertion
retained. Early development coverage is retained separately; it is not final
coverage evidence. Interrupted development checks/browser runs are retained in
`artifacts/workflow-studio/ws-b/attempts/` and are not assembled into a pass.

The browser cold-start attempt retained two failed model-picker assertions and
traces: bootstrap reported an unreachable fake runtime and the model list was
empty. Starting the fake runtime before the app fixes the six focused chat-action
cases without changing production providers, retries, assertions or timeouts.

The first rollback harness omitted the previous source's shared configuration.
Its failed command/log/source are retained; including `shared/` in the copied
previous tree permits verified candidate/previous startup and backup restoration.

## QA gates

| Gate | Status/evidence |
| --- | --- |
| G-1 | `make check`: 591 Python / 39 frontend; workflows 88.4% coverage; `check-final.log` |
| G-2 | `e2e-final.log`: 505 passes, three existing skips, one complete 43.4-minute invocation |
| G-3 | Test-diff ledger below; no weakened assertion, skip, timeout or retry setting |
| G-4 | Initial JS 245,249 gzip bytes, unchanged; streaming p95 2.7 / 3 ms; TTFT overhead 96.08 / 65.05 ms; 300-message scroll p95 16.7 / 22 ms |
| G-5 | No new UI; existing axe/keyboard suite passes in the full run; 74 contrast pairs pass |
| G-6 | Phase 3 guard passes; full previous WS-A/current API comparison has zero errors |
| G-7 | Migration 011 preserves every pre-existing column in the synthetic fixture, including old workflow tables |
| G-8 | Original prompt guards plus literal SHA-256 guards for both workflow prompts; parity confirms the loaded graph copies |
| G-9 | Not triggered: no change under `search/`, `runs/` or `providers/` |
| G-10 | Existing ordinary-chat golden request guard retained |
| G-11 | Privacy guard passes; 22,069 historical evidence/eval/fixture blobs, 15 provided references and 410 source/test files verified; synthetic only |
| G-12 | Installed app unchanged; local and normally verified Tailscale HTTPS health pass |
| G-13 | No motion changes; existing reduced-motion/guard checks retained |
| G-14 | No new production UI state at WS-B; existing design states retained |
| G-15 | Synthetic copied-data rollback passes; previous source starts on restored schema 10, candidate on 11; backup hashes equal |
| G-16 | No physical phone pass invented. This server checkpoint awaits review; visible builder/phone editing belongs to WS-C |

### Test-diff ledger

| Existing file/test | Change | Why | Behavior retained? |
| --- | --- | --- | --- |
| `test_foundation.py::test_migration_is_idempotent_and_private` | Exact expected version 10 → 11 | New migration | Yes: both opens, WAL, foreign keys, tables and private permissions |
| `test_documents.py::test_phase5a_rows_and_meta_nullable_survive_migration` | Exact expected version 10 → 11 | New migration | Yes: every old row and nullable metadata check |
| `test_folders_backups.py::test_phase5b_migration_preserves_every_existing_column` | Exact expected version 10 → 11 | New migration | Yes: projected rows, null folder IDs and empty folders |
| `web/playwright.config.ts` | Fake runtime starts first | Observed cold-start dependency failure | Yes: all projects/tests/assertions/timeouts, one worker and no existing-server reuse |

## Test output

- `make check`: **591 Python tests**, **39 frontend tests**; all lint/type/format,
  contrast, motion, additive API and privacy checks pass. Workflow coverage is
  **88.4%**; other monitored packages remain above 80%.
- `make e2e`: **505 passed, 3 existing skips in 43.4 minutes**, in one complete
  invocation after the final implementation changes. The extra hash guard changes
  only the server test suite; it was included in the final full check.
- `make build`: passes. Initial JavaScript is **245,249 gzip bytes**, unchanged.
  Streaming p95 is 2.7 ms Chromium / 3 ms WebKit; only the streaming row renders.
  First-token overhead is 96.08 / 65.05 ms. The 300-message scroll median/p95 is
  16.7 / 16.7 ms Chromium and 16 / 22 ms WebKit.
- Rollback/API rehearsal: passes on copied synthetic data, restoring the exact
  backup SHA-256 and starting previous schema-10 source. Both current local and
  normally verified Tailscale HTTPS health checks pass.
- **1,000 fresh outputs** retained separately; **960 historical files restored**
  and 40 newly generated fake settings captures relocated. Historical inputs,
  provided references, main and the 97 installed server / 410 current-release
  static hashes verify unchanged.

Evidence is under `artifacts/workflow-studio/ws-b/`. Frozen source hashes and the
historical/live-file preservation proof accompany the report.
The six mandatory parity cases pass. No live/native semantic-quality qualification
is inferred from fake-runtime tests.

## Screenshots

WS-B adds no UI. Fresh synthetic regression captures are retained separately
under `artifacts/workflow-studio/ws-b/regenerated-test-evidence/`, with all
historical evidence restored to its original bytes. No actual phone/private document capture
is part of this checkpoint.

## Open review items

- Review the engine/API decisions before WS-C's visible canvas and Outline editor.
- Image creation through the ordinary composer with results in the conversation
  remains pending in `docs/DEFERRED-FIXES.md`; it needs a durable chat-artifact scope.
- WS-D retains the reviewed input/provenance checks for cross-run reuse, test-run
  lifecycle and running-on-canvas behavior. These are not claimed completed here.
- Research remains shelved. VoiceOver remains off the current work list, with its
  historical reported failure preserved.
