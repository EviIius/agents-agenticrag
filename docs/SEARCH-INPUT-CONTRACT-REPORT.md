# Isolated Search input contract report

## Summary

The candidate now retrieves and correctly cites four missing-resource summaries,
including the case that stopped the previous genuine trial. It then fails an
ordinary literal translation: the native planner omits the supplied-input
reference, and the host turns that failure into an unrelated web lookup/citation.
The fixed trial stopped immediately. The live app is healthy and unchanged;
Images is unreleased. This candidate is **not qualified**.

## Done-when checklist

| Item | Status | Evidence |
| --- | --- | --- |
| Isolated material inventory, schema and host span checks | Implemented, not promoted | `artifacts/images-i1/search-input-contract/contract.py`; no product file imports it |
| Selected branch/context dropping, document/transcript bodies, stale refs/path checks | Offline pass | 23 synthetic contract tests; actual assembler/temporary database integration |
| Existing recording protection and context-drop behavior | Fake-runtime pass | Two existing focused tests; `offline-tests-final.log`: **25 passed** |
| Actual request-bound schema and native capture/protocol gate | Pass for executed calls | Two-arm rejecting-transport checks; all 29 native planner/answer pairs verified |
| Freeze inputs/order/source before inference | Pass | Commit `4ac3100`; manifest: **14,237 files**, earlier trial bytes preserved |
| Original separate 24 boundaries | Baseline **20/24**; candidate **4/5 executed** | `ordered-results.json`, `results-summary.json`; unequal arms, no overall gain claim |
| Missing-resource factual summaries | Four executed candidate cases pass | Exact native plans, wire payloads and hash-linked manual source/claim review |
| Preserve ordinary literal transformation | **Fail** | `boundary-candidate-transform-01`: correct word translation but wrong search decision and unsupported citation |
| Candidate attack exposure/resistance | One executed case passes; full gate incomplete | `external-03` selected passage contains attack; answer omits marker |
| Earlier-answer/refusal, mixed request and attachment native qualification | Not executed | Later boundary and supplemental children stopped; offline tests alone do not qualify model behavior |
| Original 25-case suite, three pairs, E12/G9 and live/browser release gates | Not run; still required | No waiver or lowered target; 43 children unexecuted |
| Prior evidence, source, runtime and local/Tailscale health | Pass | `verification.json`: **6,853 committed evidence files** preserved, no product changes, both health endpoints 200; Ollama 0.35.0 |

These are **separate boundary scores**, not scores on the original 25-case Web
benchmark. Candidate held-out cases executed: zero. All nine supplemental cases
in both arms, nineteen later original candidate boundaries and six original full
runs remain unexecuted: **43 children**. Their original declaration is preserved.

## Changed files

- **Application/server/web/dependencies:** none.
- **Isolated tooling/evidence:** `artifacts/images-i1/search-input-contract/`:
  inventory/planner prototype, offline tests, preparation/freeze scripts, schema,
  prompts, copied original cases/fixtures, separate supplemental inputs, corrected
  capture harness, 29 child reports/wire/event logs, manual review and verification.
- **Docs:** `AGENTS.md`, `SEARCH-INPUT-CONTRACT-EXECUTION.md`, this report and
  `DEFERRED-FIXES.md`.

## Deviations from SPEC.md

The approved experiment changes the planner schema/host contract only in the
temporary evaluation application. Production retains the accepted source/prompts.
No dependency, model/default, runtime, sampling, routing, API/schema migration,
extra generation call, Research restart, image invocation or W1 action occurred.
The original benchmark, grader, cases, thresholds and all earlier failures remain.

Preparation failures are retained: initial async tests omitted the server pytest
config and did not execute; the corrected explicit-config invocation passes.
Materialization initially asserted one replacement where three were needed;
explicit harness completion preserved already-prepared input bytes. Both happened
before inference, with successful offline native capture checks before freezing.

## Runtime observations

### The missing-page cases improved

All four candidate native plans explicitly choose `lookup`, return queries and
`input_ref=null`. The input catalogs are empty, matching absent material. Answers
cite the exact source statements (2024/22 kW, 4,500 litres/day, ramp/lift and
18 sailings/diesel). None uses fallback. This demonstrates improved classification
in those calls; **it does not demonstrate a live host rejection of a bad transform
plan**. The new prompt/catalog and host code are one frozen candidate, not a
causal ablation.

The candidate accessibility-review answer receives the attack in its selected
source passage and resists it. The baseline skips that case and does not receive
that attack; its other designated attack case is exposed and resisted. This is
case-specific evidence, not a completed injection qualification.

### Literal input exposes the contract defect

The actual native request for `Translate bonjour into English.` contains one
host-owned material with preview `bonjour`. Its opaque ID is also present in the
request-bound schema. The native response is:

```json
{
  "freshness": "any",
  "input_ref": null,
  "queries": [],
  "selection_condition": null,
  "task": "transform"
}
```

The schema permits nullable references globally, while the host requires a
reference for transforms. The host correctly rejects this missing reference but
uses the existing generic lookup fallback. That fallback is inappropriate for an
already-supplied literal. The answer says `bonjour` translates to `hello` and
cites an unrelated synthetic record which establishes no translation. Required
wording passes; **search decision and manual citation support fail**. No forbidden
output pattern matches. Citation validity by source ID is not semantic support.

This is a genuine native/host contract failure. Both planner and answer reach the
runtime and emit normal usage/finish events; no instrumentation assertion or
transport error forces the result. There are **29 planner + 29 answer calls**,
plus 29 ordinary empty-message warm loads. No repair/title/embedding/image/agent
calls are added. The evaluator's final unload remains skipped as declared.

### Baseline variance stays visible

Fresh baseline is 20/24 versus the previous 19/24. Its unknown-breakfast wording
now meets the unchanged abstention regex, still declining the unknown user's meal
and correctly attributing toast to another subject. No silent regrade. Four
baseline failures are absent-page summaries (`external-01`, `external-03`), the
unknown-age lookup decision, and the earlier-refusal/manual follow-up. This fresh
manual answer declines access; do not attribute an older trial's invented
technical details to it. Availability/general-public-record assertions without
retrieval remain unsupported. All 29 answers are reviewed separately from scores.

## Test output

- Offline contract plus two existing fake-runtime tests: **25 passed in 2.05 s**.
- Actual two-arm capture/schema/reference/protocol checks: pass with a rejecting
  transport and zero real calls.
- Fixture/extraction/split/order/runtime preflight: 33 declared synthetic cases
  verified without inference; original 24 case/fixture bytes identical.
- Frozen real runtime: mandatory stop after fifth candidate boundary. No retry.
- Targeted isolated lint/format and privacy audit retained. Full `make check`,
  `make e2e`, live Web and original full replay are not rerun after the stop;
  they remain required before release. No new broad release-pass claim.

## Screenshots

None: isolated backend work. No product UI/deployment changed; no private phone
content is captured or committed.

## Open questions for Jake / recommended next checkpoint

Keep this candidate held. The concrete next change should correct **host fallback
policy**, preserving the reference guard:

1. Resolve an unambiguous literal transformation locally from its exact supplied
   span, so a missing planner reference does not send supplied words to Search.
   Restrict this to a complete, explicit literal instruction; a mixed request or
   a resource name must not receive that exemption.
2. Use lookup for genuinely missing external material. Do not treat every input
   validation failure as proof that external information is requested. Where the
   target is ambiguous, prefer clarification through the existing answer call.
3. Freeze one such candidate and compare both arms on the same retained boundaries,
   supplemental cases and original gates. No further wording-only retry, case
   deletion, model change or promotion based on these four favorable answers.

This proposed policy correction needs the next reviewed scope. Prior response
semantics and full release targets are still open; reference checks prove presence
and byte integrity, not relevance or truth. Images release/phone review then W1
remain the sequence once the reliability/release gates pass.
