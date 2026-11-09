# Local-AI computer-use checkpoint — 8 November 2026

## Summary

The installed daily Qwen profile now selects a real app-opening operation through
Aether's native Ollama adapter. The fixed host primitive opened and verified
foreground Notes and Messages. This is isolated trial code, not live chat wiring.
The Messages reader is still unqualified: layout discovery is repaired, but its
modifiable-value exclusion rejects both current text areas. Nothing was sent.

## Done-when checklist

| Item | Status | Evidence |
| --- | --- | --- |
| Correct helper permission identity | Pass for each tested exact build | Native Settings Add selected exact bundles; unrelated switches unchanged |
| Qwen selects Notes | Pass, retained decision | Original Notes HTTP request / `notes.summary.json`, 8.141 s inference |
| Notes actually in foreground | Pass after host repair; saved decision replay | `notes-v2.summary.json`, PID 8575 equals foreground PID; 0.152 s replay, zero extra inference |
| Fresh Qwen → Messages → verified foreground | Pass | `messages-v2.summary.json`, PID 1471; 3.908 s inference / 4.057 s task |
| Actual native requests/settings | Pass, two requests total | Both payloads: num_ctx 32768, keep_alive 30m, no sampling overrides or explicit think value |
| Resource snapshots | Pass | Cold start 94%→65% memory free; zero swap before/after both tasks; snapshots, not peaks |
| No script/path/input authority from model | Pass | Strict two-app schema, fixed Apple paths/IDs, OS foreground verification, refusal/negative tests |
| Reader layout diagnosis and repair | Pass offline | Same ancestor roles, two rather than eight current areas; saved native role-only replay passes new guard |
| Private candidate collection | **Refused / unqualified** | Original permission and layout refusals retained; dynamic read `unavailable`, no candidate returned |
| Exact cause of remaining exclusion | Established for current controls | Capability-only receipt: both expose a settable AXValue; reader excludes both before snapshot |
| Recipient/thread/latest incoming identity | **Not qualified** | No private candidate, parser or model context exists |
| Live Aether chat, clicking/typing, sending | **Not enabled** | No new route, UI, server registration, deployment or send |

## Changed files

- Server: new `assistant/app_open.py`, strict intent and foreground-receipt
  contracts, existing native provider reuse, owned helper cancellation.
- Tests: `test_app_open.py` and `test_app_open_trial.py` cover target/payload,
  invalid/extra operations, refusal, exact identity, executable hashes, cancellation,
  phase order, durable budget and first-failure stopping.
- Native tools: `OpenApp.swift`; separate `ReadProbeDynamic.swift`. The original
  ten-file reader source and both earlier sealed builds remain unchanged.
- Scripts: explicit app-opening trial; separate dynamic-reader build and compiled
  fixture checks. No new package, dependency lock, ordinary prompt or provider edit.
- Docs/AGENTS and sanitized evidence in `artifacts/assistant-app-open-20261108/`
  and `artifacts/assistant-as1b-20261105/`. Raw receipts and HTTP payloads stay private.

## Deviations from SPEC.md

Jake directed Codex to keep going until local computer use is possible, then
delegated permission setup directly. The bundled Computer Use skill was used for
System Settings only; it was not used to inspect Messages, read its text, or stand
in for the local AI during the proof. Native trials use the fixed app-owned code.

App opening was separated from the unfinished private-reader gate. It needs no
conversation identity or text access, so blocking it on a Messages parser added
no protection. Reading/replying still retains those gates. This does not qualify
AS2 search/read/reply tasks, AS3 sending, general screen control or UI integration.

The original Notes trial failed foreground verification despite a correct model
decision. Its first-failure rule prevented the second request. Source/build/result
remain at `dea4f5f5`. V2 serializes AppKit's concurrent open callback onto the main
queue with its activation observer. This removes a real data race; the first
uninstrumented failure does not prove it was the only cause. V2 replayed the exact
saved Notes decision without new inference, then ran one fresh Messages task in
its own declared ledger. Total actual model calls across both scopes: **two**.

## Runtime observations

Adding the exact sealed helper via Settings resolved permission refusal. The
earlier TCC entry's path was not inspected; a cdhash mismatch is a supported
diagnosis, not proof of which earlier entry Jake had enabled. All trial helper
access is off again after testing; ChatGPT/Claude/Codex/Gemini entries were unchanged.

The role-only pane changed from 34 nodes/eight areas to 16 nodes/two areas while
all surrounding ancestor roles matched. Requiring the old content shape therefore
rejects the current pane. The new guard finds a bounded number of leaf areas
within the same pane and still refuses text fields and changing state.

The dynamic read then returned `unavailable`. A separate one-shot diagnostic
requested only known capability-presence booleans and error/modifiability flags,
with no text values. Both current areas report AXValue as settable and advertise
character-count/range APIs. The reader excludes all settable areas and then
refuses an empty selection. Modifiability alone does not establish that a control
is an editor or a message. Bounded-range availability is advertised, not yet
proven by a successful private range read. No candidate is reclassified as a
message, and no private title/description/body/identifier enters logs or Git.

Original stopped scopes remain separate: B1 two requests, permission repair one,
dynamic read one. The role-only diagnosis and capability diagnosis each used one
fresh request. Their unused refusal slots were not spent after failure. No request
was retried in its original ledger; all private receipts are retained.

## Test output

- **139 focused Python cases pass**, including 27 new app-opening/operator cases.
  Lint and strict typing pass for the new server/test files.
- Three invalid-argument checks pass on each compiled opener version; no app opens
  in these offline tests. The corrected native operations are reported separately.
- Dynamic reader: **14 compiled layout checks**, **31 compiled privacy/protocol
  checks**, **five fake operator checks**, and the saved role-only shape replay pass.
- Capability diagnostic: valid invented receipt plus **five negative validation
  checks** pass, including rejection of an unexpected text field.
- Full application check and preservation results are recorded in the final
  verification evidence alongside this report. No new browser suite is claimed:
  no UI or endpoint changed; the earlier 22-case Chromium/WebKit result is historical.

## Screenshots

No real Messages/Notes screenshot was captured. Settings was controlled through
the SDK's accessibility state; none of its generated screenshots is committed.
OS identity/foreground receipts are the native action evidence.

## Next implementation checkpoint

The first real operation works. To make it available in Aether, integrate this
qualified app-opening primitive into the existing default-off task/chat path,
with actual status, Stop and failure states; retain the fixed two-app allowlist.

For Messages, prepare a read-only contract that records AX modifiability as metadata
rather than equating it with authority to type. Review the exact pane/composer
exclusion and recipient/latest-message evidence before further private collection.
If the API supplies no reliable identity, propose a specific alternative bridge;
do not infer one from display names, content, paths or a model guess. No send is
permitted until its exact recipient and final text are approved.
