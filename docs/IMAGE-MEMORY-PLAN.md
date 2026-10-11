# Image memory qualification I1-0

10 October 2026. Jake said “Go ahead” after I0's committed results and recommended
sequence. Execute this resource checkpoint before production jobs/Images; stop
with SPEC §H4 evidence. No per-image acceptance or physical phone result is inferred.

## Frozen candidate

Reuse I0's MFLUX 0.22.0 / MLX 0.32.3 environment, Python 3.13.15, resolved lock,
model revision and weights. Preserve every I0 source/evidence file. A separate
worker at `image_worker/memory/` applies **1 GiB (1,073,741,824 bytes)** as the
MLX free-allocation cache setting before initialization. Verify that the setting
has not changed at initialization, completed steps and output completion.

This is a cache reuse policy. MLX can reclaim excess cached allocations on the
next allocation; a checkpoint's cache count can temporarily exceed the setting.
Neither this setting nor process RSS caps live tensors, Metal, Ollama or total
host memory. Do not silently enable MFLUX's low-RAM callbacks, evict components,
clear caches between images or change precision to improve these results.
[MLX cache API](https://ml-explore.github.io/mlx/build/html/python/_autosummary/mlx.core.set_cache_limit.html).

Use the exact original photograph and text prompts, both seeds 42 and 1337,
1024×1024, four steps, eight-bit eligible layers and guidance 1.0. Generate four
outputs in one actual resident-model batch after cancellation controls; retain
all images. This is one candidate, not a consistency or general-quality study.
No reference edit, new model, dependency, runtime upgrade, prompt rewrite,
quality judge or extra image repair is part of this checkpoint.

## Declared order and calls

1. Verify frozen inputs/dependencies, idle app, known model snapshot and private
   worker/source paths. If another Ollama model is already loaded, stop without
   unloading it; the tested combination is the daily profile plus this worker.
2. The unchanged I0 READY answer probe loads the daily
   `qwen3:30b-a3b-workbench-32k`. Send no options, sampling or keep-alive override.
3. Cancel an initializer, then cancel a photograph invocation after its first
   synchronized denoising step. Wait/reap/confirm absence before proceeding.
4. Recover with photograph 42/1337 and text 42/1337 in one worker. Read Ollama's
   reported residency immediately before and after each image. No extra chat
   call refreshes residency between images. Record missing/expired residency
   and stop; do not silently load it again to get a favorable measurement.
5. Only if all prior guards pass, run the unchanged READY probe afterward.

The initializer/generation cancellation attempts and four successful image
invocations are declared native image work. The two READY answers are the only
new chat calls. Ordinary Search/Library/Research and production prompts are untouched.

## Resource and stopping guards

Freeze these operational bounds before native calls; do not relax them afterward.

| Check | Bound / action |
| --- | --- |
| Whole-host swap growth | More than **512 M** above each stage's starting `vm.swapusage` used value stops the owned worker. This uses the OS-reported units, not a claim of causal attribution. |
| Application health | Any unsuccessful health sample or sample taking more than **2 seconds** stops the owned worker. |
| New human work | If live chat/transcription becomes active, stop the trial; store only the activity boolean, never private run contents. Monitoring failure also stops it. |
| Image latency | More than **60 seconds** per generation stops at a synchronized callback or after decoding; entire worker times out at **300 seconds**. |
| Chat response | Exact READY, no protocol error and no more than **10 seconds** for each declared probe; otherwise stop. |
| Chat residency | The exact daily profile must be reported loaded before and after every attempted/completed image; absence stops the trial. |
| Process and output | Cancellation must signal the owned session, reap it and confirm absence. Successful batch must contain exactly four complete matching PNG/metadata/hash records, four step events each and terminal exit zero. |
| Policy | A different cache setting, precision, model revision or package fails; no automatic alternate candidate. |

One-second RSS/swap/health/activity sampling is trial measurement, not job-progress
polling. Actual image progress remains callback events. Health/residency reads do
not send a model request. On a safety signal, retain cancelling/failure evidence
and wait for the owned process to exit; sending a signal alone is insufficient.

Record actual MLX live/cache/peak counters, sampled RSS, host swap, normal chat
before/after and read-only Chromium/WebKit composer responsiveness during the
batch. Label the browser measurement as headless, not iPhone acceptance. Compare
the four original I0 image timings/output hashes without replacing any baseline.
No uncached-system timing is claimed after model download/hash verification.

These bounds qualify only this small sequential workload and loaded daily profile
on this Mac. They do not establish safety for every chat model/context, concurrent
decoding, unbounded batches or autonomous workflows. Other host activity is not
controlled; a swap guard failure can be inconclusive about the model alone.

## Evidence and review

Add meaningful guard tests and retain both real cancellation attempts, recovery
outputs, sampler/event traces, exact source/settings/lock hashes and all failures.
Run repository checks and full browser regression; preserve old generated evidence
and frozen inputs separately. Verify installed app/source/static/interpreters,
Ollama version and normally verified local/HTTPS health after the trial. No
production service restart, image deployment or schema/API/UI change is part of I1-0.

Deliver `IMAGE-MEMORY-REPORT.md` and stop. If the policy passes, propose I1-A/B
durable execution and Images together; a passing resource probe is not that release.
