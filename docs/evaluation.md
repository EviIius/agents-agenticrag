# Experiment records and deterministic metrics

`agenticrag compare` runs every case through the direct and fixed-RAG workflows under the active
provider configuration. `--include-agent` adds bounded agentic RAG to the same run matrix. Run the
same frozen JSONL dataset again with a different explicit provider configuration to compare
local/open-weight and hosted models.

Each run gets a random `run_id`. The append-only journal writes one `started` record before model
execution and one `completed` or `failed` record afterward. A process crash therefore leaves a
latest `started` record, which `summarize` reports as incomplete and counts in the failure rate.
Each record contains:

- manifest schema version and UTC record timestamp;
- complete case input, collection, and authorization scopes;
- workflow name/version and retrieval/agent/tool budgets plus explicitly requested skill names;
- sanitized chat and embedding provider labels;
- result evidence, citations, events, and elapsed time, or a typed error.

API keys and PostgreSQL DSNs are never included.

## Case schema

Required fields are `id`, `question`, `collection`, and a non-empty `scopes` array. Optional
deterministic annotations are:

- `answerable`: `true`, `false`, or omitted;
- `required_chunk_ids`: evidence units expected from this frozen corpus/index generation;
- `expected_answer_contains`: case-insensitive substrings required in an answer.

Chunk annotations are index-generation-specific. Freeze the corpus, chunker, embedding model, and
preprocessing before creating them.

## Summary metrics

- `failure_rate`: failed or incomplete runs divided by all latest runs.
- `mean_latency_ms` and `p95_latency_ms`: completed-run wall time; p95 uses nearest rank.
- `evidence_recall`: annotated required chunk IDs present in packed evidence.
- `complete_multi_hop_evidence`: cases with more than one required chunk where all are present.
- `answer_substring_accuracy`: answerable annotated cases containing every expected substring and
  not abstaining.
- `appropriate_abstention`: unanswerable annotated cases that abstain.
- `citation_resolution_rate`: cited chunk IDs that occur in the returned evidence set.
- `tool_call_count` and `tool_failure_rate`: validated agent tool attempts and rejected/failed
  calls.
- `review_count` and `review_rejection_rate`: evidence-critic decisions.
- `budget_exhaustion_rate`: completed runs that terminated at an agent step/time cap.
- `skill_load_count`: selected skill bundles loaded across runs; exact hashes remain in events.

Every summary includes denominators and uses `null` where no cases were annotated for a metric.
Failed and interrupted runs remain in annotated metric denominators and therefore count as misses;
they are not silently dropped. Latency summaries use completed runs only.

These are engineering checks, not substitutes for the PDF's release evaluation. Substring matching
is not semantic correctness, and citation resolution is not entailment. Human/adjudicated answer
correctness, claim-level citation precision/coverage, repeated runs, paired bootstrap confidence
intervals, timeouts, resource measurements, and an independent calibrated judge still need to be
added before release claims are made.
