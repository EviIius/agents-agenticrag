# Assistant AS0 report

30–31 October 2026 · `codex/assistant-as0` · isolated fake-only candidate

## Summary

Implemented the shared observe → propose → approve → act → verify controller and
chat review UI against invented Messages and Notes windows. The proposal interface
receives the typed goal separately from observed source text. Both demonstrations
are scripted; no natural-language understanding or native app success is claimed.
The feature defaults off and its driver is available only in development. Main,
the installed application and the separate design critique branch are unchanged.
**Transport correction passes focused checks; final full suites are running.**

## Done-when checklist

| Item | Status | Evidence |
| --- | --- | --- |
| Shared immutable observations/actions, window/revision/coordinate binding | Pass | `server/app/assistant/contracts.py`; coordinate/crop/scale and forged-target tests |
| Two apps use one injectable driver, proposal interface and controller | Pass, scripted only | `driver.py`, `manager.py`; exact-edited-text and two-app tests |
| Durable tasks, one-time approvals, cancellation intent and SSE replay | Pass | Candidate migration 015; disconnect/restart/double-decision/cancellation tests |
| Recheck recipient/source/permission immediately before action | Pass, fake only | Changed incoming/window/participant and revoked-access cases |
| Never replay an uncertain commit | Pass | Consumed approvals/request keys; restart/unknown-outcome tests and no retry button |
| In-chat review and all design states | Pass, synthetic browser evidence | `/design?assistant`; edited reply, Notes, reload, Stop, interruption and disabled entry checks |
| Default-off bootstrap/API and no native implementation | Pass | Disabled/unavailable API tests; dev-and-flag constructor guard |
| Old schema definitions/rows preserved | Pass in isolated DB | Schema-14→15 test, idempotent migration and FK checks; no production migration |
| Ordinary provider paths unchanged, no new package/model call | Final regression pending | Unchanged providers/runs/prompts/locks plus payload tests in the full suites |
| Full `make check` / `make e2e` | **Pending after shared-stream correction** | Logs in `artifacts/assistant-as0-20261030/` |
| Installed files, service and other branches preserved | Initial verification passed; final pending | 646-file inventory; PID 77443; final verification follows regression |
| Human/native acceptance | **Not claimed** | AS1 app access and later model/send trials require their own scope |

## Changed files

- Server: `app/assistant/{contracts,driver,manager}.py`, `api/assistant.py`, additive
  migration 015, config/bootstrap/lifespan wiring, cancellation before chat deletion and feature-gated history for task-only chats.
- Web: lazy `AssistantChat`, `TaskCard`, SSE/rAF helper, optional Tools entry and
  attachment-free task composer; design preview and regenerated API types.
- QA: 36 fake controller/API/migration cases, five stream-client unit cases,
  22 browser cases, synthetic test-server controls and assistant coverage target.
- Six old migration tests now expect schema 15 after the full migrator runs;
  their preservation assertions remain. Historical version-13/14 fixtures and the
  existing release helper's supported-schema limit are unchanged.
- Docs: AS0 scope/schema plan, authorization note, this report and retained evidence.

## Deviations from SPEC.md

Only the recorded AS0 amendment: a default-off, fake-only computer-task capability
and additive development/test schema. No production mode, prompt, sampling,
model-call or dependency change. Shared model capacity is not entered because the
prototype makes no inference requests; desktop actions serialize independently.
The current release helper supports schemas 13/14. Schema 15 installer/fallback
qualification remains future release work, not permission to deploy this branch.

## Runtime observations

No real Mac app was launched, screen captured, Messages data read, permission
granted, model loaded or message sent. Browser tests use isolated fake runtimes
and temporary databases. Existing temporary Part B preview processes were stopped
to free the browser suite's fixed test ports; production 127.0.0.1:8787 remains
untouched. No speed or answer-quality gain is inferred from scripted tests.

## Test output

Evidence directory: `artifacts/assistant-as0-20261030/`.

- Focused controller tests: **36 passed** (`focused-stream-fix.txt`).
- Scoped coverage diagnostic: **585/632 lines, 92.6%**, confirmed in full `make check`; this is additional evidence,
  not a replacement for the unchanged 80% full-suite gates.
- Frontend lint/type/format/unit checkpoint: **156 passed**, including five new
  stream tests (`frontend-check-stream-fix.txt`).
- Focused browser run: **22 passed**, Chromium and WebKit, including eight pending
  tasks sharing one stream with responsive cancellation (`browser-focused-stream-fix.txt`).
- Initial JS: **252,564 gzip bytes / 256,000 budget** (`bundle.json`).
- Before the final transport correction, full `make check` passed **820 Python
  tests and 155 frontend unit tests**, all coverage
  targets ≥80%, 969 contrast token pairs across eight palettes, types/lint/format,
  API generation/additive compatibility, privacy scan, motion and built glass guard
  passed. `make-check-before-stream-fix.txt` retains that output; it is not the
  final source qualification.
- Final full `make check` and `make e2e`: pending.

Retained development failures: schema-name collision with workflow `Point`, type/
format errors, a test-only GET route shadowed by the SPA fallback, graceful restart
shown as cancellation, and counting metadata lookups as inference. All were fixed. A cleanup helper incorrectly assumed a flat history response;
it now captures its own created chat IDs. Task-only chats are included in history
when the capability is available, without adding task content to text context.
Diagnostic full-suite attempts were intentionally interrupted during contract
and history review; their nonzero results are retained and are not passing gates. The final
runs use `source-manifest.json`. A standalone HTTP/1.1 probe proved eight separate
streams starved an ordinary request (six connections opened, ping timed out).
The corrected transport multiplexes up to eight IDs over one stream, preserving
event ordering/replay and per-task rAF batching. The API rejects invalid or
duplicate subscriptions; an eight-task browser test checks responsive Cancel. Private failure traces are retained outside Git.

## Screenshots

`artifacts/assistant-as0-20261030/browser/`: nine states at 390/1440 widths,
light/dark, Chromium/WebKit (72 synthetic PNGs, eight axe reports). No horizontal
overflow or serious/critical axe violations in the focused run. Inspected the
phone reply review and desktop unknown-outcome captures visually. These are
browser simulations, not physical iPhone/VoiceOver acceptance. The historical
VoiceOver limitation remains unresolved.

## Open questions for Jake / review stop

After full qualification, review this fake foundation before AS1. The next scope
is qualifying a concrete shared Mac driver on an allowlisted app and one designated
test conversation, initially read-only with no inference or send. AS2 adds bounded
local-model tasks; AS3 separately qualifies one approved send. The preview must be reopened from Tools after a reload; task records remain
durable. No native access, model trial, merge or deployment follows automatically from this report.
