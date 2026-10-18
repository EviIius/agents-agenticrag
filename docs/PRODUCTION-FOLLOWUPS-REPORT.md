# Production follow-ups report

18 October 2026 · `codex/production-followups` · based on accepted main `e7ffea2b`.

## Summary

The first text send now preserves a title explicitly chosen by the user, including
renames made while the send is being prepared. Untitled chats keep their existing
fallback behavior. Workflows home no longer advertises its disabled Search block.
This candidate is isolated; no agent code, native inference or deployment is part
of the checkpoint. Full QA results are recorded below when complete.

## Done-when checklist

| Item | Status | Evidence |
|---|---|---|
| Reproduce manual-title overwrite before the fix | Pass | Four failures, one passing fallback control in `title-baseline.txt` |
| Preserve title before send, auto-title on/off | Pass | New API tests |
| Preserve rename during assembly, auto-title on/off | Pass | Event-controlled concurrent API tests; database transaction reads ownership |
| Preserve search index and Markdown export title | Pass | Same API tests |
| Retain default fallback and follow-up title | Pass | New untitled-chat control |
| No extra title request for user-named chat | Pass | Exactly one fake answer request, context-only options and no think override |
| Browser rename/send/complete/reload | Pass in focused run | Two Chromium/iPhone-profile WebKit checks and synthetic screenshots |
| Remove unavailable Search promise | Implemented | Production component also used by existing `/design?workflow-home` states |
| Full check, browser and build gates | Pending | Results below |
| Main/live preserved | Pass at initial verification | Hashes, native connection guard and healthy local/verified HTTPS |

Artifacts are under `artifacts/production-followups/` unless stated otherwise.

## Changed files

- Server: add a persisted `title_source='fallback'` condition to the existing
  first-message fallback-title CASE, inside its existing transaction.
- Web: remove “search” from Workflows home's introductory sentence.
- Tests: add five synthetic API cases and one real browser flow per engine.
- Docs: plan/report, current deferred status, authorization and retained evidence.

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
- Full suites/build/preservation: pending completion.

## Gates G-1–G-16 and core C1–C16

| Gates | Evidence / applicability |
|---|---|
| G-1/G-2 | Full check/browser results pending; focused regressions above |
| G-3 | Existing tests unchanged; new test import correction retained separately |
| G-4 | Build/bundle result pending; unchanged budget 256,000 gzip bytes |
| G-5/G-13/G-14 | Existing contrast/motion/design states; home copy uses production component |
| G-6/G-7 | No API or migration change; existing additive/schema tests in full check |
| G-8/G-9 | All prompts and search/runs/providers source unchanged; no native eval claim or triggered G9 source change |
| G-10 | Existing golden tests plus new explicit request/call-count assertions |
| G-11/G-12 | Synthetic captures, privacy/preservation and live-health records; no publication |
| G-15 | No migration; rollback rehearsal not applicable to this checkpoint |
| G-16 | No new physical-phone acceptance claimed; review precedes release |

Full suites retain core chat, Search/Library, documents/transcription, images,
workflows, backups, parameters, privacy, keyboard and motion checks. Their final
results and preservation of generated historical outputs must be recorded before
this checkpoint is called complete.

## Screenshots

`browser/preserved-title-{chromium,webkit}-fake.png` contains only synthetic fake
runtime text. The phone layout intentionally hides the title in its top bar;
the browser assertions and saved API title establish preservation, not the still
image alone. Workflows design captures from the full run are archived separately.

## Next steps and open questions

1. Review and release only these two repairs after all gates pass. Main and live
   remain unchanged until the release decision.
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
