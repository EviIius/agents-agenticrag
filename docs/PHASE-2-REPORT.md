# Phase 2 report

## Summary

The rebuilt app uses local Ollama chat with free Ollama Search → SearXNG → Exa → DuckDuckGo fallbacks.
Phone safe areas, keyboard positioning, switches, completed-answer persistence and model-picker search are repaired.
The current automated implementation checks pass, but repeated real-model answers still omit facts or misread numeric tables despite receiving the evidence.
**Phase 2 remains incomplete. Phase 3 awaits the accuracy gates in SPEC §E13; the working preview is available over the unchanged Tailscale route.**

## Done-when checklist

| Item | Status | Evidence |
|---|---|---|
| E-AC1: cited 2021 result, correct loser/opponent/4–2 | Latest live table passes semantic audit; earlier answers fail | Latest live table states Milwaukee 4 wins and Phoenix 2 wins with a citation. The evaluator originally rejected this equivalent format; the corrected assertions accept it and reject wrong counts/column labels. The latest offline keyword answer still omits essential facts/citations |
| E-AC2: thanks skips search | Passed current keyword replay/browser checks | Real planner decision, no search requests, skipped notice; request logs retained |
| E-AC3: standalone previous-year follow-up | Passed current keyword replay | `nba-followup` supplies its standalone query and a cited correct answer |
| E-AC4: immediate activity, favicon, collapse | Passed Chromium/WebKit | Measured below 300 ms in `activity-latency-*.json`; `web.spec.ts` checks favicon fallback and completion collapse |
| E-AC5: citation card/exact evidence/source panel | Passed interaction/storage checks | Sources persist across reload; cards and cited/not-cited/failed-page sections tested on phone/desktop in both themes. Citation validity is not proof of truth |
| E-AC6: provider fallback/all failed | Passed measured fallback + automated failure paths | Earlier real SearXNG outage reached Exa in 904 ms; all-provider failure returns an answer with a separate notice. The user-approved free chain supersedes the original DDG-specific requirement |
| E-AC7: SSRF | Passed | Private/all-DNS addresses, redirects, downgraded HTTP, ports, Unicode, payload bounds and credential URL tests |
| E-AC8: complete offline targets and ranking comparison | **Open: answer accuracy fails** | Both ranking reports are attached below. Latest keyword has 96% required facts and support 0.901, but uncited output and forbidden list entries fail the individual acceptance gates |
| E-AC9: live first-token P50 ≤12 seconds | Passed earlier measured live V6 | P50 6.31 s, P90 9.12 s, 22/22 searched turns have evidence. Latest live P50 6.39 s/P90 10.20 s; 22/22 searched turns have evidence |
| E-AC10: controlled injection ignored | Passed actual-model replay | The selected passage contains the controlled `PWNED` attack; the model does not obey it. A live page is not counted as an injection test |
| Sampling controls and chat actions | Passed covered paths | Real isolated API/native-payload checks plus browser rename, pin/unpin, exports, delete/cancel and persistence checks. Unset answer sampling is omitted |
| Phone/desktop panels | Passed browser emulation | 320/390/768/1440 widths, safe top/bottom insets, a panned visual viewport, reduced-height picker, compact switches and reachable Save/Close. Physical post-fix iPhone confirmation remains pending |
| Five approved models | Passed availability/smokes; full accuracy not established | All five are available. Four alternate-model cited NBA smoke checks pass; the 16K Llama variant takes 55.9 s to its first token. A full GPT-OSS comparison also has accuracy failures |

## Changed files

- `web/src/components/ui/switch.tsx`, `IconButton.tsx`, `drawer.tsx`, `sheet.tsx`, `web/src/styles/globals.css` and `ThemeProvider.tsx`: separate a 44 px switch hit target from its 32×18 px track; keep shell and panels within the visible viewport and safe areas; disable conflicting Vaul keyboard repositioning; use 16 px phone inputs to avoid Safari zoom.
- `LiveChatSettings.tsx`, `ChatSettingsPanel.tsx`, `SourcesSheet.tsx`, UI store and `ModelPicker.tsx`: one phone settings heading, pinned source header/close, mutually exclusive phone panels, scrollable picker list and reachable footer. Removing an empty outer command group fixes search hiding every model; the tablet popover respects available height.
- `useChatRun.ts` and regression tests: a late streaming chat GET cannot erase a terminal SSE answer or reattach a closed run. Rendering continues to use SSE and animation-frame batching.
- `server/app/search/chunk.py`: retain complete split tables, correct header repetition, attach short captions, ignore navigation-only sections and store headings as metadata rather than factless passages.
- `rank.py`: match regular English plurals, exclude zero lexical matches from lexical votes/source bonuses, and reduce dense bibliography-list relevance for factual requests. Reference queries retain those lists. No topical filters are used.
- `cache.py` and `pipeline.py`: recording/replay bypass cache reuse; recent-information requests refresh snapshots older than 30 minutes regardless of 1/7/30-day retention. Ordered fetch waves preserve provider priority and stop starting requests after the source cap.
- `planner.py`, `prompt.py`, SPEC §E4/E7/E8: generic intent classification and evidence V6. Comparison queries cover every requested property of each entity within three slots. No extra model call, answer sampling override or agent was added.
- `server/evals/web/`: raw-answer capture, stricter comprehensive-list checks, Unicode score normalization, corpus/plan replay metadata, prompt hashes, controlled injection qualification and isolated generic experiments. Discarded answer V7/V8 and named-cell table trials remain outside production.
- `server/tests/test_search.py`, browser/unit regressions, recorded public fixtures and the reports/screenshots linked below.

## Deviations from SPEC.md

Approved: Ollama-only runtime; five stored picker preferences; free provider order; continue Phase 3 after Phase 2 validation.

Evaluated generic refinements are recorded in SPEC: intent JSON replaces the planner's `search` field, mapped to the same internal boolean; comparison-query coverage, evidence V6, table assembly, heading/plural/bibliography ranking and recent cache reuse. Before/after reports include failures. These changes do **not** establish that the phase passes.

No dependencies, agents, extra modes, extra model calls, forced sampling defaults, legacy-data writes, production port/bind, launchd label or Tailscale changes were introduced. Test temperature settings are explicit test-chat inputs, not app defaults.

## Runtime observations

### What caused the reported failures

1. **Evidence loss:** the extractor fragmented tables. Captions crowded out data, headings consumed passage slots, reference lists displaced the result summary, and plural query terms missed singular facts. The fixes preserve the full 28-row example table; the latest result-table selection has zero bibliography passages versus two before.
2. **Incomplete queries:** four comparison properties were spread across a three-query limit, dropping one property's evidence. One query per entity now covers all requested properties without a further model call.
3. **Stale reuse:** a recent request could reuse a seven-day retained page. Retention now stays separate from a 30-minute reuse window.
4. **Model errors remain:** the supplied table distinguishes 23 positive-loss entries from five non-losing entries using dashes. Qwen sometimes omits final entries, reads dashes as one loss, or drops supported scores/citations. Named-cell table labels did not fix the comprehensive answer and were not promoted. Available sources and syntactically valid citations do not establish factual correctness.
5. **UI bugs were independent:** switch sizing, safe-area positioning and nested command filtering caused the phone/picker defects. A separate GET/SSE race could blank a completed answer.

### Real-model evaluation evidence

All answers use native sampling defaults. Recorded web freezes public provider results/pages, **not model outputs**. Source fixtures never run in production. Reports retain raw answers, selected passages, timings and prompt hashes.

| Run | Cases passed | Required facts | Forbidden cases | Uncited cases | Support | Web TTFT P50 / P90 |
|---|---:|---:|---:|---:|---:|---:|
| Original generic baseline, `012844` | 19/25 | 96% | See report | See report | 0.893 | Recorded web; older list checks |
| V6 + initial recall fixes, `144854` | 25/25 | 100% | 0 | 0 | 0.870 | 3.90 / 6.30 s |
| V6 live, `145756` | 21/25 | 84% | 0 | 0 | 0.891 | 6.31 / 9.12 s |
| Latest keyword + body ranking/query coverage, `155158` | 22/25 | 96% | 1 | 1 | 0.901 | 3.99 / 5.69 s |
| Same corpus, hybrid, `155637` | 21/25 | 92% | 1 | 0 | 0.838 | 6.74 / 11.82 s |
| Latest live production, `160515` | 23/25 | 96% | 1 | 0 | 0.916 | 6.39 / 10.20 s |

These are the scores originally recorded, before correcting equivalent-format grading. A [deterministic audit](../artifacts/phase-2/answer-format-regression-audit.json) of the saved answers now accepts the latest live 4-win/2-win table, yielding 25/25 required-fact checks. It also rejects listed non-losing teams regardless of an invented positive count. The comprehensive-list output remains forbidden in all three final comparisons; **none becomes an accepted phase**. Original report files remain unchanged with their original case hashes. Two new tests verify correct/wrong table scores and the stronger exclusion check.

Reports:

- [Baseline](../server/evals/web/reports/2026-10-02-012844-qwen3-30b-a3b-instruct-2507-q4_K_M-offline-keyword.md).
- [25-case V6 recorded pass](../server/evals/web/reports/2026-10-02-144854-qwen3-30b-a3b-instruct-2507-q4_K_M-offline-keyword-cited-evidence-v6.md).
- [V6 live failure](../server/evals/web/reports/2026-10-02-145756-qwen3-30b-a3b-instruct-2507-q4_K_M-live-keyword.md).
- [Latest live production](../server/evals/web/reports/2026-10-02-160515-qwen3-30b-a3b-instruct-2507-q4_K_M-live-keyword.md).
- [Latest keyword](../server/evals/web/reports/2026-10-02-155158-qwen3-30b-a3b-instruct-2507-q4_K_M-offline-keyword-entity-queries.md) and [functioning hybrid](../server/evals/web/reports/2026-10-02-155637-qwen3-30b-a3b-instruct-2507-q4_K_M-offline-hybrid-entity-queries.md).

**Default remains keyword.** The latest hybrid run actually uses embeddings on all 22 successful searched turns; none silently fall back. It adds embedding P50 2.73 s/P90 6.47 s without an accuracy improvement. Both runs share the recorded corpus; their planners execute independently, so query variation limits causal attribution. The earlier frozen-plan comparison (`135951` keyword versus `140319` hybrid) isolates plan variation: keyword P50 3.02 s versus hybrid 5.94 s; hybrid is used on 20 turns with two embedding timeouts. Both comparisons fail answer acceptance and remain visible.

The six original everyday questions pass their basic live checks (6/6, `142011`), with P50 6.02 s/P90 10.87 s. Their support average is only 0.693: these smoke checks do not validate every factual claim, restaurant recommendation or weather observation.

Additional model smokes: Qwen 32K 5.75 s, Gemma 8.04 s, GPT-OSS 5.46 s, 16K Llama 55.92 s (`141702`, `141731`, `141748`, `141910`). A full GPT-OSS run (`142945`) passes 20/25, with missing facts and retrieval gaps. These are not five full passing suites.

### Preview and storage

[Actual Workbench preview](https://jakes-mac-mini.tailc4d343.ts.net/) is served by the rebuilt backend and built UI at the original 127.0.0.1:8787 route. HTTPS health is 200, the picker has exactly five approved models, and the saved key remains write-only. Live browser checks filter to one model without overflow at 390/1440. This is a development preview; the installed launchd package/plist remains unchanged and the preview exit trap restores its existing job. Phase 3 deployment is pending.

Public raw recordings are gzip-compressed with original-byte SHA-256 manifests and decompression equality checks. The latest two 25-case recordings contain 241 compressed pages; the final production live recording adds 126 pages, compressed and byte-verified separately; earlier compressed recordings remain readable. Evidence files are not loaded by normal chat, so their presence does not cause inference latency. Legacy removal is a Phase 3 task, following the specified read-only import.

## Test output

- [Current `make check`](../artifacts/phase-2/check-phase2-current.txt): **163 Python tests**, **36 Vitest tests**, lint/format, strict types, API types and **56 contrast pairs** pass. Providers coverage 83.3%, runs 88.3%, search 87.6%.
- [Full browser suite](../artifacts/phase-2/e2e-final-current.txt): **106 passed, 2 deliberate duplicate skips**, Chromium/WebKit. It includes actions/parameters, stop/reconnect, long streams/timeouts, mobile panels and citation/source states in both themes.
- [Post-picker-fix focused suite](../artifacts/phase-2/e2e-panels-search-fixed.txt): **24 passed**, including the new reduced-viewport/filtering regression and all web interaction regressions. The earlier failing attempt is retained in `e2e-panels-ranking-final.txt`; it exposed the command-group bug.
- [Build](../artifacts/phase-2/build-current.txt): passes. Markdown lazy chunk is 938.90 kB raw / 287.94 kB gzip; the Phase 3 bundle budget remains open.
- [Real controls](../artifacts/phase-2/live-controls.json): explicit sampling/context/system values forwarded, unset parameters omitted; exports, deletion and model-default resets checked in isolated data.
- [Safe-area/keyboard measurements](../artifacts/phase-2/phone-safe-layout-check.txt) and [live picker filtering](../artifacts/phase-2/model-search-live.json): reachable controls, one matching model and no horizontal overflow.
- [Credential scan](../artifacts/phase-2/credential-leak-check-current.json): saved key absent from changed source, screenshots, reports and recordings; compressed page bytes are checked after decompression.
- Full real-model suites return a failing exit status when accuracy fails. They are not reported as successful implementation gates merely because provider requests succeeded.

## Screenshots

Visually inspected against the actual preview; safe-area/keyboard dimensions are simulated:

- [Phone settings](../artifacts/phase-2/settings-safe-390-live.png) and [reachable Save/footer](../artifacts/phase-2/settings-safe-footer-390-live.png).
- [Phone sidebar](../artifacts/phase-2/phone-safe-sidebar-live.png), [model picker](../artifacts/phase-2/model-safe-390-live.png) and [keyboard picker](../artifacts/phase-2/model-keyboard-safe-live.png).
- [Desktop settings](../artifacts/phase-2/settings-safe-1440-live.png) and [model picker](../artifacts/phase-2/model-safe-1440-live.png).
- Real model filtering: [phone](../artifacts/phase-2/model-search-390-live.png), [desktop](../artifacts/phase-2/model-search-1440-live.png).
- Browser fixtures explicitly labelled fake: `web-chat-{390,1440}-{light,dark}-fake-web.png`, `citation-card-…`, `sources-…`, and `panel-safe-{320,390,768,1440}-fake-runtime.png`. These prove interaction/layout, not model accuracy.

## Open questions for Jake

Post-fix physical iPhone review is still pending: keyboard, sidebar, settings Save/Close and citation/source drawers. The earlier eight photos were the before-fix evidence; browser emulation does not replace this confirmation.

No additional key, paid search subscription or Docker approval is needed. An optional isolated temperature comparison is ready, with a pending choice from Jake; AGENTS.md prohibits setting an unrequested sampling value. No lower-temperature answer has been sent and the app/model defaults are unchanged. The remaining Phase 2 gate is consistent answer accuracy, especially full numeric lists and essential result details. Extra model validators, agents or forced sampling would change the agreed design and have not been added to hide these failures. Phase 3 remains conditional on the accuracy acceptance checks.
