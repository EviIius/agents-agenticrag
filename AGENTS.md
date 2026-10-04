# AGENTS.md — rules for coding agents in this repo

The plan is docs/SPEC.md. Read it before changing anything. Work phase by phase and stop for review
at the end of each phase with the report template in SPEC §H4.

Commands: `make setup` · `make dev` · `make check` (lint, types, unit tests, contrast, API types) ·
`make e2e` (Playwright vs fake runtime) · `make record-fixtures` (needs the real runtimes) · `make eval-web` (Phase 2+).

Hard rules:
- Stack and dependencies per SPEC §C1 only. Ask before adding any.
- Port 8787, bind 127.0.0.1, launchd label and Tailscale config never change.
- No extra modes/agents/model calls. Allowed model calls: answer, search planner, title,
  transcript clean-up (TRANSCRIPTION-SPEC §6).
- Transcription runs the external engine at WORKBENCH_TRANSCRIBE_HOME as a subprocess. No new packages.
- Never commit, log or screenshot a real recording, its filename or transcript text.
- No topic-specific prompt rules. Prompt edits require eval reports (SPEC §E12).
- Never send sampling params the user didn't set. Never infer capabilities from model names.
- Streaming = SSE events + rAF batching. Never poll. Never append notices to message content.
- UI: shadcn primitives + SPEC §G4 components + §G2 tokens only. Every state on /design.
- Never touch legacy data files except read-only import.
- "Done" requires evidence: tests, screenshots, reports.

User clarification (1 Oct 2026): exclude `llama3.3:70b-instruct-q4_K_M` from the new app's picker;
keep `llama3.3:70b-workbench-16k` and the other four local chat model variants. Apply this as a
stored user preference, never as a model-name capability heuristic.

User amendment (1 Oct 2026): use Ollama only, and continue Phase 1 and Phase 2 in
sequence without intermediate approval stops; retain checkpoint/phase evidence and
reports. LM Studio and generic OpenAI adapters are outside the current build scope.

User approval (1 Oct 2026): install Docker Desktop and run local SearXNG. Web search
must use free providers; no Brave API subscription or key is required. Verify real
parameter payloads and rename, pin/unpin, Markdown/JSON export and delete actions.

User amendment (1 Oct 2026): research and refine free web search integrations;
prefer Ollama Search if live evidence supports it, with free fallbacks. The user
saved its account key in the app. Continue to Phase 3 after Phase 2 is validated;
retain phase reports and evidence. Existing httpx adapters need no added SDK.

**User amendment — 3 October 2026 (deployment and storage):** Keep the engine’s public source under `transcribe/` in the Workbench repo and run it as a subprocess. Model weights, actual config, glossary and interpreter selection are ignored by Git; deployment copies them inside the installed app at `~/.local/share/workbench/app/transcribe` to avoid Documents access restrictions. Source recordings remain outside the repo. Uploaded audio is temporary by default: remove Workbench’s copy after durable transcription, preserving transcript text, raw text, timestamps and metadata. Failed/cancelled audio remains retryable until cleared. Settings offers opt-in audio retention and bulk clearing of inactive audio without deleting outputs or chats. This supersedes TRANSCRIPTION-SPEC decisions 1 and 3 and §12’s separate deployment folder. Jake authorized removal of existing uploaded audio copies.

Completed transcript outputs are kept even when unsent; seven-day housekeeping removes only unfinished unsent attachments.

**User amendment — 3 October 2026 (VoiceOver):** Jake reports VoiceOver did not work and asked to defer it for this build. Record the reported failure as an unresolved accessibility limitation; VoiceOver is no longer a release-blocking Phase 3 acceptance gate. Do not claim VoiceOver support passed. Other phase evidence and phone checks remain applicable.

**User authorization — 4 October 2026 (Phase 4):** Proceed with the reviewed roadmap corrections and Phase 4, stopping after 4B and 4D for review. Use Atelier, Chat controls and Web search as display labels at 4D; retain internal Workbench identifiers and compact numbered citations. CSS motion only, no new dependencies or model calls. Small motion is at most 200 ms; large surfaces at most 320 ms. Motion lives in `web/src/styles/motion.css`, checked by `scripts/check_motion.py`. C1's send timing and draft rollback are an explicit behavior change requiring rejection, chat-switch and new-draft tests. Future phases, `sqlite-vec`, embedding model installation and a second runtime are not authorized by this amendment.
