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

PR #8 merged as `b50f8a80`; the repair is live. A fresh **2,106-file private
bundle** verifies, **674 installed app files** and **four worker files** match,
and database/input bytes, interpreters/selectors, plist/service identity and
Tailscale route are preserved. Schema remains 14 and Ollama remains 0.35.0.
Observed downtime was **3.49 seconds**. Local and verified HTTPS health, edit
capability and index/service-worker hashes pass. The previous UI fallback keeps
the current schema-aware backend/worker/data; old-backend/database restore
remains prohibited.

The **actual installed HTTPS composer** now accepts the privately supplied photo
and reaches **Ready** in Chromium and WebKit. A controlled first decoder
rejection forces the new conversion path; both original-byte comparisons pass
and the prepared reference is **1536 × 2048**. Typing works and Edit photo is
enabled. No instruction was submitted, no edit/model call was made, and no real
photo screenshot/trace/filename is included in evidence.

The initial live observer reached Ready but failed its request-count assertion,
so it was not credited as a fallback pass. Its private failure is preserved. The
controlled rerun blocks service workers only in the test browser to make request
interception deterministic; both fallback assertions pass. This is browser
automation on the Mac, not a physical iPhone/PWA acceptance claim. Reloading the
Home Screen app is necessary to receive the new client code.
