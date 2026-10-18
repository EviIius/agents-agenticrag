# Photo-reference editing — next checkpoint proposal

18 October 2026. Design only; no native execution or product integration is
approved by this document. This refines the PE0/PE1 section of
`HERMES-AND-PHOTO-EDITING-PLAN.md` using the pinned code already in this repository.
The two production follow-up repairs stay a separate release decision.

## What should be built

Upload one photo in the existing composer, choose an explicit edit action, type
what to change, and receive the edited image in that conversation. Keep the
original available for comparison, automatic seeds and existing save/share.
No new agent, text-model helper, download or framework is needed for this path.

It must be visibly different from describing a photo to a vision model and from
current Refine, which changes the prompt without supplying reference pixels.
Avoid a new workspace/tab. Do not infer a tool or model from its name or silently
switch ordinary chat attachments into editing.

## Confirmed existing implementation

| Boundary | Current code and consequence |
|---|---|
| Production generation | `image_worker/product/worker.py` instantiates `Flux2Klein`; `generate_image` receives prompt/seed/settings only. It has no reference-pixel argument. |
| Earlier isolated edit | `image_worker/memory/worker.py` imports `Flux2KleinEdit`, chooses it for edit mode and supplies `image_paths`. The prior single successful mug recolor is feasibility evidence, not portrait qualification. |
| Accepted image job inputs | `server/app/images/jobs.py` persists only prompt and seed; parent ID establishes lineage, not input pixels. |
| Chat API | `source_job_id` maps to lineage. It does not make a generated image or uploaded photo an engine reference. |
| Uploads | Existing content detection/HEIC conversion is reusable. The codec path bounds size/dimensions and normalizes output; do not bypass it or treat every PNG extension as PNG content. |
| Backup | Current image companion backup enumerates completed output images. New retained reference inputs need their own manifest/restore coverage. A saved database alone is insufficient. |

Source snapshot for this assessment is main `e7ffea2b`; no installed code was
changed. Use installed MFLUX 0.22.0 and FLUX.2 klein 4B revision
`e7b7dc27f91deacad38e78976d1f2b499d76a294`, 8-bit components, 1024-square output,
four steps, guidance 1.0 and the existing 1 GiB unused-allocation cache limit.
Newer external package behavior is not assumed.

## PE0: isolate the edit worker before app integration

Prepare and test an isolated worker/control harness first, without inference.
Its manifest distinguishes generation from editing, owns all paths and refuses
missing/invalid reference input. Preserve current generation behavior exactly;
no silent text-only fallback. Reuse actual progress events, stdin parent-death
watch, shared Capacity lease, cancellation/reaping and pinned model validation.

A proposed native trial is **at most six worker invocations**, no text-model calls:

1. Generate one fixed synthetic adult portrait for a private synthetic fixture.
2. Edit only its background using the frozen portrait bytes.
3. Edit only its clothing color, again from the original portrait.
4. Repeat the earlier synthetic mug recolor from the retained original input.
5. Cancel one declared edit after actual first-denoising progress.
6. Run the exact declared recovery edit once, preserving the cancelled attempt.

Freeze prompts, input hashes, seeds, settings, order and output expectations before
execution. The recovery invocation is a scheduled control case, not permission
for an arbitrary retry. Record every output/failure; no favorable seed selection,
prompt repair or extra model call follows automatically.

**This budget needs separate approval before any invocation.** Stop on the first
required format/protocol/resource/control failure or clear quality failure. Keep
all old trial artifacts. A failed portrait base is a stop, not an invitation to
keep generating until a favorable one appears.

### Native acceptance

- Actual request/metadata proves pixel input and binds each original SHA-256.
- Original remains byte-identical. Requested change is visible, face/pose/object
  identity and non-target details are reviewed side by side by a human; do not
  equate legal output PNG or high image similarity with a correct edit.
- No claim of guaranteed likeness or pixel preservation. Record unwanted changes
  explicitly. Human quality acceptance is required before publication.
- Keep current generation limits: <=60 seconds for generation/decode, <=24 GiB
  observed worker peak, 1 GiB cache policy, <=512 MiB observed host-swap growth
  and <=2-second app health. Do not loosen a limit to admit edit mode.
- Keep the exact qualified chat digest/context resident when testing coexistence.
  Refuse other unqualified residency rather than unloading chat or claiming
  generation-only qualification covers editing. Existing embedding handoff does
  not broaden into automatic eviction of other models.
- Parent death and cancellation reap the real worker before releasing capacity;
  no partial output counts as complete. Recovery must work without corrupting
  prior outputs or the live app.
- Measure actual input/output/metadata bytes and peak storage per attempt. Each
  finished revision is a whole image, not a small Photoshop-style delta.

## PE1: integrate only a qualifying worker

1. Add an explicit owned reference identifier to accepted edit jobs. Never accept
   arbitrary filesystem paths, URLs or source text supplied by a model. First
   version supports one reference image; keep existing generation batch behavior.
2. Persist a private normalized working copy before admitting the job and pin it
   through queued/running/retry states. Preserve the user's original bytes and
   record the normalization transform. Deleting an attachment must not invalidate
   admitted work or expose another conversation's input.
3. Keep input references and output lineage separate. Add schema only if needed,
   using the next available numbered migration and old-row preservation tests.
   The dormant agent branch's migration is not a production prerequisite.
4. Include retained originals/working copies/revisions in storage totals, cleanup
   and backup/restore manifests. Reuse retained input bytes across revisions
   through explicit ownership/reference counts instead of needless full copies.
5. Use the current composer, image cards, viewer and SSE. Show which reference is
   being edited, original comparison, real progress, cancel and save/share. Keep
   image turns out of text-model context and ordinary text/vision requests intact.
6. Require synthetic fake-runtime regressions, resource/control evidence,
   generation/edit request contracts, restored-input backups and an actual phone
   check. No release or new native trial is implied by offline tests.

## Later: brush-selected edits

Precise Photoshop-style local changes need masks and an appropriate compositing
contract. Whole-image reference editing can change unrelated pixels. Do not
claim mask/brush support or deterministic preservation outside a selection until
that separate engine/UI scope is reviewed and tested.

## Recommended sequence

Review/release the narrow title/workflow-wording repair; prepare PE0 offline;
review its concrete six-invocation request; evaluate quality/resources; then
review PE1 integration. Remaining disabled workflow blocks follow separately.
Native agent/Research experiments stay closed.
