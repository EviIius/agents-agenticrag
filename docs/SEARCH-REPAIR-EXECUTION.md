# Frozen Search repair execution

11 October 2026. Jake said “continue going” after the concrete repair proposal
and I1 review stop. Execute `SEARCH-REPAIR-PLAN.md` as one isolated candidate.
No production prompt/hash, API, schema, runtime, package, model, defaults or
sampling change is made before qualification. Research stays shelved; no image
or workflow model call is included.

## Fixed inputs

`artifacts/images-i1/search-repair/prompts.json` contains the exact original
prompts and the proposal's appended wording, joined by one newline. Candidate
monkeypatching happens only in isolated evaluator processes. Both arms use the
same Images product source, enabled native admission, temporary databases,
existing benchmark model's runtime-reported 16K context, existing planner utility
parameters and unset answer sampling. Ordinary chat/Library/title prompts stay
unchanged. The shared explicit date is 11 October 2026.

The separate 24-case suite has six absent-resource, six supplied-transformation,
six history-reference and six identity/time/missing-detail cases. Sixteen are
development cases; eight are designated held out before candidate inference.
Names/places/records are synthetic. Fixed seed conversation messages are input
fixtures, not claimed real model answers. Only the original planner and answer
calls run for each tested request. Source HTML is parsed/ranked by production
code from explicit wildcard synthetic fixtures; no live provider is contacted.
Two cases include untrusted attack text; their selected passages must actually
contain that attack and the answer must not follow it.

The original 25-case suite, all original graders and public recorded corpus stay
byte-identical. Original evaluator reports capture prompt texts/hashes; the trial
instrumentation identifies candidate wording even though original trial flags
remain `spec`. Per-child report destinations prevent overwriting earlier reports.

## Ordered calls and review gates

`execution.json` declares **54 child runs**, frozen before inference:

1. All 24 baseline boundary cases in file order, then candidate cases in the
   same order. Retain expected baseline failures. Stop at the first mandatory
   candidate failure, including missing attack exposure. Remaining calls stay
   unexecuted; no automatic retry or favorable result selection.
2. If all candidate boundary assertions pass, stop for agent manual review against
   the exact supplied evidence. Negative-case regexes are not proof of abstention:
   unsupported values followed by disclaimers and subject/date substitutions fail
   that review. No next phase can start without a hash-linked review record.
3. Three full original-suite matched pairs, in orders baseline/candidate,
   candidate/baseline, baseline/candidate. Run one pair at a time and review source
   support before the next pair. Every candidate must pass 25/25, actual injection
   exposure and unchanged E12/G9 targets. Compare every declared quality/timing
   aggregate with the historical accepted and fresh matched baseline; a failed
   comparison stops the trial. No new variance exemption.
4. Only if all three pairs and manual reviews pass, run the unchanged fresh live
   Web evaluation and required release regression gates. Present the H4 decision
   before releasing Images or beginning W1.

The parent records full declared order, completed runs, original evaluator reports,
exact runtime wire bodies/responses and stop reason. Manual reviews are Codex's
observations, not attributed to Jake. No held-out case or assertion may be edited
after inference. Fixture/format preparation failures remain retained separately.

## Host and preservation controls

Before every native load/stream, check live human-inference/transcription flags
and stop if active; no human text is captured. Use sequential native calls and
skip final harness unload to avoid human model ejection. Existing warm load and
keep-alive remain explicit. Never force sampling, evict a model or retry a call.
Verify the frozen source, prompts, cases, fixtures and harness around each run.
Preserve every prior Images/Search/grounding/Research failure and all prior output
bytes. Production bind, launchd service and Tailscale configuration stay unchanged.

If the candidate fails, retain it as an unqualified isolated trial and stop with
H4 evidence. Review a deterministic supplied-input/reference design separately;
do not silently change the candidate or broaden this trial into that design.
