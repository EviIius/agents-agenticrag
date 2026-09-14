# PDF-aligned implementation roadmap

## Complete in the foundation slice

- Local-first, role-specific provider configuration with loopback enforcement and no fallback.
- Optional OpenAI provider path with environment-only credentials and explicit model selection.
- UTF-8 text and Markdown parsing with source offsets and heading-aware chunks.
- Immutable content/scope versions and an atomic current-version pointer.
- SQLite FTS5 plus exact cosine retrieval under collection and scope predicates.
- Application-level reciprocal-rank fusion, document diversity, and evidence budget.
- Fixed-RAG prompting, structured output, citation allowlisting, typed failures, and abstention.
- Direct and fixed-RAG workflows behind a common experiment runner.
- PostgreSQL/pgvector runtime adapter, packaged migration, SQL contract tests, and opt-in live test.
- Content-addressed local originals with SHA-256 verification on source resolution.
- Append-only started/terminal run manifests and deterministic comparison summaries.
- Bounded TXT, Markdown, DOCX, text-PDF, and local scanned-PDF/OCR ingestion.
- Original-byte and parsed-text hashes, parser identity, content-addressed originals, and
  page/section/table/segment provenance carried into validated citations.
- Bounded obligation-driven agent with hashed local skills, read-only tools, hard budgets, stall
  detection, per-obligation evidence accounting, and a separate evidence-review pass.
- Zero-build local workbench and versioned HTTP API for runtime setup/probing, source ingestion and
  viewing, fixed/direct/agentic chat, capability inspection, citations, and execution traces.
- LM Studio, Ollama, llama.cpp, vLLM, and generic OpenAI-compatible runtime presets with selectable
  JSON Schema, JSON-object, and schema-in-prompt compatibility modes.
- Container image, loopback-published Compose service, persistent corpus volume, read-only skill
  mount, workstation bootstrap scripts, and an explicit container-runtime hostname allowlist.

## Next: finish Phase 1 qualification

1. Qualify the PostgreSQL adapter against the target Mac service and tune connection/cursor use
   from measurements; keep exact search until latency justifies HNSW.
2. Qualify Docling artifacts/OCR engines on representative scanned and complex-table fixtures;
   the implemented adapter is capability-gated and its live path remains environment-dependent.
3. Add Qwen3-Reranker-0.6B behind the existing reranker protocol and adjacent-section expansion.
4. Extend manifests with model/runtime/template hashes, embedding preprocessing artifacts,
   quantization, index-generation metadata, token counts, and hardware measurements.
5. Add owner authentication before supporting any non-loopback deployment; the current workbench
   defaults to loopback and requires an explicit `--allow-remote` override for proxy deployments.
6. Add adjudicated answer/citation labels, three-run sampling, paired bootstrap confidence
   intervals, and binomial intervals to the versioned question-set foundation.
7. Run a network-isolated functional suite with all artifacts prefetched.

## In progress: Phase 2 bounded agentic RAG

- Completed: explicit obligations, local skills, validated `search`/`lookup`/`calculate`/`finish`
  actions, evidence deltas, step/time/tool/context/stall budgets, citation allowlisting, and a
  separate evidence critic.
- Next: add adjacent-section `expand`, query-hash loop diagnostics, and supported partial findings
  at the hard cap. The agentic workflow can already be included in the same experiment journal
  with `compare --include-agent`.
- Add LangGraph only when durable checkpoints, interrupts, resumability, or cooperating subagents
  justify it.
- Compare against the fixed baseline; keep fixed RAG as the default unless the agentic mode clears
  the measured benefit gate.

## Later phases

Phase 3 expands the current read-only tool boundary and only then considers previewed/idempotent
writes. Phase 4 adds owner authentication, private VPN access, service supervision, backup/restore, cancellation, and
concurrency controls. Phase 5 compares model sizes, families, runtimes, retrieval variants, and at
most two workers before graph retrieval, long-term memory, prompt optimization, LoRA, or RL.
