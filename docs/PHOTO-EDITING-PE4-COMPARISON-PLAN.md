# Proposed corrected-selection pair

22 October 2026. **Not executed or approved by PE4's implementation scope.**
First review the private CPU coverage page at `http://127.0.0.1:8770/review.html`.
The mask now covers the existing hair and hand areas, with the manually outlined
face and watch protected. Four small manually identified regions reach 100%
coverage; that does not establish full-object coverage or generated quality.

## Question

Does the corrected selection produce the requested edit, and does Qwen provide
enough visible benefit over FLUX to justify its measured cost? Stop adding models
until this known selection confound is checked on the already installed pair.

## Proposed new allowance: exactly one invocation per engine, at most two

1. FLUX.2 klein 4B: existing pinned weights and MFLUX 0.22.0; four steps,
   guidance 1, 8-bit quantized components, existing 60-second generation/decode
   bound. PE4's ordered CPU paint/erase and independent final compositing.
2. Qwen-Image-2.1: existing pinned weights/environment; 40 steps, guidance 1,
   strength 1, linear schedule, 4-bit eligible transformer/text layers, float32
   VAE; the same explicit mask during generation and the same final compositor.
   Keep PE3's 120-second initialization / 300-second generation+decode /
   420-second wall bounds. Helpers, rewriting, verification, retries and LoRA off.

Use identical original bytes, normalized reference, corrected selection, exact
user instruction, seed 42 and 1024-square context transform on both. Freeze them
and all executed source before either launch. Keep actual source/model identities
and differing engine settings visible; this compares achieved quality and cost
with each engine's existing recipe, not equal-step model strength.

New CPU source is copied into a new private trial root. Never modify PE2/PE3
frozen source, media, selections, attempts or reports. The new append-only ledger
has two slots; failed/cancelled invocations consume a slot. No replacement, seed
search, mask/prompt refinement or third engine within this pair.

## Guards and stopping

Empty Ollama residency before and throughout both jobs; no preload, unloading or
expiry refresh. Use the existing native capacity lock, inheritance/parent-death
watch and owned process-group reaping before lease release. Keep 24 GiB measured
MLX peak, 1 GiB cache, 512 MiB swap growth and two-second app health. The MLX memory
setter remains a guideline; synchronized measured checks and host guards apply.

Protocol, resource, preservation or source-binding failure stops the pair before
another launch. A **FLUX content-quality failure is retained as the baseline and
does not cancel the declared Qwen comparison**: comparing content quality is the
purpose of this pair. Neither case is retried, and a second-case failure ends
the allowance. This distinction must be approved with this concrete scope; it
does not reinterpret the earlier first-failure trial rules.

## Review

Inspect cap placement/fit, each glove, hand anatomy and boundary seams separately.
Independently prove all unselected pixels and the manually protected face stay
exact, verify input/export identity, and report end-to-end time, MLX peak, swap,
app health, actual step progress and raw/composite/export/storage costs. Compare
the actual composites plus retained native outputs; no automatic model judge.

Only synthetic tests and sanitized metrics enter Git. The private comparison
must retain failed outputs. One favorable pair is not consistency, cancellation,
coexistence or release qualification. Stop for user quality/cost review. No
download, package/runtime/default change, main merge, production Qwen routing or
publication is included.
