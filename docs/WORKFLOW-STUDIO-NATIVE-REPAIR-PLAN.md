# Workflow native verification repair

## Authorization and purpose

14 October 2026: after reviewing the CI-C/native report and the prioritized fixes,
Jake said “Fix them.” Continue on `codex/workflow-studio`; his subsequent question
about main is a readiness question, not merge authorization. Keep main/live intact.

Correct the failed recipe and the measurement harness, then execute one frozen,
bounded native trial. Retain the original failed graph, outputs, scores and source.
This does not restart Research or broad Search/prompt experiments. Ordinary app
prompts, templates, runtime, sampling defaults, dependencies and UI stay unchanged.
The existing green CI-C source `f8e301c2` remains the product candidate.

## Recipe correction

Use the existing Start → Outline → Draft → Review → Save blocks, same original
synthetic brief and installed daily profile. Outline extracts explicit facts only;
Draft receives both the authoritative original brief and the outline, retaining
all values and scope. These are user-approved trial block prompts, not changes to
application-authored prompts or to arbitrary user workflows. Existing variable
binding carries `{{start.brief}}` directly into both Generate steps. Keep human
review before Save. Do not silently modify stored user graphs or built-in templates.

Compare all six supplied facts and every additional event claim manually. An
outline or draft that adds an unstated fact fails. Original lexical facts are a
precheck only, not a semantic pass. Passing this sample does not establish general
model reliability; structured Start fields and host-owned formatting remain a
recommended approach for fixed facts, using existing block capabilities.

## Harness corrections and offline validation

- Observe Studio `/api/workflows/stream`, capturing actual browser node.text and
  state events, without polling or fabricated progress.
- Identify the runtime's listening PID and descendants; record only their PID,
  parent PID, executable name and RSS. An absent reading is an explicit failure,
  never zero memory use. Retain global swap/vm_stat separately.
- Close readline on every outcome and record stream closure even after cancellation.
- Separate new artifacts, database and videos; preserve all original evidence.
- Validate syntax, streaming observer and process measurements offline before native
  execution; freeze sources/prompts/settings/bounds before the first call.

## One bounded native trial

At most seven calls / ten minutes on `qwen3:30b-a3b-workbench-32k`, selected using
existing runtime metadata. Two full runs (four calls): reload paused review,
approve one unchanged, edit the other, verify exported Save value and preserved
raw outputs. Third run (two calls): cancel during actual second-block streaming,
verify partial output and no downstream execution. Test Draft alone once (one call)
with explicit outline sample and original brief; verify recovery and test-history
isolation. No native image job, title/search/embed call, load/unload or new samplers.

Stop on first protocol, semantic, control, measurement or budget failure; retain
it and execute no retry. No repeated full Web/Library eval is authorized here.
Native release accuracy gate G9 remains open regardless of this trial.

## Closeout

H4 report must separate passed, failed and unexecuted checks, exact requests,
original-brief/outline binding, manual claim review, SSE/timings/RSS, cancellation
and recovery. Verify original evidence, main and installed files unchanged, commit
and push the isolated branch. No main merge or publication without Jake's explicit
okay. Physical iPhone acceptance stays pending; VoiceOver is off the work list.
