# Image attachment repair — 14 October 2026

## Summary

The supplied image contained HEIC data despite its PNG extension. Browser decoding
failed before any upload request, and the server previously accepted no HEIC codec.
Uploads now identify HEIC/HEIF contents and use the Mac's existing `sips` codec to
produce a genuine PNG. New attachments also leave Image creation mode so their chat
chips remain visible. No new package, model call, prompt or schema change.

Jake separately reports that the repaired Brief to images workflow and chat image
generation both succeeded. This confirms the previous fix functionally; the device
is unspecified, so no physical-phone or other untested check is marked passed.

## Done-when checklist

| Item | Status | Evidence |
| --- | --- | --- |
| Reproduce format mismatch without retaining the photo | Passed | Header/metadata inspected; real file decoded transiently; no personal media fixture |
| HEIC/HEIF and renamed HEIC upload as real PNG | Passed | `server/tests/test_image_uploads.py`; browser chooser/paste/drop cases |
| Existing PNG, JPEG, WebP, GIF and document uploads | Passed | Format/document suites in the complete Chromium/WebKit run |
| Conversion bounds and cleanup | Passed | 20 MB input/output limits, 2048-pixel long edge, 100-million-pixel decode ceiling, two codecs at once, 20-second subprocess timeout; cancellation/reaping/recovery tests |
| Attachment visible when leaving Image creation | Passed, final focused checks | Successful upload revision drives the mode switch; restored drafts do not |
| Full code check | Passed | 673 Python, 109 frontend; all static guards pass |
| Full browser regression | Passed | One complete invocation: 627 passes, three existing skips, zero failures |
| Published repair and actual supplied-file upload | Passed | Live Chromium/WebKit: 201, visible chip, stored PNG decodes, own test uploads deleted; zero model calls |

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
The supplied file decoded to PNG, raster 2048 × 1536, 4,042,931 bytes; its EXIF
orientation 5 makes both browsers decode it at 1536 × 2048. Conversion temporary
directories were removed, and the original is unchanged. Photo
contents and its filename are absent from Git, screenshots and test evidence.
HEIC normalization requires macOS's existing codec; a decode failure gives an
actionable JPEG/PNG export message. New codecs are not downloaded.

## Test output and gates

| Gate | Result / evidence |
| --- | --- |
| G1 | Final `make check`: 673 Python, 109 frontend, 110 contrast pairs; all guarded packages exceed 80% coverage; `artifacts/image-upload-heic/check-final.txt` |
| G2 | One complete `make e2e`: 627 passed / 3 existing skips / 0 failed, 1.0 h; `full-run/e2e.txt`; corrected focused suite also 34/34 |
| G3 | New tests only; no existing test assertion, timeout, target or skip changed |
| G4 | Initial JS 248,048 gzip bytes; previous 247,594 (+454), budget 256,000. Streaming render p95 3.6 ms Chromium / 3 ms WebKit (<8); first-token overhead 84.48 / 68.95 ms (<150); 300-message checks pass |
| G5 | Eight new synthetic upload/error axe audits, both themes at 390/1440: zero serious/critical findings; no horizontal overflow |
| G6–G8 | API-additive, old-row migration and frozen-prompt guards in `make check`; no API/schema/prompt edit |
| G9 | Search/runs/providers untouched; no new inference/eval. Existing factual-grounding limitation remains |
| G10 | Ordinary request/parameter guards unchanged and included in checks |
| G11 | Synthetic captures only; supplied image used transiently and privately; privacy audit in checks |
| G12 | Exact plist/route unchanged; one worker at 127.0.0.1:8787; local/verified HTTPS health, exact index/SW hashes and production `/design` 404 pass |
| G13 | Motion CSS untouched; full motion regression included |
| G14 | Both new error codes use production `errorCopy` in `/design` |
| G15 | No migration; schema 13, all 55 old-table projections preserved; private full app/data/plist fallback retained |
| G16 | Previous generation fix functionally accepted by Jake; physical device unspecified; repaired upload not physically checked by him yet |

## Core unchanged

The full browser invocation covers C1–C5 chat/stop/resume/long streams/branches,
C6 model selection, C7 explicit parameters, C8 web citations/errors, C9 transcript
retention/downloads, C10 mobile composer, C11 PWA/shortcuts, C14 Markdown safety,
C15 performance and C16 ordinary accessibility. Python checks retain C12 read-only
legacy import and C13 deployment invariants. Both full commands passed.

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
The three original failed cases pass in the focused Chromium/WebKit recheck and
the fresh complete run. Evidence: `artifacts/image-upload-heic/attempt-1-stopped/`.

## Screenshots and evidence

`artifacts/image-upload-heic/screenshots/fake-upload-{chromium,webkit}-{390,1440}-{light,dark}.png`
contains only the synthetic gradient's attachment chip and actionable failure copy.
The phone dark and desktop light screenshots were inspected by Codex; no actual
phone screen or photo was captured. Fresh full-run captures and performance JSON
are retained separately, and all 1,313 regenerated historical artifacts were
archived privately before restoring their tracked baseline bytes. Earlier failed
attempt data remains separate. Public text logs trim trailing whitespace; raw logs
and complete browser videos/traces remain private.

## Deployment / rollback

Candidate `cdc66a3d` is live. The publisher preserved the current entire app/data
and exact plist privately under `~/.local/share/workbench/qa/image-upload-heic-20261014/release/`,
copied three server files and the 420-file frontend build, and kept previous hashed
assets for open tabs. Restart to healthy: 1.853 s. Schema 13, integrity/FKs, all 55
old-table projections, exact plist/route, local/verified Tailscale health and build
hashes pass. No runtime/model/dependency/default/sampling change or new model call.
Publication summary: `artifacts/image-upload-heic/publication.json`.

The actual supplied file uploads and decodes through both live browser UIs, with
visible attachment chips. Only the observer's own new attachments were removed,
and absence was checked. Zero inference, screenshots, traces or videos. The first
live observer incorrectly required bitmap dimensions to equal PNG raster dimensions;
the retained PNG orientation 5 explains their transposition. It cleaned up its upload.
The observer was corrected to allow that orientation and both final checks pass;
no product source, test assertion or release target changed. Raw initial observer
failure stays private. Final summary: `artifacts/image-upload-heic/live-upload.json`.

## Known limitations / open questions

Physical iPhone upload retry remains for Jake after publication. Factual grounding
is not newly qualified; Research, future Studio expansion and reference-image editing
retain their gates. Historical VoiceOver failure and iOS keyboard recovery remain
historical limitations, with no new pass claimed.
