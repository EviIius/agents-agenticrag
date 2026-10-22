# Camera-photo preparation repair — 21 October 2026

## Summary

The supplied photo succeeds against the installed API. The reported phone
failure could not be reproduced with that attachment: it arrived as JPEG, and
synthetic HEIC, orientation variants, 12 MP and 48 MP preparations also passed.
This does not establish the cause of the earlier phone failure.

The edit-upload path now recovers automatically from a decoder rejection when
the browser can render the photo. It uploads the unchanged original together
with a bounded browser-derived PNG, then uses the existing isolated CPU codec
to validate, orient, resize and strip metadata. The resulting receipt identifies
browser orientation explicitly; it does not claim the original EXIF was read.

## Done-when checklist

| Item | Evidence |
|---|---|
| Automatic conversion, no manual export | `web/tests/photo-upload-fallback.spec.ts`: controlled decoder rejection → automatic second upload → Ready, including actual HEIC in WebKit |
| Original retained unchanged | Browser FormData byte comparisons, API preservation/binding test, real CPU API checks; supplied-photo checks remain private |
| Bound/validate the working PNG | Actual pinned CPU interpreter validates HEIC/PNG normal and browser-derived inputs, plus product-worker receipt validation; corrupt PNG refused |
| No retry loop or permission bypass | One retry only for 422 `image_unreadable`; 404 is not retried; cancelled conversion cannot submit or restore a removed photo |
| Existing editing behavior | Ten Chromium/WebKit functional checks cover replay, new-chat ownership, replacement, comparison, clearing and generated-output edits |
| Size/privacy limits | Each file remains at most 20 MB; PNG input and working edge at most 2048; dimensions at most 100 MP; no supplied-photo screenshots or fixtures |
| Initial JS | 255,948 / 256,000 gzip bytes; converter remains in the lazy photo-edit module |

## Changed files

- Web: `photo-upload.ts`, `usePhotoEdit.ts`, generated API types and focused
  browser tests. No new composer layout or mode.
- Server: optional browser-preview multipart fields, bounded input handling,
  explicit preparation provenance, compatible reference validation.
- Worker: existing CPU preparer accepts the browser-decoded PNG and emits its
  explicit recipe. The generation/edit inference implementation is unchanged.
- Docs/evidence: this report, the narrow AGENTS correction and
  `artifacts/heic-preparation-20261021/`.

## Deviations and limits

The multipart envelope grows from one 20 MB file to two bounded files plus
overhead; each individual file still has the original limit. There is no database
migration. Original dimensions in the browser-derived recipe are the browser's
oriented dimensions. Source and working hashes remain independently bound.

There are no new packages, GPU/model calls, prompts, model settings or downloads.
If neither browser nor Mac can decode damaged bytes, the photo remains retryable
and is not sent. This repair does not qualify every possible HEIF variant or
establish physical iPhone acceptance.

## Runtime observations

Existing `/usr/bin/sips`, the pinned image interpreter and Pillow handle the
tested normal HEIC path. WebKit also decodes the real synthetic HEIC through its
browser decoder after a controlled server rejection. Original orientation and
camera-size diagnostic results are retained separately. Ollama is unchanged.

## Test output

- Focused backend tests: **39 passed**.
- Product worker offline checks: **14 passed**, using real CPU Pillow and fake
  inference, with native imports/network prohibited by the harness.
- Actual CPU/API checks: **four valid cases passed**, corrupt PNG rejected,
  children reaped, no inference.
- Focused browser regression: **19 passed, one intentional Chromium HEIC skip**.
  The HEIC fallback case passes in WebKit. This is not a complete `make e2e` run.
- Initial observer run: seven passed and one failed because Playwright WebKit
  omitted multipart file bytes from `postDataBuffer()`. The corrected observer
  checks the actual browser FormData bytes without removing the assertion;
  all eight original checks then passed. Both attempts are preserved.
- Full `make check`: **766 Python / 132 frontend tests**, types, lint, formatting,
  110 contrast pairs, coverage, motion, privacy and additive API gates pass.
  Image coverage is retained in `coverage.json`. The prior tracked coverage
  artifact is restored; the new result stays in this repair's evidence folder.

## Screenshots

Synthetic Ready state: `ready-chromium.png` and `ready-webkit.png` under the
evidence directory. No real image appears in these screenshots.

## Release closeout

Pending final gates and installed-build checks. A fresh private app/worker/data
bundle and the schema-aware backend/current-data compatibility policy are used;
an old backend or pre-release database must not replace newer photo references.
