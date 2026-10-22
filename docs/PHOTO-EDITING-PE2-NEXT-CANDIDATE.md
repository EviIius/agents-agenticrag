# Mask-aware model options after PE2

21 October 2026. Research only: no installation, download, default switch or
additional native call is authorized here. PE2's two-call trial is exhausted.

## What the actual test establishes

The compositor protects pixels and preserves prepared-photo proportions. The
first hat mask was too tight: expanding it using the same retained native image
improves the cap without any inference. The glove result still misses the full
request. This single private case does **not** establish that FLUX is generally
weak or that a larger model will solve it. The current 4B editing API never sees
the brush mask; it sees a context image and regenerates it. Final compositing
prevents unwanted pixels from being used, but cannot force accessories to land
inside the selected areas.

## Recommended candidate: Qwen-Image-2.1

- Named repository **Qwen/Qwen-Image-2.1**, current revision
  `d26bb61231c349cf6b7896fa83353113880e1ba3`.
- The official model card describes a 7B **visual component**, localized edits
  and separate masks. This is not the size of the complete resident system:
  its text/vision encoder and VAE are additional components.
  [Official model card](https://huggingface.co/Qwen/Qwen-Image-2.1).
- The installed **MFLUX 0.22.0** already contains `QwenImage21Edit`. Its explicit
  `mask_image` is used for per-step source-latent blending and final pixel
  compositing. This is a better structural match to selected editing than only
  changing the whole-image generator. Keep Aether's independent final compositor
  and verifier even when a candidate offers its own blending.
  [Pinned engine implementation](https://github.com/mflux-community/mflux/blob/31c9640399572ea394d07092763be9a36007a754/src/mflux/models/qwen21/variants/edit/qwen_image_21_edit.py).
- Public repository metadata currently totals approximately **33.13 GB** for
  weights/configuration/processor files: about 14.23 GB transformer, 17.53 GB
  text encoder and 1.35 GB VAE, plus tokenizer/config files. Quantizing runtime
  weights does not remove that original download cost. Retained caches/exports
  would require additional disk space.
- The model card's license is **qwen-research**; check its terms before a named
  download approval. It is not the Apache-2.0 license of older Qwen Image models.
- Mac peak memory, quantization coverage, latency and quality are **unmeasured**.
  Do not extend the qualified FLUX guard or promise chat coexistence from model
  parameter counts. Do not unload a chat model or upgrade packages implicitly.
- Disable `auto_mask`, `enhance_prompt`, `verify`, `verify_retries` and automatic
  retries: those options can add model calls. Supply an explicit user selection
  and exact user prompt; no helper/planner or cloud fallback.

A follow-up scope should first verify compatibility offline, freeze all named
components/files and quantization settings, then request the named download and
a small fixed native matrix. Use an empty native slot first, retain the host
memory/health guards, predeclare the candidate's step/time allowance and assess
speed before considering production or coexistence. Original FLUX qualification
and its thresholds remain intact.

## Other candidates

| Candidate | Why consider it | Why it is not the first recommendation |
|---|---|---|
| FLUX.1 Fill dev, revision `358293da0354175698b67ec8299acf928313a78a` | 12B model explicitly trained for image+mask filling; installed MFLUX has `Flux1Fill` | Separate weights, gated terms/non-commercial model license and unmeasured memory/latency; not interchangeable with klein weights |
| FLUX.2 klein 9B, revision `92196c8e11f7b6cf2b7493e037d8c5345c559216` | Larger member of the current family | The installed whole-image edit API still does not accept a brush mask; size alone does not solve placement |
| Qwen-Image-Edit-2511, revision `6f3ccc0b56e431dc6a0c2b2039706d7d26f22cb9` | Officially emphasizes lower drift/character consistency | About 20.43B transformer parameters, other components additional; not equivalent to 7B Qwen-Image-2.1 and no demonstrated advantage on this Mac |

Sources: [FLUX Fill model card](https://huggingface.co/black-forest-labs/FLUX.1-Fill-dev),
[pinned MFLUX Fill documentation](https://github.com/mflux-community/mflux/blob/31c9640399572ea394d07092763be9a36007a754/src/mflux/models/flux/README.md),
[Qwen Edit 2511 model card](https://huggingface.co/Qwen/Qwen-Image-Edit-2511).

Recommendation: retain the tested mask/compositor foundation, improve mask
preview/selection boundaries, and compare a genuinely mask-aware backend before
assuming that a larger whole-image model is the answer. Do not publish PE2's
current private result as a successful two-glove edit.
