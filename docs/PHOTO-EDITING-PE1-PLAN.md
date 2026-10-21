# PE1 — photo edits in the existing chat

19 October 2026. Prepared after Jake said “Continue” following the PE0 sample
review. This accepts advancing with the documented generative-edit limitations;
it is not a report that Jake individually verified every sample or metric.
PE0's six-call allowance is exhausted. This plan adds no native-test allowance.

## Product result

In the existing composer, choose **Edit photo**, select one photo and write the
change. The same conversation receives the edited image with real progress,
Cancel, save/share and **Show reference**. Seeds stay automatic. There is no new
tab, agent, vision-model helper or prompt-rewriting call.

The first version makes one 1024-square output from one reference. A visible
reference preview says that framing and unrelated details can change. Preserve
the original privately and keep every output as a whole image/revision. No
brushes, masks, promised likeness or exact-pixel-preservation claim.

Ordinary image generation keeps its 1/2/3 picker and existing request contract.
Ordinary photo attachments continue to mean “show this to the selected vision
model.” Attaching a photo never silently selects editing.

## Confirmed integration gaps

| Current code | Consequence for PE1 |
| --- | --- |
| `api/attachments.py` converts HEIC bytes and saves the PNG instead | A later attachment-ID lookup cannot recover the camera original. Edit uploads need to retain raw bytes **before** conversion. Do not pretend legacy converted attachments retain a HEIC original. |
| `ChatImageCreate.source_job_id` and job `parent_id` only describe lineage | Refine currently supplies text, not pixels. Keep lineage and reference identity distinct. |
| `images.prepare()` writes `{prompt, seed}` before the chat transaction | Reference files must become durable before acceptance; the transaction must pin them before scheduling. |
| `ImageCreate` also serves Gallery/workflows | Do not expose arbitrary references through a generic job request. Resolve chat ownership at the chat endpoint, then pass an internal prepared reference. |
| `images/backup.py` enumerates completed `image_artifacts` only | A queued, failed, cancelled or interrupted edit can need a reference even without an output. Backup must cover pinned references independently. |
| Existing Clear removes output artifacts, not input manifests | Adding retained photos without a separate accounting/clearing contract would hide storage growth. |
| `useChatImages` keys acceptance by prompt/count/seeds/source | Include reference identity in the signature and preserve it through rejection, navigation and retry. |
| Adding an optional Pydantic request field affects `model_dump()` | Preserve old idempotency canonicalization when the new field is absent; do not break replay of pre-PE1 request keys. |

Assessment is against main `c0d65ee0` plus the isolated PE0 preparation branch.
No production data was used for the analysis.

## A. Durable references and worker boundary

### Owned data

Use the next additive migration, **014**, from production schema 13. The stopped
agent branch is not a prerequisite. Add tables only; project every pre-existing
column before/after migration and migrate twice in a synthetic populated copy.

- `image_references`: opaque ID, originating chat ID, original/working hashes,
  byte counts, dimensions, normalization recipe/version, created timestamp and
  availability state. The chat ownership value survives chat deletion because
  Gallery outputs already survive it. Do not use a cascading chat deletion to
  remove files needed by surviving jobs.
- `image_job_references`: job → reference pins. Derive use counts from joins;
  avoid independently incremented counters that can drift on transaction failure.

Store raw original, normalized working PNG and normalization receipt below
`data/image-references/<opaque-id>/`, with private permissions. Jobs pin these
bytes rather than recopying each photo on every revision. Filesystem paths,
URLs and filenames are never accepted as an API reference identifier.

Deduplicate within an owning chat by original hash and normalization version;
do not make another conversation's reference usable by guessing a content hash.
If a worker needs job-local inputs, use owned read-only bindings (for example,
validated hard links) and account for shared inodes separately from logical paths.
No symlink-based escape or arbitrary-path argument.

### Upload and pixel preparation

Add `POST /api/chats/{chat_id}/image-references` for an explicit one-file edit
upload. Verify the chat, enforce the existing 20 MiB input bound and reserve disk
headroom before multipart consumption. Stream raw bytes to a private temporary
file; detect content instead of trusting extensions. Complete preparation before
returning a ready reference ID. Cancellation/failure removes incomplete staging.

For HEIC/HEIF, reuse the existing bounded system conversion on a copy while
preserving raw bytes. PNG/JPEG also need actual bounded decode, not just signature
checking. Use the installed image interpreter's Pillow in a CPU-only subprocess;
do not install Pillow in the application environment or import MLX to normalize.
Retain PE0's bounds: ≤100 megapixels decoded, EXIF transpose, RGB, working longest
edge ≤2048, no original EXIF/location data in the working PNG. Bound conversion,
normalization concurrency/time and reap children on cancellation/parent loss.
Version one edit inputs are PNG/JPEG and HEIC/HEIF through the existing conversion
path. GIF/WebP remain ordinary vision attachments; an explicit edit attempt gets
a clear unsupported-format message rather than a silent mode switch.

Do not promise recovery of pre-PE1 HEIC originals. An explicit edit of an already
converted attachment can use only the retained PNG and must label it as such.
Normal vision upload behavior and ordinary text-model payloads remain unchanged.

Add `POST /api/chats/{chat_id}/image-references/from-job` to explicitly copy a
selected available generated output into a reference owned by the target chat.
Validate the source through the existing authorized job projection/output hash;
never turn an existing lineage ID into pixel input implicitly. A reference ID
from a different chat remains invalid; this explicit copy is a new owned handle.

### Submission, retries and output

Extend `ChatImageCreate` with optional `reference_id`. It means edit mode and
requires `count=1` / one seed. Resolve ownership and availability while holding
the existing chat lock and image lock. Revalidate original/working hashes before
admitting work. The message/job/reference pin transaction is atomic. A failed
transaction leaves neither scheduled work nor a claimed attachment.

Keep legacy `{prompt, seed}` generation manifests and old-key canonicalization
unchanged when reference_id is absent. An edit has an explicit internal mode and
complete hash-bound descriptor. The worker independently validates that descriptor
and supplies the actual working image to `Flux2KleinEdit`; no text-only fallback.
Keep lineage separate. Retry must bind the same reference and new user-requested
seed, and refuse unavailable references with a reattach explanation.

Preserve all eleven frozen PE0 executed files and evidence. Build the product
adapter separately, reusing the tested checks. Keep generation argument equality,
actual 0–4 denoising events, parent-death watch, capacity lock, reaping before
release and resource guards. The edit qualification is the exact PE0 chat digest
at 32K, not a model-name rule or automatic qualification of every generation
profile. Keep limits: 60 s generation/decode, 24 GiB MLX peak, 1 GiB cache,
512 MiB swap-growth margin and ≤2 s app health. No additional automatic eviction.

Keep native output and hash/provenance separately from a metadata-stripped export.
An engine PNG is not already a safe export simply because its input was stripped.
Validate exported pixel equality and sanitized chunks; previews/save/share must
use the approved export, while native evidence remains intact and private.

### Backup, cleanup and storage

Version the image companion manifest to cover both completed output artifacts
and all retained reference pins from the database snapshot, including edits with
no output. Cover original, working copy and receipt hashes; deduplicate blobs.
Continue reading/restoring old manifests. Backup/prune/restore must validate the
same database/reference graph, refuse corrupt/missing blobs and roll back a failed
restore into a new directory. No restore into the running data folder.

Use the existing image lock around the snapshot and companion copy. Include
reference bytes in disk admission and backup headroom, plus sanitized export
copies where separately retained. Do not count only successful output PNGs.

Failed/cancelled/interrupted edits retain their pinned inputs for explicit retry.
Startup must not clean those references as unsent uploads. An unclaimed edit
upload can expire with other unfinished unsent attachments after seven days.
Deleting an ordinary composer attachment cannot invalidate an admitted edit.

Expose separate input/output/metadata/backup totals and an explicit confirmed
**Clear inactive photo inputs** action. Never clear an active job's reference.
Keep completed output PNGs; mark cleared references unavailable, disabling their
comparison/retry with a reattach explanation. Do not silently repurpose the
existing output-only Clear operation. Shared references are deleted only after
checking every holder under the same lock.

Instrument storage from before staging through cleanup: periodic bounded samples
and samples at durable write/rename/deletion barriers. Report observed logical
high-water, unique-inode bytes, kernel allocation, sample count/gaps and final
retained bytes separately. Do not call st_blocks a measure of APFS shared extents
or claim a proven absolute peak. The PE0 peak-storage omission remains historical.

## B. Existing composer/cards/viewer

- Tools → **Edit photo** opens the native picker directly. Show one reference
  thumbnail inside the existing tray and keep the same text box/Send/Cancel.
- A concise note explains fixed square output and possible changes to other
  details. No new seed requirement, settings page or workspace.
- Distinct draft state holds reference ID, text and mode per chat/new draft.
  Switching chats, failed submission and switching tools preserve the correct
  draft. An upload in ordinary chat does not switch to editing.
- Existing generated-image actions gain **Edit image**. Existing Refine keeps its
  current text-generation meaning until the user explicitly chooses pixel editing.
- Image turns show Edit/Generate identity and a **Show reference** comparison in
  the existing viewer. Preview the normalized reference with metadata stripped;
  label any normalization/framing honestly. Keep originals private.
- Reuse SSE/rAF progress, waiting animation, viewer, motion limits and save/share.
  Respect both reduced-motion paths. No UI polling or appended message notices.
- Image turns and reference attachments used only for editing remain outside
  text-model context. Verify ordinary text/vision requests byte-for-byte.
- Add ready/preparing/upload-error/unavailable-reference/running/cancelled/
  complete/comparison/rejected-send states to `/design` at phone/desktop widths.

## QA and stop boundaries

**A: backend/worker/storage checkpoint.** Fake runtimes and CPU-only synthetic
files prove additive migration/old-row preservation, old API/idempotency replay,
cross-chat refusal, actual reference binding, hash corruption refusal, no silent
generation fallback, atomic acceptance/rollback, cancellation/reaping, active
reference deletion refusal, retry retention, restart cleanup and shared ownership.
Backup round-trips must include queued/failed/cancelled edits as well as outputs;
missing/corrupt reference blobs fail restore without leaving a partial destination.
Generation payload and old companion compatibility remain required.

**B: composer/full regression checkpoint.** All UI states, desktop/phone synthetic
screenshots, reduced motion, rejected-send/draft ownership, switching chats,
batch generation, file upload, exact ordinary text/vision context and SSE behavior.
Run make check / make e2e, including API-growth and old-row guards. Preserve all
failures; prompts/providers/sampling remain unchanged, so no new factual-answer
experiment is implied.

**C: product-worker qualification, then release.** The product adapter differs
from the frozen PE0 worker. Its native validation needs a separately reviewed,
bounded request after A/B produce a concrete candidate. Include actual CPU
HEIC decode, reference pixels, sanitized exports, peak-storage observations,
controls and the qualified chat residency; no unbounded retesting or helper call.
No PE0 seventh call is authorized by this plan.

Only after passed gates should a merge/publication be proposed. Rehearse new and
previous binaries on copied data, including queued edit jobs and schema 14. An
old binary must not silently resume an edit as plain generation; quiesce/reap
jobs and prove rollback handling before release. Preserve the original app/data/
plist fallback and current messages/inputs. Keep port 8787, bind, service and
Tailscale unchanged. Request the physical iPhone upload/edit/reference/save/share/
cancel check after an approved release; do not invent that acceptance now.

## Scope exclusions

No extra package, weight, runtime upgrade, default/model switch, chat prompt,
planner, image-description helper, agent, Research restart, masks, brushes,
multi-reference composition or workflow editing block. Remaining workflow blocks
are separate work. This plan changes no installed application files.
