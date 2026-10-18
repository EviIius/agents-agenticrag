# Production follow-ups report

18 October 2026 · `codex/production-followups` · based on accepted main `e7ffea2b`.

## Summary

The first text send now preserves a title explicitly chosen by the user, including
renames made while the send is being prepared. Untitled chats keep their existing
fallback behavior. Workflows home no longer advertises its disabled Search block.
This candidate is isolated; no agent code, native inference or deployment is part
of the checkpoint. Full check, build and one complete browser invocation pass.
Main and the live app remain unchanged; this is ready for review, not deployed.

## Done-when checklist

| Item | Status | Evidence |
|---|---|---|
| Reproduce manual-title overwrite before the fix | Pass | Four failures, one passing fallback control in `title-baseline.txt` |
| Preserve title before send, auto-title on/off | Pass | New API tests |
| Preserve rename during assembly, auto-title on/off | Pass | Event-controlled concurrent API tests; database transaction reads ownership |
| Preserve search index and Markdown export title | Pass | Same API tests |
| Retain default fallback and follow-up title | Pass | New untitled-chat control |
| No extra title request for user-named chat | Pass | Exactly one fake answer request, context-only options and no think override |
| Browser rename/send/complete/reload | Pass in focused and full runs | Chromium/iPhone-profile WebKit checks and synthetic screenshots |
| Remove unavailable Search promise | Implemented | Production component also used by existing `/design?workflow-home` states |
| Full check and build gates | Pass | 726 Python / 126 frontend; 254,973 gzip bytes |
| Complete browser invocation | Pass | **721 passed / three existing skips / zero failed**, one invocation |
| Main/live preserved | Pass at final verification | Hashes, native connection guard and healthy local/verified HTTPS |

Artifacts are under `artifacts/production-followups/` unless stated otherwise.

## Changed files

- Server: add a persisted `title_source='fallback'` condition to the existing
  first-message fallback-title CASE, inside its existing transaction.
- Web: remove “search” from Workflows home's introductory sentence.
- Tests: add five synthetic API cases and one real browser flow per engine.
- Docs: plan/report, current deferred status, authorization, retained evidence
  and an unexecuted photo-editing checkpoint proposal.

There are only two application file changes. No application API/schema,
Search/Library/provider/run code, prompt, sampling, dependency, model/runtime,
image engine, workflow behavior, service/bind/port or Tailscale change.

## Why the title fix belongs in the transaction

The endpoint reads a chat and prepares its context before inserting messages.
The old first-send fallback assignment did not consider title ownership. It could
replace a manual title while leaving `title_source='user'`, which also prevents
the later automatic title helper from correcting it.

The new condition reads the current ownership at the actual database update.
It therefore preserves a rename occurring after the initial read, without
introducing a lock around user interaction or another model call. Full-text
index insertion reads that preserved title in the same acceptance transaction.
Existing fallback creation and later automatic-title behavior remain covered.
Previously overwritten title text was not retained by this schema; users can
rename such chats manually. The repair prevents future overwrites.

## Deviations and test-diff ledger

None to the reviewed product scope. A first full-check attempt found a strict
mypy import-export error in the new test's reference to the API module's imported
`assemble`. The test now imports the same original function from its defining
module. Assertions and the event-controlled race are unchanged. Retain that
failed command and pre-correction source/freeze under `pre-types/`.

| Existing test edits | Change | Reason | Original assertions retained? |
|---|---|---|---|
| None | Two new test files only | Reproduce and guard the reported behavior | Yes; no new skips, relaxed timeouts or weaker limits |

## Runtime observations

All execution uses the fake runtime and synthetic data. Native runtime connection
attempts are blocked during QA; no native answer/planner/title/embedding/image
call is authorized. The live app stays available on its existing service.
These tests verify application behavior, not model factual reliability or a new
physical iPhone result. Native-loop trials remain failed and separately preserved.

## Test output

- Baseline reproduction: **four failed / one passed**, retained before the fix.
- Focused API regression: **39 passed**, including all five new cases.
- Focused browser regression: **two passed** (Chromium and iPhone-profile WebKit).
- Full `make check`: **726 Python / 126 frontend tests**, 110 contrast pairs,
  types, all required coverage, API, motion and privacy guards pass.
- Build: **254,973 initial gzip bytes**, under the unchanged 256,000-byte budget;
  425 output files.
- Complete `make e2e`: **721 passed / three existing skips / zero failed** in
  one complete Chromium/WebKit invocation (reported 1.2 hours), exit code 0.
- All 551 frozen candidate source/test/config hashes, 548 accepted main hashes,
  114 installed server hashes and 425 installed static hashes verify unchanged.
  The four stopped experiment ledgers and native branch are preserved. Native
  connection attempts/model calls from this QA are zero. Local and normally
  verified HTTPS health pass.
- Fresh synthetic historical-path outputs are archived with hashes before
  restoring tracked originals: 1,616 modified and 40 new outputs retained;
  all 30,101 tracked historical files restored and verified. Exact hashes are
  in `historical-preservation.json`. New workflow-home captures stay under this
  checkpoint's `browser/` folder.
- Privacy audit and source/document whitespace checks pass. Raw command logs
  retain their original whitespace; they are not normalized as source code.

## Gates G-1–G-16 and core C1–C16

| Gates | Evidence / applicability |
|---|---|
| G-1/G-2 | 726 Python / 126 frontend; 721 complete-browser passes and three unchanged skips |
| G-3 | Existing tests unchanged; new test import correction retained separately |
| G-4 | 254,973 gzip bytes / unchanged 256,000-byte budget |
| G-5/G-13/G-14 | Existing contrast/motion/design states; home copy uses production component |
| G-6/G-7 | No API or migration change; existing additive/schema tests in full check |
| G-8/G-9 | All prompts and search/runs/providers source unchanged; no native eval claim or triggered G9 source change |
| G-10 | Existing golden tests plus new explicit request/call-count assertions |
| G-11/G-12 | Synthetic captures, privacy/preservation and live-health records; no publication |
| G-15 | No migration; rollback rehearsal not applicable to this checkpoint |
| G-16 | No new physical-phone acceptance claimed; review precedes release |

The completed suites retain core chat, Search/Library, documents/transcription,
images, workflows, backups, parameters, privacy, keyboard and motion checks. The
new title flow passes in both engines inside the full run, in addition to its
focused checks. No assertion, skip, timeout or performance limit is weakened.

## Screenshots

`browser/preserved-title-{chromium,webkit}-fake.png` retains the focused captures;
`browser/preserved-title-full-{chromium,webkit}-fake.png` retains the full-suite
captures separately, with both sets hashed in `screenshot-preservation.json`.
All contain only synthetic fake-runtime text. The phone layout intentionally hides the title in its top bar;
the browser assertions and saved API title establish preservation, not the still
image alone. Eight current workflow-home captures (390/1440, both themes, both
engines) are copied into `browser/`; full generated design evidence is also
retained in the private archive. Codex inspected the fake desktop/phone title
captures and phone home layout; these observations are not attributed to Jake.

## Next steps and open questions

1. **Review draft PR #5 and release these two verified repairs.** All automated
   gates pass; main/live remain unchanged until the required review/release
   decision. The repo's AGENTS.md phase-review rule causes this stop.
2. Photo-reference editing is the next independent feature proposal, using the
   existing MFLUX/FLUX worker foundation described in
   `PHOTO-EDITING-NEXT-CHECKPOINT.md` and the earlier PE0/PE1 outline. Actual pixel inputs, immutable originals,
   edit memory/cancellation, storage and human quality review need the bounded
   checkpoint; today's Refine lineage does not pass reference pixels to the engine.
3. Remaining disabled workflow blocks follow in separate scopes. Keep native
   agent/Research campaigns closed; further factual repair starts with a concrete
   production failure and a measurable benefit.

VoiceOver stays off the requested work list. Preserve its historical failure and
existing phone limitations without inventing a pass. No further framework or
model installation is proposed by this checkpoint.
