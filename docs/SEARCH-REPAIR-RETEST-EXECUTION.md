# Frozen Search retest execution

11 October 2026. Jake said “continue going” after reviewing the invalid first
trial and the concrete corrected-harness retest proposal. Retest the same single
candidate in `artifacts/images-i1/search-repair-v2/`; keep the first trial intact.

## Inputs and measurement correction

The 24 cases, eight designated held out, both prompt arms, synthetic fixtures and
54-child invocation order are exact byte copies of the first declaration. The
original 25-case benchmark, grader and public corpus are unchanged. Candidate
wording, model, runtime, 16K context, explicit shared date, unset answer sampling,
existing planner utility values, source and native admission are unchanged.
The designated held-out split predates inference; first-trial candidate held-out
cases were not run. Baseline held-out answers have been observed, which is
retained history rather than a claim that all inputs remain unseen.

Apply only the reviewed harness correction: observe the unchanged schema produced
by `planner.schema(latest)`, record assertion errors before provider streaming,
and require actual planner/answer wire requests and complete traces before any
score can advance the sequence. Validate this actual corrected harness offline
before committing its manifest. This corrects measurement; it changes no product
schema, prompt, sampling, API, data, fallback or call type.

## Declared sequence and stop conditions

Use the same order and gates as `SEARCH-REPAIR-EXECUTION.md`: 24 baseline boundary
cases then 24 candidate boundary cases, manual support review, then three matched
full pairs in alternating order, each with support review. Require every candidate
boundary assertion and attack exposure, all three original-suite candidates at
25/25, unchanged E12/G9 aggregates against historical and fresh matched baselines,
and no case regressions. No variance exemption or weaker grading is introduced.

Stop immediately on protocol/host failure, the first mandatory candidate failure,
manual support failure or G9 failure. Preserve raw reports, wire bodies, provider
responses and the stop; explicitly mark remaining calls unexecuted. No automatic
retry, favorable-run selection, case edits or prompt experiments follow a stop.

Only after all declared gates pass may the unchanged fresh live Web evaluation
and required repository/browser release gates run. Present H4 before release.
Images remains undeployed, Research stays shelved, and W1 remains later scope.

## Host and preservation controls

Use isolated temporary databases and synthetic/public input only. Check live
human inference/transcription flags before each native load/stream, retain
sequential execution, and skip the evaluator's final unload. No human text or
private filename enters evidence. Preserve every prior trial and output byte.
No new model, package, runtime, default, route, utility parameter, image call,
workflow call, production restart or deployment is included.

If the retest fails genuinely, stop with its H4 report before reviewing the
larger deterministic supplied-input/reference design. The first invalid trial
never counts as native planner success or failure.
