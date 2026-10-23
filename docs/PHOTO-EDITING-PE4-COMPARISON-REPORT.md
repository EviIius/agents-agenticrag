# PE4 corrected-mask FLUX/Qwen comparison report

23 October 2026 · `codex/masked-photo-editing` · draft PR #9.

## Summary

Exactly one image per installed engine completed on identical frozen inputs.
Both preserve the prepared photograph's protected pixels and pass resource/
protocol checks. **Both fail the cap-and-two-glove quality requirement.**
Qwen takes 7.76 times as long without a convincing benefit on this task.
No model is promoted, and no merge, deployment or further generation follows.

## Done-when checklist

| Item | Result | Evidence under `artifacts/photo-editing/pe4-pair-20261023/` |
|---|---|---|
| New explicitly approved two-slot scope | Complete; two consumed, no retries | `results.json`, private append-only reservations |
| Same original/reference/task/seed/mask/context | Pass | `executed-source.json`, private CPU preflight/frozen manifests |
| Existing model files verified before/after | Pass | 18 FLUX / 26 Qwen files; `preservation.json` |
| Actual steps, quantization, helper refusal and binding | Pass | `progress.json`, worker sources and native metadata; CPU doubles |
| Lease, reaping, empty residency, time/memory/swap/health | Pass | `results.json`, `preservation.json` |
| Exact unselected pixels, manual face and export identity | Pass | Independent `pixel-audit.json` plus frozen codec verification |
| Correctly worn cap and two convincing gloves | **Fail, both** | Private raw/composite review and bound visual assessments |
| Consistency / production Qwen qualification | Not established | One case per recipe; neither meets quality |
| Future themes/local-AI proposals recorded | Complete, planning only | `FUTURE-PLANS-2026-10-23.md`, `future-plan-inputs.json` |

## Changed files

- `image_worker/masked_pair/`: isolated frozen pair launcher/controller,
  worker copies, preparation, CPU preflight, model/process doubles, tests and
  a separate post-generation direct pixel audit. Nothing is installed as a
  product worker.
- `AGENTS.md`, comparison plan/report: explicit approval, stopping rule and
  exhausted allowance. Previous executed sources/inputs remain unchanged.
- `FUTURE-PLANS-2026-10-23.md` and local-automation cross-reference: supplied
  themes/motion, capture, Night shift, notifications, routing/memory, messaging,
  browser/desktop use and voice proposals. No theme patch is applied.
- New evidence contains sanitized measurements, source hashes, synthetic CPU
  logs and planning-input hashes. Real media/task/selection/review stay private.

## Deviations from SPEC.md

The new allowance and exception to visual first-failure stopping were explicitly
reviewed before launch: a FLUX quality miss is retained as the baseline, while
technical/resource/preservation failures stop the pair. This does not reinterpret
earlier trial rules or reopen their budgets. There were no technical failures
in either native invocation, and neither invocation was retried.

This compares existing recipes, not equal-step model strength: FLUX uses four
steps and 8-bit eligible components; Qwen uses 40 steps, 4-bit transformer/text
layers and its unquantized float32 VAE. Both use the same 1024-square context
and final compositor. **FLUX uses the selection for context and final compositing;
Qwen also receives it during denoising.** Their raw generation behavior differs.

The FLUX trial copy adds network refusal, the existing 24 GiB allocation guideline,
an initialized event and binding/helper-count metadata to the existing worker.
Its single generation call, model, seed, prompt, precision and steps are unchanged.
The Qwen worker retains the PE3 recipe/helper refusals. The new CPU paint/erase
module is copied into the new root; no old frozen module is edited.

The direct RGB audit is an explicitly separate **post-generation CPU check**,
with its own source hash. It imports no compositor/model implementation, changes
no selection or output, and does not redefine the native gates.

## Runtime observations

Both use the installed MFLUX 0.22.0 environment. Model checkpoints total
49,111,755,974 bytes and remain installed; no package/model download or runtime
upgrade occurred. These trials require empty Ollama residency and do not qualify
chat/image coexistence. The shared native lease is held through verification
and owned worker reaping. MLX limit setters are guidelines; synchronized measured
peak checks and the independent host guards remain decisive.

| Engine | Total seconds | Initialization | Generation/decode | MLX peak bytes | Swap growth | Protected pixels changed |
|---|---:|---:|---:|---:|---:|---:|
| FLUX.2 klein 4B | 23.446 | 2.867 | 20.097 | 18,659,198,390 | 0 MiB | 0 |
| Qwen-Image-2.1 | 182.007 | 2.181 | 179.017 | 24,218,226,354 | 0 MiB | 0 |

The MLX figures are allocation measurements, not total machine RAM. Both remain
under 24 GiB. The maximum combined residency/health guard observation was
0.02120 seconds for FLUX and 0.01616 for Qwen; the actual health request retains
its two-second bound. Both workers are reaped; Ollama is empty afterward.

All 3,025,097 unselected pixels and all 42,761 manually outlined face pixels match
the prepared reference exactly. Exports match composite pixels; dimensions remain
1536 × 2048. This is measured pixel preservation, not accessory correctness.

### Visual assessment by Codex

| Item | FLUX | Qwen |
|---|---|---|
| Cap | Native cap is more coherent; final compositor trims its brim/edge where it crosses protected face pixels | Cap sits above/behind the hair already in the raw output; placement remains unconvincing |
| Front glove | Recognizable white glove, with generic workwear details | Rounded glove-like shape with weak finger/fit detail |
| Rear glove | Rear hand remains largely bare | Rear hand remains bare |
| Overall requirement | Fail | Fail |

The raw/composite comparison identifies two separate limits. The compositor
correctly refuses any change to protected pixels; a generated cap crossing that
boundary gets clipped. Missing glove content is also visible in raw generation,
so it cannot all be blamed on the compositor. The corrected coverage did not
make this full request succeed. Do not replace these failures with a claim that
a further mask, seed or larger checkpoint will necessarily solve it.

One fixed task/seed per engine cannot establish a general ranking or consistency.
For this task and these recipes, the observed Qwen cost has no demonstrated
quality payoff. Its research-only checkpoint remains an evaluation candidate.

### Storage per retained edit

| File | FLUX bytes | Qwen bytes |
|---|---:|---:|
| Raw native PNG | 1,471,106 | 1,572,950 |
| Composite PNG | 4,207,208 | 4,208,649 |
| Export PNG | 4,207,208 | 4,208,649 |
| PNG triplet total | **9,885,522** | **9,990,248** |

Both triplets total 19,875,770 bytes, excluding original/reference, context/mask,
metadata and review copies. Observed whole-job peaks were 19,943,669 logical/
unique-inode bytes for FLUX and 21,451,795 for Qwen; kernel-reported allocation
was 19,972,096 / 21,479,424 bytes. Sampling recorded 90 / 692 observations, with
maximum gaps of 0.2774 / 0.2812 seconds. These are observed peaks and kernel
allocation reports, not absolute or deduplicated physical APFS measurements.

## Test output

- **13 CPU/process checks pass**: real subprocess/codec/composite verification,
  both worker recipes with native modules replaced, helper/network/bad-bit/peak
  refusal, frozen-input tamper refusal, guard-failure reaping, exhausted slots,
  and output-bound FLUX visual failure versus stale-review continuation.
- Initial CPU run: 11 pass / two fixture failures. The controller fixture lacked
  the native-image provenance hash required by the existing verifier. Completing
  that fixture yields 13 passes without changing the production/native gate.
- Initial preparation stopped before freezing/reservation because the CPU audit
  used the public summary's face-count key against the private coverage record.
  Correcting the field name produces a passing direct face/mask/context check.
  The initial root/log remains retained separately; it launched no native job.
- Lint/format and private-marker checks pass. Initial inherited style findings
  were corrected before freezing. Both native calls pass protocol/resource/
  preservation checks and both visual checks fail. All outcomes are retained.
- Product server/web/installed worker source is unchanged. Full product suites
  were not repeated for this isolated evaluation/docs work. PE4's 777 Python /
  132 frontend, 790 browser passes / four skips / two corrected stale assertions
  with a successful 12-case rerun remain historical evidence, not a new run here.
- New 32-file source/input freeze and 962 engine/server source hashes verify
  after execution. Prior 18 input/source and 77 engine hashes verify unchanged;
  model file contents verify again. Installed app/static/worker/plist match the
  pretrial inventory. Local and verified HTTPS health return 200; Ollama remains
  0.35.0. No main merge, service/config change or deployment occurred.
- No new physical iPhone or VoiceOver result is claimed.

## Screenshots

Real-photo images are intentionally not committed or captured as repository
screenshots. The private original/selection/raw/composite comparison is open at
`http://127.0.0.1:8771/review.html`, served on loopback only. Native and exported
images remain in that private trial root. Public artifacts contain measurements
and synthetic CPU evidence only.

## Open questions for Jake

The comparison allowance is exhausted. Keep FLUX as the live engine and do not
promote Qwen from this result. Hold precision-editing release until a concrete
quality/usefulness scope is accepted. A useful alternative to review is explicit
accessory layers with user positioning: that separates exact scene preservation
from object placement. It is a new design proposal, not implemented or qualified.

Do not continue near-identical native retries or buy another checkpoint on this
evidence. Any later generative edit needs a clearly drawn replace/protect boundary
that allows intended occlusion, a bounded scope and a quality decision.

The supplied themes/AI ideas are now in the future roadmap. Theme decisions
J12/J13/J18–J20, Safari/iPhone/full-stack validation and compatible server/web
publication remain future review. No attached prompt's suggested approvals or
deployment commands were treated as Jake's instructions to execute them.
