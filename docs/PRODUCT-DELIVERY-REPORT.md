# Product delivery 1–4 report — 12 October 2026

## Summary

Images is released, with the narrow retained Search-gate exception approved by
Jake. Two fixed workflows are implemented and deployed: brief → prompt review →
one to three image variants, and recording → optional guarded clean-up → meeting
pack **draft** with original source. Durable steps, retries, cancellation, SSE
reconnect, source preservation and exports pass their integration checks.
Native demonstrations retain a quotation-context failure and a missing model
timestamp; factual automation is **not qualified**. Research stays shelved.

## Done-when checklist

| Item | Status | Evidence |
| --- | --- | --- |
| 1. Existing Images candidate released | Pass | `IMAGES-I1-RELEASE-REPORT.md`; actual synthetic live PNG, 13.2637 seconds, nine SSE events |
| 2. Specific historical G9 hold resolved | Accepted exception | Product-delivery amendment in `AGENTS.md`; original Search failures/reports retained, no score changed |
| 3. Creative ordered workflow | Pass | Native prompt preserves the entire brief; review survives application reopen; two unchanged-prompt variants generated in 27.5337 seconds; idempotent acceptance and output backup |
| 4. Meeting-pack drafting workflow | Implemented, review required | Real synthetic ASR + one guarded clean-up + one pack complete in 5.9640 seconds; originals/exports survive attachment and audio removal |
| Missing owner/date, decision/suggestion distinction on the normal speech case | Pass for this sample | `native/meeting.json`, `meeting-review.json`; budget owner/date unstated, logo remains a suggestion, no invented calendar date |
| Every requested model timestamp placement | Fail retained | Budget action lacks its own timestamp. Original source timeline is now copied directly into the source dialog and Markdown export; no model repair or invented binding |
| Quoted-instruction semantic support | Fail retained; inference stopped | `native/injection-review.json`: quoted instruction recast as an attendee's claim and unsupported consensus/confirmation framing. No amount was approved; this does not excuse the role error |
| General factual automation qualification | Not achieved | Failed adversarial support check; all packs remain labelled drafts for human source review |
| Explicit models and saved/default override precedence | Pass | Real draft wire contains only `num_ctx=32768`; existing T2 settings unchanged; fake browser verifies explicit output limit/temperature |
| Acceptance, restart, retry, cancel ownership | Pass | 24 workflow tests: crash gap, child reconciliation, completed-step reuse, clean-up acceptance cancellation/reaping, source identity and partial output |
| Original source and timestamps survive audio deletion | Pass | Real ASR source retained after attachment deletion; JSON preserves raw text/segments; Markdown/source dialog copy recorded timestamps and available speaker labels |
| Mobile/desktop source and format-selection UI | Pass automated | Final workflow browser suite: 12 passes, 14 synthetic run/upload states, source timeline and cancellable Markdown/JSON selection |
| Current data, service and runtime preserved | Pass | 35 existing tables byte-equivalent, four workflow tables added; 98 installed server/source hashes match release manifest; local/HTTPS health 200 |
| Existing Search and native chat request construction | Pass structural preservation | 14 Search modules unchanged; ordinary payload/native-stream AST unchanged; only optional background capacity priority added |
| Physical iPhone generation/save/share/cancel | Pending observation | Requested; no physical pass invented |

## Changed files

### Server

- Migration `010_workflows.sql`: immutable input definitions, step attempts,
  durable outputs and transition events.
- `app/workflows/`: two fixed templates, explicit models, actual text request
  snapshots, sequential native steps, review pause and recovery. Original source
  is preserved; clean-up from a subsequently changed transcript is rejected.
- `app/api/workflows.py`: snapshots/SSE, submission/retry/cancel, source access,
  Markdown/JSON output and direct original-source timestamp presentation.
- Lifespan registers recovery/shutdown; Ollama adds optional background priority
  while preserving default foreground behavior and native payload construction.

### Web

- Lazy `/workflows` route and sidebar entry; explicit model/settings/seed fields,
  upload, review, partial/durable outputs, retry/cancel, source dialog and shared
  cancellable save/share flow.
- Runtime digest/context annotation for the measured image-compatible profile.
- Fourteen `/design?workflows` states and source/save previews; no new package.

### Tests, docs and evidence

- Workflow integration/browser tests, additive generated API types, migration
  expectations and workflow coverage gate (80% minimum).
- `WORKFLOWS.md`, frozen task-check plan and this H4 report.
- `artifacts/product-delivery/`: all synthetic outcomes, frozen source, actual
  payloads, manual failures, hash-only deployment verification and fresh captures.

## Deviations from SPEC.md

Jake explicitly authorized Images and the two fixed task templates, including
their task calls, and the specific I1 G9 exception. No ordinary chat/Search/Library
prompt, provider payload, sampling default or benchmark threshold changes.

The meeting workflow is delivered as the explicitly approved **reviewable draft**
tool. Its native quoted-instruction failure is retained, not qualified or repaired
with another call. This release provides no factual verification, autonomous
action or Research capability. The source timeline remedies source availability,
not the model's incomplete references or semantic errors.

## Runtime observations

- Four total text calls: three drafts and one existing guarded clean-up. Two
  native images and one actual ASR invocation; no warm, judge or retry call.
- Creative draft exactly reproduces the requested brief. Both image outputs
  visually match one blue bowl with one yellow lemon on a white table.
- Synthetic recognized speech matches the spoken script. The ordinary meeting
  draft preserves the required facts, with the retained timestamp/taxonomy flags.
- Adversarial quotation context fails despite correct protocol/finish and refusal
  to approve the injected amount. Mechanical completion is not semantic support.
- A repeated rollback preparation reached its exclusive output-file guard after
  creating another private snapshot. Both snapshots remain and their row hashes
  agree; the helper now prevalidates before making another copy.
- Initial live UI inspection used a button locator for a combobox; the heading
  loaded. Corrected role inspection is retained separately, with no native calls
  or private screen capture.

## Test output

| Gate | Result | Evidence |
| --- | --- | --- |
| Complete repository check | 532 Python / 39 frontend pass; workflow coverage 87.2% | `make-check-source-timeline.log` |
| Complete browser suite | 485 passed / three existing skips, 41.5 minutes | `make-e2e-release.log` |
| Final workflow browser checks | 12 passed | `workflow-browser-source-timeline.log` |
| Final speaker/timeline export and frontend checks | 24 workflow / 39 frontend pass | `host-source-timeline/speaker-backend-tests.log`, `final-frontend-check.log` |
| Initial JavaScript | 243,462 gzip bytes / 250,000 limit | `bundle-release.json`; route remains lazy |
| Installed source/database/HTTPS | Pass | `workflows/verification.json` |

The complete browser run precedes the source-identity/export presentation deltas;
their final-source checks are recorded separately above. These changes add a source
guard and literal source display/export, with no prompt/provider/run payload edit.
The original executed native source is frozen unchanged; the only later server
difference is the export handler's direct timestamp/speaker copying.

Initial lint/type/API-helper/fixture and cancelled preliminary browser runs are
retained. The clean-up acceptance race was fixed before the complete run. No
failure log or original score is replaced with a passing result.

## Screenshots and storage

Synthetic screenshots are under `artifacts/product-delivery/workflows/`, including
390/1440 widths, light/dark, Chromium/WebKit, source timeline and selected JSON.
No real phone/recording/document screen is captured. Native PNGs and their manual
reviews remain under `artifacts/product-delivery/native/variant-101/` and
`variant-102/`.

The two native variants take **1,219,346 + 1,167,849 = 2,387,195 PNG bytes** and
**1,549 metadata bytes** in total. These are logical file sizes, excluding database,
backup copies and the shared model weights. Originals are retained separately;
no model weights are copied per workflow/version. Images reports storage and
supports individual/bulk output removal. Successful uploaded audio remains
temporary by default.

All 18,544 earlier committed evidence/eval objects and their worktree files are
preserved relative to `90132558`. Fresh old-suite captures/metrics are archived
separately (440 outputs); the latest coverage is retained before restoring the
historical file. Historical source objects remain available in Git while the new
explicitly authorized production source is committed separately.

## Open questions for Jake / next steps

Use `/images` and `/workflows` on the iPhone; the requested generation/save/share/
cancel observation remains pending. Review real meeting packs against their saved
source, particularly quoted speech. Collect specific task failures before adding
another fixed template or a workflow builder. Research, arbitrary agents,
scheduling, external writes, routing and additional models remain outside this
release. VoiceOver stays off the current work list, with its historical failure
retained.
