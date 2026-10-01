# Phase 1 checkpoint 1A report

## Summary

Implemented the native Ollama adapter, catalog/preferences, stored chats and independent streaming runs.
The runtime is selected by metadata; the excluded standard Llama is a saved preference.
Runs preserve partial output, resume by SSE replay, and close the provider stream on Stop.
This checkpoint was consolidated during Jake’s authorized Phase 1–2 continuation; no intermediate approval stop was required.
Checkpoint 1A is implemented, with physical iPhone evidence still pending.

## Done-when checklist

| Item | Status | Evidence |
|---|---|---|
| D-AC1: detection, picker and loaded state | Passed for amended Ollama scope | Recorded tags/show/ps fixtures; `test_ollama_adapter_replays_real_fixtures`; five real-model checks in `artifacts/phase-1/real-ollama.json` |
| D-AC2: first-token rendering and frames | Measured; see full report for frame limits | Chromium 101.0 ms and WebKit 61.1 ms in first-token JSON; 100 tok/s rAF measurements and compressed Chrome trace |
| D-AC3: thinking display, storage, history | Passed automated checks | `test_live_stream_history_reasoning_defaults_and_ftS`; eight think-split vectors; real native reasoning recordings |
| D-AC4: sampling only when explicit | Passed | Fake runtime request capture; real adapter fixture replay; model-default browser payload check |
| D-AC5: no total stream deadline, idle limit | Passed | Chromium completed 1,500 tokens at 10 tok/s; idle timeout after 60 s preserved partial text. The duplicate long/idle test is skipped on WebKit |
| D-AC6: Stop | Fake disconnect passed; real response closure recorded | Stop browser test; `test_cancel_queue_tab_disconnect_and_restart`; real stream closed after eight text deltas. No separate Ollama abort log marker was found |
| D-AC7: resume | Browser passed; physical phone pending | Closed browser tab/reopened after 20 s; exact stored text comparison. iPhone sleep/wake over Tailscale not performed |

## Changed files

- Server: `providers/{base,ollama,registry,thinktags}.py`, `runs/{manager,generate,context,titles}.py`, typed schemas, SQLite store and chat/connection/message/settings APIs.
- Web: live shell, typed API, SSE/rAF client, run store, composer and live thread.
- Tests/evidence: real runtime recordings, fake runtime, chat tests, first-token/frame outputs.
- Docs: SPEC/AGENTS amendments and this checkpoint.

## Deviations from SPEC.md

Ollama only and continuous Phase 1–2 work are direct user amendments. Historical LM Studio fixtures are preserved; no LM Studio adapter is active.

## Runtime observations

All five retained chat variants responded through Ollama. Gemma’s deliberately capped 64-token probe spent its budget thinking; an uncapped-default probe returned `Hello!`. That is not a load failure. GPT-OSS reports low/medium/high reasoning through metadata.

## Test output

See `artifacts/phase-2/check.txt` for current combined checks. Browser baseline: `artifacts/phase-1/e2e.txt`. Final full `make e2e`: `artifacts/phase-2/e2e-phase-final.txt`, 84 passed, 2 deliberate duplicate skips.

## Screenshots

`artifacts/phase-1/chat-{320,390,768,1440}-{light,dark}-fake-runtime.png`.

## Open questions for Jake

Physical iPhone keyboard and sleep/wake checks remain for the installed candidate. The rebuilt candidate has not replaced the installed 0.5 app.
