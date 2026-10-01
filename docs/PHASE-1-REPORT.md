# Phase 1 report

## Summary

The rebuilt app now supports native Ollama chat, reasoning, SSE resume/cancel, branches, attachments, model settings and searchable chat history.
The five approved chat variants were checked on the real runtime; the excluded standard Llama remains hidden as a stored preference.
The desktop and phone UI uses the specified tokens and primitives, with compact composer controls and a separate scrolling thread. Export-all, confirmed deletion and About details are implemented; import remains Phase 3.
Saved appearance, utility-model selection and model defaults persist on the Mac; automatic titles no longer block follow-up messages.
**Phase 1 is implemented but not accepted as complete: physical iPhone checks and the remaining screen/error evidence are pending.**

## Done-when checklist

| Item | Status | Evidence |
|---|---|---|
| D-AC1: detect/add/picker/status | Passed for Ollama amendment | Catalog/detection unit checks, recorded metadata and real five-model probes; no active LM Studio connection path |
| D-AC2: first-token/render performance | First-token passed; frame measurements recorded | 101.0 ms Chromium / 61.1 ms WebKit; `100 tokens/s render frame trace`; compressed Chrome Performance trace. Frame summaries retain outliers; median alone is not proof of uninterrupted 60 fps |
| D-AC3: thinking stored, shown and excluded from history | Passed | `test_live_stream_history_reasoning_defaults_and_ftS`, Appendix B vectors, native reasoning captures |
| D-AC4: no implicit sampling | Passed | Adapter request captures; browser preference test checks only explicitly saved temperature appears |
| D-AC5: long/idle stream | Passed | Chromium: 150-second stream completes; 70-second scripted idle interval produces 60-second timeout with partial answer preserved (the duplicate real-time gate is skipped on WebKit) |
| D-AC6: Stop | Fake passed; real transport closure recorded | Both browser engines record fake runtime disconnect; real adapter stream closed after eight deltas. Runtime abort marker not independently captured |
| D-AC7: reopen/sleep resume | Browser passed; physical iPhone pending | Reopen after 20 seconds compares final content with database; Tailscale phone sleep/wake still unverified |
| D-AC8: branches | Passed server and browser checks | `test_branching_context_settings_and_preferences`; TypeScript tree tests; `branches and history actions` at 390/1440 in Chromium/WebKit, reload preserves the selected branch |
| D-AC9: history/context | Passed | Full-history and dropped-message unit tests; context meter; reasoning never reused as history |
| D-AC10: all exact error states | Partial evidence | Error mapping tests and `/design` states; all error actions wired. Complete browser reproduction of every C12 error still pending |
| D-AC11: images | Passed for amended Ollama scope | Recorded real Gemma image response; non-vision preflight refuses images; attachment/context tests |
| D-AC12: search and history operations | Passed API and browser checks | Assistant-only FTS match; pin/rename/export/delete API coverage; interactive pin/rename/current-branch JSON export/delete in both browsers and widths; export-all/type-DELETE/About flow in both engines |
| D-AC13: automatic title <5 seconds | Passed | `artifacts/phase-1/real-title.json`: Qwen title after answer in 139.9 ms; rename protection test; pending-title follow-up regression |
| D-AC14: iPhone/Tailscale | Browser emulation passed; physical phone pending | 320/390/768/1440 layouts, both themes; Chromium/WebKit no horizontal overflow or thread/composer overlap. Physical keyboard/transport checks not claimed |
| G5 screens, both themes, Axe | Partial evidence | Welcome detected/offline, new chat, picker, chat settings, reasoning, connection/model settings, provider errors and web screens attached. Physical keyboard and complete runtime-error walkthrough remain pending. Tested chat/source/card states have no serious/critical Axe findings |

## Changed files

- Server: Ollama provider and registry; store/CRUD APIs; context assembly; run manager/generation/titles; typed request/response/SSE contracts; attachment validation.
- Web: `LiveAppShell`, `LiveThread`, `Composer`, `ModelPicker`, history/actions/dialogs, chat/model/connection settings, API/SSE/tree helpers, preference sync and run/UI stores.
- Tests/scripts: `test_chat.py`, fake runtime, Playwright chat tests, shared API generation, coverage script and runtime recorder.
- Docs/evidence: checkpoint, this report, amended SPEC/AGENTS, `artifacts/phase-1/`.

## Deviations from SPEC.md

- Jake selected Ollama only and waived approval stops between Phases 1–2. LM Studio-specific acceptance checks are superseded.
- Sampling defaults remain runtime defaults. Test-only capped probes are identified in their recordings and do not become product defaults.
- No active agents, tool loops, Supervisor or mode picker. The future tool seam remains a protocol/search module boundary per Part F.
- Import, database backup at deployment and production installation remain Phase 3 work. Export-all includes every branch and source; delete-all cancels generators first, then deletes chat rows, search entries and owned attachment files. Legacy data was not modified.

## Runtime observations

Ollama 0.35.0 returned text on Qwen instruct, Qwen 32K, GPT-OSS, Gemma and Llama 16K. A capped Gemma probe used its allowance on reasoning; the subsequent uncapped-default probe answered normally. Capabilities, thinking choices and context limits come from tags/show/ps, not model names. The standard Llama was not loaded for these checks.

## Test output

Current combined `make check`: `artifacts/phase-2/check.txt` — 142 Python tests, 33 Vitest checks, strict mypy, Ruff, contrast, API types, TypeScript, ESLint, Prettier and Vitest passed.

Full browser run: `artifacts/phase-2/e2e-full.txt` — 58 passed, 2 skipped, 2 test-label failures (`stopped` versus specified `Stopped`). The corrected Stop cases and web regressions subsequently passed in `e2e-final-targeted.txt` (10 tests). Additional preference persistence passed in `artifacts/phase-1/e2e-preferences.txt` (2 tests). The UI/performance run is `artifacts/phase-2/e2e-final-ui.txt` (14 passed). The expanded final review is `artifacts/phase-2/e2e-review.txt` (32 passed): both browsers, phone/desktop themes, model picker, chat settings, connection/model Settings, mobile drawer, simulated keyboard and provider errors. Settings shortcuts close background drawers. Theme screenshot tests set the saved backend preference as well as local storage. `artifacts/phase-1/e2e-actions.txt` adds 6 passed branch/history and Data checks. New-chat suggestion chips insert a starter and focus the composer; web suggestion enables search. `/design` includes safe Data and first-run previews. The final full `make e2e` run (`artifacts/phase-2/e2e-phase-final.txt`) passes **84 tests**, with 2 deliberate skips: duplicate foundation screenshots and the long/idle gate on WebKit. Long/idle passed on Chromium; Stop and resume passed on both engines.

`make build` passed (`artifacts/phase-1/build.txt`). The current initial JS/CSS is about 225 KB gzip; Markdown remains a separate lazy chunk. The ≤200 KB initial-bundle performance target is a Phase 3 gate and is not yet passed.

## Screenshots

- Chat at 320/390/768/1440, light/dark: `artifacts/phase-1/chat-*-fake-runtime.png`.
- New chat, model picker, reasoning chat, chat settings, connection/model settings and provider errors: `artifacts/phase-1/{screen}-{390,1440}-{light,dark}-fake-runtime.png`.
- Phone sidebar and simulated keyboard screenshots are explicitly emulation evidence.
- Performance: first-token JSON, frame JSON and `streaming-chromium-trace.json.gz` (decompress to import into Chrome Performance).
- Updated living guide: `artifacts/phase-1/design-{390,768,1440}-{light,dark}-fake-runtime.png`. Historical Phase 0 images are preserved.
- Web/citation/source review screens are in `artifacts/phase-2/`.

## Open questions for Jake

No new model-selection question: the exclusion preference is already applied. Physical phone verification awaits an installed candidate. The current launchd/Tailscale service was restored after browser tests; it still serves the old 0.5 app.
