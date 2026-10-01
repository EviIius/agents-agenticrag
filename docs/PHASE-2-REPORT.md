# Phase 2 report

## Summary

The bounded plan → search → fetch → rank → answer pipeline now runs against real Ollama and local free SearXNG search.
Docker Desktop is installed, SearXNG is running, and its tested image is pinned. Six everyday questions produced cited answers.
Parameter payloads and rename, pin/unpin, Markdown/JSON export and delete were verified; mobile drawer and saved-draft bugs were fixed.
**Phase 2 remains incomplete:** planner scope, NBA factual correctness, sustained free-provider reliability and the ranking comparison still need work.

## Done-when checklist

| Item | Status | Evidence |
|---|---|---|
| E-AC1: correct cited NBA 2021 result | Failed | Latest production-prompt live baseline contradicts itself about Bucks winning/losing and omits the series score; the generic trial corrects facts but drops citations |
| E-AC2: thanks skips search | Passed tested paths | Unit/browser checks and latest real baseline's `thanks` case |
| E-AC3: standalone follow-up | Passed latest Qwen live case | `nba-followup` in the 25-case SearXNG baseline passes with six sources |
| E-AC4: immediate activity/favicons/collapse | Implemented; dedicated timing assertion pending | Planning SSE event precedes metadata work; browser interaction checks and real screenshots |
| E-AC5: citation cards/exact passages | Passed unit/browser checks | Stored source passages, reload and normalization checks; real browser answer retains five sources |
| E-AC6: SearXNG→DDG and all-provider failure | Unit checks passed; live outage/fallback acceptance pending | SearXNG is running; HTTP 200 with no results and upstream failures now triggers fallback. Positive results survive another engine's failure |
| E-AC7: SSRF | Passed automated checks | Public-address/all-DNS validation, redirects, downgrade, ports, credentials, Unicode and size bounds in the 142-test server suite |
| E-AC8: eval targets + ranking A/B | Failed/pending | Production-prompt baseline: 19/25 cases, 88.9% decisions (<90%). Generic trial: 18/25. Healthy keyword/hybrid comparison pending |
| E-AC9: live P50 ≤12s | Passed latest measured Qwen baseline | 24/24 searched turns have sources, P50 6.80s / P90 10.23s. This does not establish availability after sustained requests |
| E-AC10: injection ignored | Controlled real-model test passed; full replay pending | Earlier `2026-10-01-151103-…-offline-keyword` fixture supplies the PWNED attack. Latest live page does not exercise it and correctly fails this gate |
| Parameter controls | Passed real Qwen payload + browser checks | `live-controls.json`; temperature, top P/K, output cap, seed, context and system prompt reach Ollama; untouched sampling omitted |
| Chat actions | Passed tested paths | Rename, pin/unpin, Markdown/JSON export, delete/cancel and persistence on Chromium/WebKit at 390/1440; real API exports and deletion also checked |
| G5 web screens/Axe | Passed previously tested states | Prior full browser suite: citation cards/sources in phone/desktop themes, no serious/critical Axe findings. Physical iPhone remains pending |

## Changed files

- Server: free provider defaults in `app/db/settings.py`; SearXNG upstream failure handling in `app/search/providers.py`; focused provider tests.
- Web: draft parameters survive closing/reopening settings before the first send; mobile settings scroll inside the drawer so Save/Reset remain accessible; history debounce preserves the list and open action menus. Fixture copy identifies the design preview.
- Tests/evals: `verify_live_controls.py`, `web/tests/parameters.spec.ts`, extended action checks, six supplemental cases, selectable free provider order, stricter query-scope checks and failure exit status. Generic planner/answer trials remain confined to the evaluator.
- Deployment/docs: Docker CLI tool path, pinned SearXNG compose/template, engine qualification notes, approval amendments and this report. Local SearXNG secret is ignored and not committed.
- Evidence: real request captures, raw public-page recordings, three evaluation reports, verified command logs and four real-runtime screenshots under `artifacts/phase-2/`.

## Deviations from SPEC.md

- Jake explicitly approved Docker Desktop installation and free provider qualification; SearXNG then DuckDuckGo is now the default, with no paid API key required.
- Production E4/E8 prompts remain verbatim SPEC prompts. Generic trial instructions have before/after evidence but are **not promoted** because they fail acceptance.
- The evaluator now actually uses the configured free provider chain instead of hardcoding DDG-only. It checks query scope and returns failure for failed supplemental/single cases as well as full sets.
- Earlier parser isolation remains: one native extraction worker avoids the recorded concurrent lxml crash while downloads remain concurrent. See previous evidence and commits.
- A development candidate is running temporarily on the existing localhost port for review. Production deployment, legacy import, PWA update flow and final bundle optimization remain Phase 3 work.

## Runtime observations

### Docker and free search

Docker Desktop 4.93.0 and engine 29.8.1 are running on the Mac. The tested SearXNG 2026.9.30 image is pinned by digest and binds only `127.0.0.1:8888`. The template retains Google CSE, Yahoo and Wikipedia, based on live engine provenance. DuckDuckGo/Qwant challenge responses, Bing connection failure and scraped Brave rate limiting are recorded.

The full production-prompt baseline initially completed all 24 searched turns with sources. After sustained baseline, supplemental and trial evaluations, Google CSE returned 429/suspension and Yahoo temporarily failed too; direct requests for all six everyday queries then returned HTTP 200 with zero results and engine errors. Yahoo subsequently recovered and supplied the real browser WWII answer. Free metasearch is working, but sustained availability remains unresolved. The adapter now distinguishes this outage from a legitimate empty result. No CAPTCHA bypass, paid key or private corpus is used.

The pinned Google CSE engine implements `week` as seven days; real freshness probes passed. Engine-specific behavior and actual `results[].engines` provenance matter more than an HTTP 200 alone. See `searxng-qualified.json` and `searxng-after-rate-limit.json`.

### Real model accuracy and latency

Production-prompt baseline: [25-case report](../server/evals/web/reports/2026-10-01-223339-qwen3-30b-a3b-instruct-2507-q4_K_M-live-keyword.md).
It passes 19/25 cases, search decisions 88.9%, required fact checks 92%, citation validity 100%, lexical support 0.8976; successful-web first token P50 6.80s / P90 10.23s with sources in 24/24 searched turns. The NBA all-losses planner still narrows the request to teams that never won championships. The NBA 2021 answer contradicts itself. Citation validity and lexical overlap do **not** prove factual correctness.

Supplemental everyday questions: [six-case report](../server/evals/web/reports/2026-10-01-223553-qwen3-30b-a3b-instruct-2507-q4_K_M-live-keyword.md).
WWII, ramen, current president, Charlotte restaurants, Raleigh temperature and burger meat each produced citations and passed the basic checks (6/6). First token P50 5.12s / P90 9.94s. The weather answer includes an observation time; the president answer states its US assumption. These checks are not exhaustive factual or restaurant-quality validation. Original question spelling is retained.

Generic trial: [before/after candidate report](../server/evals/web/reports/2026-10-01-224007-qwen3-30b-a3b-instruct-2507-q4_K_M-live-keyword-task-and-scope-v2-direct-and-consistent.md).
It passes 18/25 cases, decisions 88.9%, with sources in 22/22 searched turns and P50 5.94s. Some NBA facts improve, but citations and broader-scope answers still fail. It stays outside production.

Raw live recordings are retained separately in `fixtures/2026-10-01-{searxng,jake,scope-v2}`. Earlier DDG-only and embedding-timeout/hybrid reports remain historical failed evidence. A fair comparison against functioning hybrid ranking and real web checks on the other four approved models are still needed.

### Controls, preview and phone access

`live-controls.json` captures real native Ollama requests from an isolated test database. Sampling values are forwarded only when set, resets inherit model defaults, cleared defaults omit sampling, custom system text reaches the runtime, exports contain the conversation and deletion removes history entries. The test restores the originally loaded context afterward. Reasoning variants were not re-qualified against every model in this session.

The actual development UI is [http://127.0.0.1:5173/](http://127.0.0.1:5173/), backed by the new candidate on `127.0.0.1:8787`. A real WWII chat is retained for review. The approved five-model picker includes the 16K Llama variant and excludes the user-specified standard 70B variant. The `/design/chat/fixture` page remains a design demonstration.

The installed old package and launchd plist are unchanged. Its job is temporarily stopped while this preview occupies port 8787; the preview command's exit trap restores the existing `dev.agenticrag.workbench` job. No legacy data was imported or modified. Preview data lives in the new app's separate data directory. This is not the Phase 3 production deployment.

Tailscale initially reported `Stopped` and the hostname did not resolve. Jake reconnected it; it now reports `Running`, `Online: true`. The unchanged HTTPS route to `127.0.0.1:8787` serves the new health endpoint and UI with HTTP 200. Physical iPhone keyboard and scrolling still need Jake’s review. Routing, label and port configuration were not changed.

Open the actual preview on a phone connected to this tailnet: [Workbench](https://jakes-mac-mini.tailc4d343.ts.net/).

## Test output

- `make check`: [verified output](../artifacts/phase-2/check-verified.txt); 142 Python tests, 33 Vitest checks, strict types, lint/format, 56 contrast pairs and API contract freshness pass. Providers/runs/search coverage remains above 80%.
- `make build`: [verified output](../artifacts/phase-2/build-verified.txt); passes. Large chunk warning and the Phase 3 bundle budget remain open.
- Focused Playwright run: [verified output](../artifacts/phase-2/e2e-controls-actions-verified.txt); **10 pass**, Chromium/WebKit, widths 390/1440. Saved parameters, actual fake-runtime payloads and chat actions are covered.
- Real control checks: [output](../artifacts/phase-2/live-controls.txt); seven checks pass against Ollama plus the real product database/API in isolated data.
- Real browser: [capture](../artifacts/phase-2/live-browser.json); complete answer, five SearXNG sources and no horizontal overflow.
- HTTPS tailnet preview: [capture](../artifacts/phase-2/tailnet-preview.json); Chromium desktop and WebKit mobile load the actual retained answer through Tailscale, with no page errors/overflow and an uncovered settings Save action. This is browser emulation, not a physical iPhone test.
- Earlier full `make e2e`: `e2e-phase-final.txt` has 84 passes and two deliberate duplicate skips; the full suite was not rerun this session.
- Live evaluations: production baseline and trial exit 1 because acceptance fails; supplemental six-case run passes. Failures remain visible rather than counting fallback model answers as web evidence.

## Screenshots

Real Ollama + SearXNG screenshots, visually inspected:

- [Desktop chat, 1440](../artifacts/phase-2/live-chat-1440-real-ollama.png)
- [Mobile chat, 390](../artifacts/phase-2/live-chat-390-real-ollama.png)
- [Desktop parameters, 1440](../artifacts/phase-2/live-parameters-1440-real-ollama.png)
- [Mobile parameters, 390](../artifacts/phase-2/live-parameters-390-real-ollama.png)

HTTPS preview screenshots: `tailnet-chat-{1440-chromium,390-webkit}.png` and `tailnet-parameters-{1440-chromium,390-webkit}.png`.

Earlier `*-fake-web.png` screenshots remain synthetic interaction evidence. Physical iPhone keyboard and scrolling are not yet verified; HTTPS routing is verified from this Mac.

## Open questions for Jake

Tailscale is reconnected. Review the actual preview on the physical phone, including the keyboard, settings scrolling and citation drawers. Docker installation and free-provider setup are already approved; no search subscription is requested.

Remaining implementation gates: fix planner scope with passing generic before/after evidence, resolve factual/citation failures, qualify sustained free-search reliability, compare keyword against functioning hybrid ranking on the same recordings, and check real web behavior across all five approved models. Then complete physical phone review. Stop at Phase 2 review before Phase 3 deployment/import/hardening.
