# Local Agents and Agentic RAG

A local-first experimental workbench for comparing open-weight models with optional hosted
models across direct generation, fixed RAG, and bounded agentic RAG.

The implementation follows [Local_Agents_and_Agentic_RAG.pdf](./Local_Agents_and_Agentic_RAG.pdf):
application code owns authorization and validation, retrieved documents are treated as untrusted
data, sources are immutable and cited by stable IDs, and cloud inference is never an implicit
fallback.

## What works now

- Ingest local PDF, DOCX, Markdown, and TXT files into immutable source versions with canonical
  offsets and parser-neutral page/section/table provenance.
- Chunk and embed documents through a loopback OpenAI-compatible local server.
- Store a durable development corpus in SQLite with FTS5, exact cosine search, and SQL-enforced
  scope filtering.
- Run the same corpus contract on PostgreSQL with pgvector exact cosine search, native full-text
  search, transactional publication, and content-addressed immutable local originals.
- Fuse lexical and vector results with reciprocal-rank fusion, diversify documents, and enforce an
  evidence budget.
- Generate a fixed-RAG answer using a local model and accept only citations that resolve to the
  retrieved evidence set.
- Select chat and embedding providers independently, so the same pipeline can compare local
  models with an explicitly enabled OpenAI API profile.
- Run the core workflow and security contracts without a model server by using deterministic test
  doubles.
- Append fsynced started/terminal run manifests and summarize failures, incomplete runs, latency,
  evidence recall, multi-hop coverage, deterministic answer checks, abstention, and citation
  resolution by workflow/provider combination.
- Run an obligation-driven agent that can select local `SKILL.md` instruction bundles, invoke
  allowlisted read-only search/lookup/calculator tools, detect stalled actions, enforce step/time/
  tool/context budgets, and submit its answer to a separate evidence-review pass.
- Launch a zero-build local workbench for runtime setup, model probing, drag/drop ingestion,
  fixed/direct/agentic/supervisor chat, citations, source inspection, capability visibility, and
  delegation traces.
- Connect LM Studio, Ollama, llama.cpp, vLLM, or another loopback OpenAI-compatible server through
  strict JSON Schema, JSON-object, or schema-in-prompt compatibility modes.
- Run a manager-style supervisor that can call corpus, quantitative, advertising, and explicitly
  enabled hosted-web specialists, then synthesize their reports through a final evidence critic.
- Inspect the exact agent, tool, skill, and plugin inventory. Hosted web search is disabled unless
  an OpenAI chat profile is configured and the user opts in for that individual supervisor run.

SQLite remains the zero-service development adapter. PostgreSQL/pgvector is the production
target; its runtime adapter and packaged migration are operational, with HNSW intentionally
deferred until exact-search latency is measured.

## Requirements

- Python 3.11+
- A local OpenAI-compatible chat endpoint (llama.cpp is the primary target)
- A local OpenAI-compatible embedding endpoint (Qwen3-Embedding-0.6B is the initial target from
  the design report)

The SQLite/local-provider core and TXT/Markdown/DOCX ingestion use only the Python standard
library. Text-PDF parsing and local OCR are separate optional installs.

## Open the workbench

The fastest workstation setup on Windows is:

```powershell
.\scripts\setup.ps1
.venv\Scripts\python -m agenticrag serve
```

The browser opens at `http://127.0.0.1:8787`. Configure chat and embedding models from the Models
view; those selections stay in process memory, while non-secret preferences stay in browser local
storage. The Capabilities view reports the exact tools, skills, agent policy, and plugin status the
backend exposes—never a frontend approximation.

For an isolated container launch:

```powershell
docker compose up --build -d
```

See [workbench and model deployment](docs/deployment.md) for runtime-specific endpoints,
container-to-host networking, structured-output compatibility, and security boundaries.

Create an environment and install the project in editable mode:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -e .
```

For PostgreSQL, install the explicit storage extra:

```powershell
.venv\Scripts\python -m pip install -e ".[postgres]"
```

For text PDFs, install `.[documents]` (pypdf). For layout/table extraction and scanned-PDF OCR,
install `.[docling]`, prefetch Docling's model artifacts, and set
`AGENTICRAG_DOCLING_ARTIFACTS_PATH` to that local directory. The Docling adapter explicitly
disables remote services and external plugins; it does not download artifacts as a fallback.

## Configure local inference

Copy the names from [`.env.example`](./.env.example) into your shell environment. The application
does not automatically load `.env` files and never searches for cloud credentials.

```powershell
$env:AGENTICRAG_LOCAL_CHAT_MODEL = "your-chat-model-id"
$env:AGENTICRAG_LOCAL_EMBEDDING_MODEL = "your-embedding-model-id"
$env:AGENTICRAG_LOCAL_CHAT_BASE_URL = "http://127.0.0.1:8080/v1"
$env:AGENTICRAG_LOCAL_EMBEDDING_BASE_URL = "http://127.0.0.1:8081/v1"
```

Local profiles reject non-loopback URLs. Run a configuration check without making a network call:

```powershell
python -m agenticrag doctor
```

## Choose a corpus store

SQLite is the default and uses `--db`. To use PostgreSQL, first install pgvector in the target
PostgreSQL server, then configure the connection and immutable-object directory:

```powershell
$env:AGENTICRAG_STORE = "postgres"
$env:AGENTICRAG_POSTGRES_DSN = "postgresql://agenticrag@127.0.0.1/agenticrag"
$env:AGENTICRAG_OBJECTS_PATH = "D:\agenticrag-data\objects"
python -m agenticrag init-db
```

The DSN is read only from the environment and is never printed by `doctor`. `init-db` applies the
idempotent packaged migration, including `CREATE EXTENSION IF NOT EXISTS vector`; the database
role therefore needs the corresponding setup privilege on first use. Original source bytes stay
in the configured content-addressed local object directory. Parsed text, separate parsed-text and
provenance digests, parser identity/version, byte size, and chunk provenance are retained in the
metadata store.

## Ingest and ask

```powershell
python -m agenticrag --db .data/corpus.db init-db
python -m agenticrag --db .data/corpus.db ingest docs/handbook.md --collection private --scope owner
python -m agenticrag --db .data/corpus.db ingest scans/manual.pdf --collection private --scope owner --ocr auto
python -m agenticrag --db .data/corpus.db ask "What does the handbook say?" --collection private --scope owner
python -m agenticrag --db .data/corpus.db agent "Compare the documented limits" --collection private --scope owner --skill evidence-analysis
python -m agenticrag --db .data/corpus.db supervisor "Develop evidence-aware ad concepts" --collection private --scope owner --skill ad-creative
```

`--ocr auto` performs text extraction first and invokes OCR only for low-text pages when the fully
local Docling capability is installed and configured. `--ocr never` accepts text-only extraction;
`--ocr always` requires Docling. DOCX has no reliable page map in OOXML, so citations preserve its
section, element, table, and canonical offsets while leaving page fields null. `doctor` reports
each parser capability without making a network request.

## Skills, tools, and critical review

Project-native skills live under `.agenticrag/skills/<name>/SKILL.md`. With that default root, the
registry also discovers standard Agent Skills under `.agents/skills/<name>/SKILL.md`; every item is
shown with its source and SHA-256 digest. The repository currently includes the MIT-licensed
`ad-creative`, `ads`, and `copywriting` skills from `coreyhaines31/marketingskills`, alongside the
project's evidence-analysis and quantitative-check skills. Standard `metadata` frontmatter is
accepted but cannot grant tools or permissions. `--skill NAME` requires a particular skill, while
the planner may select additional skills from descriptions. Set `AGENTICRAG_SKILLS_PATH` or
`--skills-root` to replace the default roots with one explicit local root.

The base agent is intentionally read-only. Its gateway exposes hybrid `search`, authorized
bounded-span `lookup`, and an AST-validated arithmetic `calculate` tool. The fourth visible tool,
hosted `web_search`, is available only to the supervisor's web specialist when an OpenAI key is
already held in process memory and the user checks the per-run consent control. It uses the
Responses API with `store: false`, bounded tool calls, and returned source URLs. No workflow
exposes shell, filesystem writes, arbitrary Python, credentials, or mutation APIs.

The workflow adds useful deliberation—a plan of checkable obligations, gap-directed tool use,
stall detection, per-obligation evidence accounting, and a separate evidence critic—but the
quality ceiling still comes from the selected model. A strong local reasoning model can use this
harness in the same broad style as hosted coding/research agents; it should be evaluated rather
than assumed to match any particular OpenAI or Claude model. See
[`docs/agentic-workflow.md`](./docs/agentic-workflow.md).

Commands emit JSON so experiment runs can capture exact source, model, workflow, latency, and
failure information. Use `show-source SOURCE_VERSION_ID --scope owner` to resolve a citation.

For paired direct-versus-fixed-RAG runs, create a JSONL dataset:

```json
{"id":"atlas-001","question":"How much memory does Atlas have?","collection":"private","scopes":["owner"],"answerable":true,"required_chunk_ids":["chunk_..."],"expected_answer_contains":["64 GB"]}
```

Then run:

```powershell
python -m agenticrag --db .data/corpus.db compare cases.jsonl --runs .data/runs.jsonl
python -m agenticrag --db .data/corpus.db compare cases.jsonl --runs .data/agent-runs.jsonl --include-agent --skill evidence-analysis
python -m agenticrag summarize cases.jsonl --runs .data/runs.jsonl
```

The journal writes a `started` record before inference and a terminal record afterward, so an
interrupted run remains observable. Repeat the same frozen cases under different explicit provider
environments; workflow versions, sanitized provider labels, retrieval/agent/tool budgets, selected
skill names, results, and errors are preserved. `--include-agent` adds the bounded workflow to the
same cases rather than replacing the fixed baseline. See
[`docs/evaluation.md`](./docs/evaluation.md) for metric definitions and limits.

## Optional OpenAI comparison profile

Hosted inference is opt-in per role. It is never selected because a local server is unavailable.
For a cloud-chat/local-embedding comparison:

```powershell
$env:AGENTICRAG_CHAT_PROVIDER = "openai"
$env:AGENTICRAG_OPENAI_API_KEY = "..."
$env:AGENTICRAG_OPENAI_CHAT_MODEL = "an-explicit-model-id"
```

Embedding remains local unless `AGENTICRAG_EMBEDDING_PROVIDER=openai` is also set. Selecting an
OpenAI role without both its key and explicit model is a configuration error. Do not commit keys;
`.env` files are ignored.

Do not paste a key into chat or source files. Either enter it in the workbench's password field
(process memory only) or set it in the shell that launches the command. An explicit live check
makes a small billable model request; `--web-query` adds one billable hosted web-search call:

```powershell
$env:AGENTICRAG_CHAT_PROVIDER = "openai"
$env:AGENTICRAG_OPENAI_CHAT_MODEL = "your-enabled-model-id"
# Set AGENTICRAG_OPENAI_API_KEY in this private shell through your secret manager.
python -m agenticrag openai-check
python -m agenticrag openai-check --web-query "OpenAI Responses API current web search documentation"
```

The application reads `AGENTICRAG_OPENAI_API_KEY` but never prints it. In the UI, **Probe models**
validates authentication/model access and **Test agent contract** checks structured output,
bounded reasoning, and tool selection.

## Validate

```powershell
python -m unittest discover -s tests -v
```

The test suite covers immutable original/parsed versioning, multi-format validation and
provenance, collection and scope isolation, hybrid fusion, skill validation, safe tool execution,
bounded agent termination and evidence review,
retrieved prompt-injection handling, citation validation, termination, provider no-fallback
behavior, PostgreSQL SQL contracts, object integrity, durable manifests, and metrics. A live
PostgreSQL/pgvector round trip is enabled only when `AGENTICRAG_TEST_POSTGRES_DSN` is set.

## Architecture and next milestones

See [`docs/architecture.md`](./docs/architecture.md) for contracts and trust boundaries and
[`docs/roadmap.md`](./docs/roadmap.md) for the PDF-aligned implementation sequence. The next major
slice is reranking, adjacent-section expansion, and empirical qualification of the fixed and
bounded-agent baselines.
