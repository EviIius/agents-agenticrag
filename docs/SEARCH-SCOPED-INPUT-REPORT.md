# Scoped-input binding report

## Summary

The scoped comparison repair now directly handles native transform/null reference,
preserving both original weights without false clarification. All 49 synthetic
candidate cases and both scope/code smokes pass. The original full benchmark
then fails at **22/25**, with creative routing regressions and unsafe/incomplete
source-role answers; targeted review finds additional automatically passing
answers that violate grounding or requested chronology. Release remains held.
The live app/source/runtime stay healthy and unchanged.

## Done-when checklist

| Item | Status | Evidence |
| --- | --- | --- |
| Normalize one leading only/just, preserve actual body/reference | Implemented in isolation | `contract.py`: literals/local_target/scope_target; all other policy AST unchanged |
| Conditional/resource/external/ambiguity protections | Offline pass | `test_scope.py`: 24 targeted checks; actual IDs, availability/dropped context, force and multiple attachments |
| Existing policy/recording/context/wording/Web grading | **200 pass**, eight old-policy cases deselected | `offline-tests-final.log`, 2.04 s; original source/evidence retained |
| Actual capture/schema/protocol/grade preflight | Six arms pass | Rejecting transport includes scoped comparison; actual wording-hook/report bindings verified |
| Freeze once before inference | Pass | `b6326124`, **16,675 frozen files**, **9,098 prior evidence files** preserved |
| Original 49 cases/fixtures/prompts/schema/wording and earlier order | Pass | Byte checks, unchanged wording/audit, previous 106-child order after two prepended smokes |
| Scope/code smokes | **2/2 per arm** | Actual supplied comparison values/units/relation, no clarification instruction; working a+b code |
| Exact native missing-reference comparison fallback | **Native pass** | Repeated `history-06`: transform/null ref/no queries, host local binds actual ID, complete 7 kg/9 kg comparison |
| Original synthetic boundaries | Baseline **20/24**, candidate **24/24** | All eight designated-held-out candidate cases executed; actual sources/observations retained |
| Supplemental synthetic cases | Baseline **7/9**, candidate **9/9** | Actual attachment, missing resources, mixed request, fake markup, literal transformations |
| Ordinary synthetic cases | Baseline **7/8**, candidate **8/8** | Greeting/thanks, factual tails, poem, new code, arithmetic and quoted edit |
| Creation synthetic cases | Baseline **7/8**, candidate **8/8** | Code, fiction, actual/missing code, mixed verification, output constant, limited API documentation |
| Full original 25-case benchmark | **Baseline 24/25; candidate 22/25** | First matched pair only; candidate fails haiku, comprehensive list and fiction |
| Full injection exposure/resistance | Candidate pass; baseline fail | Candidate retrieves/exposes the attack; baseline skips retrieval and answers from memory |
| Semantic source-role/property/coverage safety | **Fail** | Reversed champion/runner-up roles; unsupported currency despite automatic pass; wrong results chronology/granularity |
| E12/G9/repeated release qualification | **Fail / incomplete** | Three mandatory case failures and matched G9 regressions; two later pairs unexecuted |
| Product/runtime/health | Unchanged, pass | Product diff empty; local/verified Tailscale HTTPS health 200; Ollama 0.35.0 |

**104 of 108 children executed**: four smokes, 98 synthetic children and the first
two original full-suite children. **Four later full children remain unexecuted**.
The original full suites contain 28 turns each. Actual wire verifies **158 planner
+ 158 answer + 104 empty-message warm-load requests**. No retry/extra judge/call.

The 49/49 synthetic score is separate from the 22/25 original score. Synthetic
wildcard evidence is deliberately simple and does not stress realistic retrieval
coverage or large tables. Those successes do not qualify general Web reliability.

## Changed files

- **Server/web/shared/dependencies/runtime:** none.
- **Isolated source/evidence:** `artifacts/images-i1/search-scoped-input/`:
  bounded scope correction, copied unchanged prior corpus/policy/wording, tests,
  frozen 108-child declaration, real native/grade capture, 104 reports, source/wire/
  event/host decisions, reviewed smokes/boundaries, full failure analysis and
  immutable/privacy/health records.
- **Docs:** `AGENTS.md`, `DEFERRED-FIXES.md`, execution declaration, this report
  and `SEARCH-TASK-AND-EVIDENCE-AUDIT-PLAN.md` (next proposal only).

## Deviations from SPEC.md

The authorized host grammar correction changes only literal inventory and local
target interpretation plus one bounded helper. All other policy AST, approved
wording correction, global prompts/schema/instructions, original 49 cases/fixtures,
original 25-case corpus, numerical/semantic/citation/latency requirements and past
failures are preserved. No topic rule, prompt expansion, runtime/model/default/
dependency/sampling change, production integration/deployment, Research/image/
workflow invocation or additional model call. Initial preparation lint/formatting
records are retained; eight old-policy expectations remain deselected with their
original source/evidence. No correction/retry follows the native stop.

## Runtime observations

### The specific scope-binding defect is repaired

Early comparison smoke has a valid native reference and complete output; this
alone does not prove handling of reference omission. The repeated boundary case
then returns **transform, input_ref=null, queries=[]**. The host binds the exact
visible original comparison ID locally, never enters clarify, and the actual
answer preserves both names, original values/units and correct lighter/heavier
relationship. This directly exercises the previously failed path. New-code smoke
continues to exercise create_local and useful addition code without Search.

### Native creative label plus stray queries causes wrong host fallback

Both original creative failures emit **task=creative** with nonempty query lists.
The inherited host policy rejects non-lookup queries as ValueError, then falls
back to lookup. The haiku/story are still produced, but two unnecessary searches
fail because no corresponding factual evidence exists in the fixed replay corpus.
This is actual routing regression, not a browser/UI or provider-protocol failure.
The output-format coverage/admission policy does not currently recover these
contradictions. Do not misdescribe them as native transform labels or absent
uploaded documents; retain the exact native plans in the failure analysis.

### Comprehensive facts require roles, coverage and time, not just valid citations

The list case's native plan adds an unrequested **later won** relationship and
returns no selection condition. Selected evidence mixes postseason stages,
partial historical tables and a flattened champion/runner-up table. The answer
omits required population members, then cites actual champions as Finals losers
in several rows. The stored source explicitly labels champion and runner-up;
these role reversals are contradicted by the very cited evidence. A conference
semifinal exit is also described at the wrong tournament stage.

`full-failure-analysis.json` binds five concrete champion/runner-up reversals to
actual selected-source fragments. The answer's cited IDs are structurally valid,
but its claim meanings are not. The blacklist also misses some wrong inclusions
because their bullets start with an article. Original checks/scores remain intact;
manual review records genuine unsupported/incomplete claims separately.

Two **automatically passing** answers also fail targeted review:

- The capital/currency comparison explicitly supplies a currency from memory,
  claiming it is known and not contradicted, while admitting the selected sources
  do not detail it. Both queries request both properties; retrieved source coverage
  is unbalanced. Source absence is not permission to answer from memory.
- The last-five-results answer mixes individual games across older years and
  labels them recent results. Its granularity/chronology does not deliver the
  requested recent-series coverage. The weak frozen lexical check passes.

These are not equivalent-wording failures. No automatic score is silently changed,
and no semantic pass is claimed for the other automatically passing full answers.
The full review is targeted failure diagnosis, not complete independent grading.

### Baseline weaknesses and limits stay visible

Fresh baseline synthetic failures include absent-resource lookups, user-age
lookup, unsupported archive access claims and mistaking a named script for a
different programming ecosystem. Its full injection case skips the required
page retrieval and emits uncited memory claims, including unsupported dates and
player statistics. It therefore scores 24/25 with injection unexercised. Baseline
weakness does not excuse candidate regressions or lower release thresholds.

The limited API synthetic case retrieves/cites the documented route and explicitly
declines unspecified behavior, without producing a function. It passes its frozen
grounding/lookup rubric; it does not qualify useful API-code generation. True
ambiguous-target clarification remains unqualified. Bounded English parsing and
single-reference validity do not prove arbitrary intent or semantic correctness.

### Matched G9 and stop provenance

| Metric | Baseline | Candidate |
| --- | ---: | ---: |
| Full cases passed | 24/25 | 22/25 |
| Search decision accuracy | 96.30% | 92.59% |
| Required-fact accuracy | 100% | 96% |
| Citation ID validity | 100% | 100% |
| Lexical citation support mean | 0.873243 | 0.898798 |
| Successful Web turns | 21 | 22 |
| Failed Web turns | 0 | 2 |
| Successful Web TTFT median | 4.233 s | 4.427 s |
| Successful Web TTFT p90 | 5.212 s | 5.950 s |

Matched G9 fails quality, failed-turn and latency comparisons. Higher lexical
support does not resolve the observed role/property errors. Historical G9 is
not computed after mandatory candidate failure; its accepted report is preserved.
The stored final stop reason says matched G9 because the existing orchestrator
overwrites the earlier mandatory-case reason with G9. Its mandatory_checks_pass
remains false, all three failures are retained, and no later child runs. The
separate analysis records both blockers without mutating the original index.

## Test output

- **200 passed**, eight old-policy checks deselected, 2.04 seconds.
- Six rejecting-transport capture/schema/protocol arms plus actual grading-hook
  bindings pass; zero native inference before freeze. 49 fixtures/runtime validate.
- All 49 synthetic candidate cases pass with retained boundary review. Scope/code
  smokes and actual missing-ref recovery pass; first original full pair fails.
- All 158 planner/answer calls and actual grade records verify native wire/events/
  frozen schema/parameters/report hashes; 104 warm loads accounted for.
- Immutable-byte, targeted source/role review, privacy and health records retained.
  No broad make check/e2e, fresh live Web, later pairs or phone review follows a
  failed isolated gate; all remain required for product release.

## Screenshots

None: no UI or deployment change; no real recording/document/phone content captured.

## Open questions for Jake / recommended next checkpoint

Use `SEARCH-TASK-AND-EVIDENCE-AUDIT-PLAN.md` next: an offline audit of the retained
task/query contradictions, evidence extraction/header/role preservation, requested
property coverage and granularity. Separate structural grading from semantic
support, then propose one bounded correction with early original-case smokes
before further native inference. Preserve this scope fix and all original targets.
No topic-specific patch, hidden repair/judge call, failed-selector restart or
favorable retry is part of that proposal.

Images remains held, Research shelved, W1 unstarted. No product deployment or
default switch follows these partial improvements.
