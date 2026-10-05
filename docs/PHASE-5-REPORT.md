# Phase 5 report

## Checkpoint 5A — presets, save clarity and model display names

### Summary

Presets copy a saved prompt and explicit sampling values into a chat. They can
be created, edited, reordered, deleted, and selected as the default for new chats.
Chat controls now validate inline, retain unsaved drafts by chat and model, and
show an explicit Saved result. Context length has a separate Apply action.
Model rename uses a dialog; renamed picker rows retain searchable runtime IDs.
5B and 5C have not started. This is the required 5A review stop.

Source commits: `074d674`, `f713414` on `codex/phase-5-everyday-chat`.

### Done-when checklist

| Item | Status | Evidence |
|---|---|---|
| P5-AC1: preset sampling precedence | Pass | `test_presets.py`: exact captures without defaults; explicit keys override saved model defaults, omitted keys inherit them |
| P5-AC2: existing chats keep copied values | Pass | Unit byte comparison after preset edit/delete; `phase5a.spec.ts` existing-chat copy assertions |
| P5-AC3: validation, dirty/saved state, separate context | Pass | `phase5a.spec.ts`, `parameters.spec.ts`, `load-selection.spec.ts`, `ui-regressions.spec.ts` |
| P5-AC4: display name and runtime ID | Pass | Rename, search, empty-name reset in `phase5a.spec.ts` |
| P5-AC11: checkpoint QA gates | Automated pass; review pending | Gates below |
| P5-AC12: web answers unchanged | Frozen pipeline | No changes under search, runs, providers or model-facing prompts; prompt and request guards pass |
| Documents, folders, automatic backups | Future checkpoints | 5B and 5C are intentionally not started |

### Changed files

- Server: additive preset schemas and `/api/presets` CRUD; migration
  `005_presets.sql`; default preset setting; optional `preset_id` on chat creation;
  copied prompt/parameters inserted when creating a chat.
- Web: `SamplingFields`, `PresetEditor`, `PresetsPane`, `ModelRename`, retained
  `control-drafts`; `LiveChatSettings`, `LiveAppShell`, `useSend`, Settings,
  command palette, picker, API types and error copy.
- Design: production components at `/design?everyday`; synthetic state captures.
- QA: new preset unit/browser tests and design axe checks; contrast coverage;
  privacy audit includes Phase 5; private-copy rollback rehearsal script.
- Docs: authorization and preset precedence recorded in AGENTS/SPEC/phase plan,
  this report, and `artifacts/phase-5/5a/` evidence.

### Deviations and clarifications

Jake answered “Do what you think is best” to the plan's contradiction between
exact preset-only sampling and preserving the existing model-default pipeline.
Presets override only their explicit keys; other keys inherit saved model defaults
and otherwise use runtime defaults. Empty presets add no sampling values of their
own. Presets never store reasoning or context. The provider/run pipeline is unchanged.
The controls explain this inheritance. The clarification is recorded in AGENTS,
SPEC and the phase plan, and tested against runtime request captures.

The phase plan said there was no display-name control, but the current app had
an input that saved on blur. This checkpoint replaces it with explicit Rename
and Cancel actions. Picker search already matched runtime IDs; that is retained.

Axe checks exposed background controls that were aria-hidden but focusable while
a Radix Select was open. Background branches are now inert until dismissal,
restored before focus returns. The desktop picker also gained its missing name.
The selected model's metadata now uses existing `text-2` over `brand-soft`;
`text-3` measured 4.48:1 there in WebKit. No palette token or threshold changed.

Visual review found the duplicate-name save alert below the editor scroll fold.
The stronger viewport assertion failed before the fix (`error-viewport-before.txt`).
Save errors now sit outside the scroll body, above the fixed footer. All eight
state variants passed the strengthened assertion and axe (`error-viewport-after.txt`).
The first full browser run passed 351 tests, but it preceded this visual fix;
`e2e-before-error-fix.txt` is retained separately. Final acceptance uses the new
complete invocation against `f713414`, not the earlier run or targeted results.

### Runtime observations

No provider, search engine or transcription engine implementation changed.
All new inference tests use the existing fake runtime and synthetic input.
No new packages or model calls were added. Installed service remains independent
of Codex's account usage limit.

### Test output

- `make check`: **217 Python tests**, **36 frontend unit tests**, **60 contrast
  pairs**; lint/types, additive API, motion, privacy and prompt guards pass.
- Coverage: providers **85.8%**, runs **89.2%**, search **88.9%**, transcribe **90.7%**.
- Build: passes (`build.txt`). The existing large-chunk notice remains; the
  measured initial gzip payload meets its budget.
- Existing skips, unchanged: WebKit real-time timeout gate (run in Chromium),
  foundation all-size screenshot capture (Chromium), and offline service-worker
  navigation (Playwright WebKit offline reload reports an internal navigation
  error; physical Safari verification remains separate).
- `make e2e`: **351 passed, three existing skips, 27.2 minutes**, in one complete
  invocation against `f713414` (`e2e.txt`).
- Preliminary targeted runs found the issues above and new-test selector/readiness
  errors. No failed run is counted as acceptance, and no existing assertion was
  loosened. Full-run acceptance requires one green invocation on frozen source.

### Budgets

| Measure | Phase 4A baseline | Previous deployed phone fix | 5A |
|---|---|---|---|
| Initial JS gzip | 224,491 B | 229,667 B | 233,783 B (+4,116 B) |
| Budget | 256,000 B | 256,000 B | Pass; increase below 8 KiB |
| Streaming p95 frame | 1.3 ms Chromium / 2 ms WebKit | See phone-fix regenerated metrics | 3.3 ms Chromium / 3.0 ms WebKit |
| First-token overhead | ≤82 ms | See phone-fix regenerated metrics | 67.95 ms Chromium / 61.05 ms WebKit |
| 300-message scroll | Existing performance suite | Pass | Pass; median scroll frames 16.7 / 17 ms |

Final timing JSON is retained under `regenerated/phase-1/` and
`regenerated/phase-3/`; historical phase artifacts were restored after testing.
Preset management and editor are lazy loaded. The existing timing thresholds
are unchanged. `bundle.json` records static-import gzip measurement.

### Gates

| Gate | Status | Evidence |
|---|---|---|
| G-1 check/coverage | Pass | `check.txt` |
| G-2 one complete browser run | Pass | `e2e.txt` |
| G-3 no weakened tests | Pass | Ledger below |
| G-4 performance | Pass | `bundle.json`; full performance tests |
| G-5 axe/contrast/keyboard | Pass | 60 token pairs; `design-axe-*.json`; existing keyboard suite |
| G-6 additive API | Pass | `check_api_additive.py`, `check.txt` |
| G-7 row preservation | Pass | `test_phase4_guards.py` migration fixture row hashes |
| G-8 prompt freeze | Pass | `test_prompt_hashes.py` |
| G-9 web eval when pipeline changes | Not triggered | No search/runs/providers changes; frozen source checked |
| G-10 ordinary payload unchanged | Pass | `test_phase4_guards.py` golden capture; existing exact-parameter captures |
| G-11 privacy | Pass | `privacy-audit.json`; invented fixtures only |
| G-12 deployment invariants | Pass | `test_deployment.py`, `pwa.spec.ts`; deployment metadata |
| G-13 reduced motion | Pass | `motion.spec.ts`, `phone-motion.spec.ts` |
| G-14 production design states | Pass | 19 states, two widths, two themes, two engines |
| G-15 rollback rehearsal | Pass | `rollback.json`, 3.18 seconds; procedure below |
| G-16 Jake phone check | Not checked for 5A | Review pending; earlier motion confirmation is in the separate phone report |

### Test-diff ledger

| Existing file/test | What changed | Why | Behavior still asserted? |
|---|---|---|---|
| `server/tests/test_foundation.py` migration idempotence | Schema version 4 → 5 | New additive migration | Yes; WAL, foreign keys, privacy and idempotence assertions retained |
| `web/tests/parameters.spec.ts` parameter integration | Click context Apply before Save | Context now has its own action | Yes; exact runtime options and system prompt retained |
| `web/tests/load-selection.spec.ts` context/load | Use separate Apply, first apply 16K then 32K; locate card through Rename button | Context action moved and display-name input became a dialog | Yes; selection, loading, context ceiling and request captures retained |
| `web/tests/ui-regressions.spec.ts` context validation | Assert restored value is valid, pristine Save disabled, changed context Apply enabled | Approved dirty-only saving and separate context action | Yes; invalid Save blocking and all layout checks retained; more validity assertions added |

No existing test was deleted, skipped, had its timeout raised, or had a runtime
or performance assertion loosened. New tests cover pristine default application
without an extra client patch, deferred chat loading, and draft isolation across
chats/models as well as the requested workflows.

### Core unchanged

All refer to the final single `e2e.txt` run, supplemented by `check.txt` unit guards:

| Core | Evidence |
|---|---|
| C1 send/stream/stats | `chat.spec.ts` |
| C2 stop/partial | `chat.spec.ts`, `phase3-accessibility.spec.ts` |
| C3 reopen/reconnect | `chat.spec.ts`, `web.spec.ts` |
| C4 long answer/idle | `chat.spec.ts` |
| C5 message/chat actions and exports | `actions.spec.ts` |
| C6 model operations/context | `load-selection.spec.ts`, `ui-regressions.spec.ts` |
| C7 explicit sampling | `parameters.spec.ts`, `test_chat.py`, `test_presets.py` |
| C8 search/citations/retry | `web.spec.ts`, search unit guards |
| C9 audio/transcript/download/retention | `transcription.spec.ts`, `recording-download.spec.ts`, `audio-storage.spec.ts` |
| C10 phone layout/composer/drawers | `mobile-layout.spec.ts`, `mobile-composer.spec.ts` |
| C11 palette/PWA/update | `polish.spec.ts`, `pwa.spec.ts` |
| C12 legacy read-only import | `test_legacy_import.py` |
| C13 deployment | `test_deployment.py`, deployment metadata |
| C14 untrusted input | `foundation.spec.ts`, SSRF unit tests |
| C15 performance | `performance.spec.ts`, chat frame and overhead tests |
| C16 axe/keyboard | `foundation.spec.ts`, `review.spec.ts`, `phase3-accessibility.spec.ts`, `phase5a-design.spec.ts` |

### Migrations and rollback

`005_presets.sql` creates one new table; pre-existing tables and rows are unchanged.
The synthetic Phase 3 fixture upgrade asserts identical old-column row hashes.

Rehearsal command: `. scripts/tool-env.sh; uv run --directory server python
../scripts/rehearse_presets_rollback.py --previous 4b312e2`.
The script copied the data folder privately, used SQLite online backup, started
current source with schema 5, added an invented preset, restored the original copy
without stale WAL/SHM, then started previous source with its installed static
build and schema 4. Health and app shell returned 200 in both versions, all old
row hashes matched, elapsed 3.18 s. The private copy was removed and production
was not modified. Output contains metadata only. Deployment took a fresh online backup before installing 5A.
`deployment-invariants.json` verifies health 200 locally and over Tailscale, schema
5, unchanged service arguments/label/Tailscale configuration, production `/design`
404, byte-identical installed static assets, and the new preset/bootstrap fields.
Backup count increased from six to seven. TLS was verified using the existing
certifi CA bundle and independently with system curl; no TLS verification was disabled.

### Evals

No prompt, provider, run or search implementation changed, so QA G-9's conditional
eval is not triggered. Prompt hashes and ordinary payload capture remain identical.
The full suite retains deterministic fake web-answer/citation assertions.
No live model eval or new model call was performed for this checkpoint.

### Screenshots

`artifacts/phase-5/5a/`: 152 synthetic state screenshots (19 states × 2 widths × 2 themes
× 2 engines), plus eight focused `context-visible-*-fake.png` captures. Names end in `-fake.png`. States: controls pristine, invalid, dirty,
saved, loading/error; context invalid/apply; preset select/list/default/editor/
collision/delete/empty/error/loading; model rename and renamed picker.
Per-variant `design-axe-*.json` records zero serious/critical requirements.
`context-visible-fake.json` verifies the input is in view and axe finds no
serious/critical violations in the focused group at both widths/themes/engines.
All final captures were visually reviewed through contact sheets, with individual
mobile editor/error and context inspection (`visual-review.json`). One additional
before-fix screenshot is retained as failure evidence, bringing the PNG total to 161.
No physical-phone screenshot or real content is saved.

### Known limitations carried forward

VoiceOver was user-reported failed and remains deferred; this report does not
claim it passed. The earlier iOS keyboard problem recovered after restart; its
cause is unproven. Dirty control drafts survive panel closing/navigation in the
current session, not a page reload. Preset reorder uses sequential additive PATCH
requests; a connection failure can leave partial order, reported inline.

### Open questions for Jake

5A is the next review. On the installed phone app, try a preset, save controls,
close/reopen with unsaved changes, apply context separately, and rename a model.
The normal phone checklist in QA §7 still applies. 5B (documents) waits for review.

---

## Checkpoint 5B — PDF and Word attachments (5 October 2026)

### Summary

PDFs and Word `.docx` files can be attached from the picker, drop or paste.
The app extracts selectable text, adds PDF page markers, preserves Word paragraph
and table order, and deletes the uploaded original. Document chips show page/token
estimates and open an extracted-text review sheet with Copy. Context warnings
follow model changes; the existing chat, search and transcription pipelines remain frozen.
This is the 5B review stop; 5C is not started.

### Done-when checklist

| Item | Status | Evidence |
|---|---|---|
| P5-AC5: PDF and Word reach the model | Pass | `test_upload_send_preserves_name_pages_table_and_only_text`; `documents.spec.ts` captured prompt includes original synthetic filenames, both page markers and tab-separated table cells |
| P5-AC6: errors and cleanup | Pass | Unit fixtures for scanned, encrypted and damaged PDFs; upload-size and timeout tests; bounded extraction/ZIP/XML/page/text limits; cancellation/worker shutdown/recovery cleanup tests |
| P5-AC7: original is not retained | Pass | Successful upload leaves only private `.txt`; failed/cancelled uploads leave no file or row; removal deletes extracted text; durable metadata is retained with sent messages |
| P5-AC8: privacy | Pass, within scanner/manual limits | `privacy-audit.json`; synthetic fixture generator; `*-fake.png` screenshots only; parser stdout/stderr suppressed, exception details replaced by fixed error codes |
| P5-AC11: checkpoint QA gates | Automated checks passed; phone review pending | Gates below |
| P5-AC12: web unchanged | Frozen | No edits to search/runs/providers or model-facing prompts; prompt hash, ordinary request capture and existing web tests pass |

### Changed files

- Server: `documents/extract.py`, `documents/service.py`, `documents/worker.py`;
  document branch and text-review endpoint in `api/attachments.py`; authoritative
  extension lists in bootstrap; optional document schemas/projection; lifecycle
  worker cleanup; migration `006_attachment_meta.sql`.
- Web: `DocumentChip`, lazy `DocumentSheet`; composer picker/metadata/context warning;
  upload progress/cancellation/error mapping; sent-message document chip; API types.
- Design: `/design?documents` and 15 production states (including the expanded menu).
- QA: document unit, browser, design/axe and real 50 MiB browser memory tests;
  synthetic fixture generator and six fixture files; documents coverage target;
  copied-data rollback rehearsal; foundation schema-version assertion.
- Docs/evidence: fixed error copy in SPEC §C12; this append-only 5B report;
  `artifacts/phase-5/5b/`. Existing 5A report/evidence remains historical and intact.

### Implementation choices and limits

No new packages, model calls or pipeline changes. Documents remain `kind='text'`;
the existing assembler sends the complete extracted text inside its existing file
wrapper. The new metadata column is nullable. GET of a new document attachment
returns the retained `.txt`, with a text MIME type and filename; existing image,
plain-text and audio attachment downloads retain their prior behavior.

Two extraction subprocesses run at most, each with a 30-second wall deadline.
Timeout/cancellation kills and awaits the worker before releasing capacity and
removing its temporary result. Startup recovery removes only interrupted document
parts/results, preserving completed text and audio. Limits: 50 MiB input,
1,500 PDF pages, 2,000,000 extracted characters, 16 MiB document XML/PDF page
content stream, 64 MiB total declared ZIP expansion and 2,048 ZIP entries.
ZIP entries are read in place; they are never unpacked into arbitrary paths.
Word DTD/custom-entity XML is rejected. Headers, footers, comments and tracked
deletions/moved-from paragraphs are excluded. No OCR, images inside documents,
legacy `.doc`, spreadsheet or slide support.

The attachment menu's new axe coverage found aria-hidden background controls
could still receive focus. It now applies native `inert` and restores focus on
close, matching the existing Select pattern. This preserves its existing modal
interaction while fixing the hidden-focus finding.

### Test output and iteration

`make check`: 240 Python tests; 36 frontend tests; 60 contrast token pairs.
Coverage: providers 85.8%, runs 89.2%, search 88.9%, transcribe 90.7%,
new documents package 96.6%. Lint, format, types, generated API, additive API,
motion, privacy, prompt and golden request guards pass.

Final focused browser run: 18 passed across Chromium and WebKit. Earlier focused
runs found a new-test selector mistake and the attachment menu focus finding;
both were fixed before acceptance. A design-only JSX edit interrupted one run;
a subsequent startup attempt found its isolated test servers still bound, so
those owned test processes were stopped and production restored before retry.
The full regression script includes cleanup and service restoration on exit.
A later startup was blocked by an orphaned Vite process on port 5173 from
the interrupted run; its repository command and orphaned parent were verified
before stopping it. The final complete run started with all test ports free.
Code review also found that trimming a table-only Word document removed tabs
for empty edge cells. The new regression failed before the fix and passed after
retaining those tabs; the first full run was interrupted and restarted against
the corrected source. The worker protocol unit test restores the logging level
after exercising the worker so other tests retain their own logging environment.
The initial check also correctly required updating the exact current schema
assertion from 5 to 6. No timeout/threshold/assertion was weakened.

Final `make e2e`: **369 passed, 3 existing skips, 0 failures (28.5m)**
from one complete Chromium/WebKit invocation against the frozen final source.
`source-verification.json` records unchanged source hashes during that run.
Earlier interrupted runs and the port-collision startup are retained separately;
they are not combined with this result.

### Budgets

| Measure | 5A | 5B |
|---|---|---|
| Initial static-import JS gzip | 233,783 B | 234,656 B (+873 B; budget 256,000 B) |
| Streaming p95 | 3.3 ms Chromium / 3.0 ms WebKit | 3.30 ms Chromium / 3.00 ms WebKit |
| First-token overhead | 67.95 ms Chromium / 61.05 ms WebKit | 77.59 ms Chromium / 61.15 ms WebKit |
| 300-message scroll median | 16.7 ms Chromium / 17 ms WebKit | 16.70 ms Chromium / 17.00 ms WebKit |
| 50 MiB document upload server RSS growth | New measure | 3.984 MiB Chromium / 1.188 MiB WebKit (limit 20 MiB) |

`bundle.json` excludes lazy imports. The review sheet is lazy-loaded. Memory
measures are real browser XHR uploads with uvicorn RSS sampled by `ps` every
50 ms; extraction worker memory is separate and was not included in the server
RSS criterion. No uploaded source was read into a single server/JS buffer.

### Gates

| Gate | Status | Evidence |
|---|---|---|
| G-1 check/coverage | Pass | `check.txt`; documents added to coverage targets, ≥80% |
| G-2 one complete E2E run | Pass | `e2e.txt`; one final invocation, both engines |
| G-3 tests not weakened | Pass | `test-diff-ledger.md`; table below |
| G-4 performance | Pass | `bundle.json`, final regenerated frame/first-token/scroll metrics; memory JSON |
| G-5 accessibility | Pass automated; VoiceOver remains deferred | 120 synthetic screenshots; 15 states × 2 widths × 2 themes × 2 engines, zero serious/critical findings; full keyboard/contrast checks |
| G-6 additive API | Pass | `check.txt`; optional document metadata, bootstrap extension list, new text endpoint |
| G-7 additive database | Pass | Phase 3 row projection guard plus `test_phase5a_rows_and_meta_nullable_survive_migration` |
| G-8 frozen prompts | Pass | `test_prompt_hashes.py` |
| G-9 web behavior | Pass existing guards; no new real-runtime eval | No search/runs/providers edits; all existing web tests in final run |
| G-10 ordinary payload | Pass | Phase 3 golden default request, parameter capture tests |
| G-11 privacy | Pass within audit limits | `privacy-audit.json`; synthetic images reviewed; physical-phone content not captured |
| G-12 deployment invariants | Pass | `deployment.txt`, `deployment-invariants.json`; existing deployment and PWA tests |
| G-13 reduced motion | Pass automated | Unchanged full `motion.spec.ts` / `phone-motion.spec.ts` coverage |
| G-14 design | Pass | `/design?documents`, screenshots/axe JSON |
| G-15 rollback | Pass | `rollback.json`: schema 6 → 5, both app health/shell 200, old row hashes identical, 3.063 s, private copy removed |
| G-16 Jake phone review | Not checked for 5B | Ready for review; no physical result invented |

### Test-diff ledger

| Existing file and test | Change | Why | Behavior still asserted? |
|---|---|---|---|
| `server/tests/test_foundation.py` / migration idempotence/private DB | Exact schema version 5 → 6 | Authorized additive migration | Yes: exact version on both startups and all privacy/idempotence assertions retained |

All other document tests are new; existing browser/core tests are unchanged.

### Core unchanged

All references below point to the same complete final E2E invocation or `check.txt`.

| Core | Passing guard |
|---|---|
| C1 send/stream/stats | `chat.spec.ts` |
| C2 stop | `chat.spec.ts`, `phase3-accessibility.spec.ts` |
| C3 resume | `chat.spec.ts`, `web.spec.ts` |
| C4 long answer/timeout | `chat.spec.ts` |
| C5 actions/branches/exports | `actions.spec.ts` |
| C6 models/load/context | `load-selection.spec.ts`, `ui-regressions.spec.ts` |
| C7 explicit sampling | `parameters.spec.ts`, `test_chat.py`, `test_presets.py` |
| C8 web/citations/retry | `web.spec.ts`, existing search/evidence/grading Python tests |
| C9 recording/transcription/storage/downloads | `transcription.spec.ts`, `recording-download.spec.ts`, `audio-storage.spec.ts`, `test_transcription.py` |
| C10 phone layout/keyboard | `mobile-layout.spec.ts`, `mobile-composer.spec.ts` |
| C11 palette/PWA/update | `polish.spec.ts`, `pwa.spec.ts` |
| C12 legacy read-only import | `test_legacy_import.py` |
| C13 deployment identity | `test_deployment.py`, deployment invariant evidence |
| C14 untrusted HTML/remote images | `foundation.spec.ts`, existing SSRF tests |
| C15 budgets | `performance.spec.ts`, chat frame and first-token tests |
| C16 axe/keyboard | Existing accessibility specs plus `documents-design.spec.ts` |

### Migrations and rollback

`006_attachment_meta.sql` adds only nullable `attachments.meta_json`. Both synthetic
Phase 3 and Phase 5A databases migrate without changing projected old columns;
old attachments receive NULL document metadata. The rollback script uses a private
copy of the actual data folder, an SQLite online backup, current app startup and
synthetic new document metadata, then restores the backup without stale WAL/SHM
sidecars and boots commit `a553702`. It removes the private copy and never modifies
production. Its health/shell/schema/row-hash result is in `rollback.json`.

### Deployment and fallback

Source commits: `444a5de` (PDF/Word attachments) and `588eb70` (preserve
empty Word table edge cells).

Deployed with `./scripts/deploy.sh --apply`, with a database backup before
installation. Local and Tailscale HTTPS health returned 200; `/design` returned
404. Existing launchd arguments and Tailscale route are unchanged. Schema is 6;
installed static bytes match the build, including `index-C9iQs0iq.js`.

Synthetic PDF and Word uploads succeeded on the installed app. Their review text
was verified, only a private extracted `.txt` remained, and DELETE removed the
synthetic files/rows. No model call or private document content was used.

The saved 5A fallback is `a553702`. Restore its database backup before deploying
the older source; the copied-data rollback rehearsal verifies this sequence.
Current source is saved in the two commits above; the final evidence commit
follows on `codex/phase-5-everyday-chat`. Earlier checkpoint evidence is restored
unchanged; this complete run's measurements are copied under `5b/regenerated/`.

### Screenshots

`screenshots.json` lists all 120 `*-fake.png` files in `artifacts/phase-5/5b/`.
PDF/Word chips, overflow, upload/extraction/failure, review text/loading/error,
all five fixed upload errors and Add menu appear at 390 and 1440 in both themes
and browser engines. Only invented synthetic document text/names are pictured.

### Evals and runtime observations

No production prompt or provider/run/search code changed. The prompt hash and
ordinary request capture guards and existing offline web tests pass. No new
real-Ollama answer/search eval was run and no claim about aggregate eval improvement
is made. Document extraction uses existing Python, pypdf, ZipFile and ElementTree.
Production document smoke testing uses synthetic uploads without model calls.

### Known limitations carried forward

VoiceOver failed in Jake's earlier check and is deferred; it did not pass.
The iOS keyboard focus issue recovered after a phone restart; its cause remains
unproven. Natural physical-phone launch motion was not instrumented in the
previous checkpoint. Physical 5B upload/review/send has not been checked by Jake.
Token counts are estimates; complex PDF reading order depends on selectable text.
Worker memory is not part of the reported uvicorn RSS sample.

### Open questions for Jake / review stop

On the phone, add a PDF and a `.docx`, tap their chips to inspect the extracted
text, then ask a question about them. Confirm the keyboard, review sheet and
response work. 5C (folders/automatic backups) waits for checkpoint review.

### 5B phone closeout — 5 October 2026

Jake: “Both PDF and .docx work.” Physical document acceptance is now user-confirmed;
this closes G-16 for 5B. Jake authorized 5C.

Jake also reported: “the animation for the sidebar and stuff stopped working,
diagnose it at a later point.” Record this as an unresolved physical motion
regression; the earlier automated motion results do not establish current phone
behavior. Diagnosis is deferred at Jake’s request while 5C proceeds.

## Checkpoint 5C — folders and automatic backups (5 October 2026)

### Summary

Chats can be organized in one-level folders, moved, removed, renamed and searched
with their folder name visible. Deleting a folder returns its chats to history.
Private automatic SQLite backups run at startup when due and daily at 03:30 on
the Mac, retaining seven copies; Settings → Data provides status and Back up now.
This is the 5C review stop. Optional forking and later phases remain unstarted.

### Done-when checklist

| Item | Status | Evidence |
|---|---|---|
| P5-AC9 folders | Pass | `test_folders_crud_move_filters_search_and_delete_keeps_chats`, `test_folder_pagination_and_empty_chats_count`; browser create/move/collapse/search/rename/cancel/delete at 390/1440 in both engines |
| P5-AC10 backups | Pass automated and copied-data rehearsal | Startup, daily timer/injected clock/DST, private online copy, row counts/integrity, seven-file retention, deploy backups untouched, low disk skip, failure/cancellation cleanup; production manual backup smoke; `rollback.json` |
| P5-AC11 QA gates | Automated checks passed; phone review pending | Gates below |
| P5-AC12 web unchanged | Frozen core guards passed; no new aggregate eval claim | No provider/run/search/prompt edits; ordinary request capture, prompt hash and all existing web tests pass |

### Changed files

- Server: additive `007_folders.sql`; `db/folders.py`, folders API; chat projection,
  assignment and optional listing filter; `backup.py`, backup API and lifecycle;
  optional chat folder fields, Folder and BackupStatus schemas.
- Web: Folders group and lazy folder dialog; Move to folder submenu; folder names
  beside search results in history and the command palette; normal history uses
  `folder=none` so pagination does not hide unfiled chats behind folder entries;
  backup status/action in Data; cache invalidation after folder/chat changes.
- Design: `/design?organize`, 21 states built from production components.
- QA: new unit/integration/browser/design tests; backup coverage target; optional
  API query-parameter guard plus regression cases; destructive/warning contrast
  pairs; exact current-schema assertions in two existing tests.
- Docs: README clean-database restore procedure; 5B user phone closeout and
  deferred motion issue recorded above; this report and `artifacts/phase-5/5c/`.

### Implementation choices and deviations

No dependencies or model-call stages were added. There are no nested folders,
drag-and-drop organization, per-folder instructions, restore UI or optional forks.
`GET /chats` without a folder filter preserves its existing set and pagination;
`folder=none` selects unfiled chats, and `folder=<id>` selects one folder. Counts
match visible history (chats with messages). Folder deletion uses `ON DELETE SET NULL`
and never deletes messages or chats. Absent folder assignment leaves it unchanged;
explicit null removes it. Existing message, sampling and web behavior is untouched.

Backups use the existing aiosqlite online-backup API under the store commit lock,
with one backup at a time and an injected local clock/disk checker for tests.
A private partial file is closed and fsynced before atomic replacement. Cancellation
waits for the actual copy before closing the destination and releasing capacity.
Only `auto-*.db` files are pruned; deploy backups remain separate. Manual backups
in the same minute atomically replace that minute's copy. Disk allowance includes
current WAL bytes in addition to the main database for a conservative size check.
Failures expose fixed warning text without filesystem paths or private contents.
The daily timer is separate from streaming; no run-state polling was added.

The API guard previously rejected any changed parameter-array length. Comparing
parameters by name/location now permits optional additions while retaining checks
for removals, type/schema changes, required additions and duplicates. Existing
guard tests remain unchanged and new cases demonstrate these constraints.

The new delete-folder design state exposed an existing `dark:bg-destructive/60`
fill with insufficient text contrast. The shared destructive Button now uses the
opaque existing danger token. Palette tokens and motion rules remain unchanged;
74 contrast pairs and the new dark-state axe scans pass.

### Test output and iteration

`make check`: **250 Python tests, 36 frontend tests, 74 contrast pairs**.
Coverage: providers 85.8%, runs 89.2%, search 88.9%, transcribe 90.7%,
documents 96.6%, new backup module 96.8%. Lint, formatting, types, API generation,
additive API, prompt/payload/privacy/motion guards pass.

Focused browser run: **16 passed** (Chromium and WebKit). Its predecessor had
12 passes and four dark delete-button contrast failures, fixed in the shared
button. No assertion was weakened. Initial new-test mistakes involved the fixture's
schema version/snapshot tuple and a missing required synthetic title source; the
new tests/fixture were corrected. Existing tests only update exact schema 6 → 7.
Synthetic screenshot captures scroll their component into view to include controls.

Final `make e2e`: **385 passed, 3 existing skips (30.9 minutes)**, one complete
Chromium/WebKit invocation against source commit `48fbb9f`. The source SHA manifest
matched before and after the run. Existing WebKit skips are the once-only real-time timeout gate, once-only
screenshot review set, and offline reload limitation requiring physical Safari;
none were added. See `source-verification.json` and `e2e.txt`.

The default `make eval-web` command was attempted, but it uses real Ollama planner
and answer calls even with frozen search fixtures. It was interrupted; its partial
output (`eval-web-interrupted.txt`) is not acceptance or aggregate comparison
evidence. No production prompt/provider/run/search code changed. Existing frozen
web, prompt and request guards pass; no new real-runtime eval improvement is claimed.

### Budgets

| Measure | 5B | 5C |
|---|---|---|
| Initial static-import JS gzip | 234,656 B | 236,159 B (+1,503 B; limit 256,000 B) |
| Streaming p95 at 100 tokens/s | 3.30 ms Chromium / 3.00 ms WebKit | 3.70 ms Chromium / 3.00 ms WebKit |
| First-token overhead | 77.59 ms Chromium / 61.15 ms WebKit | 65.34 ms Chromium / 65.26 ms WebKit |
| 300-message scroll median | 16.70 ms Chromium / 17.00 ms WebKit | 16.70 ms Chromium / 17.00 ms WebKit |

The folder dialog is lazy-loaded. Backup settings are reached through the existing
Settings chunk. `bundle.json` counts recursive static imports, excluding lazy imports.
Only the streaming row renders during the existing performance test.

### Gates

| Gate | Status | Evidence |
|---|---|---|
| G-1 check/coverage | Pass | `check.txt`; backup module ≥80%, existing coverage unchanged |
| G-2 complete E2E | Pass | `e2e.txt`, one complete invocation against frozen source |
| G-3 tests not weakened | Pass | `test-diff-ledger.md`; exact schema assertions only |
| G-4 performance | Pass | `bundle.json`, `regenerated/phase-1/`, `regenerated/phase-3/` |
| G-5 accessibility | Pass automated; VoiceOver unresolved/deferred | 168 synthetic screenshots/21 states, zero serious/critical axe; existing full keyboard walkthrough; 74 contrast pairs |
| G-6 API only grows | Pass | Guard allows new optional folder query; rejects breaking parameter changes; `check.txt` |
| G-7 database only grows | Pass | `007_folders.sql`; old Phase 3 and Phase 5B column/row projections unchanged |
| G-8 frozen prompts | Pass | Existing prompt hashes |
| G-9 web unchanged | Pass existing guards; no new aggregate eval evidence | Provider/run/search source unchanged; existing web tests and request captures |
| G-10 ordinary payload | Pass | Existing golden request and explicit parameter capture tests |
| G-11 privacy | Pass within scanner/manual limits | `privacy-audit.json`; isolated invented fixtures only; copied real data never emitted or committed |
| G-12 deployment invariants | Pass | `deployment-invariants.json`, `deployment.txt`; existing PWA/no-API-cache tests |
| G-13 motion | Automated guards pass; physical sidebar regression unresolved | Existing motion specs, unchanged motion source; Jake explicitly deferred diagnosis |
| G-14 design | Pass | `/design?organize`, screenshot/axe manifest |
| G-15 rollback | Pass | `rollback.json`: automatic restore and previous-app boot, identical rows, private backup; 4.892 s |
| G-16 Jake phone review | Not checked for 5C | Ready for review; 5B confirmation recorded above |

### Test-diff ledger

| Existing file/test | Change | Why | Behavior still asserted? |
|---|---|---|---|
| `test_foundation.py` / migration idempotence/private DB | Exact version 6 → 7 | Authorized migration | Yes; both startups, privacy, idempotence retained |
| `test_documents.py` / old metadata and row preservation | Exact version 6 → 7 | Test applies all current migrations | Yes; NULL old metadata and every projected old row retained |

No existing browser test, timeout, skip or performance threshold changed. All
folder/backup browser/unit tests and API-parameter guard regressions are new.

### Core unchanged

All browser references below are part of the same complete final invocation.

| Core | Guard |
|---|---|
| C1 send/stream/stats | `chat.spec.ts` |
| C2 stop | `chat.spec.ts`, `phase3-accessibility.spec.ts` |
| C3 resume | `chat.spec.ts`, `web.spec.ts` |
| C4 long answer/timeout | `chat.spec.ts` |
| C5 branches/actions/exports | `actions.spec.ts` |
| C6 models/load/context | `load-selection.spec.ts`, `ui-regressions.spec.ts` |
| C7 explicit sampling/presets | `parameters.spec.ts`, `phase5a.spec.ts`, Python captures |
| C8 web/citations/retry | `web.spec.ts`, Python search/evidence/grading tests |
| C9 transcription/storage/downloads | Existing transcription, audio-storage, recording-download specs and Python tests |
| C10 phone layout/keyboard | `mobile-layout.spec.ts`, `mobile-composer.spec.ts` |
| C11 palette/PWA/update | `polish.spec.ts`, `pwa.spec.ts` |
| C12 legacy read-only import | `test_legacy_import.py` |
| C13 deployment identity | `test_deployment.py`, deployment metadata |
| C14 HTML/remote-image safety | `foundation.spec.ts`, existing SSRF tests |
| C15 budgets | `performance.spec.ts`, frame/first-token tests |
| C16 axe/keyboard | Existing accessibility specs plus organization design scans |

The 5B document upload, extraction, review, context and memory guards also pass
in this run. Historical evidence stays intact; regenerated metrics live under 5C.

### Migrations and restore rehearsal

`007_folders.sql` creates folders and adds nullable `chats.folder_id` with an index
and `ON DELETE SET NULL`. No existing table is rebuilt or renamed. Both Phase 3
and Phase 5B fixtures retain every projected old column/row; old chats are unfiled.

The rehearsal makes a private full data-folder copy and SQLite online backup,
boots schema 7, adds an invented folder/chat, creates a real automatic backup,
changes only the copied database, then restores that backup into a clean database
location without stale WAL/SHM. It boots the new app and verifies identical rows.
It also restores the pre-migration backup and boots 5B commit `ed87cb2`, schema 6,
with identical old rows. All three app health/shell checks return 200. The private
copy is removed; production is unmodified; no model calls. Duration: 4.892 s.

Rehearsal command: `uv run --directory server python ../scripts/rehearse_backup_restore.py --previous ed87cb2`.
README documents the service stop, full current-folder preservation, clean DB
restore, optional matching-source rollback and chat/transcript verification.
A database-only backup cannot recreate missing attachment or library files.

### Deployment and fallback

`scripts/deploy.sh --apply` deployed source `48fbb9f`. Local and verified HTTPS
Tailscale health return 200; `/design` returns 404. Schema is 7, installed static
files match the tested build (`index-W_uSK9nx.js`), bind remains 127.0.0.1:8787
with one worker, and launchd arguments/Tailscale configuration are unchanged.
A deployment backup was made first; a startup automatic copy exists. Back up now
returned 200 and its private (`0600`) SQLite copy has integrity `ok` and matching
chat/message/transcript/folder counts. An invented folder/chat smoke verified
assignment, rename and deletion preserving the chat; synthetic rows were removed.
No answer, planner or title calls were made by this verification.

Source is saved as `48fbb9f`; the preceding accepted 5B fallback is `ed87cb2`.
Across the migration, returning to 5B uses its matching pre-migration database
copy, as rehearsed. The evidence/report commit follows the source commit.

### Screenshots

`screenshots.json` lists 168 `organization-*-fake.png` images: 21 states ×
390/1440 × light/dark × Chromium/WebKit. Folder lists, empty/loading/error states,
menus, move/search, create/rename/delete/error/busy dialogs and every backup status
appear using the production components and invented fixture data.

### Runtime observations and known limitations

No new runtime adapter or model-call stage. Existing real Ollama eval behavior
is described above; the partial interrupted eval is not a successful eval report.
Backup cadence is tested with an injected clock; no claim about days of physical
operation is made. A stopped service makes a due copy on startup; actual behavior across Mac sleep
has not been measured. The daily task uses the Mac's local time while running.

Jake reported sidebar and other animation stopped, explicitly asking for diagnosis
later. This is an unresolved physical regression, even though automated motion
checks pass. Motion diagnosis was not performed during 5C. VoiceOver previously
failed and remains deferred. The earlier iOS keyboard issue recovered after a
restart; cause remains unproven. Physical 5C folder/backup review is pending.

### Open questions for Jake / review stop

On the phone, create a folder, move a chat, collapse/reopen it, search the chat,
and delete the folder to confirm the chat returns to history. In Settings → Data,
try Back up now and check its status. Later phases wait for this checkpoint review.
