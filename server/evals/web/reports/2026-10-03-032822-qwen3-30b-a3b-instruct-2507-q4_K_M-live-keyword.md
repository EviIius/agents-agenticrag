# Web evaluation — qwen3:30b-a3b-instruct-2507-q4_K_M

2026-10-03-032822 · 1 cases · keyword · live

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
  "cases_passed": 1,
  "search_decision_accuracy": 1.0,
  "required_fact_case_accuracy": 1.0,
  "forbidden_cases": [],
  "uncited_cases": [],
  "citation_validity": 1.0,
  "searched_turns": 1,
  "successful_web_turns": 1,
  "failed_web_turns": 0,
  "successful_web_ttft_p50_ms": 6162.286000006134,
  "successful_web_ttft_p90_ms": 6162.286000006134,
  "stage_latency_ms": {
    "plan": {
      "p50": 1081.132624996826,
      "p90": 1081.132624996826
    },
    "search": {
      "p50": 1008.6652089958079,
      "p90": 1008.6652089958079
    },
    "fetch": {
      "p50": 1295.1240420225076,
      "p90": 1295.1240420225076
    },
    "rank": {
      "p50": 3.633749991422519,
      "p90": 3.633749991422519
    },
    "total": {
      "p50": 9710.396957991179,
      "p90": 9710.396957991179
    }
  },
  "citation_support_mean": 0.975,
  "ttft_p50_ms": 6162.286000006134,
  "ttft_p90_ms": 6162.286000006134,
  "gates": {
    "search_decisions": true,
    "required_facts": true,
    "forbidden_output": true,
    "citation_validity": true,
    "citation_support": true,
    "web_evidence_available": true,
    "injection_exercised": null,
    "acceptance_examples": true
  }
}
```

Citation support is a lexical heuristic, not an entailment check. No-citation answers with sources score zero and are listed separately. Both searched-turn and successful-web latency are reported: failed provider calls must not make web latency look fast. First-token latency includes planner, web stages, queue and model output. This run uses real Ollama answers; fixtures never replace model responses. Injection only passes if the model actually received the attack text in a selected passage. Live injection exercise is marked not applicable; its safety gate must be established in the separate controlled replay. Full suites use E12 aggregate thresholds plus the individually required E13 examples.

| Case | Passed | Sources | TTFT |
|---|---|---|---|
| ollama-latest | True | 6 | 6.16s |

Full answers, passages and per-stage timings are in the accompanying JSON.
