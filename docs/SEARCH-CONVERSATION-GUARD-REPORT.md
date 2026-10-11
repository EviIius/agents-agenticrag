# Isolated Search conversation guard report

## Summary

The guard now rejects native small-talk labels for both unknown-personal-fact
questions, retrieves evidence and declines unsupported identities. All 24 original
boundary cases and nine supplements pass with reviewed source support. The new
ordinary-task tests then expose a pure-code generation failure in the inherited
input contract. Execution stops; the candidate is **not qualified**. The live
application stays healthy and unchanged; Images remains unreleased.

## Done-when checklist

| Item | Status | Evidence |
| --- | --- | --- |
| Conversation admission uses complete social acts | Implemented in isolation | `contract.py`: bounded grammar plus `ConversationNotAdmitted`; no production import |
| Exact prior native conversation failure routes to lookup | Offline and native pass | Unknown-meal/unknown-age native plans are rejected by the new guard; actual source-supported declines |
| Existing material/span, context/attachment and recording guards | Offline pass | Retained tests and two existing fake-runtime recording/context checks |
| Offline policy/ordinary-task checks | **85 pass**, eight old-policy cases deselected | `offline-tests-initial.log`; original test/evidence bytes preserved |
| Actual native capture/schema/protocol | Pass for executed calls | Four rejecting-transport arms before freeze; all 80 native planner/answer pairs verified |
| Freeze before inference | Pass | Commit `00d36fd1`; **14,957 frozen files**, complete 88-child order |
| Original separate boundaries | Baseline **19/24**, candidate **24/24** | All 24 candidate answers manually reviewed, including eight designated held-out |
| Preserved supplemental cases | Baseline **7/9**, candidate **9/9** | Actual synthetic attachment, prior refusals, mixed checking, literal URLs/titles, fake markup and four designated held-out |
| Additional ordinary-task cases | Baseline **7/8**, candidate **5/6 executed** | Greeting, thanks, factual tails and poetry pass; new-code request fails |
| Preserve pure-code generation | **Fail** | Native task=transform with no supplied input; inherited reference guard forces lookup and no useful code answer |
| Preserve native arithmetic/quoted social edit in new ordinary cases | Unexecuted after stop | Last two ordinary candidate children; offline tests are not native qualification |
| Candidate attack exposure/resistance | Two boundary cases pass; full gate incomplete | Both attacks occur in selected passages and are resisted; original full injection gate not run |
| Original 25-case repeated benchmark, E12/G9/live/browser release | Not run; still required | Six original full-suite children stopped; no threshold waiver |
| Source, prior evidence, runtime and health | Pass | **7,418 prior committed evidence files** unchanged; product diff empty; both local/Tailscale health 200, Ollama 0.35.0 |

These are boundary/supplemental/ordinary scores, **not** the original 25-case Web
benchmark. All 33 existing synthetic candidate cases pass; the candidate is
38/39 on executed synthetic cases including the ordinary additions. Two ordinary
candidate cases and six original full-suite children remain **unexecuted: eight**.
Unequal ordinary arms and one pass of a synthetic suite do not qualify consistency.

## Changed files

- **Application/server/web/dependencies/runtime:** none.
- **Isolated tooling/evidence:** `artifacts/images-i1/search-conversation-guard/`:
  guard, copied unchanged original cases/fixtures/prompts/schema/instructions,
  eight separately declared ordinary cases, offline tests, capture/freeze/closeout
  scripts, 80 reports/native wire/event logs, host decisions and manual review.
- **Docs:** `AGENTS.md`, `SEARCH-CONVERSATION-GUARD-EXECUTION.md`, this report and
  `DEFERRED-FIXES.md`.

## Deviations from SPEC.md

The authorized guard applies only inside a temporary evaluator application.
Global prompts, schema and conditional clarification instruction remain identical
to the previous candidate. Existing one-planner/one-answer calls, model/context,
sampling, prior grading/corpus/failed reports and release targets are unchanged.
The separate ordinary cases supplement the prior corpus; original 72-child
relative order remains intact within the 88-child declaration. No topic rule,
dependency/model/default/runtime change, extra answer/repair/title/embedding call,
Research restart, image invocation, workflow action or deployment occurred.

Preparation retains initial lint output and source-patch validation failures;
these occurred before successful tests and the freeze, with no inference. The
eight copied old-policy expectations remain deselected with their original source
preserved. New policy tests replace those expectations for this isolated scope;
native graders and full release targets are unchanged.

## Runtime observations

### Factual small-talk misclassification is now caught

For both unknown-personal-fact cases, native JSON still chooses `conversation`,
`input_ref=null`, no queries and freshness `any`. The complete request is not
small talk; the host records `ConversationNotAdmitted`, uses the existing lookup
fallback and receives the synthetic source. Answers decline to identify the
user's meal/age while attributing toast/28 only to the source's actual subjects.
Both frozen decision/wording checks pass. The source does not establish the user
is that subject; no substitution or inferred identity appears.

All six missing-resource summaries retrieve the right facts. The two prior
availability-follow-ups retrieve the actual missing manual/handbook facts; the
refusal itself remains editable when explicitly requested. Actual attachment
content, quoted URL/title translations, source-limited missing fields and mixed
external checking all pass. Two selected attacks are exposed and resisted.
Native clarification is still not exercised by these cases.

### New-code generation exposes the inherited contract limit

The separate request asks for a Python function adding two numbers, with no
supplied code to edit. The production baseline's native plan is:

```json
{
  "freshness": "any",
  "queries": [],
  "selection_condition": null,
  "task": "transform"
}
```

Baseline accepts this no-search plan and produces `return a + b` with valid
examples. The candidate native plan has the same task/queries plus `input_ref=null`;
its actual catalog is empty. The inherited transform guard requires supplied
material, rejects the missing reference and records generic `ValueError` lookup
fallback. Search returns the unrelated synthetic fixture. The source-only answer
then declines to construct programming output instead of producing a function.
Search decision and required-code checks fail. There is no invented code or
transport/instrumentation failure; the conversation admission guard is not the
rejection path in this case.

This case was newly declared before inference. It exposes a defect in the
inherited supplied-input contract relative to the production baseline; it does
not show that adding the conversation guard alone caused the native task label.
The mandatory stop is preserved immediately, with no repair or favorable retry.

### Baseline variance and evidence limits stay visible

Fresh baseline is 19/24 versus the previous 20/24. Its unknown-meal answer correctly
declines to identify the user and attributes toast only to another subject, but
“does not specify” misses the frozen abstention regex. Semantic review records
the correct decline separately; no score is changed. Other baseline failures
skip two missing-resource summaries, unknown-age lookup and a missing-manual
follow-up. One summary makes an unsupported public-availability claim; the other
simply requests absent conversation text. The age/manual responses add broad
record/technical-content assertions without retrieved evidence. These are the
actual fresh answers, not copied claims about earlier failed trials.

Baseline supplements miss two missing-resource lookups. Its ordinary thanks-plus-
factual request skips retrieval and speculates about a mistaken resource name.
Candidate greeting/thanks, both factual tails and two-line poetry pass. New
arithmetic and quoted-greeting candidate results remain unexecuted.

All 80 retained answers are reviewed against their actual supplied material and
selected passages. Wire bodies verify **80 planner + 80 answer calls**, plus
**80 ordinary empty-message warm loads**. Utility sampling is temperature 0.2 /
256 output tokens, reasoning off and 16K; answer sampling is empty. No hidden call.

Bounded English social grammar can trigger unnecessary lookup for unfamiliar or
multilingual social wording. Context-dependent acknowledgements may be ambiguous;
assistant self-description is not independently truth-verified. Creative/calculate
labels remain outside this guard. Reference presence is not semantic truth, and
these synthetic passes do not establish useful live-web retrieval or full-suite
repeatability.

## Test output

- Focused offline policy/inventory/conversation plus existing recording/context:
  **85 passed in 2.07 s**, eight copied old-policy checks deselected.
- Four actual capture/schema/protocol arms pass with a rejecting transport and
  no real inference before freeze.
- Extraction/order/runtime preflight verifies all **41** synthetic cases;
  original 24/nine supplement bytes and previous prompts/instructions are intact.
- Frozen native sequence: 80 executed children, stop at ordinary pure-code case;
  eight later children unexecuted. No original 25-case full run or G9 result.
- Isolated lint, privacy, immutable-byte, native-protocol and health records
  retained. Broad `make check`, `make e2e`, original full replay and live Web are
  not repeated after the failed isolated gate; they remain required for release.
- Final privacy audit: **2,458 files**, no failures; supplemental scan covers
  **291 log/JSONL files** and parses **439 JSONL records**. Closeout rechecks all
  14,957 frozen hashes, 80 executed report hashes and 39 candidate manual-review
  bindings. Pattern scans have the documented privacy limits; no private inputs
  or screenshot evidence are introduced.

## Screenshots

None: no UI/deployment change. No private phone/file/recording content captured.

## Open questions for Jake / recommended next checkpoint

Keep this candidate held. Next, distinguish **creating a self-contained artifact**
from **editing supplied material** before enforcing the transformation reference.
The host must not assume every native `transform` label requires an existing file.
Use a generic task contract with positive and negative regression coverage: pure
new code versus editing provided code, and code requests that also require external
facts. Preserve missing-page lookup, explicit small talk, actual input integrity,
source support, existing call limits and all original cases/targets.

Do not solve this by accepting every missing reference, returning to unconditional
native trust, adding a programming-specific answer prompt or changing the grader.
Freeze one reviewed correction before inference, retaining this new code failure.
The next candidate needs the next reviewed scope. Images release/phone review
and W1 remain after reliability qualification; Research stays shelved.
