# Attachments redesign — main release report

## Summary

Jake approved the readiness report with “Go ahead and implement”. The redesign is merged into main with explicit merge commit `c6408a717a7872c42b55301e2961eb818a9aa5d7` (parents `55477ff1` and `d5540ee9`), and [PR #2](https://github.com/EviIius/agents-agenticrag/pull/2) is merged. The new UI is live at [Atelier](https://jakes-mac-mini.tailc4d343.ts.net/).

Publication completed **2026-10-17T00:01:52.307843+00:00** (16 October locally). The program tree matches reviewed `ff5f589e` byte for byte. Automated checks passed on main before publication. The server, API/schema, prompts, settings, sampling, model defaults and Tailscale route were preserved. Physical iPhone acceptance is requested and **not checked**.

## Done-when checklist

| Item | Status | Evidence |
|---|---|---|
| Explicit merge and main verification | Pass | `c6408a7`, two parents; `executed-web-source.json`: 256 unchanged web source/test hashes |
| Full check on main | Pass | `check.txt`: 673 Python / 121 frontend, 110 contrast pairs and all guards |
| One complete browser run on main | Pass | `e2e.txt`: 699 passed / three existing skips / zero failed, 1.2 hours |
| Release build reproduces tested assets | Pass | All 425 hashes match the main-suite build; unchanged bundle limits pass |
| Static-only publication | Pass | Timestamped publication record; 114 installed/repo server files unchanged |
| Service identity | Pass | Same PID `97687`, label `dev.agenticrag.workbench`, one worker, `127.0.0.1:8787`, exact original plist/route |
| Published hashes and health | Pass | 425 installed files verified; index/SW hashes and health verified locally/HTTPS; 551 old hashed assets retained |
| Production design route | Pass | `/design` is 404 on both origins |
| Private rollback | Pass | 567 old static files exactly verified; consistent SQLite backup integrity `ok`, directory 0700/database 0600 |
| Published UI with isolated fixtures | Pass after fixture remedy | Actual HTTPS bundle in Chromium 1440 and iPhone 13 WebKit 390; Tools, paste/undo, photo/viewer/remove, no overflow, native input hit target ≥44 px; zero final errors/inference requests |
| Physical iPhone | Not checked | Requested after publication; no invented response or native-picker capture |

## Changed files

- **Merged web UI:** reviewed AT-A/AT-B components, tests and original Claude resources. See the two checkpoint reports. No additional program source edit was made for release.
- **Installed app:** 425 web build files only. Old hashed assets remain for open clients. No server/interpreter/engine/model/config/glossary/dependency installation, restart or migration.
- **Docs/evidence:** release authorization/closeout in `AGENTS.md`, this report and `artifacts/attachments/release-20261016/`.

## Deviations and clarifications

The existing static publisher embeds an older release's baseline/evidence path. Its private frozen copy changes only import/root paths, the evidence directory and stable-server pin to `55477ff1`. Publication, health/hash validation, atomic-copy order and automatic static rollback logic are unchanged. Exact diff/hashes: `publisher-config.patch`, `publisher-source.json`. The repository publisher is unchanged.

Assets are installed first, then index, then service worker. The database is opened read-only for its consistent private backup; no migration or database restore occurs. Phone review follows publication as specified by the approved plan.

## Runtime observations

All 114 stable server files match original main and the installed app before/after publication. PID `97687` stays running. Local and normally validated Tailscale HTTPS health are 200; `/design` is 404 on both. No native model/image/transcription inference, download, unload, runtime upgrade, prompt or sampling/default change was performed.

The installed-UI observer loads the actual HTTPS build and intercepts all API data with synthetic fixtures. Service workers are blocked only in that observer to guarantee interception; PWA/cache/update behavior passes the complete main suite. No real history, filenames, screenshots, video or native picker is captured. This is browser verification, not a physical phone result.

## Test output and retained observations

- `make check` on main: **673 Python / 121 frontend / 110 contrast pairs**, plus types/lint/format/coverage/API/privacy/motion guards.
- One complete `make e2e` on main: **699 passed / three existing skips / zero failures**. The source manifest is rechecked; no program changes follow.
- Fresh release build: **425 files**, exactly reproducing all main-suite build hashes. Initial JS: **254,448 gzip bytes**.
- 120 fresh synthetic main-suite screenshots/state scans have zero serious/critical findings. Historical evidence is preserved privately and restored: **1,424 tracked files**, plus 40 generated historical-area files moved privately. Prior AT-A/AT-B evidence is unchanged.
- The first installed-UI observer fails its own zero-error assertion: its fixture returns JSON for `/api/workflows/stream`, an EventSource path not ending in `/events`. Source inspection identifies that path. Recognizing EventSource resource type/Accept headers supplies the correct synthetic stream MIME type. The same UI/zero-error/inference assertions then pass in both engines. Both sources/logs are retained; product files are unchanged.
- An inherited AT-B check log has an extra EOF blank line, reported by the first merge precommit whitespace check. Its historical bytes are preserved. No product/test gate is relaxed. Observer preparation also corrected tool-env and exact selectors before browser execution; preparatory sources remain private.

The unchanged WebKit skips are the real-time long-response/idle gate executed in Chromium, duplicate review screenshot capture, and offline reload (Playwright limitation). No skip, deadline, test or performance threshold changes for release. Original AT-A/AT-B test-diff ledgers remain applicable. No native accuracy eval runs because search/runs/providers/retrieval/prompts are unchanged; no grounding qualification is claimed.

## Screenshots

`artifacts/attachments/release-20261016/browser/`: 120 synthetic screenshots, 15 states across both engines, widths and themes. `accessibility-summary.json` indexes them. Original Claude references and checkpoint evidence remain unchanged. No live screenshot is captured.

## Gates

| Gate | Status | Evidence |
|---|---|---|
| G-1 checks/coverage | Pass | `check.txt`, `coverage.json` |
| G-2 single complete browser run | Pass | `e2e.txt`: 699 / 3 existing skips / zero failed |
| G-3 tests preserved | Pass | No release test edits; reviewed source and previous ledgers unchanged |
| G-4 budgets | Pass | `bundle.json`, `performance/summary.json`, identical tested/release build |
| G-5 automated accessibility | Pass | Fresh axe scans, full keyboard/core suites, 110 contrast pairs |
| G-6 API | Unchanged/pass guard | Frozen source, additive guard |
| G-7 database | Unchanged/pass tests | No migration; row-preservation tests and verified private backup |
| G-8 prompts | Unchanged/pass guard | Frozen source/hash guard |
| G-9 answers | Unchanged | No provider/search/run/retrieval/prompt edit; no accuracy eval |
| G-10 requests | Pass | Prior 24 raw captures, exact program parity and fresh main parameter/send checks |
| G-11 privacy | Pass within audit limits | Synthetic fixtures, no live API data/capture, private backups/history preservation |
| G-12 deployment | Pass | Same PID/service/worker/bind/route; installed hashes, PWA and 404 checks |
| G-13 reduced motion | Pass | Full main temporal/both-trigger suites |
| G-14 design states | Pass | Fresh fixture scans; production route remains 404 |
| G-15 migration rollback rehearsal | Not applicable | No migration; verified private static/database fallback |
| G-16 phone | Not checked | Requested after publication; quote pending |

## Core unchanged (C1–C16)

| Core | Passing evidence from this main invocation |
|---|---|
| C1 send/stream/stats | `chat.spec.ts`, `working-indicator.spec.ts` |
| C2 stop/partial | `chat.spec.ts`, `phase3-accessibility.spec.ts` |
| C3 reconnect | `chat.spec.ts`, `handoff.spec.ts`, `web.spec.ts` |
| C4 long/idle responses | `chat.spec.ts` Chromium real-time gate |
| C5 chat actions/branches/exports | `actions.spec.ts`, `refinement.spec.ts` |
| C6 load/select/context | `load-selection.spec.ts`, `ui-regressions.spec.ts` |
| C7 explicit parameters | `parameters.spec.ts`, Python request captures |
| C8 web/citations/failure | `web.spec.ts`, search/evidence/grading units |
| C9 recordings | `transcription.spec.ts`, `recording-download.spec.ts`, `audio-storage.spec.ts`, transcription units |
| C10 phone layout/typing | `mobile-layout.spec.ts`, `mobile-composer.spec.ts` |
| C11 palette/PWA/shortcuts | `polish.spec.ts`, `pwa.spec.ts` |
| C12 read-only legacy import | `test_legacy_import.py` |
| C13 deployment invariants | `test_deployment.py`, actual publication verification |
| C14 untrusted content/SSRF | `foundation.spec.ts`, search SSRF units |
| C15 performance | `performance.spec.ts`, chat timing/frame tests, bundle measurement |
| C16 automated accessibility | Full axe/keyboard suites; physical phone pending |

## Budgets

Initial JS: **254,448 gzip bytes** vs deployed 248,048 (+6,400), within both the 256,000-byte total and 8,192-byte increment limits. No dependency added.

| Engine | First-token UI delay (<150 ms) | Streaming render p95 (≤8 ms) | 300-message scroll p95 |
|---|---:|---:|---:|
| Chromium | 84.7 ms | 3.2 ms | 16.8 ms |
| WebKit | 62.0 ms | 3.0 ms | 20.0 ms |

Raw samples/maxima and render-row counts are retained; only the streaming row renders during the measured stream.

## Published hashes

- Index SHA-256: `06a11229828da1c196a1a6627642d7f7529e2ba5f6373fcfaddbc8a2c04de209`
- Service worker SHA-256: `0161f71981056168129c80f45a8329870873c8ca4877ecb61b0c563cefd9baac`
- All 425 paths/hashes: `artifacts/attachments/release-20261016/release-manifest.json`.
- Merge/published source: `c6408a717a7872c42b55301e2961eb818a9aa5d7`.

## Rollback

Private directory: `/Users/evilius/.local/share/workbench/data/backups/composer-static-20261017T000150014964Z`.

The complete old static tree and consistent `workbench.db` are retained and verified. Ordinary UI rollback restores saved assets using the publisher's atomic-copy order, index/service worker last; retain the current database because this release has no schema/data migration. Original main `55477ff1` and the reviewed branch remain in Git history. No restore is executed during this successful rollout.

## Known limitations and next acceptance

Historical iPhone keyboard recovery after restart remains recorded with cause unproven. VoiceOver stays excluded; no pass is claimed. Automated typing/native-input-target checks pass, but Home Screen/native-picker behavior needs Jake's observation. Reopen Atelier (accept its update prompt if shown) and report the requested picker/tray/Tools/send checks; long-paste undo is optional. No further implementation approval is needed for the published release.
