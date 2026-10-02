# Phase 2 report

## Summary

The bounded pipeline now supports authenticated Ollama Search, local SearXNG and keyless Exa, with DuckDuckGo last.
Jake's saved key works, but the free Ollama tier hit an hourly limit; cooldowns, query caching and independent free fallbacks are implemented.
The complete fallback-chain baseline supplied evidence for 24/24 searched turns, with first-token P50 6.25 s. A real SearXNG outage used Exa in 0.90 s.
**Phase 2 remains incomplete:** planner scope, comprehensive answer accuracy and the functioning ranking comparison still need work. Phase 3 is authorized after validation.

## Done-when checklist

| Item | Status | Evidence |
|---|---|---|
| E-AC1: correct cited NBA 2021 result | Passed latest Qwen baseline | Free-chain baseline correctly says Phoenix lost to Milwaukee, 4–2, with citations and no invented other-year rows. This does not validate the broad all-losses report |
| E-AC2: thanks skips search | Passed tested paths | Unit/browser checks and latest real baseline's `thanks` case |
| E-AC3: standalone follow-up | Passed latest Qwen live case | `nba-followup` in the 25-case SearXNG baseline passes with six sources |
| E-AC4: immediate activity/favicons/collapse | Implemented; dedicated timing assertion pending | Planning SSE event precedes metadata work; browser interaction checks and real screenshots |
| E-AC5: citation cards/exact passages | Passed unit/browser checks | Stored source passages, reload and normalization checks; real browser answer retains five sources |
| E-AC6: fallback and all-provider failure | Free fallback passed live; all-failed behavior passed automated checks | With Ollama rate-limited and SearXNG actually stopped, Exa returned 10 results in 904 ms. SearXNG was restored. Approved provider order supersedes reliance on challenged DDG alone |
| E-AC7: SSRF | Passed automated checks | Public-address/all-DNS validation, redirects, downgrade, ports, credentials, Unicode and size bounds in the 142-test server suite |
| E-AC8: eval targets + ranking A/B | Failed/pending | Latest production baseline: 18/25, 88.9% decisions (<90%). Experimental intent/evidence trial: 21/25, 100% decisions, but broad-list completeness and evidence gaps remain. Healthy keyword/hybrid A/B pending |
| E-AC9: live P50 ≤12s | Passed latest measured Qwen baseline | 24/24 searched turns have sources, P50 6.25s / P90 9.30s. Ollama alone supplied sources for only 7/24 turns before its hourly limit |
| E-AC10: injection ignored | Controlled real-model test passed; full replay pending | Earlier `2026-10-01-151103-…-offline-keyword` fixture supplies the PWNED attack. Latest live page does not exercise it and correctly fails this gate |
| Parameter controls | Passed real Qwen payload + browser checks | `live-controls.json`; temperature, top P/K, output cap, seed, context and system prompt reach Ollama; untouched sampling omitted |
| Chat actions | Passed tested paths | Rename, pin/unpin, Markdown/JSON export, delete/cancel and persistence on Chromium/WebKit at 390/1440; real API exports and deletion also checked |
| G5 web screens/Axe | Passed previously tested states | Prior full browser suite: citation cards/sources in phone/desktop themes, no serious/critical Axe findings. Physical iPhone remains pending |

## Changed files

- Server: free provider defaults in `app/db/settings.py`; SearXNG upstream failure handling in `app/search/providers.py`; focused provider tests.
- Search integration: Ollama bearer-key requests, keyless bounded Exa JSON-RPC, original-text snippets, Retry-After cooldowns across messages and 30-minute per-query caching. API provider types and credential redaction are updated; existing HTTP dependencies only.
- Settings/design: shared password field, Save/Remove behavior and saved/missing-key design states. Failed saves preserve entered text; successful saves clear it. Browser tests cover both mobile and desktop.
- Streaming: finished-run snapshots cannot be reattached by a stale active-run response. The full browser suite exposed this race; deterministic SSE regression tests and the affected browser checks now pass.
- Recording: public raw pages are retained as lossless gzip fixtures, with original-byte hashes. Existing uncompressed fixtures still replay. This reduces repository evidence size; it does not claim faster model inference.
  The 403 new raw page recordings occupy 27.6 MB compressed instead of 168.4 MB, with byte equality checked before removing the uncompressed copies. [Manifest](../artifacts/phase-2/raw-fixture-compression.json).
- Web: draft parameters survive closing/reopening settings before the first send; mobile settings scroll inside the drawer so Save/Reset remain accessible; history debounce preserves the list and open action menus. Fixture copy identifies the design preview.
- Tests/evals: `verify_live_controls.py`, `web/tests/parameters.spec.ts`, extended action checks, six supplemental cases, selectable free provider order, stricter query-scope checks and failure exit status. Generic planner/answer trials remain confined to the evaluator.
- Deployment/docs: Docker CLI tool path, pinned SearXNG compose/template, engine qualification notes, approval amendments and this report. Local SearXNG secret is ignored and not committed.
- Evidence: real request captures, raw public-page recordings, three evaluation reports, verified command logs and four real-runtime screenshots under `artifacts/phase-2/`.

## Deviations from SPEC.md

- Jake explicitly approved Docker Desktop installation and free provider qualification; SearXNG then DuckDuckGo is now the default, with no paid API key required.
- Jake subsequently approved trying Ollama Search and saved a free-account key. The new configured default order is Ollama → SearXNG → Exa → DuckDuckGo. Neither a paid subscription nor cloud chat inference is enabled.
- Production E4/E8 prompts remain verbatim SPEC prompts. Generic trial instructions have before/after evidence but are **not promoted** because they fail acceptance.
- The evaluator now actually uses the configured free provider chain instead of hardcoding DDG-only. It checks query scope and returns failure for failed supplemental/single cases as well as full sets.
- Earlier parser isolation remains: one native extraction worker avoids the recorded concurrent lxml crash while downloads remain concurrent. See previous evidence and commits.
- A development candidate is running temporarily on the existing localhost port for review. Production deployment, legacy import, PWA update flow and final bundle optimization remain Phase 3 work.

## Runtime observations

### Ollama account key and independent free fallback

The authenticated smoke test succeeded in **616 ms**. The full Ollama-only baseline later hit HTTP 429 with the service's explicit **hourly search request limit** and an observed `Retry-After: 860` seconds. Only **7/24** searched turns retained sources in that isolated run; 17 failed, so its apparently fast failed-turn latency is not an acceptable search result.

The adapter now remembers a quota deadline across messages in the current app process and skips requests until it expires. It starts a separate deadline when the key changes; restart clears the in-memory deadline. Successful individual queries are cached for 30 minutes alongside the existing full-query cache, with configuration/key hashes in cache identity. No credential is returned by normal settings/bootstrap responses, included in recorded public-page fixtures or printed in command logs.

The **complete free-chain production baseline** provided sources in **24/24** searched turns, with required-fact checks **92%**, citation validity **100%**, lexical support **0.886** and successful-web first-token P50/P90 **6.25/9.30 s**. Decisions remain **88.9%** and the broad NBA plan still narrows the requested population. Manual inspection also catches fabricated historical details that regex and lexical scores do not establish. [Report](../server/evals/web/reports/2026-10-01-235558-qwen3-30b-a3b-instruct-2507-q4_K_M-live-keyword.md).

The **generic intent/evidence trial** scored **21/25**, decisions **100%**, fact checks **92%**, citation validity **100%**, lexical support **0.877**, with evidence in **22/22** searched turns and P50/P90 **6.36/10.51 s**. The broad request's scope is preserved, but its answer omits required teams; the height lookup uses a different measurement than expected; the release answer supplies too few citations. A live page never received the controlled injection payload, so that gate correctly fails. Both prompts remain evaluator-only. This is a live before/after comparison with differing public web results, not a frozen ranking A/B. [Trial report](../server/evals/web/reports/2026-10-02-000327-qwen3-30b-a3b-instruct-2507-q4_K_M-live-keyword-intent-first-cited-evidence.md).

The supplemental six questions produced cited answers through fallback (**6/6 basic checks**), but lexical support **0.777** falls below the full-suite threshold. Its latency was measured while another real planner benchmark used the same runtime, so it is not a standalone latency gate. [Report](../server/evals/web/reports/2026-10-01-234939-qwen3-30b-a3b-instruct-2507-q4_K_M-live-keyword.md).

A separate **real outage** test stopped the local SearXNG container while Ollama was actually quota-limited. Exa returned **10 original-text search results in 904 ms**. The container was restored in the command's exit trap. [Outage capture](../artifacts/phase-2/free-search-live-outage.json). Exa's endpoint is free, keyless and rate-limited; no unlimited availability is promised.

The [integration review](WEB-SEARCH-OPTIONS-2026-10-01.md) evaluates all three supplied links and the maintained alternatives. The route keeps all five approved chat variants local and adds no SDK, agent tool loop or extra model call.

### Checks across the approved chat variants

Each additional variant ran the NBA 2021 question against real search and its own real local completion. Production's standard prompt retrieved evidence for Qwen 32K, Gemma and GPT-OSS; Llama 16K incorrectly skipped search. The generic intent/evidence trial retrieved evidence with all four additional variants, and the main Qwen baseline also retrieved it. These are one-question smoke checks, not five full accuracy evaluations.

| Variant | Observed result |
|---|---|
| Qwen 30B standard | Latest full baseline passes the cited 2021 case; broad-list accuracy still fails |
| Qwen 30B 32K | Standard answer lacked citations; experimental answer passes the 2021 case |
| Gemma 4 12B | Both paths cite the correct losing team but omit the required series score |
| GPT-OSS 20B | Correct cited result uses Unicode spacing/hyphens and, in the trial, the loser's 2–4 record. Literal golden regex checks initially reject those formats; typography is now normalized in the evaluator. A correctly labelled 2–4 record still differs from the golden 4–2 wording and needs semantic review |
| Llama 3.3 70B 16K | Standard planner skips search. The experimental planner retrieves evidence and cites the correct loser, but omits the series score; first answer token takes 53 s, much longer than the ~1 s search request |

See `eval-approved-models.txt`, `eval-approved-model-trials.txt` and their individual report JSONs. No model-name capability inference or forced sampling was added. These failures prevent claiming robust web answers across every model.

### Docker and free search

Docker Desktop 4.93.0 and engine 29.8.1 are running on the Mac. The tested SearXNG 2026.9.30 image is pinned by digest and binds only `127.0.0.1:8888`. The template retains Google CSE, Yahoo and Wikipedia, based on live engine provenance. DuckDuckGo/Qwant challenge responses, Bing connection failure and scraped Brave rate limiting are recorded.

The full production-prompt baseline initially completed all 24 searched turns with sources. After sustained baseline, supplemental and trial evaluations, Google CSE returned 429/suspension and Yahoo temporarily failed too; direct requests for all six everyday queries then returned HTTP 200 with zero results and engine errors. Yahoo subsequently recovered and supplied the real browser WWII answer. Free metasearch is working, but sustained availability remains unresolved. The adapter now distinguishes this outage from a legitimate empty result. No CAPTCHA bypass, paid key or private corpus is used.

The pinned Google CSE engine implements `week` as seven days; real freshness probes passed. Engine-specific behavior and actual `results[].engines` provenance matter more than an HTTP 200 alone. See `searxng-qualified.json` and `searxng-after-rate-limit.json`.

### Earlier real model accuracy and latency (historical)

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

- `make check`: [latest integration output](../artifacts/phase-2/check-search-integrations.txt); 151 Python tests, 35 Vitest checks, strict types, lint/format, 56 contrast pairs and API contract freshness pass. Providers/runs/search coverage remains above 80%.
- `make build`: [verified output](../artifacts/phase-2/build-verified.txt); passes. Large chunk warning and the Phase 3 bundle budget remain open.
- Focused Playwright run: [verified output](../artifacts/phase-2/e2e-controls-actions-verified.txt); **10 pass**, Chromium/WebKit, widths 390/1440. Saved parameters, actual fake-runtime payloads and chat actions are covered.
- Real control checks: [output](../artifacts/phase-2/live-controls.txt); seven checks pass against Ollama plus the real product database/API in isolated data.
- Real browser: [capture](../artifacts/phase-2/live-browser.json); complete answer, five SearXNG sources and no horizontal overflow.
- Ollama key controls: [HTTPS browser capture](../artifacts/phase-2/ollama-key-controls-browser.json); fake-key route interception verifies saved state, failed-save retention, successful clearing and removal at desktop Chromium/mobile WebKit without modifying the real key.
- Full browser run: [output](../artifacts/phase-2/e2e-search-integrations.txt); **91 passed, 1 failed, 2 skipped**. The failure exposed a stale active-run race that restarted the reasoning display after completion. After the fix, [all 20 affected review/key checks pass](../artifacts/phase-2/e2e-search-recovery.txt) on Chromium/WebKit. The complete eight-minute suite was not rerun after that repair.
- Restored HTTPS preview: [capture](../artifacts/phase-2/ollama-search-active-browser.json); saved key is recognized, password input stays empty, no page errors or horizontal overflow at 390/1440. New built UI and backend provider/cooldown/cache changes are running at the unchanged route.
- Credential artifact check: [capture](../artifacts/phase-2/credential-leak-check.json); saved credential does not occur in changed source, reports or web recordings.
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

New saved-key settings, visually inspected: [desktop](../artifacts/phase-2/ollama-search-active-1440-chromium.png), [mobile](../artifacts/phase-2/ollama-search-active-390-webkit.png). The screenshots show an empty password field and an enabled Remove action, without exposing the key.

Earlier `*-fake-web.png` screenshots remain synthetic interaction evidence. Physical iPhone keyboard and scrolling are not yet verified; HTTPS routing is verified from this Mac.

## Open questions for Jake

Tailscale is reconnected. Review the actual preview on the physical phone, including the keyboard, settings scrolling and citation drawers. Docker installation and free-provider setup are already approved; no search subscription is requested.

Remaining implementation gates: promote a validated generic planner refinement, resolve factual/completeness failures across models, compare keyword against functioning hybrid ranking on the same recordings, and complete the full controlled-injection replay. Then complete physical phone review. Jake authorized continuing to Phase 3 after Phase 2 validation; the remaining failed gates currently prevent that transition. No additional key or search payment is needed.
