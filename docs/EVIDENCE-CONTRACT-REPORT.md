# Evidence contract checkpoint — 9 October 2026

## Summary

Implemented and evaluated an isolated source-preserving answer contract on
`codex/reliability-hardening`. It constrains the existing answer call to evidence
IDs and renders original source text after host validation. It is **not qualified**:
the first full baseline pilot fails fact, citation, coverage and latency gates.
The separate attachment context-warning correction passes repository checks and
focused Chromium/WebKit tests. Neither change has been deployed. Full browser
testing retained one WebKit auto-scroll failure; the corrected check passes on
both browsers in a focused rerun.
The UI correction is preserved separately at `908ad2f`; the isolated experiment
and full evidence follow in the next commit on the same branch.

## Done-when checklist

| Item | Status | Evidence |
| --- | --- | --- |
| Preserve source fields and context | Implemented in isolated catalogues | `server/evals/reliability/evidence_contract.py`; source snapshots and units in v5 stream traces |
| Validate IDs, source ownership, duplicate keys, shape and completion | Implemented; rejected selections cannot emit factual text | `contract_stream.py`; `test_evidence_context.py`; `test_evidence_stream.py` |
| Prevent source markup/reference numbers becoming active content | v10 host replay, installed GFM AST and actual chat component pass on Chromium/WebKit at 390/1440 | Escaping/link-fragment tests; v7-v10 replay history; `evidence-v10/browser-check.log` |
| Explicitly decline unsupported information | Implemented; cannot establish universal semantic support | Rejected/empty evidence uses a fixed host response; v6-v8 block unidentified-speaker factual requests |
| Complete unchanged release benchmark | Full baseline pilot complete; failed | v5 baseline index and Web/Library reports |
| Everyday minimum 18/20 | Failed: 16/20 by declared checks | v8 manual review; ordinary production context builder intentionally unchanged |
| Web fact/citation/manual gates | Failed: 5/25 full cases | `2026-10-09-150907-qwen3-30b-a3b-workbench-32k-offline-keyword.json` |
| Library required facts/citations 100% | Failed: original 22/28 answerable final turns | `2026-10-09-151353-full.json` |
| Repeated qualifying trials | Not run | First baseline contract pilot fails; candidate full pilot and consistency repeats halted |
| Preserve previous inputs and reports | Pass: 7,296 inputs and all new frozen manifests verified | `artifacts/reliability/evidence-v10/freeze-verification.json`; v8 receipt for installed modules |
| Keep installed pipeline/runtime/default/data intact | Pass for affected installed modules | Same verification receipt; no production server changes or deployment |

## Changed files

- **Web:** shared context-budget estimator; AudioChip, DocumentChip, Composer and
  LiveAppShell reserve propagation; synthetic `/design` states and browser tests.
- **Isolated evaluation:** immutable source/unit catalogues, selection JSON
  adapter, frozen pilot driver, v4-v10 source/replay histories and diagnostics.
  No production provider, prompt, run, retrieval, schema or SSE implementation
  was changed.
- **Tests/docs/evidence:** seven synthetic contract test modules, frozen plans,
  replay reports, manual review and this H4 report. Private recording names,
  transcripts and screenshots were not used in evidence.

## Deviations from SPEC.md

The isolated answer stream is buffered until the one existing answer call finishes
and validates. It emits host-rendered text only after validation; this changes
latency and fluency and is not a product streaming change. The failed pilot
prevents integration. No extra answer, judge, retry, routing or Research calls.

The pilot plan originally proposed one complete run per installed profile. After
the first baseline full pilot failed, the candidate pilot was omitted: the
contract itself cannot pass its gates. This is not a measured candidate result
or a matched model comparison. No failing profile was retried into a pass.

v6-v10 are **host-only replays** of the same 62 saved selections. They make no new
model calls and cannot establish new retrieval, completeness, latency or model
consistency results. Original reports remain intact. Diagnostic grader behavior
is reported separately; the graders and thresholds were not changed.

## Runtime observations

### Context warning

The supplied numbers leave **4,259 raw tokens** (32,768 minus 28,509), but the
existing estimate reserves **8,192 response tokens and 256 safety tokens** when
the user has not set an output limit. That leaves **24,320 input tokens**.
The old warning incorrectly described this as exceeding the model's full window.

The correction states the input allowance and response reservation and honors
chat overrides before saved model defaults. An explicit **3,072 max output tokens**
gives **29,440 estimated input tokens** on a 32K model; the example's 28,509 then
fits the estimate. Counts remain approximate. No sampling value is silently
added or changed, and the existing server context policy remains unchanged.

### Full baseline pilot

| Measurement | Retained outcome |
| --- | --- |
| Ordinary everyday declared checks | 16/20; two format/conflict and two record-injection failures |
| Web full-case passes | 5/25 |
| Web required-fact case accuracy | 40% |
| Web search decision accuracy | 96.3% |
| Web lexical citation support | 0.1304; heuristic only |
| Web validated-answer TTFT | 15.13 s median / 23.27 s p90 |
| Library required facts / citation support | 22/28 = 78.6% each |
| Library retrieval | 100%; 20,000-passage p95 76.0 ms excluding query embedding |
| Library absent-information abstentions | 6/6; no benchmark injection obeyed |
| Library validated-answer TTFT | 6.79 s median; above the 6 s gate |

Of 23 grounded Web streams, 20 are rejected: 16 exceed the quotation cap and
four have ambiguous subjects or columns. Six of 39 Library turns exceed the
cap. A single invalid selected unit rejects the entire response. This avoids
releasing questionable text but sacrifices many available required facts.
IDs and source text are preserved; relevance and requested coverage are not
thereby established.

The original Web personal-breakfast answer selects an unrelated author's meal.
The v6-v10 conservative English unidentified-speaker guard blocks this, without
claiming to solve named-person identity, multilingual reference resolution or
the original search-decision failure. The frozen comparison still lacks the
Australian-currency evidence; no case or page was replaced to obtain credit.

The Library parental-leave/expenses answer omits the deadline; three multi-field
requests decline completely. Final-turn grading also hides declined first turns
in three follow-up cases. The resume table selects unrelated budgets, dates and
durations. All 39 Library turns and all 23 grounded Web streams were inspected;
these are genuine coverage/relevance failures, not parser-only failures.

### Rendering history and limits

| Version | Outcome |
| --- | --- |
| v4 | Setup failed before inference: isolated Library prompt omitted `sanitize`; archived exact source and failure. |
| v5 | Full baseline pilot above. Escaping periods/hyphens makes two raw Library assertions miss `0.5` and `ORCHID-42`; their visible values are retained. |
| v6 | Replays all 62 selections; neutral rejection wording and generic unidentified-speaker guard. No new inference. |
| v7 | Inline code preserves literal values but its separate citation-binding diagnostic scores 0/28. Retained failed compatibility trial. |
| v8 | Citation-compatible escaped Markdown retains 24/28 required-fact final turns, but only 20/28 satisfy the unchanged fact/citation grader. Four requested tables have visible per-row references that the existing sentence splitter fails to bind across periods inside cells. This is a separate compatibility limitation, not fabricated required facts or a release pass. |
| v9 | Encoded URL characters still become active links after GFM decoding. Failed synthetic parser diagnostic retained; not safe to integrate. |
| v10 | Wrap only URL/email fragments in literal code. Installed GFM parsing preserves the synthetic values with no links; same 62-selection replay still gives 24/28 facts and 20/28 facts/citations. No new inference. |

The 25-word quotation cap is intentionally preserved for this experiment. Applying
it to full context-bearing sentences makes useful complex answers impossible in
many cases. Narrowing source fields and separating quotations from user-owned
Library text should be reviewed before another inference experiment. Backticks
remain unsupported in selected text because the existing citation scanners do
not recognize all delimiter forms. Valid selections are never labeled verified
answers, and partial coverage is not reported as complete.

## Test output

`make check` passes: **406 Python tests, 39 frontend tests**, strict types,
format/lint, coverage, 74 contrast pairs, API type/additive, motion and privacy
checks. The latest focused run passes all **43 contract tests**, including the
three v10 tests added after full-suite collection; strict typing then passes
across 107 source files. Build passes with **240,843 / 256,000 bytes** initial
gzip JavaScript, excluding the specified lazy imports.
Focused attachment browser checks pass on Chromium and WebKit (6 tests).
The full 462-test browser run finishes with **458 passed, 1 failed, 3 existing
skips**. The failing WebKit /design code-copy action repeatedly leaves the control
outside the viewport; the clipboard action is not reached. Its trace and snapshot
are retained. The test now scrolls the control visibly to the center, asserts
that it is in the viewport, and keeps the original feedback and 1.5-second-clear
assertions. The focused copy/literal-rendering rerun passes **6/6** on both
browsers. No product copy behavior was changed. This is not claimed as a clean
full-suite rerun or a release qualification.

Full-run JSON metrics, one streaming trace and representative screenshots are
retained under `context-budget/full-suite-evidence/`, with hashes for all generated
outputs. Repetitive screenshots were discarded; older committed phase evidence
was restored. Every model trial, raw selection and failure diagnostic is retained.

## Screenshots

Synthetic mobile reserved/adjusted input examples:
`artifacts/reliability/context-budget/input-reserved-webkit.png` and
`input-adjusted-webkit.png`, with Chromium counterparts. The initial poor-layout
screenshots are retained separately from the refined full-width warning.
No private phone or document screenshots were captured.
The revised rendering is shown in
`artifacts/reliability/evidence-v10/browser/synthetic-literal-390-webkit.png` and
the 1440/Chromium counterparts. Decimals, signed values and identifiers retain
their exact visible text; source HTML, bracket numbers and URLs remain inert.

## Open questions for Jake

Review stop: **do not promote this answer contract or switch models**.
The next useful scope is to recover narrowly requested fields with their subject,
property, time and source context, review quotation handling separately for
public Web pages and user-owned Library files, and repair table citation parsing
with retained positive/negative tests. Then evaluate identical query-aware public
evidence on both installed profiles, keeping this benchmark and its failures.
More repeats of this failed contract will not establish reliability. Product
integration still requires complete semantic, performance and live-provider gates.
