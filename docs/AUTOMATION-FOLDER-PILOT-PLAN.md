# NS0/NS1 — one local recording-folder workflow

23 October 2026. Concrete proposal after the theme checkpoint. No watcher,
schedule, folder permission, package, native test or model call is enabled here.

## What it does

**A new recording in one chosen folder → transcribe → draft summary, decisions
and actions → save a local meeting pack.** Use the existing editable Meeting
pack graph, with transcript clean-up disabled for the first pilot. The existing
Generate text block uses the frozen `MEETING_PACK` instructions and one explicitly
selected installed model with the user's saved settings. No planner, title,
extra checking model, routing or agent framework is needed.

## What the code already provides

| Existing part | Evidence | Remaining work |
|---|---|---|
| Recording → transcription → meeting-pack graph | `server/app/workflows/template_graphs.py:template_graph` | Bind a durable folder intake to a graph snapshot |
| Durable transcript/source and hashes | `server/app/workflows/blocks.py:execute` | Reuse normal ingestion/pinning; never pass a source path straight into a model |
| Request-key idempotency | `server/app/workflows/engine.py:GraphRunner.submit` | Persist one stable request key and attachment before submission; reuse both after a crash |
| Queued work and capacity ownership | Graph runner plus existing transcription/capacity managers | Bound trigger backlog; do not evict chat models or start competing heavy jobs |
| Interrupted-step recovery and explicit retry | `GraphRunner.recover` / `resume` | Preserve these semantics; do not silently restart a paid-in-time native step |
| Saved graph outputs and Markdown/JSON export | `blocks.py` OutputNode / `api/workflow_graphs.py:export` | Add an authorized local output writer; current Save results does **not** write to an arbitrary folder |
| SSE progress | Existing workflow stream | Show trigger/intake state through SSE; no browser polling |

These are inspected code paths, not a new end-to-end automation test result.

## Proposed first boundaries

- One user-selected input folder and a separate selected output folder, neither
  nested in the other. No recursive traversal. Reject symlinks and files escaping
  the configured directory; do not scan Documents, Messages or other locations.
- Preview existing files at enable time and mark them as the baseline. Process
  only newly admitted content unless the user explicitly chooses a backfill.
- Accept only the existing audio formats and upload limits. Intake waits at least
  30 seconds with unchanged size/mtime, then copies into app-owned temporary
  storage while hashing. Recheck identity/size/mtime after copying; discard the
  staged copy if changed. This reduces incomplete-copy risk; a producer's atomic
  move into the input folder is the strongest completion signal.
- Deduplicate by trigger ID plus full content hash: rename/copy/double discovery
  of unchanged content cannot start a second run. A graph edit does not silently
  invalidate that record. New content is a new item; Retry reuses the existing
  accepted item and successful graph steps.
- Persist discovered → stable → staged → accepted → running → review/complete/
  failed states. Bind the exact attachment ID, graph snapshot, model/settings and
  request key before graph submission. Reconcile a crash after submission by that
  key, rather than generating a fresh one.
- One active item and at most two queued staged items. Stop accepting when the
  queue or staging-byte ceiling is reached, leaving originals untouched and the
  backlog visible. Set the concrete byte ceiling against available disk space
  in the implementation plan, preserving the existing upload headroom rule.
- Pause prevents new acceptance. Cancel targets owned work, waits for process
  reaping and keeps completed outputs. Restart restores the intake ledger;
  interrupted native steps require explicit Retry, as the current engine does.
- Write an opaque run-ID subfolder containing `meeting-pack.md`, `transcript.txt`,
  `timestamps.json` and a manifest of source/output hashes and graph/model IDs.
  Use temporary files and a committed manifest/atomic directory rename so a
  partial pack never appears complete. A writer retry must not regenerate text.
- Never delete or move the user's input. Existing temporary-audio retention rules
  apply only to Aether's copy; transcript and finished outputs remain durable.
  Paths, recording names and transcript text stay out of logs/repo/screenshots.
- Output is a draft for review, with direct access to the original transcript.
  Missing owners/dates must stay missing. No messages, email, external publishing,
  arbitrary file writes or model-authored destination paths.

## Checkpoints

### NS0 — CPU/fake-runtime foundation

Build a disabled trigger configuration and manual **Preview intake** flow using
synthetic fixtures only. Implement durable admission/deduplication, output writing
and restart reconciliation behind tests. No unattended run, real folder access,
real transcription/model call or new dependency. Show each state on `/design`.
Stop with full regression evidence and the concrete NS1 test/settings proposal.

Required tests: incomplete/changing copy; duplicate events and renamed identical
bytes; changed content; source/path replacement and symlinks; submission crash
before/after acceptance; restart with completed/interrupted steps; pause/cancel;
queue/disk limits; partial export/retry; backup/restore; private-content logging;
unchanged ordinary chat payloads and SSE behavior.

### NS1 — bounded useful pilot, then opt-in enable

Review the selected folders, saved graph/model/settings, scan interval and missed-
run policy first. A standard-library periodic **server-side folder scan** is the
proposed trigger; browser updates remain SSE. Name this explicitly in the scope
so the existing no-polling UI rule is not silently reinterpreted. Prefer one
small scan every 30 seconds, skipping while paused/full; coalesce missed checks
into one bounded scan, not a burst of historical timer events.

Propose at most two short synthetic recordings, one existing graph answer call
per recording, clean-up off, stopping on technical/resource failure. Judge the
result against a prewritten transcript/rubric: correct summary/decisions/actions,
no invented owner/date, useful Markdown, exact source linkage and no duplicates.
No real unattended input is admitted until that review passes and the user
enables the trigger. Repeated quality failures stop expansion of the pilot.

## Decisions still needed

The next implementation approval would cover NS0 only. NS1 separately needs
the actual input/output locations, graph and model, timing/catch-up choice and
named native-call bound. This document selects no private paths and grants no
access. Later schedules, file types, notifications or agent-chosen tools each
need evidence from this narrow pilot before expansion.
