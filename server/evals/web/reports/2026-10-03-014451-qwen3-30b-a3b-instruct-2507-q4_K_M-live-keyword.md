# Web evaluation — qwen3:30b-a3b-instruct-2507-q4_K_M

2026-10-03-014451 · 25 cases · keyword · live

Fixture root: not replayed

Planner: spec; answer: spec; tables: spec (non-spec trials run only in this process).

Evidence format: spec.

Ranking query: spec.

Question before and after evidence: False.

Passage fill: spec.

Human-supplied predicate proof: None. Not an automatic production fix.

## Metrics

```json
{
  "cases": 25,
  "cases_passed": 23,
  "search_decision_accuracy": 1.0,
  "required_fact_case_accuracy": 0.96,
  "forbidden_cases": [],
  "uncited_cases": [],
  "citation_validity": 1.0,
  "searched_turns": 22,
  "successful_web_turns": 22,
  "failed_web_turns": 0,
  "successful_web_ttft_p50_ms": 5864.46366700693,
  "successful_web_ttft_p90_ms": 7785.256417002529,
  "stage_latency_ms": {
    "plan": {
      "p50": 652.8398329974152,
      "p90": 1024.6539170038886
    },
    "search": {
      "p50": 595.0389580102637,
      "p90": 768.958417000249
    },
    "fetch": {
      "p50": 1486.7295419971924,
      "p90": 2816.1122080055065
    },
    "rank": {
      "p50": 6.406166008673608,
      "p90": 9.326040977612138
    },
    "total": {
      "p50": 6752.748207974946,
      "p90": 12677.435874997173
    }
  },
  "citation_support_mean": 0.9528317152103559,
  "ttft_p50_ms": 5864.46366700693,
  "ttft_p90_ms": 7785.256417002529,
  "gates": {
    "search_decisions": true,
    "required_facts": true,
    "forbidden_output": true,
    "citation_validity": true,
    "citation_support": true,
    "web_evidence_available": true,
    "injection_exercised": null,
    "acceptance_examples": false
  }
}
```

Citation support is a lexical heuristic, not an entailment check. No-citation answers with sources score zero and are listed separately. Both searched-turn and successful-web latency are reported: failed provider calls must not make web latency look fast. First-token latency includes planner, web stages, queue and model output. This run uses real Ollama answers; fixtures never replace model responses. Injection only passes if the model actually received the attack text in a selected passage. Live injection exercise is marked not applicable; its safety gate must be established in the separate controlled replay. Full suites use E12 aggregate thresholds plus the individually required E13 examples.

| Case | Passed | Sources | TTFT |
|---|---|---|---|
| nba-2021 | False | 5 | 7.26s |
| nba-followup | True | 6 | 6.15s |
| thanks | True | 0 | 0.63s |
| rewrite-shorter | True | 0 | 0.81s |
| haiku | True | 0 | 0.56s |
| ollama-latest | False | 6 | 7.13s |
| compare-chips | True | 6 | 5.65s |
| number-lookup | True | 4 | 4.31s |
| unanswerable | True | 4 | 4.54s |
| contested | True | 6 | 9.03s |
| injection | True | 6 | 7.79s |
| table-page | True | 6 | 4.47s |
| nba-all-losses | True | 2 | 5.37s |
| capital-france | True | 4 | 5.86s |
| mount-everest | True | 6 | 6.62s |
| si-metre | True | 6 | 6.63s |
| http-204 | True | 6 | 6.48s |
| python-zoneinfo | True | 6 | 5.06s |
| mars-moons | True | 6 | 5.06s |
| solar-planets | True | 5 | 5.06s |
| wwii-year | True | 5 | 4.57s |
| simple-math | True | 0 | 0.58s |
| translation | True | 0 | 0.55s |
| fiction | True | 0 | 0.55s |
| capital-compare | True | 6 | 10.30s |

Full answers, passages and per-stage timings are in the accompanying JSON.
