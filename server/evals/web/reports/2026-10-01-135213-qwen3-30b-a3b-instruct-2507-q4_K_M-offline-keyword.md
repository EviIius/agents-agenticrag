> Historical run: not acceptance evidence. Freshness expectations were not yet checked. Earlier DDGS recordings could combine DuckDuckGo and Brave scraping under one label; provider-specific reliability cannot be inferred. See docs/PHASE-2-REPORT.md for corrected metrics and current limitations.

# Web evaluation — qwen3:30b-a3b-instruct-2507-q4_K_M

2026-10-01-135213 · 1 cases · keyword · recorded web

## Metrics

```json
{
  "cases": 1,
  "cases_passed": 1,
  "search_decision_accuracy": 1.0,
  "required_fact_case_accuracy": 1.0,
  "forbidden_cases": [],
  "citation_support_mean": null,
  "ttft_p50_ms": 4713.444834000256,
  "ttft_p90_ms": 4713.444834000256
}
```

Citation support is a lexical heuristic, not an entailment check. No-citation answers are reported separately and do not improve support. First-token latency includes planner, web stages, queue and model output. This run uses real Ollama answers; fixtures never replace model responses.

| Case | Passed | Sources | TTFT |
|---|---|---|---|
| nba-2021 | True | 6 | 4.71s |

Full answers, passages and per-stage timings are in the accompanying JSON.
