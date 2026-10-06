# Web evaluation — qwen3:30b-a3b-workbench-32k

2026-10-06-213415 · 15 cases · keyword · recorded web

Fixture root: /Users/evilius/Documents/GitHub/agents-agenticrag/artifacts/phase-8/gate/web-fixtures

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
  "cases": 15,
  "cases_passed": 9,
  "search_decision_accuracy": 1.0,
  "required_fact_case_accuracy": 0.6,
  "forbidden_cases": [],
  "uncited_cases": [],
  "citation_validity": 1.0,
  "searched_turns": 15,
  "successful_web_turns": 15,
  "failed_web_turns": 0,
  "successful_web_ttft_p50_ms": 4792.728291999083,
  "successful_web_ttft_p90_ms": 5663.742291973904,
  "stage_latency_ms": {
    "plan": {
      "p50": 955.312917008996,
      "p90": 1149.423792026937
    },
    "search": {
      "p50": 0.018625054508447647,
      "p90": 0.02900004619732499
    },
    "fetch": {
      "p50": 282.0482079987414,
      "p90": 812.2800830169581
    },
    "rank": {
      "p50": 7.582125021144748,
      "p90": 9.712125000078231
    },
    "total": {
      "p50": 6417.328791983891,
      "p90": 8837.113332992885
    }
  },
  "citation_support_mean": 0.939983579638752,
  "ttft_p50_ms": 4792.728291999083,
  "ttft_p90_ms": 5663.742291973904,
  "gates": {
    "search_decisions": true,
    "required_facts": false,
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
| sqlite-integrity-storage | True | 6 | 4.46s |
| python-environment-threads | False | 6 | 5.65s |
| git-undo-strategies | True | 6 | 4.13s |
| browser-worker-cache | True | 6 | 3.54s |
| wcag-keyboard-motion | False | 6 | 6.56s |
| http-precondition-comparison | False | 6 | 4.79s |
| postgres-snapshot-recovery | False | 6 | 4.73s |
| linux-link-lifetime | True | 5 | 4.91s |
| nasa-voyager-webb | False | 6 | 4.43s |
| nasa-mars-landings | True | 6 | 4.63s |
| esa-observatory-comparison | True | 6 | 5.66s |
| national-park-origins | True | 6 | 4.91s |
| unesco-first-sites | True | 5 | 4.85s |
| archives-founding-documents | True | 6 | 3.64s |
| ietf-http-transports | False | 6 | 4.83s |

Full answers, passages and per-stage timings are in the accompanying JSON.
