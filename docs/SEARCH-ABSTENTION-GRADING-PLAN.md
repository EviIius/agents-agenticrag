# Proposed checkpoint: equivalent abstention grading

Status: **proposal only**, 11 October 2026. No grader changed, answer regraded or
new native inference performed after the creation-contract trial's stop.

## Observed defect

`SEARCH-CREATION-CONTRACT-REPORT.md` retains a correct source-scoped decline that
says the evidence `does not establish` the requested personal fact. Lookup and
citation checks pass; the frozen regex rejects that phrasing. Earlier retained
trials show similar equivalent-wording failures. Product behavior should not be
modified merely to satisfy one phrasing proxy.

## Bounded scope for review

1. Audit abstention checks in the existing boundary/supplemental/ordinary and
   original release evaluation paths. Distinguish vocabulary gaps from real
   missing lookup, identity substitution, wrong dates and unsupported additions.
2. Prepare a generic, limited equivalent-decline matcher with wording positives
   and negatives. Positives include source-scoped `does not establish/specify`
   and `isn't known from these records`; wording negatives include negated and
   merely quoted declines. Separately test the combined grading/manual gates on
   fabricated facts following an apparent decline, source/user subject
   substitution, wrong date/measurement and missing evidence disguised as
   successful lookup. A wording matcher cannot detect arbitrary unsupported
   additions. No topic/entity rules, model judge or production prompt change.
3. A lexical matcher is only a wording check. Existing lookup/citation/required-
   fact/forbidden checks and independent manual claim/subject/time review must
   still reject unsafe output. Do not claim lexical positives prove semantics.
4. Audit retained answers without inference. Emit separate original-versus-
   corrected scores with answer/report hashes and reasons. Leave all original
   reports, cases, fixture corpus, answers and failure history unchanged. An
   accepted grader correction must be explicit and cannot excuse genuine failures.
5. If offline parity/negative tests pass and the grading correction is accepted,
   freeze the **same** creation-contract policy, corrected evaluator and declared
   order before inference. Include an early new-code smoke to establish whether
   the intended repair actually runs. Retain the existing ordinary/creation and
   original boundary/supplemental cases, original 25-case benchmark and matched
   comparisons; predeclare repeats and stop on first mandatory/support/protocol/
   G9 failure. No favorable retry or silent target/order change.

## Unchanged requirements

One existing planner and one answer per turn; fixed approved runtime/model/
context/sampling, no new package/model/default, product routing or extra model
call. Same factual/citation/support/injection/coverage/latency targets, manual
source review and release requirements. No Research/image/workflow invocation
or deployment. Offline correction alone does not qualify native code generation,
full Search reliability or Images release. Stop with H4 for reviewed next steps.
