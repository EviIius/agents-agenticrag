# Workflow native repair report

## Summary

The original failed trial is intact. A separate frozen recipe carries the
original brief into both Generate steps; two complete native runs produce faithful
drafts and pass reload, approval, edited saving and raw-output checks. The native
trial stops after six calls when the cancellation probe misses a short running
window. A third finished draft again broadens the supplied materials claim.
**The trial is not qualified and consistent factual fidelity is not established.**

## Done-when checklist

| Item | Status | Evidence |
| --- | --- | --- |
| Original brief in both writing steps | Pass for recipe | All six exact captured requests; both source and upstream outline bindings verified in `execution-analysis.json` |
| First two outlines/drafts preserve facts and scope | Pass for these two runs | Retained raw outputs and Codex manual reviews in `run-1/2-fact-check.json`; original baseline failed review |
| Consistent factual fidelity | **Unresolved** | Third unexpectedly finished draft adds “all necessary materials”; no automatic factual qualification |
| Real Studio SSE capture | Pass | 149 actual browser events captured across the first two native runs; offline observer also passes |
| Listener/runner RSS capture | Pass | PID ownership + descendants; actual process RSS snapshots and offline negative/matching checks |
| Clean driver / stream shutdown | Pass for completed native streams | Driver exits after failure without forced interruption; six closed streams; cancelled-close negative check retains error honestly |
| Review reload / unchanged approval | Pass | First paused review survives reload; Save/export value equals raw draft |
| Edited review / saved value / original outputs | Pass | Second reviewed value includes exact synthetic suffix; raw outline/draft remain unchanged |
| Native cancellation during generation | **Not demonstrated** | Existing DOM-running probe times out after the short draft finishes; failure retained, no retry |
| Recovery / single-block history isolation | Not run | First-failure stop after six calls; seventh call not made |
| Corrected cancellation trigger | Offline pass only | Prospective observer clicks a visible enabled Cancel control on actual node.text; fake partial output and no downstream execution verified |
| Bounds / defaults / preservation | Pass | Six of seven maximum calls, 306.16 seconds of 600; existing num_ctx only, same runtime/profile; product source and installed files unchanged |

## Changed files

No product server, web, prompt, template, dependency, schema or provider source
changes. User-authored example prompts and trial-only capture/driver changes are
under `artifacts/workflow-studio/native-trial-repair/`. Their pre-inference hashes,
exact requests, NDJSON, original inputs, raw outputs, durable snapshots, manual
reviews and measurement results are retained separately from the first trial.
New plan/report, AGENTS authorization/closeout and the deferred-list update record
actual progress. Prospective cancellation code is separate from executed source.

The recipe is a correction to this explicit graph, not a silent rewrite of stored
user workflows or built-in templates. Both use existing variable binding. Human
review remains required before saving factual drafts.

## Deviations from SPEC.md / reviewed plan

The first offline observer started a fake run by API without selecting it in the
builder. The server paused, but the editing canvas did not show an active run.
That zero-native-call failure/source is retained in `offline-1/`; launching through
the actual Run UI repairs the precondition without relaxing the assertion.

The cancellation probe inherited from the original trial awaited a DOM running
state. The third draft streamed for about half a second and finished before that
condition was observed; the assertion timed out. No assertion, timeout or required
control behavior was weakened. The original executed files stay frozen. The
prospective event-triggered UI probe is tested against the fake runtime only;
**no additional native inference followed the failed gate.**

The unexecuted single-block sample was updated before inference to supply both
`start.brief` and `outline.text`, required by the new recipe's dependencies.
It is not counted as an executed recovery test.

## Runtime observations

Installed Ollama remains 0.35.0 and the runtime-reported daily profile remains
`qwen3:30b-a3b-workbench-32k`, context 32,768. No temperature, seed or other sampling
value is introduced. Both Generate blocks receive the same original brief; each
Draft receives its own actual outline. Only six approved answer requests occur;
no title, Search, embedding, native image or load/unload call occurs.

First-call wire TTFT is 1.788 s; later calls range from 0.140 to 0.280 s. First-call
wire total is 2.254 s; subsequent calls range from 0.590 to 0.724 s. These cold/warm
observations and the first report's timing are not a matched latency benchmark.
The complete-run elapsed values include Codex's manual review time and UI actions.

Actual CPU process RSS is now captured for the listening runtime and descendants.
This is not unified-memory/GPU allocation, peak host memory or mixed image/chat
qualification. Global swap/vm_stat snapshots remain separate.

Two complete drafts contain exactly the workshop name, time, participant limit,
price, pencils and paper, without the previous recurrence or broader-material
claims. Their approvals and saved edit work. The third, which was intended to be
cancelled, instead finishes with “includes all necessary materials: pencils and
paper.” Read-only manual review flags that broader claim. Passing two samples
therefore does not cure the model's tendency to expand source scope.

## Test output

Offline capture controls: pass, zero native calls; fragmented NDJSON and cancelled
closure recording tested. Corrected actual fake-runtime event observer: pass
with five node.text events. Prospective actual-event cancellation: pass with nine
node.text events, a visible enabled UI control, preserved partial draft and zero
review attempts; zero native calls. These passes are distinct from native results.

Native trial: **failed and stopped at six calls**. Two full runs completed; third
running-state assertion failed. Cleanup cancels the paused synthetic run; all six
model streams had already completed, so cleanup does not prove in-flight cancel.
The recovery/single-block test stays unexecuted. Readline now closes normally.

No application source changed since the frozen CI-C candidate. Its existing full
regression evidence remains applicable: 654 Python / 104 frontend checks, 615
browser passes with three existing skips, successful build and original thresholds.
Those fake/browser checks do not replace the missing native cancellation check.
G9 and earlier Search/meeting-summary support failures remain unresolved; no broad
prompt trial or Research restart is part of this repair.

## Screenshots

`review-1-synthetic.png` and `review-2-synthetic.png` show actual native paused
review, including the second host edit. Only synthetic input/output is captured.
The full native video stays outside Git, with path/hash in `videos-outside-git.json`.
No actual-phone or VoiceOver pass is claimed.

## Open questions for Jake / next step

Do not merge as a fully verified native automation release yet. The remaining
control check is a minimal native cancel/recovery pair using the event-triggered
probe, the same recipe/profile and explicit source samples. That requires a new
reviewed continuation after this declared stop, not a hidden retry of this trial.
No more broad factual prompt loops are proposed. Preserve original fields and
human review; for exact factual outputs prefer host-owned formatting of explicit
Start fields over model-written assertions.

Main/live remain unchanged. The branch provides a saved review checkpoint; final
merge and publication still require Jake's explicit okay. If merging the UI while
retaining these documented native limitations, that narrower decision must be
explicit rather than reported as a complete native pass.
