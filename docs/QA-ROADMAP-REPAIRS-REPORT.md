# QA roadmap repairs — checkpoint 1 report

## Summary

Implements the reviewed repair checkpoint on `codex/qa-roadmap-repairs`, based on
accepted main `74eae6d8`. Candidate is `51bfae4a`, with application code unchanged
from `1a2224d9` (initial repair `42beb377`). The original Claude
document and Run log are unavailable; Jake's pasted summary supplied the claims
to investigate. Full checks and the complete browser suite pass. The installed
app is unchanged; this checkpoint is ready for review before publication.

## Done-when checklist

| Item | Status | Evidence |
| --- | --- | --- |
| Rejected draft recovery | Fixed; focused checks pass | Failing baseline, `composer-drafts.test.ts`, `qa-repairs.spec.ts`, original C1 rejection matrix |
| Unsupported thinking values | Fixed; synthetic API/wire checks pass | Invalid values rejected with 422 before a message/model request; supported values/default omission preserved |
| Document Start input | Fixed; PDF/DOCX graphs complete | Original 422 reproduced; extracted document metadata accepted; plain text still rejected |
| Embedding/image conflict | Manual recovery fixed; admission limits preserved | Loaded embedding Eject is enabled; fake API preserves preferences and Library settings; original residency tests pass |
| Auto label and stale-level recovery | Model default; accessible reset | Actual Tools menu checks in both engines, including switching to a model without thinking controls |
| Long thinking | Guidance and existing cancellation | Warning after one minute; retrieval time excluded; Stop reply calls existing active-run cancellation once |
| Aether rename | Display/export/PWA labels implemented | Shared display config, metadata and export labels; internal identifiers remain compatible |
| Full check | Passed on frozen candidate | 686 Python / 126 frontend / 110 contrast pairs; `check-final.txt` |
| Complete browser run | Passed on frozen candidate | 711 passed / three existing skips / zero failed; `e2e-full.txt` |
| Installed app preservation | Verified unchanged and healthy | 102 baseline file hashes match, same PID 97687, local/HTTPS health 200; `installed-before.json`, `installed-after.json` |

## QA findings and severity

| Finding | Diagnosis and repair | Limit |
| --- | --- | --- |
| P1 rejected source draft loss | The optimistic clear survived unmount, while the late rollback returned before restoring the source draft. Per-draft submission ownership and subscriptions restore it across remounts. Editing, including an intentional clear, invalidates the old submission. | The exact claim that a different new-chat draft was wiped did not reproduce in the baseline test; that draft survived. The related source-draft loss did reproduce. Both drafts are checked after the failure resolves. |
| P1 unsupported thinking changes meaning | The adapter selected the first supported option for invalid values. Validate merged preferences before admission, validate saved defaults, and guard the wire adapter. | No direct native `high` experiment was run. Raw Ollama's fallback behavior is a Claude-reported observation, not independently qualified here. |
| P1 Document workflow rejected | A Start field expected kind `document`; attachments use kind `text` plus extracted-document metadata. Accept that representation and reject text without the metadata. | This repairs file input validation. It does not enable the separately gated Read a document block. |
| P2 embedding prevents images with unusable recovery | Settings already fetched non-chat models, but Eject was disabled for every non-chat model, even while loaded. Enable explicit Eject when loaded and identify embedding use. | This is manual release, not automatic unloading or new mixed-model memory qualification. Library/search can reload its embedding model on a future request. |
| P2 long reasoning | The stream can keep producing reasoning; the idle timeout is not a total-thinking deadline. Add truthful guidance and an accessible existing Stop action. | No hard thinking limit, guaranteed final answer, hidden continuation request or speed/accuracy improvement is claimed. |

The native model scores, word-perfect transcription assertion, Linux failure
causes and specific latest-stable release claim in Claude's summary are not
verified without the original run inputs/log. Existing grounding limitations and
failed qualification reports remain applicable. Structural/UI passes do not
establish factual correctness.

## Changed files

- **Server:** providers' thinking validation, merged/saved preference validation,
  workflow input matching, image-admission error guidance and display-only export
  labels. No migration, provider sampling/default, production prompt, runtime,
  model installation, automatic unloading or new inference call.
- **Web:** submission-owned reactive text drafts, Models Eject eligibility and
  embedding label, Model default wording, long-thinking guidance/Stop and clock,
  display/PWA/export labels; synthetic design states for long thinking and stale
  thinking overrides. Tools and Chat controls keep reset available after a model
  capability change; the menu adds no unsupported runtime option.
- **Tests:** 13 new synthetic server cases, five frontend draft ownership cases,
  six new browser cases per engine. Four existing tests update expected display
  names/export labels. One existing Studio contrast test adds actual workflow,
  model-metadata, saved-theme and opacity readiness; its color/axe assertions and
  deadline remain unchanged. No release threshold is loosened.
- **Docs/evidence:** reviewed scope, this H4 report, current deferred-work status
  and `artifacts/qa-roadmap/repair-1/`.

## Deviations from SPEC.md

User-approved roadmap changes the display name to Aether and explicitly rejects
unsupported reasoning rather than silently substituting a different value. The
clock remains a presentation subscription, not backend polling. The warning
does not append anything to saved message content.

An Answer now action would need a separate request contract and evaluation;
cancelling the current stream cannot itself guarantee a final answer. This
checkpoint exposes the existing stop operation and preserves user settings.

## Runtime observations

All test inference is scripted/fake. No installed Ollama/image/transcription
generation, load or unload was requested. Models are identified by metadata;
image digest/context/size/count limits are unchanged. Internal `workbench`
paths/service identifiers, `atelier.workflow/1`, local-storage keys, existing
model aliases, port 8787, loopback binding and Tailscale remain unchanged.

The pinned Ollama 0.35.0 source handles the empty-message, zero-keep-alive unload
request before chat capability checks. This supports using the existing explicit
Eject endpoint for an embedding model without asking it to generate chat text.
[Ollama 0.35.0 ChatHandler](https://github.com/ollama/ollama/blob/v0.35.0/server/routes.go#L2509).
This is a source compatibility check, not a new native unload or image-memory trial.

The installed baseline and final inspection have PID 97687 and healthy local/
normally verified HTTPS responses. All 102 recorded installed server/config
hashes match; final inspection is read-only. An inspection using framework Python initially failed because its CA
store could not validate the certificate. System curl with ordinary certificate
verification succeeds; no certificate bypass or server change was used.

## Test output

- Corrected baseline: five server failures and one negative-control pass;
  two browser failures reproduce source-draft loss and disabled embedding Eject.
- First baseline harness had an invalid chat-create field and an incorrect Models
  tab locator. Correcting them retained the intended assertions and reproduced
  the actual defects. Initial sources and both logs are preserved.
- Focused server/API plus existing image residency checks: **23 passed**.
- Send/motion plus draft/Eject browser checks: **42 passed**, both engines.
- Working-indicator plus four initial QA browser cases: **26 passed**, both engines.
- Final five repair browser cases: **10 passed**, both engines, including actual
  fake-run cancellation and retrieval/think timing separation.
- Self-review found that rejecting a stale level after switching to a model with
  no thinking controls could hide the way to reset it. The added regression fails
  in both engines before correction and all **12 focused repair checks pass**
  afterward. The explicit override remains visible and resettable; invalid values
  are still rejected. No implicit substitution or new runtime level is added.
- The first complete browser attempt on `42beb377` is intentionally interrupted
  after **198 passes**, one interrupted case and 513 unrun cases, so the correction
  can receive a fresh complete run. Preserve its log/source manifest; it is not a
  full browser pass or a failure blamed on machine speed.
- The next full attempt retains **351 passes, one failed Studio canvas contrast
  scan, one interrupted case and 361 unrun cases**. Its trace records the app
  entrance still active; observed foreground colors are partially transparent
  blends of the passing steady-state tokens. The test scanned before app/model
  readiness and forced DOM theme independently of saved preferences. Strengthen
  readiness rather than alter product colors, axe rules or thresholds. **20
  repeated checks pass** after the correction (ten per engine, both themes).
  Source, trace, diagnostic and interrupted log are retained.
- Preliminary full check: **679 Python / 126 frontend / 110 contrast pairs**;
  includes the initial six new server cases. Seven additional server cases were
  then added for the final full invocation below.
- Complete `make check` on the application recovery correction: **686 Python / 126
  frontend / 110 contrast pairs**; types, formatting, coverage, API additive,
  motion and privacy guards pass. The first candidate's identical counts are
  retained separately. The final repeat including the readiness-test correction
  also passes with the same counts (`check-final.txt`).
- Final complete `make e2e`: **711 passed / three unchanged skips / zero failed**,
  all 714 scheduled tests on `51bfae4a`, Chromium and iPhone-profile WebKit,
  in one complete invocation (`e2e-full.txt`, about 1.2 hours). No assertions,
  quality thresholds or existing skips were relaxed to achieve this result.
- Final frozen build: **254,975 initial gzip bytes**, budget 256,000; +527 bytes
  versus accepted main's 254,448, below the unchanged 8,192-byte increment limit.
  All 425 build hashes are retained in `build-manifest.json`. The earlier
  254,957-byte build is retained separately.
- Final source/build verification: all **560** frozen source/test/config files
  and all **425** built files match their manifests. The first build observer
  incorrectly looked in `web/dist`; correcting it to the configured
  `server/app/static` resolves the absent-path result. No product source change
  or rebuild was needed (`source-build-final-verification.json`).

Failed logs and baseline sources are retained. The full run's **1,605** changed
historical artifact files and **40** new historical-path screenshots are copied
with verified hashes to the private archive
`~/.local/share/workbench/qa/qa-roadmap-20261016/full-browser-output/`.
Original tracked evidence is restored byte-for-byte; no historical artifact diff
remains. The archive manifest hash and counts are retained in
`historical-evidence-preservation.json`. New checkpoint evidence stays in
`artifacts/qa-roadmap/repair-1/`. Raw command logs retain their original whitespace,
including reporter trailing spaces and final blank lines; the source/documentation
`git diff --check` excludes these raw `.txt` logs and passes. No raw test result
is reformatted to make a formatting check pass.

## Screenshots

`artifacts/qa-roadmap/repair-1/browser/` contains synthetic draft recovery,
embedding Eject and long-thinking captures. The first viewport capture of the
long-thinking fixture did not include the lower-page warning, so a separate
read-only observer captures the actual warning element.

The first observer wrongly applied the phone's 44 px target minimum to the
desktop's 36 px primitive and stopped. Its failure is retained. The final
observer checks the existing desktop/mobile requirements, records measured
dimensions/errors before assertions, blocks all API writes and performs no
native inference. An initial module-import path error is also retained.

## Rename checklist

- Aether display name, document title, Apple web-app title, PWA name/short name,
  sidebar/settings/welcome/error text and new download labels.
- Preserve existing A icon, server label, internal schema/storage keys, source
  filenames, saved outputs, model aliases and service/network identity.
- Existing manually named Home Screen bookmarks may retain their old label;
  no physical iPhone rename/update pass is claimed.
- Public naming availability is not qualified by this display change.

## Next steps and review

All checkpoint gates above pass. Review draft PR #3 before publication. A live
release includes server changes and needs the established backup/restart/health
procedure, followed by phone acceptance. Do not treat this branch as deployed.

After that, scope the remaining workflow blocks and bounded read-only chat tools
as separate checkpoints with host-enforced permissions, step/time budgets,
source provenance and held-out quality/injection evaluations. Tool-call validity
is not answer-quality qualification. Routing follows only when task-specific
comparisons justify it; no model name supplies a capability or quality heuristic.

Research remains shelved. VoiceOver remains excluded with its historical failed
observation preserved. No new product scope or native experiment is started here.

## Open questions for Jake

None needed to implement the repair checkpoint. Review is required before its
publication and before advancing to a separately specified tools/routing phase.
