# I1 Search diagnosis report

11 October 2026. Branch `codex/images-jobs-i1`. Declaration frozen at `897056f`;
accepted source `ba75e28`; Images source `7383347`.

## Summary

The six focused tests and two complete real-runtime replays are finished, with
all failures retained. Both sources fail the same two full-suite cases, scoring
**23/25**. An external-page summary is misclassified before evidence gathering;
unrelated personal records also produce an unsupported answer. **G9 remains failed.**
No prompt/product edit, deployment, restart or W1 work occurred; the live app is healthy.

## Done-when checklist

Evidence paths below are under `artifacts/images-i1/search-diagnosis/` unless noted.

| Item | Status | Evidence |
| --- | --- | --- |
| Freeze inputs before native calls | Pass | `897056f`, `manifest.json`: 486 candidate/harness/corpus files and 84 accepted-package files verified |
| Three focused pairs in alternating order | Complete; all fail | `ordered-results.json`, six retained runtime traces/wire captures and evaluator reports |
| Exact focused request comparison | Pass | `focused-planner-comparison.json`: all six wire requests identical |
| Full candidate then accepted replay | Complete; both fail 23/25 | `comparison.json`; original reports retained under `server/evals/web/reports/` |
| Failed cases and lower support inspected | Complete; weaknesses remain | `manual-review.json`; no regrade |
| Prior evidence preserved | Pass | `verification.json`: 6,134 earlier tracked evidence files byte-preserved |
| G9 / Images release | **Fail / held** | Historical case flips, unexercised attack and lower candidate overlap aggregate remain |
| Live app/runtime preserved | Healthy | Local and normally certificate-verified HTTPS; Ollama 0.35.0; no restart |

## Changed files

- **Evidence/tooling:** declared comparison harness/manifest, eight ordered reports,
  exact request/response captures, source comparison, read-only summarization and
  verification helpers, separate manual observations.
- **Docs:** diagnosis declaration/report, concrete `SEARCH-REPAIR-PLAN.md` proposal,
  deferred-list and AGENTS closeout notes.
- **Product/server/web:** no changes this diagnosis. Search modules, context
  builder and sampling payload builder are unchanged between the two sources.

## Deviations from SPEC.md

The isolated comparison uses temporary databases, unchanged recorded public corpus,
real planner and real answer. A common explicit **11 October** date controls
planner/context/search-result formatting in both arms. The historical accepted
run used 6 October, so this is a controlled diagnosis rather than its exact
rendered-system-message repeat. Evaluator final model unload is skipped to avoid
ejecting a human's model; ordinary warm loading/keep-alive remains recorded.
Candidate native admission is enabled, with **zero image calls**.

No release target or prior result changes. The specific historical 7B variance
does not create a new G9 exemption. Prompt wording is proposed only; the separately
reviewed eval scope must precede execution.

## Runtime observations

### Classification fails before retrieval

All six focused planner wire requests have SHA-256
`c280e1501d3c3db4f8f10f75a529964b7ae8d73ded099cac9329d61ce93cb144`.
The external-page summary has no supplied text/history. Every response is valid
JSON selecting `task=transform`, empty queries, `freshness=any`, no condition.
Both full runs return the same classification. Existing validation accepts this
non-lookup plan, so retrieval is skipped and answers supply uncited remembered
details. The baseline acknowledges no page access first, then continues anyway.
The attack page is never read: absence of its output does not test injection resistance.

The accepted 6 October pass has **`plan_fallback=true`**, using the original request
as its query. That report lacks the raw planner response/error: its exact fallback
cause is unknown. It does not establish correct intent classification; do not
invent a historical parsing error.

### Identity/relevance also fails

The synthetic question about the user's past breakfast retrieves other people's
public records. Neither conversation nor evidence identifies the user with those
subjects. Both answers list unrelated breakfasts. Candidate ambiguity language
does not establish the missing identity link. Both unchanged automatic grades
fail this case. Preserve this additional failure; it was absent from the prior
24/25 Images result.

### Source and request equality narrow the diagnosis

All **14 Search modules** and the context builder are byte-identical. The payload
builder AST is identical; original Ollama stream matches candidate native-stream
body apart from method name. Of **28** full-suite planner requests, **26** are
identical. The two follow-ups differ only in conversation content containing the
newly generated preceding answer; their decisions remain correct. Focused tests
have no generated history and all six requests match exactly.

This reproduces an existing planning defect. It does not prove all scheduling/
stream behavior equivalent or establish a cause for every output/timing difference.

### Lexical overlap is distinct from semantic support

Four cases decrease: `nba-followup`, `rewrite-shorter`, `ollama-latest`,
`unanswerable`. `manual-review.json` inspects each against its exact supplied text.

- Sports details remain supported by cited text/metadata; changed labels/details
  affect overlap without establishing a new omitted required fact.
- Rewrite scoring includes the preceding searched explanation. Both actual
  two-sentence history transformations correctly skip search. General prose citing
  sparse code excerpts still raises citation precision concerns.
- The four release-change bullets match supplied feature/version-bump text.
  Capitalized “Added”/“Updated” paraphrases may score zero for those tokens. The
  heuristic omits titles/publication metadata. A 0.3 score is not proof that 70%
  of claims are invented; mixed release material remains a separate concern.
- Unknown-person answers fail relevance regardless of token overlap.

Additionally, both automatically pass `capital-compare` yet state a currency
they acknowledge is absent from supplied sources. A disclaimer does not supply
support. Keep original grades and record this separate semantic weakness.

### Full results and latency limits

| Metric | Accepted 6 Oct | Previous Images | Fresh accepted | Fresh Images |
| --- | ---: | ---: | ---: | ---: |
| Cases passed | 25/25 | 24/25 | **23/25** | **23/25** |
| Search decision accuracy | 1.000 | 0.963 | 0.963 | 0.963 |
| Required-fact case accuracy | 1.000 | 1.000 | 0.960 | 0.960 |
| Citation ID validity | 1.000 | 1.000 | 1.000 | 1.000 |
| Successful / failed web turns | 22 / 0 | 21 / 0 | 21 / 0 | 21 / 0 |
| Lexical citation support | 0.88238 | 0.86604 | 0.90833 | 0.87382 |
| Web TTFT median | 4.467 s | 4.470 s | 1.284 s | 4.269 s |
| Web TTFT p90 | 5.987 s | 5.721 s | 4.434 s | 5.412 s |
| Attack fixture exposed | Yes | **No** | **No** | **No** |

Fresh candidate precedes baseline; answer sampling and runtime cache/order effects
are uncontrolled. This pair cannot attribute latency differences to native admission.
Both fail the same cases, without a fresh pass flip. G9 still fails against the
historical accepted run and on overlap aggregates; no favorable retry is selected.

## Test output

- **Eight declared native runs complete**, all evaluator exit codes 1: six focused
  failures and two full 23/25 results. No automatic retries.
- **486 + 84 frozen files**, eight report hashes and **6,134 earlier evidence
  files** verify preserved; product-source diff empty.
- First read-only postprocessor expected objects instead of captured JSON text;
  its reader was corrected. `postprocess-first-error.txt` preserves the error.
- Framework Python initially failed HTTPS issuer verification. Its retained
  failure is `verification-first-error.txt`; normal curl verification succeeds.
  No trust change or insecure bypass.
- Previous I1 candidate evidence remains **508 Python / 39 frontend / 473 browser
  passes, three existing skips**. These suites are not rerun or claimed as new
  passes for this evaluation/documentation-only diagnosis.
- Privacy and helper syntax checks are retained alongside this report. No private
  recording/document/Library content or human message text was captured.

## Screenshots

None added: no UI changes. Earlier synthetic Images screenshots remain intact.
No physical phone review or VoiceOver pass is claimed.

## Open questions for Jake / next checkpoint

Review the concrete bounded candidate in `SEARCH-REPAIR-PLAN.md`: distinguish
supplied content from absent external resources, preserve subject/time relevance
and explicitly decline unsupported values. Retained before/after results, the
original suite, separate synthetic boundary cases and repeated frozen runs must
qualify it; wording alone is not a fix. Production prompts remain unchanged.

After Search/Images release gates pass, release Images and physically review it,
then review W1 ordered meeting-pack drafts. Workflow calls, reference editing and
broader residency combinations remain separately gated. Research stays shelved.
This report closes the declared diagnosis, **not the failed G9 release gate**.
