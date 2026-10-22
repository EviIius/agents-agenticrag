# PE2 masked-editing report

Started 21 October; closed 22 October 2026. Isolated branch:
`codex/masked-photo-editing`. Main and the installed application are unchanged.

## Summary

Brush selection, compositing and durable retry/backup support are implemented.
The independent CPU checker verifies that the result is the exact composite of
the admitted reference, native output and mask before promoting an output.
Both authorized native jobs pass protocol, preservation and resource checks.
**The private hat/two-glove result fails quality review and is not approved for
release.** Preservation and generated-content quality are separate findings.

## Done-when checklist

| Item | Status | Evidence in `artifacts/photo-editing/pe2-20261021/` |
|---|---|---|
| Brush, size, Undo, Clear, Apply/Cancel | Pass | `browser-final.log`: Chromium and WebKit, pointer/keyboard checks |
| Draft/send ownership and rejected-send replay | Pass | New browser checks plus existing photo-edit functional checks; same request/selection retained |
| Exact unselected pixels, original prepared proportions | Pass | `offline-final.log`; actual native proof; private face-region comparison |
| Independent rejection of a changed protected pixel, even with an updated file hash | Pass | Actual CPU checker test in `test_masked_edit.py` |
| Bounds, malformed selection, cross-chat refusal | Pass | CPU tests and `test_masked_photo.py` |
| Retry retains the same selection | Pass | API and browser checks |
| Raw FLUX PNG, composite, export retained/accounted/backed up | Pass | API backup/restore/removal test; `native_bytes` accounting and backup disk headroom |
| No schema/dependency/runtime/default change | Pass | Existing JSON manifests store the selection; dependency files untouched |
| App checks and initial JS | Pass | Full `make-check-final.log`; `bundle.json`: 255,966 / 256,000 gzip bytes |
| Native scope respected and live app preserved | Pass | Two launches only; `native-result.json`, `native-source.json`, `preservation.json` |
| Hat and both gloves match the requested edit | **Fail** | Private review: clipped initial cap, incomplete gloves; diagnostic improves cap but does not satisfy the full request |
| Merge/publication | **Not performed** | Quality review remains open; branch/draft PR only |

## Changed files

- **Server:** `schemas.py`, `api/chat_images.py`, `db/image_jobs.py`, image job/
  codec/output validation/backup code and backup headroom. Selections are bounded
  normalized strokes, saved in the existing admitted request and retry params.
- **Worker:** `masked_edit.py`, edit/reference worker integration; installer adds
  the fifth reviewed CPU module. The ordinary generation worker stays unchanged.
- **Web:** lazy brush dialog, photo draft/submission state, reference-tray controls,
  portrait frame proportions and raw-native storage totals. Fixtures expose the
  selection state and working dialog in `/design`.
- **Tests:** masked API/backup cases, real CPU/native-double worker cases, brush
  browser cases and updated typed fixtures. No user image is a test fixture.

## Deviations / boundaries

The installed klein editing API does not accept a generation mask. This version
fits a cropped context onto the unchanged 1024-square inference canvas and
composites only admitted selected pixels onto the prepared reference. It is
**not mask-aware denoising**. An accessory placed elsewhere in the raw result can
therefore be clipped by the selection. The UI tells users to include space for
additions; that does not make the model obey a mask it never sees.

The retained normalized RGB reference, longest edge ≤2048, is the preservation
baseline. Full original bytes stay private; camera-resolution/EXIF preservation
is not claimed for the output. A 3-pixel Gaussian blend is multiplied by the hard
mask, so blending cannot change unselected pixels. Outputs retain those prepared
dimensions. Legacy whole-photo edits and ordinary generation keep their previous
1024-square behavior and canonical request identity when selection is absent.

No database migration is required. Raw native PNG is additional output storage,
covered by cleanup, backup/restore, hash checks and backup headroom. A future
publication needs the PE2-aware backend plus all five worker files; reverting to
the PE1 backend can discard selection on retry and is not a safe fallback.

## Runtime observations and actual trial

Exactly **two native invocations**: one synthetic, then the supplied private
original with the user's exact prompt and fixed seed 42. No preload, auxiliary
model call, regeneration, new weight or package was used. The ordinary resource
guards and production shared native lock were retained; the model slot was empty.

| Case | End-to-end seconds | Output | Protected pixels | Changed outside selection | MLX peak | Swap growth |
|---|---:|---|---:|---:|---:|---:|
| Synthetic | 21.035 | 768 × 1024 | 744,543 | 0 | 18,659,198,390 bytes | 0 MiB |
| Private | 23.053 | 1536 × 2048 | 3,093,481 | 0 | 18,659,198,390 bytes | 0 MiB |

Both real 0–4 denoising sequences and worker reaping pass. Health samples,
observed storage/sampling gaps, raw/composite/export sizes and source hashes are
retained in `native-result.json`; these are observations, not a proven absolute
APFS peak. Native worker source remains frozen byte for byte. The exact executed
controller includes a private task/selection and is retained privately with its
hash recorded; the public controller is explicitly a sanitized template.

### Quality findings

The first cap mask was too small and clips the hat. This is a selection error,
not evidence that FLUX cannot draw a cap. A **CPU-only diagnostic** expands the
composite selection using the same retained FLUX pixels and original generation
transform; most of the cap reappears without a model call. It remains a separate
diagnostic, not a replacement native pass. Glove coverage/placement is incomplete
and boundaries remain imperfect. The full two-glove request is not met.

The face-region pixels in the original trial are exactly equal to the prepared
source. That is stronger than a visual likeness claim, but it does not qualify
the generated accessories. One private task cannot establish a general model
ranking. See `quality-review.json` and the private review page opened locally at
`http://127.0.0.1:8768/review.html`.

## Test output and retained failures

- Full **make check: 773 Python / 132 frontend tests pass**, with 110 contrast
  pairs, lint/types/format/API/motion/privacy gates and **83.1% image coverage**.
- **26 offline worker checks pass**, real Pillow/process validation with native
  inference replaced; no hidden GPU invocation.
- **18 focused browser checks pass** in Chromium/WebKit, plus **two preview-load
  failure checks** after exposing that state in `/design`; final frontend checks
  also pass all 132 tests. A full `make e2e` was
  not repeated; this is focused coverage, not a new full-browser-suite pass.
- Initial browser run: 14 passes, four failures. Selection buttons were submitting
  the containing form; explicit button types fix the product bug. Tests now type
  an instruction before opening the selector and retain their assertions.
- Initial full check: 772 passes, one failure. The new backup test selected an
  unrelated automatic startup DB without the intended image companion. It now
  selects its uniquely paired backup at the declared test clock; all byte/hash
  restore assertions remain. Initial logs and final results are both retained.
- The previous tracked coverage artifact is restored; new coverage lives with
  this checkpoint. Earlier trial evidence, native ledgers and user documents are
  untouched. Private images, masks, raw task text and filenames remain outside Git.

## Screenshots

Synthetic phone brush views: `browser/mask-390-{light,dark}-{chromium,webkit}.png`.
Only synthetic pictures appear in repository screenshots or traces. Private
original/native/composite/diagnostic images are in the private review directory.

## Next step / review boundary

Keep the tested selection/compositor foundation isolated and do not publish the
current content-quality result. `PHOTO-EDITING-PE2-NEXT-CANDIDATE.md` recommends
evaluating **Qwen-Image-2.1**, whose installed-engine implementation can apply the
mask during denoising. Its ~33.13 GB component download, research license, actual
Mac memory and latency need a named reviewed trial; no such installation or
extra native invocation occurred. FLUX Fill and larger general editors are
documented alternatives, not assumed upgrades.
