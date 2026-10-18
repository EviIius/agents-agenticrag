# Image memory handoff — H4 report

## Summary

Jake reported image failures in chat and Brief to images on the physical iPhone.
Read-only runtime inspection found the already-qualified 32K chat profile plus
the configured Library embedding model resident. The conservative image guard
correctly rejected two models; this was not a measurement of exhausted RAM.
Jake explicitly approved automatically releasing idle embedding models.

The patch releases only configured local embedding-only models while holding
the shared native scheduler slot. It then verifies residency before FLUX starts.
The qualified chat profile and all original image admission limits remain.
Technical/release results are recorded below; physical phone acceptance remains
pending. Hermes installation/inference remains on hold for that prerequisite.

The live metadata check caught an overly strict first draft: Ollama reports the
configured embedding model with auxiliary `tools` and `thinking` flags. The final
rule requires `embedding` and permits those two auxiliary flags, while excluding
`completion` and unknown capabilities. The retained runtime-shape reproduction
fails before that correction and passes afterward; no live release was attempted
with the first draft.

## Done-when checklist

| Item | Status | Evidence |
| --- | --- | --- |
| Reproduce original rejection | Pass | `artifacts/image-memory-recovery/before.txt`, retained original reproduction source |
| Identify eligible models through configuration and fresh capabilities | Pass | `test_only_configured_embedding_identity_is_eligible`, `test_fresh_embedding_only_capability_required`, local-runtime negative controls |
| Keep the qualified chat model resident | Pass, synthetic | Full engine handoff test runs a harmless fake worker; only the configured embedding receives an empty unload request |
| Validate whole plan before any release | Pass | Unknown/64K/oversized chat and mixed-capability second embedding reject without a partial unload |
| Bind model identity and reject races | Pass | Fresh tags/digest and residency snapshot checks; alias/residency/duplicate/malformed metadata tests; unexpected post-release model rejects |
| Wait for active Library work and permit the next Library query | Pass, synthetic | Shared-lease test waits for an existing embedding request, releases residency, then calls the unchanged embedding adapter again; saved settings stay identical |
| Wait for actual release, honor cancellation, fail closed | Pass | Delayed unload, missing acknowledgement, timeout and cancellation tests; registry cache invalidation after attempted release |
| Durable progress and existing retry | Pass | `test_handoff_progress_is_durable_and_pushes_to_existing_image_stream`; chat/workflow regression tests |
| Desktop and phone-sized browser status | Pass | Eight Chromium/WebKit checks, both themes, 390/1440 widths; screenshots in `artifacts/image-memory-recovery/browser/` |
| Existing chat cancellation/SSE and workflow retry | Pass | Six Chromium/WebKit regression checks; completed text block stays on attempt 1 when failed image retries |
| Full repository checks | Pass: 721 Python / 126 frontend, 110 contrast pairs | `artifacts/image-memory-recovery/check-final.txt` |
| Build and initial JS budget | Pass | 425 build files; 254,964 gzip bytes, unchanged 256,000-byte ceiling |
| Publication and fallback | Pass, live | PR #4 merged as `799b7f4f`; 114 server / 425 static hashes match; healthy in 1.779 s; all 55 tables preserved |
| Physical iPhone check | User-confirmed pass | Jake selected “Both image paths and phone checks pass”; `artifacts/image-memory-recovery/phone-check.json` |

## Changed files

- `server/app/images/engine.py`: configured local embedding selection, fresh
  runtime identity/capability checks, empty-request release under the existing
  Capacity lease, bounded residency verification and unchanged read-only guard.
- `server/app/images/jobs.py`: passes Store to the engine and persists/pushes
  “Making room for images” through the existing preparing state.
- `server/app/main.py`: invalidates the loaded-model registry cache after a
  release attempt.
- `web/src/lib/image-state.ts` and its tests: exposes the real handoff stage
  instead of inaccurately claiming image weights are already loading.
- Both synthetic image previews, one focused browser specification and the
  new server handoff tests. No existing test assertion is weakened.
- `AGENTS.md`, this report, frozen source/build manifests, raw attempts,
  synthetic screenshots and the one-shot release controller.

## Deviations from SPEC.md

Jake's explicit policy approval supersedes only the no-automatic-unload rule
for configured, local, idle embedding-only models at image preparation.
No model-name capability heuristic, new dependency/weights, chat inference,
prompt/sampling/default/schema change or broader memory qualification is added.
Other chat/unknown models and unqualified contexts still need an explicit choice.
An image request does not delete Library documents, vectors or configuration.

## Runtime observations

The read-only diagnostic found the qualified chat digest
`09386c7af8487c073bfb845833462d30d0d48ad69428c301b909dc159c028b0a`,
32,768 context and 19,508,609,678 resident bytes, alongside a configured embedding
model reporting 5,776,426,925 resident bytes. The existing single-resident-model
qualification rejects that combination. Runtime expiry can change residency
later; the patch always obtains fresh metadata.

Pinned Ollama 0.35.0 acknowledges an empty chat request with `keep_alive: 0`
before its scheduler finishes asynchronous release. The handler returns
`done_reason: unload` before completion-capability validation, so this management
operation also works for embedding-only models. See the official pinned
[request handler](https://github.com/ollama/ollama/blob/v0.35.0/server/routes.go)
and [scheduler](https://github.com/ollama/ollama/blob/v0.35.0/server/sched.go).
The patch therefore waits up to five seconds for residency to clear; no browser
polling is added. UI updates still use the existing persisted SSE events.

The app's shared scheduler serializes its native operations. Unrelated external
Ollama clients do not participate in that lease; observed metadata changes fail
closed and the existing read-only runtime guard remains active during generation.
No claim of atomic control over external Ollama clients is made.

All qualification limits remain: exact existing chat digests, exact 32K context,
at most one resident chat, positive resident bytes at most 21,827,095,100, and
at most 512 MiB swap growth. Worker/model revision, precision, cache, image size,
step count, process ownership, cancellation and output validation are unchanged.

## Test output and preservation

- Original guard reproduction: one expected failure, retained unchanged.
- First focused handoff/admission invocation: 40 passed in 0.86 s.
- Expanded handoff/image/chat/workflow invocation: 93 passed in 9.88 s.
- Final focused handoff/admission invocation: 45 passed in 0.89 s, including
  the runtime's actual capability shape and an unknown-capability negative control.
- Exact runtime-shape reproduction: one retained failure, then one pass in 0.48 s.
- New browser status checks: eight passed in 23.2 s.
- Existing browser cancellation/SSE/workflow retry checks: six passed in 27.6 s.
- Final full `make check`: **721 Python / 126 frontend**, 110 contrast pairs; lint, format, types, coverage, API types/additivity, motion and privacy all pass.
- This narrow patch does not rerun or claim the previous entire 711-test browser
  suite. It runs all server/frontend checks and the 14 browser cases covering
  changed status, image cancellation/SSE, and workflow retry behavior.
- Initial lint/format/type failures and their corrections remain in the raw
  attempt logs. Executed source is frozen in `executed-source.json` (548 files);
  build assets are frozen separately in `build-manifest.json` (425 files).
- The first full check passed (719 Python / 126 frontend), but did not prove the
  newly discovered runtime capability shape. Its source and output are preserved
  under `pre-metadata/`; a second full check covers the corrected final source.
  The reproduction harness's initial import-path error is retained separately.
- All model/unload/embedding traffic in tests is intercepted synthetic HTTP.
  The engine subprocess test runs a tiny fake worker, not MFLUX. There is no
  new real generation, warmup, model download or native trial.

## Screenshots

`artifacts/image-memory-recovery/browser/` contains chat/gallery handoff states,
390 and 1440 widths, light/dark themes, Chromium and iPhone-profile WebKit.
Every capture uses fabricated prompts and metadata. The user's screenshots and
private media, filenames, messages and Library text are excluded.

## Publication

Published 17 October at 23:51:35 UTC after the final full check passed. Merged
main reproduces all 548 tested source and 425 tested build hashes. Both local
and normally verified Tailscale HTTPS health/workflow/image-status endpoints
pass; HTML/service-worker hashes match and production `/design` remains disabled.
The service identity, plist, interpreter, dependencies, schema 13, Tailscale
route and existing transcription/image worker controls are unchanged.

Actual installed HTTPS assets also pass Chromium and iPhone-profile WebKit
typing, Tools/Model default, long-paste undo and photo tray/viewer/remove checks
with intercepted synthetic API data, zero page errors and zero native requests.
Service workers are blocked for that interception; no new complete PWA browser
suite or physical iPhone observation is claimed. The copied observer's initial
legacy full-PWA-suite label is preserved separately and corrected in its source
and final output; the second observer invocation changes no product code or API
assertion.

Private full app/data/plist fallback:
`~/.local/share/workbench/qa/image-memory-handoff-20261017`.
Pushed source fallback tag: `checkpoint/pre-image-memory-handoff-2026-10-17`.
The tested same-schema rollback restores the old application while retaining
accepted current messages/files; it does not replace live data with an old DB.
Source/release/controller evidence is in `artifacts/image-memory-recovery/`.
No real inference or model release was performed during QA or deployment. The
automatic release runs when the user next starts an image with eligible idle
embedding models resident; actual generation and phone confirmation remain pending.

## Open questions for Jake

Jake confirmed both image paths and the requested phone checks after publication.
This closes the repair/memory-handoff phone prerequisite. No further approval is
needed to resume the already-approved isolated Hermes H0 trial; its original
structural/native gates and call limits remain. The earlier pending statements
above describe the state at publication, before this user confirmation.
