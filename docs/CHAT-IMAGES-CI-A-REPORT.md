# Chat images CI-A report

## Summary

The waiting dots become Claude's Atelier mark and status line. Real queue/loading/
search phases win over a seeded 36-word sequence. Reasoning starts as a closed,
literal tail ticker; expansion retains the original text and respects manual
scrolling. Source is frozen at `76957979` on `codex/workflow-studio`.
One complete final invocation passes 573 browser cases with three existing
skips in 56.6 minutes. Native workflow testing is prepared for later; no native
trial, main merge or publication occurred.

## Done-when checklist

| Item | Status | Evidence |
| --- | --- | --- |
| CI-AC1: real stages before playful text | Passed | `working-indicator.spec.ts` controlled existing SSE/rAF path; pure phase tests |
| CI-AC2: stable seeded 36 words, 2.4 s, Plain | Passed | `status-words.test.ts`, browser fake clock/reload |
| CI-AC3: literal bounded ticker, expand/follow, close into Thought row | Passed | Browser geometry/manual-scroll and raw SSE text tests |
| CI-AC4: announcements only on phase changes | Passed | Cosmetic word/ticker hidden, stable phase status text checked |
| CI-AC5: performance | Passed | Original unchanged performance suite; added 100-delta/s ticker profiler |
| CI-AC6: both reduced-motion triggers | Passed | Static fully drawn mark, text still updates |

## Changed files

- Web: `WorkingLine`, `AtelierMark`, extracted `Thinking`, shared activity clock,
  pure seeded/status/tail helpers, LiveThread integration, Appearance control,
  browser-local preference and CSS motion. No SSE/client send pipeline change.
- Design/tests: production `/design?indicator` states, valid synthetic times,
  pure helper/clock tests, an additional original SSE batching test, browser
  timing/scroll/motion/accessibility/persistence and ticker performance cases.
- Docs: authorization, execution plan, this report and the later bounded native
  workflow trial proposal. Claude's supplied files remain byte-identical.
- Server/shared/packages/runtime: no source change.

## Deviations and implementation decisions

- A stream cannot predict a phase/token 400 ms in advance. Actual known phases
  replace cosmetic labels immediately; the app never delays a token.
- The server's existing preference whitelist rejects a new status-word key.
  CI-A remains web-only: Playful/Plain persists in browser storage. Existing
  Mac-synced preference payloads are unchanged; this one setting does not sync
  between devices yet. A future server checkpoint can add that key.
- The explicit B6 height collapse uses the existing allowed height property.
  Mark/word motion uses opacity, transform and stroke-dasharray. All motion is
  confined to the existing stylesheet and stopped by both reduced-motion triggers.
- During a live answer, the Thought duration uses the observed reasoning time
  until runtime stats arrive. Historical reasoning without duration says
  “Thought process”; it does not invent a zero-second duration.
- Reading counts derive from actual unique URLs. Failed read attempts finish the
  active count but never increase the “Read N pages” success count.
- The existing fake runtime emits its first reasoning and answer chunks nearly
  together. A new controlled synthetic EventSource test exercises their separated
  timing through the unchanged production listeners and rAF batching. All old
  actual fake-runtime interactions remain and run in the complete suite.

## Runtime observations

No native inference, model download, runtime/package change or Research run.
Read-only installed metadata confirms the existing daily 32K profile for the later
proposal. A report-path error from uv's directory change is retained; the repeated
metadata inspection succeeded. No physical phone or VoiceOver pass is claimed.

## Test output

`make check`: 646 Python tests / 101 frontend tests; all ten required coverage
areas exceed 80%; 110 contrast pairs; types, API, prompt/payload, privacy and
motion checks pass. One complete `make e2e` invocation: 573 passed, three existing
skips, zero failures in 56.6 minutes. Logs are under `artifacts/chat-images/ci-a/`.
Focused candidate: 101 frontend tests and 18 Chromium/WebKit browser passes.
The first focused browser run failed an entrance-animation geometry measurement
and a case-sensitive accessible-name lookup. Failures/traces are retained; the
measurement now settles, and the actual control text is explicitly capitalized.
A later CSS audit found that disabling animations also disabled the outgoing
word fade, causing a brief overlap. Its base opacity is now zero; a MutationObserver
assertion verifies the outgoing word stays hidden under both reduced-motion
triggers. The first complete-suite attempt was deliberately stopped (513 passed,
three existing skips, one interrupted, 59 not run, 49.1 minutes). Its source,
traces, logs and 989 generated outputs are retained. A new complete invocation
passes on the corrected frozen source. No existing assertion, timeout, threshold or
skip was relaxed.

## Gates

| Gate | Status and evidence |
| --- | --- |
| G-1 | Passed: `check-final-source.log`, 646 Python / 101 frontend, all coverage ≥80%, 110 contrast pairs |
| G-2 | Passed: one `e2e-final.log` invocation, 573 passed / three existing skips / zero failures, 56.6 minutes |
| G-3 | Passed: ledger below and `test-diff-ledger.json`; no removed assertion, raised timeout/threshold or added skip |
| G-4 | Passed: `bundle-final-source.json`, `performance-final.json`; initial JS 244,418 gzip bytes, +2,148 from WS-D; 300-row scroll and 100-delta/s ticker |
| G-5 | Passed automated checks: 112 new-state axe audits, zero serious/critical, both themes/sizes/engines; existing keyboard suites green. No physical VoiceOver claim |
| G-6 | Passed additive API guard; all server/shared source is unchanged |
| G-7 | Passed existing populated-fixture row-preservation tests; no new migration |
| G-8 | Passed frozen-prompt guards; no prompt change |
| G-9 | Not triggered: search/runs/providers source unchanged, verified with baseline hashes |
| G-10 | Passed original golden payload/parameter guards; `useSend.ts` and provider/run source unchanged |
| G-11 | Passed: `privacy-final.json`; synthetic captures only and all videos outside Git |
| G-12 | Passed original deployment/PWA tests; 97 installed server / 410 static hashes unchanged; local and verified HTTPS health; production `/design` 404 |
| G-13 | Passed both reduced-motion triggers, original motion suite and new outgoing-word opacity assertion |
| G-14 | Passed: production `/design?indicator`, 14 states; `browser/` captures and `axe-final.json` |
| G-15 | Not applicable: no migration/publication; WS-D's prior rehearsal retained |
| G-16 | Not checked on a physical iPhone. VoiceOver excluded per Jake's amendment; no invented result |

## Test-diff ledger

| Existing file/test | Change | Why | Existing behavior still asserted? |
| --- | --- | --- | --- |
| `web/src/lib/sse.test.ts` | Added one independent raw-reasoning/rAF batching test | Protect literal ticker input and answer transition | Yes; all original tests unchanged |
| `ProductionFixtures.tsx` | Active synthetic messages use current ISO time | Presentation elapsed clock cannot use a days-old fixture date | Yes; existing states/statuses unchanged |
| `ConversationMotionPreview.tsx` | Pending synthetic send gets current ISO time | Same elapsed-clock precondition | Yes; original C1 interaction/assertions unchanged |

## Budgets

| Measure | WS-D | CI-A |
| --- | --- | --- |
| Initial JS gzip | 242,270 bytes | 244,418 bytes (+2,148; budget 256,000) |
| Ordinary 100 tok/s render p95, Chromium / WebKit | 3.4 / 3 ms | 2.6 / 3 ms |
| First-token overhead, Chromium / WebKit | 80.73 / 64.60 ms | 77.79 / 61.39 ms |
| Ticker at 100 synthetic deltas/s p95 | Not present | 0.5 / 1 ms, one active row |

## Core unchanged

| Core | Passing evidence in the single complete browser / Python run |
| --- | --- |
| C1: send/stream/stats | `chat.spec.ts` live chat and frame/first-token tests |
| C2: Stop | `chat.spec.ts`, `phase3-accessibility.spec.ts` |
| C3: reconnect | `chat.spec.ts`, `web.spec.ts` late snapshot guards |
| C4: long answer/idle | `chat.spec.ts` beyond-90-second and idle preservation |
| C5: actions/branches/export | `actions.spec.ts`, `review.spec.ts`, `conversation-motion.spec.ts` |
| C6: model/context | `load-selection.spec.ts`, `ui-regressions.spec.ts` |
| C7: user parameters | `parameters.spec.ts`, Python payload/default tests |
| C8: Search/citations | `web.spec.ts`, original Python search/grading tests |
| C9: transcription/storage | `transcription.spec.ts`, `recording-download.spec.ts`, `audio-storage.spec.ts` |
| C10: phone/layout/keyboard | `mobile-layout.spec.ts`, `mobile-composer.spec.ts`, `handoff.spec.ts` |
| C11: palette/PWA | `polish.spec.ts`, `pwa.spec.ts` |
| C12: read-only import | Python legacy import guards |
| C13: deployment identity | Python deployment guards and installed preservation hashes |
| C14: untrusted input | `foundation.spec.ts`, `evidence-rendering.spec.ts`, original SSRF guards |
| C15: performance | `performance.spec.ts`, `chat.spec.ts`, new ticker profiler |
| C16: automated accessibility | `foundation.spec.ts`, `review.spec.ts`, keyboard suite, 112 new-state axe audits; physical VoiceOver excluded |

## Migrations and rollback

None. Schema 012 and existing additive/preserved-row tests remain unchanged.
Main and installed source/static/service/Tailscale are preserved. This branch is
still an isolated preview and has not been merged or published.

## Evals

None: no prompt, provider, retrieval, sampling, native call or factual-answer
construction changed. Existing frozen prompt/golden-payload checks are retained.

## Screenshots

Synthetic production state captures:
`artifacts/chat-images/ci-a/browser/<state>-<width>-<theme>-<engine>-fake.png`.
Waiting, Plain, queue, loading, Web/Library search, reading/unreadable pages,
collapsed/expanded thinking, answer, complete, stopped and error. Synthetic motion
recordings are kept outside Git; exact manifests accompany the checkpoint.
The final run retains 450 videos (66,612,764 bytes); with earlier available
attempts, 907 videos are preserved in total. Historical 30,764 evidence/eval/
fixture blobs, 15 workflow references, all 17 supplied chat-image files, 537
frozen source/test files and 335 unchanged core files verify intact. Fresh final
outputs: 1,202 retained separately, 1,162 original files restored, 40 new fake
captures moved into the checkpoint. The interrupted run retains 989 generated
outputs separately. Main stays at `dce4c49`.

## Known limitations carried forward

VoiceOver's reported historical failure is not a pass and remains outside the work
list. The earlier physical-phone keyboard failure recovered after restart; its
cause remains unproven. Browser WebKit evidence does not establish a physical
phone pass. Research and failed factual-grounding designs remain shelved.
Image chat turns/viewer are still CI-B/C work, not implemented by this checkpoint.

## Open questions / next checkpoint

Stop for CI-A review per the phase plan. Next: saved image turns, atomic/idempotent
job acceptance, both image roles excluded from text context, truthful progress
and existing saving/sharing (CI-B), then viewer/iteration (CI-C). After integration,
use `WORKFLOW-STUDIO-NATIVE-TRIAL-PLAN.md`: at most seven calls on the installed
daily profile to verify graph ordering, bindings, approval, cancellation and a
single-block test. That trial is prepared, not executed. Final main merge and live
publication still require Jake's okay.
