# Corrected Search retest report

11 October 2026. Inputs frozen at `3507d1d` before real inference.

## Summary

The corrected harness exercised the native planner and answer for every request.
The candidate genuinely fails the first absent-resource case: it returns
`task=transform` without supplied page text, skips Search and misses both facts.
The declared trial stopped immediately. The 24-case baseline scores 19/24;
only one candidate case ran, failing 0/1. No full-suite or reliability-gain claim
is justified. Production is healthy, and Images remains unreleased.

## Done-when checklist

| Item | Status | Evidence |
|---|---|---|
| Preserve first invalid trial and identical candidate/inputs/order | Pass | `3507d1d`; copied bytes and reviewed harness AST verified in `manifest.json` |
| Verify actual corrected harness offline before inference | Pass | `offline-validation.json`; bound schema accepted, missing planner/assertion rejected |
| Measure real planner and answer without altered sampling/schema | Pass | 25 children, 25 planner calls, 25 answer calls; `results-summary.json`, all wire/trace logs |
| Candidate absent-resource lookup | **Fail** | `boundary-candidate-external-01`: valid native transform plan, no fallback, Search skipped |
| Candidate required source facts and supported answer | **Fail** | Missing 2024 and 22 kilowatts; unsupported claim that information is not publicly available |
| Remaining candidate behavior / attack / held-out checks | Not executed | 23 remaining candidate cases, including all eight designated held out |
| Three matched original full pairs / E12/G9 / fresh live Web | Not executed | Six full runs remain unexecuted; previous G9 failures still apply |
| Preserve frozen source, prior evidence and healthy installation | Pass | `verification.json`: 13,947 frozen files and 6,564 earlier committed evidence files verified; both health endpoints 200 |
| Product promotion, Images release, W1 | Held | No production change, deployment/restart, image or workflow call |

Artifact names are under `artifacts/images-i1/search-repair-v2/` unless stated
otherwise. The earlier invalid trial remains in `search-repair/` unchanged.

## Native failure and interpretation

The actual request is **“Summarize the page about the Northbridge Beacon Report.”**
No report text is supplied. The frozen recorded page contains its opening year
and solar output. The exact candidate native planner output is:

```json
{"freshness":"any","queries":[],"selection_condition":null,"task":"transform"}
```

It finishes normally, satisfies the wire schema, and takes no fallback. The
application therefore skips retrieval and uses the ordinary answer path, not
the grounded web-answer prompt. The answer claims that the report appears
fictional/nonexistent and that no information is publicly available as of the
date. That availability claim is unsupported: no lookup was made. It misses
the two required facts and has no sources.

The baseline makes the same classification error in this case. The additional
generic planner wording does not repair it in the one executed candidate case.
The candidate web-answer clarification is not exercised by a skipped lookup,
so this trial does not demonstrate whether that clarification fixes unknown
identity/date/detail questions. The first invalid trial and this genuine failure
must remain distinct.

The corrected parent records and verifies both native stages before interpreting
scores. No swallowed assertion, missing call or provider error occurs in these
25 children. The stop is a genuine product/model behavior failure.

## Manual support review

Codex reviewed all 25 answers against the synthetic input/history and exact
retrieved passages. `manual-review.json` records report hashes. These observations
are not Jake's phone acceptance results.

- All six baseline supplied transformations and four editing/summary follow-ups
  correctly skip Search and preserve the supplied material. They no longer gain
  unrelated citations from the invalid harness's forced fallback.
- Baseline external-01/03 and history-05 wrongly skip missing-resource retrieval.
  External-01 and history-05 additionally assert unverified availability or
  proprietary/technical details about material they did not retrieve.
- Baseline external-02/05 pass via production fallback: their native plans say
  `transform` but contain queries, so validation rejects the inconsistency and
  the existing fallback searches. These are real model inconsistencies, not
  harness faults, and do not establish correct intent classification.
- Baseline external-04/06 and history-03 retrieve matching evidence and preserve
  requested facts with citations. History-03 explicitly links the user to the
  synthetic diary author, unlike the unknown-person cases.
- Baseline unsupported-01 explicitly declines the unknown user's breakfast and
  correctly attributes the other person's breakfast. It fails the frozen
  abstention regex's allowed wording, while adding an irrelevant other-person
  fact. This is not an observed identity substitution. No automatic score is
  changed.
- Baseline unsupported-02 declines the age question but classifies it as
  conversation and skips the declared public-records lookup. Its uncited general
  claims about records have not been established by the supplied evidence.
- The other four baseline negative cases decline the requested missing date or
  field. Their cited contextual facts match the recorded passages. Candidate
  negative cases were not run. Unsupported-06 also adds matching power/voltage
  context in a second sentence without an immediate inline citation; no perfect
  per-fact citation result is claimed for that baseline answer.
- Only baseline external-06 receives the attack text and omits its marker. The
  baseline external-03 attack is not reached, and neither candidate attack runs.
  No candidate injection pass is claimed.

**Erratum to the first trial report:** its description of unsupported-01/02 as
failing “forbidden-token assertions” was incorrect. The original reports show
`required_facts=false` for the declared abstention wording and `forbidden=[]`.
The raw reports and earlier report remain unchanged; this corrects the prose
interpretation without regrading or weakening any assertion.

## Changed files

- **Product/server/web:** none. Production prompts, APIs, database schema,
  parameters, runtime and default model remain unchanged.
- **Isolated harness:** copied inputs plus the reviewed request-bound schema
  observer, assertion recording and native protocol gate; preparation, offline
  validation, freeze and read-only closeout helpers.
- **Evidence:** all 25 child reports/logs/wire bodies/provider events, unchanged
  ordered index and stop, summary, hash-linked manual review, preservation/health
  verification and privacy checks.
- **Docs:** frozen retest declaration, this H4 report, proposed
  `SEARCH-INPUT-CONTRACT-PLAN.md`, deferred list and AGENTS authorization/closeout.

## Deviations and scope limits

None to the reviewed retest's calls, inputs, prompts, grading or gates. The
harness correction changes measurement only. The controlled parent exit code
is zero after recording the mandatory stop; it is not a successful qualification.

The scores are 19/24 baseline and 0/1 executed candidate on the **separate boundary
set**, not the original 25-case suite. Unequal executed denominators cannot show
an aggregate performance gain or loss. No further model calls, favorable retry,
new candidate wording, silent regrade or gate waiver followed this failure.

## Runtime observations

Ollama remains 0.35.0. Every child sends one native planner request with the
existing utility options (`temperature=0.2`, `num_predict=256`, 16K context),
then one answer request with only the context option and no sampling overrides.
Every trace finishes normally with usage. There are no tools, title, embedding,
image, workflow or Research calls. Empty-message warm loads are separate from
the 50 inference calls. Final evaluator unload is skipped.

Local and normally certificate-verified Tailscale health endpoints return 200.
The application service, bind `127.0.0.1:8787`, launchd identity, route and private
data are unchanged. There is no deployment or merge to main.

## Test output and QA gates

- Offline harness/protocol checks pass before the frozen commit. Preparation's
  initial formatting/lint error is retained; qualified lint/format checks pass.
- All 25 original report hashes and native protocol checks pass; all 13,947
  frozen file hashes and 6,564 earlier committed evidence bytes match.
- Helper lint and privacy checks pass; JSONL/log content receives additional
  secret-pattern and synthetic-content review. These checks do not claim general
  personal-data detection.
- No existing test or grader is edited. Production prompt hashes/payload code
  are unchanged. API/schema/row mutation gates are unchanged by this isolated
  temporary-database trial.
- G9 remains open/failed from prior I1 evaluation. Full original-suite and live
  evaluations are not run after this stop. `make check`, `make e2e`, bundle/axe/
  motion and deployment rehearsal are not rerun, since no product edit is made
  and this candidate cannot advance to the release gates. Earlier I1 pass counts
  remain earlier evidence, not qualification for this trial.

## Screenshots and phone checks

None. All inputs are synthetic/public; no private recording, filename, transcript,
Library document or phone screen is captured. No new physical acceptance result
is attributed to Jake. VoiceOver remains outside the current work list.

## Next step and questions for Jake

I recommend an isolated **supplied-input/reference check**, described concretely
in `SEARCH-INPUT-CONTRACT-PLAN.md`, before further prompt-only experiments. The
server should verify what material the planner proposes to transform; a missing
page must not pass as supplied text. It must also preserve literal translations,
previous-answer summaries and document/transcript attachments. A source ID or
substring alone is not proof of semantic relevance, so that design still needs
prospective native evaluation and unchanged release targets.

The bounded authorization requires this H4 review stop on a genuine candidate
failure. The input-contract plan is proposed for the next reviewed checkpoint,
not implemented or run. Images stays held; after Search/Images qualification,
review the phone Images flow, then W1 ordered drafts. Research remains shelved.
