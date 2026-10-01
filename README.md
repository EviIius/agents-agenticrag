# Workbench

A local chat app being rebuilt from [docs/SPEC.md](docs/SPEC.md). Phase 0 provides the server foundation and a responsive fixture interface. Live chat is Phase 1; web search is Phase 2; migration and deployment are Phase 3.

## Develop

Requires Python ≥3.12, uv, Node ≥22.12 and npm. `scripts/tool-env.sh` also finds isolated build tools under `~/.local/share/workbench/tools` when available.

```sh
make setup
make dev
```

Open `http://127.0.0.1:5173` or `/design`. All answers and statistics in this preview are explicitly labelled **Fake runtime**. The current installed app remains on `127.0.0.1:8787` and its existing Tailscale address.

```sh
make build       # static output → server/app/static
make check       # server lint/types/tests, contrast, API contract, web types/format/tests
make e2e         # Chromium + WebKit, fixture runtime, accessibility and screenshots
make api-types   # regenerate from FastAPI's OpenAPI after schema changes
make fmt
```

`make dev-server` binds to `127.0.0.1:8787` with one worker. Stop the existing installed service before using it; the foundation does not replace that service. Development mode enables `/design`; production excludes it. The dev server's API proxy points to 8787, but Phase 0 fixture UI makes no API calls.

## Preservation

The previous app is preserved on branch `legacy/chat-web-0.5` and tag `legacy-0.5`; its source is under `legacy/` on this branch. Installed data is backed up separately. New database writes use `~/.local/share/workbench/data/workbench.db`; legacy data is never opened by the new server.

The standard `llama3.3:70b-instruct-q4_K_M` variant will be hidden through the stored model preference in Phase 1. The `llama3.3:70b-workbench-16k` variant and four other chat models will remain available. Model weights are preserved.
