# Phase 7 report — checkpoint 7A

## Summary

Jake accepted the technical 7-0 probe with “Not sure how to verify it, so I guess
continue on”; no individual phone results are inferred. Library storage, ingestion
and Settings are implemented. Files can be indexed, organized, opened, re-indexed
and deleted. This checkpoint stops for review; answering from Library files and
its citation UI belong to 7B. The prior 7-0 report is retained below.

## Done-when checklist

| Item | Status | Evidence |
|---|---|---|
| P7-AC1 probe | Pass, retained | `candidate/probe-active-{development,installed}.json`; approved sqlite-vec 0.1.9 |
| P7-AC2 existing rows/citations | Pass | Existing projected-row fixture tests; `7a/rollback.json`, private current-data copy, schema 7→8→7 |
| P7-AC3 five formats/page ranges | Pass | `test_library.py` synthetic PDF, Word, Markdown, text, HTML; exact per-page PDF ranges |
| P7-AC4 restart recovery | Pass | Queued recovery and atomic chunk/vector replacement tests |
| P7-AC5 concurrent chat | Pass | Shared-semaphore test: existing chat starts streaming between embedding batches |
| P7-AC6 delete storage/history | Storage pass; historical UI deferred to 7B | Original/chunk/FTS/vector deletion and preserved source snapshots tested; no Library answer UI exists at 7A |
| P7-AC7 model change/re-index | Pass | Dimension changes, stale documents, stored-chunk re-index with no re-extraction |
| Library Settings | Pass automated | `library.spec.ts`, both engines/widths/themes, all 24 preview states |
| No chat behavior/prompt change | Pass automated | Full existing core suite and frozen prompt/API/payload guards |
| User checkpoint review | Pending 7A | This report; no new physical iPhone check claimed |

Evidence paths are relative to `artifacts/phase-7/`.

## Changed files

- Server: additive migration `008_library.sql`; new `library/` extraction worker,
  supervised extraction and durable ingestion manager; `api/library.py`; additive
  settings/bootstrap/router/schema wiring; upload-space guard reused for Library.
- Web: lazy `Settings › Library`, pure production view/feedback components and
  `/design?library` preview; Settings tab registration and generated API types.
- Tests: 22 new Library server cases, 14 new browser cases across both engines;
  explicit embedding-only fake-runtime models. Three existing migration tests
  retain their exact checks with schema version 8. `7a/test-diff-ledger.md` lists
  each edit; no existing browser test changed.
- Checks/docs: Library coverage target 80%; approval/acceptance recorded in
  `AGENTS.md`; this report; synthetic screenshots and metadata-only evidence.

Source checkpoint: `5f43800` on `codex/phase-7a-library`. Accepted 7-0 fallback:
`c1ecc2b`. Source files are frozen through the complete browser invocation.

## Deviations from SPEC.md

- Durable progress columns/events support resumable SSE, with no progress polling.
  A nullable full extracted-text column preserves complete text for “Open”; the
  existing chunker may omit paragraphs unsuitable for retrieval. No old column
  or table is rebuilt; the existing web citation table is untouched.
- An additive `POST /api/library/embedding` validates registry capability and
  probes the actual vector dimension before changing selection. Generic settings
  cannot accept a caller-invented dimension. No capability is inferred from names.
- PDF pages are chunked individually with the unchanged search chunker, giving
  exact page-start/page-end metadata. Markers are removed from passage text.
- The selected extension has no need for a separate `library/store.py`; the
  manager uses the existing transaction/Store abstraction and loads only the
  approved extension, then disables extension loading.
- First embedding selection preserves queued uploads. Subsequent model changes
  mark documents stale; re-index uses retained chunks. Query-prefix changes do
  not force document re-index; document-prefix changes do.
- P7-AC6’s “What the model saw” UI is structurally a 7B acceptance item. Its 7A
  durability contract is tested, and the UI portion is explicitly outstanding.

## Runtime observations

`7a/real-ingestion-fake-document.json`: the complete application ingested a
committed synthetic two-page PDF through real loopback Ollama using approved
`qwen3-embedding:0.6b`, measured 1,024 dimensions, two passages and `ready` in
1.547 seconds. Two embedding requests (selection probe and ingestion), no chat
call; deletion removed the original/index and the isolated temporary data was
cleaned. This is not a throughput promise for large or private documents.

The extraction subprocess suppresses stdout/stderr and parser logging. Safe error
codes convey failures; private document text/names are not emitted. Library
originals remain in the private data directory to support future citations.
The earlier temporary-audio retention policy is unchanged. Existing automatic
backups remain SQLite-only: they include extracted Library text, chunks and
metadata, but original files need a separate backup of the private Library folder.

An optional web-eval attempt was mistakenly invoked in its real-model default
mode and terminated before completion. It used only committed synthetic/public
eval fixtures and existing local planner/answer calls; no report or score was
produced, and no web-eval pass is claimed. Its log contains 48 successful
chat HTTP response lines before termination. The G-9 change trigger does not apply:
search, run, provider and prompt sources are unchanged. P7-AC13’s complete replay
requirement remains a later full-Library gate before phase closure.

## Test output

`make check`: 279 Python and 36 frontend tests passed; 74 contrast pairs;
lint, types, formatting, coverage, API additive guard, row/payload guards, motion,
privacy and frozen prompts passed. Library coverage: 458/470 = 97.4% (80% gate).

Second complete `make e2e`: **417 passed, 3 existing documented skips, 0 failures**,
**35.4 minutes**, both engines. All 379 frozen source hashes stayed unchanged
through both full invocations. No partial-run assembly. The existing skips cover
the once-on-Chromium real-time timeout and foundation review checks, and
Playwright WebKit’s offline service-worker navigation limitation. The previously
failed WebKit copy test passed all original assertions in 5.3 seconds; its prior
intermittent failure remains listed, with root cause unresolved.

### Development failures and corrections

Tests found initial queued-upload handling, a fake embedding endpoint that changed
the existing search-fallback fixture, and a full-text SQL binding error. These
were corrected before the frozen full suite. Two interrupted focused browser
attempts exposed wrong invocation cwd, same-model selection setup and generic
duplicate-error copy; normal web cwd, explicit isolated reset and safe Library
ApiError feedback fixed them. No assertion/threshold/timeout was weakened and no
new skip was added. A private rollback rehearsal initially retained SQLite
handles during directory cleanup; explicit closes corrected the operations
script. Actual production data was not modified by that failed rehearsal.

The focused Library run passed 14 cases, but only a complete frozen run is
the regression gate. Its log is retained separately. The first complete run
finished with 416 passed, three existing skips and one existing WebKit copy test
failure (36.6 minutes). Its locator remained outside the viewport; a separate
debug click succeeded, but the root cause is unresolved. The failed log, safe
error context and synthetic trace frame remain under `7a/`. This intermittent
copy-check failure is explicitly listed for Jake; no assertion or timeout changed.

### Performance

Initial JavaScript: 237,762 bytes gzip, +87 from the accepted 237,675-byte baseline,
below 256,000. Library Settings remains lazy-loaded.
Streaming render p95: **3.1 ms Chromium / 3.0 ms WebKit**. First-token
overhead: **73.61 / 58.92 ms**. The 300-message scroll median: **16.7 / 16 ms**.
Only the streaming row rendered. See `7a/regenerated-metrics/phase-{1,3}/`.
The existing sidebar candidate test rejected width animation on WebKit (25 ms
p95); its fallback remains active. This does not close the reported physical
sidebar motion issue.

The final 100 MiB browser-upload RSS observations were +81,920 bytes Chromium
and +0 bytes WebKit, sampled every 50 ms (10 and 5 samples); both are below the
20 MiB gate. These samples exclude the extraction subprocess and are not a claim
of zero allocation. `7a/upload-memory-{chromium,webkit}-fake.json`.

### QA gates

| Gate | Evidence / disposition |
|---|---|
| G-1 check/coverage | `7a/check.txt`, `7a/coverage.json` |
| G-2 one complete green run | `7a/e2e.txt`; prior copy-test failure explicitly retained/listed |
| G-3 ledger | `7a/test-diff-ledger.md`; no existing browser edits/new skips |
| G-4 budgets | `7a/bundle.json`, complete performance suite, streamed 100 MB upload RSS check |
| G-5 axe/contrast/keyboard | 24 Library states × two engines × two widths × two themes; existing core keyboard suite; VoiceOver deferred |
| G-6 API additive | `make check`; new routes/types only; old contracts retained |
| G-7 rows/migrations | Existing synthetic fixture hash guards; current-data private-copy migration/rollback; web citations unchanged |
| G-8 frozen prompts | Hash guard passed; no prompt source change |
| G-9 web eval | Change trigger not applicable; interrupted optional attempt ungraded; full-phase replay still outstanding |
| G-10 runtime payloads | Existing golden/parameter/preset assertions; Library uses embed, no product chat calls added |
| G-11 privacy | `7a/privacy-audit.json`, `7a/committed-source-privacy.json`, `7a/screenshot-review.json`; synthetic-only captures, no real document names/text in evidence |
| G-12 deployment | `7a/deployment.json`: local/TLS 200, engine ready, production design 404, invariant hashes unchanged |
| G-13 reduced motion | Existing motion tests pass; reported physical sidebar/other regression remains deferred |
| G-14 design states | All 24 Library states represented by production view/feedback on `/design?library` |
| G-15 rollback | `7a/rollback.json`: private current-data copy, online backup, 7→8→7, old/new ASGI health 200, 0.962 seconds |
| G-16 review | 7-0 accepted by Jake; 7A review pending; no individual new phone test attributed to Jake |

Core C1–C16 remain covered by the existing chat, actions/export, model/context,
parameters, web, transcription/cleanup/storage, mobile/composer, shortcuts/PWA,
legacy import, deployment, untrusted-content, performance and keyboard/axe suites.
No legacy data is modified. No additional package, runtime or chat model call is
part of 7A; the approved sqlite-vec and embedding model are retained.

## Screenshots

`7a/screenshots/library-{change-model,delete-all,embedding,ready}-{390,1440}-
{light,dark}-{chromium,webkit}-fake.png`, plus eight `library-*-files-*-fake.png`
views: 40 synthetic preview captures inspected
by Codex. These are browser observations, not physical iPhone observations.
The axe JSON files cover all 24 states in each engine/width/theme combination.
Screenshots preserve the viewport and may require scrolling to see lower rows;
the DOM accessibility/overflow checks cover the complete state. One additional
synthetic frame from the failed copy test was inspected and retained under
`7a/failures/`; it contains no private document or recording.

## Deployment and fallback

`7a/deployment.json`: the exact frozen application files are installed, schema
8 is active, Library’s approved extension is available, and embedding selection
starts unset so the user chooses it in Settings. No production file was uploaded
or used as a fixture. Local and verified TLS health are 200; transcription is
ready; production `/design` is 404. Bootstrap succeeded on its first attempt.
Before migration, the service was stopped and an online schema-7 database backup
and private copy of the previous public source were preserved. No interpreter,
package, engine asset, plist or Tailscale change was made. Public operation scripts
are retained under `7a/`; dependency manifests match the already approved lock.
302 historical tracked artifacts were restored; 21 current metric JSON files are
preserved under `7a/regenerated-metrics/`; 40 newly generated outputs outside 7A
were moved to private quarantine. Text normalization removes trailing whitespace
and blank EOF lines only; test outcomes are unchanged.

The accepted installed interpreter, transcription interpreter selection, launchd
label, one worker, loopback port and Tailscale route are retained. The service
operates independently of Codex usage limits. Tests temporarily owned port 8787;
their wrapper restores the accepted installed service on exit, including failure.

Rollback: stop the existing launchd job; restore the private source copies recorded
in `7a/deployment.json` into installed `server/app` and `shared`; with all database
handles closed, restore its online schema-7 backup to `data/workbench.db`, removing
only its WAL/SHM sidecars; bootstrap the unchanged plist and verify local/TLS health.
The source/DB backup is private and stays outside Git. Reverting only code is
insufficient because the schema changed. See successful rehearsal evidence.

## Open questions for Jake

Review 7A in Settings → Library: choose the approved embedding model, add a test
file and confirm it reaches Ready; try collections and removal. No model answer
from Library files is offered yet. Stop here per the 7A plan. J7 retrieval/answer
eval targets need approval before 7B; optional 6B remains skipped and Research is
not authorized. Existing VoiceOver and deferred motion limitations remain open.

---

The following report preserves the historical 7-0 review state; its acceptance
and 7A authorization are recorded above and in `AGENTS.md`.

# Phase 7 report — checkpoint 7-0

## Summary

The Library probe passes in the development and actual installed server interpreters.
The approved uv-managed Python 3.14.7 build supplies SQLite extension loading;
`sqlite-vec` is pinned at 0.1.9 and the selected embedding model is already installed.
The full existing suite passes, and Atelier is live with its original environments
and a private database backup preserved. No Library product code or migration
was added. Stop here for the planned 7-0 review before 7A.

## Done-when checklist

| Item | Status | Evidence |
|---|---|---|
| J3 dependency approval | Approved | Jake: “go ahead” to the explicit package/model question; `AGENTS.md` |
| J8 model selection | Approved | `qwen3-embedding:0.6b`, Ollama reports `embedding`; no model download |
| Interpreter remedy | Verified and active | Jake: “go ahead” to isolated Python preparation/testing with the original runtime preserved for rollback; `candidate/promotion.json` |
| Step 1: SQLite loads extension | Pass, both actual environments | `probe.json`, `candidate/probe-active-{development,installed}.json`, version `v0.1.9` |
| Step 2: aiosqlite through `db/core.connect()` | Pass, both | Same files; isolated temporary data, schema 7; loading disabled after load |
| Step 3: 20,000 × 768 / 50 queries / k40 | Pass, both | Actual p95 under 17 ms, sorted finite distinct results; raw timings retained |
| Step 4: full 3,000-character passage | Pass, both | `truncate: false`, HTTP 200; 557 evaluated tokens; reported context 32,768; 1,024 returned dimensions |
| Core regression gates | Pass automated | `candidate/check.txt`, `candidate/e2e.txt` |
| Live service and engine | Pass metadata checks | Local/TLS Tailscale HTTP 200; engine ready; `candidate/promotion.json` |
| User checkpoint review | Pending | This report; 7A has not started |

All evidence paths below are relative to `artifacts/phase-7/` unless noted.

## Changed files

- Server metadata: `server/pyproject.toml`, `server/uv.lock` add only
  `sqlite-vec==0.1.9`; no other dependency version changed.
- Scripts: `scripts/probe_library_extension.py` records the original prerequisite;
  `scripts/probe_library.py` runs the four steps against temporary synthetic data.
  `scripts/privacy_audit.py` extends the existing artifact/image guard to Phase 7.
- Docs: `AGENTS.md` records approval and the interpreter remedy; this report.
- Evidence: `probe.json`, original blocked results, candidate installation/probe/
  checks, the single full browser run, performance, screenshots and promotion metadata.
- Local deployment: development/installed virtual environments now use the
  verified managed Python; installed manifests match the approved frozen lock.
  Old environments remain in a private fallback folder. No engine interpreter change.
- No tracked application, frontend, shared payload, test or migration file changed.

Source checkpoints: initial blocker `7a25137`; probe/remedy preparation `5fcbe1f`.
Accepted 6A fallback: source `533418b`, evidence `19c25a1`, acceptance `4ada059`.

## Deviations from SPEC.md

The original framework Python 3.14.7 lacked `enable_load_extension`. The required
stop was honored, evidence committed, and Jake authorized the isolated remedy.
The managed distribution retains Python 3.14.7 and all Python package versions;
its bundled SQLite is 3.53.1 rather than 3.50.4. No alternate SQLite package,
storage design, second model runtime, migration or new chat model call was added.

The roadmap authorization example points to §6.3; the actual Library answer
prompt is §5.3. `AGENTS.md` records the correct section. No prompt was edited.
The 768-dimension benchmark is separate from the chosen model's measured 1,024
output dimensions. Future storage must use the actual model shape.

## Runtime observations

The original failure is preserved in `probe-initial-blocked.json` and the
individual initial interpreter JSON files. Both environments could import the
same extension binary but their framework Python could not enable loading.
The managed candidates, then both actual active environments, passed all four
steps. Context and capability came from Ollama metadata, not model-name inference.
No truncation, vector or passage text is logged. Four embedding requests total
(two candidate, two active verification), all invented text to loopback Ollama.
No answer, planner, title or clean-up model call was made by this probe.

The first runtime activation hit a nonzero launchd bootstrap result. Its script
restored both environments and manifests; the initial recovery bootstrap did not
recover health. A manual bootstrap restored the original service with local and
TLS health 200. Initial stderr was not captured, so the exact cause is unproven.
`candidate/promotion-attempt-1.json` preserves this operational failure.
The second activation waited for the old listener to exit and captured/retried
bootstrap registration; bootstrap succeeded on its first attempt and active
probes, health and engine-ready checks passed. No test was rerun or weakened to
hide the operational failure. Text logs have only trailing whitespace and blank
EOF normalization for Git; outcomes and line contents are retained. `candidate/promotion.json` records the successful
switch, preserved environments and pre-switch database backup.

An initial blocked-attempt health helper using framework `urllib` also encountered
its missing default CA store. Existing `httpx` was used with certificate
verification enabled; no SSL bypass or application change occurred.

Reference documentation: [sqlite-vec Python loading](https://alexgarcia.xyz/sqlite-vec/python.html),
[stable package release](https://pypi.org/project/sqlite-vec/0.1.9/),
[Ollama embedding truncation behavior](https://docs.ollama.com/api/embed),
[uv managed Python installations](https://docs.astral.sh/uv/concepts/python-versions/).

## Test output

- `make check` on the managed development candidate: **257 Python**, **36 frontend**,
  **74 contrast pairs**, exit 0. Lint, types, API types/additive guard, frozen prompt,
  projected-row/payload guards, motion and privacy pass. Coverage: providers 85.8%,
  runs 89.2%, search 88.9%, transcribe 93.1%, documents 96.6%, backup 96.8%.
- One complete `make e2e`: **403 passed, 3 existing documented skips, 0 failures**,
  **33.8 minutes**, Chromium and WebKit. No partial-run assembly. All 369 source
  hashes remained unchanged through that invocation, at source `5fcbe1f`.
- Existing skips: real-time long-stream gate runs once on Chromium; foundation
  review captures once on Chromium; Playwright WebKit offline service-worker
  navigation limitation. No new skip, assertion edit or timeout change.
- Probe script lint/format and `git diff --check` pass; no new product package
  needs a coverage target. New probe scripts execute against real approved dependencies.

### Performance

Initial JS remains **237,675 bytes gzip**, **0-byte delta** from 6A, below 256,000.
Streaming render p95 is **2.6 ms Chromium / 3.0 ms WebKit**; first-token overhead
**62.13 / 57.69 ms**. The 300-message scroll median is **16.7 / 17 ms**.
`candidate/bundle.json` and `candidate/regenerated/phase-{1,3}/` contain results.
The vector benchmark timings do not establish retrieval quality or answer latency;
J7 eval-target approval remains required before 7B.

### QA gates and core unchanged

| Gate | Evidence / disposition |
|---|---|
| G-1 check/coverage | `candidate/check.txt`, regenerated coverage JSON |
| G-2 one green full run | `candidate/e2e.txt` |
| G-3 test ledger | No test file changed; existing privacy guard only gains Phase 7 coverage |
| G-4 budgets | Bundle/performance figures above; passing existing performance specs |
| G-5 axe/contrast/keyboard | Existing design/review/keyboard suites green at both widths/themes; no new UI state; physical VoiceOver remains deferred |
| G-6 API additive | Guard passes; app schemas/routes unchanged |
| G-7 rows/migrations | Existing synthetic fixture upgrade guard passes; no migration; active schema 7 |
| G-8 frozen prompts | Existing hashes pass; none changed |
| G-9 web eval | Not triggered: search, runs, providers and prompts unchanged |
| G-10 runtime payloads | Existing golden/parameter assertions pass |
| G-11 privacy | `candidate/privacy-audit.json`; synthetic capture discipline and all eight saved images visually reviewed |
| G-12 deployment | Production code unchanged; plist hash/one worker/bind/port unchanged; TLS health; pre-switch backup; production design route checked |
| G-13 reduced motion | Existing motion suite passes; reported physical motion issue remains deferred |
| G-14 design states | No new product/UI state; existing production design states re-tested |
| G-15 migration rollback | Not triggered: no migration; environment restoration occurred after first activation failure |
| G-16 user review | Pending 7-0 review; no new physical phone observation attributed to Jake |

| Core | Passing suite / guard in the single run or check output |
|---|---|
| C1 send/stream/stats | `chat.spec.ts` |
| C2 stop/partial | `chat.spec.ts`, `phase3-accessibility.spec.ts` |
| C3 reopen/reconnect | `chat.spec.ts`, `web.spec.ts` |
| C4 long answer/idle timeout | `chat.spec.ts` |
| C5 actions/export | `actions.spec.ts`, `chat-export.spec.ts` |
| C6 model/context | `load-selection.spec.ts`, `ui-regressions.spec.ts` |
| C7 parameters | `parameters.spec.ts`, server request/preset tests |
| C8 web/citations/failure | `web.spec.ts`, unchanged web/search unit guards |
| C9 recording/retention/clean-up | `transcription.spec.ts`, `recording-download.spec.ts`, `audio-storage.spec.ts`, `cleanup.spec.ts`, server tests |
| C10 mobile layouts/composer | `mobile-layout.spec.ts`, `mobile-composer.spec.ts` |
| C11 shortcuts/PWA | `polish.spec.ts`, `pwa.spec.ts` |
| C12 legacy import | `test_legacy_import.py` |
| C13 deployment | `test_deployment.py`, actual promotion checks |
| C14 untrusted content | `foundation.spec.ts`, SSRF tests |
| C15 budgets | `performance.spec.ts`, chat timing tests |
| C16 axe/keyboard | Foundation, review, Phase 3 accessibility and existing design suites |

## Privacy, deployment and fallback

Probe databases are private temporary directories and are removed. No real
recording, filename, transcript, glossary term or document was read for the probe
or captured in evidence. Promotion opened the current Workbench database only
for a private backup and schema/integrity checks; no production rows were emitted.
Legacy data was not opened. The backup itself and runtime environments remain
outside Git. The real transcription interpreter selection hash is unchanged.

The full browser run requires exclusive port 8787: the accepted live service was
temporarily stopped, then restored automatically by the shell wrapper before
runtime activation. Health restoration is recorded in `candidate/service-restored.json`.
The final promotion preserves 71 installed application source files, the plist,
Tailscale forwarding configuration and all existing engine assets. The active
service and actual probes pass after the switch. Installed dependency manifests
now match the approved lock; production has 47 packages, equal in name/version to
the preceding installed environment including the previously approved extension.
Development has the same 60 package versions as the preceding checkout environment.

`candidate/promotion.json` contains the exact backup/fallback paths and environment
moves. To revert this schema-7 runtime remedy: stop the existing launchd job, remove
only the candidate aliases recorded there, move each active environment back to
its recorded candidate location, restore each preserved `.venv` to its original
target, restore installed `pyproject.toml`/`uv.lock` from the fallback folder, then
bootstrap the unchanged plist and verify local/TLS health. Keep the managed Python
and data backup available. Original environments must be restored to their target
paths for their existing entry-point paths. No database restore is needed for
this environment-only change; there is no migration.

Earlier phase evidence was restored after capturing current metrics separately.
`candidate/archive.json` records 298 historical files restored, 22 metric files
archived, and 40 newly generated historical outputs moved to a private temporary
folder. The old phase fallback evidence remains intact.

## Screenshots

Eight synthetic regression screenshots are saved under `candidate/screenshots/`:
partial-clean-up at 390 and cleaned-chip at 1440, light/dark, Chromium/WebKit.
All were visually inspected. They are existing production components, not new
Library UI. No live iPhone screenshot or physical review was performed here.

## Open questions for Jake

Jake accepted the technical checkpoint and authorized 7A on 5 October 2026:
“Not sure how to verify it, so I guess continue on”. No physical phone result is
inferred from this acceptance. No embedding-model pull
is needed. Eval targets J7 still require approval before 7B, and Research remains
gated. VoiceOver, the earlier unexplained iOS keyboard incident and the reported
sidebar/other physical motion issue retain their prior unresolved/deferred status.
