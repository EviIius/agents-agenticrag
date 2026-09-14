# Architecture and trust boundaries

## Current vertical slice

```text
CLI / versioned local HTTP API / bundled web workbench
        |
        +-- provider factory -------------------------+
        |       |                                     |
        |       +-- local loopback (default)          +-- OpenAI (explicit opt-in)
        |
        +-- fixed RAG workflow
                |
                +-- hybrid retriever
                |       +-- lexical search (SQLite FTS5 / PostgreSQL tsvector)
                |       +-- exact cosine search (SQLite scan / pgvector)
                |       +-- reciprocal-rank fusion + evidence budget
                |
                +-- validated answer/citation boundary
                        |
                        +-- immutable source version
                                +-- original SHA-256 + parsed SHA-256 + parser identity
                                +-- page / section / table / canonical offsets

        +-- bounded agentic RAG
                +-- obligation planner
                +-- hashed local skill registry
                +-- read-only tool gateway
                |       +-- authorized hybrid search
                |       +-- searched-source bounded lookup
                |       +-- AST-safe arithmetic
                +-- step / time / tool / context / stall budgets
                +-- evidence allowlist + separate critic pass

        +-- manager multi-agent supervisor
                +-- schema-validated assignment plan (maximum 3)
                +-- non-recursive specialist calls
                |       +-- corpus researcher
                |       +-- quantitative analyst
                |       +-- advertising strategist + selected skills
                |       +-- hosted web researcher (OpenAI + per-run consent only)
                +-- specialist report synthesis + final evidence critic
                +-- delegation and external-source trace returned to the UI

Experiment runner --> append-only JSONL manifests --> deterministic metric summaries
```

The workbench is a zero-build static client of `/api/v1`; it does not duplicate retrieval or agent
logic. Runtime connections are held in process memory, non-secret preferences stay in browser
storage, and the capability inspector is rendered from backend-reported tools, skills, plugin
status, budgets, and agent policy. Source upload is bounded, base64-decoded by the local service,
parsed through the same ingestion boundary as the CLI, and removed from temporary storage after
immutable publication.

The SQLite store makes the slice runnable on a clean machine and is deliberately labeled a
development adapter. It preserves the important contracts: current immutable versions, exact
vector search, lexical search, collection constraints, and authorization filtering before content
leaves the database. The PostgreSQL adapter implements the same contract using transactional
publication, pgvector exact search, PostgreSQL full-text search, and a SHA-256-verified local object
store for immutable originals.

The ingestion boundary reads a bounded local file exactly once, validates its extension against
its signature, hashes the original bytes, and produces deterministic canonical text plus
`ProvenanceSpan` records. Built-in parsers cover UTF-8 text, Markdown, and safe OOXML traversal.
Text PDFs use optional pypdf. Docling is the richer PDF/OCR adapter only when its artifacts path is
explicitly configured; remote services and external plugins are disabled. A scanned or low-text
PDF fails with a remediation message when that local capability is absent.

## Security invariants

1. The authenticated application supplies scopes. Model output never supplies identity, scopes,
   collections, database credentials, or filesystem roots.
2. Retrieval queries apply collection and scope predicates before chunks are returned. There is no
   fetch-then-filter path.
3. Retrieved text is delimited as untrusted evidence. Instructions inside a document have no tool
   authority.
4. A generated citation is accepted only when its chunk ID is in the authorized evidence set. The
   application constructs source-version and offset metadata; the model cannot invent it.
5. Original bytes, parsed text, parser identity, scope set, chunks, provenance, and embeddings are
   immutable within a version. Re-ingesting changed content, parser output, parser identity, or
   permissions publishes another version and atomically advances the current pointer.
6. SQLite keeps one embedding index generation per database. PostgreSQL can retain generations
   for different embedding-provider labels; reusing a label with a changed dimension or chunking
   signature is rejected instead of silently mixing incompatible vectors.
7. `local` provider profiles accept loopback URLs only, unless the operator supplies exact private
   hostnames through `AGENTICRAG_LOCAL_RUNTIME_HOSTS` for container networking. OpenAI requires an
   explicit role selection, model, and API key. Provider failure never causes fallback.
8. The current release has no mutation tools, shell execution, durable generated memory, hosted
   tracing, or background network activity. Hosted web search exists only behind OpenAI provider
   configuration and explicit per-run consent; Responses requests use `store: false`.
9. Skill discovery is confined to explicit project and standard Agent Skills roots, rejects
   escaping paths and oversized or malformed bundles, records source plus hashes, and treats
   skill metadata as incapable of granting tools or permissions.
10. Agent actions are model proposals, not authority. The host owns the tool allowlist, validates
    exact arguments, applies collection/scopes, limits source lookup to versions already observed
    through authorized search, and rejects fabricated final citations.
11. Browser writes require same-origin requests, assets use a restrictive Content Security Policy,
    provider probes call only the explicitly selected `/v1/models` endpoint, and non-loopback UI
    binding requires the operator to opt into `--allow-remote` for a trusted proxy deployment.
12. Supervisor plans can name only the backend-reported specialist allowlist. Assignment IDs,
    tasks, skills, delegation count, time, specialist steps, synthesis references, and final review
    are validated by host code; specialists cannot recursively delegate.

## Provider contract

Chat and embedding are independent roles. Both use narrow protocols in
`agenticrag.providers.base`; the current adapter speaks the OpenAI-compatible HTTP shape. A
loopback llama.cpp, Ollama, LM Studio, vLLM, or MLX deployment can therefore be qualified without coupling the
workflow to its runtime. The same workflow accepts an OpenAI comparison provider only when the
operator selects it through environment configuration.

For heterogeneous open-source models, structured agent responses have three explicit transport
modes: provider-enforced JSON Schema, provider JSON-object mode with a trusted schema instruction,
and schema-in-prompt mode for minimal compatible servers. All modes converge on the same strict
Python validators. The workbench includes an opt-in model contract check covering structured JSON,
a bounded arithmetic obligation, tool selection, and host validation before a model is trusted for
agentic runs.

Provider labels are included in results and append-only run manifests. Credentials are not. Current
manifests also capture workflow version, retrieval budgets, case inputs, results, typed failures,
and interrupted `started` runs. Exact artifact revision, quantization, runtime build, token usage,
and hardware measurements remain qualification work.

## Why the controllers do not require LangGraph yet

The fixed workflow has no adaptive loop. The bounded agent implements planning, gap-directed
tools, review, and hard termination as inspectable plain Python. The supervisor adds cooperating
agents through a bounded manager pattern while retaining the same host-owned contracts. LangGraph
becomes useful when the project adds durable checkpoints, interrupts, or resumable distributed
state; it is not required merely to call tools or bounded specialists. The workflow protocol lets
that runtime be added later without changing provider, skill, tool, or evidence contracts.

## Answer contract

The generator returns `{answer, citations, abstained}` under a JSON schema. The host validates
field types, rejects unknown or duplicate citation IDs, and requires at least one citation for a
non-abstaining fixed-RAG answer. An empty authorized retrieval set terminates without calling the
generator and returns an explicit abstention.

Citation objects are enriched by the host with canonical offsets, page bounds when the format can
provide them, section paths, table IDs, OCR markers, and stable segment IDs. This proves citation
resolution, not entailment. Claim-to-span entailment and per-obligation
sufficiency validation are Phase 2/evaluation work.
