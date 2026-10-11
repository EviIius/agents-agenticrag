# Image memory qualification I1-0 report

10 October 2026. Isolated native resource test; no image feature deployed.

## Summary

The frozen 1 GiB unused-allocation cache policy passes all five declared stages.
Four 1024-square images complete with the intended daily chat profile reported
loaded before and after every image, without measured stage-relative swap growth.
Median generation is 9.47 seconds; decoded pixels match their original I0 samples
exactly. The policy does not cap live allocations, which still peak at 18.66 GB.
This qualifies the small tested combination, not a production queue or all models.

## Done-when checklist

Evidence paths below are relative to `artifacts/image-trial/i1-0/` unless stated.

| Item | Status | Evidence |
| --- | --- | --- |
| Freeze original inputs and one bounded policy before native work | Pass | `manifest.json`; prepared source commit `64f3f56`; `docs/IMAGE-MEMORY-PLAN.md` |
| Reuse pinned engine, environment and original weights | Pass | `preflight.json`; same 18 model files, 15,980,140,843 bytes; no redownload |
| Unchanged READY probes, without sampling or keep-alive overrides | Pass | `chat-before-summary.json`, `chat-after-summary.json`; 3.159 s and 0.040 s |
| Cancel during initialization and synchronized denoising | Pass | `cancel-init-summary.json`, `cancel-generation-summary.json`; exits −15; reaped and absent |
| Recover and complete all four original photograph/text jobs | Pass | `recovery-batch-summary.json`; four PNG/metadata/hash pairs and four actual step events each |
| Intended chat residency immediately before/after every image | Pass | Eight worker residency events; retained `/api/ps` metadata; unchanged daily 32K profile |
| Frozen resource guards | Pass | `results.json`; 45 health/swap/activity samples; no safety guard violation |
| Cache setting and actual allocations measured | Pass, bounded scope | `images/recovery-batch/*.json`; verified 1 GiB setting/end cache; 18.66 GB peak allocation |
| Original sample comparison and Codex inspection | Pass, four samples only | `output-review.json`; all decoded pixels identical; changed PNG metadata retained |
| Read-only browser focus during native batch | Limited observation | `browser-during-trial.json`, `browser-overlap.json`; first Chromium assertion fails on an intentionally blocked startup write |
| Separately corrected read-only browser measurement after batch | Pass, limited observation | `browser-readonly-after-trial.json`; settings PATCH blocked, composer focus succeeds; no physical phone result |
| Meaningful resource/control tests and repository checks | Pass | `control-tests.log`: 26 tests; `make-check.log`: 480 Python, 39 frontend; lint, types, contrast and API checks |
| Full unchanged browser regression | Pass | `make-e2e.log`; 463 passed, three existing skips, 38.1 minutes |
| Final original-evidence and installed-app preservation | Pass | `preservation-final.json`, `regression-storage.json`; 505 installed files and 5,458 earlier tracked artifacts unchanged; normal local/HTTPS health passes |

## Changed files

- **Isolated worker:** `image_worker/memory/{worker.py,run.py,guard.py,trial.json,
  test_guard.py,README.md,browser-probe.cjs}`. Reuses I0's native engine and
  supervised subprocess controls. No production server or frontend edits.
- **Docs:** frozen `IMAGE-MEMORY-PLAN.md`, this H4 report, the current-state entry
  in `DEFERRED-FIXES.md`, and scope/closeout amendments in `AGENTS.md`.
- **Evidence:** this checkpoint's manifests, preparation/test logs, five native
  stage summaries, requests, worker events/receipts, actual PNGs and metadata,
  decoded-pixel review, browser attempts, gallery and preservation receipts.
- **Installation:** private source/requests/output directories only. Existing I0
  interpreter, package lock and shared model weights reused. No deployment.

## Deviations from SPEC.md

The named image trial and two unchanged READY probes are authorized by the
10 October amendment. Production model-call rules, prompts, API, schema,
sampling precedence, default model and runtime are unchanged.

Initial source lint/formatting and a formatter path invocation were corrected
before freezing or executing native work. Preparation observations remain in
`preflight.json` and the initial/final lint evidence. They are not discarded
native trials or changes made after a favorable image result.

The first separately frozen browser measurement incorrectly treated any blocked
write as a failed read-only probe. During the actual batch Chromium loaded and
focused the composer, but one startup write was deliberately aborted and caused
that measurement to exit 1; WebKit loaded/focused with no attempted writes.
The original source, manifest, log and failed result are retained under
`browser-attempt-1/` and the original browser evidence files.

Only the separate browser measurement was corrected: preserve the write blocker,
record safe method/public-route classifications, and qualify HTTP/focus rather
than require zero attempted writes. Its separately frozen follow-up passes
**after**, not during, generation and observes a blocked `PATCH /api/settings`.
The first attempt did not record its method, so that route is not proven for it.
Neither attempt executes an API write or model call. Native source, cache policy,
guard bounds, stage order and original test gates remain frozen and unchanged.
These results do not prove normal Chromium startup side effects during generation.

## Runtime observations

MFLUX 0.22.0 / MLX 0.32.3, Python 3.13.15, pinned FLUX.2 klein 4B revision,
8-bit eligible layers, bfloat16 compute, four steps, guidance 1.0, 1024×1024 and
the original seeds 42/1337. No cache clears, low-RAM callbacks, component eviction,
model unload or keep-alive override are used.

| Output | I1-0 generation | Original I0 generation | Decoded pixels |
| --- | ---: | ---: | --- |
| Photograph, seed 42 | 9.404 s | 16.716 s | Identical |
| Photograph, seed 1337 | 9.491 s | 11.534 s | Identical |
| Text, seed 42 | 9.452 s | 9.947 s | Identical |
| Text, seed 1337 | 9.607 s | 9.709 s | Identical |

Median is **9.472 s**, nearest-rank p90 **9.607 s**, n=4. Recovery batch takes
39.901 s end to end, including worker/model preparation and output handling.
Original I0 timings span fresh-worker and resident histories; the table is not
a controlled causal speed comparison. Model-file verification warms file caches;
no uncached startup benchmark is claimed. PNG bytes differ because embedded
metadata differs, while decoded RGB pixels and their hashes match exactly.

At output checkpoints live allocation is about 8.56 GB, cumulative MLX peak
**18,657,035,774 bytes (18.66 GB / 17.38 GiB)**, and unused cache **1,073,741,824
bytes (1 GiB)**. I0's resident end cache was about 31 GB. Lower cache reuse does
not imply a lower peak of live tensors. The API reclaims excess free cache on a
subsequent allocation and does not impose a hard host/GPU/Ollama memory cap.
[MLX cache API](https://ml-explore.github.io/mlx/build/html/python/_autosummary/mlx.core.set_cache_limit.html).

All three native stages begin and end at OS-reported swap used **2104.12 M**;
maximum observed positive growth is zero. Existing swap is not zero. There are
45 one-second health/swap/activity samples; all health requests succeed, maximum
health request time 2.32 ms. Sampled process RSS is retained but is not Metal
memory or a true instantaneous peak. No human chat/transcription activity or
monitoring error is reported by the sampled booleans.

The normal daily chat profile reports 32,768 context tokens and 21.83 GB in
`/api/ps`, and stays
loaded through both cancellations and the four-image batch without an explicit
refresh. READY passes before and after. The after probe caches **14 of 15 prompt
tokens**, so its 40 ms latency is not evidence for real conversation latency or
simultaneous chat decoding. Exactly those two answer calls are made.

During-batch limited headless measurements: Chromium composer visible/focusable
at 94.7/16.1 ms; WebKit at 150.4/98.4 ms. The after-batch limited probe records
75.6/13.8 ms and 97.6 ms with successful focus. Raw frame deltas are retained.
These are warm local browser observations with API writes blocked, not measured
iPhone loading or a physical iPhone keyboard pass.

## Test output

- Isolated controls/guards: **26 passed**. Covers stage-relative swap growth,
  delayed/failed health, human activity, unknown units, strict READY protocol,
  residency and owned-process signal/reaping behavior; original I0 controls kept.
- `make check`: **480 Python and 39 frontend tests passed**; lint, types,
  74 contrast token pairs, motion checks and generated API checks pass.
- `make e2e`: **463 passed, three existing skips**, 38.1 minutes. No tests,
  timeouts, assertions or skips changed.
- Final preservation: **505 installed files**, three server environment files,
  transcription interpreter selector, **7,296 original inputs**, **204/214 earlier
  frozen files**, both original nine-file image attempts and all **17 current
  frozen files** verify unchanged. Existing image Python and all 56 package
  versions match I0; all 18 model files rehash successfully. All 17 native PNGs
  from both checkpoints revalidate, and both browser measurement sources remain
  separately preserved.
- Live local and normally verified Tailscale HTTPS health: pass. Ollama remains
  **0.35.0**; no application deployment or service restart occurred.
- Privacy audit: **2,040 paths, no failures** (`privacy-audit.log`). Codex
  inspected all four native images and sampled the new narrow/tablet settings
  screenshots, which show the fake runtime. Capture routes and fixtures remain
  synthetic; the audit does not automatically establish image-content privacy.

## Screenshots and output review

`artifacts/image-trial/i1-0/gallery.html` shows every native output and its exact
prompt, seed and measured time. Four native PNGs remain unchanged under
`images/recovery-batch/`. Codex directly inspected each: requested mug/notebook
subjects and FIELD NOTES text/colors match, with no defect flagged in these four
samples. This is Codex's review, not an invented user or phone acceptance. I0's
other sample defects remain open; this smaller resource test does not regrade them.

All **5,458 earlier tracked artifacts** are restored to their original bytes.
The **392 rewritten outputs** remain in the ignored local archive
`tmp/image-trial/i1-0/generated`; **23 new JSON metrics** and **40 newly generated
synthetic settings screenshots** are retained under this checkpoint. Hash mappings
are in `regression-storage.json` and `generated-new-files.json`. No earlier report
is replaced. No real inputs, recording/document names, private text, screenshots
or Library files are used as trial evidence.

## Decision and next steps

**Pass I1-0 for the tested sequential workload and loaded daily profile.** One
candidate, four samples and a tiny cached chat probe do not qualify arbitrary
loaded models, full contexts, concurrent decoding, longer batches or workflows.

Proceed next to the concrete I1-A/B scope in `IMAGE-INTEGRATION-PLAN.md` after
this review: durable job/artifact state, supervised invocation, cancellation/reaping,
SSE replay, restart reconciliation and a lazy Images/Jobs UI. Enforce explicit
resource admission; do not silently unload the user's models to fit an image.
Keep initial image generation to the tested settings/engine and one invocation
at a time until additional settings/model combinations are measured. Reference
editing needs its separate input, storage and preservation checks before exposure.

For the first integration, prefer one owned worker process per image invocation,
with capacity released only after exit/reaping. Keeping the native engine alive
indefinitely would retain allocations while users switch chat models. Existing
chat and transcription managers have separate semaphores, so an image-only lock
would not establish shared hardware admission. Integrate admission at actual
native-call boundaries, preserving existing request payloads and allowing network
waits between calls to release capacity. Test cancellation while waiting as well
as during work; a disconnected HTTP request must not abandon the owned process.

Then build ordered recording-to-meeting-pack drafts, followed by image variants
and human selection. Automated factual output remains a reviewed draft: the failed
grounding candidate is still unqualified, Research remains shelved, and this image
checkpoint authorizes no workflow/agent calls.

## Open questions for Jake

I1-0 stops for the review required by its plan, AGENTS.md and SPEC §H4. The next
concrete scope is the existing I1-A/B durable jobs and Images proposal; no additional
model or package is proposed. No new native trial or product deployment follows
automatically from this resource pass.
