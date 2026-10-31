# Local model harness: M0.1 architecture audit

30 October 2026 · documentation only · `codex/harness-m0-1`

## Decision

The supplied plan is a useful direction, with substantial reuse and several
corrections required before implementation. Keep Aether's existing application,
native Ollama adapter, workflow engine and capacity controller. Add capabilities
one at a time, with evidence that they accomplish a useful task.

**Updated after Jake clarified the goal:** prioritize a conversational personal
assistant in the existing chat: search, open an allowed Mac app, read a selected
Apple Messages conversation and prepare a reply for approval. Jake selected
Apple Messages (iMessage and forwarded texts), then clarified that typed requests
should drive a reusable computer-use assistant across apps. Messages is the first
pilot; shared observe/act/verify tools are part of the initial architecture.
The concrete first scope is
[Assistant first](ASSISTANT-FIRST-PLAN.md). It supersedes this audit's initial
recording-folder-first recommendation; that useful automation remains later work.
A planner/grounder split should follow a measured need.

This is a recommendation for review, not implementation approval. The supplied
[plan](local-models-plan.md) is preserved byte for byte; this audit records its
corrections without silently rewriting the author's proposal.

## 1. Scope, source and evidence

- Audited production source: main
  `e7bab217f8738cd31803afb1d732ae51c8d51a1f`.
- Pending design work: draft [PR #13](https://github.com/EviIius/agents-agenticrag/pull/13),
  `codex/design-critique-b` at `02ea8711`. It is open, unmerged and outside this
  audit's implementation scope. Library navigation and greeting archiving in
  later critique checkpoints must not be described as shipped.
- Read-only host observations and installed-code preservation:
  [evidence](../artifacts/harness-m0-1-20261030/observations.json).
  No user database, recording, transcript, private photo or screen was inspected.
- Checked public upstream documentation as of 30 October; local compatibility
  and performance remain untested unless explicitly stated below.
- This checkpoint makes zero model calls and installs nothing. It changes only
  planning documentation and the scope note in AGENTS.md.

M0.1's technical map can be complete before Jake reviews it. The proposal's
acceptance condition, “Jake has read it and agrees,” remains pending.

## 2. Current architecture and conventions

### Runtime and application

Browser/PWA → Tailscale Serve → one FastAPI/uvicorn process on
`127.0.0.1:8787` → native Ollama or supervised local media subprocesses.

| Concern | Actual implementation | Consequence for the proposal |
| --- | --- | --- |
| Server | Python 3.14.7 installed; package requires Python ≥3.12. FastAPI, Pydantic v2, httpx, aiosqlite, sse-starlette. [Factory](../server/app/main.py), [lock](../server/uv.lock). | Reuse the existing validation, async HTTP and lifecycle. A new agent framework is unnecessary for a fixed pipeline. |
| Frontend | React 19, strict TypeScript, Vite, Tailwind, shadcn/Radix, Zustand, React Query; lazy workflow builder uses approved `@xyflow/react`. [Manifest](../web/package.json). | Extend existing screens and primitives; cover every new state on `/design`. |
| Chat transport | [Native Ollama](../server/app/providers/ollama.py), selected by [Registry](../server/app/providers/registry.py). Images are base64 message fields; schemas use native `format`; reasoning and keep-alive use the same payload builder. | Image-input plumbing and structured JSON transport already exist. An arbitrary OpenAI-compatible server does **not** plug in today. |
| Provider contract | [ChatRequest/Adapter](../server/app/providers/base.py) and runtime-reported [ModelInfo](../server/app/schemas.py). Tool-call fields are reserved; the ordinary payload builder does not implement the experimental tool loop. | New tool exposure, action formats and role requirements need explicit contracts. Names are selection identifiers, never capability evidence. |
| Workflow contracts | Strict Pydantic graph/config models, canonical hashes, immutable snapshots, typed template variables and model selections. [Graph](../server/app/workflows/graph.py), [definitions](../server/app/workflows/defs.py). | Map new fixed tasks into this system before inventing another workflow framework. |
| Execution | [GraphRunner](../server/app/workflows/engine.py), [block performers](../server/app/workflows/blocks.py), [shared text requests](../server/app/workflows/text.py). | Already supports ordered execution, user-authored prompts, review/edit pauses, choices, attempts, cancellation and retry/reuse. These are not general desktop-action permissions. |
| Media engines | [Images](../server/app/images/engine.py) and [transcription](../server/app/transcribe/engine.py) use supervised subprocess boundaries outside the chat adapter. | Preserve these boundaries. Share scheduling across engines rather than force every media operation through `Adapter.stream`. |
| Persistence | One private SQLite WAL database; transactional raw SQL and ordered migrations. [Store](../server/app/db/core.py). | Reuse records/ownership rules; design only the missing schema additions. No migration is added here. |
| Deployment | GUI LaunchAgent `dev.agenticrag.workbench`; fixed installed entry path under `~/.local/share/workbench/app`, one worker. | Bind, service identity and Tailscale route remain fixed. A GUI session is necessary but is not proof of screen-control permissions. |

Locked server versions include Pydantic **2.13.5**, FastAPI **0.142.2**, httpx
**0.28.1**, and sqlite-vec **0.1.9**. These are inspected lock values, not a request
to upgrade. Live Ollama reports **0.35.0**.

### Queues, priority and cancellation

[Capacity](../server/app/capacity.py) already grants a single managed native lease
and optionally holds a cross-process file lock. It prefers interactive requests,
then admits waiting background work after three interactive admissions. This
prevents background starvation. It does **not** implement “chat always first.”

Workflow text passes `background=True`; transcription and image execution use
the shared capacity boundary. Library embedding and some utility paths use
their existing adapter/connection admission. A new role must declare its priority
explicitly; do not assume every current utility request is background work.

The shared native controller is attached to Ollama/transcription when the image
worker is configured; otherwise the existing connection semaphores remain.
Preserve this conditional wiring when designing a capability independent of images.

The queue is in memory; it is not itself a durable task scheduler. Workflows and
image jobs persist their accepted work separately. Releasing between background
calls avoids holding a lease for an entire multi-step task, but one inference can
still take minutes. No bounded chat-wait promise is credible without a measured
maximum step time, all contenders and a declared fairness rule.

Stop must cancel queued work and terminate or await running inference. For a
subprocess, retain the lease until the child is reaped, following the existing
image engine. A phone disconnect is not cancellation. Future speech services or
desktop drivers must establish their own execution/termination acknowledgement;
an HTTP connection closing is insufficient evidence.

### Runs, streaming and recovery

| Run type | What persists | Restart/reconnect behavior |
| --- | --- | --- |
| Chat | Message snapshots, model/usage/source data | Chat SSE event history is in memory. Reconnect can replay while that process lives; startup marks active replies interrupted. It cannot continue the same token stream after restart. |
| Workflows | Definitions, snapshots, inputs, steps, attempts, source pins and event journal | Migrations [010](../server/app/db/migrations/010_workflows.sql), [011](../server/app/db/migrations/011_workflow_graphs.sql), [012](../server/app/db/migrations/012_workflow_run_modes.sql) already exist. Queued safe work can be rescheduled; unfinished running blocks become interrupted for explicit retry, preserving complete work. |
| Images | Jobs, progress/state, output/export files, reference bindings | Recovery reconciles outputs and interrupts uncertain execution. Migration [013](../server/app/db/migrations/013_chat_images.sql) adds image chat turns and [014](../server/app/db/migrations/014_image_references.sql) references. |
| Transcription | Attachment/transcript metadata, raw and cleaned text, timestamps | Completed outputs persist before temporary audio removal. Unfinished work becomes interrupted, not silently retranscribed. |

Chat uses [SSE with event IDs](../server/app/api/runs.py) and browser
[requestAnimationFrame batching](../web/src/lib/sse.ts). Workflow and media
events use their existing SSE paths. Future step/approval views should extend
these contracts and generated API types. Do not poll run status or append
control messages to generated answer text.

### Config, storage, secrets and logging

- Deployment configuration uses `WORKBENCH_*` through
  [Settings](../server/app/config.py). Product preferences live in SQLite through
  [settings](../server/app/db/settings.py). There are no twelve-model-role config
  entries or seven new flags today. Add the minimum roles needed by the first
  capability; retain explicit model choice, operational context and unset sampling.
- Production data lives in `~/.local/share/workbench/data`, **not** repo `.data/`.
  Use `Settings.data_dir` and a private subdirectory for future artifacts; do not
  move current attachments or DB files into the repository.
- Search account keys are stored privately in SQLite and removed from public
  settings responses, replaced with presence booleans. They are not established
  as encrypted-at-rest secrets. New DataHub tokens need a similarly explicit
  server-only design, not flags or URLs carrying tokens. No secrets were read here.
- Current host/origin/CSP/optional Tailscale-owner checks are in
  [security.py](../server/app/security.py). They protect HTTP access; they do not
  authorize desktop actions or DataHub writes.
- [Daily backups](../server/app/backup.py) already include companion image and
  reference handling. New screenshot/run artifacts require declared retention,
  pins, deletion, disk accounting and restore coverage; a SQLite row alone does
  not back up its file.
- Operational logs must not contain recording filenames, transcript text,
  private document contents or private screens. The existing
  [privacy audit](../scripts/privacy_audit.py) is a partial pattern check, not
  proof that screenshots are safe. This audit retained no screens or audio.
- “Never save fixtures” and “save real output fixtures” conflict in the proposal.
  Keep original historical evidence; future synthetic/public fixtures may be
  committed under existing rules. Private captures and real clips stay private,
  with consent and explicit retention. An opt-in test environment variable does
  not grant model-call or real-data authorization.

### Development and QA

- [Makefile](../Makefile): `make setup` prepares dependencies, `make dev` runs
  Vite, and `make build` produces static assets. None was needed for this audit.
  Do not run the development server on occupied production port 8787.
- `make check` covers Ruff lint/format, mypy, pytest/coverage, token contrast,
  generated OpenAPI types/additive compatibility, motion and built-glass guards,
  privacy, TypeScript, ESLint, Prettier and frontend unit tests. Follow the current
  Makefile rather than copying an older test command from a report.
- `make e2e` uses [Playwright](../web/playwright.config.ts), one worker and
  synthetic runtime/app data, in desktop Chromium and iPhone-sized WebKit.
  Fake runtime 18080, fake app's configured isolated port and Vite 5173 are test
  services. These browser checks do not establish physical iPhone behavior.
- `make record-fixtures`, `make eval-web` and `make eval-library` can invoke real
  runtimes. Web fixture replay still uses real model calls; only an explicitly
  fake run is model-free. Existing runners and frozen reports must remain intact.
  New native experiments need a pinned request budget, synthetic/public inputs,
  stop conditions and separate retained results, even if integration is opt-in.
- Read-only source inspection is not a full regression pass. This checkpoint
  runs only three existing fake/CPU checks relevant to disputed queue/payload/
  admission claims, plus documentation/privacy/preservation verification.

## 3. What already exists and what is missing

| Proposed capability | Existing pieces to reuse | Missing work / current boundary |
| --- | --- | --- |
| M0 shared core | Config, Pydantic, vision transport, schemas, capacity/fairness, durable workflow attempts/events, review pauses, cancellation, backups | Capability flags, role requirements, action-specific approvals and new artifact contracts. Avoid rebuilding the existing run engine. |
| 1 Computer use | Vision attachment path, provider schema support, media job supervision patterns, PWA SSE views | No production `computer_task`, screen driver, coordinate adapter, desktop permissions or computer task suite. Driver installation and model trials require named scopes. |
| 2 Planner/grounder split | Explicit per-block model choice and bounded step boundaries | No qualified split planner, grounder or verifier. Each adds calls, memory and latency. Compare one model first, then split only on a demonstrated gap. |
| 3 Brindle Hollow | SQLite/SSE patterns and background capacity are reusable | No town module/prototype was located in this tree. Do not pretend the eight-resident source was reviewed. Needs the actual prototype, ownership/repo decision, event budget and standalone-service boundary. |
| 4 DataHub metadata | Typed outputs, local-only private workflows, review UI patterns | No DataHub SDK, client, credentials, live version or integration was established. Start with public schemas and draft-only output; real lab access and writes are separate. |
| 5 Transcript cleanup | Manual guarded cleanup, private engine glossary, deterministic alias corrections, Whisper vocabulary hints, raw transcript retention, meeting-pack template | Per-edit review, structured edits, evidence-linked notes and glossary suggestions are additions. Do not replace the glossary with a new YAML system or add fuzzy/phonetic packages by default. |
| 6 Phone voice | Upload/transcribe path, phone composer, local chat and stop controls | No push-to-talk assistant, TTS playback queue or mlx-audio service. Keep long-recording transcription intact; qualify a small warm voice round trip separately. |
| 7 Evals | Web, Library, everyday-model suites plus preserved Research/reliability experiments | No single unified eval UI/database or grounding/VM suite. Add an adapter/index over existing formats before rewriting them. Fakes validate plumbing, not model quality. |

### Phase 9 and automation: direct answer

**Partly implemented foundations; automatic workflow triggers are not shipped.**
Migration 010 and later graph/run schemas exist. The manual meeting-pack and
brief-to-images workflows execute through the real durable engine. Search,
Library search, classify, read-document, condition and compose blocks are still
unavailable in the production block catalogue; annotations are UI-only.

There is no app-level calendar trigger, batch trigger or recording-folder
acceptance ledger. The legacy public transcription engine does contain a
standalone [folder watcher](../transcribe/localtranscribe/watcher.py) and launchd
helper. Its presence does not establish it is enabled, routed through Aether's
capacity controller, or suitable for copying into the app. Reuse file-settling
ideas after review; do not enable that service as a shortcut around shared capacity,
private logging or recording retention.

### Transcript overlap: direct answer

The private engine already implements an alias glossary (`correct = variants`),
longest-first bounded matching and vocabulary hints in
[glossary.py](../transcribe/localtranscribe/glossary.py), used by the Whisper
adapter. The app's [GlossaryFile](../server/app/transcribe/glossary.py) accesses
the engine-reported private path and writes atomically. Manual
[Cleanups](../server/app/transcribe/cleanup.py) chunks the text, preserves the
original and rejects excessive changes under the approved fixed contract.

Project 5 should extend these mechanisms. An `original` substring check prevents
applying an edit to the wrong text; it does not make the replacement correct.
Likewise, finding a quote does not establish that its owner, due date or claimed
decision follows from it. Add semantic review and abstention tests. Fuzzy and
phonetic suggestions should require review before becoming deterministic aliases.

### Existing agent experiments: direct answer

Hermes, PydanticAI and native-loop work is preserved on separate branches, not
registered in this production app. Native branch `376205a3` includes stopped N1
and a failed bounded citation retest. No N2/N3 or Research qualification follows.
The ordinary provider's reserved tool fields are not an active tool registry.

Reusing validated transport/control code later is possible; introducing computer
actions must not reopen failed factual-answer experiments or imply that a JSON
schema solves support, relevance or completeness. A new task needs its own
observable success checker and bounded trial.

## 4. Host and upstream fact check

### Observed host

Read-only checks report **Apple M5 Pro**, hardware `Mac17,16`, **68,719,476,736
bytes = 64 GiB RAM**. `df` reports a 1.8 TiB-class data volume and about 1.5 TiB
available; this is filesystem reporting, not a physical drive specification.
Ollama reports **0.35.0**, with **no model resident at observation time**. The
proposal's “daily model stays loaded” is a future policy, not current reality.
No model was loaded to verify it.

The production listener is PID **77443** on loopback port **8787**. Its installed
Python path is stable and the plist is in `~/Library/LaunchAgents`. Accessibility,
Screen Recording, display scaling/headless resolution, microphone routing and
permission survival across deploy/rollback were not exercised. Do not trigger
permission prompts or capture the real desktop during this docs-only milestone.

### External claims

| Claim | Assessment from primary sources | Required correction / next gate |
| --- | --- | --- |
| Holo4 27B/35B-A3B exist; OSWorld 2.0 figures 61.7/30.9 | Confirmed publisher figures, specifically **scores**, with success rates 41.5/12.3 and publisher harness conditions. [H release](https://hcompany.ai/newsroom/holo4). | Do not label the scores task success rates, or transfer them to quantized local execution. No Mac latency/accuracy ranking is established. |
| Holo4 licensing differs by variant | The [27B card](https://huggingface.co/Hcompany/Holo4-27B) lists CC BY-NC 4.0; [35B-A3B](https://huggingface.co/Hcompany/Holo4-35B-A3B) lists Apache 2.0. | Keep exact checkpoint/license in a future candidate plan. The 35B variant is a plausible permissively licensed candidate, not a qualified default. |
| Holo3.1-9B exists | [Publisher card](https://huggingface.co/Hcompany/Holo-3.1-9B) lists a multimodal checkpoint and Apache 2.0. | Local transport/template/coordinate behavior still needs exact-version fixtures and a trial. |
| Hosted H features imply local schema/reasoning behavior | Not established. The supplied H full-text docs URL could not be retrieved in this audit. | Verify the pinned local template/runtime, schema support, reasoning and tool parse with recorded outputs before action execution. No fallback runtime is implicitly approved. |
| Cua Driver and Lume provide appropriate interfaces | [Official repository](https://github.com/trycua/cua) documents Driver and Apple Silicon VMs; Driver background input depends on app/platform support. | Prefer a pinned driver's minimal interface over another agent framework. Installation, permissions, licence inventory and local performance remain separate checks. |
| A host driver controls a VM as a second screen | Needs correction. [Cua's VM guide](https://cua.ai/docs/cua-driver/guides/vms-and-remote) runs the driver **inside the guest** and transports requests to it. | Use an explicit guest target and per-guest grants. Do not route host coordinates into the VM or grant the guest host data/credentials by default. |
| Coordinate conventions can be inferred from the base family | Too broad. [UI-TARS coordinate guide](https://raw.githubusercontent.com/bytedance/UI-TARS/main/README_coordinates.md) maps through the actual smart-resized dimensions. | Pin each model's prompt/parser convention and transform: crop offset, resized dimensions, display origin and scale. Test corners, out-of-range values, 1×/2× and multiple displays; no blanket Retina=2 assumption. |
| mlx-audio offers speech endpoints | [Upstream server](https://github.com/Blaizzy/mlx-audio/blob/main/mlx_audio/server.py) defines speech and transcription routes plus execution management. | It is a separate managed engine, not a drop-in implementation of Aether's chat Adapter. Require pinned dependencies, formats, cancellation, lease/residency and phone audio tests. |
| DataHub supports source-attributed field documentation | Confirmed in [versioned 1.7 documentation](https://archive.docs.datahub.com/docs/1.7.0/generated/metamodel/entities/schemafield). The supplied latest-doc URL failed retrieval. | Confirm the actual lab version/SDK. Read current aspects, merge only owned entries, and test concurrent human edits, tags/terms and write idempotency. A full-aspect replacement can otherwise overwrite other entries. |
| Roughly 40 GB loaded weights is a sufficient budget | Not established by this host inspection or the proposed weight estimates. | Include context cache, vision processing, media workspaces, VM RAM and OS headroom; qualify actual combinations with memory/swap, cancellation and chat responsiveness. Keep existing image guards. |
| Voice can answer within 2 seconds | An unmeasured target, not an available service guarantee. | Separate queue wait, warm/cold load, STT, model TTFT and TTS. Report median/p95 and contention. Do not force sampling/thinking changes to achieve the target. |

These links support the narrow claims in the table; no remote software or model
was executed or downloaded. Weight sizes, candidate rankings, local throughput,
all driver actions and simultaneous model residency remain unqualified.

## 5. Corrections required before feature code

1. **Keep Ollama-only chat.** The current native adapter is deliberate. Adding
   llama.cpp, LM Studio, vLLM or hosted inference needs its own decision and
   compatibility scope. Speech/image engines retain their subprocess interfaces.
2. **Reuse capacity and run records.** Do not add another generic run engine or
   replace fairness with strict chat priority. First map new invocation types,
   durable inputs, leases, recovery, storage and expected maximum waiting time.
3. **No universal retry.** The proposal's “retry once” adds model calls and may
   replay side effects. Predeclare each capability's total call/time budget,
   count invalid requests/retries/verifiers, and stop on the declared failures.
   Never silently repair answers or replay a write of uncertain outcome.
4. **Approve an exact operation.** A generic click/type allowlist is insufficient:
   Enter can submit a message and a coordinate can change meaning after approval.
   Bind approval to run/step, target/guest, action arguments and observed state;
   expire it on change and consume it once. An ambiguous submit/delete is refused
   or needs fresh explicit review. Host policy, not model risk labels, decides.
5. **Keep evidence private and bounded.** Use `Settings.data_dir`, pins/retention
   and restore manifests. Do not commit private screen captures or speech clips.
   Keep prior failures/reports; do not move or delete historical evidence to
   implement the proposal's new storage preference.
6. **Separate output validity from usefulness.** Valid JSON, cited text, a quote,
   a changed screen or an LLM confidence score is not a task-success proof. Use
   independent checkers, negative controls, held-out tasks and human review.
7. **Keep optional complexity optional.** Town services, twelve roles, a unified
   eval dashboard, model judges, fine-tuning, cloud fallback and a split planner
   need not precede the first useful task. Expand after measurements justify it.

## 6. Recommended sequence and concrete next milestone

| Order | Scope | Review evidence before progressing |
| --- | --- | --- |
| 0 — now | Finish this M0.1 map and review the pending Part B UI candidate independently. | Accurate source map, explicit deviations, read-only host facts and unchanged production. No forced Part B merge to do planning. |
| 1 | Reusable computer-use contracts: typed task → observe → propose → authorize → act → verify in the current chat. Apple Messages is the first pilot. | [AS0](ASSISTANT-FIRST-PLAN.md): fake driver in two apps, coordinate/state binding, approval and Stop tests before native execution. |
| 2 | Shared driver preflight, then a bounded real trial: open one app, search public information, read one selected test conversation and draft a reply. | Verify actual transcript access, recipient identity, shared observations, local-only requests, budgets and outputs. No send in this trial. |
| 3 | Explicit Send/Edit/Cancel in chat; then phone push-to-talk. | One-time exact recipient/text approval, changed-thread invalidation, uncertain-send handling and phone checks. Separate native-send and speech scopes. |
| 4 | Prove reuse in Notes/browser, then separately scope VM-backed tasks. | Same desktop driver and task controller; add structured adapters where useful. Pin dependencies/model and validate task success before expanding the allowlist. |
| 5 | Compare single model against planner/grounder **only when needed**. | Matched screens/tasks, equal call/time/resource budgets, failure accounting and repeated results; sign-off before changing defaults. |
| 6 | Recording-folder automation, transcript edit review, DataHub drafts then reviewed writes. | Reuse the [folder pilot](AUTOMATION-FOLDER-PILOT-PLAN.md); keep per-capability quality, permissions, retention and restart gates. |
| 7 | Brindle Hollow as its own optional application/service. | Actual prototype supplied; bounded inference budget, shared admission API, independent state/backups and 72-hour synthetic soak with chat contention measurements. |

The original audit recommended recording-folder automation first because it
reuses the workflow engine. Jake's subsequent clarification makes conversational
app actions the immediate goal. This revision changes the recommendation while
retaining the source audit and its permission/quality boundaries. The subsequent
clarification makes reusable computer-use tooling part of the first architecture
milestone, with narrowly qualified app access beginning in Messages.

## 7. Remaining decisions and limits

- The assistant target and Apple Messages selection are now explicit. Review the
  concrete AS0/AS1 scope in `ASSISTANT-FIRST-PLAN.md` before implementation.
- Messages transcript access is not established by the app's send-capable scripting
  dictionary. Test one selected conversation through a reviewed bridge first.
- General computer use still needs a named driver/dependency scope, first app allowlist,
  trial model/runtime/checkpoint and explicit local-call allowance.
- DataHub version/location, real-work-data permission and the town prototype/repo
  remain unknown; do not guess or inspect private project folders to fill them.
- No screen permissions, real desktop, VM, audio playback or physical iPhone
  test occurred. No performance improvement or new model qualification is claimed.

See the [M0.1 report](HARNESS-M0-1-REPORT.md) for verification and the review stop.
