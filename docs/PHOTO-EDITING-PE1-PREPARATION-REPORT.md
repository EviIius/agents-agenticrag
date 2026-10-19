# PE1 preparation report — 19 October 2026

## Summary

Jake said “Continue” after the PE0 six-call result and quality-review request.
Advance with the documented generative-edit quality limitations; do not invent
individual sample checks by Jake. The concrete PE1 integration plan is now
grounded in the actual composer, job acceptance, upload, cleanup and backup code.
The missing storage-observation helper is prepared and tested offline.

## Done-when checklist

| Item | Status | Evidence |
| --- | --- | --- |
| PE0 review continuation | Recorded | User's “Continue”; AGENTS.md amendment |
| Concrete reference ownership/API/worker/UI/backup plan | Prepared | `PHOTO-EDITING-PE1-PLAN.md` |
| HEIC original-loss and backup gaps | Confirmed in code | `api/attachments.py`, `images/backup.py`; analysis in plan |
| Old idempotency/generation context compatibility | Included as required gates | Existing canonical request construction, useChatImages signature and exact-context tests |
| Missing storage instrumentation | Prepared offline | `image_worker/editing/storage_measure.py` |
| Storage helper tests | Pass | Nine synthetic tests: transient high-water, rename, hardlinks, nested files, symlinks, sample bound and metadata |
| Native count | Unchanged at six | Original launch journal/hash and source-preservation evidence |
| Product/API/schema/UI | Not changed in preparation | Production source hashes match accepted main; no migration or endpoint yet |

## Changed files

- **Isolated helper/tests:** storage accounting of per-path logical bytes,
  unique-inode bytes, kernel allocation, observed peaks and sample gaps. No file
  contents, filenames or paths are emitted; no model imports/calls.
- **Docs:** PE1 plan, this H4 report and user continuation record.
- **Production server/web:** none. All eleven executed PE0 files remain frozen.

## Deviations from SPEC.md

No new product behavior or native invocation. The helper is a prospective fix,
not retroactive measurement of PE0's missing disk high-water. Keep the original
report and six outcomes unchanged. Observed peak samples are explicitly labelled
and do not claim a mathematically exact peak or APFS physical extent accounting.

## Runtime observations

Read-only preservation/health checks only. No package, weight, image-worker,
chat-model, embedding, runtime-load or unload operation. Existing failed agent
experiments and Research remain stopped.

## Test output

- Nine new synthetic storage checks pass on the final formatted helper.
- Ruff lint/format and privacy/diff checks pass; initial formatter findings are
  retained in preparation evidence and repaired without altering frozen PE0 code.
- Existing complete suites and native measurements are not rerun or relabelled.
  Production/UI source is unchanged; no new full application/browser pass claimed.

## Screenshots

No UI was changed. Retain the actual PE0 comparison gallery and its desktop/phone
screenshots under `artifacts/photo-editing/native-20261019/`; no private media or
new fake product screenshots were captured.

## Open questions for Jake

The PE1 plan is the concrete scope for the next implementation checkpoint:
durable references/backup/worker first, then composer/full QA. This preparation
does not publish photo editing. The exhausted PE0 budget does not authorize a
new native validation call for the eventual product adapter. Native validation
and release remain later concrete review steps after the candidate exists.
