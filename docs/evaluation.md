# Experiment records and deterministic metrics

For a realistic, document-grounded comparison, follow
[evaluation v3 preparation](evaluation-v3-preparation.md) before using results for routing.

`agenticrag compare` runs every case through Direct and Fixed under the active provider
configuration. `--all-modes` adds Agentic and Supervisor. `--all-installed` checks every
installed Ollama chat model; `--model` selects specific models, `--exclude-model` skips one,
and `--repeat` runs each case more than once. The command reads the workbench's saved
runtime settings when available and writes an atomic JSON report with grouped results.

Build the isolated sample corpus with `python scripts/build_evaluation_corpus.py`, then run:

```bash
PYTHONPATH=src python -m agenticrag --db .data/evaluation-corpus.db compare \
  examples/evaluation-v1.jsonl --all-modes --all-installed --repeat 2 \
  --runs .data/evaluation-runs.jsonl --report .data/workbench-evaluation.json
```

This full matrix includes slow 70B Agentic and Supervisor runs; budget for a long serial
run. The Models page reads a report named `workbench-evaluation.json` beside its active
corpus database. Use `--report` to publish a complete report to that location.

`examples/evaluation-v2.jsonl` expands the local diagnostic set from eight to 24
cases spanning lookup, numerical details, two-source synthesis, mode selection,
missing evidence, access labels, and imported prompt-injection text. Keep the v1
dataset and its reports unchanged so comparisons remain reproducible. Begin with
one installed model and one repeat on v2, inspect the missed cases, then repeat
the promising configurations. Do not publish the v2 report as an automatic router
input until the answers and citations have been manually reviewed; substring
checks can miss wrong facts and can reject correct paraphrases.

```bash
PYTHONPATH=src python -m agenticrag --db .data/evaluation-corpus.db compare \
  examples/evaluation-v2.jsonl --model qwen3:30b-a3b-workbench-32k \
  --runs .data/evaluation-v2-runs.jsonl --report .data/evaluation-v2-report.json
```

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
- `required_quotes`: objects with `logical_path` and a verbatim `quote`; whitespace and case
  are normalized when checking whether a retrieved passage contains the quote;
- `split`: `dev` or `locked` (defaults to `dev`). Use `compare --split locked` to run only
  held-out cases and `summarize --split locked` to score only their recorded results;
- `expected_answer_contains`: case-insensitive substrings required in an answer.
- `forbidden_answer_contains`: substrings that must be absent, useful for prompt-injection
  and access-scope cases;
- `category`: a label for later per-task routing analysis.

Chunk annotations are index-generation-specific. Freeze the corpus, chunker, embedding model, and
preprocessing before creating them.

## Summary metrics

- `failure_rate`: failed or incomplete runs divided by all latest runs.
- `mean_latency_ms` and `p95_latency_ms`: completed-run wall time; p95 uses nearest rank.
- `evidence_recall`: annotated required chunk IDs present in packed evidence.
- `quote_evidence_recall`: annotated quotes found in a retrieved passage from the
  specified document path. Unlike chunk IDs, these annotations survive re-chunking.
- `complete_multi_hop_evidence`: cases with more than one required chunk where all are present.
- `answer_substring_accuracy`: answerable annotated cases containing every expected substring and
  not abstaining.
- `appropriate_abstention`: unanswerable annotated cases that abstain.
- `citation_resolution_rate`: cited chunk IDs that occur in the returned evidence set.
- `inline_citation_coverage`: cited IDs whose numbered marker appears somewhere in the answer.
  This checks formatting, not whether the nearby claim is actually supported.
- `tool_call_count` and `tool_failure_rate`: validated agent tool attempts and rejected/failed
  calls.
- `review_count` and `review_rejection_rate`: evidence-critic decisions.
- `budget_exhaustion_rate`: completed runs that terminated at an agent step/time cap.
- `skill_load_count`: selected skill bundles loaded across runs; exact hashes remain in events.
- `mean_model_loaded_gb`: sampled Ollama loaded-model footprint after each completed run.

Every summary includes denominators and uses `null` where no cases were annotated for a metric.
Failed and interrupted runs remain in annotated metric denominators and therefore count as misses;
they are not silently dropped. Latency summaries use completed runs only.

These are engineering checks, not a model quality ranking. Direct is intentionally scored on
the same sourced tasks as the grounded modes, so its low substring score is not a general
measure of conversational ability. Substring matching is not semantic correctness, citation
resolution is not entailment, and loaded-model footprint is not peak memory pressure.
Human/adjudicated answer correctness, claim-level citation support, paired confidence
intervals, timed cancellation cases, peak resources, web cases, and an independent calibrated
judge are still needed before release claims or automatic model routing.
