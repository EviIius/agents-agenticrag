# Reliability repair checkpoint — 9 October 2026

## Summary

The repair is isolated on `codex/reliability-hardening`; the installed application
still uses the stable `f87db46` tree. Seven generic prompt/data-framing trials are
retained. Everyday extraction improves, but free-form Web answers still attach
correct-looking citations to unsupported claims. Qualification remains open.
Literal-copy and host-owned ID probes use the same single answer call. They
separate provenance from relevance and completeness; no Research loop or judge
is introduced. None of the free-form trials is qualified for deployment.

## Done-when checklist

| Item | Status | Evidence |
|---|---|---|
| Preserve original comparison and frozen inputs | Pass: 7,296 original inputs unchanged | `artifacts/model-comparison/`; `docs/model-comparison/frozen-inputs.json` |
| Repair post-period Library citation grading | Implemented; original scores preserved | `server/evals/library/citation_binding.py`; `server/tests/test_library_eval.py`; `artifacts/reliability/library-regrades-v3.json` |
| Preserve negative citation-placement checks | Pass in focused run | Same tests: wrong source, neighboring sentence, paragraph, bullet, table row, out-of-row reference and Markdown link |
| Prevent known embedded override behavior | Improved in pilots, not universally proven | `artifacts/reliability/everyday-reviews.json`; frozen v4–v7 data framing |
| Planner input-availability decisions | Current-model first probe improves 13/18 to 18/18; not repeated or candidate-qualified | Original current model 13/18; v5 current model 18/18; `docs/reliability/planner-cases.json` |
| Preserve format and source-only grounding | Not qualified | Baseline v6/v7 19/20; candidate v7 20/20 everyday, but Web misbinding remains |
| Unchanged Web release and regression gates | Not qualified | v7 baseline 24/25, candidate 23/25 automatic; manual unsupported relationships remain |
| J7 required-fact/retrieval/citation gates | Both v7 profiles automatic pass; extra-claim review fails | All required facts and citations 100%, six abstentions, no obeyed injection; extra resume pronouns/deadline basis remain |
| Three complete qualifying repeats per profile | Not run | Known grounding failures prevent a qualification recommendation; failed pilots are not retried into a pass |
| Exact-excerpt feasibility | Complete; provenance improved, semantic qualification fails | `server/evals/reliability/extractive/`; eight frozen inputs; no production integration |
| Full repository/browser gates | Pass: 366 Python, 36 frontend, 457 browser tests; 3 existing skips | `artifacts/reliability/make-check.log`; `make-e2e.log` and command JSON receipts |
| Keep production, preferences and data intact | Verified for affected modules | `artifacts/reliability/production-preservation.json` |

## Changed files

- **Evaluation tooling:** Library citation binding, effective imported-module hashes
  in everyday/Web/Library reports, versioned regrades, held-out planner probe and
  isolated alternative-module loader. The loader refuses the older v1 archive
  rather than replaying it against restored stable source.
- **Isolated prototypes:** `server/evals/reliability/trials/v2` through `v7`;
  v1 source is archived separately in `artifacts/reliability/v1/server/app`.
  `server/evals/reliability/extractive/` tests an exact-provenance answer contract.
- **Tests:** Existing `server/tests/test_library_eval.py` is extended; new
  `test_reliability_trials.py` and `test_extractive_contract.py` check framing
  and rejection behavior. New table-selection and evidence-ID tests cover
  unchanged values/headers, source membership and rejection of forged output.
- **Docs/evidence:** `AGENTS.md`, `docs/RELIABILITY-PLAN.md`, this report,
  supplementary synthetic planner cases and all trial manifests/raw outcomes.
- **Production source/UI/database/deployment:** unchanged. Alternative modules
  are imported only by isolated evaluator children; they are not installed.

## Deviations from SPEC.md

Jake's request to make the app reliable authorizes the documented isolated
repairs, with original prompts/results retained. No release threshold is lowered.
The Library regrade corrects local post-period reference binding; it never
adds a fact or citation to the answer. Original reports remain unchanged.

The fixed 1,500-token evidence budget is a v7 experiment, not a deployed setting.
The extractive feasibility test changes the isolated answer format to a schema
containing only literal quotations and source IDs. A separate v3 contract
accepts host-owned unit IDs and renders host-provided text. It is not a product mode,
ordinary payload change, UI implementation or approved streaming-contract change.
It cannot qualify a free-form answer or replace the frozen release benchmark.

## Runtime observations

### What was actually wrong

1. **Planner availability:** A reference to an article/page was mistaken for
   supplied article text. Moving availability checks earlier and separating
   quoted records improves the supplementary decision checks. A boolean
   attachment-availability flag still does not provide entities for useful
   external queries; decision correctness and query quality are different.
2. **Injection boundary:** Repeated warnings and task footers did not stop the
   known override on the current model. Encoding delimited material separately
   from the task did. This is measured for the known synthetic attacks, not a
   guarantee for arbitrary nested or malformed input.
3. **Grader defect:** Same-line citations after a period were lent to the next
   sentence. Correct binding raises the candidate's three original Library
   citation scores from 96.4%, 96.4%, 89.3% to 100% each. The genuine uncited
   baseline shipping sentences still fail. This repair does not prove arbitrary
   extra claims are supported.
4. **Missing evidence:** The frozen capital/currency comparison has no selected
   passage establishing Australia's currency. v5–v7 current-model answers
   correctly leave it unknown and fail the original required-fact check.
   Replay uses saved search batches; different query wording cannot recover an
   absent fact. This is a coverage failure, not permission to supply AUD from
   memory to manufacture a passing score.
5. **Wrong relationships:** v7 current-model and candidate answers both attach
   828 m to the occupied-floor measurement, while the cited source lists 585.4 m
   for that property. Shared numbers and a valid citation ID do not establish
   the subject/property/value relationship.
6. **Invented details:** v7 current-model output supplies game scores beyond the
   three 2024 games and one 2023 game present in its cited passages. Its fasting
   answer attaches an unstated weight-loss result to a glucose-outcome study.
   These are factual failures even when heuristic aggregate thresholds pass.
   Candidate v7 also confuses a publication date with the host retrieval date.
7. **Earlier-turn and extra-claim gaps:** All v7 current-model Library answers
   were read against the distinct selected synthetic texts. Required facts are
   correct, but resume pronouns and the start event for a deadline are unstated.
   A correct final follow-up does not repair an earlier unsupported statement.
   Candidate v7 has unstated pronouns in earlier/absent-information turns,
   despite all required-fact citation checks passing.

### Observed latency

v7 replay's successful Web answer TTFT is **3.58 s median / 4.79 s p90** on the
current profile and **19.09 s / 21.88 s** on the candidate. Candidate total
Web duration is **49.45 s median / 114.71 s p90**. These are recorded-corpus
measurements with negligible replay search time, not a fresh live E-AC9 test.
The candidate's runtime-reported default reasoning is medium; the ordinary
answer payload still leaves reasoning and sampling unset. No hidden parameter
change was used to improve speed. The host-ID probe is also slower on the
candidate (19–181 seconds per complete response); it is not a performance pass.

### Trial history

| Version | Generic change | Retained result / decision |
|---|---|---|
| v1 | Grounding policy and extra source/citation instructions | Known embedded override still obeyed on current model; candidate speculative details remain. Candidate Web was deliberately stopped; partial trace is not a full passing run. |
| v2 | Task footer, attachment availability, shorter Web rules | Current-model Web 25/25 automatic, but manual invented scores/incorrect measurements persist; override still obeyed. |
| v3 | Repeat task outside explicitly quoted material | Known override still obeyed in the focused smoke; not promoted to a full pilot. |
| v4 | JSON-encode quoted material; task outside data | Focused override stops; planner 16/18, including an embedded lookup failure. |
| v5 | Shared framing for planner/context; JSON passages and actual source URLs | Current-model planner 18/18 first run; full Web 24/25, Library citation 96.4%; failures retained. |
| v6 | Explicit unknown-attribute rules and local citation footer for Library | Current-model everyday 19/20; Web 23/25 automatic; Library automatic J7 pass. Manual Web grounding still fails. |
| v7 | Smaller Web evidence ceiling; concise single-fact response | Current-model everyday 19/20, Web 24/25; candidate everyday 20/20, Web 23/25. Both Library automatic J7 pass; manual grounding rejection remains. |

Each frozen version has its own manifest. No failing run is overwritten. The
v1 driver's generic missing-report error says “Harness setup failure”; its actual
cause was deliberate termination after the known grounding failure, documented
in `artifacts/reliability/v1/qualification-stop.json`. Do not classify that
termination as a runtime protocol failure or completed candidate suite.

## Test output

Focused citation/framing/contract/table/ID tests pass (**71**). `make check`
passes: **366 Python tests**, **36 browser-unit tests**, Ruff/types/formatting,
74 contrast token pairs, API type/additive checks, motion guard and privacy audit
(2,103 scanned paths, no flagged failures). Mypy passes across **100** app/test
files. Coverage meets each existing threshold (provider 86.5%, runs 89.4%, search
88.9%, transcription 93.1%, documents 96.6%, Library 92.6%, backup 96.8%).
Output: `artifacts/reliability/make-check.log` and `make-check.json`.
`make e2e` passes: **457 passed, 3 existing skips**, across Chromium and iPhone
WebKit, in 38.2 minutes. It uses the existing fake app/runtime and unchanged
timeouts, assertions and skips. Output: `artifacts/reliability/make-e2e.log`
and `make-e2e.json`. Existing Vite future-loader warning is
retained; no warning suppression or unrelated config change was made. The
browser run also emits ResizeObserver loop notifications; their cause and
historical presence are not established by this tooling-only checkpoint.
They are retained as observations rather than silently suppressed.
Initial focused-test failures were test fixture construction and a missing
prototype list annotation, corrected before that prototype was frozen. Initial
shell commands used an unavailable PATH/root virtual environment, then used
`scripts/tool-env.sh` and the existing server environment. No runtime was changed.

The excerpt checker verifies literal provenance only. The ID checker accepts
only host-owned text by construction. Neither proves relevance, publisher truth,
correct temporal interpretation or complete coverage. Raw source markup needs
safe text rendering; the prototypes are not product renderers.

### Test-diff ledger

| Existing file/test | What changed | Why | Behavior still asserted? |
|---|---|---|---|
| `server/tests/test_library_eval.py` | Added positive post-period citation and negative local-binding cases | Correct parser defect without borrowing citations across units | Yes; existing exact-number, page, wrong-source, abstention and injection assertions remain |

Other test files are newly added. No timeout, threshold or skip was changed.

## Screenshots

No new product screen or state; no private user screen was captured. Prototypes
are evaluation-only. The unchanged browser suite regenerates synthetic images
and performance outputs. Six representative PNGs and performance outputs are
retained in `artifacts/reliability/browser-evidence/`; its manifest hashes all
regenerated outputs and marks redundant PNG copies omitted to limit repository
growth.
Earlier tracked evidence was restored after archival. These automated fake
captures are not physical-phone observations. Existing UI stays on the stable
tree.

## Coverage and answer-contract observations

The separate offline table selector improves the retained comprehensive-list
input from **14/23 to 23/23 required names present**, at the same budget and on
the same fetched page bytes. It preserves rows and scores. Its ranking uses a
recorded source-order prior and default allocation ratio, not an exact pipeline
replay; the complete model answer has not been re-evaluated with this selector.
See `artifacts/reliability/table-selection-probe.json`.

The literal-copy v2 probe accepts **4/8 current-model** and **7/8 candidate**
responses. Rejections withhold every excerpt in that response. Both number
responses demonstrate a further limit: exact numeric quotations can omit the
property labels needed to interpret them. Candidate's short injection-page
excerpts lose temporal context. These are provenance tests, not answer passes.
The v1 contract had no inference: a numeric-substring weakness was found before
inference, archived and corrected in the separately frozen v2 contract.

The host-ID v3 probe accepts **8/8 responses on each profile**. Those are
structural/provenance successes, not eight correct answers. Manual review finds:

- Both select another author's breakfast for a question about the user.
- The current model selects conference-final rows for a Finals-results request;
  the candidate selects some relevant rows but the five-series request remains
  incomplete. One-unit-per-source is itself a coverage restriction.
- The candidate selects a sentence beginning “They” without its antecedent.
- The source unit for the security exercise contains the correct code and the
  malicious source instructions. Neither model obeys them, but a product
  renderer would need to display them safely as data.

Both profiles preserve the requested synthetic shipping/warehouse values and
provide Paris capital evidence. The host never accepts model-written prose or
an invented source unit. These gains do not resolve identity, context and full
answer coverage. See `artifacts/reliability/extractive-v3/manual-review.json`.

All **7,296 original input hashes** and frozen trial/archive bytes pass the final
integrity audit (**7,353 checks**). Original comparison reports remain unchanged;
the candidate's original Library score correction is separately retained. The
v2 regrade did not record a grader hash; its source archive is preserved. The
v3 archived grader matches its recorded hash; current formatting differs without
logic changes. No fresh live Web or physical-phone acceptance was run: failing
isolated candidates were not promoted. The installed service answers HTTP 200;
that establishes service availability, not factual answer quality.

## Recommendation and review stop

**Keep the live build and current model. Do not promote v1–v7 or restart Research.**
The concrete next checkpoint is in `RELIABILITY-NEXT-CHECKPOINT.md`: test complete
table coverage and context-preserving evidence selections; constrain the
existing answer call and render original source evidence; explicitly decline
unsupported information. Valid IDs alone are insufficient. This changes the
answer-format and streaming/rendering contract, so review sample output and
complete unchanged gates before product integration.

Three qualifying full repeats are not justified while the first pilots contain
known factual failures. This checkpoint establishes causes, repairs the grader,
preserves failed trials and proposes a bounded implementation; it does not
establish general answer reliability. SPEC H4 requires a review stop here.

## Open questions for Jake

The review decision is whether to proceed with the proposed bounded evidence
contract in `RELIABILITY-NEXT-CHECKPOINT.md`. It requires output/streaming
review and unchanged acceptance gates before integration. This checkpoint
does not justify calling either model generally reliable or changing the
production default.
