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

**User authorization — 4 October 2026 (Phase 5):** Fix and verify the reported
Reduce motion › Always failure and missing app entrance using iPhone Mirroring,
then build `docs/next/PHASE-5-EVERYDAY-CHAT.md`. Presets, folders, document
attachments and automatic backups are in scope; this lifts the earlier non-goal
on folders. Stop for review after 5A, 5B and 5C. Document text and filenames follow
the recording privacy rule. No new packages or model calls. Later phases and
optional chat forking remain separately gated.

**User authorization — 4 October 2026 (4B review and 4C):** Jake asked Codex to verify the live Workbench and iPhone Mirroring, fix Markdown/JSON chat exports to use the cancellable format-selection/save/share flow already provided for recording outputs, then continue to 4C. Preparing a file may fetch the existing export endpoint; cancellation never starts a download or opens the native share sheet. Keep the chat export dialog available after save/share/download. Physical review observations by Codex must be labeled as such, not attributed to Jake. The 4D review stop remains in force.

**User clarification — 5 October 2026 (preset precedence):** Jake delegated the
conflict between exact preset-only sampling and the frozen model-default pipeline
to Codex ("Do what you think is best."). Preserve saved model defaults: a preset
overrides only the values it stores; unspecified values inherit the user's saved
model defaults, otherwise the runtime default. Empty presets add no sampling
values of their own. This refines P5-AC1; no provider/run pipeline change is needed.

**User acceptance and authorization — 5 October 2026 (5C and 6A):** Jake said
"5C is sufficient. Continue on." Record 5C as accepted without inventing individual
phone test results. Proceed to 6A transcript clean-up and glossary per
`docs/next/PHASE-6-TRANSCRIPTION-T2-AND-RUNTIMES.md`, stopping for review after 6A.
The optional second runtime, Library and Research remain separately gated. The
reported sidebar/other motion regression remains deferred at Jake's request.

**User clarification — 5 October 2026 (6A retry visibility):** Jake delegated the
conflict between hiding retry controls and the frozen T1 disabled-control behavior
to Codex ("Do what you think is best."). Preserve the visible disabled
"Transcribe again" entries after audio removal, with the re-upload explanation.
This refines the 6A plan's visibility note; unavailable audio still cannot retry.

**User acceptance — 5 October 2026 (6A):** Jake said “I confirmed it works.
Move on.” Close the 6A review stop, retaining source/evidence and the deferred
motion/accessibility limitations. The next phase's explicit gates remain: 6B
needs a named second runtime; 7-0 needs `sqlite-vec` approval and an embedding
model selection before installation or probe execution.

**User authorization — 5 October 2026 (7-0):** After Codex requested explicit
approval for `sqlite-vec` and the installed, runtime-reported embedding model
`qwen3-embedding:0.6b`, Jake said “go ahead.” Proceed with the Library probe
in `docs/next/PHASE-7-LIBRARY.md` §2 and stop for review after 7-0. Library
retrieval is in scope; this lifts the earlier RAG non-goal. Library text and
filenames follow the recording privacy rule. The future library answer prompt
in §5.3 requires frozen hashes and before/after evals for edits. Embedding calls
are distinct from chat model calls. Optional 6B is skipped; Ollama remains the
only runtime. Research is not authorized.

**User authorization — 5 October 2026 (7-0 interpreter remedy):** After the
extension-loading prerequisite failed, Jake said “go ahead” to preparing and
verifying an isolated uv-managed Python 3.14.7 environment while preserving
the current live runtime. Verify the approved extension and embedding probe
and existing app tests against the candidate. Keep the framework interpreter
and existing environments intact; do not alter the transcription interpreter.
An installed-app runtime switch is presented after candidate verification.

**7-0 environment closeout — 5 October 2026:** Both server environments now
use the verified uv-managed Python 3.14.7 build with extension-capable SQLite.
Their previous framework environments and installed manifests are preserved
under the private fallback path recorded in `artifacts/phase-7/candidate/promotion.json`.
The system/framework Python and transcription interpreter remain unchanged.
The full check/browser suites and actual installed/development probes passed.
Stop for 7-0 review before 7A. J7 eval targets remain unapproved until a later
explicit decision before 7B. Record the initial launchd activation failure and
successful recovery without claiming its cause was proven.
