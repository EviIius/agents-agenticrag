# PE1-A report — durable photo-reference backend

19 October 2026. Isolated `codex/photo-reference-prep`; no app deployment.

## Summary

Implemented owned photo references, explicit pixel-edit execution, sanitized
exports, input retention/clearing and reference-aware backup/restore. Original
bytes are kept before HEIC conversion; references are pinned independently of
job lineage. Ordinary generation retains its original worker and payload.
This is the backend checkpoint: composer integration is PE1-B, and actual
product-worker qualification remains PE1-C. No new native model call was made.

## Done-when checklist

| Requirement | Status | Evidence |
| --- | --- | --- |
| Additive schema 14 / old rows unchanged | Pass | `test_migration_preserves_all_populated_v13_columns`; old migration projection/integrity checks, run twice |
| Explicit chat-owned reference upload | Pass, synthetic | `test_owned_upload_dedup_preview_and_private_original`; foreign-chat lookup/submission refused |
| Preserve original before HEIC conversion | Pass with mocked system conversion | `test_heif_raw_original_survives_copy_conversion`; original header bytes retained, working PNG separate |
| Real PNG/JPEG decode/orientation/limits | Pass, CPU only | `test_real_cpu_codec_orientation_resize_metadata_original_hash`, longest-edge and bomb/unreadable cases |
| Actual pixel path / no generation fallback | Pass with fake native modules | `test_product_edit_calls_pixel_class_and_actual_reference`; exact kwargs include image_paths; fallback rejected before model construction |
| Atomic acceptance, hash checks, retry pins | Pass | Atomic rollback, tampered-reference refusal, idempotent acceptance, retry and shared-inode assertions |
| Ordinary upload deletion cannot break an admitted edit | Pass | `test_removing_ordinary_upload_does_not_unpin_admitted_edit` |
| Cancellation / parent loss / lease ownership | Pass, owned fake processes | Codec cancellation/reaping, worker parent-death exit, edit cancellation reaps before lease release and final checks |
| Clear inactive input without deleting output | Pass | Active references refused; output survives clearing; old edit retry needs reattachment |
| Failed inputs survive housekeeping/restart | Pass | Pinned failed input retained beyond seven days; damaged original preserved until explicit clear |
| Queued/failed/cancelled input backup | Pass | One shared reference restored into three job bindings; missing blob removes partial restore |
| Completed edits / exports and older backups | Pass | Prior valid pair survives failed new backup; complete output restore and existing v1 backup regressions |
| Metadata-free exports preserve pixels | Pass | Native PNG retained; export copies unchanged IHDR/IDAT/IEND and excludes metadata chunks |
| Storage observations wired into preparation/execution | Pass, synthetic | Measured write barriers/timer, logical/inode/allocation totals, explicit observed-peak labels |
| Full checks / browsers | Complete; initial browser fixture failure repaired | `make-check.txt`: 745 Python / 126 frontend; `make-e2e.txt`: 720 pass, one fixture failure, three existing skips; corrected case passes both projects in `browser-focused.txt` |
| PE0/main/live preserved | Pass in preservation audit | Eleven frozen PE0 sources and 73 evidence files; live server/static/selectors and original generation worker |

## Changed files

- **Database/API:** additive `014_image_references.sql`, reference upload/info/
  preview/from-job/clear routes, optional chat reference ID, retry preservation,
  response projections and generated API types.
- **Image service:** owned reference files and CPU codec, atomic job pins,
  edit dispatch, sanitized export, resource/health/reaping guards, storage,
  recovery and version-2 reference backup companions. Old companions still work.
- **Isolated image worker:** new `reference_contract.py`, `reference_codec.py`
  and `edit_worker.py`; existing generation `worker.py` is byte-identical.
- **Tests:** synthetic backend cases, actual CPU Pillow and fake-native process
  controls. Migration tests now expect schema 14 while retaining old-column
  projections, integrity and foreign-key assertions.
- **Web:** generated types and defaults in existing design/test fixtures only.
  No new tool, button, composer behavior, screen or visual treatment yet.
  One browser test now isolates unrelated workflow notifications while its clock
  is frozen; all original send/draft/undo assertions and timeouts remain.

## Deviations from SPEC.md

None from the approved PE1-A scope. Optional image-reference fields are additive;
generation requests without a reference preserve legacy canonicalization and
old request-key replay. No prompt, sampling, model, package, runtime, port, bind,
service or Tailscale change.

Transport detail: the existing FastAPI multipart parser spools the upload; the
endpoint reads bounded chunks into a buffer capped at 20 MiB before writing and
fsyncing the owned original. It does not stream directly into the final reference
file or introduce a new multipart parser. Receive-size/headroom guards run before
multipart parsing, and the durable original exists before any conversion.

The companion format becomes version 2 only for reference-bearing data; ordinary
image backups remain compatible. Photo-containing backups use a unique suffix
so a failed companion cannot replace a prior valid database/manifest pair.
Damaged retained input is distinct from an explicit deletion: it remains counted
and recoverable instead of being silently removed at the next startup.

## Runtime observations

All model execution in this checkpoint uses fake modules/runtimes. Real Pillow
decodes synthetic PNG/JPEG in the existing isolated image interpreter, protected
against native imports/network. No weights are loaded and no MFLUX inference
occurs. System HEIC preservation is tested with a conversion double; actual
HEIC-to-edit execution remains a later qualification case.

Product editing admits only the exact PE0-qualified Qwen digest at 32K with the
unchanged resident-byte bound. Idle embedding release keeps its existing narrow
policy; other chat profiles are not automatically ejected. Empty residency is
currently unqualified for edits and should be evaluated explicitly at PE1-C;
do not require a permanent resident chat model without reviewing that usability
limit. Existing ordinary generation admission remains unchanged.

The unchanged safety limits remain 60 seconds generation/decode, 24 GiB native
MLX peak, 1 GiB cache, 512 MiB swap-growth margin and two-second app health.
Fake controls exercise rejection/cancellation; none of this establishes actual
product-worker speed, memory or likeness. PE0's six native results stay intact.

## Test output

```sh
make check
make e2e
server/.venv/bin/python -m pytest -c server/pyproject.toml image_worker/product/tests -q
```

The last command uses the already-installed private image interpreter for Pillow
inside controlled children. It intentionally is separate from the general server
suite, which does not require an image-worker installation.

- **Focused backend + offline worker:** 33 cases pass; 14 of these are actual CPU
  codec/owned-process tests with fake MLX/MFLUX. Separate final worker run:
  14 passed. No claim of 14 native image generations.
- **Full backend:** 745 passed; images 83.6% line coverage. All required module
  thresholds remain at 80% and pass. Frontend: 126 unit cases pass after updating
  fixtures to include additive response defaults.
- **Retained initial findings:** first full run exposed two remaining schema-13
  assertions; changed only the expected version to 14, retaining preservation
  checks. A later TypeScript check found omitted new fields in fixture objects;
  added generation/zero-byte/unavailable defaults without changing their UI.
- **Final combined check:** `make check` exits 0 on the frozen candidate: lint,
  formatting, types, coverage, 110 contrast pairs, generated API types, additive
  API guard, motion and privacy audit, plus all frontend checks above.
- **Additional review findings repaired:** reference availability updates now
  advance holder versions and publish SSE data; periodic storage sampling starts
  after capacity acquisition so a long queue cannot exhaust the sample budget.
  Dedicated regressions cover both.
- **Full browser invocation:** 720 passed, one failed, three existing skips in
  Chromium and iPhone-profile WebKit. The failure was the frozen-clock draft test
  encountering a workflow notification left by another test, before its first
  Send. Its trace/video is retained. Only that test's unrelated workflow snapshot
  is isolated, keeping every real send/draft/undo assertion and existing timeout.
  A fresh targeted invocation then passes **both projects, 2/2**. The original
  full invocation is not relabeled as an entirely green run. WebKit also passed
  the corrected case in the full run. No other browser failure occurred.
- Final product-worker lint/format passes for all five new Python files. The
  generation worker, frozen PE0 sources and original benchmark evidence remain
  unchanged; preservation results are in `preservation.json`.

## Screenshots

No new UI is delivered by A. Selected current-run synthetic regression screenshots
are under `artifacts/photo-editing/pe1-a-20261019/browser-screenshots/`. The full
fresh artifact run is preserved privately; `browser-archive.json` records its
paths/hashes and restoration of earlier committed evidence byte-for-byte.
No real photo, recording, filename, transcript or private conversation was used.
No physical iPhone or VoiceOver acceptance is claimed.

## Open questions for Jake

Review the backend checkpoint, then PE1-B connects **Edit photo**, the native
picker, reference tray, draft recovery and viewer comparison to these contracts.
Product-native validation is requested only after that concrete candidate exists;
the six-call PE0 budget remains exhausted. No main merge or deployment at A.
