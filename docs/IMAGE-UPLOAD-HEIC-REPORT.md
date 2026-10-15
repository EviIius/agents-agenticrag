# Image attachment repair — 14 October 2026

## Summary

The supplied image contained HEIC data despite its PNG extension. Browser decoding
failed before any upload request, and the server previously accepted no HEIC codec.
Uploads now identify HEIC/HEIF contents and use the Mac's existing `sips` codec to
produce a genuine PNG. New attachments also leave Image creation mode so their chat
chips remain visible. No new package, model call, prompt or schema change.

Jake separately reports that the repaired Brief to images workflow and chat image
generation both succeeded. This closes that previous phone retry, not the new upload
check or other untested phone/VoiceOver checks.

## Done-when checklist

| Item | Status | Evidence |
| --- | --- | --- |
| Reproduce format mismatch without retaining the photo | Passed | Header/metadata inspected; real file decoded transiently; no personal media fixture |
| HEIC/HEIF and renamed HEIC upload as real PNG | Passed | `server/tests/test_image_uploads.py`; browser chooser/paste/drop cases |
| Existing PNG, JPEG, WebP, GIF and document uploads | Passed, focused | Chromium/WebKit format matrix and document suite: 16 passes |
| Conversion bounds and cleanup | Passed | 20 MB input/output limits, 2048-pixel long edge, 100-million-pixel decode ceiling, two codecs at once, 20-second subprocess timeout; cancellation/reaping/recovery tests |
| Attachment visible when leaving Image creation | Passed, final focused checks | Successful upload revision drives the mode switch; restored drafts do not |
| Full code check | Passed | 673 Python, 109 frontend; all static guards pass |
| Full browser regression | Pending | One complete invocation running |
| Published repair and actual supplied-file upload | Pending | Private app/data/plist fallback and no-inference verification prepared |

## Changed files

- Server: `app/images/uploads.py`, `app/api/attachments.py`, `app/main.py`.
- Web: image preparation/detection, upload hook, shell/Composer upload revision,
  actionable error copy and its `/design` previews.
- Tests: new Python/frontend/browser upload cases and a generated synthetic 32 × 16
  PNG/HEIC fixture, with its standard-library/native-codec generator.
- Documentation: this report and the recorded acceptance/scope in `AGENTS.md`.

## Deviations from SPEC

D8's original PNG/JPEG/WebP/GIF input list now also accepts HEIC/HEIF, including
misnamed files. Normalized storage/provider input remains PNG and all existing
image-size and vision-capability guards remain. This implements Jake's requested
upload repair using an installed OS facility, with no dependency addition.
No reference-image editing or other image-generation feature is added.

## Runtime observations

The selected chat model reports `vision: true`; no model-name heuristic is used.
The supplied file transiently decoded to PNG, 2048 × 1536, 4,042,931 bytes; the
temporary source/output directory was removed. Its original is unchanged. Photo
contents and its filename are absent from Git, screenshots and test evidence.
HEIC normalization requires macOS's existing codec; a decode failure gives an
actionable JPEG/PNG export message. New codecs are not downloaded.

## Test output and gates

| Gate | Result / evidence |
| --- | --- |
| G1 | Final `make check`: 673 Python, 109 frontend, 110 contrast pairs; all guarded packages exceed 80% coverage; `artifacts/image-upload-heic/check-final.txt` |
| G2 | Pending one complete Chromium/WebKit invocation; corrected upload/chat-image focused suite: 34 passes |
| G3 | New tests only; no existing test assertion, timeout, target or skip changed |
| G4 | Final initial JS 248,048 gzip bytes; previous 247,594 (+454), budget 256,000; full-suite performance artifacts pending |
| G5 | Eight new synthetic upload/error axe audits, both themes at 390/1440: zero serious/critical findings; no horizontal overflow |
| G6–G8 | API-additive, old-row migration and frozen-prompt guards in `make check`; no API/schema/prompt edit |
| G9 | Search/runs/providers untouched; no new inference/eval. Existing factual-grounding limitation remains |
| G10 | Ordinary request/parameter guards unchanged and included in checks |
| G11 | Synthetic captures only; supplied image used transiently and privately; privacy audit in checks |
| G12 | Existing service/route publication checks pending; no deployment config change |
| G13 | Motion CSS untouched; full motion regression included |
| G14 | Both new error codes use production `errorCopy` in `/design` |
| G15 | No migration; schema stays 13; private code/data/plist fallback prepared |
| G16 | Previous generation retry accepted by Jake; repaired upload not physically checked by him yet |

## Core unchanged

The full browser invocation covers C1–C5 chat/stop/resume/long streams/branches,
C6 model selection, C7 explicit parameters, C8 web citations/errors, C9 transcript
retention/downloads, C10 mobile composer, C11 PWA/shortcuts, C14 Markdown safety,
C15 performance and C16 ordinary accessibility. Python checks retain C12 read-only
legacy import and C13 deployment invariants. Final run status is pending.

## Test-diff ledger

No existing test file was edited. New tests cover actual synthetic HEIC conversion,
regular bytes/text, invalid contents, timeout/cancellation, stale temporary cleanup,
header detection, chooser/paste/drop and attachment visibility. Existing assertions,
release thresholds and three existing browser skips are unchanged.

## First full-run failure and correction

Candidate `5dc9148f` failed three Chromium chat-image cases because its new-file
effect treated restored pending recordings as new uploads and disabled explicit
Image mode during initial load. This is a product regression introduced by that
candidate, not a test flake. Stop retained at 282 passes / 3 failures / 1 interrupted /
342 not run in 27.1 minutes. No publication occurred.

The refinement uses a revision incremented only after an actual successful upload;
pending restoration, removal and draft rollback do not increment it. A new browser
case uploads a synthetic recording, restores it and checks explicit Image mode across
navigation/reload. No existing test or gate is weakened. First-attempt raw log and
677 regenerated files are retained separately; traces/videos remain private.
The three original failed cases pass in the focused Chromium/WebKit recheck; final complete
regression remains pending. Evidence: `artifacts/image-upload-heic/attempt-1-stopped/`.

## Screenshots and evidence

`artifacts/image-upload-heic/screenshots/fake-upload-{chromium,webkit}-{390,1440}-{light,dark}.png`
contains only the synthetic gradient's attachment chip and actionable failure copy.
The phone dark screenshot has been inspected by Codex; no actual phone screen or
photo has been captured. Additional regression evidence will be retained here,
with historical tracked artifacts restored after capture.

## Deployment / rollback

Pending full checks. The prepared publisher preserves the current entire app/data
and exact plist privately, copies only three changed server files and the built
frontend, keeps previous hashed assets for open tabs, and checks unchanged schema,
old table projections, local/verified Tailscale health and build hashes. No model
generation is needed to verify upload, and no service identity is changed.

## Known limitations / open questions

Physical iPhone upload retry remains for Jake after publication. Factual grounding
is not newly qualified; Research, future Studio expansion and reference-image editing
retain their gates. Historical VoiceOver failure and iOS keyboard recovery remain
historical limitations, with no new pass claimed.
