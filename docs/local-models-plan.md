# Harness Build Plan: Local Model Capabilities

Oct 30, 2026 · @Jake Brulato

## How to use this plan

Codex builds the seven capabilities one milestone at a time, starting with a written map of the existing harness. Export this doc as Markdown, save it in the harness repo as `docs/local-models-plan.md`, and point to it from `AGENTS.md`.

Instructions for Codex:

1. **Map the harness before writing code (milestone M0.1).** Write `docs/harness-notes.md`: language and runtime, how tools are registered and called, how the agent loop and UI streaming work, config and secrets, logging, and how tests run. Then map each module in this plan onto those conventions. Paths and names in this plan are suggestions.
2. **One milestone per branch and PR, in the order under Build order.** Each PR ships code, tests, a demo command under `scripts/demos/`, and a short entry in the repo's changelog.
3. **Stop at the end of each milestone.** Summarize what works, what doesn't, and any deviation from this plan, then wait for review.
4. **The harness wins conflicts.** Where this plan clashes with how the harness already works, follow the harness and note the deviation in the PR. Don't refactor harness code beyond what a milestone needs.
5. **Off-Mac sandboxes.** If Codex runs in a Linux cloud sandbox, it can't exercise macOS screen control, MLX or audio. Build those parts behind interfaces with fakes, and skip macOS-only integration tests off-Mac.

Kickoff prompt:

```text
Read docs/local-models-plan.md. Complete milestone M0.1 only: write docs/harness-notes.md and map the plan onto the harness. Don't write feature code yet. Finish with a summary and a list of places where the plan doesn't fit the harness.
```

Prompt for each later milestone:

```text
Implement milestone <ID> from docs/local-models-plan.md. Follow the ground rules. Stop when its acceptance criteria pass, then summarize.
```

## Goals and scope

The harness (`agents-agenticrag`) gains seven local-model capabilities, each behind its own feature flag that defaults to off.

| # | Capability | What Jake gets |
| --- | --- | --- |
| 1 | Computer-use tool | Chat can hand off "do X in app Y" to a local vision model that operates macOS |
| 2 | Planner + grounder | One model plans each step in words; a small vision model finds where to click |
| 3 | Brindle Hollow engine | The town prototype runs 24/7 on local models with persistent memory |
| 4 | Metadata descriptions | Drafted column descriptions, tags and glossary terms for DataHub, written only after review |
| 5 | Transcript cleanup | Recordings come back with jargon fixed and action items pulled out |
| 6 | Voice assistant | Push-to-talk from the phone, spoken replies, same tools as chat |
| 7 | Personal evals | New models are scored on Jake's own tasks before they become a default |

Out of scope:

- Cloud model calls, unless a capability's config explicitly allows them.
- New chat modes or agents beyond what the approved `AGENTS.md` amendments list.
- Unattended computer use on the real desktop. Autonomous runs happen only in a sandbox VM.
- Real work data, until Jake decides it's allowed (see Ground rules).

## Ground rules

These rules apply to every milestone. A PR that breaks one isn't done.

1. **Amend before building.** `AGENTS.md` allows only a fixed set of model calls. Each project adds its calls through a written amendment and a `docs/next/PHASE-*.md` file that Jake approves before any feature code. Without the amendment, refuse the milestone.
2. **Flags default off.** Each capability gets its own flag, following the existing `WORKBENCH_*` pattern (for example `WORKBENCH_COMPUTER_USE`). With every flag off, the app behaves exactly as it does today.
3. **One model queue.** Every model call goes through `server/app/providers/` and the server's in-memory queue. Background work takes the queue one step at a time and releases it between steps, so a chat waits at most one step. No other process calls a model server directly.
4. **Code controls the flow.** Prefer fixed pipelines with schema-constrained outputs. Agent loops get hard caps on steps and time, and code checks each result before the next step.
5. **Models live in config.** No model names in code. Code asks for a role (`planner`, `grounder`, `stt_fast`), and config maps each role to a model and endpoint.
6. **Never execute model output.** Parse it into a whitelisted action or a JSON schema, validate it, and retry once with the validation error appended. Never `eval` or `exec` model text.
7. **Local only by default.** No calls to hosted model APIs unless a capability's config sets `allow_cloud: true`. Capabilities 4 and 5 can never set it.
8. **Side effects need approval.** Anything that changes state outside the harness goes through the Phase 0 approval layer. That covers clicks, typing, DataHub writes and sent messages.
9. **Records in the database, files in `.data/`.** Run records go in the database. Screenshots and audio go under `.data/`. Never commit them; the repo is already large.
10. **Work data stays out until Jake says otherwise.** Build and test with synthetic or public data. Whether real work data may be processed on this machine is Jake's call under his employer's policy. Either way, the code keeps that data local.
11. **Tests in every PR.** Unit tests use fakes: a fake model, a fake screen and fake audio. Tests that need macOS, a model server or audio run only when `RUN_LOCAL_INTEGRATION=1` is set.

## Target environment

Everything runs on Jake's Mac mini: M5 Pro, 64 GB unified memory, 2 TB storage. Codex confirms the details below in M0.1, because they come from Jake's earlier notes, not the repo.

- **Model serving.** Ollama is the current runtime. Any server with an OpenAI-compatible endpoint plugs into `providers/`: Ollama, llama.cpp's `llama-server`, LM Studio or vLLM. A vision model also needs image input support in whichever server hosts it. GGUF vision models need their projector (`mmproj`) file.
- **Memory budget.** Keep the models loaded at the same time under about 40 GB, leaving room for macOS, Docker and the server. The daily chat model stays loaded. Vision, speech and town models load on demand and unload after a `keep_alive` timeout. The 70B model is never loaded alongside a vision model.
- **macOS permissions.** Screen control needs Accessibility and Screen Recording grants for the process that takes screenshots and sends input. That process must run in Jake's logged-in GUI session, as a LaunchAgent rather than a LaunchDaemon. Grants attach to the executable, so confirm they survive a deploy and a rollback.
- **Display.** If the Mac mini runs without a monitor, check the resolution screenshots come back at. A dummy display plug or a fixed resolution keeps the screen size stable for grounding.
- **Phone.** The PWA is the main remote interface, so approvals, the Stop button and voice must all work there. The Mac mini has no built-in microphone, so voice input comes from the phone.
- **DataHub.** Project 4 targets Jake's DataHub home lab. Its server URL and token live in local config, never in the repo.

| Model | Role in this plan | Approx. memory at 4-bit |
| --- | --- | --- |
| Llama 3.3 70B | On-demand only | \~40 GB |
| Holo4-35B-A3B | Computer-use agent (fast) | \~20 GB |
| Daily chat model (Qwen 30B class) | Chat, planner candidate | \~18 GB |
| Holo4-27B | Computer-use agent, planner candidate | \~16 GB |
| Holo3.1-9B | Grounder candidate | \~6 GB |
| Parakeet 0.6B + Kokoro 82M | Speech in and out | \~2 GB |

Sizes are approximate weights only, before the context cache. Check real numbers with `ollama ps` after loading.

## Architecture overview

&#91;embedded content: harness architecture · shared core, 5 modules, 4 local services, town engine\]

Inside the server, the top row is the shared plumbing from Phase 0 and the bottom row holds the project modules. The town engine runs as its own service but sends every model call through the harness.

## Build order

&#91;embedded content: build order · Phase 0, then two tracks\]

Build the top track left to right. The bottom track can follow in any order, and any of it can move earlier; Project 5 is the smallest.

Order for Codex, one milestone per PR:

1. Phase 0: M0.1 to M0.5
2. Eval plumbing and grounding set: M7.1, M7.2
3. Project 1: M1.1 to M1.5
4. VM suite and model comparison: M7.3, M7.4
5. Project 2: M2.1 to M2.3
6. Project 5: M5.1 to M5.4
7. Project 6: M6.1 to M6.4
8. Project 4: M4.1 to M4.5
9. Project 3: M3.1 to M3.4

## Phase 0: Shared foundations

Phase 0 changes nothing Jake sees. It maps the harness, gets the rule amendments approved, and adds the pieces every project shares.

| Milestone | Delivers | Done when |
| --- | --- | --- |
| M0.1 Harness map | `docs/harness-notes.md`: architecture, conventions, and where each project plugs in. Confirms or corrects every fact in this plan. | Jake has read it and agrees with the mapping |
| M0.2 Rules and flags | An `AGENTS.md` amendment listing each new model call and trigger, a `docs/next/PHASE-*.md` per project, and one flag per capability, all off | Jake approves; every existing test suite passes with all flags off |
| M0.3 Roles and vision | Role-to-model config, image input through `providers/`, a health check per backend, and a budget check that refuses role sets over the memory limit | A screenshot sent to a configured vision model returns schema-valid JSON; the same path passes with a fake provider |
| M0.4 Run records | Tables for runs, steps and artifacts, files under `.data/runs/<run_id>/`, and a retention setting | A dummy three-step background job records its steps and a screenshot, shows in the UI, and is pruned on schedule |
| M0.5 Approvals and Stop | Risk tiers, allow and deny lists, an approval queue in the web UI and PWA, and a Stop button | A fake tier-2 action waits for a tap on the phone; a deny-listed target is refused; Stop ends a running job within one step |

What M0.1 must check:

- **Phase 9 status.** The October 8 plan proposed Phase 9, Automations: a background runner, run and step tables (migration 010), and a recording-to-notes pipeline. Record what exists. This plan reuses it wherever it does.
- **Queue priority.** Chat must always go first. If the queue has no priority today, add the smallest change that lets a waiting chat go before the next background step.
- **How the server is launched.** Screen control needs a process in Jake's GUI session (see Target environment). Record how the server runs today and whether a deploy changes the executable path.

Roles to define in M0.3: `chat`, `planner`, `grounder`, `computer_agent`, `stt_fast`, `stt_batch`, `tts`, `cleanup`, `metadata_writer`, `town_small`, `town_large`, `judge`.

Risk tiers for M0.5, used by projects 1, 4 and 6:

| Tier | Examples | Default |
| --- | --- | --- |
| 0 Read | Screenshot, list windows, read DataHub | Allowed |
| 1 Navigate | Scroll, focus or open an allowlisted app | Allowed in the sandbox VM; ask on the real desktop |
| 2 Change | Click, type, key combinations | Ask, unless the app is allowlisted for that task |
| 3 Irreversible | Send, submit, delete, purchase, DataHub writes, terminal commands | Always ask, confirmed by a tap |
| Blocked | Password managers, banking and payment sites, System Settings privacy panes, Keychain | Never |

Text on screen and web content are data, never instructions. A tier-3 action needs Jake's tap whatever the screen or the model says.

## Project 1: Computer-use tool

Chat gets a `computer_task` tool. A local vision model works through screenshots and mouse and keyboard actions until the task is done, stuck, or out of budget.

Design:

- **Driver: borrow first.** Try [Cua Driver](https://github.com/trycua/cua) first. It's MIT-licensed, connects through a CLI, MCP or SDKs, and can act without moving the pointer or taking focus where macOS allows. If it doesn't fit, write a small pyobjc driver (Quartz screenshots, CGEvent input) running as its own LaunchAgent at a fixed path. The driver only executes actions and never calls a model, so it doesn't bypass the queue.
- **One coordinate function.** Models return points in different conventions. Qwen3-VL uses relative coordinates; Qwen2.5-VL-based models such as UI-TARS-1.5 and OpenCUA use pixels in the resized image. Retina screenshots also have twice the pixels of the points used for input. One tested function maps model output to screenshot pixels to screen points.
- **One adapter per model family.** Each adapter builds the prompt, declares its coordinate convention and image size, and parses output into a whitelisted `Action`. Build Holo4 first, then Qwen3-VL as a generic baseline, then UI-TARS-1.5-7B. Take prompt and output formats from H Company's docs and the model cards, never from memory. H's API docs list JSON-constrained output, a separate reasoning stream, and an element-localization mode returning `{x, y}` on a 0–1000 grid; confirm the local weights behave the same.
- **No code execution.** OpenCUA emits pyautogui code. Parse it with a whitelist parser and never run it.
- **Small action set.** `click`, `double_click`, `type`, `key`, `scroll`, `drag`, `wait`, plus `done`, `fail` and `ask_user`. Local models get less reliable as the tool list grows.
- **The loop.** Observe, propose, check policy and approval, act, wait for the screen to settle, observe again. Defaults: 25 steps and 5 minutes. Stop early when the screen hasn't changed after 3 actions, when one action repeats 3 times, or on `ask_user`. Context holds the last few screenshots, downscaled, plus a text log of every action.
- **Background job.** Each task runs as a durable job modeled on the transcription job manager. Each model step takes the queue and releases it.
- **What Jake sees.** A live step list in chat (thumbnail plus action), approval prompts in the web UI and PWA, and a final summary linking to the run record.
- **Sandbox.** Lume, also from the Cua project, runs macOS VMs on Apple Silicon through Apple's Virtualization framework. The driver targets the VM as a second screen. Autonomous mode is allowed only there.

Tool contract:

```text
computer_task(task, app=None, target="desktop" | "vm", mode="confirm_each" | "confirm_risky" | "autonomous", max_steps=25)
  -> {status: "done" | "failed" | "stopped" | "needs_input", summary, steps, run_id}
# mode="autonomous" is accepted only with target="vm"
```

| Milestone | Delivers | Done when |
| --- | --- | --- |
| M1.1 Driver | `ScreenDriver` interface (Cua Driver or own), coordinate mapping, permission check, CLI `computer screenshot` and `computer click --dry-run` | Mapping tests pass at 1× and 2× scale and three resolutions; dry-run logs without moving the pointer; missing permissions give a clear message |
| M1.2 Locate | Holo4 adapter and `computer locate "<target>"`, which saves a screenshot with a marker and clicks nothing | Fixture tests parse saved real outputs; hit rate on the Project 7 grounding set is reported against a target set beforehand |
| M1.3 Loop | Agent loop in `confirm_each` mode, run records, caps, Stop | Demo: open TextEdit, type "hello from the harness", save as `~/Desktop/agent-test/hello.txt`. The file exists and every step is recorded |
| M1.4 In chat | `computer_task` in chat, approvals on the phone, risk tiers and app allowlist | The demo runs from the phone with approvals there; a deny-listed app is refused before any action |
| M1.5 Sandbox | Lume VM target; `autonomous` allowed only there | The demo passes in the VM with no approvals; the same autonomous request on the desktop is refused |

## Project 2: Planner + grounder

Each step splits into deciding what to do (planner) and finding it on screen (grounder). The split becomes the default only if the Project 7 suite shows it beats one model doing both.

Why split: H Company [reports](https://www.nocode.mba/ai-release-tracker/releases/holo4) Holo4-27B at 61.7% on OSWorld 2.0 against 30.9% for the faster 35B-A3B. The harness's own evals found the daily model reliable at single steps but inconsistent at steering many. A split lets a strong planner pair with a fast grounder while code checks every step.

Design:

- **Planner output.** JSON such as `{"next": {"action": "click", "target": "blue Save button in the dialog"}, "expect": "the dialog closes", "plan": [...], "done": false}`. Targets are words, never coordinates.
- **Grounder.** `locate(target, screenshot) -> {x, y, confidence}`. Holo models support single-turn localization directly.
- **Verifier.** After each action, a yes/no check that `expect` happened, from a cheap vision call or a screenshot diff.
- **Recovery.** On low confidence or a failed check, crop around the first guess at 2× zoom and locate once more. If that fails, the planner re-plans with the failure noted.
- **Same tool.** `computer_task` keeps its contract. Config picks `strategy: single` or `strategy: split`, never the caller.
- **Memory.** Planner and grounder must pass the M0.3 budget check together.

Configurations to compare:

| Config | Planner | Grounder |
| --- | --- | --- |
| A | Holo4-27B, end to end | Same model |
| B | Holo4-35B-A3B, end to end | Same model |
| C | Daily chat model | Holo3.1-9B |
| D | Holo4-27B | Holo3.1-9B |

| Milestone | Delivers | Done when |
| --- | --- | --- |
| M2.1 Grounder | `grounder` role and a `locate` service with zoom refinement | The grounding suite reports hit rate with and without refinement |
| M2.2 Split loop | Planner, verifier and re-plan behind `computer_task` | The M1.3 to M1.5 demos pass with `strategy: split` |
| M2.3 Default | Configurations A to D run on the computer-use suite | Results are in the phase doc; the default changes only on a higher success rate and Jake's sign-off |

## Project 3: Brindle Hollow engine

The town prototype becomes a 24/7 engine on the Mac mini: SQLite for state, rules for routine life, and local models for dialogue, the gazette and nightly reflections.

Starting point: Brindle Hollow is a single-file HTML, JS and canvas prototype. Eight residents with jobs, schedules, relationships and memories run on hand-written rules and browser storage, with a daily gazette and five powers (storm, festival, stranger, rumor, whisper). The plan for the Mac mini version was a local model for dialogue and reasoning, SQLite memory with search, and nightly reflections.

Design:

- **Engine as its own service.** A `town/` package with its own LaunchAgent owns the tick loop and SQLite: residents, relationships, memories (FTS5 search), events and gazette issues. The prototype becomes the viewer, reading state over HTTP and server-sent events.
- **Rules stay the cheap path.** Port the prototype's rules for movement, schedules and relationship drift. Models only write words: dialogue lines, reactions to whispers and rumors, the gazette and reflections. With no model available, the town keeps running on rules alone.
- **Model calls through the harness.** The engine calls a localhost-only harness endpoint at background priority, so chats always go first. Calling Ollama directly would compete with chats, which ground rule 3 forbids. The endpoint adds model calls, so it belongs in the M0.2 amendment.
- **Tiered cognition.** `town_small` writes short dialogue lines. `town_large` writes the gazette and reflections in a night window, for example 02:00 to 05:00.
- **Per-resident models as an experiment.** Config can map each resident to its own model. Several models loaded at once is heavy, so this runs as a scheduled experiment week, not the default. Log lines per day, repetition (distinct-n), how often residents cite memories, and relationship drift.
- **Harness tools.** `town_news()` returns today's gazette and `town_whisper(resident, text)` plants a whisper. Neither needs approval, because the town is its own sandbox.
- **24/7 operation.** Restart on crash, system sleep off, and the town database added to the harness's daily backup.

| Milestone | Delivers | Done when |
| --- | --- | --- |
| M3.1 Rules engine | Prototype rules ported, SQLite state, viewer reading from the engine | Runs 72 hours unattended; a restart resumes the same state; the viewer shows what the prototype showed |
| M3.2 Dialogue | `town_small` dialogue through the harness endpoint at background priority | During a chat, a reply never waits on more than one town call; every line is schema-valid |
| M3.3 Memory and reflection | FTS5 memory search, nightly reflections, model-written gazette | Residents refer to past events; one gazette issue a day |
| M3.4 Experiments and tools | Per-resident model config, experiment metrics, `town_news` and `town_whisper` | An experiment report compares models on the logged metrics |

## Project 4: Metadata description generator

A fixed pipeline drafts table and column descriptions, tags and glossary terms for datasets in Jake's DataHub lab. Nothing reaches DataHub until Jake approves it.

Design:

- **Input per dataset.** Field names, types and existing docs; table name and platform; upstream and downstream names; the lab's glossary terms and tags. Sample values are off by default and masked when on.
- **One structured call per table.** It's a narrow, single-step task, the kind the daily model handles well. Output per field: a description of at most two sentences, suggested terms and tags, a PII flag, a confidence score and a one-line reason.
- **No invented terms.** Allowed glossary terms and tags go into the JSON schema as enums, so constrained decoding can't produce a term that doesn't exist.
- **Review queue.** A table in the web UI and PWA with approve, edit or reject per field, and bulk approve for high-confidence rows.
- **Write-back with attribution.** Use [DataHub's Python SDK](https://docs.datahub.com/docs/generated/metamodel/entities/schemafield.md). Field descriptions go to the schema field's `documentation` aspect, where each entry records a source and an actor. Use a distinct source, such as a `local-llm` platform URN, with Jake as the actor. Re-runs replace only that source's entries, so human-written docs are never touched. Terms and tags go to `glossaryTerms` and `globalTags`.
- **Approval and data rules.** Each write batch is tier 3 and needs a tap. This capability can never use a cloud model (ground rule 7).

| Milestone | Delivers | Done when |
| --- | --- | --- |
| M4.1 Read path | List datasets and fetch schema, glossary and tags from the lab through the SDK | Unit tests use recorded SDK responses; a dry run prints the model input for one dataset |
| M4.2 Drafts | Generation call with an enum-constrained schema; proposals stored in the database | 50 fields from a public sample schema (for example TPC-H) all get schema-valid proposals, with no term outside the enum |
| M4.3 Review | Review queue in the web UI and PWA | Approve, edit and reject persist; nothing is written to DataHub yet |
| M4.4 Write-back | Approval-gated writes with attribution | Approved text shows in DataHub under the AI source; a re-run replaces only its own entries |
| M4.5 Quality | Metadata suite in Project 7 with gold descriptions for the sample schema | Judge scores are reported, plus Jake's spot check of 20 fields |

## Project 5: Transcript cleanup

The existing transcription and clean-up path gains a local glossary, edits Jake can review one by one, and notes whose action items are backed by verbatim quotes.

Starting point: recordings sent from the phone PWA are already transcribed on the Mac mini. `server/app/transcribe/cleanup.py` runs a user-started clean-up step with a code-side check. The October 8 plan proposed a recording-to-notes pipeline as Phase 9B. This project extends whatever exists rather than duplicating it.

Design:

- **Local glossary.** `.data/glossary.yaml`, gitignored. Each entry holds the correct term, known mis-hearings and an optional hint. Internal system names never go into the repo or any cloud tool.
- **Pass 1, deterministic.** Exact, fuzzy (rapidfuzz) and phonetic (Double Metaphone) matches of known mis-hearings are replaced with the correct term. Precision comes first; anything uncertain is left for pass 2.
- **Pass 2, edits instead of rewrites.** Overlapping chunks go to the `cleanup` role with the glossary in the prompt. The model returns edits as `{segment_id, original, replacement, reason}`. Code applies an edit only if `original` appears verbatim in that segment.
- **Review.** A diff view shows every change, and Jake can reject any edit.
- **Notes.** Decisions, action items (owner, task, due date) and open questions, each with a supporting quote. Code drops any item whose quote isn't verbatim in the transcript.
- **Learning loop.** When Jake fixes a word both passes missed, the harness proposes a glossary entry for him to accept.
- **Speech-to-text hints.** If the batch model accepts a prompt or hotword list, as Whisper's initial prompt does, pass it the most common glossary terms.
- **Trigger.** Clean-up stays user-started, as `AGENTS.md` defines it. Running it automatically after transcription needs its flag and an approved amendment.
- **Later, optional.** Once a few hundred approved before-and-after pairs exist, try a LoRA fine-tune with mlx-lm. Keep it only if the Project 7 suite shows it beats prompting.

| Milestone | Delivers | Done when |
| --- | --- | --- |
| M5.1 Glossary | Glossary format, pass 1 and the diff view | On synthetic transcripts with planted mis-hearings, every pass-1 replacement is correct |
| M5.2 Model edits | Pass 2 inside the existing clean-up step, with the verbatim check | Recall on planted errors is reported; no edit that fails the verbatim check is applied |
| M5.3 Notes | Notes extraction with the quote check, reusing Phase 9B where built | Planted action items are found; no item lacks a verbatim quote |
| M5.4 Learning | Fix-to-glossary proposals and speech-to-text hints | A fix in the UI produces a glossary proposal; re-running the same audio applies it |

## Project 6: Voice assistant

Push-to-talk in the phone PWA sends speech to the Mac mini. The harness answers with the same tools as typed chat, and the reply plays back as speech.

Design:

- **Input.** Push-to-talk in the PWA, which already uploads audio. No wake word: the Mac mini has no microphone, and push-to-talk avoids false triggers.
- **Speech server.** [mlx-audio](https://github.com/Blaizzy/mlx-audio) (MIT) runs speech models on Apple Silicon and serves an OpenAI-compatible API, including `/v1/audio/transcriptions` and `/v1/audio/speech`. Start it with `mlx_audio.server`. The harness calls it through `providers/` like any other model server.
- **Speech to text.** `stt_fast` uses Parakeet (`mlx-community/parakeet-tdt-0.6b-v3`) for short commands. `stt_batch` stays on the existing Whisper path for long recordings.
- **The answer.** The same run pipeline as typed chat, with a voice style prompt: short sentences, no markdown, numbers written to be spoken.
- **Text to speech.** `tts` uses Kokoro (`mlx-community/Kokoro-82M-bf16`). Synthesize sentence by sentence as the reply streams, so the first sentence plays while the rest is generated.
- **Approvals by tap only.** Tier 2 and 3 actions need a tap on the phone, never a spoken "yes". A misheard word must not send or delete anything.
- **Latency target.** Under 2 seconds from releasing the button to first audio, for a short answer with no tools. Log each stage: upload, speech to text, first token, first audio.

| Milestone | Delivers | Done when |
| --- | --- | --- |
| M6.1 Speech server | mlx-audio as a managed local service, `stt_fast` and `tts` roles, a CLI round trip | `voice say "hello"` plays audio; `voice transcribe clip.wav` stays within a word error rate, set beforehand, of the Whisper transcript |
| M6.2 Round trip | PWA push-to-talk to chat to spoken reply, request and response | Works end to end from the phone; per-stage timings are logged |
| M6.3 Streaming | Sentence-by-sentence playback and a stop button | First audio plays before the full reply is generated |
| M6.4 Tools by voice | Voice style, tap approvals, tools including `computer_task` | A spoken request triggers a tool; a tier-3 action waits for a tap |

## Project 7: Personal eval suite

The harness's existing eval harnesses gain one suite per new capability and a model comparison report, so models change on evidence from Jake's own tasks.

Design:

- **Reuse, don't rebuild.** The repo already has three eval harnesses. New suites plug into the existing runner and result format.
- **Targets before runs.** Each suite's pass targets go in its phase doc before the first run, as the repo already does.
- **Results in the database.** Run, model, suite, case, score, latency and tokens go in tables, never in Git.
- **Pinned judge.** Where a judge model scores outputs, pin it in config. Check it against 20 items Jake labels by hand before trusting it.
- **Report.** A harness page shows models against suites, the change from the current default, and a one-line "switch?" verdict. `evals compare <model>` runs the quick suites at once and the slow ones overnight.

| Suite | Cases | Measures | Lands with |
| --- | --- | --- | --- |
| Grounding | 50 screenshots of Jake's own apps, each with a labeled target box, made with a click-and-drag labeling helper | Hit rate, latency | M7.2 |
| Computer use | 15 short tasks in the Lume VM, each with a setup script and a checker, such as "this file exists with this text" | Success, steps, time | M7.3 |
| Cleanup | Synthetic transcripts with planted mis-hearings and action items | Precision, recall, quote check | M5.2 |
| Metadata | Gold descriptions for a public sample schema | Judge score, term accuracy | M4.5 |
| Voice | Jake's own short clips | Word error rate, latency per stage | M6.2 |
| Town | 30 sampled dialogues per model | Repetition, memory references, judge score | M3.4 |

| Milestone | Delivers | Done when |
| --- | --- | --- |
| M7.1 Plumbing | New suite type, result tables, report page | Existing suites still run; a dummy suite appears in the report |
| M7.2 Grounding | Grounding suite and labeling helper | 50 labeled screenshots, scored end to end with a fake grounder |
| M7.3 Computer use | VM task suite with checkers and a nightly run | A nightly run completes unattended inside the VM |
| M7.4 Compare | `evals compare` and the "switch?" verdict | Adding a model to config and running one command produces the report |

The cleanup, metadata, voice and town suites arrive with their projects' milestones.

## Testing strategy

Every milestone ships three layers of tests, and only the first runs everywhere.

1. **Unit tests with fakes.** A fake model with canned outputs, a fake screen with saved screenshots, fake audio with saved clips, and a fake DataHub with recorded SDK responses. These run in CI and in a Linux cloud sandbox.
2. **Fixture tests from real outputs.** The first time a model is wired up, save its real outputs as fixtures. Parsers and adapters must pass them, so a model update that changes its format fails loudly.
3. **Local integration tests, gated.** Anything that needs macOS, a model server, audio, the VM or DataHub runs only with `RUN_LOCAL_INTEGRATION=1` and skips cleanly elsewhere.

Also:

- The existing suites, including the browser suite, pass with all flags off and with each new flag on.
- Each milestone adds a demo script under `scripts/demos/` that Jake can run with one command.
- The nightly VM run from Project 7 doubles as the regression test for Projects 1 and 2.

## Risks and open questions

The biggest risk is building on repo facts that have changed: this plan's picture of the harness comes from a review on October 8, and the repo moves fast. M0.1 exists to catch that.

| Risk | Effect | Mitigation |
| --- | --- | --- |
| Repo facts out of date | Milestones target code that has moved | M0.1 confirms every fact before code |
| Amendments not approved | Codex must stop | M0.2 bundles every amendment into one review |
| Model output formats change between releases | Silent parse failures | Adapters with fixture tests; formats from current docs |
| Coordinate errors (Retina, several displays) | Clicks land in the wrong place | One tested mapping function; one display at a fixed resolution |
| macOS grants lost after a deploy | Computer use stops working | Driver at a fixed path; permission check at startup |
| Too many models loaded at once | Memory swapping, slow chats | M0.3 budget check; on-demand loading |
| Text on screen tries to steer the agent | Unwanted actions | Screen text is data; tier 3 always needs a tap |
| Holo4-27B license is non-commercial (CC BY-NC 4.0) | Can't be used for work | Personal use only; Holo4-35B-A3B is Apache 2.0 |
| Background work slows chats | Worse daily use | Chat-first queue; background steps release after each step |

Open questions for Jake:

- [ ] Does any of Phase 9 (automations) exist yet?
- [ ] Should the town engine live in this repo as `town/`, or in its own repo?
- [ ] Is real work data ever in scope for Projects 4 and 5 on this machine?
- [ ] Which apps go on the computer-use allowlist first?
- [ ] Where does the DataHub lab run, and on which version?

## Appendix: Models and sources

Start with these candidates and let the Project 7 suites pick the defaults. Check for newer releases before each comparison.

| Role | Candidates | Notes |
| --- | --- | --- |
| Computer-use agent | [Holo4-27B](https://www.nocode.mba/ai-release-tracker/releases/holo4), [Holo4-35B-A3B](https://ai-tldr.dev/models/holo4-35b-a3b/) | 27B is stronger on long tasks and non-commercial; 35B-A3B is faster and Apache 2.0 |
| Grounder | [Holo3.1-9B and 4B](https://huggingface.co/Hcompany/Holo-3.1-9B), [Qwen3-VL-8B](https://github.com/QwenLM/Qwen3-VL), [UI-TARS-1.5-7B](https://github.com/bytedance/ui-tars), [OpenCUA](https://huggingface.co/xlangai/OpenCUA-32B) | Holo3.1 is Apache 2.0; UI-TARS-1.5 and OpenCUA return pixels on the resized image; OpenCUA writes pyautogui code |
| Planner | Daily chat model, Holo4-27B | Chosen in M2.3 |
| Speech to text | Parakeet `mlx-community/parakeet-tdt-0.6b-v3`, Whisper `mlx-community/whisper-large-v3-turbo-asr-fp16` | Both served by [mlx-audio](https://github.com/Blaizzy/mlx-audio) |
| Text to speech | Kokoro `mlx-community/Kokoro-82M-bf16` | Served by mlx-audio |
| Judge | Pinned after M7.1 | Checked against 20 hand-labeled items |

Sources:

- [Holo4 release summary](https://www.nocode.mba/ai-release-tracker/releases/holo4) (No Code MBA)
- [Holo4 35B-A3B summary](https://ai-tldr.dev/models/holo4-35b-a3b/) (AI TL;DR)
- [Holo3.1-9B model card](https://huggingface.co/Hcompany/Holo-3.1-9B) (Hugging Face)
- [H Company docs](https://hub.hcompany.ai/llms-full.txt)
- [Qwen3-VL](https://github.com/QwenLM/Qwen3-VL) (GitHub)
- [UI-TARS](https://github.com/bytedance/ui-tars) (GitHub)
- [OpenCUA-32B model card](https://huggingface.co/xlangai/OpenCUA-32B) (Hugging Face)
- [Cua: Cua Driver, Lume and Cua Bench](https://github.com/trycua/cua) (GitHub)
- [DataHub schema field metadata](https://docs.datahub.com/docs/generated/metamodel/entities/schemafield.md)
- [mlx-audio](https://github.com/Blaizzy/mlx-audio) (GitHub)
