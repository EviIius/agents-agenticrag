# Bounded table-admission report

12 October 2026. Candidate frozen at `b6dc54b8`; original question, evidence,
prompts, schema, model and thresholds retained. H4 review stop.

## Summary

The isolated selector repairs a real omission: an original seven-column table
with 28 rows / 23 qualifying entries now fits the existing source budget.
Only one of 28 retained benchmark turns changes in the offline replay.
The approved native comparison stops after its first pair: both answers include
the 23 entries, but the candidate adds an unsupported temporal relationship.
There is **no demonstrated native answer improvement or release qualification**.

## Done-when checklist

| Item | Status | Evidence |
| --- | --- | --- |
| Repair the actual retained omission within existing limits | Pass, offline only | `comparison.json`: 0 → 28 original table rows, 23 positive counts; 5,337 / 5,502 tokens; all seven columns and original text SHA retained |
| Preserve other original selections | Pass | All 22 source-bearing turns reproduce baseline passage bytes; only `nba-all-losses` changes; six other turns have no selected sources |
| Reject malformed/unrelated/code/ambiguous/over-budget data | Pass | 33 admission tests; original passage metadata, ordering and three-passage/source cap retained |
| Freeze inputs, instrument actual native calls and stop safely | Pass | 16 protocol/continuation tests; `manifest.json`, `execution.json`, actual wire/trace/admission records |
| Improve the actual answer | **Not demonstrated** | Both native planners choose the qualifying event correctly, so the existing selector already supplies the complete table; the new hook is a no-op in both native arms |
| Every candidate factual claim supported | **Fail** | Candidate opening says “later won championships”; its sole supplied source is aggregate counts without chronology |
| Repeated candidate consistency | **Not run** | First candidate semantic failure stops four later declared children; no retry |
| Repository/browser regression gates | Pass | 508 Python, 39 frontend, 473 browser; three existing browser skips; 49 isolated admission/protocol checks |
| Preserve prior evidence and installed app | Pass | 17,861 earlier committed evidence/eval files, 16,675 prior frozen files, 7,692 current frozen files verified; affected installed Search/context files unchanged |
| Deploy/promote, Images release or general Search qualification | **Not authorized / not achieved** | Live app unchanged; prior G9 and general grounding failures remain open |

All evidence paths in this report are relative to
`artifacts/images-i1/search-table-admission/` unless otherwise stated.

## Actual before/after result

| Measurement | Current Search baseline | Table candidate |
| --- | --- | --- |
| Original required entries present | 23 / 23 | 23 / 23 |
| Nonqualifying listed entries | 0 | 0 |
| Inline citation on each entry | Yes | Yes |
| Original automatic case result | Pass | Pass |
| Selected sources | One aggregate table | Same aggregate table |
| Hook changes admitted passages | No | No |
| Actual evidence cost / budget | 645 / 5,499 | 645 / 5,499 |
| First answer token | 4.684 s | 3.286 s |
| Total turn time | 10.822 s | 9.524 s |
| Manual extra-claim review | Pass with arithmetic caveat below | **Fail: unsupported chronology** |

Both planners return `property_word=lost`, `operator=occurred`, `value=null`.
The existing literal-condition pipeline consequently selects the 23 positive
rows before ranking. The offline admission repair protects the different retained
failure path, where the planner had not established that condition and three
introductions occupied the table's slots. That failure path was not exercised
by these two fresh native plans. Do not credit the hook for the complete lists
or the timing difference; neither is causal evidence of improvement.

The candidate's opening adds **“including those that later won championships in
other years.”** The user asked for wins in other years, without the “later”
condition. Total losses, appearances and wins do not establish their temporal
sequence. Every team/count item is supported by the supplied table, but this
extra relationship is not. Lexical citation support is 1.0 in both reports;
that does not establish semantic support. The original automatic scores remain
unchanged, with the manual failure recorded separately.

Seven `Finals Won` cells contain literal dashes. Both answers emit zero wins.
The source's equal appearances/losses and explicit 0.0% wins establish that
arithmetic conclusion; the review does not infer zero from a dash alone. This
is not literal null preservation and does not qualify the abandoned exact-value
answer contract. The baseline review initially says six such cells; a retained
addendum corrects it to seven without changing the original review or answers.

### Retained native evidence

- `pair1-baseline/reports/*.json` and `pair1-candidate/reports/*.json`: original
  answer, selected sources, original-case scores and measured latency.
- Each arm's `wire.jsonl`, `trace.jsonl`, `admission.jsonl`, logs and public-model
  preflight metadata: actual requests, stream events and selection decisions.
- `pair1-baseline-review.json`, its addendum and
  `pair1-candidate-review.json`: every list item/count/citation, opening and
  conclusion reviewed against the actually supplied source.
- `ordered-results.json`: semantic stopping reason and four unexecuted children.

Actual calls: **two planners, two answers and two empty-message warm loads**.
No judge, repair, retry, embedding, title, Research, image or workflow call.
All eleven recorded protocol checks pass in each executed arm.

## Changed files

- **Isolated tooling:** `admission.py`, 33 admission tests, `replay.py`, native
  harness, 16 guard tests, freeze/order/prompt manifests, archival and preservation
  helpers. The production selector does not import this candidate.
- **Evidence:** offline comparison, both native answers and manual reviews,
  all preparation failures/logs, regression results and integrity/health records.
- **Docs:** approved native scope, this H4 report, authorization/closeout in
  `AGENTS.md`, deferred-status update and the concrete source-first next proposal.
- **Production source:** no server/web/transcription/deployment/runtime change.

## Deviations from SPEC.md

The explicit user approval permits this isolated bounded model comparison; it
does not permit deployment or waive failed gates. Earlier unqualified planner
contracts are excluded. Existing prompts/settings and the installed Qwen model
remain unchanged, as verified against actual wire and installed source hashes.

The declared maximum is three pairs; the mandatory semantic stop ends inference
after the first pair. No additional native experiment follows. The original
benchmark/corpus/report history is neither rewritten nor regraded.

## Runtime observations

Ollama remains 0.35.0. Both arms stream normally with usage/finish events, the
existing utility temperature 0.2 / 256-token exception, 16K context and an empty
answer sampling payload. Human-inference/transcription checks run before warm
load and each model stream. Temporary `workbench-eval-*` stores isolate app data;
the evaluator's final unload is suppressed to avoid ejecting a user's model.

Both plans supply the right qualifying condition in this run. This is observed
success, not proof that condition selection is consistent. The earlier original
omission and other genuine failures remain preserved.

## Test output

- `tests-initial.log`: **33 passed**.
- `tests-native-preparation.log`: **16 passed**.
- `tests-freeze-final.log`: **49 passed in 4.45 s**.
- `make-check.log`: **508 Python / 39 frontend passed**, lint/types/API/contrast/
  motion/privacy checks passed.
- `make-e2e.log`: **473 passed, three existing skips, 39.2 minutes**. It finishes
  before native inference, so it does not compete with native timings.
- `archive-tests.log`: **432 fresh test outputs retained**, 392 historical files
  restored byte-for-byte plus 40 new fake settings captures moved into this
  checkpoint's evidence directory.
- `closeout-integrity.json`: source/input preservation, actual call counts,
  local health 200, normally verified Tailscale HTTPS health 200, runtime unchanged.
- Preparation lint failures are retained; final isolated lint passes with E402
  excluded for the documented repository-path bootstrap. The read-only closeout
  helper's initial import-order warning and its exact source are also retained.

## Screenshots

No product/UI or physical-phone change is claimed. Required fake-runtime browser
captures are under `regenerated-test-evidence/`; the manifest maps each fresh
capture/metric to its historical path and SHA. Native results use the actual
public-fixture answer/source records, not real recordings, filenames, Library
documents or phone captures. Privacy scans report no failures; pattern scanning
is not a complete privacy proof.

## Feasibility and next steps

**Concrete evidence mechanics can improve. Consistent generated-answer improvement
has not been demonstrated by this checkpoint.** The offline fix is real, but the
native trial did not exercise it, and complete supplied evidence still allowed
an unsupported relationship in the answer. Stop broad prompt continuation and
do not release this candidate on its favorable automatic score.

The next useful scope is a host-only structured-source correction: preserve
original table headers/roles across extraction and chunking, reproduce the known
omission branch, and make missing source facets explicit in diagnostics. Keep
old scores/corpus; evaluate newly covered evidence separately. See
`SEARCH-STRUCTURED-EVIDENCE-NEXT.md`. This proposal authorizes no new inference or
deployment. General factual outputs remain drafts for human review; Images stays
held by its existing G9 gate, Research shelved, W1 unstarted and VoiceOver off the
current work list.

## Open questions for Jake

Review this failed bounded comparison and the smaller source-first proposal
before another native trial or release. No further model experiment is queued.
