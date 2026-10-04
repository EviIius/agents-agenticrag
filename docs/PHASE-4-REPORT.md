# Phase 4 report — 4A/4B review checkpoint

## Summary

4A is validated: contract, data, prompt and motion guards; locked dependency resolution; production components on `/design`; a shared engine-reported audio extension list; removal of duplicate fixtures and the tracked `.DS_Store`.
Production presentation is unchanged: all 50 synthetic screenshots match the original build pixel for pixel.
The app-shell split (4A.6) passed its separate full regression run. 4B adds first-party CSS motion to production overlays and controls, with both reduced-motion triggers. Its final complete browser invocation passed 247 tests with 3 existing skips.
The 4B preview is deployed and verified on the existing Tailscale route. Physical phone review is pending at this checkpoint. Phase 4 is not complete; 4C/4D and the Atelier rename have not started.

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
| Phone review | Not checked | Required at the 4B stop |

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

The remaining full-phase clips (send/stream/reasoning, web search, copy and theme switch) belong to 4C/4D and are pending. The clips demonstrate timing; the phone review determines feel.

## Migrations, rollback and evals

No migration; rollback rehearsal is not applicable. The generated Phase 3 fixture preserves hashes projected onto existing columns. No server search/run/provider or model-facing prompt change, so no new web eval is required. Existing web checks remain part of the full regression run.

## Known limitations carried forward

VoiceOver was reported not working and deferred by Jake; it has not passed. The 3 October iOS keyboard issue recovered after a phone restart; its cause remains unproven. Three pre-existing browser skips remain documented in the Phase 3 evidence.

## Open questions for Jake

Phone review after the 4B preview is deployed: open/close Settings, model picker and sidebar; send/stop, switch models, citations, recording outputs and keyboard; set Reduce motion to Always and restore it. 4C/4D remain pending until this review.

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
