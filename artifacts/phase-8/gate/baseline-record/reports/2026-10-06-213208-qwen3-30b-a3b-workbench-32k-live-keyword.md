# Web evaluation — qwen3:30b-a3b-workbench-32k

2026-10-06-213208 · 15 cases · keyword · live

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
  "successful_web_ttft_p50_ms": 7230.045375006739,
  "successful_web_ttft_p90_ms": 16372.059124987572,
  "stage_latency_ms": {
    "plan": {
      "p50": 917.2788329888135,
      "p90": 1153.6449160194024
    },
    "search": {
      "p50": 769.6502080070786,
      "p90": 1062.1818749932572
    },
    "fetch": {
      "p50": 2040.1957079884596,
      "p90": 11980.841166980099
    },
    "rank": {
      "p50": 7.805000001098961,
      "p90": 11.836958001367748
    },
    "total": {
      "p50": 9401.703500014264,
      "p90": 17055.359125020914
    }
  },
  "citation_support_mean": 0.9431594860166288,
  "ttft_p50_ms": 7230.045375006739,
  "ttft_p90_ms": 16372.059124987572,
  "gates": {
    "search_decisions": true,
    "required_facts": false,
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
| sqlite-integrity-storage | True | 6 | 6.11s |
| python-environment-threads | False | 6 | 7.49s |
| git-undo-strategies | True | 6 | 16.37s |
| browser-worker-cache | True | 6 | 6.07s |
| wcag-keyboard-motion | False | 6 | 7.93s |
| http-precondition-comparison | False | 6 | 6.41s |
| postgres-snapshot-recovery | False | 6 | 7.47s |
| linux-link-lifetime | False | 5 | 7.23s |
| nasa-voyager-webb | False | 6 | 7.92s |
| nasa-mars-landings | True | 6 | 6.47s |
| esa-observatory-comparison | True | 6 | 12.32s |
| national-park-origins | True | 6 | 6.93s |
| unesco-first-sites | True | 5 | 16.59s |
| archives-founding-documents | True | 6 | 6.66s |
| ietf-http-transports | True | 6 | 6.12s |

Full answers, passages and per-stage timings are in the accompanying JSON.
