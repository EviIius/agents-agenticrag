# Evidence fields checkpoint — 9 October 2026

## Summary

Table-row citation binding and the incorrect public quotation limit on Library
files are repaired in evaluation tooling. An isolated original-column selector
and smaller evidence payload are implemented. The new native baseline trial
fails its protocol and was interrupted; it is **not qualified or deployed**.
A stricter prospective schema is prepared and unit-tested, without new inference.
The installed production source remains the stable `f87db46` application.

## Done-when checklist

| Check | Result |
| --- | --- |
| Retain original cases, corpus, reports and prompts | Pass; original 7,296 input hashes verified |
| Keep citations local to their table row | Pass; positive and negative placement tests |
| Separate public prose/data and Library excerpt limits | Implemented; host-only diagnostic improves, new Library trial not executed |
| Select original columns with source and context | Implemented in v11; native protocol fails |
| Keep row identity, dates, qualifications and blank cells | Tested; v12 also guards the first named field after an ordinal |
| Reduce repeated source/paragraph input | Median payload characters reduced 54.36% Web / 55.33% Library on identical saved sources; not a token/latency qualification |
| New full Web/Library and semantic/performance gates | **Not passed**; Web trial interrupted, Library and candidate not run |
| Repository regression checks | `make check` passes; no new product UI/browser run |
| Deployment or default promotion | Not performed |

## Changed files

- `server/evals/library/citation_binding.py` and
  `server/tests/test_library_eval.py`: treat each Markdown table row atomically;
  periods inside cells cannot detach a Citation-column reference. A neighboring
  row, an out-of-row reference, linked reference or wrong source cannot supply it.
  Fact predicates and original benchmark cases are unchanged.
- `server/evals/reliability/evidence_contract_v11.py`, its stream wrapper,
  isolated driver and `trials/evidence-v11/`: one existing answer call selects
  source IDs and original row column indexes. Reject invalid shapes/references,
  missing identity/scope columns, ambiguous units and over-budget excerpts.
  Original values and full source snapshots remain auditable; unsupported
  information gets an explicit decline rather than model-memory facts.
- `server/evals/reliability/evidence_schema_v12.py`: **unexecuted remedy** with
  per-unit schema branches. Prose admits no columns; ambiguous fragments are not
  selectable. Row branches require identity/scope positions and constrain the
  remaining indexes to that original row. Native runtime compatibility with
  these schema keywords remains unverified.
- `server/tests/test_evidence_fields.py` and `test_evidence_schema.py`: novel
  properties, blank values, qualifiers/dates, signed values, forged/duplicate
  indexes, public/Library budgets, ordinal identity and immutable snapshots.
- `review_fields_v11.py`, `artifacts/reliability/evidence-v11/` and scoped plan:
  frozen prompts, original inputs, parser regrades, saved-selection host replays,
  raw partial trial streams, coverage analysis and checks. Historical v8/v10
  citation grader sources are archived before changing their common module.

## Deviations from SPEC.md

This is the explicitly authorized isolated checkpoint, not production E8/J7
integration. Existing source-call, sampling, dependency and runtime limits remain.
Public prose stays at 25 words per source; compact original table data has a
separate 512-word ceiling (six words per selected cell/header). Library excerpts
have a 2,000-word document ceiling and a 4,000-word aggregate ceiling. These are
experimental rendering policies, not lowered release targets or a legal claim.

The predeclared first full Web/Library pilot was stopped after observed protocol
failures. Do not convert partial outcomes into a full-suite accuracy score.
The driver and child were interrupted with SIGINT; cancellation also interrupted
one grounded stream. No new Library run, candidate run or repeated pilot followed.
The schema remedy has only host/schema tests, no native call or qualification.

The v11 trace was observed after multiple cases had run, rather than automatically
stopping on its first invalid selection. Future pilot tooling needs an immediate
protocol stop before starting the next model call.

## Runtime observations

### Three different measurements

| Measurement | Result | Meaning |
| --- | --- | --- |
| Parser-only regrade of original v5 answers | 22/28 remains 22/28 | Original missing facts/declines are not repaired |
| Parser-only regrade of v10 host-rendered answers | 20/28 → 24/28 | Four table-format binding misses recovered; original reports unchanged |
| v11 host replay of unchanged v5 selections | 27/28 final-turn required facts/citations | Library budget/format diagnostic, **not new inference or semantic qualification** |
| New v11 native grounded Web streams | 15 rejected, 1 unsupported, 1 interrupted | Protocol failure; no factual evidence emitted |

All 17 grounded traces, including earlier turns, were inspected. Eleven completed
selections put indexes on sentence evidence, two selected ambiguous fragments,
one lost row identity/column binding, and one exceeded the public budget. The
remaining completed selection declined despite supplied relevant evidence.
Raw selections are retained; none was rewritten into a successful model answer.

The host-only Library diagnostic's remaining required-fact failure is
`parental-expenses`: the old selection omits the 14-day expense deadline.
The original supplied passages contain every required literal fact in all 28
answerable cases. Retrieval document/page hits are therefore insufficient to
explain that omission. The old irrelevant selections and incomplete follow-up
handling remain in the retained manual review; the 27/28 diagnostic does not
erase them or prove the answers relevant.

### Remaining evidence-gathering and host problems

- **Missing currency:** the recorded planner uses its three slots for Japan's
  capital, Japan's currency and Australia's capital. Selected original evidence
  does not establish Australia's currency. A future separate query-aware corpus
  must cover all requested fields within the same query/fetch budgets; both
  profiles must receive identical evidence. Original failures remain frozen.
- **Five results:** recorded queries cover 2022–2024. Supplied passages contain
  two complete series tables and game-level/other evidence; they do not establish
  all five requested results. The original automatic rubric is weaker than this
  completeness requirement; do not label its possible pass a complete answer.
- **Complete list:** all 23 required names exist in the original host-selected
  table. The model selects 23 rows, but a 31-word context includes a trusted
  host-generated selection annotation. v11 incorrectly charges that annotation
  against the public prose limit, so no answer renders. Separate authenticated
  host metadata from source quotation costs; page text must never grant itself
  that exemption.
- **Row identity:** the complete-list table begins with an ordinal and blank
  header. Column zero alone does not identify the named subject. v12 conservatively
  requires the first labeled textual field as well, without claiming this proves
  arbitrary subject/property semantics.
- **Latency:** v11 produces no successful grounded answers, so no successful
  answer latency or J7 first-token pass can be claimed. Smaller payload characters
  do not by themselves qualify performance. Buffering still delays validated text.
- **Ordinary chat:** unchanged; its retained 16/20 rubric score and embedded-text
  failures remain blockers. This trial does not claim to improve those answers.

## Test output

- Final `make check`: **434 Python tests**, 39 frontend tests; lint, formatting,
  types, required coverage, 74 contrast pairs, API/additive and motion guards,
  privacy audit pass. Source and raw output are retained in `make-check.log`.
- Focused evidence/citation/stream tests: **64 passed**.
- Initial check failed on a test's `getattr` lint/line length; fixed after the trial
  stopped. Its exact frozen pre-fix test source and failing log remain archived.
  Earlier type errors and their log are retained; final types pass.
- Additional optional eval-file lint retains an **I001 import-style failure** in
  the frozen, executed v11 module. It is kept exactly as executed; no false claim
  that this optional lint command passed. The new prospective schema's lint passes.
- Original coverage evidence restored; the current run's coverage is saved in
  this checkpoint's artifact folder. Original reports and corpus are unchanged.
- No full browser suite rerun: production application and UI source were untouched
  in this checkpoint. The previous checkpoint's full WebKit auto-scroll failure
  and focused fix remain recorded, not relabeled a clean full-suite release.

## Screenshots

None newly captured. No product UI was changed or deployed; all new evidence is
public/synthetic test data. Previous literal-render Chromium/WebKit evidence
remains in the prior checkpoint; it is not claimed as a v12 native result.

## Open questions for Jake / next checkpoint

No installation, package or runtime decision is needed. Next, validate v12's
native schema behavior using a predeclared original-case smoke with automatic
stopping, then run the remaining original cases only if that smoke is valid.
First fix authenticated host-context quotation accounting. Preserve strict ID,
subject/property/time and unsupported-coverage checks; do not reinterpret failed
selections or change the grader to create a pass.

If this contract becomes credible, record a separate query-aware public corpus
and test both profiles on identical evidence. Full semantic, ordinary-chat,
latency, live-provider and regression gates still precede product integration.
Research remains shelved. This checkpoint stops for review without deployment.
