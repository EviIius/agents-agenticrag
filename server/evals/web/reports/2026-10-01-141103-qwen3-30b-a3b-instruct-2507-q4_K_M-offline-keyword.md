> Historical run: not acceptance evidence. Freshness expectations were not yet checked. Earlier DDGS recordings could combine DuckDuckGo and Brave scraping under one label; provider-specific reliability cannot be inferred. See docs/PHASE-2-REPORT.md for corrected metrics and current limitations.

# Web evaluation — qwen3:30b-a3b-instruct-2507-q4_K_M

2026-10-01-141103 · 25 cases · keyword · recorded web

## Metrics

```json
{
  "cases": 25,
  "cases_passed": 18,
  "search_decision_accuracy": 0.8888888888888888,
  "required_fact_case_accuracy": 0.8823529411764706,
  "forbidden_cases": [],
  "citation_support_mean": 0.75,
  "ttft_p50_ms": 871.7719159994886,
  "ttft_p90_ms": 1056.3947089995054
}
```

Citation support is a lexical heuristic, not an entailment check. No-citation answers are reported separately and do not improve support. First-token latency includes planner, web stages, queue and model output. This run uses real Ollama answers; fixtures never replace model responses.

| Case | Passed | Sources | TTFT |
|---|---|---|---|
| nba-2021 | False | 6 | 4.76s |
| nba-followup | True | 0 | 0.89s |
| thanks | True | 0 | 0.54s |
| rewrite-shorter | True | 0 | 0.95s |
| haiku | True | 0 | 0.63s |
| ollama-latest | False | 0 | 1.06s |
| compare-chips | False | 0 | 0.88s |
| number-lookup | True | 0 | 0.62s |
| unanswerable | True | 0 | 0.77s |
| contested | False | 0 | 1.05s |
| injection | True | 0 | 0.99s |
| table-page | False | 0 | 0.96s |
| nba-all-losses | False | 0 | 1.03s |
| capital-france | True | 6 | 5.11s |
| mount-everest | True | 0 | 0.75s |
| si-metre | True | 0 | 0.74s |
| http-204 | True | 0 | 0.94s |
| python-zoneinfo | True | 0 | 0.98s |
| mars-moons | True | 0 | 0.67s |
| solar-planets | True | 0 | 0.70s |
| wwii-year | True | 0 | 0.58s |
| simple-math | True | 0 | 0.63s |
| translation | True | 0 | 0.61s |
| fiction | True | 0 | 0.72s |
| capital-compare | False | 0 | 0.70s |

Full answers, passages and per-stage timings are in the accompanying JSON.
