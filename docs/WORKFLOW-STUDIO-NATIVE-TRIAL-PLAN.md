# First local-LLM Workflow Studio trial

Prepared 13 October 2026. **Executed 14 October; failed the first semantic gate
and stopped after two calls.** See `WORKFLOW-STUDIO-NATIVE-TRIAL-REPORT.md`.
The frozen plan below was executed after CI-B/C integration and its review, on `codex/workflow-studio` with a separate synthetic data folder. Main,
installed chats, service port, Tailscale and current default stay intact.

## Purpose

Verify that the builder's saved graph drives the actual installed Ollama model:
ordered calls, variable binding, visible streaming, durable outputs, human approval,
cancellation and a single-block test. This establishes execution behavior; it does
not qualify factual web answers or revive Research. Fake-runtime results alone
cannot establish this native result.

## Model and boundaries

Use `qwen3:30b-a3b-workbench-32k`, the existing daily profile. Read-only installed
metadata on 13 October reports chat capability and a 32,768-token context in
`artifacts/chat-images/ci-a/runtime-metadata-read-only.json`. Recheck metadata
before execution. No capability is inferred from its name. No model download,
new adapter, package, runtime upgrade, routing, supervisor or tool loop.

Use the existing Generate block performer and the model's existing saved defaults.
No sampling value is added by the trial. Prompts are explicit user-authored test
block text in the isolated definition; freeze the definition and exact requests
before execution. Ordinary chat prompts and requests remain unchanged.

## Synthetic graph

Start (`brief`, text) → Generate outline → Generate draft → Approve or edit →
Compose text → Save results. Both Generate blocks explicitly select that profile.
The second block uses the first block's typed output through the variable picker.
The review block is reached only after both calls finish; Compose and Save are
host operations and never call a model.

Input: “Create a short announcement for a fictional art workshop. The workshop is
called Cobalt Saturday; it meets at 10:00, admits 12 participants, costs $20, and
provides pencils and paper. Do not add a date, address or registration link.”

Outline prompt: “Using only the supplied brief, make a short outline for the
announcement. Preserve every supplied detail. Brief: {{start.brief}}”.

Draft prompt: “Write the announcement from this outline. Preserve its details and
add no event facts. Outline: {{outline.text}}”.

The syntax is checked against the builder's actual variable keys when preparing
the immutable graph. No guessed or missing reference is accepted.

## Bounded execution: at most seven native calls

1. Two complete runs of the same frozen graph: four calls total. Approve one
   draft unchanged; edit the other to include a synthetic host-authored suffix.
2. A third run: cancel during the second Generate block, at most two calls. Its
   first completed output remains saved; the partial second output is labeled
   cancelled; downstream review/save never run.
3. Test only the second Generate block once using an explicit synthetic outline:
   one call. It stays isolated from normal run history.

No retry or extra trial follows a failure. If the graph issues an unexpected call,
stop immediately. Total elapsed execution is bounded to ten minutes; cancel and
retain the diagnostic on overrun. Never count a metadata request as inference.
Do not run a native image job concurrently in this first trial. Image/chat memory
coexistence needs its own measurements; this trial cannot establish that policy.

## Evidence and acceptance

- Requests appear in graph order, with exactly two calls per complete run. Each
  second prompt includes that run's actual first output, and no other run's text.
- Both completed announcements retain the six supplied details, with no added
  date/address/link. Review raw outputs manually; retain every failure.
- Canvas/Outline show actual streamed text and real waiting/running/paused states.
  Review persists across reload; approval starts only the host steps remaining.
- The edited review value appears in saved results. Earlier raw outputs remain.
- Cancel releases the runtime connection and capacity slot; a subsequent permitted
  single-block test succeeds. It cannot continue an already-cancelled run.
- Record actual cold/warm time to first text, per-block/end-to-end elapsed time,
  request count, process-memory/swap snapshots and output byte counts. Do not turn
  these observations into a general model quality or mixed-memory qualification.
- Retain exact synthetic graph/request/output snapshots, SSE timeline, logs,
  hashes and an H4 report. Keep synthetic videos outside Git.

Before starting, verify CI-A/B/C and Studio regression evidence, the isolated data
path and the seven-call budget. Stop with results and a recommendation before any
merge/publication or expansion. Physical iPhone results are recorded only when
actually observed or supplied by Jake; VoiceOver remains outside the work list.

## Execution clarification — 14 October 2026

Jake explicitly authorized CI-C followed by this bounded trial. The implemented
WS-B/D catalogue has eight block types; a separate Compose text block belongs to
later Studio scope. This first graph therefore uses Start → Outline → Draft →
Approve or edit → Save results, with the existing host Save block binding the
reviewed value directly. The originally unspecified identity Compose step is
absorbed into Save's formatting, without a model call or engine change. Do not
claim that a distinct Compose block was tested. The seven-call budget and all
other acceptance checks remain. Retain this deviation in the report.

The isolated host reads only public runtime metadata and the selected profile's
saved sampling defaults through the installed app's model endpoint; it never
reads installed chats, files, keys or database contents. It copies those defaults
into its new trial database, preserving the request pipeline. A transport guard
counts calls before network delivery and captures exact synthetic request/response
bytes. No load/unload, title, search, embedding or native image call is permitted.
