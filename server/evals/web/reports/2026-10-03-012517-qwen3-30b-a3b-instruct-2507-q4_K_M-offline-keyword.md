# Web evaluation — qwen3:30b-a3b-instruct-2507-q4_K_M

2026-10-03-012517 · 1 cases · keyword · recorded web

Fixture root: evals/web/fixtures/phase2-closeout-live

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
  "successful_web_ttft_p50_ms": 3449.757458001841,
  "successful_web_ttft_p90_ms": 3449.757458001841,
  "stage_latency_ms": {
    "plan": {
      "p50": 1441.0110829921905,
      "p90": 1441.0110829921905
    },
    "search": {
      "p50": 0.010624993592500687,
      "p90": 0.010624993592500687
    },
    "fetch": {
      "p50": 980.8817919983994,
      "p90": 980.8817919983994
    },
    "rank": {
      "p50": 0.6471669767051935,
      "p90": 0.6471669767051935
    },
    "total": {
      "p50": 8549.77312500705,
      "p90": 8549.77312500705
    }
  },
  "citation_support_mean": 1.0,
  "ttft_p50_ms": 3449.757458001841,
  "ttft_p90_ms": 3449.757458001841,
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
| nba-all-losses | True | 1 | 3.45s |

Full answers, passages and per-stage timings are in the accompanying JSON.
