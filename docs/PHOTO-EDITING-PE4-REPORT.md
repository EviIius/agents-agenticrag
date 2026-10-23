# PE4 — selection repair report

22 October 2026. Isolated `codex/masked-photo-editing`, draft PR #9.
Implementation and QA complete; stopped for selection/comparison review.

## Summary

Added Paint/Protect/Move, zoom/pan, a visible brush cursor, Undo/Redo, uniform
overlay and selected/protected views. Ordered erasing travels through durable
requests and the CPU compositor; legacy masks retain their original bytes and
serialized shape. The supplied photo has a separate private CPU coverage review.
No new generated image or native/model invocation has been made.

## Done-when checklist

| Item | Status | Evidence under `artifacts/photo-editing/pe4-20261022/` |
|---|---|---|
| Paint/Protect, zoom/pan and coordinate mapping | Implemented, focused pass | Initial browser passes and corrected four-case diagnostic |
| Undo/Redo/Clear/Cancel and empty selection | Focused pass | Browser acceptance/rejection/retry and empty-state checks |
| Selected/protected preview and approximate coverage | Focused pass | Actual canvas alpha checks; UI labels distinguish changeable/protected pixels |
| Ordered erasing and erased-region preservation | Pass | `cpu-focused-initial.log`, real Pillow/process tests |
| Legacy raster and request identity | Pass | Retained PE2 mask hash; exact API projection/replay assertions |
| Retry, cross-chat ownership and backup restore | Pass | `api-focused-initial.log`, 11 API cases including paint/protect variant |
| Private photo coverage and facial protection | CPU pass only | `private-coverage.json`; no generated-quality assertion |
| Full check / bundle | Pass | 777 Python, 132 frontend, 83.1% image coverage; 255,964/256,000 gzip bytes |
| Full browser suite | 790 pass / four intentional skips / two stale-label assertion failures; correction verified in 12-case rerun | `browser-full.log`, retained failure traces, `browser-qa-correction.log` |
| Prior trial/live app preservation | Pass | `preservation-final.json`; frozen PE3 sources/inputs and exhausted two-attempt ledger verify |
| Main merge/publication/native retest | Not performed | Separate review scope remains |

## Changed files

- **Web:** lazy mask dialog and `photo-mask.ts`, typed API update and /design
  protected/erased-empty states; browser tests for preview, pointer mapping,
  protection/replay and limit handling.
- **Server:** optional `PhotoStroke.operation`, omitted when absent; validation
  rejects unknown operations and erase-only selections. Existing serialized
  masks remain unchanged. API/backup tests cover the additive operation.
- **CPU worker:** `masked_edit.py` applies paint/erase in order and refuses an
  empty effective mask before any model import. Erased and other unselected
  pixels remain exact under the existing contained feather/composite verifier.
- **Docs/evidence:** scoped plan, private-coverage metrics, current test evidence;
  previous executed sources, failures and native ledgers remain immutable.
- **Existing QA assertion:** `qa-repairs.spec.ts` now checks the compact visible
  `Default` label plus the full `Model default` accessible name/tooltip specified
  by the already approved mobile Tools redesign. Selection/capability checks stay.

## Deviations from SPEC.md

No schema migration or dependency. The unchanged selection version accepts a new
optional operation; omitted strokes are paint and keep their old raster hash.
New operations require this updated CPU worker and schema-aware backend; an older
worker cannot safely process them. No old-worker fallback is qualified here.

The full regression exposed an older assertion that predated the compact Tools
label in `30f0bb17` / `MOBILE-TOOLS-REPORT.md`. Correcting that test changes no
product behavior, thinking level or model payload. The original failures remain.

The browser preview uses native canvas edge antialiasing and reports approximate
coverage. The real CPU raster and output verifier are authoritative; browser
statistics do not prove semantic object coverage. A completely erased mask is
disabled in the UI and refused by the CPU raster before native model imports.

The live FLUX engine, Qwen checkpoint, inference settings, prompts, sampling,
service/port/plist/Tailscale and old data are unchanged. The proposed subsequent
two-engine comparison is documented separately; no new native allowance is
created by implementation or CPU mask review.

## Runtime observations

No model was invoked. The supplied original was inspected privately on CPU, with
manual small-region annotations and a facial outline. The old rectangular
protection area had also excluded hair needed for the cap. The corrected mask
paints existing hair/hands and space for additions, then erases the facial outline
and watch from the changeable area.

| Small manually identified region | Prior selected | Corrected selected |
|---|---:|---:|
| Crown hair | 33.47% | 100% |
| Side hair | 14.62% | 100% |
| Front hand | 79.14% | 100% |
| Rear hand | 100% | 100% |

The manually outlined face has zero selected pixels; 3,025,097 pixels remain
protected. The mask uses 20 strokes and remains within existing point/manifest
bounds. A CPU composite with synthetic replacement pixels verifies zero changed
protected pixels. These observations establish selected-region coverage, not a
new successful hat/glove edit, full-object coverage or automated face detection.
The rear-hand region was already covered in the failed generation, so selection
coverage alone is insufficient to explain or solve every quality failure.

The separate Chromium canvas audit receives only the private mask coordinates,
loads no private photo and blocks API requests. It selects 120,720 pixels against
the CPU's 120,631: 89 boundary pixels differ because of preview antialiasing.
Both cover the four checked regions and leave the manual facial region empty.
This is checked-region agreement, not complete raster or generated-quality parity.

The final inventory matches all 668 installed application/static files (including
548 embedded static files), the installed worker and launchd plist. The prior
18 frozen input/source files and 77 engine sources verify; the old reservation
count remains two. Ollama is 0.35.0. Local and normally verified Tailscale HTTPS
health return 200; no service restart, main merge or publication occurred.

## Test output

- **make check:** 777 Python / 132 frontend pass; required coverage, 110 contrast
  pairs, API additive/types and motion/privacy checks pass. Image coverage 83.1%.
- **32 CPU/process checks pass**, including six new protection/legacy/refusal
  checks. The new real API focused run passes 11 cases.
- Initial browser run: 37 passes / three failures. Two new preview tests compared
  unpremultiplied RGB without alpha; they now measure selected/protected opacity.
  WebKit rounded the injected fractional pointer coordinate; the test now records
  the delivered event independently, retaining four-decimal payload assertions.
- The first coordinate-instrumentation correction awaited a pending page promise
  and timed out twice. The final correction registers a synchronous one-shot
  event listener before input; all four targeted Chromium/WebKit checks pass.
  Original logs/traces remain retained; assertions were not weakened.
- Full browser run on product commit `c0229e7c`: **790 passed, four skipped,
  two failed**. Both failures are the same old assertion expecting visible
  `Model default` instead of the approved compact `Default`. Corrected assertion
  also checks the full tooltip and accessible name; **all 12 cases in that QA
  file pass in Chromium/WebKit**. No product code changed after the full run,
  so the full suite was not repeated for a test-only correction.
- All seven new protection-editor cases pass in each browser in the full run:
  ordered erasing/replay, selected/protected opacity, zoom/pan coordinates,
  erased-empty refusal, rejected-stroke limit isolation and both short-phone
  themes. Existing photo ownership, retry, preparation and mask checks pass too.
- A final frontend check again passes types/lint/format and all 132 unit tests.
  The four full-run skips are pre-existing: Chromium HEIC decode and WebKit's
  long-answer, duplicate review-size screenshot and offline-PWA checks.
- No physical iPhone or VoiceOver pass is claimed.

The complete current regression captures and 754 fake browser recordings are
retained in the private PE4 `regression-captures` archive, with hashes in
`regression-captures.json`. All 1,736 changed historical tracked artifacts were
restored byte-for-byte; 72 newly generated historical-path files were archived.
The PR retains 108 relevant synthetic photo captures, focused precision images,
full logs and all initial/final failure traces. No historical result is replaced.

## Screenshots

Synthetic phone snapshots: `browser/precision-fake-390-{light,dark}-{browser}.png`.
The interactive synthetic editor is available at
`http://127.0.0.1:5173/design?photo-edit&state=selection-protected`, using a
temporary fake-runtime preview separate from the live application.
The private CPU-only before/after mask comparison is open locally at
`http://127.0.0.1:8770/review.html`; it contains no new generated edit. Real media,
filenames, facial coordinates and selection details remain outside Git.

## Open questions for Jake

Review the corrected mask and the proposed
`PHOTO-EDITING-PE4-COMPARISON-PLAN.md`: one fixed run per installed engine with the
same corrected selection, source and user prompt. No generation under that
proposal has been approved or executed. Retain both models and keep main/live
unchanged until their separate quality/release review.
