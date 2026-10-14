# Chat images CI-C report

## Summary

CI-C on the isolated `codex/workflow-studio` branch adds Claude's full-screen
image viewer, More like this, prompt refinement, vision-gated Ask about it,
phone scroll snapping and image-aware exports. Source freeze: `f8e301c2`.
Main and the installed app remain unchanged. The complete browser regression run passes. The separately requested bounded
native workflow trial stops after its first semantic failure; see its H4 report.
This branch has not been merged or published.

## Done-when checklist

| Item | Status | Evidence |
| --- | --- | --- |
| CI-AC17 Viewer FLIP, thread navigation, focus | Pass | `chat-image-viewer.spec.ts`, videos outside Git |
| CI-AC18 More like this / Refine lineage | Pass | Python lineage/export test; browser uncertainty/draft test |
| CI-AC19 Vision-gated existing upload | Pass | Fake runtime explicitly reports vision; no automatic text send |
| CI-AC20 MD/JSON selected-branch export | Pass | `test_chat_image_exports.py`; no embedded image bytes |
| CI-AC21 Phone snap/dots/gestures | Pass in Chromium/WebKit | 390 px pinch/double-tap/pan/swipe-down check |
| CI-AC22 Both themes/widths axe | Pass | Viewer and refine axe at 390/1440 in both engines |

## Changed files

Server: `api/chats.py`, one synthetic export/lineage test. No new schema or API.
Web: ImageTurn, shared ImageActions, lazy ImageViewer, Composer, LiveThread,
LiveAppShell, useChatImages, per-chat draft/refinement state, /design preview and
motion.css. One browser test file. Docs and evidence helpers/report.

## Deviations from the supplied plan

Viewer navigation follows the selected conversation branch in thread order,
excluding unavailable/removed outputs. Closing returns to and focuses the frame
that opened it. Refine changes the prompt and records lineage; reference-image
editing remains CI-D. No new dependency or inference is used for CI-C.

## Runtime observations

Focused fake checks exposed a real portal timing error: parent layout effects
ran before Radix mounted its Content, leaving the viewer's fit geometry at zero.
A stable element callback now measures the mounted viewport with ResizeObserver;
zoom is bounded against zero-size geometry. A light-theme contrast error used an
undefined background token; the existing `--surface` token fixes it. Nested-dialog
Escape testing now waits for the closing child surface to settle before targeting
the viewer. No assertion threshold, timeout or existing skip was relaxed.

## Test output

`make check`: 654 Python / 104 frontend tests pass; required coverage >80%,
110 contrast pairs, API additive/types, motion, privacy and frozen prompt checks.
Three focused browser attempts retained: 12 pass/8 fail; 10 pass/2 fail;
20 pass/0 fail after fixes. A workspace-intent review fix was then checked in
both engines (2 pass). Its initial test corrections are retained separately:
wrong hard-navigation/back selector (2 failures) and model-qualified textarea
label (2 failures). Every available recording and failure trace is kept.
The first complete attempt was deliberately interrupted for that intent fix:
60 passed, one interrupted, 557 unrun in 8.9 minutes; its log/source and available
trace remain. No thresholds/timeouts/skips were relaxed.
The next full attempt retained 613 passes, two WebKit failures and three existing
skips (1.0 hour). Its focus race is repaired by running iteration in Radix's close
focus callback; the existing delayed-controls test now waits for separate model/
header bootstrap while chat detail stays held. Nested save-dialog arrows stay
owned by that dialog. Six repetitions of each of three WebKit checks then pass
(18/18). The final complete invocation passes: **615 passed, three existing skips, zero
failures in 1.0 hour**, on frozen source `f8e301c2`. `npm run build` passes.
Native Web accuracy gate G9 remains open; 56 zero-inference payload comparisons
over 25 original questions prove context parity, not factual-answer qualification.
No native Web eval or answer-prompt change was made.

## Screenshots

Synthetic viewer/refine/conversation shots and axe records under
`artifacts/chat-images/ci-c/browser/`; complete-suite regenerated evidence is
archived separately and previous committed bytes restored. Motion videos
are stored outside Git under `~/.local/share/workbench/qa/chat-images/ci-c/`.
No private recording/document evidence or physical iPhone/VoiceOver pass claimed.

## Performance and preservation

Initial JS: **247,594 gzip bytes**, +746 from CI-B, below the 256,000-byte total
and 8,192-byte growth allowances. The viewer remains lazy loaded. Required browser
performance checks pass: chat render p95 3.6 / 3 ms, first-token display overhead
75.26 / 66.43 ms, ticker render p95 0.5 / 1 ms (Chromium / WebKit).
All 16 new viewer/refine axe audits pass; full existing catalogue audits also pass.

The archive retains 1,286 fresh suite outputs, restores 1,246 historical files and
relocates 40 synthetic captures. All 620 available final videos (79,647,011 bytes)
remain outside Git, alongside separately retained failed-attempt recordings.
2,620 redundant regenerated-attempt copies resolve to retained, hash-verified
canonical files, avoiding 711,161,599 duplicate bytes without discarding outcomes.

Verification preserves 556 frozen source/test files, 322 core files, 35,324
historical evidence/eval/fixture blobs, all 15 workflow references and all 17
supplied image-plan files. The installed 97 server / 410 static files and main
`dce4c49e` remain unchanged. Local and normally verified Tailscale HTTPS health
pass; production `/design` stays 404. Port, service, route, runtime and defaults
are unchanged. The first health helper hit the framework Python certificate-store
limitation; macOS curl verified HTTPS without bypassing certificate verification.

## Native workflow trial

`docs/WORKFLOW-STUDIO-NATIVE-TRIAL-REPORT.md` records two actual Qwen calls, exact
variable binding, streaming and the paused review. Both outputs add unsupported
event facts, so the declared stop rule ends inference. No repeat, approval/edit,
in-flight cancellation or recovery pass is claimed. This failure does not change
the green CI-C UI checks or qualify native workflow answer fidelity.

## Open questions for Jake

Final merge and publication still require Jake's explicit okay. CI-C and the bounded trial
are closed out for review. Reference-pixel editing, further native experiments and
Studio expansions remain separately gated.
