# Web evaluation — qwen3:30b-a3b-instruct-2507-q4_K_M

2026-10-11-181843 · 1 cases · keyword · recorded web

Fixture root: /Users/evilius/Documents/GitHub/agents-agenticrag/artifacts/images-i1/search-repair/fixtures

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
  "successful_web_ttft_p50_ms": 226.36729100486264,
  "successful_web_ttft_p90_ms": 226.36729100486264,
  "stage_latency_ms": {
    "plan": {
      "p50": 6.543791969306767,
      "p90": 6.543791969306767
    },
    "search": {
      "p50": 0.9306250140070915,
      "p90": 0.9306250140070915
    },
    "fetch": {
      "p50": 3.284833044745028,
      "p90": 3.284833044745028
    },
    "rank": {
      "p50": 0.7861250196583569,
      "p90": 0.7861250196583569
    },
    "total": {
      "p50": 492.1970829600468,
      "p90": 492.1970829600468
    }
  },
  "citation_support_mean": 1.0,
  "ttft_p50_ms": 226.36729100486264,
  "ttft_p90_ms": 226.36729100486264,
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
| external-03 | True | 1 | 0.23s |

Full answers, passages and per-stage timings are in the accompanying JSON.
