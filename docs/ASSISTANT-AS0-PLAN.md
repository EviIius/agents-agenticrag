# AS0 implementation boundary

30 October 2026. Jake's “continue” starts AS0 from `b81faf81`, following the
accepted technical map and clarified general computer-use target. This is the
concrete implementation/schema proposal before applying it to synthetic data.

## Deliverable

An opt-in, explicitly labelled **fake desktop demonstration** in existing chat,
with a shared desktop driver/controller operating synthetic Messages and Notes.
No natural-language/model comprehension is claimed: the demonstration uses
selected scripted tasks. Typed instructions are retained as the user's request.
Every new state is available on `/design?assistant`.

`WORKBENCH_ASSISTANT_ENABLED` defaults false. AS0 has no native implementation;
the fake driver is constructed only in development with that flag enabled.
Enabled-without-driver requests fail closed. The flag cannot authorize native
screen capture, app control, inference or sending. No existing model payload,
prompt, reasoning, sampling or chat context changes.

## Proposed additive schema: migration 015

Use the existing private SQLite database and Store, not a second database or
external queue. Apply this candidate migration only in test/development copies;
production is untouched and migration/release approval remains separate.

- `assistant_tasks`: ID, chat and optional parent message FK, unique request key,
  original request, bounded full snapshot JSON, state, update time and durable
  cancellation-intent bit. The snapshot retains the exact approved action.
- `assistant_approvals`: approval ID, task FK, exact bound observation/action hash,
  state and expiry. Store the exact approved edited action before execution.
- `assistant_events`: increasing ID, task FK and snapshot event for durable SSE
  replay. Detailed model token streams are not part of this checkpoint.

Task snapshots contain bounded steps and observation metadata. All FK children
cascade on chat/task deletion. Startup interrupts unfinished tasks, invalidates
pending approvals and marks a potentially committed action outcome unknown.
It never silently resumes an external write. Existing tables/rows are not altered.
The migration name/order must be reconciled with any later independently merged
schema change before release. No rollback drops new task records over live data.

## Contracts and controller

- Immutable Pydantic observations, window identity/revision, UI elements and
  explicit image resize/crop/display metadata. Coordinates validate before use.
- Small typed action union; no generated script/code evaluation. Host policy
  owns allowlist, writable targets, commit permissions and exact approval binding.
- Shared injectable driver/proposal interfaces. Both AS0 implementations are
  scripted and fake. A native model proposal source is AS2 work.
- Verify a fresh state after every action. A stale target or changed incoming
  message blocks execution; no automatic retry. Unknown commit outcomes are
  terminal and cannot be replayed by reusing an approval/request key.
- Persist acceptance, decision and execution intent before dispatch; serialize
  desktop actions and consume each approval once. Release resources while
  awaiting review; queued cancellation never dispatches later.
- Existing capacity coordinates future model invocations; AS0 makes none.
  Desktop actions have their own serial lock, not a competing model queue.
- Existing SSE/event-ID and rAF patterns for live UI, no status polling. Use
  one multiplexed browser connection for all active tasks so pending approvals
  cannot exhaust HTTP/1.1 connections and block actions.

## Acceptance and evidence

Test fake Messages and Notes through one controller; coordinate scale/crop
mapping; disabled/unavailable API; malformed/forged targets; wrong chat/parent;
recipient ambiguity; untrusted text; missing/revoked permission; stale source;
edited draft binding; duplicate decision; reconnect/restart; queued/running
cancellation and unknown commit outcome. Preserve old provider payload tests.

Run full `make check` and `make e2e` against fake runtimes, retain failures and
synthetic screenshots, verify default-off bootstrap behavior and installed-file
preservation. No existing threshold/skip is weakened. Stop with the H4 report.
AS1 app access, AS2 model calls and AS3 live send remain separately gated.
