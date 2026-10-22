# PE3 preparation report

22 October 2026. Isolated branch `codex/masked-photo-editing`; draft PR #9.

## Summary

Prepared the concrete Qwen-Image-2.1 download and two-invocation feasibility scope.
Verified installed API/source and the actual CPU image processor without weights,
network access during the probe, MFLUX/MLX imports or image-model invocation.
The pinned file list is approximately 33.13 GB; no weights have been downloaded.
Native compatibility, memory, latency and content quality remain unqualified.

## Done-when checklist

| Item | Status | Evidence |
|---|---|---|
| Exact official revision/file sizes/hashes/license | Prepared | `image_worker/masked_trial/model-files.json`; official metadata and license retained in PE3 artifacts |
| Installed explicit-mask API and source pinning | Pass, static only | `preflight.json`: installed source SHA-256 inventory and signature/component observations |
| Real CPU processor at portrait/landscape/max reference sizes | Pass | Three `processor_cases` in `preflight.json`; no MFLUX/MLX import or weight read |
| Independent final compositing still protects outside pixels | Pass, CPU only | All three actual synthetic contexts/composites report zero changed protected pixels |
| Hidden helper calls disabled in proposed settings | Prepared | `trial.json`; inspected actual helper branches |
| Named quantization, time/memory/storage and first-failure scope | Prepared | `PHOTO-EDITING-PE3-QWEN-TRIAL-PLAN.md` |
| New model download/native test | **Not run** | Separate scope approval pending; earlier native ledgers unchanged |
| Live app/product files | Unchanged | This continuation changes only trial preparation, docs and public metadata artifacts |
| Installed source and local/HTTPS health | Pass | `preservation.json`: 124 server/shared files and four installed worker files match main; both health checks pass |

## Changed files

- `image_worker/masked_trial/`: CPU/static preflight, exact public model file
  manifest and proposed native settings. No product worker or server/UI change.
- `docs/PHOTO-EDITING-PE3-QWEN-TRIAL-PLAN.md`: bounded next scope and approval text.
- `artifacts/photo-editing/pe3-prep-20261022/`: checked public metadata, license,
  initial/final probe outcomes and source fingerprints. No private photo/mask/task.

## Deviations from SPEC / boundaries

No native/download authorization is inferred from preparing the scope. No package
is added. The installed CPU image processor imports the already installed torch
dependency; no PyTorch model, checkpoint or MPS generation is constructed.
No UI, server, installer, production guard, default or service change is made.

## Runtime observations

MFLUX 0.22.0 contains the needed Qwen edit API. Its VAE deliberately remains
float32; transformer/text eligible layers support requested quantization. This
differs from FLUX's three-component quantization assertions. Forty-step latency
and empty-slot qualification are proposed as separate candidate measurements,
never an implicit extension of existing FLUX thresholds.

The license retrieved at the pinned revision explicitly limits use to
noncommercial research/evaluation. The plan is a trial; future production
suitability requires review. The machine reports 64 GiB RAM and roughly 1.5 TiB
free disk; capacity is not evidence that the model fits or runs quickly.

## Test output and preparation failures

- Actual offline `preflight.py`: **pass**, three synthetic processor/context/
  compositing sizes. Pixel tensors are 4096 × 1536 and image grid is 1 × 64 × 64.
  Model invocations: **zero**. Metadata was fetched separately before the probe;
  the probe itself blocks network and weight reads.
- Ruff check and format check of new preparation source: **pass**.
- Changed-file/privacy audit: **pass**, 1,947 paths scanned and zero findings.
- Installed server/shared and worker hashes match main; both local and normally
  verified HTTPS health checks pass. The Qwen image snapshot is not present.
- Initial overly broad import guard rejected torch availability inspection, then
  the required CPU torch import. Corrected to forbid model/MLX imports and actual
  network/weight reads while allowing the installed processor's CPU dependency.
  Both observations are retained. No dependency installation followed either.
- The first recorded preflight passed with a Pillow deprecation warning and a
  Ruff import-style finding. Both corrected; initial output/source hash retained.
- No product regression suite is rerun: product source is unchanged. PE2's
  773 Python / 132 frontend / focused browser results remain historical evidence,
  not newly repeated passes. No new visual or physical iPhone pass is claimed.

## Screenshots

None required for this CPU/static preparation; no app UI was changed. The prior
private PE2 comparison remains separate and its quality failure remains recorded.

## Open questions for Jake

AGENTS.md requires approval of the exact next download/native scope: the pinned
33.13 GB Qwen checkpoint and at most two ordered images under the plan's resource
and candidate-only time bounds. No merge, deployment or further model is included.
