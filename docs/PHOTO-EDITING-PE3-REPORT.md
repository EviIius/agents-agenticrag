# PE3 — two-engine masked-edit feasibility report

22 October 2026. Branch `codex/masked-photo-editing`; draft PR #9.

## Summary

Both model checkpoints are installed: existing FLUX is preserved and remains live;
Qwen-Image-2.1 is a separate local evaluation candidate. The pinned 33.13 GB Qwen
download verifies all 26 files and adds no packages. Both authorized native jobs
pass protocol, pixel preservation and resource checks. **The private accessory
edit fails content quality; Qwen is not promoted or integrated into the live UI.**

## Done-when checklist

| Item | Status | Evidence in `artifacts/photo-editing/pe3-20261022/` |
|---|---|---|
| Keep both checkpoints on disk | Pass | `model-storage.json`; installed FLUX config/worker unchanged |
| Exact Qwen revision and 26 file content hashes | Pass | `download.json`; model allowlist and private full receipt |
| No new dependency/runtime/default | Pass | Existing MFLUX 0.22.0 environment; installed source/worker/plist preservation |
| Explicit mask in actual denoising | Pass | Frozen native worker; real 0–40 progress on both cases |
| Helper generation/retries disabled | Pass | Frozen call settings, helper methods refused; CPU doubles verify refusals |
| Transformer/text 4-bit coverage, unquantized VAE | Pass | 228/344 quantized layers; VAE zero quantized layers |
| Outside pixels / face / original proportions | Pass | Independent CPU proof; 3,068,788 protected private pixels and face region exact |
| Native/composite/export retained and accounted | Pass | Both result JSONs; private exports independently equal decoded composite pixels |
| Memory/swap/health and owned process reaping | Pass, empty slot only | Both results; preservation; no chat coexistence qualification |
| Synthetic selected color change | Pass | Synthetic outputs and `synthetic-quality.json`, Codex observation |
| Correctly worn cap and two gloves | **Fail** | `private-quality.json`; private original/native/composite comparison |
| Merge/publication/Qwen picker or routing | **Not performed** | Quality gate failed; main and live remain unchanged |

## Changed files

- `image_worker/masked_trial/`: pinned downloader, isolated worker/controller,
  launcher, CPU/native-double tests and operator README. No product worker,
  server, UI, installer or database change.
- `AGENTS.md`, PE3 plan and this H4 report: approval and exhausted-scope closeout.
- New public artifacts contain only synthetic media, sanitized measurements,
  executed-source hashes and test results. Original photo, exact task, selection,
  face region, private result and review page remain outside Git.

## Deviations / boundaries

Qwen uses the existing engine's real generation mask plus PE2's independent
post-compositor. It does not replace FLUX in the application. Both weights can
remain on disk; this trial admits an **empty native slot only**. No model was
loaded/unloaded in Ollama. No simultaneous residency is qualified.

Candidate settings are the predeclared 1024-square, 40-step, seed-42, guidance-1,
strength-1, linear-scheduler, 4-bit eligible transformer/text layers and float32
VAE. No precision fallback, LoRA, rewriting, auto-mask, verification helper or
retry. The MLX limit setter is a guideline; synchronized measured peak checks and
the independent swap/health guards remained active. Production FLUX limits stay
unchanged. The longer candidate-only time caps are not a production speed pass.

The Qwen weight license is limited to noncommercial research/evaluation. Retain
the license and treat production suitability as a separate decision. No product
use beyond this evaluation is implied.

## Runtime observations

Exactly two native invocations; all previous ledgers remain closed. Both received
the frozen original references and selections, emitted actual 0–40 progress,
completed decode and were reaped before releasing the shared native lease.

| Case | Total seconds | Initialization | Generation/decode | MLX peak bytes | Swap growth | Changed outside selection |
|---|---:|---:|---:|---:|---:|---:|
| Synthetic | 189.355 | 2.638 | 186.006 | 24,218,179,569 | 0 MiB | 0 |
| Private original | 186.659 | 2.308 | 183.580 | 24,218,228,914 | 0 MiB | 0 |

MLX peak is about **24.2 GB / 22.55 GiB**, below the 24 GiB cap; it is not a
measurement of total host RAM. Maximum complete residency-plus-health guard
observations were 0.02195/0.01798 seconds; both actual application-health checks
retained their two-second limit. No package, Ollama version, service, port, bind,
plist, Tailscale or live source/static/worker change occurred. Ollama stays 0.35.0.

The retained FLUX cases took 21.035/23.053 seconds. Qwen takes roughly eight to
nine times as long in these different-budget cases. They differ in steps and the
private selection; this is feasibility evidence, **not** a matched model ranking.

### Quality diagnosis

Codex sees a successful yellow selected region in the synthetic result. In the
private result a red cap is present but sits above/behind the hair, and only one
glove-like patch is convincing. The request for a naturally worn cap and two
correct gloves is unmet. The placement issue is already present in the raw Qwen
output; it is not introduced only by the final compositor.

The selection also leaves most hair protected and constrains the crossed hands.
This is a material setup limitation: a mask-aware model cannot replace protected
hair/hand pixels to make a properly fitted accessory. Thus the result fails the
task but does not prove that Qwen is intrinsically weaker or that more parameters
will fix it. Do not quietly reinterpret this as a quality pass or run another
selection under the exhausted allowance.

All 3,068,788 unselected pixels, the independently compared face region and the
1536×2048 prepared dimensions are exact. Sanitized export pixels also match the
composite. This pixel-preservation success does not qualify the accessories.

### Storage

| Retained item | Actual bytes |
|---|---:|
| FLUX inference snapshot, 18 files | 15,980,140,843 |
| Qwen snapshot, 26 files | 33,131,615,131 |
| Both snapshots | **49,111,755,974** |
| Synthetic native + composite + export | 456,142 |
| Private native + composite + export | 9,946,166 |

Snapshots exclude transfer caches and generated media. The private composite and
export are 4,212,254 bytes **each**, plus a 1,521,658-byte raw native PNG. Original,
prepared reference, mask/context and metadata are additional retained storage.
Observed private-case peak was 19,941,178 logical/unique-inode bytes and
19,963,904 kernel-reported allocated bytes, with 704 samples and a 0.2764-second
maximum gap. These are observed values, not proven absolute APFS physical peaks.

## Test output

- **Seven CPU/process checks pass**, with actual Pillow, subprocesses and inference
  replaced: explicit mask and final preservation, helper/network refusal, bad
  quantization/peak refusal, guard-failure reaping and remaining-case blocking,
  plus LFS/Git-blob hash verification and same-length corruption rejection.
- Ruff check and format check pass for the trial Python files; changed-file
  privacy audit passes. Initial style findings were fixed before source freeze.
  Initial and final seven-pass CPU logs are retained; no native trial was retried.
- Both native technical checks pass; one private content-quality gate fails.
  This consumes the entire new two-invocation allowance. No additional image,
  helper, preload or text-model call followed.
- Product source is unchanged, so the full app/browser suites were not repeated.
  PE2's earlier 773 Python / 132 frontend and focused browser passes remain
  historical. No new physical iPhone/VoiceOver claim is made.

## Screenshots / review

Public screenshots are synthetic source/context/mask/native/composite/export PNGs
under `artifacts/photo-editing/pe3-20261022/synthetic/`. The private comparison was
opened locally at `http://127.0.0.1:8769/review.html`; it includes original, actual
Qwen, retained FLUX trial, separate FLUX CPU diagnostic and the selection preview.
It is not exposed through Tailscale.

## Next step / review stop

Keep both checkpoints, with **FLUX as the live engine** and Qwen isolated. Do not
add model routing or replace the live default from these results. The next useful
work is selection quality: make the pixels to replace and protect easier to
inspect, allow precise paint/erase correction, and check that accessory masks
cover the necessary hair and each hand **before** buying more inference time.
A subsequent corrected-selection Qwen comparison needs its own concrete bounded
scope; this two-call allowance is exhausted. No stronger-model download is
justified by this single, selection-confounded failure.
