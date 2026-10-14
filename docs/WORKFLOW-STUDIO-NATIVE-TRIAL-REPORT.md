# Workflow Studio native trial report

## Summary

Frozen CI-C source `f8e301c2` drove the installed daily Qwen profile through a
saved synthetic graph. Exactly two ordered calls completed, the second received
the first output unchanged, and the builder paused at review. **The semantic gate
failed:** the announcement invented recurrence and broader material provision.
Inference stopped immediately after Codex rejected it; no retry or expansion.
This is a partial execution result, not a qualified native workflow pass.

## Done-when checklist

| Item | Status | Evidence |
| --- | --- | --- |
| Existing runtime/capability/context/defaults | Pass | `runtime-metadata.json`: Ollama 0.35.0; completion capability; context 32,768; saved sampling defaults empty |
| Frozen graph and inputs | Pass | `frozen-definition.json`, `frozen-inputs.json`, hashes |
| Ordered calls / exact variable binding | Pass for first run | Two captured `/api/chat` requests; draft ends with exact outline; `execution-analysis.json` |
| No added sampling / other native calls | Pass | Both options contain only existing `num_ctx:32768`; keep_alive 30m; no title/search/tools/image calls |
| Visible streaming / paused review | Observed, limited instrumentation | Chromium driver awaited nonempty live preview and paused block; retained video/frame; both model streams and 19 durable graph snapshots retained |
| Six supplied details, no extra event facts | **Fail** | Both outputs introduce “every Saturday” and “all materials provided”; Codex manual review in `run-1-fact-check.json` |
| Reload / approve unchanged / edited save | Not run | Semantic stop occurred before these operations |
| Second complete run / consistency | Not run | Stop rule, no additional calls |
| Cancel during second inference / retain partial text | Not run | Both calls finished before semantic review; failure cleanup cancelled the paused run only |
| Single-block recovery / normal-history isolation | Not run | Stop rule, no additional calls |
| Runtime connection/capacity released | Pass for completed streams / cleanup | Both streams closed; status showed capacity false at two calls; Save attempt count remains zero |
| Budgets | Pass | 2/7 native calls; 6.565 seconds from run creation to paused review; termination within the ten-minute bound |
| Timing / byte counts / memory | Partial | Exact wire/node timings and bytes retained; global vm_stat/swap snapshots present; RSS collector and browser delta timing unavailable |
| CI-C regression / main and installed app intact | Pass | CI-C H4: 654 Python, 104 frontend, 615 browser passes / three existing skips; preservation and health manifests |

## Changed files

No product source changes for the trial. Trial-only `native_host.py` and
`driver.mjs` capture traffic and drive Chromium. Synthetic graph/input/output,
request/NDJSON, durable run/step/event snapshots, analysis, hashes and review are
under `artifacts/workflow-studio/native-trial/`. The SQLite trial folder and video
remain outside Git under `~/.local/share/workbench/qa/workflow-studio/`.
Reports, the plan's execution status and AGENTS closeout are updated.

## Deviations from SPEC.md / reviewed plan

The implemented catalogue does not yet have a distinct Compose text block.
Existing Save directly binds `{{review.value}}`; no Compose behavior is claimed.
This clarification was documented before inference, without an engine change.

First setup issued zero inference calls: appending the trial-only status route
after the existing SPA fallback returned HTML. The original setup/source/results
remain in `setup-1/`. Moving that auxiliary route ahead of the fallback and using
a second fresh synthetic database repaired the harness, without product changes.

The event observer watched legacy `/api/workflows/events`, while Studio uses
`/api/workflows/stream`. `timeline.json` is empty; no fabricated browser-received
SSE timeline or first-visible-token time is reported. Native NDJSON and durable
server snapshots are retained separately. The runtime RSS collector returned no
matches; that is unavailable RSS, not zero memory use. No inference rerun was
used to repair these measurements. After failure cleanup completed, the driver's
readline handle remained open; Codex interrupted that harness process. No
additional model call or product behavior change followed.

## Runtime observations

The profile was initially not loaded. First-call wire time to text was **3.750 s**,
including 3.571 s reported model load; the second was **0.187 s**, with 0.002 s
load. Generate node times were 4.906 / 1.640 s. The run reached review in 6.565 s.
This one cold/warm pair does not establish general latency or model quality.

| Call | Wire total | Request bytes | Response bytes | Output UTF-8 bytes | Output tokens |
| --- | ---: | ---: | ---: | ---: | ---: |
| Outline | 4.863 s | 518 | 14,478 | 419 | 99 |
| Draft | 1.551 s | 697 | 17,706 | 565 | 121 |

Swap was 952.88 MB before and after; whole-machine VM observations include other
apps and do not qualify image/chat coexistence. No native image job was started.

All six supplied details appear, but lexical completeness does not prove fidelity.
The brief named the workshop Cobalt Saturday without a recurring schedule; the
outline added “Meet every Saturday” and the draft propagated it. Providing pencils
and paper became a claim that all materials were provided. The first output thus
introduced drift and the next faithfully copied that drift. This is a model/source
fidelity failure, not a lost variable or server sequencing failure.

## Test output

Native trial: **failed and stopped after two calls**, first manual semantic gate.
The driver retained the failed result and cancelled the paused synthetic run.
Both raw Generate outputs remain; Save never started. The other five permitted
calls were not made. Cleanup is not the planned cancellation-during-inference test.

CI-C required gates passed before execution: `make check` 654 Python / 104 frontend;
`make e2e` one full invocation, 615 passed / three existing skips / zero failures;
production build passed. These fake/browser tests do not replace native semantic
acceptance. No native Web evaluation, default switch or Research restart occurred.

## Screenshots

`artifacts/workflow-studio/native-trial/paused-review-video-frame-synthetic.png`
is a frame extracted three seconds before the actual Chromium recording ends,
inspected by Codex. It shows completed Generate blocks and waiting review.
The video hash/path is in `video-outside-git.json`; all text is synthetic.
No physical iPhone or VoiceOver result is claimed.

## Open questions for Jake / recommendation

Keep the review boundary and preserve the original brief as authoritative input
for every factual writing step. A proposed next bounded test should pass both
original brief and outline to Draft, with an explicit comparison at review;
for repeatable announcements, host-owned fact fields and a template avoid a
model rewriting dates/prices/counts. Correct the event/RSS harness before any
new trial. Those changes and a retest need a reviewed scope; this stop does not
authorize another prompt experiment or full native qualification.

CI-C is reviewable on `codex/workflow-studio`. Main/live app stay unchanged.
Final merge and publication still require Jake's explicit okay.
