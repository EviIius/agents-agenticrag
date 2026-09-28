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

### Access from another device

The workbench has a responsive phone layout, but this local deployment is still bound to `127.0.0.1`. Keep the app on loopback and reach it through a private network overlay or an authenticated TLS reverse proxy when you add remote access. The workbench does not currently provide user accounts, login, per-user collections, or CSRF protection for a public endpoint. Do not forward port 8787 directly to the internet. A remote deployment should add authentication and authorization at the edge, HTTPS, request-size limits, and a deliberate policy for which local files and model endpoints the remote user can reach. The model and corpus are on the Mac mini; a phone or laptop is only the browser client.

Conversation transcripts are stored locally in `workbench-chats.db` beside the corpus database.
They are available to every browser that can reach this single-user service, so authenticated
remote access is a prerequisite before sharing the workbench with another person. The UI can
reopen or delete saved chats; deleting a chat removes its transcript, not indexed source files.

### Private access with Tailscale Serve

For access from your own phone or laptop, install the [Tailscale macOS client](https://tailscale.com/docs/install/mac)
on the Mac mini and Tailscale on the other device, then sign both into the same tailnet. Complete
the macOS VPN permission prompt. With AgenticRAG still listening on `127.0.0.1:8787`, run:

```sh
tailscale serve --bg 8787
tailscale serve status
```

Open the HTTPS `.ts.net` address reported by `tailscale serve status` on your other device.
Tailscale Serve keeps this endpoint inside the tailnet; do not use Funnel, which can make an
endpoint public. The tailnet identity and access rules control who can reach this single-user
workbench. Anyone allowed to open it can read all projects and transcripts, so restrict access
to your own devices until the app has separate user accounts. If Serve asks you to enable HTTPS
or sign in, finish its browser flow first. Keep port 8787 bound to loopback.

If the standalone Mac app has not put `tailscale` on your shell path, use
`/Applications/Tailscale.app/Contents/MacOS/Tailscale` in place of `tailscale`.

To stop remote serving while retaining local access, run `tailscale serve --https=443 off` and
check `tailscale serve status`. See [Tailscale Serve](https://tailscale.com/docs/features/tailscale-serve)
for current syntax and access-control details.

### Projects, attachments, and web answers

Projects group a source collection and its saved chats. Search in the sidebar matches chat
titles and transcript text within the selected project. Grounded modes can search that project's
documents; they do not automatically read every other chat in the project. Direct mode receives
earlier turns from the current chat.

The chat **Attach** control accepts TXT, Markdown, DOCX, and PDF documents and indexes them in
the current project before asking a Fixed question. It also accepts PNG, JPEG, and WebP images up
to 8 MiB for a Direct question with a vision-capable Ollama model. Image bytes are not kept in the
saved transcript. Text PDFs work with `.[documents]`; scanned PDFs need the configured OCR
installation.

Install `.[web]` to enable the **Web search** switch with a local model. It searches external
services only when checked for a Direct or Supervisor question, passes bounded search excerpts
and text from up to two public HTTPS pages to the model, and displays source URLs. Page requests
pin a validated public IP, reject private destinations and redirects, and fall back to snippets
when a page is unavailable. Web text is untrusted and generated claims are not independently
verified. Hosted search has separate credential and opt-in gates below.

To populate a fresh default library with three original example documents, run
`python scripts/seed_sample_corpus.py` while the workbench is serving. The examples live in
`examples/sample-corpus` and use collection ID `research` with access label `private`.

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

Use `http://127.0.0.1:11434/v1`. The Ollama compatibility layer supports chat, streaming, JSON mode, tools, and reasoning controls. AgenticRAG disables Ollama reasoning for final answers so a small token budget does not yield an empty answer. For structured actions, it retries an empty JSON Schema response in `JSON object` mode. `JSON object` is also the conservative preset for models that do not reliably honor JSON Schema mode; switch to `Prompt only` for older or minimal servers.

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
