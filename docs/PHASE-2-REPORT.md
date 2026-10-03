# Phase 2 report

## Summary

The numeric-list accuracy fix and authorized temperature comparison are implemented and evaluated.
The final 25-case recorded-web run passes 24/25; fresh live NBA research and the 32K Qwen replay return all 23 qualifying entries with a citation on every row.
Native answer sampling is retained: the controlled temperature-0.2 run performs worse.
**Phase 2 remains open:** one release-source coverage case fails, and the latest browser suite has two phone layout failures. Jake deferred iPhone work until these two tasks were finished; Phase 3 is held.

## Done-when checklist

| Item | Status | Evidence |
|---|---|---|
| E-AC1: cited 2021 result, loser/opponent/4–2 | Passed final recorded run | `001904`; equivalent 4-win/2-win tables accepted, wrong counts rejected |
| E-AC2: thanks skips search | Passed final recorded run and covered browser path | `001904`, real utility planner, no search |
| E-AC3: standalone follow-up | Passed final recorded run | `001904`, `nba-followup` |
| E-AC4: immediate activity/favicon/collapse | Passed covered browser paths | `e2e-selection-production.txt`, `activity-latency-*.json` |
| E-AC5: exact citation evidence/source panel | Passed storage/interaction checks | Bound host citation cells persist as the actual model input; full cached page remains unchanged. Citation validity does not establish truth |
| E-AC6: fallback/all failed | Passed covered paths | Free Ollama → SearXNG → Exa → DDG; earlier real outage reached Exa in 904 ms; current unit/browser failure paths |
| E-AC7: SSRF | Passed | Private DNS, redirects, downgrade, ports, Unicode and payload/credential URL tests |
| E-AC8: offline targets/ranking comparison | Aggregate and named-example gates pass; one individual coverage case open | Final `001904`: 24/25, required facts 100%, valid citations 100%, no forbidden/uncited cases. `ollama-latest` has one distinct cited source where its case requires two. Earlier keyword/hybrid comparison retained below |
| E-AC9: live TTFT P50 ≤12 s | Earlier full live measurement passes; final targeted live passes | Earlier `160515` P50 6.39 s/P90 10.20 s; final live NBA `001926` TTFT 10.47 s. No new full 25-case live run on the final formatter |
| E-AC10: controlled injection | Passed final recorded run | `001904` receives controlled attack and ignores it; live pages do not substitute for this test |
| Comprehensive NBA losses | Passed final recorded, live and 32K Qwen checks | `001904`, `001926`, `001943`: all 23 qualifying entries, no excluded teams, per-row references, no false “all 28” conclusion |
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

The generic E4/E7 refinement uses a nullable condition inside the existing planner call. Its property is constrained to literal request words, and the host applies it only to supported unambiguous numeric columns. Matching table rows include host citation labels, while unfiltered prose from that selected-table source is omitted from the answer evidence to avoid population-total confusion. Full raw pages remain cached. E8's V6 answer system prompt and answer sampling defaults are unchanged; source wrapper metadata now explicitly identifies `[N]`.

No additional dependency, agent, mode or model call was introduced. Existing source/token/per-source passage budgets remain. No legacy-data writes, port/bind, launchd label or Tailscale changes.

## Runtime observations

### Accuracy diagnosis and final fix

The evidence contained a complete 28-row table: 23 positive loss counts and five missing markers. Earlier answers converted missing markers into losses, omitted final entries, confused numeric columns, copied a full-population total into a subset conclusion, or omitted inline references. Table formatting and lower temperature alone did not fix this. Related prose could also displace the direct data.

The planner now names the literal qualifying property from the request within its existing JSON response. The host requires one matching numeric column and the stated comparison; unsupported/ambiguous conditions preserve the evidence. Missing values never become zero. Generic grammatical normalization binds action words to their numeric nouns. Occurrence selection requires nonnegative integer counts; unsupported units, compound thresholds and malformed values decline selection.

Verified selected tables take priority within the original budgets. Their unfiltered attached prose and other prose from the same source are withheld from the answer context. Each selected row retains its values and gains a host reference cell, bound after source numbering. The model receives and cites these exact passages; the UI is not adding citations after generation. Other sources remain available. This is a targeted numeric-list fix, not universal factual verification.

| Final native-default run | Outcome | Evidence |
|---|---|---|
| [25-case recorded web, `001904`](../server/evals/web/reports/2026-10-03-001904-qwen3-30b-a3b-instruct-2507-q4_K_M-offline-keyword.md) | 24/25; required facts 100%; valid citations 100%; no forbidden or uncited output; support 0.9613; recorded-web TTFT P50 3.90/P90 6.10 s | All aggregate E12 and required E13 example gates pass. One release case needs another distinct source |
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

[Workbench development preview](https://jakes-mac-mini.tailc4d343.ts.net/) uses the rebuilt backend/UI at unchanged 127.0.0.1:8787. [Final preview health](../artifacts/phase-2/selection-preview-health.json) verifies local/HTTPS health, exactly five approved models and the standard Qwen warmed at 16K. The saved search key remains write-only. Installed-package deployment and legacy read-only import are Phase 3 work; the preview exit trap restores the existing launchd job.

Public page recordings are lossless gzip with SHA-256 manifests and decompression equality checks. [Compression evidence](../artifacts/phase-2/selection-fixture-compression.json) covers this investigation's four new live fixture roots. Reports and fixtures are not loaded during normal chat and do not add inference latency.

## Test output

- [Final `make check`](../artifacts/phase-2/check-selection-final.txt): **180 Python tests**, **36 Vitest tests**, lint/format, strict types, generated API contract and **56 contrast pairs** pass. Search coverage 87.7%.
- [Focused accuracy tests](../artifacts/phase-2/accuracy-selection-tests.txt): **101 passed** before the last additional grading assertion; final full check includes it.
- [Latest full browser suite](../artifacts/phase-2/e2e-selection-production.txt): **106 passed, 2 failed, 2 skipped**. Both 390 px Chromium review-screen tests fail keyboard/thread bounds (light/dark). This is not a passing UI gate; Jake deferred its repair.
- [Final build](../artifacts/phase-2/build-selection-final.txt): passes. Markdown lazy chunk remains 938.90 kB raw / 287.94 kB gzip; the Phase 3 bundle budget is still open.
- [Real parameter/chat action evidence](../artifacts/phase-2/live-controls.json) remains available. Explicit answer parameters forward; omitted defaults are not sent.
- [Credential check](../artifacts/phase-2/credential-leak-check-selection.json): scans changed/new source and artifacts, including decompressed recordings, without logging the saved key.
- Full evals report their failing case even when aggregate targets pass. The remaining release source-count assertion was not weakened.

## Screenshots

Visually inspected against the actual preview; safe-area/keyboard dimensions are simulated:

- [Phone settings](../artifacts/phase-2/settings-safe-390-live.png) and [reachable Save/footer](../artifacts/phase-2/settings-safe-footer-390-live.png).
- [Phone sidebar](../artifacts/phase-2/phone-safe-sidebar-live.png), [model picker](../artifacts/phase-2/model-safe-390-live.png) and [keyboard picker](../artifacts/phase-2/model-keyboard-safe-live.png).
- [Desktop settings](../artifacts/phase-2/settings-safe-1440-live.png) and [model picker](../artifacts/phase-2/model-safe-1440-live.png).
- Real model filtering: [phone](../artifacts/phase-2/model-search-390-live.png), [desktop](../artifacts/phase-2/model-search-1440-live.png).
- Browser fixtures explicitly labelled fake: `web-chat-{390,1440}-{light,dark}-fake-web.png`, `citation-card-…`, `sources-…`, and `panel-safe-{320,390,768,1440}-fake-runtime.png`. These prove interaction/layout, not model accuracy.

## Open questions for Jake

No key, paid search subscription or Docker approval is needed. Native temperature is retained after the authorized comparison. The two requested backend/evaluation tasks are finished; Phase 2 still needs the release-source coverage case and deferred iPhone keyboard/panel repair plus physical confirmation before Phase 3.
