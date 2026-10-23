# PE5 focused-region comparison report

23 October 2026 · isolated `codex/masked-photo-editing` · draft PR #9.

## Summary

All six declared native jobs complete and pass technical/preservation checks.
Qwen gives the better delivered hat and a slightly preferred front glove;
FLUX handles the rear hand better. Focused edits improve some missing detail,
but neither combined result satisfies the complete quality request. Qwen's
three jobs total 581.836 seconds versus FLUX's 70.066; speed is reported
separately from quality. No production promotion follows this diagnostic.

## Done-when checklist

| Item | Status | Evidence |
|---|---|---|
| New maximum-six scope; previous ledgers remain closed | Complete; six consumed, no retries | Plan, `executed-source.json`, private scope/ledgers |
| Exact per-pair reference, instruction, selection, seed and context | Pass | Private 100-file scope and CPU preflight |
| Disjoint regional masks reproduce the prior selection exactly | Pass | CPU preflight: 120,631 selected pixels, zero outlined-face pixels selected |
| Three focused edits per engine | Six technical passes | `results.json`, actual progress, owned reaping |
| Raw/composited accessory review | Complete, mixed quality | `quality.json`, output-bound private manual reviews |
| Final independent preservation/export audit | Pass | `pixel-audit.json`: all regions and both combined images |
| Installed/old-trial/model preservation | Pass | `preservation.json`: source freezes, 44 model files, installed inventory and health |
| Private comparison and H4 closeout | Complete; user review pending | Loopback review page, this report; no merge/publication |

## Changed files

- `image_worker/masked_local/`: mask partition/CPU review, preparation, six-slot
  order/provenance wrapper and five additional scope rejection tests.
- Plan/report and AGENTS authorization; sanitized offline/source/runtime evidence
  under `artifacts/photo-editing/pe5-local-20261023/`.
- No product source or installed worker is changed. The unchanged PE4 native
  workers, launcher/controller, recipes and shared scheduler lease are reused.

## Deviations from SPEC.md

This is the separately requested quality trial. The old budgets stay exhausted.
Visual failures are retained and permit the predeclared next comparison;
technical/resource/provenance/preservation failure stops all remaining jobs.

This tests a **focused editing strategy**, including regional instructions,
selections and crops, with three generations per engine. It does not isolate
resolution from instruction changes, equalize the engines' different recipes,
or establish repeatability. No image helpers, automated model judge or chat
prompt modification is involved.

Each generation starts from the same original. The final CPU composition copies
only each stage's disjoint selected pixels; no native output is fed into another
model. No best-of output selection or concealed retry is used.

## Runtime observations

Both installed checkpoints/settings are unchanged:
FLUX four steps / 8-bit eligible components; Qwen 40 steps / 4-bit eligible
transformer/text, float32 VAE. Qwen receives the denoising mask; FLUX uses the
selection for context and final compositing. Empty Ollama residency and all PE4
time/resource/health/reaping guards remain in force.

| Region | FLUX seconds | Qwen seconds |
|---|---:|---:|
| Hat | 23.093 | 190.900 |
| Front glove | 23.558 | 193.725 |
| Rear glove | 23.415 | 197.211 |
| Sum of three measured jobs | **70.066** | **581.836** |

These sums exclude setup, manual reviews and final CPU combination. Qwen takes
8.30 times the measured generation-job time with these recipes. Maximum measured
MLX allocation is 18,659,198,390 bytes for FLUX and 24,218,442,452 for Qwen; these
are MLX allocations, not total machine RAM. Every job has zero swap growth and
zero changed protected pixels, passes real-step progress and is reaped while
holding the native lease. No concurrency/coexistence qualification is claimed.

Independent direct RGB checks using the frozen masks prove that all 3,025,097
unselected pixels and all 42,761 outlined-face pixels match the original in
both combined images. Every regional exported PNG matches its composite. Pixels
inside selected background areas can still change: exact outside preservation
does not establish natural-looking seams or successful accessory placement.

### Manual quality observations by Codex

| Target | FLUX focused edit | Qwen focused edit |
|---|---|---|
| Hat | Coherent raw cap; final brim becomes a detached fragment. A circular wall-tone seam remains inside the selection | Intact cap and clearer emblem; still sits high on the hair. Preferred delivered hat |
| Front glove | Follows the pose; plain white and somewhat soft; watch stays intact | More padded/cartoon-like with stronger seam/edge detail; slight preference. Watch stays intact |
| Rear glove | Three fingers now pale blue-white; soft finish and a small adjacent skin-colored patch remain. Better rear-hand result | White blobs are displaced beside the hand; existing fingers remain bare. Fails placement/anatomy |

The cap limitation separates generation from occlusion: the final compositor
must keep the protected face pixels, so a generated brim across that boundary
gets removed. Buying a slower generation alone cannot remove that constraint.
The focused front-hand strategy improves visible finger/finish detail. FLUX's
rear fingers now show a glove instead of remaining entirely bare. Qwen's failed
rear result shows why additional time cannot itself guarantee higher quality.

Relative to the retained PE4 one-shot pair, these are genuine localized gains,
not a complete-task pass. The original/reference/union selection and engine
recipes remain fixed, but context and regional instructions change together;
do not attribute all gains solely to resolution. Each engine's combined result
uses all three declared outputs, with no mixed-engine or best-of replacement.

### Retained storage

| Item | FLUX bytes | Qwen bytes |
|---|---:|---:|
| Three native/composite/export PNG triplets | 27,741,572 | 27,823,332 |
| Final combined PNG | 4,199,445 | 4,218,526 |

These files total **63,982,875 bytes**, excluding originals, references, masks,
contexts, metadata, inspection crops and source copies. The full per-job storage
samples and observed logical/unique-inode/kernel-allocation peaks are retained
in `storage-observations.json`. They are observed peaks, not absolute physical
APFS storage measurements. Keeping six diagnostic triplets is more expensive
than keeping only a delivered combined image; no retention policy is changed.

## Test output

- **18 CPU/process checks pass**: five new scope tests plus the 13 unchanged
  paired-controller/worker-double cases. Native model modules are replaced in
  those tests. Cross-region order, source/input tampering, stale review,
  technical failure and exhausted-slot continuation are refused.
- Actual private CPU preflight passes disjointness, exact union, equal inputs/
  contexts/masks and zero selected face pixels before any native invocation.
- Initial lint found import ordering and an unused binding. Those were corrected
  before freezing; lint and format then pass. No native preparation failure,
  technical failure, native retry or undeclared generation occurred.
- Full product suites were not repeated for this isolated trial. Earlier PE4
  product results remain historical evidence, not a fresh release gate.
- All 100 scope-bound source/input files, the three regional freezes and 962
  engine/server sources verify unchanged. Prior pair/PE3 freezes and their
  exhausted ledgers remain intact; all 18 FLUX and 26 Qwen checkpoint files
  reverify. Installed app/static/worker/plist match the initial inventory.
  Local and normally verified HTTPS health return 200; Ollama remains 0.35.0
  with no model resident afterward. The private review and eight image assets
  return 200. No package/model download, service change or deployment occurred.

## Screenshots

All real-photo originals, raw outputs, masks, inspection crops and combined
results stay outside Git. The private A/B review is open at
`http://127.0.0.1:8772/review.html`, with finished composites, regional details,
raw outputs, a folded engine key and the earlier one-shot comparison. It is
served on loopback only. Codex's own review was not blinded; the page's A/B
labels let Jake compare before opening the key. No new user quality acceptance,
physical iPhone or VoiceOver pass is claimed.

## Open questions for Jake

Review the actual results before accepting a precision-editing direction.
Qwen deserves to remain a quality candidate: its delivered hat is better here,
and speed should not override Jake's preference. This evidence does not support
automatically using Qwen for every region: its rear-hand result is worse.

The next useful design addresses accessory occlusion explicitly. A hat may
need to cover part of hair/forehead while keeping the remaining face pixels
exact; preserving every outlined-face pixel forbids some natural brim placement.
That is a mask/protection decision, not a promise that more steps or another
checkpoint will fix it. The three-region approach is a promising diagnostic
for gloves, with per-region engine strengths now visible. A mixed-engine edit
was not generated or silently substituted for either declared combined result.

All six new slots are consumed. Stop for quality/direction review; no further
native call, download, integration, main merge or deployment follows this scope.
