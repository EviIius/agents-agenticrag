# Chat motion audit — 15 October 2026

## Summary

The installed application had `appearance.reduce_motion = always`. That saved
preference deliberately suppresses the mark loops, message entrances, streaming
word fades, image effects and workflow activity. Its origin was not established.
Restored **Follow system** through the existing settings API. Claude's chat/image
motion is already implemented; no new animation code or deployment was necessary
to resolve the reported static chat. Added temporal regression checks against
both the development components and the actual installed bundle.

## Done-when checklist

| Item | Status | Evidence |
|---|---|---|
| Inspect Claude's actual prototype and references | Pass | Opened both original prototypes in Chromium and WebKit; exercised chat send through drawing and thinking. Inspected the thinking reference and motion tables. Prototype stroke/dot values change across frames in both engines. |
| Restore the saved animation preference | Pass | Private before/after records: `always` → `system`. Local and verified Tailscale HTTPS settings and health checks pass. |
| Waiting mark keeps drawing | Pass | Installed Chromium: 100 distinct stroke values across 230 frames. WebKit: 99 across 229 frames. Both halves of each observation contain movement. |
| Thinking mark keeps moving | Pass | Installed Chromium: 146 distinct dot transforms. WebKit: 126. The reasoning ticker remains collapsed and retains its original text. |
| A sent message visibly enters | Pass | Installed Chromium and WebKit both record 13 distinct transforms; opacity rises from 0 / 0.396145 to 1. No inference occurs. |
| Words and reasoning transitions work | Pass | Word rotation is checked during the installed-bundle observation. Existing fake-stream tests verify real-stage priority, reasoning batching, collapse on answer and unchanged request settings. |
| Image reveal and viewer motion work | Pass | Existing lost-response/reveal/reload test and viewer opening/navigation/closing tests pass in both engines. |
| Workflow run activity and reduced motion work | Pass | Existing sweep activity test verifies normal, OS-reduced and Always modes in both engines. |
| Reduced motion still works | Pass | New frame-sampling tests see a static fully visible dot under each trigger; existing indicator/image/viewer/workflow checks also pass. |
| Regression checks | Pass | 36 focused browser checks and 10 installed-bundle checks; full `make check` results below. |

## Motion mapping

| Claude's intended effect | Existing implementation | Verification in this checkpoint |
|---|---|---|
| New user row enters once, 200 ms | `LiveThread.tsx`, `row-in` | Actual opacity and transform samples during send; existing no-replay test |
| A draws every 1.8 s while waiting | `AtelierMark.tsx`, `mark-draw`, `mark-dot-drop` | Repeated motion sampled in original prototype and installed app |
| Thinking dot bobs every 1.2 s | `mark-dot-bob` | Repeated transform samples, not just an animation-name assertion |
| Status words rotate every 2.4 s and slide/crossfade | `WorkingLine.tsx`, `word-in`, `word-out` | Installed word change plus existing controlled-clock checks |
| Live label shimmer | `activity-shimmer` | Source/bundle audit; existing reduced-motion tests |
| Reasoning ticker updates without text animation | `WorkingLine.tsx`, existing SSE/rAF | Actual fake reasoning stream, original text, fixed geometry |
| Status collapses when the answer starts | `line-collapse`, `Thinking.tsx` | Existing controlled and actual fake-stream checks |
| Answer words fade in and caret blinks | `Markdown.tsx`, lazy Streamdown CSS, `caret-blink` | Source audit and existing send/streaming test |
| Image develops, progresses and reveals | `ImageTurn` components, `image-drift-*`, `image-sheen`, `image-reveal` | Existing reveal/reload and both reduced-motion checks |
| Viewer opens from the card and closes back to it | `ImageViewer`, FLIP transforms, `image-viewer-swap` | Existing viewer geometry/navigation/focus test |
| Running workflow sweep, connection flow, paused ring, completion badge | `wf-sweep`, `wf-flow`, `breathe`, `wf-badge` | Source audit; existing normal/reduced sweep test |

The reasoning text itself has no slide animation in Claude's specification.
During Thinking the dot moves while the A outline stays drawn. History rows and
previously completed images intentionally do not replay their entrance effects.
This report covers the reported chat failure and the related chat/image and
workflow run effects; it is not a new acceptance claim for every fine-grained
workflow editing interaction in the wider Studio specification.

## Changed files

- Web tests: `web/tests/motion-playback.spec.ts` — API-isolated synthetic fixtures,
  repeated-cycle measurements, actual send opacity/transform measurements and
  both reduced-motion triggers. The same tests can target an installed build.
- Documentation: this report and the deferred motion issue's follow-up.
- Evidence: `artifacts/chat-motion-audit/verification.json` and four synthetic
  browser images.
- Installed data: only the existing reduced-motion preference was changed.
  Application source, service configuration and static assets were not replaced.

## Deviations from SPEC.md

The reported symptom was resolved through the existing preference rather than
adding duplicate effects. No dependency, prompt, sampling, runtime, model or
request-pipeline change was made. No general Research/grounding qualification
follows from this visual check.

## Runtime observations

The installed CSS already contains the required chat mark keyframes. Local and
verified HTTPS return identical `/assets/index-Bvu0bPDb.css`, SHA-256
`e51e2ea402f511f371a199e956b5eee2a71d7121a28582843b493a0f9748d1b0`.

The initial health observer assumed a `status` field after successfully changing
the preference. The endpoint uses `ok`; the corrected observer passes without
an application change. Both observations and the preference backup are private.

Installed-bundle tests intercept every API request with synthetic data, reject
their synthetic send after measuring its entrance, and reject unexpected writes.
They do not read real chat history or create live chats/model requests. The
other browser tests use the existing fake runtime. The user's screenshot is
excluded from evidence. These are browser checks, not a physical iPhone pass.

## Test output

- Full `make check`: **673 Python / 109 frontend tests passed**; lint, types,
  coverage gates, 110 contrast pairs, API types/additivity, motion and privacy
  guards pass. The existing Vite future-config-loader warning remains.
- Focused browser run: **36 passed**, zero failures, in 1.6 minutes.
- Installed-bundle browser run: **10 passed**, zero failures, in 26.5 seconds.
  An earlier installed run also passed all ten before the additional word-change
  assertion and screenshots were added; its observations are retained privately.
- Original chat prototype: drawing and thinking change across frames in both
  Chromium and WebKit, with no page errors. Workflow prototype opens in both.
- The full browser suite was not repeated for this preference/test-only change;
  the prior product source remains the fully tested `88c0eadc` tree.
- Historical tracked evidence overwritten by existing browser tests was archived
  privately and restored; fresh results are separate.

Private logs, raw frame samples, first observations and synthetic videos:
`~/.local/share/workbench/qa/motion-audit-20261015/`.

## Screenshots

All synthetic; screenshots document layout, while frame samples and private
videos provide the motion evidence:

- `artifacts/chat-motion-audit/waiting-synthetic-screen-chromium-fake.png`
- `artifacts/chat-motion-audit/waiting-synthetic-screen-webkit-fake.png`
- `artifacts/chat-motion-audit/thinking-synthetic-screen-chromium-fake.png`
- `artifacts/chat-motion-audit/thinking-synthetic-screen-webkit-fake.png`

## Open questions for Jake

No approval is needed. Fully close and reopen Atelier to hydrate the saved
preference in an already-open Home Screen app. Follow system continues to honor
the iPhone's own Reduce Motion setting. Physical device confirmation is not
invented here.
