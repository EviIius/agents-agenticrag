# Phase 1, step 1 report — provider recordings

## Summary

Recorded real Ollama and LM Studio wire responses before starting adapter code.
Added a repeatable fixture recorder, checksummed request sidecars, and contract checks.
Discovered that LM Studio silently answers an unknown model ID using a loaded model.
Paused before step 2 as SPEC.md requires when observed runtime behavior contradicts it.
Phase 1 and Checkpoint 1A are **not complete**.

## Done-when checklist

| Item | Status | Evidence |
|---|---|---|
| Record both real runtimes | Passed | `server/tests/fixtures/providers/`, `artifacts/phase-1/provider-recordings.txt` |
| Plain text, native reasoning, length stop | Passed on both | `test_recorded_text_reasoning_and_length` |
| Gemma image input | Passed on Ollama | `test_recorded_gemma_image_input_completed` |
| Catalog, show, ps, load/unload payloads | Recorded | Raw JSON/NDJSON fixtures; `test_lmstudio_loaded_context_and_unload_contract` |
| Unknown-model 404 | Ollama passed; LM Studio contradicts spec | `test_runtime_unknown_model_discrepancy_is_preserved` |
| D-AC1: detection, Add all, picker loaded state | Pending implementation | Metadata recorded; API/UI not wired yet |
| D-AC2: streaming delay and frame rate | Pending | No adapter or live client yet |
| D-AC3: reasoning UI, storage, history | Pending | Real native reasoning captured for later adapter tests |
| D-AC4: sampling payloads | Pending adapter tests | Recorded normal probes omit sampling; only length probes set 20 tokens |
| D-AC5: long stream, idle timeout | Pending | Fake runtime baseline only |
| D-AC6: Stop and cancellation | Pending | Live run management not implemented |
| D-AC7: resume, iPhone sleep | Pending | Live run management not implemented; phone check will require manual evidence |

## Changed files

- Server: `server/tests/fixtures/providers/` raw responses, sidecars and README;
  `server/tests/test_provider_recordings.py`.
- Scripts: `scripts/record_provider_fixtures.py`; enabled `make record-fixtures`.
- Docs/evidence: this report; `artifacts/phase-1/check-step-1.txt`,
  `artifacts/phase-1/provider-recordings.txt`.
- Web: no changes during the recording step.

## Deviations from SPEC.md

No architecture or dependency deviation implemented. Runtime evidence contradicts
§C5's unknown-model 404 assumption on LM Studio. The spec's opening instruction
requires recording the evidence and stopping to ask before accommodating this.

Proposed resolution: reject IDs absent from the runtime catalog with
`model_not_found` before generation, so the application never relies on LM Studio's
fallback routing. Validate reported response model identity using runtime identifiers
and loaded-instance metadata when available, without model-name heuristics.

## Runtime observations

- Ollama was reachable. LM Studio was installed but its server was off; started the
  existing service using `lms server start` on its existing port 1234.
- LM Studio model catalogs match the documented v1 shape. Explicit load accepts
  `{model, context_length}`; unload accepts `{instance_id}`. Recorded both.
- With a model loaded, a request for `workbench-fixture-unknown-model` returned 200
  and streamed from `qwen3-30b-a3b-instruct`. With none loaded, it returned 400 with
  “No models loaded.” Ollama returned 404 for the same unknown ID.
- LM Studio's GPT-OSS metadata reports low/medium/high reasoning, default low.
  Ollama's GPT-OSS metadata reports the same options but default medium.
- Ollama's Gemma reports vision and boolean thinking controls; the synthetic image
  request completed. Neither of the two installed LM Studio chat models reports
  vision, so no real LM Studio image fixture can be captured yet.
- All tested models were unloaded after the probes. The excluded standard Llama
  was queried for metadata only, never loaded or used for generation.
- Existing installed app, launchd label, Tailscale configuration and legacy data
  were not changed.

Official protocol references: [LM Studio model catalog](https://lmstudio.ai/docs/developer/rest/list),
[LM Studio unload](https://lmstudio.ai/docs/developer/rest/unload),
[Ollama thinking metadata](https://github.com/ollama/ollama/blob/main/docs/capabilities/thinking.mdx).
Observed responses above are supported by the local fixtures, not assumptions from docs.

## Test output

`make check`: passed. 57 Python tests, strict mypy, Ruff checks/format, 56 contrast
pairs, generated API type freshness, TypeScript, ESLint, Prettier, and 1 Vitest test.
Full output: `artifacts/phase-1/check-step-1.txt`.

`make e2e`: not rerun for this step; no web or application runtime code changed.
Phase 0's browser evidence remains in `artifacts/phase-0/` and `docs/PHASE-0-REPORT.md`.
Provider/run coverage gates become applicable when those modules are implemented.

## Screenshots

No UI change in this step. Previous light/dark desktop and mobile captures are in
`artifacts/phase-0/`. New live-chat screenshots are due at Checkpoint 1A.

## Open questions for Jake

Approve the proposed catalog guard so adapter work can continue despite the
observed LM Studio fallback. This is the review required by SPEC.md's opening rule.

## Direction retained for the next steps

Future agents remain part of the product direction. Leave only §F3's reserved
provider tool event/message and run event seams in Phase 1; the agent implementation
has its own later spec and §F4 entry criteria.

The live UI will retain §G1's warm reading surface, serif answers, restrained cobalt,
compact controls, clear model/loading states and quiet metadata. Responsive and
accessibility evidence will accompany the live chat checkpoint.
