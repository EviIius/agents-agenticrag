# PE0 native trial — prerequisite wait, 19 October 2026

## Summary

Jake authorized the frozen trial of at most six worker invocations by saying
“Continue” after the prepared report and concrete approval request. Source,
private worker copies and runtime version match. Preflight found **no resident
chat model**, so no attempt has been reserved and no worker has started.
The trial is ready and waiting for Jake to load the required Qwen 32K profile.

## Done-when checklist

| Item | Status | Evidence |
| --- | --- | --- |
| Native six-invocation approval | Granted | User's continuation, AGENTS.md and `authorization.json` |
| Frozen source and worker copies | Pass | Nine preparation source/report hashes; four private worker files unchanged |
| Execution instrumentation | Prepared | Compiled staging/measurement drivers; execution manifest freezes all eleven files |
| Runtime and app health | Pass | Ollama 0.35.0, healthy local app, no active chat in initial preflight |
| Required daily chat residency | Waiting | Runtime reports an empty model list; load qualified digest at unchanged 32K |
| Portrait request and retained mug input | Prepared without inference | Request hashes frozen; actual old synthetic mug descriptor verified on CPU |
| Worker invocations / reserved attempts | 0 / 0 | No launch journal or attempt reservation exists |
| Native edit quality, resources and recovery | Not run | Six-case trial has not begun; no pass or failure inferred |
| Live app/main | Preserved | No application change, deployment, load/unload request or data mutation |

Evidence: `artifacts/photo-editing/native-20261019/`. The completed offline
84-case preparation is retained separately in
`PHOTO-EDITING-PE0-PREPARATION-REPORT.md` and its original evidence directory.

## Changed files

- **Execution tools:** CPU-only fixed-case staging, per-case worker launch/event/
  residency/swap/RSS/reaping/storage recording, using the frozen controller and
  production native lock. No automatic next case or retry.
- **Docs/evidence:** native authorization, initial preflight, staged input hashes
  and this prerequisite record. The frozen worker/contracts/controller/plan and
  the nine preparation files remain unchanged.
- **Server/web/dependencies:** none. No model/runtime upgrade or new package.

## Deviations from SPEC.md

None to the reviewed scope. The plan explicitly requires the qualified daily
model to remain resident and forbids refreshing it with another call. Empty
residency is a prerequisite wait before the first attempt. Do not silently test
images alone, load a chat model through an extra call, or call this a native
image failure. This does not consume or expand the six-invocation budget.

## Runtime observations

Read-only GETs report Ollama 0.35.0, a healthy app, no active chat and zero loaded
models. No model-management, chat, embedding or image request was sent. Jake was
asked to load the existing qualified Qwen3.8 profile at 32K in Aether's Models
settings. Do not ask for the already granted trial approval again.

## Test output

- Reuse the completed **84 passing offline checks** on unchanged frozen code;
  no new complete app/browser suite or native test invocation is claimed.
- Both execution drivers compile. CPU staging validates the exact portrait
  request and the retained synthetic mug reference, without native imports.
- Initial metadata preflight used system Python lacking httpx and exited before
  inspecting runtimes or invoking a worker. The existing server interpreter
  performed the same read-only check successfully; no dependency was installed.
- Production source/static hashes, worker selectors, stopped trial ledgers,
  privacy and local/verified HTTPS health remain preserved.

## Screenshots

No image was generated or edited; there is no native output to inspect. No
personal photo, filename, recording, transcript or private chat was captured.

## Open questions for Jake

Please load the existing Qwen3.8 32K profile in **Settings → Models** and report
when it is loaded. The pending input request is a residency prerequisite; the
six-call native trial is already authorized. Preserve source/settings and stop
at the first failed required gate or rejected visual review. Human quality
acceptance still precedes any PE1 integration. PR #6 remains a draft; main and
the live app stay unchanged.
