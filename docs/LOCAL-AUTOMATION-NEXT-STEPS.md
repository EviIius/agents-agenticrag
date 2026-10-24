# Local automation — roadmap status and recommended first scope

20 October 2026. Answers Jake's question during PE1-C: “Do we have automated
workflows on the list where Local AI can start doing things for me automatically?”
This is planning only; no automatic task or extra model call is started.

23 October checkpoint: `AUTOMATION-FOLDER-PILOT-PLAN.md` turns this recommendation
into a concrete NS0/NS1 proposal after the isolated themes checkpoint. It names
the reusable graph/runner code and the missing folder-intake/output-writer work.
No watcher, schedule, private folder access or native test is enabled by the plan.

## Already on the list

- `next/workflow-studio/WORKFLOW-STUDIO-SPEC.md` §12, **WS-F**, explicitly lists
  **Schedule trigger** and **Loop over a list**, each with its own reviewed scope.
- `APP-DIRECTION-AND-WORKFLOWS.md` §§4–5 and W2 put scheduling/batching after
  dependable manual workflows, with model-chosen actions later if justified.
- The live graph builder already executes a chain after **Run**, with saved
  outputs, review pauses and failed-step retry. It has no enabled recurrence
  trigger or folder watcher. The word “scheduler” in the current graph engine
  means choosing the next block within a run, not starting runs on a calendar.
- Hermes/PydanticAI/native-agent trials are stopped, not production automation.
  Research stays shelved. Their history does not qualify an autonomous assistant.

## Recommended after photo editing closes

Use the existing workflow engine for one controlled pilot:

**New recording in a chosen local input folder → Transcribe → Summary, decisions
and action items → Save the meeting pack in a chosen output folder.**

A folder input trigger is a proposed addition, not an already implemented WS-F
feature. A bounded schedule that checks that one folder is one possible first
trigger; the concrete timing and locations should be chosen in its spec. Later,
add daily/weekly schedules for other saved workflows and batching over documents.
No separate agent framework is needed to execute a defined chain.

Useful behavior for the first scope:

1. Explicitly choose input/output locations, workflow, text model and timing.
   The Mac/app must be running for local execution; missed runs need a declared
   skip/catch-up rule, rather than an unbounded catch-up burst.
2. Persist trigger/input identity and run acceptance; the same unchanged file
   must not run twice. Wait for a file to finish copying before accepting it.
3. Reuse the shared capacity lease, resource limits, input pins and cancellation.
   No simultaneous heavy GPU work or automatic chat-model eviction.
4. Record a visible history: queued, running, awaiting review, complete, failed.
   Resume from durable inputs; retry the failed step explicitly, preserving
   successful steps. Give each trigger a pause switch and bounded queue.
5. Save outputs locally. Keep review steps for external messages or changes
   outside the chosen output destination. Factual summaries remain reviewable
   drafts; owners/dates absent from a recording must remain absent.
6. Qualify duplicate delivery, invalid/unfinished files, cancellation, restart,
   capacity contention and storage cleanup on synthetic files. Check actual
   output usefulness against the transcript before enabling unattended runs.

This is distinct from asking a model to invent its own plan and tools. A later
agent can choose among allowed actions if a real task needs that flexibility,
under explicit tool/time/step budgets and measured task quality. It does not
need to precede useful scheduled local workflows.

## Current priority boundary

Finish photo-edit quality review and installer/fallback/release checks first.
Then propose the narrow automation pilot and its permissions/acceptance tests.
Jake's roadmap question is not authorization to install a watcher, create an app
or Codex schedule, restart agent trials, or let a model send messages/delete files.
