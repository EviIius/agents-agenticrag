# PE5 focused-region quality comparison

23 October 2026 · isolated `codex/masked-photo-editing` branch.

Jake requested further FLUX/Qwen trials and explicitly accepts slower generation
when quality improves. This is a new bounded trial, not a reopening of PE2–PE4.

## Question and allowance

Can giving each accessory its own high-resolution context improve the original
request, and does Qwen produce the better finished result? Maximum **six new
native invocations**: hat FLUX/Qwen, front glove FLUX/Qwen, rear glove FLUX/Qwen.
Every invocation consumes its slot, including failures/cancellation. No retries,
seed search, new weights, packages, helpers, integration or deployment.

Each pair uses identical original/reference bytes, seed 42, focused instruction,
selection and CPU context. Split the already reviewed selection into three
disjoint parts. Their union must equal that selection exactly; all face pixels
remain excluded. Freeze all six requests and sources before the first launch.
The three edits use the original independently; combine only their disjoint
selected pixels afterward. A native output never becomes a later model input.

This tests a different editing strategy, not a checkpoint-only comparison. Both
engines use the same strategy. Compare each final combined result with its own
retained PE4 one-shot result as well as with the other engine. One focused run
per region does not establish seed robustness or general consistency.

## Recipes and guards

Retain the exact PE4 workers/settings: FLUX four steps, guidance 1, 8-bit eligible
components; Qwen 40 steps, guidance 1, strength 1, linear schedule, 4-bit eligible
transformer/text and float32 VAE. 1024-square native context. Qwen receives the
mask during denoising; FLUX uses it for context/final compositing.

Reuse the frozen-source controller, two-slot append-only ledger per region and
shared native capacity lease. A six-slot outer scope fixes order and checks every
prior result/review. Technical/resource/provenance/preservation failure stops
the entire trial. A visual miss is retained and does not stop the predeclared
comparisons. No best-of selection or unreported failed output.

Empty Ollama residency throughout; never unload or refresh a model for the
trial. 24 GiB measured MLX peak, 1 GiB cache, 512 MiB swap-growth maximum,
two-second app health, owned worker reaping/parent-death watch. FLUX retains
120-second init / 60-second generation+decode / 180-second worker wall bounds;
Qwen retains 120 / 300 / 420 seconds. Accepting slower quality does not relax
resource checks or silently increase either engine's time allowance.

## Quality review and evidence

Inspect final and raw regional outputs separately. Record cap placement and fit,
front/rear glove completion, hand anatomy, boundary seams and unintended content
inside each selection. Three target completion checks stay separate; preserved
face/background cannot compensate for a missing accessory. Compare combined
outputs at full size and crops, using anonymous A/B labels on the private page.
Codex's manual observations and Jake's eventual preferences are separate records.

Independently audit RGB pixels against the original, each regional mask and their
union, manual face and exported PNG. Report total/per-region latency, peak MLX,
swap, truthful progress and retained storage. All native media, exact image
instructions, masks and coordinates remain private. Only sanitized measurements,
source hashes and synthetic tests enter Git. Preserve all prior trials, live
source/worker/service and supplied untracked proposals. Stop with SPEC H4 results
and a private comparison for quality review.
