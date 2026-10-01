# Chat and web simplification — 2026-09-30

## Decision

The requested priority is ordinary chat completion with reliable web evidence. Autonomous agents, supervisor, tool calling, Deep research, model routing, source-count budgets, and model-based relevance/claim reviews have been removed from the executable app and UI. Existing chats, sources, project notes, and provider selections retain their data paths. Old reports remain historical conversation data.

File count itself was not the main latency cause: modules and documents sitting on disk do not each add a model call. The former research pipeline repeatedly invoked the local model. The supplied log contains 27 claim-support checks totaling approximately 588 seconds, in addition to source relevance checks and searches. Privacy rejections were also counted as provider failures, and the plan drifted into other leagues and teams with no championships.

## Current request path

1. Web Off performs ordinary conversation completion with optional saved preferences.
2. Web Ask shows the exact user-derived query and waits for consent. Web On remembers permission per project.
3. One public query discovers results. The free DDGS adapter consults at most DuckDuckGo and Brave instead of its entire automatic engine pool. The historical environment setting remains `duckduckgo` for compatibility; the app correctly calls it Public web search. SearXNG and authenticated Brave Search are configuration alternatives.
4. At most four distinct HTTPS pages are read concurrently. Failed reads are disclosed and excluded. If none are readable, the app produces no sourced answer.
5. Canonical text is saved and indexed lexically, without loading an embedding model. Pages share a 24,000-character context budget, allowing up to 12,000 contiguous characters from one page so a compact historical table can fit. Partial excerpts are explicitly labeled in the prompt.
6. The selected model performs one ordinary completion, streamed immediately. It receives no callable tools or planning schema.
7. Numbered citations open immutable snapshots and highlight the exact text supplied. Save to library keeps a page beyond retention.

The web prompt excludes private file retrieval, project notes, and earlier assistant reports. Only user-authored topic context may contribute to a short follow-up query. This removes the recipe/example contamination observed in the basketball report. Search snippets discover URLs but are not answer evidence.

## Page extraction and model adapters

HTML extraction preserves table rows, cell separators, and bold emphasis, which can distinguish winners from other columns. The previous extraction flattened those distinctions and allowed winner/loser inversions. A live check also exposed `sticky-header` table classes being mistaken for navigation; the extractor now retains those tables. It now removes navigation/footer chrome without mistaking Wikipedia's root feature classes for a footer. Unicode paths and query parameters are encoded before HTTP requests. Pages with too little actual text are rejected.

Search results are ordered before the read cap to favor an explicit topic domain; successful reads then favor compact complete text. The prompt requires preserving relationships, citing list rows, and stating coverage gaps. This is a deterministic heuristic and prompt guidance, not a semantic fact checker.

Ollama uses native chat streaming with a bounded 16K context, avoiding oversized default allocations and mandatory JSON output. Other local servers use ordinary Chat Completions streams. Hosted OpenAI uses Responses text events with storage disabled. Truncated/error streams remain incomplete; partial text is retained in history. Empty usage-only SSE frames are accepted.

## Verification

- **77 automated tests**, one optional PostgreSQL integration test skipped because no test database is configured. HTTP tests cover Web Off/Ask/On, durable consent, cancellation, source scope checks, Save to library, and rejection of removed agent settings.
- **Six installed local model variants** passed a recorded-page check for 2021 NBA Finals losing team, winning team, series score, and a linked citation:

| Model | Completion seconds | First token seconds |
|---|---:|---:|
| Gemma 4 12B MLX | 12.89 | 10.93 |
| GPT-OSS 20B | 11.17 | 9.12 |
| Qwen3 30B A3B instruct | 14.23 | 9.01 |
| Qwen3 30B A3B 32K variant | 5.39 | 0.11 |
| Llama 3.3 70B instruct | 119.37 | 86.9 |
| Llama 3.3 70B 16K variant | 32.36 | 0.26 |

These timings include model loading when necessary, but exclude search/page acquisition. Different warm states prevent a fair model-speed ranking. The 70B cold load remains a real latency cost. The final checker accepts explicitly labeled table columns as well as prose; its initial prose-only rule falsely rejected GPT-OSS's correct table without requiring another model call.

- A comprehensive recorded-page Qwen regression matched **80/80 winner/loser pairs** in an official NBA source, with a citation on every table row; completion took **37.47 seconds**, excluding search/page acquisition. The final installed live request also matched **80/80 pairs** and cited every row: **45.10 seconds end to end**, first streamed text at **13.00 seconds**, one completion after actual search/page reads and Web Ask consent. Earlier live requests exposed discarded tables, insufficient excerpt coverage, and relationship inversions; those failures drove the extraction, budgeting, ranking, and prompt changes. These checks verify faithful table records from that source, not universal truth or all accompanying prose. One final footnote still overstated completeness of a secondary excerpt; general semantic verification remains outside the fixed pipeline.
- A live bounded metasearch check returned eight results in 1.14 seconds. Provider speed and availability vary.
- Browser checks passed at **320, 390, 430, 768, and 1440 pixels**: no page overflow or composer-control overlap; Ask consent, streaming, wide tables, citation excerpts, source saving/opening, model page, remembered Web mode, and cancellation. Additional checks cover settings, notes, upload, model selection, Web Off, history restoration, and a reduced mobile viewport with simulated safe areas.
- These are Chrome browser viewport checks. Physical iPhone Safari, microphone permissions, and hosted API credentials were not tested live. Hosted protocol/error handling is tested with fixtures.

Evidence files are in the ignored `.data/web-chat-review/` directory. Reusable model checking is in `scripts/check_web_models.py`.

## Repository cleanup

Removed obsolete agent/research/routing/evaluation modules and associated tests, duplicate UI assets, obsolete plans, skill bundles, fixtures, examples, and generated build output. Retained storage/provider/parser code required by ordinary chat or existing data. Current design tokens and font licenses remain the visual authority.

Removed material has recovery copies outside the repository under `~/.local/share/agenticrag/backups/`, including `pre-web-chat-20260930.tar.gz` and `pre-web-chat-design-and-root.tar.gz`. The installed package, launch configuration, and databases are backed up before updating the service.

## Practical limits

The fixed four-page pipeline is not exhaustive research. Public search engines can rate-limit; pages can block access or require JavaScript. There is no automatic model retry chain. Socket timeouts and redirect limits bound individual exchanges rather than guaranteeing an exact request wall time. Models can still misread evidence; citations are inspection links, not proof that every claim is correct. OpenAI credentials and optional PostgreSQL need live checks in those environments.

## Deployment

The installed service and existing phone HTTPS endpoint both report 0.5.0 / asset 50. Installed browser checks at 390 and 1440 pixels loaded history and all four views without page errors, overflow, or agent controls.

Release 0.5.0 uses asset version 50 and the new Chat & Web shell. The local installed service is updated after database and package backups. The existing local and phone HTTPS addresses remain the access points. Reload the browser or reopen the installed phone app to fetch the new shell.
