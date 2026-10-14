# Native cancellation and recovery report

## Summary

The remaining native control pair passes on the isolated branch, using the same
saved graph, original brief, outline sample and installed daily Qwen profile.
Actual first-text SSE triggers a visible, enabled Cancel control; an incomplete
native stream closes and its partial output is retained. An identical second
single-block run completes, survives reload and stays outside normal history.
Its one answer passes manual source review; general factual reliability remains
unqualified. Main/live remain unchanged.

## Done-when checklist

| Item | Status | Evidence |
| --- | --- | --- |
| Actual native cancellation through UI | Pass | `cancel-action.json`, native screenshot/video, actual node.text event; no fabricated delay/progress |
| Cancelled partial output / no downstream execution | Pass | One UTF-8 byte (“C”) retained; Review/Save attempts zero; sample ancestors make no model calls |
| Incomplete native stream closes | Pass | First request has no done event, completed_stream false, close_error null and actual close timestamp |
| Capacity release before recovery | Pass | `after-cancel-status.json`; first stream closes before second request begins |
| One single-block recovery | Pass | Second identical native request completes with normal stop; node complete; no extra calls |
| Samples and original-source bindings | Pass | Both requests exactly match frozen Draft with original brief and explicit outline; ancestor attempts zero |
| Test/history isolation and reload | Pass | Normal history empty; output unchanged across reload; both runs mode test |
| Manual source review | Pass for one recovered output | All six details retained, no extra event claim; `recovered-fact-check.json` |
| Bounds / sampling / preservation | Pass | Two calls / 139.27 seconds (<180); same request bodies and existing num_ctx only; frozen source verified |
| Main/live/G9/phone limitations | Retained | Product source f8e301c2 unchanged; no general grounding, phone or VoiceOver pass |

## Changed files

No product server/web/schema/dependency/runtime/prompt/template change. The
trial-only observer now checks the control is visible, enabled and hit-testable;
it retries only on subsequent actual text events if temporarily covered. The
existing DOM-timing probe is preserved in earlier trials. Native capture guard
is narrowed to two calls / three minutes. Driver, exact inputs, graph, SSE,
requests/NDJSON, closure, snapshots, measurements and source hashes are under
`artifacts/workflow-studio/native-controls/`. Plan, H4 report, AGENTS and the
current deferred list are updated. Synthetic videos and trial database remain
outside Git.

## Deviations from SPEC.md / reviewed plan

The first offline pair cancels correctly but tries to configure the second test
while following the previous run. The resulting absent Block name assertion,
source/log/output and video are retained in `offline-1/`; zero native calls.
Explicitly closing the previous Run panel restores the editing precondition.
The final frozen offline pair then passes both operations without weakening any
assertion, timeout or release target.

Both native operations now use the real builder **Test this block** menu and
sample fields, rather than starting by API and racing a new page load. Triggering
Cancel from actual streamed text repairs the earlier missed running window.
No provider slowdown, extra prompt, sampling change, timer-generated stage or
additional model call is used to create a cancellable window.

## Runtime observations

Ollama remains 0.35.0; profile is the existing runtime-qualified
`qwen3:30b-a3b-workbench-32k`, context 32,768. Both model requests are identical
and contain only the existing num_ctx option. Keep-alive and saved user defaults
are copied unchanged into the isolated synthetic database.

First native text arrives 1.819 s after request start. The UI Cancel click follows
3.22 ms later; the native stream closes another 9.65 ms later without a completion
event. The retained draft is one byte (“C”), so this proves early partial-output
preservation, not long-output quality. The follow-up request starts after closure,
receives text in 0.147 s and completes in 0.560 s. Its retained text is 131 UTF-8
bytes. These are observations from one pair, not a general latency benchmark.

The recovered output says the fictional workshop meets at 10:00, admits 12
participants, costs $20 and provides pencils and paper, with no extra event fact.
Earlier unsupported-material and recurrence outputs remain unchanged and visible
in their reports. One correct recovery does not qualify consistent grounding.

## Test output

Final frozen offline UI pair: pass, zero native calls. Native pair: **pass, exactly
two calls**, actual cancel/closure/capacity, recovery, sample/history isolation,
reload and manual review. No native retry or extra experiment occurs.

Application source is unchanged from the fully checked CI-C candidate; its
existing regression evidence remains applicable: 654 Python / 104 frontend,
615 browser passes with three existing skips and successful build. These suites
were not rerun for this harness-only checkpoint. Original cases, targets and
reports are preserved. G9/ordinary grounding limitations and Research shelving
remain; no deployment/default switch or new native image job.

## Screenshots

`artifacts/workflow-studio/native-controls/cancelled-native-synthetic.png`
and `recovered-native-synthetic.png` show actual desktop-native cancelled/complete
states. Codex visually inspected both. The recovered screenshot after reload has
its output row collapsed; raw answer and manual review are retained in JSON.
Offline screenshots are under `offline/`; the first failed setup is separate.
All screenshots/videos contain synthetic data. Native/offline video paths and
hashes are recorded in `videos-outside-git.json`. No physical iPhone/VoiceOver
result is claimed.

## Open questions for Jake / next step

The previously missing native cancellation/recovery gate is closed. Together with
the prior full-run approval/edit/reload evidence, this supports merging the reviewed
UI and workflow checkpoint with factual outputs requiring human review. It does
not qualify unattended factual automation, remaining WS-E blocks, pixel editing
or general web reliability. Physical iPhone acceptance of the new chat-image flow
remains pending.

Main/live remain unchanged. Final merge and publication still require Jake's
explicit okay; the isolated branch is the review and fallback checkpoint.
