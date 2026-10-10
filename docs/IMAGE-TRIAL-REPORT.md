# Image trial I0 report

10 October 2026. Native trial, Codex visual review, regression checks and
preservation closeout are complete. Stop for I0 quality/latency review; comfortable
mixed-model memory use is not yet qualified.

## Summary

The approved MFLUX/FLUX.2 klein 4B worker runs on the 64 GB M5 Pro Mac mini:
twelve 1024-square images and one reference edit completed, with actual step
events, cancellation/reaping and recovery. Generation median is 9.77 seconds.
Three generation samples have quality flags; first-image host swap increased.
The image feature is not integrated. Quality/latency and memory policy need review.

## Done-when checklist

| Item | Status | Evidence |
| --- | --- | --- |
| Exact isolated dependency/model selection | Pass | MFLUX 0.22.0, Python 3.13.15, MLX 0.32.3, `image_worker/uv.lock`, pinned model revision and file hashes |
| Original frozen prompts/settings | Pass | Six prompts × seeds 42/1337; four steps, 1024×1024, 8-bit eligible layers, unchanged across repair |
| Native generation/reference edit | Pass | Twelve generations plus one edit; complete PNG/dimension/metadata/hash checks |
| Actual progress and termination | Pass | Four completed-step callbacks per successful job; initializer/generation cancellation exits −15, reaped and absent before next stage |
| Failure recovery | Pass with boundary limitations | Real missing-input/empty-snapshot failures, then successful jobs; missing/partial-output unit checks |
| Headless/private worker paths | Pass for supervised subprocess | Minimal inherited environment, private source/requests/outputs; no interactive image app or repository access needed by child |
| Application responsiveness | Pass for measured probes | 156 successful-image-stage health samples, no failure; real Chromium/WebKit focus checks, no physical phone claim |
| Comfortable mixed-model memory use | **Not qualified** | Swap rose during first image with a 21.83 GB loaded chat model; ordinary keep-alive expiry later removed that model |
| Visual quality/acceptable latency | **Jake review pending** | Codex reviewed all 13 outputs; nine clean generation matches, three flags; no invented user acceptance |
| Repository checks | Pass | `make-check.log`: 480 Python / 39 frontend |
| Full browser regression | Pass | `make-e2e.log`: 463 passed, three existing skips; 37.6 minutes |
| Final production/input preservation | Pass | `preservation-final.json`: 505 installed files, 7,296 original inputs, 204/214 earlier frozen files and both nine-file image attempts preserved |

## Changed files

- Isolated `image_worker/`: dependency project/lock, frozen synthetic specification,
  pinned downloader, event worker, process controls, stage runner, 12 control tests
  and operational README. No image dependencies enter the server's environment.
- `artifacts/image-trial/i0/`: all 13 outputs and metadata, full/failed traces,
  exact attempt-one source, diagnostic, manifests, resource/progress records,
  manual review and a standalone `gallery.html`.
- Documents: this H4 report, proposed `IMAGE-INTEGRATION-PLAN.md`, deferred-list
  update and AGENTS authorization/closeout. The executed trial plan is unchanged.
  Ignore rules guard private worker assets if mistakenly placed under the repository.
- No production app/frontend/provider/schema/default/prompt/sampling change.

## Deviations from SPEC.md

The named isolated image environment/model calls are explicitly approved for I0;
they do not change the production call rules or authorize I1 UI/workflows.

Attempt one falsely rejected quantization before pixel generation. Its metadata
inspection used default `tree_flatten`, which descends into dictionary-like MLX
Modules. A small synthetic quantized Linear reproduces the false zero-layer count.
The generic correction preserves Modules as leaves. Exact old source/evidence is
saved, the corrected source is frozen again, and failure/cancellation checks are
repeated before generation. No engine/configuration fallback or repaired image
was used; no model, precision, prompt, steps, seed or dependency changed.

No OS page-cache purge was performed. `cold` is a stage name for the first
successful fresh worker after download and an earlier aborted initialization,
not a verified uncached-system measurement. Cold/cached successful worker samples
are each n=1; actual resident reuse is measured separately at n=9.

The first browser probe targeted `/design`, deliberately unavailable in production
(404), and timed out waiting for its heading. It is retained as a setup observation.
The replacement uses the actual app's visible composer, collects only focus/frame
timings, and records no private text, filenames or screenshots. No product fix
was required for the expected development-route restriction.

## Runtime observations

### Quality and time

| Measurement | Sample count | Result |
| --- | --- | --- |
| All generation calls | 12 | Median 9.77 s; p90 11.53 s; range 9.52–16.72 s |
| Same model-instance reuse | 9 | Median 9.71 s; p90 10.02 s |
| First successful fresh worker, end to end | 1 | 20.00 s; internal model initialization 1.41 s |
| Second fresh worker, end to end | 1 | 14.10 s; not a resident-model run |
| Reference-edit worker, end to end | 1 | 26.02 s |
| Weight download plus hash receipt | 1 | 234.34 s; 15,980,140,843 snapshot bytes; duplicate root checkpoint omitted |
| Chat probe before / after | 1 each | READY; 2.67 / 3.42 s, no explicit sampling/options/unload |

All p90s use nearest rank; this small sample is not a general performance promise.
Generation timing includes rendering/PNG validation/save but excludes that worker's
initialization. Whole-worker timings include supervision/startup and exit.

Codex's manual observations, not Jake acceptance:

- Both photographs, both text posters and both bottle/box arrangements match.
- Interior seed 42 adds a second lamp. Seed 1337 matches the intended arrangement.
- Illustration seed 1337 has two apparent tails. Seed 42 matches the requested
  illustration, with somewhat awkward umbrella-handle geometry.
- Counting seed 42 clearly shows the requested fruits; seed 1337's top yellow
  fruit is unusually round, making pear identity less clear.
- The edit turns the mug green and visually preserves framing/table/notebook/light.
  It does not prove exact preservation of every pixel or editing consistency.

The twelve images are unchanged native outputs. No favorable-seed selection,
postprocessing, prompt rewriting, repair generation or model quality judge was used.

### Quantization, memory and control

The actual loaded modules report eight VAE, 109 transformer and 253 text-encoder
quantized layers, all eight bits and group size 64. Other nonquantizable layers
retain native precision; recorded compute precision is bfloat16. Calling this an
entirely eight-bit model would be inaccurate.

The first generation's MLX allocation peak is 18.66 GB and its ending cache is
31.11 GB; these are distinct quantities. RSS samples peak around 7.68 GB across
successful stages and do not include every shared/Metal allocation. Whole-host
swap rose from 1,365.56 MB to 4,035.62 MB during the first successful image, so
unrestricted comfortable coexistence is not qualified. Other host activity is
not controlled; do not attribute every byte solely to this model.

The chat model is reported loaded at 21.83 GB during first/second-worker stages,
then absent after resident/edit stages. This is consistent with ordinary runtime
keep-alive expiration; no explicit unload or keep-alive override was sent. Do not
present the faster resident timings as a continual two-model residency benchmark.

Actual callback events follow synchronized denoising steps, with decoding/saving
reported separately. Cancellation during initialization and after a generation
step kills the owned process group, waits for exit, and confirms the process is
absent before another invocation. No cancelled image is marked complete. Process
absence proves its address space has ended; it is not a host-wide GPU cache/swap
measurement. Next jobs succeed and every sampled app health check returns 200.

The production browser probe makes the composer usable in about 98 ms Chromium
and 188 ms WebKit on local loopback during generation; both focus successfully.
These are fresh headless-browser measurements, not phone keyboard, mobile-network
or Home Screen app acceptance.

## Test output

- Isolated controls: **12 passed**; timeout, process termination/reaping,
  malformed/missing-terminal/nonzero outcomes and incomplete/invalid image data.
- Synthetic quantization diagnostic: wrong default flatten count reproduced,
  module-aware count recognizes eight-bit quantization without loading an image model.
- Frozen worker/source verification: pass before each native stage.
- `make check`: **480 Python / 39 frontend**, full repository gates pass.
- Source/document diff whitespace check: pass. Raw command logs retain their
  original terminal whitespace.
- `make e2e`: **463 passed, three existing skips**, 37.6 minutes. Tests,
  assertions, timeouts and skips are unchanged.
- Final preservation: **505 installed files**, server environment/transcription
  selector, **7,296 original inputs**, **204/214 earlier frozen files** and both
  nine-file image attempts verify unchanged. All 13 PNGs revalidate.
- Live local and normally verified Tailscale HTTPS health: pass; Ollama remains
  **0.35.0**. No application deployment or service restart occurred.

## Screenshots and output review

`artifacts/image-trial/i0/gallery.html` displays every native output with its exact
prompt and Codex's observations. PNGs and metadata are under `images/`; the edit's
input is retained under `images/cold/photograph-42.png`. No real prompts, reference
files, recordings, filenames, transcripts or Library documents were used as evidence.

All **5,260 earlier tracked artifacts** are restored to their original bytes.
The **382 rewritten outputs** are retained in the ignored local archive
`tmp/image-trial/i0/generated`; 23 JSON metrics and 40 newly generated synthetic
settings screenshots are retained under this checkpoint. Hash mappings are in
`regression-storage.json` and `generated-new-files.json`. No old report is replaced.

## Decision and next steps

The engine is a credible image integration candidate, with visible quality
limitations. Comfortable mixed-model memory and user quality/latency acceptance
remain open. No image feature is deployed and Research remains shelved.

Before I1, qualify a bounded MLX cache/residency policy with the intended chat
model loaded; preserve these default-policy observations and original trial
images. MLX exposes a cache-limit control, but an unused-allocation cache limit
is not a cap on live tensors, all GPU memory or Ollama residency.
[MLX cache API](https://ml-explore.github.io/mlx/build/html/python/_autosummary/mlx.core.set_cache_limit.html).

Then I1 should build durable jobs and image UI together, with one managed heavy
invocation at a time, explicit residency/resource accounting, actual cancellation,
saved inputs/outputs and SSE recovery. An active-job limit alone does not bound
already-loaded models. Ordered workflows follow that tested foundation; no agents
or factual-answer qualification is inferred from image success.

## Open questions for Jake

Review the retained samples and whether measured latency is acceptable.
AGENTS.md, the I0 plan and SPEC §H4 require this checkpoint review before I1.
The next memory-policy test and integration scope should be reviewed concretely;
no additional package/model is proposed for that next step.
