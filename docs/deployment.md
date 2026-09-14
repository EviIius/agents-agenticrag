# Workbench and local-model deployment

AgenticRAG 0.4 provides a zero-build web workbench and a versioned local HTTP API. The browser is a client of the same backend contracts used by the CLI: authorization scopes, immutable sources, provider selection, tool budgets, skill loading, delegation, and citation validation are not reimplemented in JavaScript.

## Workstation launch

Install and open the workbench:

```powershell
.\scripts\setup.ps1
.venv\Scripts\python -m agenticrag serve
```

On macOS or Linux:

```sh
./scripts/setup.sh
.venv/bin/python -m agenticrag serve
```

The default listener is `http://127.0.0.1:8787` and the command opens it in the system browser. Use `--no-open` for a headless session. Non-loopback binding is rejected unless `--allow-remote` is explicit; remote access should be terminated by a trusted, authenticated TLS reverse proxy.

## Container launch

```sh
docker compose up --build -d
```

Open `http://127.0.0.1:8787`. The published port is loopback-only, corpus data lives in the `agenticrag-data` volume, and project plus standard Agent Skills are mounted read-only. The container can reach a model server on the host through `host.docker.internal`; choose a runtime preset, replace `127.0.0.1` in its URL with `host.docker.internal`, and save the connection.

`AGENTICRAG_LOCAL_RUNTIME_HOSTS` is an explicit hostname allowlist for container and private-network topologies. It does not enable arbitrary remote inference. For a model sidecar on the same private Compose network, add its exact service name to this comma-separated allowlist.

## Runtime recipes

All integrations use the OpenAI-compatible surface. Chat and embeddings may use separate runtimes or separate models.

### LM Studio

Start the local server from the Developer tab or run:

```sh
lms server start
```

Use `http://127.0.0.1:1234/v1` for both roles. LM Studio documents OpenAI-compatible models, chat, responses, embeddings, and tool use. AgenticRAG still executes tools itself so access control and budgets remain host-owned.

### Ollama

```sh
ollama serve
```

Use `http://127.0.0.1:11434/v1`. The Ollama compatibility layer supports chat, streaming, JSON mode, tools, and reasoning controls. `JSON object` mode is the conservative AgenticRAG preset; switch to `Prompt only` if a particular model does not reliably honor JSON mode.

### llama.cpp

```sh
llama-server -m model.gguf --host 127.0.0.1 --port 8080 --jinja
```

Use `http://127.0.0.1:8080/v1` for chat. Run a separately pooled embedding model on another port, such as 8081. llama.cpp documents OpenAI-compatible chat, embeddings, schema-constrained JSON, and function calling. `--jinja` is relevant when exercising a model's native tool template, although AgenticRAG's current bounded agent emits validated action JSON instead of giving the runtime direct tool authority.

### vLLM

```sh
vllm serve <model> --host 127.0.0.1 --port 8000
```

Use `http://127.0.0.1:8000/v1`. For GPU container deployments, vLLM publishes an official `vllm/vllm-openai` image. Treat its API as an internal service: vLLM notes that its API-key option does not protect every endpoint, so expose it only behind a reverse proxy with a complete network policy.

## Structured-output compatibility

The chat role exposes three modes:

- `JSON Schema`: strongest constraint for runtimes and models that implement schema-constrained decoding.
- `JSON object`: asks the runtime for JSON mode and includes the exact schema in a trusted system instruction.
- `Prompt only`: sends the exact schema in the prompt without a provider-specific `response_format`; this is the broadest fallback for older or minimal OpenAI-compatible servers.

All three modes feed the same Python validation. A model cannot add tools, exceed the host budget, cite a chunk it did not retrieve, or bypass the final critic contract simply because it produced plausible JSON.

## Hosted OpenAI profile and key check

The **OpenAI (hosted, opt-in)** preset is the only interactive profile that may send a credential
off-device, and its destination is restricted to `https://api.openai.com/v1`. The API key remains
in backend process memory and is never returned by the API or written to browser storage. The UI
marks the profile as hosted and billable.

The web-search specialist uses `POST /responses` with `store: false`, one explicit `web_search`
tool, a hard tool-call bound, and included source URLs. It remains unavailable until the OpenAI
chat role is configured, Supervisor mode is active, and the user checks **Web search** for that
individual run. The local corpus and embedding roles do not switch providers automatically.

For a terminal smoke test, place the key into `AGENTICRAG_OPENAI_API_KEY` using a private shell or
secret manager, set the explicit chat model and provider, then run `python -m agenticrag
openai-check`. This performs a live billable structured-output request. Add `--web-query "..."`
only when you also intend to pay for and authorize a hosted web-search call.

## Operational checks

`GET /healthz` is a minimal process health check. The Models view probes the selected runtime's bounded `/v1/models` endpoint and reports latency and model identifiers. It never scans ports or discovers network services automatically.

The capability inspector is the source of truth for the current process:

- tools are compiled into a host-owned capability list; hosted web search reports unavailable until its explicit gates are satisfied;
- skills are direct child directories containing bounded `SKILL.md` files under the project root and, by default, `.agents/skills`;
- agents report their delegation and recursion policy, including runtime-dependent availability;
- plugins are deliberately empty until a plugin adapter and permission model are implemented.

This makes model intelligence compositional: stronger open-source models can plan better, but all models receive the same explicit capabilities and are held to the same execution and evidence contracts.
