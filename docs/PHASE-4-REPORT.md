# Phase 4 report — validated 4A–4D preview, phone review pending

## Summary

4A is validated: contract, data, prompt and motion guards; locked dependency resolution; production components on `/design`; a shared engine-reported audio extension list; removal of duplicate fixtures and the tracked `.DS_Store`.
Production presentation is unchanged: all 50 synthetic screenshots match the original build pixel for pixel.
The app-shell split (4A.6) passed its separate full regression run. 4B adds first-party CSS motion to production overlays and controls, with both reduced-motion triggers. Its final complete browser invocation passed 247 tests with 3 existing skips.
The 4B preview was deployed and verified on the existing Tailscale route. Jake subsequently authorized Codex to inspect the live app, correct chat exports and continue 4C. 4C is now validated and installed: 289 browser tests passed with the same 3 existing skips. 4D is also validated and installed as Atelier: 307 browser tests passed with the same three existing skips. Phase 4 awaits Jake’s required physical-phone review.

## Done-when checklist

| Item | Status | Evidence |
|---|---|---|
| Baseline | Pass | `artifacts/phase-4/baseline/check.txt`, `e2e.txt`, `bundle.json` |
| 4A.1–4A.5 guardrails and production fixtures | Pass | `artifacts/phase-4/4a-components/check.txt`; 212 Python, 36 frontend, 56 contrast checks |
| Complete component regression run | Pass | `artifacts/phase-4/4a-components/e2e-final.txt`: 223 passed, 3 existing skips |
| No production pixel changes | Pass | `artifacts/phase-4/4a-components/screenshot-diff-final.json`: 50 exact matches |
| Dependency resolution unchanged | Pass | `artifacts/phase-4/baseline/dependency-constraints.json`, `npm-ci.txt` |
| 4A.6 split | Pass | `artifacts/phase-4/4a-split/check.txt`, `e2e.txt`: 223 passed / 3 existing skips; `move-audit.json` verifies unchanged function bodies; 50 exact screenshot matches |
| 4B foundation | Automated checks pass | `4b/check.txt`, `build.txt`, `e2e.txt`: 247 passed / 3 existing skips in one complete invocation |
| Installed preview | Pass | `4b/deploy.txt`, `deployment-verification.json`: health 200, Tailscale 200, production `/design` 404; installed static files match |
| 4C conversation and chat export chooser | Pass | `4c/check.txt`, `e2e.txt`: 289 passed / 3 existing skips; `deployment-verification.json` |
| 4D visual refinement and Atelier identity | Automated checks and deployment pass | `4d/check.txt`, `e2e.txt`, `deployment-verification.json`, `live-observation.json` |
| Phone review | Not checked | Codex live observations recorded below; Jake review remains due at 4D |

## Changed files

- Server tests: `test_phase4_guards.py`, `test_prompt_hashes.py`, synthetic Phase 3 database fixture.
- Scripts: API compatibility, motion and privacy guards; database fixture generator; synthetic capture and pixel comparison tools.
- Web: dependency ranges; production fixture bindings; shared audio extensions; removal of five duplicate UI implementations; finite-animation settlement before screenshots/axe.
- Web split: `useSend`, `useUploads`, `useModelOps`, `useShortcuts`, `ChatMenu`, `HistoryList`, `EmptyState` and `Panels`; no business-logic changes.
- Docs: reviewed `docs/next/` roadmap, authorization in `AGENTS.md`/`SPEC.md`, this report and checkpoint evidence.
- 4B web: `styles/motion.css`, shared reduced-motion hook, production primitive cleanup, conditional overlay presentation retention, `/design` motion harness and 24 Chromium/WebKit motion checks.
- No `server/app` file changes and no database migration.

## Deviations from SPEC.md

The keyboard walkthrough exposed an existing Chromium race during model-switch/new-chat navigation. Original HEAD reproduced it in 1 of 3 isolated repetitions. The test now awaits the new-chat heading and finite motion and additionally verifies toggle focus before pressing Enter. No assertion, timeout, budget or skip was weakened. Six isolated repetitions then passed, followed by the complete green suite. See `keyboard-original-head.txt`, `keyboard-settled.txt` and `artifacts/phase-4/test-diff-ledger.md`.
An intermediate full run was interrupted during review to preserve the original picker behavior for cached models while offline; only the final complete invocation counts as the gate.

4B retains closing overlay presentation data so Radix Presence can finish the CSS exit. Logical close, cancellation and mutation callbacks remain immediate; closing contents are inert. Reopening resets initial chat titles/download formats. This is documented in Phase 4 §4.4 and checked in `motion.spec.ts`. Vaul retains ownership of its drag physics; Sonner retains its toast motion.

The first complete 4B run had 233 passes, 14 failures and the same 3 skips. Twelve failures measured the 44 px recording-dialog target during entrance scaling. Two Escape/shortcut sequences overlapped closing layers. The affected tests now await finite motion before geometry or sequential overlay handoffs, retain every original assertion and additionally check closure/focus. All 36 repeated affected-flow checks passed in Chromium/WebKit (`4b/affected-tests.txt`). The final complete invocation subsequently passed; `4b/e2e-first.txt` and `4b/palette-race-fake.json` retain the failure evidence.

The second full run passed 245 cases and failed two WebKit motion tests at the driver polling deadline. The replacement measurement records logical close and actual DOM detachment on the browser clock, asserting the same ≤400 ms budget; polling/trace overhead is excluded. All 48 repeated motion checks passed in Chromium/WebKit with the same 400 ms budget (`4b/motion-timing-tests.txt`), with no application changes. `4b/e2e-second.txt` retains that run. The third full invocation passed 247 tests with the same 3 existing skips (`4b/e2e.txt`); this is the complete green acceptance run.

## Runtime observations

Synthetic fake runtime only. No new runtime, dependency, model call, sampling parameter or prompt. No live recording or transcript was captured.

## Test output

- Baseline: `make check` — 207 Python / 36 frontend; `make e2e` — 223 passed / 3 existing skips.
- 4A.1–4A.5: `make check` — 212 Python / 36 frontend; build succeeds; `make e2e` — 223 passed / 3 existing skips in one complete 15.7-minute invocation.
- 4A.6: checks/build pass; 223 browser tests pass / 3 existing skips in one complete 15.6-minute invocation.
- 4B: `make check` — 212 Python / 36 frontend / 56 contrast checks; build succeeds; `make e2e` — 247 passed / 3 existing skips in one complete 19.7-minute invocation. Also 36 affected-flow repetitions and 48 motion repetitions passed.
- API, prompt, ordinary-request and synthetic migration guards pass. The 4B motion guard is now enforcing and passes: dead utilities, `transition-all`, invalid keyframe properties and static `will-change` are prohibited.
- Deployment: `scripts/deploy.sh --apply` succeeds; local health and the existing HTTPS route return 200, production `/design` returns 404, and installed static assets match this build. The label, 127.0.0.1 bind and port 8787 are preserved (`4b/deployment-verification.json`). System curl validated the HTTPS certificate; standalone Python lacks the local issuer certificates.

## Budgets

| Build | Initial JS gzip | Limit |
|---|---:|---:|
| Original HEAD | 224,491 bytes | 256,000 |
| 4A.1–4A.5 | 222,902 bytes | Original ± 2 KiB |
| 4A.6 split | 225,186 bytes | Original ± 2 KiB |
| 4B foundation | 226,220 bytes | 4A + 8 KiB; global 256,000 |

The `frame-summary-*.json` and `ttft-overhead.json` copies in the baseline/4A folders are Phase 3 reference data, not fresh checkpoint measurements (`artifacts/phase-4/performance-provenance.json`). Each complete run does re-execute the unchanged frame/first-token gates and emits fresh `performance-*.json`; 4B/final archives fresh raw browser frames and first-token captures and derives its frame summaries from those arrays.

Resolved dependency versions and integrity values are unchanged. Caret ranges constrain future updates; the lockfile and `npm ci` reproduce this build.

Fresh browser performance at 4B (synthetic fake runtime, 300 history messages, 100 tokens/s):

| Metric | Chromium | WebKit | Gate |
|---|---:|---:|---|
| Streaming-row React render p95 | 1.4 ms | 2 ms | ≤8 ms; only one row rerenders |
| 300-message scroll median | 16.7 ms | 17 ms | <20 ms |
| Scroll p95, reported | 16.8 ms | 18 ms | Informational |
| Fake-runtime first token to browser render | 80.50 ms | 75.28 ms | <150 ms |

Raw rAF intervals and derived summaries are separate from React render duration; their median alone does not establish uninterrupted 60 fps. Sources are the final full-run browser captures in `4b/` and `final/`.

## Screenshots

`artifacts/phase-4/baseline/*-fake.png` and `artifacts/phase-4/4a-components/*-fake.png`: 390/1440, light/dark, synthetic chat, web, reasoning, model picker, settings, palette, sources, sidebar and transcript states. Captures were inspected as contact sheets; all content is synthetic.

`artifacts/phase-4/final/*-fake.png`: 50 settled 4B screenshots of the same production states at 390/1440 in light/dark, including recording and transcript states. Both contact sheets were inspected; all API responses and content are synthetic. No live phone screenshot was captured.

## Motion recordings

Four isolated synthetic clips for the 4B scope were captured and their frame sheets reviewed. They remain local and ignored by Git:

- `artifacts/phase-4/motion/settings-desktop-fake.webm`
- `artifacts/phase-4/motion/model-picker-phone-fake.webm`
- `artifacts/phase-4/motion/sidebar-phone-fake.webm`
- `artifacts/phase-4/motion/overlays-reduced-phone-fake.webm`

The conversation clips were completed at 4C and are recorded below. The clips demonstrate timing; the phone review determines feel.

## Migrations, rollback and evals

No migration; rollback rehearsal is not applicable. The generated Phase 3 fixture preserves hashes projected onto existing columns. No server search/run/provider or model-facing prompt change, so no new web eval is required. Existing web checks remain part of the full regression run.

## Known limitations carried forward

VoiceOver was reported not working and deferred by Jake; it has not passed. The 3 October iOS keyboard issue recovered after a phone restart; its cause remains unproven. Three pre-existing browser skips remain documented in the Phase 3 evidence.

## Review history

At the 4B stop, the full QA phone walkthrough had not been checked. Jake then requested Codex verification and continuation to 4C, together with the chat export correction. Codex observations and remaining physical-phone limitations are recorded in the 4C section. The next required phase stop is 4D.

## QA gates at the 4B review stop

| Gate | Status | Evidence |
|---|---|---|
| G-1 Checks and coverage | Pass | `4b/check.txt`: 212 Python, 36 frontend, 56 contrast; coverage gate ≥80% |
| G-2 One complete Chromium/WebKit run | Pass | `4b/e2e.txt`: 247 passed / 3 existing skips, one complete 19.7-minute invocation |
| G-3 No weakened tests | Pass | Ledger below; no removed assertions, raised thresholds or new skips |
| G-4 Performance | Pass | `4b/bundle.json`, `performance-*.json`, `frames-*.json`, `first-token-*.json`; thresholds unchanged |
| G-5 Accessibility | Automated checks pass | Complete browser run scans existing screens/states in both themes and widths after settlement; 56 contrast checks pass. VoiceOver remains unresolved and deferred |
| G-6 Additive API | Pass | `check_api_additive.py` in `4b/check.txt` |
| G-7 Existing database rows | Pass | `test_phase4_guards.py` synthetic Phase 3 projected-row hash check; no migration |
| G-8 Frozen prompts | Pass | `test_prompt_hashes.py` in `4b/check.txt` |
| G-9 Web eval | Not triggered | No changes under server search, runs or providers; existing web tests remain required |
| G-10 Runtime payload | Pass | Golden ordinary request and parameter tests in `4b/check.txt` |
| G-11 Privacy | Pass within audit scope | Isolated synthetic fixtures; all 50 final images reviewed; final `4b/privacy-audit.json` has no findings. Marker scanning does not prove absence of private content |
| G-12 Deployment invariants | Pass | Unit checks, `4b/deploy.txt`, `deployment-verification.json`; installed preview verified |
| G-13 Both reduced-motion triggers | Pass | Complete green run plus `motion-timing-tests.txt`: 48 repeated passes; page-local exit measurement retains the 400 ms budget |
| G-14 Production states on `/design` | Pass | `MotionPreview.tsx` uses production primitives, settings and chat/download dialogs; `final/*-fake.png` |
| G-15 Rollback rehearsal | Not applicable | No schema or data migration; deploy makes its normal SQLite backup |
| G-16 Jake's phone review | Not checked | Awaiting the 4B preview review; no phone pass claimed |

## Core unchanged

C1–C16 are gated by the same complete browser invocation and `make check`:

| Flow | Evidence |
|---|---|
| C1 Send/stream/stats | `chat.spec.ts` live chat |
| C2 Stop/partial answer | `chat.spec.ts`, `phase3-accessibility.spec.ts` |
| C3 Resume | `chat.spec.ts`, `web.spec.ts` late snapshot |
| C4 Long answer/timeout | `chat.spec.ts` real-time timeout gate |
| C5 Chat actions/branches | `actions.spec.ts` |
| C6 Model operations/context | `load-selection.spec.ts`, `ui-regressions.spec.ts` |
| C7 User-set parameters | `parameters.spec.ts`, `test_chat.py` |
| C8 Search/citations/retry | `web.spec.ts`; search/evidence/grading unit tests |
| C9 Recording/output/storage | `transcription.spec.ts`, `recording-download.spec.ts`, `audio-storage.spec.ts`; transcription unit tests |
| C10 Phone/keyboard/drawers | `mobile-layout.spec.ts`, `mobile-composer.spec.ts`; physical review pending |
| C11 Palette/shortcuts/PWA | `polish.spec.ts`, `pwa.spec.ts` |
| C12 Read-only legacy import | `test_legacy_import.py` |
| C13 Deployment | `test_deployment.py` |
| C14 Untrusted content | `foundation.spec.ts`, search SSRF tests |
| C15 Performance | `performance.spec.ts`, chat frame and first-token checks |
| C16 Accessibility | `foundation.spec.ts`, `review.spec.ts`, `phase3-accessibility.spec.ts`; VoiceOver remains unresolved |

## Test-diff ledger

| File | Change | Reason | Assertions preserved |
|---|---|---|---|
| web/tests/actions.spec.ts | Await finite animations before screenshots and axe | Stable evidence with motion | Yes; selectors, timeouts and budgets unchanged |
| web/tests/audio-storage.spec.ts | Await finite animations before screenshots and axe | Stable evidence with motion | Yes; selectors, timeouts and budgets unchanged |
| web/tests/chat.spec.ts | Await finite animations before screenshots and axe | Stable evidence with motion | Yes; selectors, timeouts and budgets unchanged |
| web/tests/foundation.spec.ts | Await finite animations before screenshots and axe | Stable evidence with motion | Yes; selectors, timeouts and budgets unchanged |
| web/tests/load-selection.spec.ts | Await finite animations before screenshots and axe | Stable evidence with motion | Yes; selectors, timeouts and budgets unchanged |
| web/tests/mobile-layout.spec.ts | Await finite animations before screenshots and axe | Stable evidence with motion | Yes; selectors, timeouts and budgets unchanged |
| web/tests/phase3-accessibility.spec.ts | Settle screenshots/axe; await new-chat heading and verify toggle focus in the walkthrough | Stable evidence and the reproduced baseline navigation race | Yes; selectors, timeouts and budgets unchanged |
| web/tests/polish.spec.ts | Settle overlay handoffs, screenshots and axe; add closure/focus assertions | Keyboard contexts must finish their presentation transitions | Yes; selectors, timeouts and budgets unchanged |
| web/tests/recording-download.spec.ts | Settle dialog opening, retry/Escape, target geometry, screenshots and axe | Measure final target size and exercise the settled overlay | Yes; selectors, timeouts and budgets unchanged |
| web/tests/review.spec.ts | Await finite animations before screenshots and axe | Stable evidence with motion | Yes; selectors, timeouts and budgets unchanged |
| web/tests/transcription.spec.ts | Await finite animations before screenshots and axe | Stable evidence with motion | Yes; selectors, timeouts and budgets unchanged |
| web/tests/ui-regressions.spec.ts | Await finite animations before screenshots and axe | Stable evidence with motion | Yes; selectors, timeouts and budgets unchanged |
| web/tests/web.spec.ts | Await finite animations before screenshots and axe | Stable evidence with motion | Yes; selectors, timeouts and budgets unchanged |

Keyboard walkthrough also waits for the new-chat heading and finite motion, then adds a focused-toggle assertion before Enter. Original HEAD reproduced the same failure in 1 of 3 Chromium repetitions (`4a-components/keyboard-original-head.txt`); synchronized current code passed all 6 Chromium/WebKit repetitions (`keyboard-settled.txt`). No existing assertion, timeout, selector, or budget was removed or weakened.

The intermediate second full run was interrupted during review before applying the picker correction: retain the original cached-model rendering condition when a runtime becomes offline. No test assertion or timeout changed for this correction. `4a-components/e2e-final.txt` is the required final complete invocation.

4B's first complete run had 14 failures: twelve recording-save geometry checks ran during entrance scaling (the measured target was just below 44 px), one recording Escape overlapped closing layers, and one palette handoff overlapped exiting/entering overlays. `recording-download.spec.ts` now settles before returning the open download, before Escape after retry, and before geometry measurement. `polish.spec.ts` settles at picker/Settings handoffs and additionally asserts Settings detaches and the reopened palette input is focused. Original target-size, visibility, cancellation, keyboard, accessibility, timeout and performance assertions remain intact. Evidence: `4b/e2e-first.txt`, `4b/palette-race-fake.json`; the final complete run is the acceptance gate. New motion detachment checks use the plan's 400 ms limit.

The second full 4B invocation passed 245 cases and failed two WebKit normal-overlay cases at the new test's 400 ms driver-poll deadline (`4b/e2e-second.txt`). The new motion test now records `data-state=closed` and DOM detachment with a page-local MutationObserver and asserts their elapsed time is ≤400 ms. Playwright transport/trace latency no longer counts as product exit time; no animation duration, product timing budget or existing test timeout was raised. The same measurement covers real chat/download dialog exits. `overlay-*-fake.json` records the measured lifetimes. All 48 repeated motion checks and the subsequent full suite passed.

## 4C checkpoint — validated and installed

Jake authorized live verification, the chat export correction and continuation to 4C on 4 October. Codex inspected the installed Workbench and iPhone Mirroring transiently. The model picker, chat settings/context presets, sidebar and Appearance opened and closed. This is Codex-observed interaction evidence, not Jake's acceptance of all QA §7 flows. No live screenshot or recording content was saved. Mirroring later showed another app in use, so further phone interaction was stopped.

The reported export problem was confirmed: the old chat export download closed the dialog and handed the file to iOS's native preview. The corrected chat flow shares `FileSaveDialog` with recording outputs: selected brand/check format, editable Markdown/JSON choices, title-based filename, Cancel/close and pre-prepared native file share. Cancellation never starts a fallback download. Unsupported sharing retains a separate-tab download and keeps the original dialog available. The correction was deployed before conversation motion; the installed desktop chooser, format switching and Cancel were inspected. The corrected native iPhone share sheet has not been physically rechecked.

4C adds session-only fresh rows, one-frame existing-chat send presentation with revision-safe rollback, waiting dots, lazy Streamdown word fades/caret, thinking/search Collapsible motion, local copy feedback, composer/chip/progress/ring motion, sidebar activity/title motion, successful-load-only status pulse, first-page empty-state entrances, native theme cross-fade, thread hairline/gradient and large-panel entrance. Internal identifiers, APIs, prompts, sampling and SSE/rAF handling are retained. 4D and display renames are not part of this checkpoint.

The final complete Chromium/WebKit invocation passed 289 tests with the same three existing skips in 22.9 minutes. Checks, build, performance, synthetic visual review and deployment verification passed. The required 4D review remains ahead.

### 4C implementation details and approved exceptions

- Existing-chat Send clears the submitted draft and shows an optimistic user bubble immediately. On rejection it removes that bubble and restores text only if the draft revision is unchanged; switching chats, typing a newer draft, or typing and clearing a newer draft prevents stale restoration. New chats keep confirmation timing. Confirmed optimistic replacements do not enter twice.
- The first full 4C invocation passed 281 cases, failed four, and retained the same three skips (`4c/e2e-first.txt`). Restricting confirmed cache seeding to existing chats passed all 24 focused repetitions (`regression-repetitions.txt`) but was insufficient in the full suite. The second attempt was stopped after a design update-toast settlement recurrence (`e2e-second-interrupted.txt`); diagnostics caught a 120 ms button background transition at 83 ms. Settlement now samples on browser frames and requires two clear frames within the same 1,000 ms deadline; eight repetitions passed (`settlement-repetitions.txt`). Diagnostics collect animation metadata only.
- The third attempt was stopped after the search/late-response and phone typing cases recurred (`e2e-third-interrupted.txt`). A deferred new-chat route could leave the old composer mounted after the URL changed, and could let a fast run finish before its chat query subscribed. The confirmed navigation now uses `flushSync`, with the installed React Router DOM provider; sent-file clearing accounts for the now-synchronous handoff. Confirmation timing, HTTP payloads and SSE/rAF handling are unchanged. New `handoff.spec.ts` cases populate 45 synthetic history chats, exercise a held stale GET and verify the next touch draft survives. All 20 coupled repetitions passed in Chromium/WebKit (`cold-regressions.txt`), with search activity at 101–111 ms. `cold-regressions-setup.txt` retains the new test's initial fixture URL error and the missing DOM-provider warning; both were corrected. Only the final complete suite counts as acceptance.
- Fresh IDs originate only from this session's send/edit/regenerate and expire on animation end or at 400 ms, including rows that are no longer mounted. Reloaded/history/branch rows have no fresh flag.
- Streaming word fades are on in the lazy Markdown chunk. Both reduced-motion triggers disable them and the caret blink. SSE and rAF batching are unchanged.
- Code Copy revealed an existing missing `pointer-events-auto` utility in Streamdown's floating controls; a scoped production CSS rule restores clicks without changing code presentation. Its native polite `Copied` output is retained, avoiding a duplicate announcement. The table's inner scrolling area is now focusable and named for keyboard access.
- The 240 ms sidebar width candidate measured p95 16.8 ms in Chromium and 25 ms in WebKit on 300 synthetic messages. Width therefore snaps; labels fade. No budget was raised. Candidate measurements are retained separately from the final streaming/scroll measurements.
- The shared save dialog performs a preparation GET when opened. This is an explicit user-requested exception to the earlier no-GET-on-Cancel check; cancellation still starts no download or native sharing. It retains current-branch export content and the dialog after returning from sharing or downloading. No API/schema change.

Preflight provenance: `export-tests.txt` retains the 35-pass/13-failure first run (selected-control autofocus fixed Escape; browser download tests selected the fallback path). `export-tests-fixed.txt` passed all 48 cases. `conversation-preflight.txt` retains the 18-pass/10-failure first motion run (ambiguous Sources selector and incorrectly seeded switch-chat fixture). `conversation-preflight-fixed.txt` retains 31 passes/15 failures while new cases were developed: empty chats were excluded from history, a title selector was wrong, the design route does not hydrate server appearance preferences, modal aria-hidden hid the trigger from role queries, table scroll focus was missing, and code controls were not clickable. `conversation-preflight-second.txt` passed 32 cases with two remaining new copy-test failures (duplicate polite outputs and a long nested design fixture); those were corrected without removing existing tests/assertions. `conversation-extra-tests.txt` passed all six additional copy/new-chat/edit/regenerate/theme checks. The acceptance gate remains the final complete invocation.

### 4C current evidence

Changed files: web app/chat components (`FileSaveDialog`, export wrapper, `LiveAppShell`, `LiveThread`, `Composer`, `Markdown`, picker, sidebar/history, panels, theme and empty state); presentation-only `fresh` store and copy-feedback hook; `motion.css`, `globals.css`, `prose.css`; production conversation previews on `/design`; `main.tsx` uses the installed React Router DOM provider for synchronous navigation. Tests: new `conversation-motion.spec.ts` and populated-history `handoff.spec.ts`, approved export and Collapsible selector updates, and browser-frame settlement in `helpers.ts` (ledger preserved). Scripts: synthetic capture selector update and `record_phase4_conversation.cjs`, which refuses to capture a non-fake backend. Docs: authorization, this report and the ledger. No server application, prompt, database, package or lockfile change.

- `4c/check.txt`: one green `make check` invocation — 212 Python, 36 frontend unit tests, 56 contrast pairs; providers/runs/search/transcribe coverage 85.8/89.2/88.9/90.7%. API-type/additive, prompt, database-row, request-payload, motion and privacy guards pass.
- `4c/build.txt`, `bundle.json`: 228,270 initial JS bytes gzip. Baseline 4A split 225,186; increase 3,084 bytes, below 8,192. No dependency/lockfile or `server/app` source change.
- `4c/screens/`: 50 synthetic production-state captures at 390/1440 in light/dark. Both contact sheets were reviewed. `export-*-fake.png` and `axe-*-fake.json` add the new chat save formats and six conversation states; zero serious/critical findings in the development preflight.
- Five local ignored 4C clips were recorded and reviewed: `send-reasoning-phone-fake.webm`, `search-phone-fake.webm`, `copy-phone-fake.webm`, `theme-desktop-fake.webm`, `send-reduced-phone-fake.webm`. The final clips use actual isolated fake-runtime SSE for send/reasoning/search, production copy controls and theme changes; all five frame sheets were reviewed. `record_phase4_conversation.cjs` refuses production connections. They are not physical-phone evidence.

No migration or prompt/server pipeline change: G-7/G-8 guards pass, G-9 eval not triggered, and G-15 rollback rehearsal is not applicable. Deployment continues to create the normal database backup. Known limitations remain VoiceOver (failed/deferred) and the earlier iOS keyboard incident (recovered after restart, cause unproven).


### 4C final budgets and deployment

| Metric | Chromium | WebKit | Gate |
|---|---:|---:|---|
| Streaming-row React render p95 | 2.8 ms | 3.0 ms | ≤8 ms; only one streaming row rerenders |
| 300-message scroll median | 16.7 ms | 16 ms | <20 ms |
| Scroll p95 (reported) | 16.8 ms | 19 ms | Informational |
| Fake first token to browser render | 73.13 ms | 59.97 ms | <150 ms |
| Search activity visible | 121.9 ms | 108 ms | <300 ms |
| Populated-history cold handoff | 106.7 ms | 99 ms | <300 ms |

Initial JS gzip is 228,270 bytes (<256,000 and +3,084 versus 4A split). Raw animation-frame arrays and their summaries are separate from React render duration; median rAF intervals do not prove continuous 60 fps. Fresh captures are archived in `4c/`, with provenance in `performance-provenance.json`; older phase evidence was restored after archiving.

`4c/deploy.txt` and `deployment-verification.json`: installed static hashes match, local health and the unchanged Tailscale route return 200, production `/design` returns 404; launchd label, 127.0.0.1:8787 and one worker are unchanged. The deployed chooser was inspected live: JSON selection, switching to Markdown, corresponding filename and Cancel return work. No live file was shared or downloaded. The heading still names the initial export format when switching; a neutral “Export chat” heading is a 4D copy refinement. Native iPhone sharing remains physically unconfirmed.

### QA gates at 4C

| Gate | Status | Evidence |
|---|---|---|
| G-1 Checks/coverage | Pass | `4c/check.txt`: 212 Python / 36 frontend / 56 contrast, coverage above 80% |
| G-2 Complete browser run | Pass | `4c/e2e.txt`: 289 passed / 3 existing skips, one 22.9-minute invocation |
| G-3 Test integrity | Pass | `test-diff-ledger.md`; approved export behavior exception, unchanged budgets/timeouts/skips |
| G-4 Performance | Pass | Fresh `4c` bundle, render, scroll, first-token and activity captures; sidebar width fallback retained |
| G-5 Accessibility | Automated pass | Full scans/keyboard checks and contrast pass; VoiceOver failed/deferred, not claimed passed |
| G-6 Additive API | Pass | `4c/check.txt`, no server application changes |
| G-7 Existing rows | Pass | Projected synthetic Phase 3 row hashes, no migration |
| G-8 Frozen prompts | Pass | Prompt hash guard, no prompt change |
| G-9 Web eval | Not triggered | No server search/run/provider changes; existing full web tests pass |
| G-10 Payload | Pass | Golden request/parameter guards in `4c/check.txt` |
| G-11 Privacy | Pass within audit scope | `4c/privacy-audit.json`, reviewed synthetic screenshots and clips; marker scanning has stated limits |
| G-12 Deployment | Pass | `4c/deployment-verification.json`, original label/bind/port retained |
| G-13 Reduced motion | Pass | Both OS preference and Appearance Always; static indicators and no word/caret/theme animations |
| G-14 Production states | Pass | Production `ConversationMotionPreview` and existing fixtures; `4c/screens/` |
| G-15 Rollback | Not applicable | No migration; normal deployment database backup retained |
| G-16 Jake phone review | Not checked | Codex live inspection does not replace Jake's physical review; review due at 4D |

Core C1–C16 use the same evidence mapping above, now passing in the complete 4C invocation. Added `conversation-motion.spec.ts` covers immediate send and rejection/chat-switch/new-draft rollback, native-share cancellation, fresh flags, copy feedback, reduced motion and theme; `handoff.spec.ts` covers populated history, stale fetch and the next touch draft. Search visibility and all original functional gates remain unchanged.

### Service continuity

Workbench is a separate launchd service running installed code, with local Ollama and a subprocess transcription engine. Codex's weekly development limit does not stop it. The verified 4C deployment and Git checkpoint remain available while 4D is developed; no unverified 4D build will replace it. Future phases are not authorized at this checkpoint.


## 4D continuation — validated preview installed

At the start of 4D, Jake asked to continue the authorized phase plan near the Codex weekly limit. The verified 4C build remains the fallback, commit `9b48ce8`; Codex quota has no connection to its launchd runtime. Testing uses an isolated fake service with an EXIT trap that restores the installed server independently of the conversation. 4D source is not deployed until the complete gates pass.

Design-system audit follows the approved V/N review: existing colors, fonts and tokens retained; user bubble/actions, assistant footer/info, borderless/humanized activity and reading passages, single code/table surfaces, one sidebar search and desktop density, grouped/default controls, one focus outline, input-first palette, consistent selection, ghost model actions/manage footer/connection name, friendly error headings, centered editable title, destructive menu, theme metadata, skeletons, Search pill and dashed drop target. Display labels are Atelier, Chat controls and Web search; internal Workbench identifiers, numbered citations and all API/parameter/prompt semantics remain. New icon PNGs and currentColor SVG follow the approved concept; its 512 px render was shown to Jake before any 4D commit.

New production components `ChatTitle` and `OfflineNotice` are also rendered by `RefinementPreview` on `/design`; other revised components retain their existing production previews. Added tests cover defaults, theme-color, PWA identity/internal key, offline disclosure and inline rename/surfaces. Test-copy adjustments are listed individually in the ledger; the first affected run's exact-Send/footer selector failures are retained. The initial implementation was followed by the diagnostic attempts below and the final complete acceptance run. Its evidence and deployment are now recorded at the end of this report; no physical-phone result is claimed.

4D first complete-run attempt was interrupted after two dark-theme axe failures (15 passed, 2 failed, 1 interrupted, 284 not run). Both found the history shortcut hint against shadcn’s inherited translucent dark input fill, 4.41:1 instead of 4.5:1. Production now explicitly applies the planned surface-2 fill to the history field; no token was changed. The contrast guard additionally covers brand text on brand-soft selection. `e2e-first-interrupted.txt` preserves the attempt; a fresh complete green run is required.

The next run was stopped during synthetic visual review before acceptance: the code Copy control crossed the header edge. Its existing Streamdown wrapper is now anchored inside the header with ghost presentation. The source-stack order/time spacing and title/model width constraint were also finalized before freezing the source. `e2e-visual-review-interrupted.txt` is not acceptance evidence. A new complete run follows.

A brief startup run was also stopped when the final title constraint moved the header action icons inward. The model region now preserves the auto spacer, keeping actions at the right edge. `e2e-title-layout-interrupted.txt` is retained; final source hashes will verify no product edits during the acceptance run.


### 4D visual evidence index

Before captures are the Phase 3 commit `66a8c6b` or Phase 4's pixel-identical baseline; after captures are the frozen 4D production source. All use the committed synthetic fixture, with network routes intercepted. For rows below, `baseline/<screen>-1440-light-fake.png` compares with `4d/screens/<screen>-1440-light-fake.png`, with matching dark/390 captures alongside. Supplemental before/after states are under `4d/before-details/` and `4d/details/` respectively. These are browser fixtures, not physical-phone evidence.

| Finding | Before → after screen | Closure |
|---|---|---|
| V1 | active-chat; `/design` production-state tests | Five fixture-only implementations were removed at 4A; LiveThread and revised production components are used in the previews |
| V2 | active-chat | User actions follow the bubble at the right, hover/focus on fine pointers and always on touch |
| V3 | active-chat | Borderless user-bubble token, radius-lg, 15/23, padding 10/14, max 85% |
| V4 | reasoning-chat; supplemental surfaces | One assistant footer, actions left/stats right, correct reveal rules; formatted Message info |
| V5 | web-chat | Borderless favicon-first summary with humanized expanded steps |
| V6 | supplemental surfaces | One code surface with Copy inside the header; one scrolling table surface |
| V7 | new-chat | One quiet filtering search field; collapsed palette icon retained |
| V8 | active-chat | Fine-pointer history density 36 px; touch targets retain 44 px |
| V9 | web-chat and sources | Reviewed proposal superseded by Jake's numbered-citation preference; compact numbers/+N retained, passages use Newsreader |
| V10 | chat-settings | Model defaults replace empty disabled fields; System prompt/Sampling/Length and context/Reasoning grouping |
| V11 | model-picker | One brand focus outline; inherited shadcn ring utilities removed |
| V12 | command-palette | Input first, accessible hidden title/description, touch-only close and shortcut hints |
| V13 | settings-appearance | One brand-soft/brand segmented selection style |
| V14 | model-picker | Ghost Load/Eject, Manage models footer, actual connection name |
| V15 | supplemental offline | Human guidance and retry, technical failure behind Details; generic toast title uses errorCopy |
| V16 | settings-appearance | Approved warm overlay/shadow/radii applied at 4B and retained |
| V17 | active-chat | Centered desktop title, inline rename and scrolled hairline; hidden on phones |
| V18 | supplemental chat-menu | Delete in danger color after separator |
| V19 | settings-appearance | Both theme-color meta tags track the resolved app theme, verified in refinement tests |
| V20 | before-icon-512-fake.png → icon-512-fake.png | Cobalt easel A replaces bars; five icon files, central 80% maskable safe area; render shown before commit |
| V21 | supplemental history-loading | Production skeleton rows replace loading prose; lazy Markdown fallback also uses a skeleton |
| V22 | new-chat | Labeled Search pill on desktop, stable Web search accessible name/pressed state |
| V23 | supplemental drop-target | Dashed brand outline on translucent background |

The title width is capped against the model label while preserving the right action spacer. The final source freeze occurs after this visual correction. No keyframe, animation duration, color token, API or stored setting semantics changed during that review.


### 4D scope and limitations

No database migration or dependency was added. No server application, endpoint, prompt, runtime adapter, search pipeline, transcription engine or caching rule changed. Web eval is not triggered by these display-only changes; frozen prompt, additive API, row-hash and golden request guards remain mandatory. Approved C1 timing/rollback and persistent chat-export behavior were already validated at 4C and remain covered.

VoiceOver remains reported failed and deferred. The earlier phone keyboard incident recovered after an iPhone restart; its cause remains unproven. Browser WebKit evidence is not a physical iPhone test. The native iPhone save/share sheet for chat exports still needs physical review. Existing Home Screen installations may retain their old icon/label until iOS refreshes or Jake adds the updated app again; internal PWA identity and server data stay unchanged.

At 4D the report stops for Jake's phone review from QA §7. No Phase 5 feature, additional runtime, embedding model or sqlite-vec installation is authorized or included. App availability depends on the Mac, its local runtimes and Tailscale connectivity; Codex development quota is not a dependency of the running app.

The next frozen-source invocation was stopped after two stale test-label failures: recording protection still queried its former state-dependent accessible name, and the full Settings loop still queried Search. Only these selectors were updated to the approved Web search label; disabled state remains asserted, with the original reason and false pressed state now explicitly asserted too. No production source, assertion, timeout, skip or performance gate changed. `e2e-labels-interrupted.txt` records 134 passed, two failed, one interrupted and 165 not run; it is not acceptance evidence.

The subsequent complete diagnostic run passed 291 cases and retained three existing skips, with eight failures at the same old provider-copy selector in both browsers/four layouts. The displayed provider now shares one metadata line with timings as explicitly required by 4D. The assertion anchors the same provider followed by the separator/end; no timeout or other assertion changed. `e2e-source-selector-failed.txt` is diagnostic evidence, not acceptance. A focused citation check precedes the required complete final invocation.

The supplemental 390/light menu scan reported aria-hidden-focus on the header/composer. Two-frame settlement did not clear it, and the same synthetic menu scan reproduced two serious aria-hidden-focus nodes at Phase 3 commit `66a8c6b` (`before-details/axe-chat-menu-390-light-fake.json`). ChatMenu now uses Radix's nonmodal menu semantics, preserving menu keyboard navigation and return focus while keeping background controls in the accessibility tree. This is a scoped focus correction discovered by G-5, not a claim of repaired VoiceOver. New refinement cases scan 390/1440 and light/dark in both engines, verify Escape returns focus and verify the next draft remains editable. Original core/menu assertions remain.

The next complete run passed 306 cases with three existing skips and one WebKit failure in the recording setup: Escape did not close Add attachment. Its trace sends Escape about 10 ms after the menu becomes visible, before Radix's effect-based document listener is necessarily registered. Composer now controls this menu and closes it from its synchronous React key handler as well as normal Radix dismissal; this preserves first-frame interaction and leaves the existing test/assertions unchanged. `4d/e2e-attachment-escape-failed.txt` preserves the 23.1-minute diagnostic invocation; another complete green run is required. Screenshot fixtures also now explicitly include the required stop finish reason rather than rendering an undefined synthetic statistic; production stats/schema were not changed.


### 4D final acceptance

The complete final Chromium/WebKit invocation is the acceptance run; all earlier attempts remain diagnostic evidence. Production and test-file hashes were frozen for this invocation and verified unchanged afterward. No existing test was removed, no timeout or performance limit increased, and the three baseline skips remain. `test-diff-ledger.md` records every existing-file change, including stable Web search labels and explicit recording-protection assertions.

Changed files: `shared/config.json`, HTML/PWA display metadata and the five icons; production app/chat/settings components and primitives; `globals.css`, `prose.css`, small presentation rules in `motion.css`; `ChatTitle`, `OfflineNotice` and production `RefinementPreview`; new `refinement.spec.ts`, approved test label updates, synthetic capture scripts, contrast guard, README, this report and evidence. No `server/app`, package, lockfile, database, prompt or runtime-engine change.

Deviations: the approved citation-number preference supersedes V9's domain-label suggestion. AppShell/TopBar remain design frames as explicitly allowed by 4A.5; the five fixture-only content/control implementations are deleted. Sidebar width still snaps because the 4C candidate exceeded its p95 gate; labels fade. The scoped nonmodal ChatMenu focus correction is documented above; it fixes a baseline aria-hidden/focus mismatch without claiming VoiceOver repair.

Runtime observations: 4D automated measurements use the isolated fake runtime and synthetic transcription engine. No real inference/eval call was needed for this display-only checkpoint. Installed service health, build hashes and browser interactions are verified separately. No new runtime behavior is inferred from a model name.

### QA gates at 4D

| Gate | Status | Evidence |
|---|---|---|
| G-1 Checks and coverage | Pass | `4d/check.txt`: 212 Python, 36 frontend, 58 contrast pairs; coverage 85.8/89.2/88.9/90.7% |
| G-2 Complete browser run | Pass | `4d/e2e.txt`, one complete Chromium/WebKit invocation; counts below |
| G-3 Test integrity | Pass | `test-diff-ledger.md`; unchanged original budgets/timeouts/skips; approved label changes |
| G-4 Performance | Pass | Fresh `4d` bundle/render/scroll/first-token/activity captures, below unchanged gates |
| G-5 Accessibility | Automated pass | Full screen/state axe, contrast and keyboard gates; VoiceOver failed/deferred, not claimed passed |
| G-6 Additive API | Pass | `4d/check.txt`; no server application change |
| G-7 Existing rows | Pass | Synthetic Phase 3 projected-row hash guard; no migration |
| G-8 Frozen prompts | Pass | Prompt hash guard; no prompt changes |
| G-9 Web eval | Not triggered | No server search/run/provider change; full web/citation cases pass |
| G-10 Payload | Pass | Golden ordinary-chat payload and exact parameter guards |
| G-11 Privacy | Pass within audit scope | `4d/privacy-audit.json`, isolated synthetic fixtures and reviewed images/clips; scanner limits retained |
| G-12 Deployment | Pass | `4d/deploy.txt`, `deployment-verification.json`; backup first, original label/bind/port/worker/Tailscale route retained |
| G-13 Reduced motion | Pass | Full motion/conversation suite, OS and Appearance Always triggers |
| G-14 Production states | Pass | `RefinementPreview` and existing production fixtures, 50 review screens + 8 surface/passages + 20 supplementary after states |
| G-15 Rollback | Not applicable | No migration; deployment creates the normal database backup; validated 4C fallback is `9b48ce8` |
| G-16 Jake phone review | Not checked | Required 4D review stop; Codex browser observation and synthetic WebKit do not substitute for Jake's physical check |

### Core flow evidence at 4D

Every row refers to the same final complete `4d/e2e.txt` invocation, with server guards in the single green `4d/check.txt`.

| Core | Passing guard |
|---|---|
| C1 Send/stream/stats | chat.spec + conversation-motion.spec immediate presentation and rollback |
| C2 Stop/partial | chat.spec + phase3-accessibility.spec Escape-before-confirmation |
| C3 Reconnect/stale snapshot | chat.spec resume + web.spec late-snapshot + handoff.spec |
| C4 Long answer/idle | chat.spec real-time long/idle gate, unchanged thresholds |
| C5 Branch/actions/export | actions.spec branch contents, rename/pin/delete and cancellable format chooser |
| C6 Load/context | load-selection.spec + ui-regressions.spec |
| C7 Parameters | parameters.spec + golden server request captures |
| C8 Web/citations | web.spec + unchanged server search/evidence/grading tests |
| C9 Recordings | transcription.spec + recording-download.spec + audio-storage.spec + test_transcription.py |
| C10 Phone layout/keyboard | mobile-layout.spec + mobile-composer.spec |
| C11 Palette/PWA | polish.spec + pwa.spec |
| C12 Legacy import | test_legacy_import.py, read-only/idempotent |
| C13 Deployment | test_deployment.py + actual installed-service verification |
| C14 Untrusted content | foundation.spec + unchanged SSRF tests |
| C15 Performance | performance.spec + chat.spec frame/first-token gates |
| C16 Accessibility | foundation/review/phase3-accessibility/conversation/refinement scans + contrast |

### Phase 4 acceptance index

| Criterion | Evidence/status |
|---|---|
| P4-AC1 | 4A component/split complete green runs, locked resolution and 50 exact screenshot matches |
| P4-AC2–5 | Motion guard and full normal/reduced overlay/conversation tests; centralized bounded CSS |
| P4-AC6 | Final 4D bundle below 256,000 and within 8,192 of 4A split; no dependencies added |
| P4-AC7 | C1–C15 implementation and full motion/conversation/handoff cases |
| P4-AC8 | Streaming word fade stays enabled; final unchanged performance gates pass |
| P4-AC9 | Width snaps, using the documented 4C over-budget candidate fallback |
| P4-AC10 | V1–V23 before/after index above, with V9's approved numbered-citation correction |
| P4-AC11 | Production previews and five deleted lookalikes; permitted AppShell/TopBar design frames retained |
| P4-AC12 | Complete axe/keyboard run, 58 contrast pairs, all synthetic review screens settled |
| P4-AC13–14 | Actual deployment invariants, API/cache guards and no server application change |
| P4-AC15 | Pending Jake's physical 4D review; no physical pass invented |

Local ignored motion evidence is refreshed against the final 4D source: Settings, model picker, phone sidebar, reduced overlays, send/reasoning, search, copy, theme and reduced send (`artifacts/phase-4/motion/*-fake.webm`). Nine short clips cover the requested eight moments plus reduced overlays; the synthetic fixture and actual isolated fake SSE guards are retained. These clips are not physical iPhone evidence.

### Open review for Jake

The Phase 4D preview is installed for the QA §7 phone walkthrough: launch/typing, immediate send and streaming, Stop, model selection, citation dismissal, recording follow-up, history search, Settings/theme and Reduce motion Always. Also verify chat Markdown/JSON format switching, Cancel and return from native sharing. VoiceOver remains deferred. Phase 5 has not started.

### Final commands and budgets

- `make check`: 212 Python tests, 36 frontend unit tests, 58 contrast pairs; lint, types, API, row, prompt, payload, motion and privacy guards pass. Coverage remains providers 85.8%, runs 89.2%, search 88.9%, transcribe 90.7%.
- `make e2e`: **307 passed, 3 existing skips, 23.1 minutes**, one complete Chromium/WebKit invocation. Source and tests unchanged throughout (`4d/freeze-verification.json`). The unchanged recording/download suite additionally passed 54 repeated cases after the first-frame Escape correction.
- `make build` and `scripts/deploy.sh --apply`: pass. Database backup precedes deployment; health/Tailscale 200, `/design` 404, installed static hashes match, original label/bind/port/one-worker settings retained. Source checkpoint `0a8cf4b`; all earlier phase artifacts restored after archiving the final run’s fresh measurements.

| Budget | 4D result | Gate/comparison |
|---|---|---|
| Initial JS gzip | 229,606 bytes | ≤256,000; baseline 224,491, 4A split 225,186, previous 4C 228,270; +4,420 versus split and +1,336 versus 4C |
| Streaming render p95 at 100 tokens/s | Chromium 2.5 ms / WebKit 3 ms | ≤8 ms; only the streaming row renders |
| First-token overhead | Chromium 69.3 ms / WebKit 58.8 ms | ≤150 ms |
| Search activity visible | Chromium 119.9 ms / WebKit 100 ms | ≤300 ms |
| 300-message scroll interval p95 | Chromium 16.8 ms / WebKit 19 ms | Unchanged passing performance gate |
| Raw frame-interval p95 | Chromium 16.8 ms / WebKit 19 ms | rAF intervals, not React render durations or proof of continuous 60 fps |

Fresh raw arrays and metrics live in `4d/` and `final/`; `performance-provenance.json` distinguishes checkpoint measurements. The 78 after images were visually reviewed (`4d/visual-review.json`). Twenty supplemental scans have zero serious/critical findings (`supplemental-axe-summary.json`). Nine synthetic clips were refreshed at the final source and sampled for visual review (`video-review-metadata.json`); clips remain ignored by Git. The old baseline menu accessibility failure remains documented, not counted as a current pass.

### Codex live observation at 4D

Codex inspected the installed app through the unchanged Tailscale URL in the in-app browser. Atelier title/sidebar, Chat controls, Web search navigation and Appearance selections are present. JSON opens the neutral Export chat chooser with JSON selected; selecting Markdown changes its pressed state and filename extension; Cancel returns to the chat without downloading. Chat controls opens/closes and offers the configured 32K preset. The browser was left on the chat with dialogs closed. This is Codex observation, not Jake’s physical-iPhone acceptance; native sharing was not invoked. Inspected chat parameters/default-prompt state match the read-only pre-deploy backup. No live recording screenshot or transcript was persisted.

The installed service runs independently of Codex weekly usage. Validated 4C fallback `9b48ce8` and its separate-checkout deployment instructions remain in README. No migration, model installation, new runtime, dependency, prompt change or Phase 5 feature is included. **Stop for Jake’s 4D physical review before Phase 5.**

Source/docs whitespace checks pass. Captured console output is retained verbatim, including emitter blank-line spaces; the whole-diff whitespace check reports only those raw log lines.
