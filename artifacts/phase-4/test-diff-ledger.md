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

The second full 4B invocation passed 245 cases and failed two WebKit normal-overlay cases at the new test's 400 ms driver-poll deadline (`4b/e2e-second.txt`). The new motion test now records `data-state=closed` and DOM detachment with a page-local MutationObserver and asserts their elapsed time is ≤400 ms. Playwright transport/trace latency no longer counts as product exit time; no animation duration, product timing budget or existing test timeout was raised. The same measurement covers real chat/download dialog exits. `overlay-*-fake.json` records the measured lifetimes. Repeated motion checks and another complete suite are required before acceptance.
