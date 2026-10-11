# I1 Search diagnosis — frozen comparison

11 October 2026. Jake asked to continue after the I1 report recommended a matched
baseline/candidate Search investigation. This authorizes this isolated diagnosis;
it does not waive G9, authorize prompt changes or release the Images build.

## Question and fixed inputs

Does the accepted `ba75e28` source reproduce the planner's missed external-page
summary, and does `7383347` with native admission enabled change request payloads
or the ordinary frozen Search results? The existing 24/25 result and every trial
remain. No new model, package, sampling/default/runtime change or image call.

Use the existing installed benchmark model and runtime-reported 16K context;
ordinary answers have empty sampling values, planner utility values remain the
existing production values. Use the unchanged 25 cases, grader, recorded corpus,
real planner and real answer. Do not replay model responses or recorded plans.
The clock in planner/context/search-result dates is fixed to 11 October 2026 for
both arms, so crossing midnight cannot change otherwise matched request content.
This date control is isolated instrumentation; production prompts are unchanged.

Freeze the complete production source for each arm, harness/clock/capture code,
cases, grading and recorded corpus before inference. Baseline source is extracted
read-only from the accepted Git object into an ignored temporary directory. Both
arms use temporary new databases. Candidate native admission is enabled using the
already installed public worker selector; no image job is submitted.

## Predeclared sequence (no automatic retries)

1. Three matched injection-case pairs: baseline/candidate, candidate/baseline,
   baseline/candidate. Capture exact runtime payloads, response events and raw
   planner JSON. Compare utility requests byte for byte, with only JSON key order
   normalized. Date is the shared explicit control; no sampling normalization.
2. One full 25-case candidate run and one full baseline run, in that order. Retain
   all outputs even if either misses a gate. G9 still compares against the accepted
   6 October 25/25 report as well as the fresh matched baseline; a favorable run
   does not erase the earlier failed run or qualify consistent behavior.
3. Inspect every failed case and cited support changes. Separate task classification,
   retrieval/ranking, answer support and lexical grader observations.

Before each native invocation, check the live app's human-run/audio-active flags.
Stop when human work is active. Skip the evaluator's final model-unload operation
so it cannot eject a model used by a human; log this residency-only instrumentation.
No parallel native runs, implicit profile switch, forced sampling seed or hidden
fallback. Normal evaluator warm load/keep-alive remains explicit and recorded.

## Stop and report

Retain ordered calls, source hashes, original failure, exact request comparisons,
full aggregate/case comparisons and the H4 diagnosis report. No automatic model
retry, favorable-run selection, threshold/grader weakening or production prompt
edit. If both sources miss the same intent, propose a generic supplied-content vs
external-resource correction with its own before/after eval scope; do not assume
that a source-equivalent failure is a release pass. Keep live I1-0 unchanged and
stop before deployment/W1 if G9 remains unresolved.
