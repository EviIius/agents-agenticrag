# PE0 offline preparation — 19 October 2026

## Summary

The isolated reference-editing worker and bounded controller are prepared on
`codex/photo-reference-prep`, based on accepted main `c0d65ee0`. The 84 offline
checks pass, including new reference/process controls and existing image and
residency regressions. Production code and the live app are unchanged.
No weights were loaded and no native model call was made. Image quality,
likeness, native edit latency, memory and coexistence remain unqualified.

## Done-when checklist

| Item | Result | Evidence |
| --- | --- | --- |
| Explicit generation/edit contract | Pass, offline | Missing mode/reference, unknown fields, duplicate JSON, bad seed/prompt and stale receipts reject before initialization |
| Bound owned reference pixels | Pass, offline | Fixed private paths, symlink rejection, original/working SHA-256 and dimensions; no filename/path field accepted |
| Preserve originals and normalize | Pass, CPU | Original bytes retained; PNG/JPEG decode, EXIF orientation, bounded size and metadata stripping tested |
| Keep ordinary generation arguments | Pass, fake backend | Exact same seed/prompt/1024-square/four-step/guidance call, with no image_paths for generation |
| Pass real reference file to edit interface | Pass, fake backend | Edit class receives the verified PNG path; changed original/reference prevents output commit |
| Durable output and genuine terminal state | Pass, offline | Partial files are not accepted; bad dimensions, quantization and peak limit reject; finished requires committed metadata and PNG |
| Cancellation, parent loss and recovery | Pass, owned synthetic process | Real stdin EOF exits worker; inherited production supervisor reaps before returning lease; final residency/swap guard also runs after cancellation; planned next edit recovers |
| Fixed trial budget/order/stop | Pass, offline | Six attempts, source-bound receipt, no repeat/out-of-order/failed predecessor; hash-bound visual review before next image |
| Native approval | Not granted | No actual trial approval receipt created; dummy receipts occur only in temporary unit-test directories |
| Native image quality/resources | Not run | Must be evaluated in the separately approved trial |
| Main/live unchanged | Pass | Frozen application/source/installed hashes and health checks; preservation record |

Evidence: `artifacts/photo-editing/prep-20261019/`. Source and operational notes:
`image_worker/editing/README.md`. Trial scope: `image_worker/editing/trial.json`.

## Changed files

- **Isolated worker:** `image_worker/editing/worker.py`, adapted from the existing
  production worker; the production copy is untouched. Select `Flux2KleinEdit`
  only for an explicit bound edit and supply one verified reference path.
- **Reference contracts:** actual PNG/JPEG decoding with existing Pillow,
  original/working copies, SHA-256, dimensions, orientation and stripped metadata.
  HEIC is outside this synthetic trial; future integration reuses the existing
  Mac codec and needs its own input/backup tests.
- **Controller:** reuse the production `Engine`, `Capacity`, inherited file lock,
  parent pipe and reaping. Require exact declared daily 32K chat residency;
  retain existing memory/swap/time/cache limits and monitor app health. Ordered
  reservations/results do not overwrite history. Each call returns for review.
- **Tests:** CPU image fixtures, native-module doubles that forbid actual native
  imports/network, contract/process/approval/budget tests. No existing test edit.
- **Docs:** this report, source/evidence manifests and explicit offline scope.
  No server, web, API, schema, dependency, prompt or default change.

## Deviations from SPEC.md

This checkpoint is preparation outside the production app. It does not introduce
a production image mode or new model call. Reuse the completed 726 Python /
126 frontend / 721 browser passes (three existing skips), with all 551 frozen
application/test/config hashes unchanged; these are prior results, not new full
suite runs. The new worker/control code is covered by its own offline suite.
No UI or browser source changes; no new full browser/build invocation is claimed.

The installed MFLUX 0.22.0 source supports `Flux2KleinEdit.generate_image` with
`image_paths`. Metadata/source inspection does not import MLX or load weights.
The private candidate copies only worker source and existing selectors; no
package installation or weight copy occurs. The app's configured product worker
remains unchanged. Human visual acceptance is separate from protocol success.

## Runtime observations

The CPU subprocess uses already installed Pillow 12.3.0. Synthetic native modules
stand in for Metal/MFLUX only inside the test driver. Fake peak-memory numbers
and step events test guards and are not measurements of the real edit engine.
Native-runtime sockets are refused during the final suite; no refused connection
attempt is recorded. Model names are not used to infer capability or admission.

The retained synthetic mug original and normalized working image total
**2,849,981 bytes (2.72 MiB)**. This measures that one reference pair only; future
portrait/output/revision storage must be measured natively. Every retained output
revision is a whole image. This trial creates no new generated or edited image.

## Test output

- First offline suite: 32 passed; expanded budget suite: 40 passed.
- Final suite: **84 passed in 11.49 seconds** — 47 preparation cases and 37
  existing image/residency cases, with native ports blocked.
- The preceding 82-case source/run is retained under `pre-postguard/`. Offline
  review found that expected cancellation bypasses the normal success-path swap
  check; add final residency/swap checks after reaping while still holding the
  lease, and a final health check. Two negative controls prove these gates also
  reject during cancellation. The final rerun resolves that concrete control risk.
- Ruff lint and formatting pass on all new Python files. Initial lint/format
  failures are retained; corrections are formatting, unused imports and deliberate
  guard-before-import placement, without relaxing test assertions.
- Privacy, frozen source and installed/live preservation checks pass.
- No new model call, package, image generation, runtime switch, service restart,
  deployment or production data mutation.

## Screenshots

No UI changed and no new native image exists to review. CPU fixtures are synthetic
colored images in temporary test folders; no personal photo, document, recording,
filename or transcript is captured. The existing release's synthetic UI evidence
is unchanged. No physical-phone or VoiceOver pass is claimed by this checkpoint.

## Open questions for Jake

AGENTS.md and the PE0 proposal require approval before native invocation. The
prepared request is **at most six worker calls**, using the existing installed
model/interpreter: one fictional adult portrait, background edit, oriented
non-square clothing edit, old mug recolor, cancellation and one planned recovery.
Freeze the generated portrait's hash after its one declared generation and bind
all dependent inputs before their calls; the retained mug hash is already frozen.

Keep the declared daily Qwen digest at 32K resident and the same 60-second,
24-GiB worker peak, 1-GiB cache, 512-MiB swap-growth and 2-second health bounds.
No chat-model probe, automatic unload, retry, favorable-seed selection, download
or live integration. A required failure or rejected visual review stops the trial.
Human quality acceptance is required before proposing PE1 in-chat integration.
