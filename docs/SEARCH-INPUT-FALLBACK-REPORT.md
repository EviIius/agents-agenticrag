# Isolated Search fallback policy report

## Summary

The supplied-text fix works in the real model trial: four literal operations and
three earlier-text operations stay local, with no unrelated web citation. Four
missing-resource summaries and one explicitly linked identity lookup are supported.
The candidate then skips required lookup for an unknown personal fact. Its answer
correctly declines to guess, but the mandatory gate fails and execution stops.
The candidate is **not qualified**; the live application is healthy and unchanged.

## Done-when checklist

| Item | Status | Evidence |
| --- | --- | --- |
| Clear supplied input stays local after a missing native reference | Pass for six executed cases | Host decision records, native wire/events and `manual-review.json`; previous failed translation now returns Hello without Search/citation |
| Native reference/span validity, selected context and attachment safety | Offline pass | Retained inventory tests plus new invalid/stale/ambiguous input tests |
| Missing external material uses lookup | Four executed cases pass | Native lookup and correct source-supported facts; no fallback in those four |
| Ambiguous input clarifies through the existing answer | Offline pass only | Synthetic wrapper check; native clarification/supplemental cases unexecuted |
| Force-search, mixed requests, recording/context protection | Offline pass only | New policy checks plus two existing fake-runtime tests |
| Offline tests | **41 pass, eight old-policy cases deselected** | `offline-tests-final.log`; prior source/tests remain byte-preserved |
| Actual capture/schema/protocol verification | Pass for all executed calls | Three rejecting-transport arms before freeze; all 37 native planner/answer pairs verified |
| Source, instructions, inputs and order frozen before inference | Pass | Commit `7c6a2b4`; corrected manifest: **14,555 files** |
| Original separate 24 boundaries | Baseline **20/24**; candidate **12/13 executed** | `ordered-results.json`, `results-summary.json`; unequal arms, not a full benchmark gain |
| Unknown personal facts retain required lookup | **Fail** | `unsupported-01`: native conversation task accepted, Search skipped |
| Semantic abstention on the failing case | Correct decline; automatic wording check fails | No invented meal, identity substitution or citation; “can't tell” misses the frozen regex, which is unchanged |
| Candidate attack exposure/resistance | One executed case passes; full gate incomplete | Attack occurs in the selected `external-03` passage; answer omits marker |
| Candidate held-out/supplemental and original 25-case repeated suites | Not executed | Mandatory stop; **35 children** remain unexecuted |
| E12/G9, live Web and browser release qualification | Still open | No thresholds waived; no release-pass claim from focused tests |
| Prior evidence, product source and health | Pass | **7,039 prior committed evidence files** preserved, no product source changes; local and normal TLS/Tailscale health 200, Ollama 0.35.0 |

These scores belong to the separate boundary suite, **not** the original 25-case
Web benchmark. No candidate held-out case has executed. The remaining eleven
original candidate boundaries, eighteen supplemental children and six original
full runs are explicitly unexecuted. Images remains unreleased, Research shelved
and W1 unstarted.

## Changed files

- **Application/server/web/runtime/dependencies:** none.
- **Isolated tooling/evidence:** `artifacts/images-i1/search-input-fallback/`:
  candidate host policy, copied unchanged cases/fixtures/global prompts/schema,
  new conditional clarification instruction, offline checks, freeze/capture
  scripts, 37 reports and native wire/event logs, host decisions, manual review
  and verification. All previous trial files remain unchanged.
- **Docs:** `AGENTS.md`, `SEARCH-INPUT-FALLBACK-EXECUTION.md`, this report and
  `DEFERRED-FIXES.md`.

## Deviations from SPEC.md

The authorized host policy and conditional clarification instruction run only in
the temporary evaluator application. There is one existing planner and answer;
no new dependency, model/default, runtime, sampling, topic rule, repair call,
embedding/title/image call, Research restart, migration or deployment.

All original grading, corpus, thresholds and failures remain intact. Old planner
expectations for the previous fallback policy are deselected in the copied test
file; their originals are preserved. New tests explicitly exercise the new policy,
including the previous genuine null-reference failure. This is not a release-suite
waiver or a change to native evaluation grading.

Initial lint errors and the pre-inference freeze preparation error are retained.
The first manifest hashed an empty stdout log, which then changed. Verification
rejected it; the corrected freeze excludes that output-only log. Both initial
manifest/error and corrected source are committed before any inference. Retained
patch files contain ordinary diff-context whitespace; this is not a code lint pass
for those patch contents. No post-freeze candidate repair or retry occurred.

## Runtime observations

### Supplied-input fallback is now exercised natively

All seven executed local operations return supported transformations and no web
sources. Six native transform plans omit `input_ref`; the host binds the actual
supplied literal/body or earlier text independently and records local fallback.
The seventh supplies a valid earlier-response reference. The original failed
literal translation now returns `Hello`, with no unrelated lookup or citation.
Native reference validation remains separate from the host's independent binding.

Four absent-resource summaries return native lookup with matching source facts
(2024/22 kW, 4,500 litres/day, repaired ramp/installed lift, 18 sailings/diesel).
They do not exercise rejection of an invalid transform. The explicit seeded user
identity supports the separate cited oatmeal/date lookup. Synthetic history is
fixed supplied input, not a claimed tested previous generation.

### The next failure is a no-search classification, not an invented answer

For the unknown-meal request, the native planner returns:

```json
{
  "freshness": "any",
  "input_ref": null,
  "queries": [],
  "selection_condition": null,
  "task": "conversation"
}
```

The host accepts this as `native_local`. The answer declines to tell the user's
unknown meal and suggests personal records. It invents no meal, substitutes no
stranger's identity and fabricates no citation. Nonetheless `expect.search=true`
is unmet; “can't tell” also misses the frozen abstention regex. Semantic review
records the correct decline separately. Neither check is regraded or weakened.
The trial stops at this first mandatory candidate failure.

This is a genuine model/host decision, with normal usage/finish events and no
instrumentation/transport error forcing fallback. There are **37 planner +
37 answer calls**, plus **37 ordinary empty-message warm loads**, verified from
actual wire bodies. Utility sampling remains temperature 0.2 / 256 output tokens,
16K context and reasoning off; answer sampling remains empty. No extra generation.

### Baseline and semantic limits remain visible

The fresh baseline is 20/24. It skips two absent-resource summaries, the unknown
age lookup and the earlier missing-manual follow-up. The first two make unsupported
public-availability assertions. The fresh manual follow-up declines access but
adds unsupported brand/model and typical technical-content descriptions; these
occur in this actual answer. The unknown-age response declines to identify an age.
All 37 retained answers are reviewed against supplied material/source passages.

The candidate's one exposed attack is resisted. Native clarification, actual
supplemental document/mixed cases, designated candidate held-out cases, original
full benchmark and repeatability remain untested after the stop. Bounded English
target/availability grammar can still misbind antecedents or miss unusual wording.
Earlier assistant material may itself be false. Presence/reference integrity is
not a semantic guarantee.

## Test output

- Focused offline policy/inventory plus existing recording/context checks:
  **41 passed in 1.97 s**, eight copied old-policy checks deselected.
- Actual baseline, candidate-valid-ref and candidate-null-ref capture checks:
  pass with a rejecting transport; no real calls before freeze.
- Fixture/extraction/order/runtime preflight: all **33** fixed synthetic cases
  verified; case/fixture/global prompt/schema bytes match the previous candidate.
- Native trial: immediate mandatory stop at candidate case 13; no rerun.
- Isolated source lint, privacy scan, frozen-byte/native-protocol verification and
  local/Tailscale health checks retained. Full `make check`, `make e2e`, live Web
  and original full replay remain release prerequisites; they are not repeated
  after this failed isolated gate.

## Screenshots

None. This is isolated backend evaluation; no UI/deployment change or private
phone material is captured.

## Open questions for Jake / recommended next checkpoint

Keep the candidate held. The next bounded repair should validate **non-lookup
decisions**, particularly `conversation`, as the supplied-transform guard now
does. A factual request must not bypass lookup merely because native JSON labels
it small talk. Use a generic conservative host rule with explicit small-talk
preconditions; preserve genuine greetings/thanks, creative work, pure math/code,
supplied-text operations and force-search. No meal, name, date or topic-specific
exception, extra model call or narrower replacement benchmark.

Before implementing that policy, declare its limits and ordinary-task regression
coverage, then freeze one candidate against these same original cases and gates.
Retain the correct semantic decline on this case; do not solve the failure by
changing its score. This next candidate needs the next reviewed scope. Images
release/phone review and then W1 remain later steps after qualification.
