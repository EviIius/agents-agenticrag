# PE1-B report — photo editing in chat

## Summary

Tools → Edit photo now uses the native picker, one private reference and the
existing composer. Edited image turns support progress/cancel, save/share,
explicit Edit image and reference comparison. Ordinary generation and vision
attachments keep their existing meanings. The branch remains isolated and
unreleased. Full regression evidence retains a corrected older test-selector
failure separately from the completed invocation.

## Done-when checklist

| Item | Status | Evidence |
| --- | --- | --- |
| Direct picker, thumbnail, preparation/error/retry states | Implemented | `photo-editing.spec.ts`, nine `/design?photo-edit` states |
| Separate per-chat edit drafts; rejection/navigation/replacement safety | Focused pass | Six unit cases; Chromium/WebKit delayed acceptance and cancelled upload cases |
| Explicit reference-preserving submission and Edit image | Focused pass | Body equality after lost acceptance; from-job ownership request |
| Existing Refine/generation/text/vision behavior | Verified with retained fixture correction | Full command logs; no prompts or generation worker changed |
| Normalized reference comparison, retained output after clear | Focused pass | Real viewer, confirmed clear and missing-input retry checks |
| Existing tokens, SSE/rAF and motion preferences | Pass | Design matrix, full motion cases and unchanged motion system |
| Initial JS budget | Pass | `bundle-final.json`: 255,912 / 256,000 gzip bytes |
| Full checks | Pass | 745 Python / 132 frontend / 110 contrast pairs; `make-check.txt` |
| Full browser suite | Complete; corrected fixture result separate | 737 passed / two selector failures / three existing skips; `make-e2e.txt` |
| Corrected image-upload file | Pass, 12/12 | `browser-image-upload-final.txt`; final frontend check also passes |
| Production/frozen evidence preservation | Pass | `preservation.json`, `browser-archive.json`; 1,640 historical artifacts restored |
| Separately requested private hat check | Complete, limited quality | One invocation; original unchanged; actual face/expression/framing drift disclosed |
| PE1-C/release/physical phone acceptance | Not performed | Later separately reviewed scope |

## Changed files

- Web: lazy photo draft/controller/host/tray; composer Tools and submit handling;
  image actions/cards/viewer; Gallery retry, input cleanup and storage details;
  nine synthetic design states; draft unit/browser regressions.
- Server: test-only fake engine/codec wiring; no additional product-server change
  beyond the committed PE1-A backend.
- Docs/evidence: B authorization, QA analysis, this H4 report and synthetic/fake
  command logs/screenshots. Private user imagery is excluded.

## Deviations from SPEC.md

The reviewed PE1 plan and 20 October user authorization define this new edit
flow. No new dependency, model, prompt, sampling value, agent, runtime, service
port or production change is included. The fixed one-image square format and
potential changes to unrelated details are visible in the composer/viewer.

## Runtime observations

One separately authorized private local edit completed in 19.01 seconds total;
the requested hat appears, but eyes/expression/framing also change. It is not
an exact-preservation result or full product qualification. The original and
all private input/output records are retained outside Git. PE0 stays six calls;
stopped agent and Research trials remain closed.

## Test output

`make check` passed: 745 Python / 132 frontend tests, 110 contrast pairs, all
lint/type/format/API/coverage/motion/privacy guards. Image coverage is 83.5%
against the unchanged 80% floor. Build and initial gzip budget pass.

Full browser invocation: 737 passed / two selector failures / three existing
skips. All eighteen new photo-edit cases passed. Both failures use the same older
creation-mode upload test's wrong selector; product code is unchanged by its
correction, and the complete image-upload file is rerun separately. Do not call
the original complete invocation green. Full-run source is preserved separately
from the final test-only correction.
The entire corrected image-upload file then passes **12/12**, including both
failed cases, with final frontend lint/types/formatting and 132 unit tests passing
again. `final-test-only-delta.json` proves every product source and all other
full-run case sources stay unchanged. This is a full invocation plus a corrective
run, not a claim of one wholly green browser invocation.

Retain the initial development/discovery/navigation
fixture failures and their corrective focused passes separately. The nine-state
design matrix passed 8/8; asynchronous-ownership comparison passed 4/4, and the
subsequent new-chat reservation regression passed 2/2 before the full invocation.
The earlier broad invocation was deliberately interrupted after 26 passes to
repair the reviewed new-chat ownership bug. Its log/outputs remain separate;
it is not represented as completed QA.
A second invocation exposed three ambiguous selectors in older upload tests
and was stopped after 50 passes. Those tests now explicitly target the ordinary
attachment picker; cancellation passes both browsers before the new full run.
All original upload/assertion/timeout behavior is retained.

The dev-server log contains Streamdown/React Router module-import warnings;
affected tests passed. Their cause remains unproven, and built-app module loading
needs verification during PE1-C. No clean-console or physical-phone pass is claimed.

All 572 final candidate, 551 main, 114 installed server, 425 installed static,
eleven frozen PE0 source and 73 native evidence hashes verify. All 1,640 changed
historical artifacts were restored after archiving fresh synthetic outputs;
40 new run artifacts were privately archived. Main/live are unchanged and healthy;
Ollama remains 0.35.0. The separate private edit is one invocation; PE0 stays six.

## Screenshots

Synthetic screenshots under `artifacts/photo-editing/pe1-b-20261020/browser/`:
`ready-390-dark-webkit-fake.png`, `complete-1440-light-chromium-fake.png`, and
the matching preparing/error/unavailable/running/cancelled/comparison/rejected
states in both themes and browser projects. No supplied user photo is committed.

## Open questions for Jake

Stop at B for review. PE1-C still needs a concrete bounded native qualification
and release/rollback scope before merge/publication. The real-photo result has
been shown privately; quality acceptance is not assumed.
