# Attachments and composer: AT-A report

Work started 15 October; review continued 16 October 2026.

## Summary

Reviewed Claude's full spec, prompts, prototype and all 29 reference images. The proposal is sound: it removes a redundant picker step, keeps uploads beside the draft, and reduces the phone toolbar to one row. AT-A implements §§2, 3 and 6 on `codex/attachments-redesign`, based on `55477ff1033938e7cc2b8560fad41ceeaa9f7a72`. J-U1, J-U3, J-U4 and J-U5 are adopted. AT-B and release await Jake's review.

AT-A is complete for branch review. One full browser invocation passed 677 tests with three existing skips and zero failures. The tested source is `be5a839cbba6c61b48c0523c6430ae03a65d855f`; draft PR: [#2](https://github.com/EviIius/agents-agenticrag/pull/2). No main merge, installed-app edit, publication, service restart, dependency, server/schema/prompt change or real model call is part of this checkpoint.

## Assessment of the supplied design

- The prototype and references give sufficient layout, motion and error-state detail to implement AT-A. Its fake uploads are replaced by the existing real upload/extraction/transcription pipeline.
- The native file input is the touch target at +. iOS decides its offered menu items; a WebKit touch-profile check proves the anchor/hit target, not the exact physical-device menu.
- Thinking levels come solely from runtime metadata. The app does not hard-code the prototype's example levels for other models.
- Photos use the existing viewer, with filename and navigation but without generated-image actions. Preview URLs survive the upload-to-server handoff and are released afterward. Actual-size zoom uses the longest image dimension, preserving square-image behavior and correcting portrait uploads.
- Retaining a photo on a text-only model is an intentional J-U3 behavior change: it stays in the tray and blocks Send until switched or removed. Upload errors are not attached and do not block an otherwise valid message. Failed/cancelled durable recordings retain their existing retry requirement.
- New drop visuals, long-paste conversion and sent-message grids are AT-B. The current paste/drop routes still use the same upload pipeline.

## Done-when checklist

| Item | Status | Evidence |
|---|---|---|
| AT-AC1 native picker target | Pass | `attachments-redesign.spec.ts` combined accept/hit test |
| AT-AC2 desktop picker/shortcut, feature-dependent audio accept | Pass | Browser chooser checks; `file-kinds.test.ts`; unavailable-engine check |
| AT-AC3 mixed classification | Pass | `file-kinds.test.ts` and actual format/document/recording browser tests |
| AT-AC4 immediate previews, URL lifecycle | Pass | Held-response upload and cancellation checks, including an already-open viewer |
| AT-AC5 progress and cancel | Pass | Real XHR/fake upload, abort and original-file retry checks |
| AT-AC6 inline problems | Pass | `/design?attachments`, actual unreadable/network/limit checks |
| AT-AC7 retained vision warning | Pass | Warning → runtime-reported vision selection → enabled Send |
| AT-AC8 waiting Send ring | Pass | Held-response and transcription checks |
| AT-AC9 two rows, tools/chips, no exclusivity toast | Pass | 390 px tools test and retained Library answer integration |
| AT-AC16 keyboard/focus and Image entry | Pass | Tools Enter/Space/arrows/Escape/chips and image-mode regressions |

## Changed files

- Web: upload classification and lifecycle; attachment tray/tile; compact document/recording cards; Tools/chips; composer and exclusivity note; existing viewer/text sheet; design fixtures and motion/tokens.
- Tests: new classifier, upload, state, keyboard and motion checks; existing UI selectors updated for approved control relocation (ledger below).
- Docs: original Claude package, this report and scoped AGENTS amendment. No server or dependency files.

## Deviations and clarifications

No new feature scope. A real new pick reveals the tray immediately, including failures dropped while Image mode was active; completed-upload behavior remains, and restored recordings never trigger this transition. Independent image drafts are preserved. This closes an error-visibility regression caused by replacing toasts with tile errors. The 600 ms ready check uses a short entrance, a hold and a short exit, preserving the existing small-motion timing cap. Both reduced-motion triggers remove its motion. The transcription engine and extraction service continue to own final file details. Errors automatically clear after the eight-second grace period, paused during interaction/previews.

## Runtime observations

Only fake runtime/engine fixtures were used. No new actual model call or native transcription was executed. A synthetic native HTTP proxy in the upload test holds a real fake-app response; this avoids WebKit multipart replay corruption from Playwright `route.fetch`. Its Origin/Referer are fixed to the fake application's own origin. Product CSRF checks are unchanged.

## Test output

`make check` passed: 673 Python tests, 121 frontend tests and 110 contrast pairs, including types/lint/API/prompt/privacy/motion guards. One complete `make e2e` invocation passed: **677 passed / 3 existing skips / 0 failed** across Chromium and WebKit (1.1 hours), using the exact source hashes in `executed-web-source.json`. The final logs are `check.txt` and `e2e.txt`. Earlier attempts and their corrections are retained in the private QA directory and indexed in `retained-attempts.json`. They caught photo hit-area overlap, hidden-background focus, dark hover contrast, native-input overflow, exit-ghost accessibility, test multipart forwarding, moved status/action selectors, recording-menu exit preconditions and an unwired preparation spinner. A positive temporal check now measures spinner movement under normal motion and no movement under both reduced-motion triggers. The first full run was intentionally stopped after 27 passes to correct square-only photo zoom; it is not presented as a green full run. The first portrait assertion expected PNG although existing opaque-image normalization correctly returns JPEG; that expectation was corrected, with both browsers passing and the codec unchanged.

The first completed full invocation (664 pass / 13 fail / 3 existing skips) is **not qualified**. Its three causes and retained traces are indexed separately: an empty Tools menu in a legacy fixture, duplicate global Tools selectors while a picker exits, and geometry sampled before chip entrance ended. The remedy preserves all existing size/time thresholds, provides the fixture with a working Search control, disables truly empty menus, and scopes/settles real interactions. The final full run verifies those remedies in both engines. A later source review found the no-vision-model menu could lack a menuitem; its disabled-placeholder remedy passes axe in both engines and has its own design state. The intermediate run was stopped after 46 passes, with one interruption and 633 unrun; it is retained and not a passing full run.

The three unchanged WebKit skips are the real-time timeout gate (run once in Chromium), duplicate review screenshot capture (interaction checks still run in WebKit), and offline reload (Playwright WebKit navigation limitation; physical Safari review remains required). Their source files are unchanged from base main.

## Screenshots

Synthetic state screenshots and axe reports: `artifacts/attachments/at-a/browser/`: 26 states × eight engine/width/theme combinations, 208 state scans with zero serious/critical findings, plus Tools scans. There are 216 synthetic screenshots. `accessibility-summary.json` indexes the state coverage. Representative final Tools, warning, preparation/progress and ready screenshots were visually reviewed by Codex; this is not Jake’s physical-phone verification. Source reference images remain in `docs/next/attachments/reference/`. Videos and failed traces are private under `~/.local/share/workbench/qa/attachments-redesign-20261015/`; no native picker was captured.

## Gates

| Gate | Status | Evidence |
|---|---|---|
| G-1 check/coverage | Pass | `check.txt`: 673 Python, 121 frontend; required coverage gates pass |
| G-2 one complete browser run | Pass | `e2e.txt`: 677 pass / 3 existing skips / zero failures |
| G-3 approved UI test adaptations | Pass | Ledger below; no skip/timeout/performance changes |
| G-4 budgets | Pass | `bundle.json`, `performance/summary.json`; measurements below |
| G-5 axe/keyboard/contrast | Pass | New state scans plus full existing suite |
| G-6 additive API | No API edits | Full check/API additive guard |
| G-7 additive database | No database edits | Existing migration preservation tests |
| G-8 frozen prompts | No prompt edits | Hash guard; source comparison |
| G-9 frozen answer pipeline | No search/provider/run edits | Source comparison; no new inference evaluation required |
| G-10 request parity | Pass | 24 raw before/after comparisons: ordinary/web/Library/scoped Library × Auto/Off/On × Chromium/WebKit; `payload-parity-fake.json` |
| G-11 privacy | Pass | Synthetic fixtures only; check privacy guard; reference and evidence image review |
| G-12 deployment invariants | No deployment | Existing deployment/PWA tests; main/installed trees unchanged |
| G-13 reduced motion | Pass | Both triggers in old and new browser tests |
| G-14 every AT-A state on design | Pass | `/design?attachments` |
| G-15 rollback rehearsal | Not applicable | No migration or publication |
| G-16 Jake's phone check | Not checked | Branch review required before release; no physical-phone pass claimed |

## Test-diff ledger

Existing test edits are listed below. No test is deleted or skipped, and no timeout or performance threshold is raised. The approved UI changes replace obsolete menu/pill/toast assertions; all transport, content, budget and lifecycle assertions remain.

| File and tests | What changed | Why / behavior still asserted |
|---|---|---|
| `helpers.ts` | Composer-scoped real Tools, native-picker and recording-action helpers; settle finite menu exit before reopening | UI relocation; no forced click, handler invocation or mocked interaction |
| `chat-image-viewer.spec.ts` | Create image entry through Tools | Viewer navigation/actions/closing/focus unchanged |
| `chat-images.spec.ts` | Entry selector and enabled-state role | Same generation, draft, cancellation and payload assertions |
| `composer-workflows.spec.ts` | Entry menuitem and helper | Existing 44 px target, image submission and workflow behavior retained |
| `documents-design.spec.ts` | Axe scans Tools instead of removed app file menu; error-only fixtures assert empty Tools disabled | Native picker is outside DOM; no native picker capture. The normal fixture supplies a working Search toggle |
| `documents.spec.ts` | Combined picker; inline budget status/action and per-file remove labels | Exact new accept has its own test; original PDF/Word extraction, payload, editing, budget and errors retained |
| `image-uploads.spec.ts` | Tools entry; count active tiles rather than inert exit ghosts; unreadable photo now an error tile | Explicit §3.4 change, strengthened with zero POSTs and usable Send; all actual format/HEIC/paste/drop assertions retained |
| `library-answers.spec.ts` | Switch state uses menuitemcheckbox; scope chip with settled bounds; inline disabled reason and exclusivity note | Same retrieval/citations/history/disabled-off checks. Requested phone chip height is 36 px; + and Tools remain 44 px and all controls stay inside 320 px |
| `handoff.spec.ts` | Search entry through Tools | Same cold route/SSE/late snapshot correctness and timing assertions |
| `mobile-composer.spec.ts` | Tap actual native input and cancel chooser rather than opening/escaping old app menu | Typing and keyboard flow retained |
| `phase3-accessibility.spec.ts` | Keyboard through Tools to web checkbox | Ordinary keyboard/labels/stop behavior retained |
| `recording-download.spec.ts` | One combined native picker; no app menu | All cancellable format/save/share/download assertions retained |
| `review.spec.ts` | Read Search checkbox state in Tools | Same suggestion behavior and query state |
| `transcription.spec.ts` | Compact action menu and moved status/action selectors; conditional absence after budget resolved | Same actual upload/transcribe/cancel/retry/remove, output limits, runtime payloads and unavailable-engine behavior. Wait for prior finite menu exit before reopening, without changing deadlines |
| `ui-regressions.spec.ts` | Tools and reasoning radio items | Same explicit On/Off selection and model behavior |
| `web.spec.ts` | Web checkbox via Tools | All answer/citation/skip/failure/streaming assertions retained |


## Budgets

Previous initial JavaScript: 248,048 gzip bytes. Limit: 256,000 and no more than 8,192 added bytes. Current measurement: **254,207 gzip bytes**, an increase of **6,159** from 248,048; 1,793 bytes under the fixed limit and within the 8,192-byte increment cap. No added dependency.

Performance from the same complete run (unchanged limits):

| Measurement | Chromium | WebKit | Limit |
|---|---:|---:|---:|
| First-token UI overhead | 72.3 ms | 67.0 ms | <150 ms |
| Streaming render p95, 100 tokens/s | 3.1 ms | 3.0 ms | ≤8 ms |
| Rows rerendering during stream | 1 | 1 | Only active row |
| 300-message scroll median frame | 16.7 ms | 17.0 ms | <20 ms |

The current run’s performance and coverage are retained under this checkpoint. 1,347 tracked historical artifacts were restored after preserving this run privately; 40 new files produced in old phase directories were moved to that private archive. See `historical-artifact-preservation.json`. Earlier reports and native trial evidence are unchanged.

## Core unchanged

The final full browser run and full check pass all applicable original core assertions, with the approved UI relocation adapters described above. No new skip, raised timeout or relaxed performance threshold is introduced.

| Core | Browser/server guard |
|---|---|
| C1 send/stream/stats | `chat.spec.ts`, `handoff.spec.ts` |
| C2 stop/partial text | `chat.spec.ts`, `phase3-accessibility.spec.ts` |
| C3 resume/late snapshots | `chat.spec.ts`, `web.spec.ts` |
| C4 long/idle answer behavior | `chat.spec.ts` |
| C5 branches/history/export/delete | `actions.spec.ts` |
| C6 model operations/context | `load-selection.spec.ts`, `ui-regressions.spec.ts` |
| C7 only explicit parameters | `parameters.spec.ts`, golden tool-body comparison, server captures |
| C8 web/citations/skip/failure/retry | `web.spec.ts` and unchanged search server tests |
| C9 recording/output/storage | `transcription.spec.ts`, `recording-download.spec.ts`, `audio-storage.spec.ts`, cleanup/server tests |
| C10 phone/keyboard/drawers | `mobile-layout.spec.ts`, `mobile-composer.spec.ts` |
| C11 commands/PWA/cache | `polish.spec.ts`, `pwa.spec.ts` |
| C12 legacy read-only import | Server legacy-import tests |
| C13 fixed deployment identity | Server deployment tests |
| C14 untrusted content | `foundation.spec.ts` and server SSRF tests |
| C15 fixed performance thresholds | `performance.spec.ts`, `chat.spec.ts` |
| C16 ordinary a11y | New attachment scans plus `foundation.spec.ts`, `review.spec.ts`, `phase3-accessibility.spec.ts` |

VoiceOver remains excluded with its historical failure unresolved; ordinary keyboard/focus/labels remain in scope.

## Migrations and rollback

None. Installed code, data, launchd service and Tailscale route are untouched. Base main remains `55477ff1`. The source-only branch can be discarded without a data rollback.

## Evals

No inference evaluation: server prompts, providers, runs, search and Library source are unchanged. Parameter presence/values are preserved and checked by browser captures and existing fake-runtime parameter tests.

## Known limitations carried forward

- Physical iPhone native picker and final feel require Jake's review; WebKit emulation is not a physical-device pass.
- Historical iOS keyboard issue recovered after restart, cause unproven. Historical VoiceOver failure is not a pass.
- Research stays shelved and factual-answer qualification remains unchanged.
- AT-B (new drop card, long paste, sent grids/optimistic attachments) is not implemented in AT-A.

## Open questions for Jake

Review AT-A's tray and composer before AT-B. No release or merge is requested at this checkpoint.
