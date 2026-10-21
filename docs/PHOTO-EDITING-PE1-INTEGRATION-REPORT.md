# PE1 integration preparation report

21 October 2026. Isolated `codex/photo-reference-prep`, draft PR #6.

## Summary

Jake accepted the reported generative-edit tradeoffs and authorized integration
preparation. The product now admits the exact native-qualified empty-slot or
strict 32K arrangement. The worker installer and private app/data/plist bundle
preparer are implemented, with a schema-aware compatibility fallback rehearsed
on synthetic copies. Main, the installed application and native-test allowances
are unchanged. The complete regression and preservation gates pass. Preparation
is complete on the isolated branch; publication remains a separate decision.

## Done-when checklist

| Item | Status | Evidence under `artifacts/photo-editing/pe1-integration-20261021/` |
| --- | --- | --- |
| User quality acceptance | Accepted 21 October, generative limitations retained | AGENTS.md amendment; no exact-likeness claim |
| Promote only tested empty/strict-32K admission | Pass | Full Python checks; `guard-parity.json`, 217 frozen-policy comparisons |
| Installer supplies generation/edit/CPU files, preserves selectors | Pass | New release-preparation tests; byte-equal staged worker files |
| Busy native lease, selector/symlink refusal, interrupted-copy recovery | Pass | `test_photo_release_preparation.py`; no runtime/weights execution |
| Private candidate/original data/plist/source archive | Prepared | `bundle-rehearsal.json`, 2,322 hashed files; private bundle only |
| Old UI + current backend/worker, retained current data | Rehearsed | Candidate/compatibility child runs; post-candidate chat/input retained |
| Queued edit recovery and explicit retry retain reference | Pass, fake execution | Capture installed before startup; no silent generation |
| Actual CPU HEIC normalization through staged installer | Pass | `candidate.txt`; CPU-only subprocess allowlist and reaping |
| Paired DB/image/reference restore | Pass | One output, four pinned jobs; original/reference/output bytes retained |
| Schema 13→14 startup preserves original chat | Pass | `baseline13.txt`, `upgrade13.txt`; actual staged imports |
| Full checks | Pass | 759 Python / 132 frontend / 110 contrast, images coverage 83.6% |
| Full Chromium/WebKit suite | Pass | `make-e2e.txt`; 739 passed, three existing skips |
| Prior evidence/source/live identity and exhausted budgets | Pass | `preservation.json`; historical artifacts restored after archiving |
| Main merge/publication/physical phone acceptance | Not performed | Separate review after preparation |

## Changed files

- Server: `images/engine.py` admits the measured empty slot alongside the strict
  known digest/context/size combination; its error copy describes both options.
  `test_photo_references.py` covers allowed and rejected arrangements.
- Tooling: `install_image_worker.py` installs four reviewed public files under a
  native lease, preserves matching selectors and restores prior named files on
  the tested copy failure. `prepare_photo_release.py` prepares/verifies only; it
  cannot publish. `deploy.py --apply` refuses this source's migration-014 path
  before service inspection/mutation, preventing the old generic procedure from
  bypassing the combined worker/reference/fallback contract.
- Tests: `test_photo_release_preparation.py` exercises installer failure/lease/
  selector protection, snapshots, source races, corruption and fallback integrity.
- Docs: authorization, release runbook, this H4 and synthetic evidence. No web,
  image-worker model code, prompt, dependency, runtime or default was changed.

## Deviations from SPEC.md

The user-approved PE1 scope and passed four-call native matrix refine the old
single-resident edit guard. The product policy is equivalent to the frozen tested
candidate across 217 host cases; this does not qualify arbitrary other models,
64K/multiple profiles or different memory limits.

The original generic deployment backup/fallback path cannot protect retained
photo inputs or prevent old-server reference loss. It is explicitly blocked for
this source. The reviewed runbook retains the schema-aware backend/new worker
and current data while restoring the previous UI. **Full old-backend rollback
on schema 14 remains unsafe and unqualified.** Backend startup failure requires
preserving current data and a schema-aware repair, not an old DB overwrite.

## Runtime observations

The actual staged candidate and compatibility app are imported from their own
payload paths, using unchanged existing dependencies. Both operate on the same
synthetic current-data copy: a new chat and HEIC reference created after the
candidate starts still exist after the compatibility switch. The previous
compiled UI changes, but its backend stays byte-identical to the candidate.

A configured worker causes accepted queued jobs to resume on startup. The
corrected rehearsal installs a reference-aware fake capture before startup,
proves that the queued edit dispatches `run_edit` with its bound original, then
checks explicit retry. These captures deliberately fail without native work;
they are not generation results or new model calls. Earlier C preparation with
no configured worker correctly observed interruption instead. Both behaviors
are retained; no product restart policy was changed to satisfy the rehearsal.

The installed codec handles an actual synthetic HEIC upload on the staged app.
Only system `sips` and the CPU reference codec may spawn; network/model execution
is forbidden. The paired backup restores one completed output and all four
reference pins, including failed/cancelled/queued inputs. Restored job manifest
JSON has equivalent values with canonical key ordering; its byte formatting can
differ. Original/working photos, receipts and image outputs remain byte-identical.

## Test output

`make check` passes: **759 Python**, **132 frontend**, **110 contrast pairs**;
all app/test lint, formatting, types, coverage, motion, privacy and API-growth/
API-type gates pass. Image coverage is **83.6%**, above the unchanged 80% floor.
The focused admission/installer/preparer run passes 33 tests before the full run.
New scripts pass their own Ruff check. Three overlong literal strings were split
without changing their ASTs after the full checks; both formatting-equivalence
receipts are retained and the final bundle verifies again.

Full `make e2e`: **739 passed, three existing skips**, in 1.2 hours. All 18
photo-editing cases pass across Chromium and WebKit, including the previously
corrected image-upload selectors. There are no failed tests in this invocation.
The raw log retains eight ResizeObserver warnings, also observed eight times in
B's earlier log. Their cause is unproven; this is not a clean-console claim or a
physical iPhone pass. See `console-observations.json`.

The new run archives 1,702 changed/new synthetic artifacts privately and restores
all 1,662 overwritten tracked historical files. Five selected screenshots and
the final coverage report accompany this checkpoint. Preservation verifies 574
current source files, 577 frozen C files, 572 B source files, 922 B evidence
files, 52 C-preparation and 47 C-native evidence files. Main's 551 source files,
114 installed server files, 425 installed static files, 429 candidate static
files, installed worker/selectors and original service plist remain unchanged.
PE0 and stopped agent evidence/ledgers also verify. Native calls this checkpoint:
**zero**. Local and normally verified HTTPS health pass; Ollama remains 0.35.0.

### Retained preparation failures

- Initial `make check` stopped at one overlong synthetic SQL test string. Its log
  is retained; the corrected complete invocation passes all gates.
- The first bundle rehearsal attached its fake engine after startup, wrongly
  expecting queued edits to be interrupted with a worker configured. The socket
  guard stopped a metadata connection and no native worker was launched. The
  corrected capture is installed before app creation and proves reference-bound
  resume instead. Original source/log/data copy are retained.
- The next rehearsal incorrectly supplied `title` to ChatCreate. The API correctly
  returned 422. The harness now uses create then the existing PATCH; no product
  API was loosened.
- The restore projection initially required raw byte equality for job input JSON.
  Four manifests differ only in key formatting and retain identical parsed values.
  The final projection requires semantic equality for those manifests and exact
  bytes for originals/working images/receipts/outputs. All earlier artifacts remain.
- Separate script-lint outputs retain the literal-line findings and formatting
  correction; no product behavior was altered by those corrections.

## Screenshots

No new UI surface was introduced. Five selected synthetic attachment/chat-image/
workflow screenshots from the completed run are in `browser-screenshots/`; the
complete changed-artifact archive is private. Historical screenshots are restored
byte-for-byte. Existing native sample images remain frozen, and Jake's private
photo is never used or copied into integration evidence. Codex inspected the
selected WebKit image state; this is a design fixture, not physical-phone review.

## Open questions for Jake / release boundary

The browser gate and preservation archive are complete. The private rehearsal
bundle is not a production recovery snapshot. A fresh
quiesced production bundle, merge/publication approval and then physical iPhone
verification remain required. See `PHOTO-EDITING-RELEASE-RUNBOOK.md` for the exact
future boundary and compatibility fallback limitations. No new native call,
automatic model unloading, agent, scheduler or watcher is authorized.
