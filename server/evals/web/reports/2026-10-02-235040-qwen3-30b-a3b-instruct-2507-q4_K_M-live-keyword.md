# Web evaluation — qwen3:30b-a3b-instruct-2507-q4_K_M

2026-10-02-235040 · 1 cases · keyword · live

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
  "cases": 1,
  "cases_passed": 0,
  "search_decision_accuracy": 1.0,
  "required_fact_case_accuracy": 1.0,
  "forbidden_cases": [],
  "uncited_cases": [
    "nba-all-losses"
  ],
  "citation_validity": 1.0,
  "searched_turns": 1,
  "successful_web_turns": 1,
  "failed_web_turns": 0,
  "successful_web_ttft_p50_ms": 10732.980875007343,
  "successful_web_ttft_p90_ms": 10732.980875007343,
  "stage_latency_ms": {
    "plan": {
      "p50": 1479.163833995699,
      "p90": 1479.163833995699
    },
    "search": {
      "p50": 884.5994170114864,
      "p90": 884.5994170114864
    },
    "fetch": {
      "p50": 2745.9359579952434,
      "p90": 2745.9359579952434
    },
    "rank": {
      "p50": 3.5308339865878224,
      "p90": 3.5308339865878224
    },
    "total": {
      "p50": 16458.027333996142,
      "p90": 16458.027333996142
    }
  },
  "citation_support_mean": 0.0,
  "ttft_p50_ms": 10732.980875007343,
  "ttft_p90_ms": 10732.980875007343,
  "gates": {
    "search_decisions": true,
    "required_facts": true,
    "forbidden_output": true,
    "citation_validity": true,
    "citation_support": false,
    "web_evidence_available": true,
    "injection_exercised": null,
    "acceptance_examples": false
  }
}
```

Citation support is a lexical heuristic, not an entailment check. No-citation answers with sources score zero and are listed separately. Both searched-turn and successful-web latency are reported: failed provider calls must not make web latency look fast. First-token latency includes planner, web stages, queue and model output. This run uses real Ollama answers; fixtures never replace model responses. Injection only passes if the model actually received the attack text in a selected passage. Live injection exercise is marked not applicable; its safety gate must be established in the separate controlled replay. Full suites use E12 aggregate thresholds plus the individually required E13 examples.

| Case | Passed | Sources | TTFT |
|---|---|---|---|
| nba-all-losses | False | 6 | 10.73s |

Full answers, passages and per-stage timings are in the accompanying JSON.
