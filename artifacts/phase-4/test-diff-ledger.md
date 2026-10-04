# Test diff ledger

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

The second full 4B invocation passed 245 cases and failed two WebKit normal-overlay cases at the new test's 400 ms driver-poll deadline (`4b/e2e-second.txt`). The new motion test now records `data-state=closed` and DOM detachment with a page-local MutationObserver and asserts their elapsed time is ≤400 ms. Playwright transport/trace latency no longer counts as product exit time; no animation duration, product timing budget or existing test timeout was raised. The same measurement covers real chat/download dialog exits. `overlay-*-fake.json` records the measured lifetimes. All 48 repeated motion checks and the final complete 4B suite passed.

## 4C and the user-requested chat export correction

`helpers.ts` now samples finite animations on browser animation frames and requires two clear frames within the same 1,000 ms deadline. The sparse driver polling repeatedly caught a 120 ms button background transition near its end on the design-page update-toast case; the second full attempt was stopped after this recurrence and retained in `4c/e2e-second-interrupted.txt`. Failure diagnostics retain only animation names, properties, timings, tag names and data-slot values, never page text. No timeout or budget increased, no assertion or case was removed, and no skip was added. Browser-frame measurement removes transport/poll scheduling from settlement and strengthens its clear-state requirement.

| File and tests | Change | Reason | Behavior still asserted? |
|---|---|---|---|
| `actions.spec.ts`, branches and history actions | Cancel asserts no browser download rather than no GET; download keeps the dialog available, which is explicitly closed afterward. Ordinary download tests disable Web Share, with a separate native-share cancellation test in `conversation-motion.spec.ts`. | Jake explicitly requested the recording-style format chooser/save/share flow for chat Markdown/JSON exports. Opening prepares a file through the existing read-only endpoint; Cancel does not share/download. | Current-branch contents, omitted sibling branches, filenames, rename/pin/delete and browser downloads retained. Explicitly approved exceptions: preparation GET and persistent dialog after saving. |
| `web.spec.ts`, citation and activity tests | Replace details/summary selectors with production Radix collapsible trigger/data-state; exact Sources button name avoids matching the new summary button. | Phase 4C C6 replaces native details with Collapsible. | Citation passage/card, Sources contents, closure, axe and 300 ms visibility budget unchanged. |

`conversation-motion.spec.ts` adds new cases; no existing test, timeout, performance threshold or skip is removed or raised. Preflight failures are retained with their diagnostic output; only a subsequent single complete green run counts as the acceptance gate.

All additional short-lived flag checks record state on the page clock (MutationObserver), so transport latency cannot miss the 200 ms model pulse or fresh message entrance. New tests seed visible history entries before navigation, choose the named Actions trigger, scope the New chat link to the sidebar banner, and use the actual `/design` reduced-motion/theme buttons. These correct new fixture/selector setup without changing any pre-existing gate. A missing pointer-event override for code controls and keyboard focus for the table's inner scroll area were fixed in production components; the native code-copy polite output is retained once.

Final 4C acceptance: `4c/e2e.txt` passed 289 cases with the same 3 existing skips. New populated-history handoff cases exposed the deferred-route race; production now synchronously commits confirmed navigation using the installed Router DOM provider. No old assertion, timeout or budget changed.
