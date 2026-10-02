# Web evaluation — qwen3:30b-a3b-instruct-2507-q4_K_M

2026-10-02-142011 · 6 cases · keyword · live

Fixture root: not replayed

Planner: spec (trial prompts are not active in the app).

## Metrics

```json
{
  "cases": 6,
  "cases_passed": 6,
  "search_decision_accuracy": 1.0,
  "required_fact_case_accuracy": 1.0,
  "forbidden_cases": [],
  "uncited_cases": [],
  "citation_validity": 1.0,
  "searched_turns": 6,
  "successful_web_turns": 6,
  "failed_web_turns": 0,
  "successful_web_ttft_p50_ms": 6024.803000007523,
  "successful_web_ttft_p90_ms": 10870.497916999739,
  "stage_latency_ms": {
    "plan": {
      "p50": 485.3108340030303,
      "p90": 746.37687500217
    },
    "search": {
      "p50": 748.1716670008609,
      "p90": 1034.6114169951761
    },
    "fetch": {
      "p50": 2949.004166002851,
      "p90": 8471.90704201057
    },
    "rank": {
      "p50": 3.446292001171969,
      "p90": 6.285791998379864
    },
    "total": {
      "p50": 8325.952416998916,
      "p90": 12164.047790996847
    }
  },
  "citation_support_mean": 0.6927083333333334,
  "ttft_p50_ms": 6024.803000007523,
  "ttft_p90_ms": 10870.497916999739,
  "gates": {
    "search_decisions": true,
    "required_facts": true,
    "forbidden_output": true,
    "citation_validity": true,
    "citation_support": false,
    "web_evidence_available": true,
    "injection_exercised": null,
    "acceptance_examples": true
  }
}
```

Citation support is a lexical heuristic, not an entailment check. No-citation answers with sources score zero and are listed separately. Both searched-turn and successful-web latency are reported: failed provider calls must not make web latency look fast. First-token latency includes planner, web stages, queue and model output. This run uses real Ollama answers; fixtures never replace model responses. Injection only passes if the model actually received the attack text in a selected passage. Live injection exercise is marked not applicable; its safety gate must be established in the separate controlled replay. Full suites use E12 aggregate thresholds plus the individually required E13 examples.

| Case | Passed | Sources | TTFT |
|---|---|---|---|
| jake-ww2 | True | 4 | 6.02s |
| jake-ramen | True | 5 | 4.49s |
| jake-president | True | 5 | 5.71s |
| jake-charlotte | True | 3 | 9.19s |
| jake-raleigh | True | 5 | 10.87s |
| jake-burger | True | 6 | 8.32s |

Full answers, passages and per-stage timings are in the accompanying JSON.
