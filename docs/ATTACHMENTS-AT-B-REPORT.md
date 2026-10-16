# Attachments and composer: AT-B report

16 October 2026. Branch: `codex/attachments-redesign`. Draft PR: [#2](https://github.com/EviIius/agents-agenticrag/pull/2).

## Summary

AT-B implements Claude’s drop, paste and sent-message design on accepted AT-A (`3e3ae755`), based on main `55477ff1`. J-U2 is adopted: text pastes over 4,000 characters become text attachments with Keep as text. All AT-B acceptance checks pass for branch review. Main and the installed app remain unchanged. Publication and merge require Jake’s final review.

## Done-when checklist

| Item | Status | Evidence |
|---|---|---|
| AT-AC10 drop overlay / leave / Escape / route boundary | Pass | `attachments-thread.spec.ts`: real nested drag events, composer target, Settings and Workflows boundary; existing document drop |
| AT-AC11 screenshot and long paste with undo | Pass | Actual fake-app uploads, original text/character count, exact 4,000 boundary, in-flight cancellation, uploaded-file removal, selection restoration, ten-second expiry, preservation during earlier send/stream |
| AT-AC12 fixed sent photo grids and file cards | Pass | 1/2/3/7 photos, mixed cards; delayed portrait loads preserve photo and text-bubble geometry |
| AT-AC13 per-message viewer and existing sheets | Pass | Viewer reaches seventh photo; PDF, text and recording sheets use production controls |
| AT-AC14 optimistic-to-confirmed preview handoff | Pass | Held upload-copy and send responses prove same decoded local image remains until server image is ready; real request body and durable reload asserted |
| AT-AC15 axe, both themes and widths | Pass | 15 new states × Chromium/WebKit × 390/1440 × light/dark, plus existing AT-A/core checks |

## Changed files

- Web: `DropOverlay`, `MessageAttachments`, drop boundary in `LiveAppShell`, paste/undo in `Composer`, sent rows in `LiveThread`, preview lifetime in `useUploads`, character metadata in `AttachmentTile`, and token-based layout/motion.
- The unchanged issue classifier moved from `AttachmentTray` to `lib/attachment-issues.ts`, allowing lazy tray loading while keeping the sent attachment renderer eager for stable handoff.
- Design: `/design?attachment-thread` supplies normal, optimistic/history, loading/error, drop, paste, viewer and sheet states, all synthetic.
- Tests: two new browser suites and two approved selector/name changes in existing tests. No server, API, database, prompt, dependency, provider, sampling or model-default edit.

## Deviations and clarifications

- The frozen message API requires nonempty text. File-only Send remains unavailable; the paste note says “Add a message to send it.” No placeholder prompt is invented and no API change is introduced.
- One-photo boxes retain a fixed 240 px frame with `object-fit: contain`; portrait/landscape aspect is preserved without layout movement. Multiple photos follow the 160/112 px grid sizes. Recording cards retain their existing output/retry action menu.
- Keep as text restores the original selection if the draft is untouched; otherwise it inserts at the current caret, preserving newer typing. Its ten-second grace pauses while the composer is disabled. During an earlier reply, undo remains usable on the newer draft. Only that paste’s unsubmitted upload is removed.
- Tray code loads on first attachment use; the sent renderer stays in the initial bundle to avoid a loading flash. Existing modal sheets and the drop card remain lazy.

## Runtime observations

The 24 exact request comparisons ran at source `f2de7454`; the only subsequent source change is the native CSS cursor value (`zoom-in` → `pointer`). Request code and JavaScript are unchanged. Synthetic fake runtime and fixture uploads only. No actual LLM, native image or transcription inference was run. Screenshots contain only synthetic files. Native picker UI was not captured. Physical iPhone behavior is not claimed.

## Test output

`make check` passed: **673 Python tests, 121 frontend tests and 110 contrast pairs**, plus types, lint, formatting, coverage, API, privacy and motion guards. One complete `make e2e` invocation passed **699 tests / three existing skips / zero failures** across Chromium and WebKit (1.1 hours). Tested program source: `ff5f589ebfce4238acb09da089d4579c453af702`, with all 256 web source/test hashes verified afterward. No further program source change followed.

All 24 original-main/current raw request comparisons are byte-identical. All 120 new state scans have zero serious/critical axe findings. Logs, coverage, frozen source, exact payload captures, layout geometry and performance data are under `artifacts/attachments/at-b/`.

Earlier failures are retained, not counted as passing evidence. The first focused run was 22 pass / 10 fail: its new harness queried hidden modal backgrounds, reused a navigation-scoped handle, missed the mobile sidebar and tried a touch-hidden Next button. Their remedies retain real user controls and gate deadlines. The second focused run was 60 pass / two fail, both obsolete document-drop wording; the approved selector update passes in the 12-check remedy run and the final complete suite. Formatting/type errors in the new harness and the first prototype observer are also indexed in `retained-attempts.json`.

The first full static check passed Python/coverage/contrast/API checks, then the unchanged motion guard rejected CSS cursor `zoom-in` as a dead utility. The cursor is now `pointer`; no guard was weakened. Its concurrent browser attempt was stopped after 11 passes, one interruption and 690 unrun cases. That attempt is not qualified. Raw logs, source snapshots and videos/traces remain private in the indexed QA directory.

The three unchanged WebKit skips are the real-time timeout gate (executed in Chromium), duplicate review screenshot capture, and offline reload (Playwright WebKit limitation). Their source and deadlines are unchanged. Successful final-run videos and 1,412 overwritten historical artifacts were preserved privately; tracked history was restored, and 40 newly generated historical-area files were moved privately. Prior AT-A evidence is unchanged.

## Screenshots

`artifacts/attachments/at-b/browser/` contains 120 final synthetic screenshots and eight axe reports: 15 states at both widths, both themes and both engines. `accessibility-summary.json` indexes them. Codex visually reviewed representative phone mixed attachments, desktop seven-photo grids, paste and drop layouts. Claude’s original prototype/spec/reference hashes match AT-A. This is browser observation, not Jake’s physical-phone verification.

## Gates

| Gate | Status | Evidence |
|---|---|---|
| G-1 checks / coverage | Pass | `check.txt`, `coverage.json` |
| G-2 one complete browser invocation | Pass | `e2e.txt` |
| G-3 existing tests preserved | Pass | `test-diff-ledger.md`; no skip, timeout or performance threshold changes |
| G-4 bundle and runtime budgets | Pass | `bundle.json`, `performance/summary.json` |
| G-5 axe / keyboard / contrast | Pass | New state scans plus complete existing suite |
| G-6 additive API | Unchanged | Frozen source and additive guard |
| G-7 additive database | Unchanged | No migration; existing row-preservation tests |
| G-8 prompts | Unchanged | Frozen source and hash guard |
| G-9 answer pipeline | Unchanged | Search/runs/providers unchanged; no new inference eval |
| G-10 exact requests | Pass | `payload-parity-fake.json`: raw original-main/current bodies; no normalization |
| G-11 privacy | Pass | Synthetic fixtures, privacy guard, unchanged original design source |
| G-12 deployment invariants | Unchanged | No publication/service/route change; existing deployment tests |
| G-13 reduced motion | Pass | Positive temporal drop animation check and both reduced-motion triggers |
| G-14 all new states on design | Pass | `/design?attachment-thread` plus AT-A `/design?attachments` |
| G-15 rollback rehearsal | Not applicable | No migration or deployment; branch isolated from main |
| G-16 Jake’s phone check | Not checked | Branch review required; no physical-phone pass claimed |

## Budgets

Initial JavaScript: **254,448 gzip bytes**, versus 254,207 at AT-A and 248,048 on original main. This is +241 bytes from AT-A and +6,400 from main, under both the 256,000-byte total and 8,192-byte increment limits. No added dependency. Final timings from the same complete browser run (unchanged limits):

| Measurement | Chromium | WebKit | Limit |
|---|---:|---:|---:|
| First-token UI delay | 70.5 ms | 59.8 ms | <150 ms |
| Streaming render p95 at 100 tokens/s | 3.3 ms | 3.0 ms | ≤8 ms |
| 300-message scroll frame p95 | 16.8 ms | 20.0 ms | Existing scroll test passes |

Only the streaming row renders during the measured stream. Raw frame traces, maxima and all samples are retained in the separate performance evidence.

## Open questions for Jake

Review Part B in the isolated preview. No implementation choice remains unresolved. Merge and publication wait for final approval.
