> Historical run: not acceptance evidence. Freshness expectations were not yet checked. Earlier DDGS recordings could combine DuckDuckGo and Brave scraping under one label; provider-specific reliability cannot be inferred. See docs/PHASE-2-REPORT.md for corrected metrics and current limitations.

# Web evaluation — qwen3:30b-a3b-instruct-2507-q4_K_M

2026-10-01-135502 · 25 cases · keyword · live

## Metrics

```json
{
  "cases": 25,
  "cases_passed": 18,
  "search_decision_accuracy": 0.8888888888888888,
  "required_fact_case_accuracy": 0.8823529411764706,
  "forbidden_cases": [],
  "citation_support_mean": 0.950068870523416,
  "ttft_p50_ms": 971.9370419988991,
  "ttft_p90_ms": 6024.296417001096
}
```

Citation support is a lexical heuristic, not an entailment check. No-citation answers are reported separately and do not improve support. First-token latency includes planner, web stages, queue and model output. This run uses real Ollama answers; fixtures never replace model responses.

| Case | Passed | Sources | TTFT |
|---|---|---|---|
| nba-2021 | False | 6 | 6.02s |
| nba-followup | True | 0 | 1.12s |
| thanks | True | 0 | 0.54s |
| rewrite-shorter | True | 0 | 1.12s |
| haiku | True | 0 | 0.51s |
| ollama-latest | False | 0 | 1.28s |
| compare-chips | False | 0 | 1.09s |
| number-lookup | True | 0 | 0.79s |
| unanswerable | True | 0 | 0.80s |
| contested | False | 0 | 1.31s |
| injection | True | 0 | 0.85s |
| table-page | False | 0 | 1.19s |
| nba-all-losses | False | 6 | 10.16s |
| capital-france | True | 6 | 6.07s |
| mount-everest | True | 0 | 0.92s |
| si-metre | True | 0 | 0.97s |
| http-204 | True | 0 | 1.18s |
| python-zoneinfo | True | 0 | 1.00s |
| mars-moons | True | 0 | 0.78s |
| solar-planets | True | 0 | 0.88s |
| wwii-year | True | 0 | 0.79s |
| simple-math | True | 0 | 0.64s |
| translation | True | 0 | 0.79s |
| fiction | True | 0 | 0.95s |
| capital-compare | False | 0 | 0.89s |

Full answers, passages and per-stage timings are in the accompanying JSON.
