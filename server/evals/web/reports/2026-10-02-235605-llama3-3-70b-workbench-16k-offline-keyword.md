# Web evaluation — llama3.3:70b-workbench-16k

2026-10-02-235605 · 1 cases · keyword · recorded web

Fixture root: evals/web/fixtures/phase2-selection-live

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
  "successful_web_ttft_p50_ms": 77316.60262499645,
  "successful_web_ttft_p90_ms": 77316.60262499645,
  "stage_latency_ms": {
    "plan": {
      "p50": 14656.682290995377,
      "p90": 14656.682290995377
    },
    "search": {
      "p50": 0.10045799717772752,
      "p90": 0.10045799717772752
    },
    "fetch": {
      "p50": 2305.6041250092676,
      "p90": 2305.6041250092676
    },
    "rank": {
      "p50": 3.5291660024086013,
      "p90": 3.5291660024086013
    },
    "total": {
      "p50": 139038.25604199665,
      "p90": 139038.25604199665
    }
  },
  "citation_support_mean": 0.9871794871794872,
  "ttft_p50_ms": 77316.60262499645,
  "ttft_p90_ms": 77316.60262499645,
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
| nba-all-losses | True | 6 | 77.32s |

Full answers, passages and per-stage timings are in the accompanying JSON.
