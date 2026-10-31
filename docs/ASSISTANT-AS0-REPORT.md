# Assistant AS0 report

30–31 October 2026 · `codex/assistant-as0` · isolated fake-only candidate

## Summary

Implemented the shared observe → propose → approve → act → verify controller and
chat review UI against invented Messages and Notes windows. The proposal interface
receives the typed goal separately from observed source text. Both demonstrations
are scripted; no natural-language understanding or native app success is claimed.
The feature defaults off and its driver is available only in development. Main,
the installed application and the separate design critique branch are unchanged.
**Full qualification passes: 821 Python, 156 frontend and 922 browser tests;
four existing browser skips remain.**

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
| Ordinary provider paths unchanged, no new package/model call | Pass | Unchanged providers/runs/prompts/locks plus payload tests in the full suites |
| Full `make check` / `make e2e` | Pass | Final qualified logs in `artifacts/assistant-as0-20261030/` |
| Installed files, service and other branches preserved | Pass | `final-verification.json`; 646 installed files, unchanged plist and PID 77443; local/verified HTTPS health |
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

No native Messages/Notes session was opened or read; no desktop capture, permission
grant, model load or external message send occurred. Browser tests use isolated fake runtimes
and temporary databases. Existing temporary Part B preview processes were stopped
to free the browser suite's fixed test ports; production 127.0.0.1:8787 remains
untouched. No speed or answer-quality gain is inferred from scripted tests.

## Test output

Evidence directory: `artifacts/assistant-as0-20261030/`.

- Focused controller tests: **36 passed** (`focused-stream-fix.txt`).
- Full assistant coverage: **593/643 lines, 92.2%**. The earlier scoped diagnostic
  (585/632, 92.6%) is retained separately; the unchanged full-suite gate is 80%.
- Frontend lint/type/format/unit checkpoint: **156 passed**, including five new
  stream tests (`frontend-check-stream-fix.txt`).
- Focused browser run: **22 passed**, Chromium and WebKit, including eight pending
  tasks sharing one stream with responsive cancellation (`browser-focused-stream-fix.txt`).
- Initial JS: **252,562 gzip bytes / 256,000 budget** (`bundle-final.json`).
- Full `make check`: **821 Python tests, 156 frontend unit tests**, all coverage
  targets ≥80%, 969 contrast token pairs across eight palettes, types/lint/format,
  API generation/additive compatibility, privacy scan, motion and built glass guard
  pass. `make-check-qualified.txt` retains the final output (475.05 seconds).
  `make-check-final.txt` retains the check before the one-test completion-wait
  correction. The earlier 820/155 pre-transport pass is retained under
  `make-check-before-stream-fix.txt`.
- Full `make e2e`: **922 passed, four unchanged skips, zero failures (1.4 h)**,
  Chromium and WebKit. `make-e2e-qualified.txt` retains the complete output.

The first complete corrected-transport browser run is retained in
`make-e2e-final.txt`: **921 passed, four unchanged skips, one WebKit failure**.
The failure was the existing bulk-delete test, after a full Chromium run had
accumulated about 14,000 synthetic messages. It started its five-second empty
history assertion before the delete response completed: the nested confirmation
already hides Settings, so `settings.not.toBeVisible()` was not a completion
signal. Deleting a private copy of the synthetic database took **4.96 seconds**
(`delete-scale-diagnostic.json`); the original was not modified. Three focused
WebKit repetitions passed before the test correction (nine cases total).
The test now requires the actual 204 response, confirmation closure and empty
history, retaining the existing overall and assertion budgets. No app change or
skip was added. `source-manifest-qualified.json` freezes that one-test correction;
`make-check-qualified.txt` and `make-e2e-qualified.txt` record its final gates.
The same WebKit sequence passes in **9.4 seconds** in the new full run, including
the successful delete response and empty-history assertions.


Retained development failures: schema-name collision with workflow `Point`, type/
format errors, a test-only GET route shadowed by the SPA fallback, graceful restart
shown as cancellation, and counting metadata lookups as inference. All were fixed.
A cleanup helper incorrectly assumed a flat history response;
it now captures its own created chat IDs. Task-only chats are included in history
when the capability is available, without adding task content to text context.
Diagnostic full-suite attempts were intentionally interrupted during contract
and history review; their nonzero results are retained and are not passing gates.
The final runs use `source-manifest-qualified.json`; `source-manifest.json` retains
the earlier source inventory before the export-test correction.
A standalone HTTP/1.1 probe proved eight separate
streams starved an ordinary request (six connections opened, ping timed out).
The corrected transport multiplexes up to eight IDs over one stream, preserving
event ordering/replay and per-task rAF batching. The API rejects invalid or
duplicate subscriptions; an eight-task browser test checks responsive Cancel.
Private failure traces are retained outside Git.

### Preservation

`final-verification.json` confirms all **644 frozen executable/input files** and
**646 installed public files** match, with unchanged launchd plist and PID 77443.
Main remains `e7bab217`; the separate design critique branch remains `02ea8711`.
Provider, run, search, Library, image, transcription, shared and dependency files
match main. The supplied harness proposal's SHA-256 is unchanged. Local and
normally certificate-verified HTTPS health return 200. Framework Python's first
HTTPS check lacked an issuer certificate; system curl passed with normal
verification, without changing trust configuration or bypassing TLS checks
(`health-client-diagnostic.json`).

The suites regenerated 1,967 historical artifacts and 108 additional old-directory
captures. Their fresh synthetic outputs were archived privately before restoring
the originals; **all 32,388 historical hashes verify**. See
`historical-artifact-preservation.json` for counts and the archive hash. New AS0
evidence stays in this checkpoint's directory. No user data was restored or deleted.

## Screenshots

`artifacts/assistant-as0-20261030/browser/`: nine states at 390/1440 widths,
light/dark, Chromium/WebKit (72 synthetic PNGs, eight axe reports). No horizontal
overflow or serious/critical axe violations in the focused run. Inspected the
phone reply review and desktop unknown-outcome captures visually. These are
browser simulations, not physical iPhone/VoiceOver acceptance. The historical
VoiceOver limitation remains unresolved.

## Open questions for Jake / review stop

Local fake-only preview: <http://127.0.0.1:5173/design?assistant>.
For the chat flow, open <http://127.0.0.1:5173/>, choose **Tools → Use computer**,
select the scripted Messages or Notes demonstration, and submit a typed request.
Review/Edit/Send/Cancel operate only on invented in-memory app windows. The typed
request does not select or generate the scripted action. `preview.json` records
the isolated entry points; production remains on port 8787.

Review this technically qualified fake foundation before AS1. The next scope
is qualifying a concrete shared Mac driver on an allowlisted app and one designated
test conversation, initially read-only with no inference or send. AS2 adds bounded
local-model tasks; AS3 separately qualifies one approved send. The preview must
be reopened from Tools after a reload; task records remain durable. No native
access, model trial, merge or deployment follows automatically from this report.
