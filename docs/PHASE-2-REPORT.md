# Phase 2 report

## Summary

Implemented the bounded plan → search → fetch → rank → answer pipeline, exact stored citation passages, compact search controls and source cards/drawers.
There are no library retrieval calls, research loops or extra claim-checking model calls in the new chat path.
SSRF, Unicode URLs, source persistence, provider fallback, citation normalization and browser interactions are covered.
The real 25-case baseline exposed provider rate limiting and incorrect planner scope; the report does not count fallback chat as working web search.
**Phase 2 is not complete: live provider setup and accuracy/retrieval gates still fail.**

## Done-when checklist

| Item | Status | Evidence |
|---|---|---|
| E-AC1: correct cited NBA 2021 result | Not consistently passed | Real baseline sometimes omits the required series score/citations; fake browser result is not model-accuracy evidence |
| E-AC2: thanks skips search | Passed automated path | Pipeline unit request log and Chromium/WebKit follow-up checks |
| E-AC3: standalone follow-up | Planner path implemented; live grounded answer pending | Full history is supplied to the planner; provider failures prevented complete live source coverage |
| E-AC4: immediate activity/favicons/collapse | Implemented; dedicated latency assertion pending | Planning event emitted before metadata work; successful-page favicons; live/done states and browser interaction checks |
| E-AC5: citation cards/exact passages | Passed browser and unit checks | Both engines, phone/desktop, themes; source card and drawer, reload, exact passage display; 28 shared normalization vectors |
| E-AC6: SearXNG→DDG and all-provider failure | Unit passed; real SearXNG pending | Provider respx/fallback tests and normal-answer failure tests; local container has not been started |
| E-AC7: SSRF | Passed | Public-address/all-DNS checks, private redirects, HTTP downgrade, non-443 ports, credentials, Unicode path, compressed-size bounds |
| E-AC8: eval targets + ranking A/B | Failed/pending | Baseline planner 24/27 = 88.9% (<90%); sparse fixture coverage prevents reliable A/B conclusions. Trial reports are not production acceptance |
| E-AC9: live P50 ≤12s | Insufficient source coverage | Successful searches: P50 6.67s, P90 8.93s, only 3 successful web turns; 21 searched turns failed. Full-set live gate remains pending |
| E-AC10: injection ignored | Passed controlled real-model test | `2026-10-01-151103-…-offline-keyword` report: selected passage contains PWNED attack; Qwen response does not. This is a synthetic adversarial fixture, not a live-provider test |
| G5 web screens/Axe | Passed tested states | Phone/desktop themes, citation card and sources panel; no serious/critical Axe findings |

## Changed files

- Server: `search/{fetch,extract,chunk,providers,merge,rank,cache,planner,prompt,citations,pipeline,fixtures}.py`; search/status/favicon APIs; generation hook and source/read persistence.
- Web: compact globe control, search activity, citation pills/cards, sources sheet/drawer, search settings, shared normalization and SSE search states.
- Tests/evals: 25-case harness, unchanged live recordings, separate synthetic browser and attack fixtures, before/after planner trial, hybrid run logs, source tests and browser tests.
- Deployment/docs: prepared localhost-only SearXNG compose/settings template and setup notes; this report; evidence under `artifacts/phase-2/`.

## Deviations from SPEC.md

- The harness now records/checks planner freshness, rather than silently ignoring `freshness_in` expectations. Historical reports do not contain that field.
- No new production prompt rules: E4 and E8 remain verbatim SPEC prompts. A generic task/scope clarification exists only in the evaluation harness and is not promoted.
- Native extraction now uses one dedicated worker. The original concurrent lxml parsing crashed CPython with SIGABRT; downloads still run concurrently. This preserves the specified stack and thread-pool extraction, while keeping parser/tree ownership on one worker.
- SearXNG config is prepared but cannot be validated until the required host container runtime is approved/installed. The image digest will be pinned after the real smoke test.

## Runtime observations

The older live baseline initially returned results, then mostly rate-limited/returned no results. Its DDGS backend list included DuckDuckGo and Brave scraping while labeling both DuckDuckGo, so engine provenance is indeterminate. The implementation now requests only `backend="duckduckgo"`; the separate keyed Brave API remains its own provider. The [DDGS documentation](https://github.com/deedy5/ddgs#text) describes its selectable backends. Fresh recordings are kept separately under `fixtures/2026-10-01-ddg-only`. A current single-query smoke succeeded, but the full rerun soon hit HTTP 202 challenge responses again. No Brave key or Docker/OrbStack is available. The complete live baseline had only three successful web turns, so fallback model facts are not evidence that search works. The NBA all-losses planner narrowed the request to teams that never won championships despite the user’s explicit broader scope.

The latest DDG-only recording is `server/evals/web/reports/2026-10-01-173016-…-live-keyword.md`: 25 cases, 6 pass, planner accuracy 88.9%, required facts 96%, citation support 0.8873. Only 3 web turns succeeded and 21 failed. Successful-source TTFT is P50 6.67s / P90 8.93s, insufficient coverage for acceptance. The 2021 result had the right facts but no inline citations; the comprehensive-losses queries still narrowed the population to teams that never won. The Ollama-release freshness check was exercised (`week`) and passed its planner expectation, but fetching failed. These recordings use one named engine and the current stricter harness.

A generic planner trial improved decision accuracy to 26/27 = 96.3%, but still narrowed the NBA request and failed citation/fixture gates. It remains unpromoted. The baseline’s “18 cases passed” and subsecond median used older loose checks; corrected metrics are in `artifacts/phase-2/live-baseline-corrected-metrics.json` and only four baseline cases pass those stricter checks.

The first hybrid run exited 134: macOS’s crash report identifies an invalid free inside lxml HTML parsing on a worker thread. `extraction-crash-summary.json` preserves the relevant stack without machine identity. The single-worker stress check extracted 48 recorded pages with no errors in 3.76s. The full hybrid retry completed all 25 cases without a crash: 6 pass, decisions 88.9%, citation support 0.6979. Only two turns have web sources; embedding timed out at ~8.02 seconds and fell back to keyword ranking. Successful-source TTFT P50 is 14.39 seconds. This is a failed embedding availability test, not a valid hybrid-versus-keyword quality comparison. Parser isolation follows the thread ownership concerns documented in the [lxml FAQ](https://lxml.de/FAQ.html#can-i-use-threads-to-concurrently-access-the-lxml-api); the crash cause attribution is an inference from the local stack and observed concurrent calls.

## Test output

`make check`: current output in `artifacts/phase-2/check.txt`; 142 Python tests and 33 Vitest checks passed after parser isolation and Data controls; strict typing, lint/format, 56 contrast pairs and API contract are included. Providers/runs/search line coverage remains above 80%.

`make e2e`: full baseline had 58 passes plus two case-sensitive label failures; the corrected UI/performance run passed 14 tests and the expanded final review passed 32. Both Chromium and WebKit exercised Stop, 100 tok/s rendering, saved preferences, citation cards and source panels. The final complete suite (`artifacts/phase-2/e2e-phase-final.txt`) passes 84 tests with 2 deliberate duplicate skips. The real-time long/idle gate passed on Chromium; Stop/reopen passed on both engines.

`make eval-web`: complete live and offline baseline reports are attached under `server/evals/web/reports/`; their limitations are stated above. The newer harness returns a failure exit when full-set gates fail. The planner trial returned 1. The initial hybrid process crashed; the completed retry returned 1 because accuracy, source coverage and injection gates failed. No missing fixture is silently replaced by live traffic or a fabricated success.

## Screenshots

`artifacts/phase-2/{web-chat,citation-card,sources}-{390,1440}-{light,dark}-fake-web.png`. All are clearly synthetic browser evidence. Phone sources and desktop dark sources were visually reviewed; text is contained and the composer remains in a separate row. Models/settings screenshots are in Phase 1.

## Open questions for Jake

The dependency choice is already pending: install Docker Desktop for local SearXNG, supply a Brave key, or explicitly keep DuckDuckGo-only reliability pending. **SPEC C1 requires approval for adding a dependency.** No container runtime has been installed while that question is unanswered.

Remaining work before acceptance: complete healthy live recordings for 25 cases, resolve the planner’s broad-scope error with generic before/after evidence, meet citation/fact thresholds across the approved models, finish a fair keyword/hybrid comparison, and verify the installed candidate on the physical phone. Production deployment/import belongs to Phase 3; the installed 0.5 app is still restored and running.
