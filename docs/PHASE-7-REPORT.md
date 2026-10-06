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
