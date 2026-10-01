# Chat & Web

A local chat app with public web search, streamed answers, and inspectable source snapshots.

## What it does

- One question box and your selected chat model.
- A compact Web control: **Off**, **Ask**, or **On**, saved per project.
- Web Off: normal conversation completion. Saved project preferences can be included.
- Web Ask: shows the exact search query and waits for permission.
- Web On: searches without another permission prompt.
- One search, up to four public page reads in parallel, then one completion.
- Numbered citations open the immutable text excerpt supplied to the model.
- **Save to library** keeps a page beyond the project's retention period.
- Chat history, projects, notes, local file storage, image input for supported models, and mobile installation.

Web answers do not search private files, load an embedding model, or include old assistant reports. Search snippets are used to discover pages; unreadable pages are excluded from answer context. A failed search is an error, not a fabricated web answer.

The Python package and existing data paths remain named `agenticrag` so existing installations and stored conversations continue to work.

## Run

```sh
./scripts/setup.sh
.venv/bin/python -m agenticrag serve
```

On Windows, run `scripts/setup.ps1`. Select a model under **Models**. Ollama, LM Studio, llama.cpp, local OpenAI compatible servers, and OpenAI Responses are supported. Hosted credentials are explicit; no provider or model is switched automatically.

Ollama requests use a bounded 16K context rather than the model's potentially very large default. A large model still needs time and memory to load. The header reports actual loaded state where the runtime exposes it.

## Search providers

Search is independent of the chat model:

```sh
AGENTICRAG_WEB_PROVIDER=duckduckgo
```

The existing `duckduckgo` setting now uses the installed `ddgs` package to consult at most DuckDuckGo and Brave. It is labeled Public web search in the app. This is one host query with up to two search engines; their HTTP timeouts are not a guaranteed total wall-time limit. Alternatives:

```sh
AGENTICRAG_WEB_PROVIDER=searxng
AGENTICRAG_SEARXNG_URL=https://your-search.example
```

```sh
AGENTICRAG_WEB_PROVIDER=brave
AGENTICRAG_BRAVE_API_KEY=your-key
```

A local SearXNG endpoint may use loopback HTTP. Public page reading uses HTTPS, checks and pins public DNS addresses, bounds response size, and rejects private addresses. JavaScript-only pages, access blocks, and unsupported document types are reported in **Search details**.

## Limits and accuracy

Four pages and bounded excerpts are a latency limit, not a promise of exhaustive research. For large lists, specify the league and date range. The answer should disclose missing coverage. Models can still misinterpret evidence; citations let you inspect the text, and do not certify every claim. A model that omits citations is labeled explicitly.

The app has no autonomous tool selection, research planning, multi-model routing, source-count budgets, or background report generation. Normal requests retain durable progress so reloading the app can show a request already in progress.

## Checks

```sh
.venv/bin/python -m unittest discover -s tests -p 'test_*.py'
```

See [architecture](docs/architecture.md), [deployment](docs/deployment.md), and [the implementation review](docs/WEB-CHAT-REVIEW-2026-09-30.md).
