# PE1-B QA analysis

20 October 2026. Isolated branch `codex/photo-reference-prep`; production remains
the accepted schema-13 application. This checkpoint connects the PE1-A reference
backend to the existing composer, image cards and viewer. It does not authorize
release or claim that the generative model preserves faces exactly.

## Risk analysis and evidence

| Risk | Check | Result |
| --- | --- | --- |
| Choosing a normal photo silently selects editing | Existing attachment tests plus explicit Tools → Edit photo picker | Ordinary attachments retain their vision meaning; editing uses a separate picker and reference endpoint |
| An edit becomes text-only generation | Fake `run_edit` asserts explicit mode; uploaded reference ID and one seed/count are asserted in browser transport | Reference binding survives submission and replay |
| Lost acceptance schedules a second edit | First response is accepted server-side then aborted client-side; second request body compared exactly | Request key, seed, count, prompt and reference are identical |
| Sending an earlier draft destroys newer typing/photo | Delayed send with both new typing and a replacement upload still in progress; six draft unit tests | New draft moves to the accepted chat; pending upload completes into its current owner |
| Chat switching moves a photo into the wrong draft | Real SPA navigation between new/existing chats, followed by held/cancelled replacement upload | Owner's draft is restored; cancelled upload cannot restore its photo |
| A late error invalidates a newly reattached deduplicated reference | Old submission error with same reference ID but different upload token | New upload remains ready |
| A completed edit is retried without its photo | Card/retry gating and Gallery review | Gallery routes to the original chat; no reference-free generation request is made |
| Clearing inputs deletes completed outputs | Confirm/cancel clear flow, then revisit chat | Completed image remains visible; missing-input retries are disabled with reattach explanation |
| Comparison downloads the wrong file | Viewer checks normalized reference URL and action visibility | Output Save/actions are hidden while reference is displayed; restored with output |
| Old Refine semantics change | Edit image explicitly calls from-job; existing Refine then exercised | Pixel editing is explicit; Refine still opens ordinary generation controls |
| Raw camera metadata is previewed | UI uses normalized reference and sanitized output routes from PE1-A | Private original is not exposed by the composer/viewer |
| New states overflow or violate basic semantics | Nine states × phone/desktop × light/dark × Chromium/WebKit, serious/critical axe checks | See final browser evidence |
| Ordinary chat/context contracts regress | Full existing Python/frontend/browser suites | Exact text/vision context, image count, uploads, workflow and SSE cases remain in the suite |
| New editor bloats initial loading | Final production build and recursive static-import gzip measurement | 255,912 bytes against unchanged 256,000-byte budget; photo host/controller/tray are lazy |

## Findings and repairs

1. Upload completion originally addressed the draft key captured at upload start.
   A new chat can be adopted during an earlier send while its replacement photo
   is still uploading. Uploads now have stable tokens and find their current
   draft owner on completion/error; cancellation also addresses the token. The
   browser test delays both requests and verifies the ready replacement in the
   adopted chat.
2. Gallery's generic retry endpoint cannot express an owned chat reference.
   Edited images now return to the originating chat for reference-preserving
   retry. Missing reference/origin is explained rather than silently producing
   a text-only generation.
3. Reference availability can change after a completed edit. Chats containing
   edits retain their existing SSE subscription so clear/reactivation updates
   reach retry and comparison controls. No UI polling was added.
4. A reference comparison originally left output actions visible. Those actions
   are now hidden while viewing the reference, so Save cannot misleadingly save
   an output under a reference preview. Clearing a reference while comparing
   falls back to the available output state.
5. An old unavailable-reference response could target a new upload with the same
   deduplicated reference ID. Matching the upload token as well prevents that.
6. A rejected ordinary generation in a new chat can reserve a different empty
   chat from a later photo upload. Reusing that old submission's chat sent the
   new reference to the wrong owner and correctly triggered a server refusal.
   Submission state now discards a reserved chat that differs from the explicit
   reference owner. A browser regression rejects generation, selects a photo,
   and asserts its accepted request/navigation use the uploaded reference's chat.
   Both Chromium and WebKit pass. The first broad browser run was interrupted
   after 26 passes to repair this review finding; its log and synthetic outputs
   are retained separately, and a new full invocation uses the corrected source.
7. New test development exposed fixture mistakes: importing a React design
   component into Node test discovery, navigating to empty chats absent from the
   sidebar, selecting a hidden desktop sidebar duplicate on phone, and selecting
   a link during the mobile drawer's closing transition. The pure state list was
   extracted; navigation seeds synthetic history and waits for drawer closure.
   Tests still use real SPA links, uploads and acceptance. Assertions/timeouts
   were not weakened. Initial failure contexts/traces and subsequent logs remain
   in the B evidence folder. One intermediate aggregate log was overwritten by
   a later focused command; its two original failure traces/contexts and source
   are retained. Do not describe that intermediate invocation as a pass.
8. The separate photo picker exposed overly broad selectors in older upload
   tests. `input[type=file]` now correctly finds two different product inputs;
   three cleanup cases failed Playwright's strict selection before uploading.
   Existing attachment tests now target `input.composer-file-input`, preserving
   their ordinary-upload behavior and all assertions. Settings Library uploads
   remain scoped to their separate input. The cancellation case passes 2/2 with
   the explicit selector. The interrupted run retains 50 passes, three selector
   failures and its traces; fresh complete suites use the updated tests.
9. The complete follow-up browser invocation reports 737 passes, two failures
   and three existing skips. Both failures are the same older creation-mode
   upload case: its intentionally hidden attachment input has no
   `composer-file-input` class. The corrected selector preserves the old ordinary
   input while excluding only the separate Edit photo picker. No product file,
   assertion or timeout changes in this final repair. The original full log,
   both traces and exact full-run source manifest remain intact. A fresh run of
   the entire image-upload file verifies the correction; its result is recorded
   below and in H4. Do not relabel the original full invocation as entirely green.
   The fresh complete image-upload file passes **12/12** across both browsers,
   including both corrected creation-mode cases. Final frontend lint/types/
   formatting and all 132 unit tests pass again. All other full-run case sources
   and every product source remain identical (`final-test-only-delta.json`).

## Separate private real-photo check

The user separately authorized one local FLUX edit on a supplied photo. It is
outside the frozen six-call PE0 trial, with no retry or helper/text-model call.
The current product worker completed it in 19.01 seconds total (15.66 seconds
generation), reporting 18,658,395,574 peak MLX bytes and zero observed swap growth.
The sanitized export is 1,319,175 bytes; the original was verified unchanged.

Codex's visual observation: the requested hat was added, but eyes/expression,
framing and other details also changed. These results support describing this
as generative editing; they do not establish exact likeness or unrelated-pixel
preservation. No mustache edit was run. The source, filename, hashes, image
outputs and private execution records stay outside Git/public evidence.
No user quality acceptance or physical-phone pass is invented.

This single check is not PE1-C qualification: actual HEIC decode, empty-residency
usability, final bounded native controls, release/rollback rehearsals and an
approved deployed-phone check remain later gates.

## Final commands and preservation

- `make check` passed: 745 Python tests, 132 frontend tests, 110 contrast pairs,
  coverage (images 83.5%, unchanged 80% floor), types, lint, formatting, API growth,
  motion and privacy guards.
- Final production build passed: 255,912 initial gzip bytes within the unchanged
  256,000-byte limit; 429 built files have a separate build manifest.
- Complete browser invocation: 737 passed / two creation-mode fixture-selector
  failures / three existing skips. All eighteen new photo-edit cases passed.
  The corrected image-upload-file result is retained separately. Full-run
  product code and all other case sources remain identical; only that selector
  changes after the full invocation. No whole-suite green invocation is claimed.
- Dev-server logs include Streamdown highlighting and React Router dynamic
  module-import warnings. Tests covering those screens passed; their cause is
  not established here. Preserve the logs and check module loading in the built
  candidate during PE1-C rather than claiming a clean console.

The final archive restores all **1,640** overwritten tracked historical artifacts
byte-for-byte, after preserving the fresh synthetic run privately; 40 additional
run artifacts are archived separately. The B screenshots and failure traces stay
in this checkpoint's evidence folder.

The read-only audit passes: 572 final candidate files, 551 main source files,
114 installed server files, 425 installed static files, all eleven PE0 source
files and 73 PE0 evidence files verify. PE0 remains six invocations; the separate
private user-photo check is exactly one. Stopped trial ledgers, generation worker,
Ollama 0.35.0 and local/verified HTTPS health remain preserved. No deployment.
