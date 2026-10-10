# Image trial I0 — proposed scope after checkpoint R review

10 October 2026. Preparation only; no image package, weights or interpreter was
installed and no images were generated during checkpoint R.

## Named recommendation

Trial **MFLUX with `black-forest-labs/FLUX.2-klein-4B`** in an isolated worker
environment. The workflow goal makes CLI/Python control a useful first property
to test. Draw Things remains the manual alternative if this worker fails its
control or visual-quality checks; do not install both engines initially.

MFLUX documents the klein implementation, image-conditioned editing, quantization
and CLI/Python entry points. Its source package currently declares version
0.22.0, but a version declaration does not prove a compatible published wheel or
resolved dependency set exists. Verify and pin a usable published release,
dependency lock and model revision before the trial.
[Klein implementation](https://github.com/mflux-community/mflux/blob/main/src/mflux/models/flux2/README.md),
[package declaration](https://github.com/mflux-community/mflux/blob/main/pyproject.toml).

Common documentation demonstrates callbacks, but its illustrated callback setup
uses another model. Do not claim verified klein progress, safe termination or
restart behavior from that example. Those are trial requirements.
[Common API notes](https://github.com/mflux-community/mflux/blob/main/src/mflux/models/common/README.md).

The model has an Apache 2.0 license. Publisher GPU figures are not measurements
on this Mac. The documented host is an M5 Pro Mac mini with 64 GB unified memory;
actual loaded-model, context and worker peaks must be measured together.
[Publisher model card](https://huggingface.co/black-forest-labs/FLUX.2-klein-4B).

## Installation boundary

AGENTS.md requires named approval for new dependencies. The proposal is the
isolated MFLUX environment and this one model, including the resolved image
dependencies. Preserve the server and transcription interpreters, dependency
locks, current Ollama version and app service. Do not add these packages to the
chat server. Do not download a second image or chat model as a fallback.

Prepare the public trial wrapper under this repository. Keep the interpreter,
weights, caches and any credentials outside Git; use a private installed-app
location for unattended execution rather than relying on Documents access.
Finalize the storage layout before installation, avoiding repeated copies of
large weights during ordinary app deployments. Existing automatic database
backups must not silently expand to include models or temporary inputs.

Keep real image prompts and reference files private like document inputs. Use
only the synthetic cases below in committed logs, screenshots and trial evidence.

No app UI, production adapter, new listener or Tailscale change is part of I0.
The existing application stays available. A working trial permits the separately
reviewed durable-job/image integration checkpoint I1; it is not that release.

## Frozen first trial

Resolve the supported CLI/API before constructing the wrapper. Then freeze its
source, model revision, dependency lock and these explicit trial settings:

- Distilled klein 4B, 1024×1024, four steps, one image per invocation.
- 8-bit quantization if verified for the pinned implementation; record exactly
  which components it quantizes. Stop and review an unsupported configuration;
  do not silently fall back to a different precision or model.
- Seeds 42 and 1337 for every generation prompt; no prompt rewriting.
- Six synthetic prompts below, all twelve outputs retained. Fixed seeds help
  compare runs but do not guarantee identical pixels across revisions/hardware.

| Case | Exact prompt | Manual task check |
| --- | --- | --- |
| Photograph | A realistic photograph of a red ceramic mug on a wooden table beside a closed blue notebook, morning window light, no people. | Mug, closed notebook, requested colors and relationship. |
| Interior | A small reading room with one green armchair to the left of a tall bookcase, a floor lamp behind the chair, and a round rug. | Object presence, count and spatial relationships. |
| Illustration | A flat editorial illustration of a small orange fox carrying a purple umbrella in light rain, cream background, simple shapes. | Subject, umbrella, colors and requested illustration style. |
| Text | A simple navy poster with large clearly readable white text exactly saying FIELD NOTES and a small yellow circle below the words. | Exact text and layout; mark misspellings as failures. |
| Count | Exactly three yellow pears and one green apple on a white plate against a plain grey background, overhead photograph. | Three pears, one apple; retain every count failure. |
| Arrangement | A studio product photograph of a glass water bottle between two small white boxes, soft shadows, plain beige background. | Bottle position, two boxes and requested presentation. |

Use a generated synthetic input for one reference edit: change the mug color to
green while preserving the notebook, camera view and scene. Retain input/output
and assess whether unrelated content changed. Stop if reference editing is not
supported by the pinned entry point; do not assume publisher features exist in
every implementation.

## Measurements and control checks

Separate first execution/download, uncached initialization, cached initialization
and resident-model generation. A second CLI invocation may have warm disk caches
while still loading a new model; do not label it resident warm performance.

Record every run's duration, output validity, model-load time where available,
observable stage/step progress, process memory and available MLX memory counters,
swap, downloaded/cache bytes and remaining disk space. Sampling memory is not
necessarily a true peak; label measurement limitations and retain the raw trace.

Test:

1. Execution without depending on an interactive app window; then a supervised
   subprocess invocation suitable for the installed app's service context.
2. Cancellation during initialization and generation. Confirm worker/process
   termination and memory release before reporting cancelled or granting the
   next heavy invocation. Merely cancelling the HTTP requester is insufficient.
3. Failed initialization, bad input and missing output. No partial PNG counts
   as a successful image; a later invocation must recover predictably.
4. Current app health and browser responsiveness while a job runs. Measure
   normal chat again afterward. Any concurrent chat experiment must be explicitly
   declared and retain its payload; no hidden model unloading.
5. Output metadata: exact prompt, model revision, quantization, seed, dimensions,
   steps, dependency/wrapper version and completed file hash.

The one-shot subprocess is a trial boundary, not a final residency decision.
Compare the observed cost of restarting with a resident worker before designing
I1. Do not alter current runtime loading policy to improve an image benchmark.

## Review gate

Deliver the twelve generation outputs, reference edit, every failure and an H4
report. Summarize task adherence separately from visual preference. Report median
and p90 timings with sample counts and clearly identified cold/warm categories.

Jake reviews quality and acceptable latency from actual results. Technical
progress, cancellation, failure recovery, resource fit and preservation checks
must pass before selecting this engine for integration. A failed trial does not
authorize a bigger model, another package or a new runtime upgrade automatically.

I1 then implements the shared durable queue and image UI. Later W1 starts with
the recording-to-meeting-pack template. Factual outputs remain reviewable drafts
until supported-answer qualification passes; image success does not qualify
factual automation or reopen Research.
