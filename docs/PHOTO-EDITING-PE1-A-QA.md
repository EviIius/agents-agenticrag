# PE1-A QA analysis

## What was checked

This checkpoint verifies the new backend using synthetic files and fake model
runtimes. It does not claim native product-worker quality, timing, memory, HEIC
editing or phone acceptance. The existing six-call PE0 record is preserved.

| Risk | Evidence / test | Result |
| --- | --- | --- |
| Another chat supplies a guessed reference ID | Owned upload/info/preview and cross-chat submission tests | Refused; explicit from-job copy creates a new owned handle |
| A filename changes format handling | PNG content uploaded under a different extension; HEIF content under a PNG name | Content drives preparation; filenames are not stored in reference records |
| Original photo disappears during conversion | HEIF conversion double, raw original hash/byte assertions | Original and normalized working input are separate |
| PNG/JPEG signature passes despite invalid pixels or excessive dimensions | Real CPU codec invalid/bomb/orientation/resize tests | Actual decode required; bounds and metadata stripping enforced |
| An edit silently becomes plain generation | Product worker fake-native driver and exact kwargs check | Explicit edit class plus actual image_paths; missing reference/generate mode rejected |
| Acceptance commits messages but loses files/pins | Late FK failure injected into acceptance batch | No message/job/pin is accepted or scheduled; ready unclaimed reference survives |
| Input changes between preparation and use | Reference hash and receipt tampering tests; worker checks before/after its fake generation | No accepted output from changed input |
| Deleting an ordinary attachment breaks admitted work | Upload removal test with a queued edit | Owned reference remains intact; edit completes with fake engine |
| Retry selects a new source or repeats a request unexpectedly | Chat request-key and branch tests, same reference pin assertions | Source identity retained; duplicate request replays rather than schedules twice |
| Stop releases resources before the child exits | Actual owned fake process cancellation, PID absence and capacity assertions | Child reaped while lease held; post-reap residency/health checks verified in event order |
| Server/parent loss leaves a runaway worker | Parent-pipe closure in product fake-native process | Exit 71, no completed output |
| Clearing shared inputs breaks another active job | Shared reference joins and active-clear refusal | Active pins block clearing; completed outputs remain downloadable |
| Client shows stale availability after clear/reattach | Timestamp and persisted SSE assertions | Availability changes advance the job version and publish updated reference state |
| Seven-day cleanup removes retryable input | Failed pinned input predating expiry; startup recovery | Pin protects input; damaged originals remain until explicit clear |
| A backup covers outputs but misses pending inputs | Queued/failed/cancelled shared-reference restore | All three job bindings restored from one reference entry |
| A failed backup replaces a valid one | Corrupt working input before second photo backup | New incomplete pair removed; prior valid pair remains restorable |
| Restore accepts missing/corrupt blobs | Missing input blob and existing image corruption regressions | Restore fails and removes the partial destination |
| Output carries camera/engine metadata | Synthetic PNG metadata chunk and exact export-byte assertion | Native file retained; exported critical pixel chunks unchanged, metadata excluded |
| Storage hides original/working/export data | API counters, shared-inode assertions, per-case storage observations | Categories separated; observed peaks are not claimed as exact APFS physical usage |
| A long queue exhausts the diagnostic sample budget | Blocked-capacity regression with sampler entry assertions | Initial/final observations retained; periodic sampling starts only when capacity is acquired |
| Schema addition changes existing rows | Populated v13 and older migration projection tests, integrity/FK checks and second migration | Existing columns remain unchanged; version advances to 14 |
| Existing generation/text/vision breaks | Existing complete suites and exact ordinary-chat payload/context tests | See final command logs; no generation-worker or prompt changes |

## Findings repaired during this checkpoint

1. **Schema-version assertions:** two older tests still expected 13. The database
   correctly reached 14; their old-column, integrity and FK checks remain.
2. **Generated response types:** design/test fixture objects omitted the added
   required response defaults. Generation mode/zero bytes/unavailable edit support
   are now explicit in those fixtures; rendered controls are unchanged.
3. **Availability push updates:** manual review found that a reference could be
   cleared/reactivated without advancing job.updated_at. Clients merge on that
   version, so they could ignore an otherwise valid SSE event. Availability and
   holder timestamps now update together; upload/clear publish current job data.
4. **Incomplete photo-backup exposure:** photo bundles receive unique names and
   failed new pairs are removed, preserving an earlier valid backup.
5. **Damaged versus deleted input:** corruption no longer means an implicit
   deletion at next recovery. Recoverable originals remain counted until an
   explicit clear; backup reports a failure if the retained graph is incomplete.
6. **Long queue sampling:** review found periodic storage samples could use the
   bounded sample budget while waiting for another native task. Queuing makes no
   temporary output writes. The initial observation stays; periodic samples now
   start after capacity acquisition, before execution/staging, with final cleanup
   observations retained. A blocked-capacity regression proves the order.
7. **Frozen-clock browser fixture:** the Chromium long-paste test stopped at its
   first Send click, before its draft assertions. The trace shows a paused
   workflow notification from a previous shared-database test covering Send; the
   frozen clock prevents its expiry. That single test now supplies empty workflow
   snapshots, leaving its real message/upload transport and all draft/undo/request
   assertions intact. No force-click, timeout increase or product change is used.
   The initial trace/video and subsequent focused results are retained separately.
   This does not claim to repair notification placement in the product; check
   normal-clock notification placement alongside the composer at PE1-B.

The failed and intermediate logs remain under
`artifacts/photo-editing/pe1-a-20261019/`. Targets were not reduced and original
benchmark reports, native trials and production files were not rewritten.

## Final results

- `make check` exits 0: 745 Python tests, 126 frontend tests, all coverage gates
  (images 83.6% against 80%), 110 contrast pairs, types, lint, formatting, API
  compatibility, motion and privacy checks.
- 19 focused reference cases and 14 additional CPU/fake-worker controls pass.
  They do not represent native GPU inference.
- The complete browser invocation reports 720 passed / one fixture failure /
  three existing skips. The isolated frozen-clock case then passes 2/2 in a
  fresh Chromium/WebKit invocation. Preserve the original full failure; it is
  not rewritten as a green invocation.
- No product UI behavior, prompt, sampling, dependency, model, runtime, main or
  installed application change. Native PE0 remains exactly six invocations.

## Interpretation and remaining gates

The tests establish file ownership, storage/transaction behavior, fake-runtime
request contracts and control boundaries. Mocked inference cannot establish
product edit quality or GPU resource use. Real Pillow tests establish only the
CPU codec behavior they exercise; the HEIF preservation unit uses a converter
double, so complete HEIC editing remains unqualified.

PE1-B must connect the existing composer and viewer, including draft recovery,
reference comparison, clear-input affordances, one-image edit mode and explicit
framing expectations. PE1-C needs a separately approved bounded native product
trial and later release/phone checks. Empty chat residency is deliberately not
yet qualified for edits and needs review before publishing a convenient flow.
Clearing inactive live inputs does not erase copies in retained backups; the
existing backup retention/pruning policy still applies. The UI must distinguish
those storage categories when presenting the clear action.

The browser run may log viewport-change ViewTransition rejections during resize
tests. Preserve these logs and assess any test failure; do not claim zero console
warnings or that PE1-A fixed existing transition code. No transition implementation
was changed in this backend checkpoint.
