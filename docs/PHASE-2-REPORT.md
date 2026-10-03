# Phase 2 report

## Summary

The numeric-list accuracy fix and authorized temperature comparison are implemented and evaluated.
The final evaluation closeout is recorded below, after release coverage, section/row selection, citation binding and follow-up fixes. Original questions, case hashes and failing runs remain preserved; two benchmark requests now explicitly ask for the fields/source type their assertions require.
Native answer sampling is retained: the controlled temperature-0.2 run performs worse.
**Phase 2 remains open for mobile review:** the latest browser suite has two phone layout failures. Jake requested release/evaluation closeout first and will provide phone screenshots in a separate design task. No mobile layout work or Phase 3 implementation is part of this closeout.

## Done-when checklist

| Item | Status | Evidence |
|---|---|---|
| E-AC1: cited 2021 result, loser/opponent/4–2 | Passed latest full recorded run | `032410`; explicit winner/loser/series-score request, correct values and valid citations |
| E-AC2: thanks skips search | Passed latest full recorded run and covered browser path | `032410`, real utility planner, no search |
| E-AC3: standalone follow-up | Passed latest full recorded run | `032410`, `nba-followup` resolves the prior year correctly |
| E-AC4: immediate activity/favicon/collapse | Passed covered browser paths | `e2e-selection-production.txt`, `activity-latency-*.json` |
| E-AC5: exact citation evidence/source panel | Passed storage/interaction checks | Bound host citation cells persist as the actual model input; full cached page remains unchanged. Citation validity does not establish truth |
| E-AC6: fallback/all failed | Passed covered paths | Free Ollama → SearXNG → Exa → DDG; earlier real outage reached Exa in 904 ms; current unit/browser failure paths |
| E-AC7: SSRF | Passed | Private DNS, redirects, downgrade, ports, Unicode and payload/credential URL tests |
| E-AC8: offline targets/ranking comparison | Passed latest full recorded suite | `032410`: 24/25, required facts 96%, valid citations 100%, no forbidden/uncited cases, support 0.8853. Release coverage passes. Earlier keyword/hybrid comparison retained below |
| E-AC9: live TTFT P50 ≤12 s | Passed full live measurement | `032719`: P50 **5.96 s**, P90 **7.52 s**, 22/22 searched turns have evidence. Full run precedes the final official-index discovery fix; its affected case passes separately in `032822` at 6.16 s |
| E-AC10: controlled injection | Passed latest full recorded run | `032410` receives the controlled attack and ignores it; live pages do not substitute for this test |
| Comprehensive NBA losses | Passed latest full recorded run; final live pending | `032410`: all 23 qualifying entries, per-row references, no excluded teams or false 28-total. Earlier 32K checkpoint `001943` retained |
| Sampling and chat actions | Passed covered paths | Isolated real API/native payload evidence and browser rename/pin/export/delete/persistence; unset answer parameters omitted |
| Phone/desktop layout | **Open; iPhone work deferred** | Latest Chromium/WebKit suite: 106 pass, 2 fail, 2 skip. Both failures are 390 px Chromium keyboard/thread bounds in light/dark themes |
| Five approved models | Available; full accuracy not established for all five | Final formatter checked on Qwen 16K/32K. Intermediate selection smokes pass Gemma/GPT-OSS/16K Llama; these are not five final full suites |

## Changed files

- **Server:** `search/planner.py` adds an optional literal-word condition to the existing single planner call; `selection.py` conservatively binds a numeric column and selects matching rows; `pipeline.py` gives verified evidence priority and binds its row references; `prompt.py` labels source citations in host metadata; `schemas.py` records the condition and trusted selection flag.
- **Web:** generated `api-types.ts` and the `/design` source fixture reflect the added fields. No new iPhone layout changes in this work.
- **Tests:** `test_search.py`, `test_web_evidence.py`, `test_web_grading.py` cover immutable per-request schemas, ambiguous/unknown numeric data, row/cell preservation, source persistence, forged host annotations, citation binding and stricter list checks.
- **Evals/docs:** `cases.yaml`, `grading.py`, `run_eval.py`, trial helpers, SPEC E4/E7/E8 and this report retain before/after answers, exact prompt/code hashes, failed trials, public fixtures and the isolated temperature comparison.
- **Earlier Phase 2 changes retained:** table assembly/chunking, heading/plural/bibliography ranking, recent-page reuse, free search adapters, sampling/chat actions, phone safe areas/switches/picker filtering and terminal SSE persistence. See the historical test/evaluation artifacts for those changes.

## Deviations from SPEC.md

User-approved scope: Ollama only; five stored picker preferences; free providers; continue Phase 3 after Phase 2 validation; isolate temperature tests; defer current iPhone work.

The generic E4/E7 refinement uses a nullable condition inside the existing planner call. Its property is constrained to literal request words, and the host applies it only to supported unambiguous numeric columns. Matching table rows include host citation labels, while unfiltered prose from that selected-table source is omitted from the answer evidence to avoid population-total confusion. Full raw pages remain cached. At the numeric-list checkpoint, E8's V6 answer system prompt and answer sampling defaults were unchanged; the closeout adds generic supported-outcome/table-values and planner source-constraint instructions described below. Native answer sampling remains unchanged; source wrapper metadata now explicitly identifies `[N]`.

No additional dependency, agent, mode or model call was introduced. Existing source/token/per-source passage budgets remain. No legacy-data writes, port/bind, launchd label or Tailscale changes.

## Runtime observations

### Evaluation closeout — 3 October UTC (2 October on the Mac)

Jake authorized the first two closeout items and deferred the third to a separate mobile design task. The two-source release requirement was not justified by the request: a single official note can establish version and changes. The old test also did not assert either detail. The corrected test requires a cited version, cited change assertions and a cited official release URL; one unsupported or missing claim fails it. Plain colon-ended labels are not factual assertions. Two-source requirements remain for actual comparison/contested cases. Regex/provenance checks still require manual claim review, not just a green score.

Inspection found a real production defect as well: headings such as the entry/version were replaced by the next generic “Changes” heading, and separate entries with identical subheadings merged into one passage. The host now preserves consecutive heading labels, respects every section boundary during merging, and sends escaped section context beside each passage. Raw page/cache and passage bodies remain unchanged. No topic-specific instruction, extra call, new dependency or temperature override was added.

[Release review](../artifacts/phase-2/closeout-release-review.json) compares the old mixed-version answer (`001904`) with the corrected answer (`010755`): it identifies the version from the leading official section and describes only that section's four changes, with references. The first closeout grading attempt (`010700`) rejected an uncited colon-ended label; that grader defect was corrected with a regression test, and its original report is preserved.

[Initial recorded-web closeout `011012`](../server/evals/web/reports/2026-10-03-011012-qwen3-30b-a3b-instruct-2507-q4_K_M-offline-keyword.md): **25/25**, real planner/answer and frozen public inputs; required facts/decisions/citation validity 100%, no forbidden or uncited output, support 0.9660; web TTFT P50 **4.03 s**, P90 **6.21 s**. Controlled injection is exercised and ignored. Old reports/case hashes are unchanged; the case correction means this is not a score-only A/B with `001904`.


### Failures found by the full live closeout and their fixes

The first full live closeout `011356` passes 22/25 but fails the mandatory list/score examples and release provenance. These failures prevent treating the earlier 25/25 replay as sufficient. Its saved public corpus supports diagnosis without changing web input while refining selection:

- Strip isolated edit navigation markers and recognize headings even without a blank line; keep heading context and section boundaries.
- Bind an abbreviated W/L column only with its explicit local wins-and-losses definition and the same heading/header. Copy the definition so series counts are not described as individual-game losses. An undefined or different-section table remains uninterpreted.
- Reassemble selected rows before final chunking, preserve identity/numeric/reference fields, and identify any omitted long prose column. The full original page stays cached. Verified numeric-list evidence uses scoped tables, with other fetched pages recorded as unused, preventing older background from competing with direct rows.
- Apply a bounded relevant lead/compact-table prior within the original caps. Zero-match passages remain unboosted; reference requests retain their bibliography behavior. Keyword remains the default.
- **Fix citation binding order:** sanitize tags before assigning source numbers, rather than overwriting the bound table with the original `[pending]` cells. The integration test now requires actual numbered cells in persisted evidence and the answer request.
- Include planner queries as retrieval context, explicitly not additional user requirements. This preserves the resolved year/entity for short follow-ups within the same answer call.

The repaired list in `012517` has all 23 entries, row citations and the correct series unit. The bound-reference/resolved-query full replay `013543` still fails the implicit score requirement, so the final answer instructions add the generic supported-outcome/table-values guidance, with before/after evidence `013543` versus `013800`. No topic-specific instruction or extra model call was added. A short overlap between the targeted score test and the preceding diagnostic live run means `013855` is not used as the final isolated latency qualification.

**Request/assertion alignment:** the literal “Who lost …? Show a table” admits a correct one-team table; the old release question did not request an official source. The benchmark requests now explicitly ask for winner/loser/final series score and official release notes. Required facts, score checks, citation coverage and official provenance remain intact. This clarification is recorded in SPEC E12/E13; old scores/questions are not rewritten or compared as an unchanged-dataset A/B. The release coverage grader also handles plural/singular change words and a cited fact followed by a colon-ended label on the same line. Separate regression tests cover both.

### Source-type preservation and rejected prompt trial

The clarified recorded run `015047` passes 24/25 and all E12/E13 gates, with the personal-breakfast question failing its refusal check. The clarified live run `015414` passes 24/25 and the mandatory examples, but **fails release provenance**: it cites mirrors rather than the explicitly requested official notes. A green aggregate does not close that requirement. The planner omitted the source qualifier from its queries.

A general planner source-constraint prompt trial is **rejected**: `015926` recorded / `020252` live regress the comprehensive list because the optional condition becomes null; the live answer again includes nonmatching teams. Both full results remain attached. Release coverage passes that trial, but manual review finds older release changes mixed into the answer, demonstrating why citation/provenance regexes are not factual entailment. The trial also invents a version in a query. Do not use those runs as completion evidence.

The retained fix preserves literal positively requested official/primary source qualifiers in host queries, with no inferred publisher, new query, prompt change, temperature change or model call. Unit checks cover duplicates, negative directives, incidental uses of “official”, and the existing 120-character query limit. The previously evaluated planner prompt is restored. Final validation is indexed below.

### Official-index discovery

The host qualifier alone is insufficient for the live release requirement: full `032719` still cites mirrors despite preserving “official”. Its 24/25 score and aggregate gates are reported, but **release coverage fails**. A same-query [SearXNG date-filter comparison](../artifacts/phase-2/closeout-date-filter-comparison.json) establishes a concrete retrieval cause: with `time_range=week`, the official continuously updated index is absent; without a publication-date filter, it ranks first. For positively requested official/primary sources only, the pipeline discovers pages without that filter, preserving the plan freshness for page-cache reads. Tests prove ordinary searches retain their filter and both paths retain page freshness. No additional search or model call is added. The affected release case is validated separately on the final pipeline; unaffected full-suite results remain identified as pre-fix, rather than recomputed or relabelled.

### Closeout decision and final evidence

**Ready for the separate iPhone UI review. Evaluation closeout items 1 and 2 are sufficiently verified; whole Phase 2 and Phase 3 remain open for the UI gates.** Native answer sampling remains unchanged. This is a bounded acceptance decision, not a claim of perfect accuracy or five-model full-suite coverage.

| Evidence | Result | Scope |
|---|---|---|
| [Recorded full suite `032410`](../server/evals/web/reports/2026-10-03-032410-qwen3-30b-a3b-instruct-2507-q4_K_M-offline-keyword.md) | **24/25**; decisions 100%, required facts 96%, valid citations 100%, zero forbidden/uncited cases, lexical support **0.8853**; controlled injection received/ignored | All E12 aggregate/E13 mandatory gates pass. Personal-history case fails strict refusal despite stating the user's breakfast is unknown and then adding irrelevant examples. Precedes the final date-filter policy change |
| [Live full suite `032719`](../server/evals/web/reports/2026-10-03-032719-qwen3-30b-a3b-instruct-2507-q4_K_M-live-keyword.md) | **24/25**; decisions/required facts/citation validity 100%, zero forbidden/uncited cases, support **0.9254**, **22/22** searched turns with evidence; web TTFT **5.96 / 7.52 s P50/P90** | Mandatory score/follow-up/complete-list examples pass; official release provenance fails before the final discovery fix. This report is not relabelled as a final 25/25 run |
| [Final affected release case `032822`](../server/evals/web/reports/2026-10-03-032822-qwen3-30b-a3b-instruct-2507-q4_K_M-live-keyword.md) | **1/1**, official provenance/cited version/change coverage passes; support **0.975**, TTFT **6.16 s** | Final pipeline; discovery is unfiltered only for positively requested official/primary sources. Regression tests prove ordinary requests and page freshness retain their behavior |

Manual review confirms the final release version and listed changes match the selected official notes. **The added publication date is not independently verified:** the answer takes October 2 from a mirror, while the GitHub page metadata is September 29 and does not establish that individual release's date. Citation support is lexical, not entailment; metadata/date attribution and irrelevant personal-history examples remain accuracy limitations. The final date-filter fix is checked on its affected case with unit coverage for both branches; unaffected full-suite observations remain explicitly pre-fix. No blended 25/25 score or final-code full suite is claimed. [Machine-readable closeout summary](../artifacts/phase-2/closeout-summary.json) retains hashes, scope and limitations.

The recorded/live inputs differ, and two benchmark requests were clarified earlier; scores are not an unchanged-dataset controlled A/B. Native versus 0.2 temperature evidence below remains one authorized comparison, with native retained. Further open-ended temperature tuning is not needed to start the UI review.

### Numeric-list checkpoint before the evaluation closeout

The evidence contained a complete 28-row table: 23 positive loss counts and five missing markers. Earlier answers converted missing markers into losses, omitted final entries, confused numeric columns, copied a full-population total into a subset conclusion, or omitted inline references. Table formatting and lower temperature alone did not fix this. Related prose could also displace the direct data.

The planner now names the literal qualifying property from the request within its existing JSON response. The host requires one matching numeric column and the stated comparison; unsupported/ambiguous conditions preserve the evidence. Missing values never become zero. Generic grammatical normalization binds action words to their numeric nouns. Occurrence selection requires nonnegative integer counts; unsupported units, compound thresholds and malformed values decline selection.

Verified selected tables take priority within the original budgets. Their unfiltered attached prose and other prose from the same source are withheld from the answer context. Each selected row retains its values and gains a host reference cell, bound after source numbering. The model receives and cites these exact passages; the UI is not adding citations after generation. Other sources remain available. This is a targeted numeric-list fix, not universal factual verification.

| Earlier native-default checkpoint | Outcome | Evidence |
|---|---|---|
| [25-case recorded web, `001904`](../server/evals/web/reports/2026-10-03-001904-qwen3-30b-a3b-instruct-2507-q4_K_M-offline-keyword.md) | 24/25; required facts 100%; valid citations 100%; no forbidden or uncited output; support 0.9613; recorded-web TTFT P50 3.90/P90 6.10 s | All aggregate E12 and required E13 example gates pass. The release case uses the earlier arbitrary two-source requirement |
| [Fresh live NBA, `001926`](../server/evals/web/reports/2026-10-03-001926-qwen3-30b-a3b-instruct-2507-q4_K_M-live-keyword.md) | 1/1; 23 matching entries, every row cited; no false 28-total; support 1.0; TTFT 10.47 s, total 20.28 s | Real search, pages, planner and answer |
| [Qwen 32K NBA replay, `001943`](../server/evals/web/reports/2026-10-03-001943-qwen3-30b-a3b-workbench-32k-offline-keyword.md) | 1/1; 23 entries and per-row citations; support 1.0; TTFT 8.97 s, total 15.68 s | Actual completion context 32768 |

UTC report dates roll to October 3; the Mac's local work date remains October 2. Recorded web freezes public results/pages, not model output. The full final suite runs a fresh real planner; temperature comparison plans are frozen separately.

**Stronger grading:** comprehensive lists now need a reference on every Markdown list/table item, and the regression rejects false “all 28” conclusions. Earlier runs with a cited introduction could pass the old grader despite uncited rows. [The saved-answer audit](../artifacts/phase-2/strict-list-citation-audit.json) documents these failures without rewriting old reports. Exact hashes in each new report identify its planner, answer builder, pipeline and selection implementation. Lexical support is not entailment and does not prove every numeric, date or explanatory claim.

### Before/after and failed trials

- [Pre-selection baseline `190310`](../server/evals/web/reports/2026-10-02-190310-qwen3-30b-a3b-instruct-2507-q4_K_M-offline-keyword.md) supplies all rows but includes nonmatching teams. The earlier heading and delimiter repairs fail this accuracy gate.
- Row-record, null-label, query-position and prompt-only trials fail; they remain evaluator-only. A human-provided predicate proof `230450` shows that a selected table can work but is explicitly not an automatic production result.
- Automatic literal-word candidates `233347`, `233642`, `233704`, `233725` establish the condition approach. Early production `234311`/live `234345` still fail citations or scope. Priority/labels improve the same live corpus in `234643`.
- Intermediate source-citation-label live `000040` has uncited rows and a false 28-total despite its old score. Final scoped tables/row references and stronger grading address those errors in `001904`, `001926`, `001943`.
- Gemma `235306`, GPT-OSS `235335`, 16K Llama `235605` pass intermediate NBA selection smokes (TTFT 11.41/7.25/77.32 s respectively). Their final scoped formatter/full-suite accuracy remains untested. The earlier 32K citation failure `235057` is repaired in final `001943`.

### Authorized temperature comparison

| Controlled 25-case run | Cases passed | Required facts | Valid citations | Web TTFT P50 / P90 |
|---|---:|---:|---:|---:|
| [Native defaults, `222041`](../server/evals/web/reports/2026-10-02-222041-qwen3-30b-a3b-instruct-2507-q4_K_M-offline-keyword.md) | 24/25 | 96% | 100% | 2.81 / 5.04 s |
| [Explicit temperature 0.2, `222231`](../server/evals/web/reports/2026-10-02-222231-qwen3-30b-a3b-instruct-2507-q4_K_M-offline-keyword-temperature-0p2.md) | 21/25 | 88% | 100% | 2.76 / 5.19 s |

[Comparison data](../artifacts/phase-2/temperature-comparison.json) records changed cases, observed answer parameters and limitations. Plans and public web inputs are frozen to isolate answer sampling; these decision scores do not measure fresh planning. One run per setting is insufficient to establish statistical significance. Native sampling is retained. The temperature-0.2 full run omits the essential 4–2 detail, release citation coverage and three qualifying list entries. Its unanswerable response says the fact is not established, but misses the existing refusal regex; original scores remain unchanged. Native output also contains an unsupported closing exclusion claim despite passing the list-name checks. Neither a lexical support score nor a passing aggregate run proves every claim.

The harness now creates a chat through the supported API and PATCHes its explicitly requested temperature, instead of attempting an unsupported create field. It checks completion stats for the value. These test chats use isolated temporary storage; no user chat or model preference changes.

### Ranking and historical live evidence

**Default remains keyword.** Earlier same-corpus keyword `155158` passes 22/25 with TTFT P50 3.99/P90 5.69 s; functioning hybrid `155637` passes 21/25 with P50 6.74/P90 11.82 s, including embeddings on all 22 searched turns. Independent planners limit exact attribution. Frozen-plan `135951` versus `140319` also favors keyword latency (3.02 versus 5.94 s P50). These original failures remain recorded; hybrid was not rerun with the final formatter.

Earlier full live `160515` passes 23/25 under its then-current assertions; the original V6 replay `144854` passes 25/25 but subsequent runs expose numeric-list failures. The six everyday-question smoke checks `142011` pass basic checks with support only 0.693, so they do not validate every recommendation or weather claim. These historical results are not substituted for final-code validation.

### Preview and storage

[Workbench development preview](https://jakes-mac-mini.tailc4d343.ts.net/) uses the rebuilt backend/UI at unchanged 127.0.0.1:8787. [Evaluation-closeout preview health](../artifacts/phase-2/closeout-preview-health.json) verifies local/HTTPS health, exactly five approved models and the standard Qwen warmed at 16K. The saved search key remains write-only. Installed-package deployment and legacy read-only import are Phase 3 work; the preview exit trap restores the existing launchd job.

Public page recordings are lossless gzip with SHA-256 manifests and decompression equality checks. [Closeout compression evidence](../artifacts/phase-2/closeout-fixture-compression.json) covers the additional live fixture roots, including rejected trials. Reports and fixtures are not loaded during normal chat and do not add inference latency.

## Test output

- [Final closeout `make check`](../artifacts/phase-2/closeout-official-index-check.txt): **187 Python tests**, **36 Vitest tests**, lint/format, strict types, generated API contract and **56 contrast pairs** pass. Search coverage **88.9%**.

- [Closeout `make check`](../artifacts/phase-2/closeout-check.txt): **182 Python tests**, **36 Vitest tests**, lint/format, strict types, generated API contract and **56 contrast pairs** pass. Search coverage 87.8%. The two new tests cover distinct section boundaries/context and cited official version/change coverage.
- [Numeric-list checkpoint `make check`](../artifacts/phase-2/check-selection-final.txt): **180 Python tests**, **36 Vitest tests**, lint/format, strict types, generated API contract and **56 contrast pairs** pass. Search coverage 87.7%.
- [Focused accuracy tests](../artifacts/phase-2/accuracy-selection-tests.txt): **101 passed** before the last additional grading assertion; final full check includes it.
- [Latest full browser suite](../artifacts/phase-2/e2e-selection-production.txt): **106 passed, 2 failed, 2 skipped**. Both 390 px Chromium review-screen tests fail keyboard/thread bounds (light/dark). This is not a passing UI gate; Jake deferred its repair.
- [Final build](../artifacts/phase-2/build-selection-final.txt): passes. Markdown lazy chunk remains 938.90 kB raw / 287.94 kB gzip; the Phase 3 bundle budget is still open.
- [Real parameter/chat action evidence](../artifacts/phase-2/live-controls.json) remains available. Explicit answer parameters forward; omitted defaults are not sent.
- [Final credential check](../artifacts/phase-2/closeout-credential-check.json): scans changed/new source and artifacts, including decompressed recordings, without logging the saved key.
- Full evals report their failing case even when aggregate targets pass. The release assertion was explicitly corrected for official-source coverage rather than source diversity; historical failures remain recorded.

## Screenshots

Visually inspected against the actual preview; safe-area/keyboard dimensions are simulated:

- [Phone settings](../artifacts/phase-2/settings-safe-390-live.png) and [reachable Save/footer](../artifacts/phase-2/settings-safe-footer-390-live.png).
- [Phone sidebar](../artifacts/phase-2/phone-safe-sidebar-live.png), [model picker](../artifacts/phase-2/model-safe-390-live.png) and [keyboard picker](../artifacts/phase-2/model-keyboard-safe-live.png).
- [Desktop settings](../artifacts/phase-2/settings-safe-1440-live.png) and [model picker](../artifacts/phase-2/model-safe-1440-live.png).
- Real model filtering: [phone](../artifacts/phase-2/model-search-390-live.png), [desktop](../artifacts/phase-2/model-search-1440-live.png).
- Browser fixtures explicitly labelled fake: `web-chat-{390,1440}-{light,dark}-fake-web.png`, `citation-card-…`, `sources-…`, and `panel-safe-{320,390,768,1440}-fake-runtime.png`. These prove interaction/layout, not model accuracy.

## Open questions for Jake

No key, paid search subscription or Docker approval is needed. Native temperature is retained after the authorized comparison. Release-source coverage and full live validation are documented above, including preserved failures and request/assertion alignment. Evaluation closeout is ready for the deferred iPhone keyboard/panel review, repair and physical confirmation in Jake’s separate task. The two known browser layout failures still prevent marking whole Phase 2 complete or beginning Phase 3. Date attribution and personal-history output limitations remain documented, without claiming perfect factual accuracy.
