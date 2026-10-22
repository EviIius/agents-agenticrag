# PE3 — Qwen explicit-mask feasibility trial

22 October 2026. **Approved for the pinned download and bounded viability trial.**
Branch: `codex/masked-photo-editing`; draft PR #9. The user's continuation advances
offline preparation after PE2. It does not silently reopen PE2's exhausted two-job
allowance. Jake subsequently asked to retain both engines and approved installation
in response to the concrete download/two-image question. Retain FLUX as the live
engine; Qwen remains an isolated evaluation candidate.

## Decision this trial answers

Can a model that receives the selection during denoising add the requested
accessories at acceptable quality and measured cost on this 64 GiB Mac?

PE2 proved exact protected-pixel preservation, but its FLUX editor never received
the brush mask. Its initial cap mask also clipped the generated cap. Neither
problem proves a general ranking of model strength. Retain the original result
and CPU diagnostic. Do not silently replace them with a more favorable test.

## Named components and storage

- **Qwen/Qwen-Image-2.1**, exact revision
  `d26bb61231c349cf6b7896fa83353113880e1ba3`.
- Existing MFLUX 0.22.0 image environment, interpreter and installed dependencies.
  No package installation, update or separate framework. The actually installed
  processor imports the existing CPU torch package; this is not a second model.
- Exact inference, processor, configuration and license files are frozen in
  `image_worker/masked_trial/model-files.json`: **33,131,615,131 bytes** total,
  including **33,115,613,408 bytes of weights**. This is approximately 33.13 GB
  (30.86 GiB), before outputs. Require 50 GiB free before download.
- Download only those paths at that revision to a separate ignored private cache;
  check file sizes and LFS SHA-256 / Git blob SHA-1 as applicable. Keep the receipt.
  No implicit latest revision, helper weights, quantized export or alternative
  checkpoint. Native execution uses a complete local snapshot with Hub and
  Transformers offline, plus a socket blocker.
- The pinned [license](https://huggingface.co/Qwen/Qwen-Image-2.1/blob/d26bb61231c349cf6b7896fa83353113880e1ba3/LICENSE)
  limits the weights to noncommercial research/evaluation. This is a local
  evaluation only. Future ordinary product use needs a separate suitability
  decision; do not treat this candidate as an Apache-2.0 replacement.

The checked official metadata and license text are retained under
`artifacts/photo-editing/pe3-prep-20261022/`. No weights had been downloaded at
preparation. The subsequently approved download/trial outcome is recorded in
`PHOTO-EDITING-PE3-REPORT.md`; its two-invocation allowance is now exhausted.

## Offline findings and limits of that evidence

`image_worker/masked_trial/preflight.py` reads installed source without importing
MFLUX/MLX, and runs the real image processor on synthetic CPU images without
weight reads or network access. Portrait, landscape and maximum working-reference
sizes pass. The frozen source confirms:

- Explicit white/black mask drives per-step source-latent blending and a final
  composite. This is actual generation conditioning, unlike PE2's post-composite.
- Transformer/text-encoder eligible layers can be quantized; **VAE is deliberately
  unquantized float32**. Reusing FLUX's all-three-components 8-bit assertion would
  reject this valid engine configuration.
- Auto-mask, prompt rewriting and verification can invoke additional generation.
  They must all remain disabled, with no automatic retry.

This establishes API/CPU preparation compatibility only. The checkpoint's tensor
loading, actual quantization coverage, Metal peak, speed and edit quality remain
unverified. Processor import required the existing torch package; no package was
added to make the preflight pass.

## Frozen parameters

Machine-readable source: `image_worker/masked_trial/trial.json`.

One reference and explicit mask; native canvas **1024 × 1024**, seed **42**,
**40 steps**, guidance **1**, strength **1**, linear scheduler, KV cache on,
step skipping off. **4-bit eligible transformer/text layers**, original float32
VAE, no LoRA. Inspect quantized module coverage/bits before generation without
forcing all lazy parameters to materialize at once. No precision fallback.

Explicitly pass `auto_mask=None`, `enhance_prompt=False`, `verify=False`,
`verify_retries=0`, `use_step_cache=False`, `negative_prompt=None`.
The prompt is not rewritten. No planner, detector, captioner, judge, text-model
call or cloud fallback. Model-native image/text embeddings are part of the single
image generation invocation. Forty steps follows the official base-model recipe;
do not compare it as though it were FLUX's four-step budget.

## Maximum two native invocations

Before the first launch, freeze all executed worker/controller/component hashes,
parameters and **both** input requests. Keep the real input, user task, masks,
face-protection region and outputs private. Reserve each attempt durably before
launch; a failed or cancelled invocation consumes it. No deletion/replacement
attempt. The prior PE0/PE1/PE2 ledgers remain closed.

1. **Synthetic:** the original PE2 CPU-drawn blue-rectangle fixture and selection,
   exact instruction in `trial.json`. Verify yellow content, selection boundaries,
   actual step events 0–40, output binding, exact outside pixels and resource
   bounds. Codex inspects the retained native/composite, recording the observation
   as Codex's, not the user's. Failure ends the trial before private generation.
2. **Private original:** the previously supplied office portrait, exact original
   hat/two-glove request. Select enough room for the additions while excluding
   the face; freeze this selection before invocation 1. Inspect the hat and each
   glove separately, hand anatomy, placement and boundaries. Verify the protected
   face and every unselected pixel exactly. One result only, no regeneration.

Fit reference context without distortion using PE2's transform. Map the hard
selection into the **same** native viewport, black in padding. Pass that mask
directly to Qwen. Keep PE2's independent final compositor and CPU verifier, raw
native output, sanitized export and original prepared dimensions.

For the real-photo comparison, show original FLUX, its retained mask diagnostic
and Qwen separately. A corrected selection differs from the initial FLUX one;
this is a feasibility comparison, not a controlled model-ranking experiment.

## Candidate-only resource boundary

- Empty Ollama residency required first and throughout; no automatic unloading,
  preload or expiry refresh. Do not infer chat coexistence from an empty-slot pass.
- Acquire the **existing production native lock** using `Capacity`; inherit the
  lock descriptor into the worker, watch parent stdin and reap the entire owned
  process group before releasing the lease. No competing live image/chat job.
- Keep **24 GiB MLX peak**, **1 GiB cache**, **512 MiB swap growth** and **2 seconds
  application health**. Check residency/swap/health independently while work runs;
  stop/reap on a failed guard. The installed MLX memory-limit setter is a guideline
  for graph evaluation, not an absolute allocation ceiling. Apply it, and retain
  measured peak checks at synchronization barriers plus independent host guards;
  do not claim the setter alone enforces a hard ceiling.
- Proposed candidate-only maxima: **120 seconds initialization**, **300 seconds
  generation plus decode**, **420 seconds overall**. These are new reviewed trial
  allowances, not changes to FLUX's qualified 60-second limit or production policy.
  End-to-end latency includes initialization. A >60-second generation is reported
  as a daily-use speed concern even if it completes under this feasibility cap.
- Record actual denoising progress, peak memory, swap, health samples, reaping,
  input/native/composite/export bytes, logical/allocated storage and sampling gaps.
  Measurements do not prove an absolute filesystem peak.

Stop on the first compatibility, protocol, resource, preservation **or quality**
failure. Preserve partial outputs and exact source; no retry with more steps,
another precision, stronger prompt, different seed or model.

## Acceptance and next review

The requested hat and **both** gloves must be correct, with no extra/detached
hand, no obvious clipping/seams, unchanged protected face and background, and
preserved prepared-photo dimensions. A mere changed-pixel count is not a quality
pass. Retain failures and separate structural preservation from content quality.

After at most two calls, stop with SPEC H4 evidence and a private comparison for
Jake. A favorable pair is feasibility evidence only: it does not qualify repeated
quality, cancellation/recovery, chat coexistence or production integration.
Keep main, live app, existing FLUX worker/defaults and PR #9 unmerged.

## Approval record

The named **33.13 GB pinned model download** and this **maximum two-image trial**,
in the existing image environment with the candidate-only budgets above, were
presented for approval. Jake subsequently said to retain both engines for
viability and approved installation. The private receipt records that approval
and binds the frozen sources/inputs; it does not reopen any previous native
allowance. No Qwen production integration or live-default change is included.
