# Web search integration review — 1 October 2026

## Recommendation

Use **Ollama Search as the first configured provider**, with local SearXNG, keyless Exa and DuckDuckGo as bounded fallbacks. Keep all chat inference local. The free Ollama tier is useful for ordinary chat, but the observed hourly request limit makes it unsuitable as the only provider for sustained use. The adapter uses the existing httpx dependency; it adds no agent loop, model call or SDK.

Jake approved trying this route and saved an Ollama key in the app. The first authenticated `/api/search/test` request succeeded in **616 ms**, with three results retained by the test endpoint. This is reachability evidence, not a reliability or answer-accuracy result. No key is printed in logs, recorded fixtures, reports or public settings responses.

The 25-case Ollama-only run supplied evidence in **7 of 24 searched turns**, then returned an explicit hourly usage-limit error. One captured response instructed the client to retry after **860 seconds**. The adapter now respects that deadline across messages and immediately proceeds to another provider during the cooldown. Changing the credential starts a separate limit state; restarting the app clears the in-memory cooldown. Successful individual queries are cached for 30 minutes, so overlapping planner queries reuse their exact results and provenance. Recording evaluations bypass those caches.

The complete free-chain baseline supplied evidence in **24/24 searched turns**, with first-answer-token P50 **6.25 s** / P90 **9.30 s**. Required-fact regex checks passed 92%, citation validity 100%, and lexical citation support averaged 0.886. Search decisions still scored **88.9%**, and manual inspection found fabricated historical details in the broad NBA answer. This establishes that the fallback route works, not that Phase 2 accuracy is complete. See the [baseline report](../server/evals/web/reports/2026-10-01-235558-qwen3-30b-a3b-instruct-2507-q4_K_M-live-keyword.md).

With SearXNG actually stopped and Ollama quota-limited, Exa supplied ten results in **0.90 s**; SearXNG was restored immediately afterward. The later generic prompt trial scored 100% search decisions, but incomplete answers still fail validation. Its one-question checks retrieved evidence with all five approved chat variants; some omitted the required score, and Llama's first token took 53 s. Provider access and answer quality are separate results. See the [Phase 2 report](PHASE-2-REPORT.md) for the per-model limitations and failed gates.

[Ollama's search guide](https://docs.ollama.com/capabilities/web-search) documents `POST https://ollama.com/api/web_search`, an account/API key requirement, query and max_results fields, and URL/title/content responses. [Ollama's announcement](https://ollama.com/blog/web-search) describes a free individual tier and higher paid limits. Exact current free-search quotas are not specified there. The broader [pricing page](https://ollama.com/pricing) describes cloud model credits; it is not an exact web-search quota contract. No subscription, credit purchase or cloud model inference was configured. Authentication/quota errors trigger fallback.

Ollama's documented search API does not expose a hard date-filter parameter. The adapter does not invent one; freshness-sensitive answers still require recent, timestamped evidence. The local planner and answer model are independent of the search API and still need accuracy evaluation.

## The three links Jake supplied

| Link | Evaluation | What we use |
|---|---|---|
| [LocalLLaMA thread](https://www.reddit.com/r/LocalLLaMA/comments/1bmmfqz/any_straightforward_way_to_allow_models_to_search/) | March 2024 discussion of LM Studio extensions, Open WebUI and manual URL retrieval. Useful discovery leads; its comments do not establish current reliability or API requirements | Follow the leads to maintained project documentation; avoid restoring LM Studio or adding an agent loop |
| [OpenAI web search](https://developers.openai.com/api/docs/guides/tools-web-search?api-mode=responses) | Useful reference for search actions, source annotations, domain/freshness controls and clickable citations. Hosted Responses search uses OpenAI models and is billed; it is not a free search endpoint for Ollama | Preserve source provenance and visible citations. Do not integrate the paid hosted tool into this free local-model build. [Pricing](https://developers.openai.com/api/docs/pricing) |
| [Hugging Face reply](https://discuss.huggingface.co/t/how-to-use-website-search-functionality-with-my-llm/135257/2) | Describes both host-driven retrieval and model function calling, and links a DuckDuckGo-based Ollama example. The whole thread was retrieved through its canonical URL after the direct reply URL failed in the research browser | Use the host-driven approach already in SPEC E1, which does not depend on every model supporting tool calls |

The forum posts are leads, not primary technical authorities. Implementation conclusions below use project-owned docs and source repositories.

## Candidates and fit

| Project/service | Free access/setup | Fit for this app | Decision |
|---|---|---|---|
| [Ollama Search](https://docs.ollama.com/capabilities/web-search), [Python client source](https://github.com/ollama/ollama-python) | Free account + API key; hourly usage limit observed, exact quota undocumented | Native REST response fits SearchResult and the existing stored-passage pipeline; chat inference stays local | Integrated as preferred configured provider, with Retry-After cooldown and independent free fallbacks |
| [Exa MCP](https://exa.ai/docs/get-started/exa-mcp), [source](https://github.com/exa-labs/exa-mcp-server) | Official keyless, rate-limited endpoint | Independent search source without a new installed service or SDK. One fixed search-only JSON-RPC request; disable generated summaries and expose no agent tools | Integrate as fallback. Actual NBA smoke: HTTP 200, relevant official NBA/reference results in 0.64s. Handles JSON/SSE and bounded payloads |
| [SearXNG](https://github.com/searxng/searxng), [search API](https://docs.searxng.org/dev/search_api.html) | Already installed locally; no account/key | Useful free metasearch. Availability still depends on upstream engines and this Mac's network/IP | Retain as fallback; exact engine provenance and recorded simultaneous outages matter |
| [Open WebUI](https://github.com/open-webui/open-webui), [troubleshooting](https://docs.openwebui.com/troubleshooting/web-search/) | Open source app with provider integrations | Helpful separation of search success, fetch success, query generation and model/tool limitations. Importing its entire app would duplicate our stack | Borrow design/diagnostic ideas, not its app or agent framework |
| [Vane, formerly Perplexica](https://github.com/ItzCrazyKns/Vane) | Separate answering app, SearXNG and model-provider integration | Shows retrieval and citation patterns; another complete app does not independently fix upstream rate limits | Reference only |
| [TinySearch](https://github.com/TinySuiteHQ/TinySearch) | DDGS or bundled SearXNG; local embedding/ranking stack | Original-text retrieval and bounded evidence are relevant. Same search backend risks; ONNX/server dependencies would need separate approval | Reference for selection/ranking; do not install another retrieval stack now |
| [Jina Reader](https://github.com/jina-ai/reader), [limits](https://jina.ai/reader/) | Basic URL reader access; hosted search/auth/rate limits need qualification | A page-reading fallback, distinct from a reliable free search provider. Self hosting adds a browser service; hosted reading moves page fetches off the Mac | Consider later only if recorded JS-only page failures justify it. Retain SSRF checks and exact read-text provenance |
| [OpenSERP](https://github.com/karust/openserp) | Self-hosted browser-rendered SERP service; no per-search API key | Interesting independent implementation, but adds another service/browser and still relies on upstream engines | Reserve candidate if current qualified providers cannot meet latency/reliability; installation needs SPEC C1 approval |
| [ollama-internet-search-tool](https://github.com/alby13/ollama-internet-search-tool) | Python example using DuckDuckGo and Ollama | Confirms retrieval→context→answer pattern; does not remove DuckDuckGo rate limiting | Example only; do not add it as a duplicate provider |

## Integration contract

- Only standalone planner queries go to search services. The conversation, private corpus and system prompt are not sent to a search provider.
- Search selection remains deterministic host code. Models receive numbered original passages and stream answers; the provider does not select our chat model or activate agents.
- Ollama Search is skipped without a key; 401/403/429 and request failures continue through the provider order. Ollama and Exa 429 responses establish a cooldown using Retry-After seconds (60 seconds if missing/invalid). Exa is keyless; quota, malformed tool responses, timeouts and oversized responses are failures, not successful empty searches.
- Exa's fixed advanced-search tool uses `enableSummary=false`. Returned text/highlights are stored as search snippets; page fetches still go through the original local SSRF-safe reader. It does not run Exa Agent.
- Free availability is measured, not promised. A second metasearch wrapper using the same failed engines is not an independent fallback.
- Existing Tailscale routing, port 8787 and launchd label stay unchanged. Account keys are stored on the Mac and redacted from normal API responses.

## Validation before Phase 3

1. Ollama-only and full-chain baselines are recorded. The supplemental six everyday questions each produced cited answers through fallback, but that run's lexical support averaged 0.777 and its latency was contended by another local benchmark; it is not a passing full quality gate.
2. Compare generic planner/answer refinements before promoting any prompt change. A later intent-first planner-only trial scores 96.3% and preserves the broad population, but that result does not establish answer correctness. Production prompts remain unchanged pending full evaluation.
3. Validate citations and actual facts separately: lexical overlap is not entailment and cannot excuse contradictory winners/losers.
4. Finish functioning keyword/hybrid A/B on the same recordings and verify the five approved model variants.
5. Exercise outages and usage limits, then physical phone behavior. Phase 3 is authorized only after Phase 2 validation.
