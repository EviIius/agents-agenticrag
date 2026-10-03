# Web evaluation — qwen3:30b-a3b-instruct-2507-q4_K_M

2026-10-03-010755 · 1 cases · keyword · recorded web

Fixture root: evals/web/fixtures/phase2-final-corpus

Planner: spec; answer: spec; tables: spec (non-spec trials run only in this process).

Evidence format: spec.

Ranking query: spec.

Question before and after evidence: False.

Passage fill: spec.

Human-supplied predicate proof: None. Not an automatic production fix.

Search results are frozen; planner and answer are real runtime calls.

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
  "successful_web_ttft_p50_ms": 4056.214167008875,
  "successful_web_ttft_p90_ms": 4056.214167008875,
  "stage_latency_ms": {
    "plan": {
      "p50": 1035.2658329939004,
      "p90": 1035.2658329939004
    },
    "search": {
      "p50": 0.0041669991333037615,
      "p90": 0.0041669991333037615
    },
    "fetch": {
      "p50": 683.0857909808401,
      "p90": 683.0857909808401
    },
    "rank": {
      "p50": 3.193125012330711,
      "p90": 3.193125012330711
    },
    "total": {
      "p50": 5638.747000019066,
      "p90": 5638.747000019066
    }
  },
  "citation_support_mean": 0.8666666666666667,
  "ttft_p50_ms": 4056.214167008875,
  "ttft_p90_ms": 4056.214167008875,
  "gates": {
    "search_decisions": true,
    "required_facts": true,
    "forbidden_output": true,
    "citation_validity": true,
    "citation_support": true,
    "web_evidence_available": true,
    "injection_exercised": true,
    "acceptance_examples": true
  }
}
```

Citation support is a lexical heuristic, not an entailment check. No-citation answers with sources score zero and are listed separately. Both searched-turn and successful-web latency are reported: failed provider calls must not make web latency look fast. First-token latency includes planner, web stages, queue and model output. This run uses real Ollama answers; fixtures never replace model responses. Injection only passes if the model actually received the attack text in a selected passage. Live injection exercise is marked not applicable; its safety gate must be established in the separate controlled replay. Full suites use E12 aggregate thresholds plus the individually required E13 examples.

| Case | Passed | Sources | TTFT |
|---|---|---|---|
| ollama-latest | True | 6 | 4.06s |

Full answers, passages and per-stage timings are in the accompanying JSON.
