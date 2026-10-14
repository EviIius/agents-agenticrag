# Workflow Studio and chat images — live deployment report

## Summary

The reviewed main checkpoint `93b1fd21` is live at the existing Tailscale URL.
All 556 frozen source/test files match CI-C's fully tested `f8e301c2` application.
The private full application/data/plist fallback was verified and its whole-data
restore rehearsed before publication. The service became healthy after 1.604 s.
Jake explicitly approved this release's narrow G9 exception; factual grounding
is still unqualified, and factual workflow outputs require human review.

## Done-when checklist

| Item | Status | Evidence |
| --- | --- | --- |
| Publish reviewed source and build | Pass | `publication.json`: 556 frozen files, 113 installed server files and 420 current-build static files verified |
| Full private fallback | Pass | Whole installed app, whole data directory and exact original plist; consistent private SQLite backup; fallback path below |
| Combined upgrade and whole-backup restore | Pass | Private copied data: candidate schema 10 → 13 starts; 45 pre-existing table projections unchanged; restored schema 10 starts with prior application, 1.561 s rehearsal |
| Production migration preserves old data | Pass | All 45 pre-existing column/row projections compared while quiescent, before service bootstrap; all old messages initially kind=text; schema 13, integrity/FKs pass |
| Fixed service identity and route | Pass | `dev.agenticrag.workbench`, one worker, `127.0.0.1:8787`; exact original plist and Tailscale serve output unchanged |
| Existing runtimes and workers | Pass | 3,542 non-cache venv files and 33 transcription files match prior snapshot; image worker selector preserved; Ollama still 0.35.0 |
| Local and HTTPS checks | Pass | Health, graph definitions/templates, available image engine, exact new index/service-worker hashes; `/design` is 404 on both origins |
| Published desktop interface | Pass | Actual HTTPS Chromium: Workflows home/canvas, chat Image mode and 2-image selector, Gallery; zero page errors/inference requests in completed desktop check |
| Published phone-layout interface | Pass on instrumented recheck, with retained initial flag | Actual HTTPS WebKit at 390 × 844: Outline, chat Image mode/count and Gallery; zero page errors/inference requests; unclassified earlier flag retained below |
| Physical iPhone | Pending | Asked Jake after rollout; no physical check or VoiceOver pass invented |
| G9 | Specific release exception accepted; not an accuracy pass | Jake's “Then go ahead” accepts the explained scoped exception; ordinary prompts/request parity retained, no new accuracy eval |
| Privacy | Pass, with normal audit limits | No real filename/text/media capture; live browser takes no screenshot/video; all data snapshots outside Git; changed-file audit passes |

Evidence directory:
`artifacts/workflow-studio/live-deployment-20261014/`.

## Changed files

- **Product server/web:** no further source changes after the reviewed CI-C
  candidate. The new build is installed; prior hashed assets are retained for
  already-open clients. Existing interpreters, transcription config/glossary/
  weights and image worker/weights are preserved.
- **Documentation:** `AGENTS.md` records the scoped deployment authorization;
  this H4 report records publication and limitations.
- **Evidence:** public publication/manifest/commands/build/browser summaries.
  Private one-off control sources, failed attempts and complete snapshots remain
  outside Git. No private database or user file is included in repo evidence.

## Deviations from SPEC.md

The exact working plist and already-matching frozen server environment were
preserved rather than re-rendered/reinstalled. The existing deploy script was
not rewritten: the approved one-off rollout preserves complete app/data and
has whole-backup restoration for failure. Old hashed assets remain available.
G9 has a specific user-approved release exception, not a broad exemption or a
claim that model grounding improved. Physical phone review follows deployment.

## Runtime observations

- Local and normally verified Tailscale HTTPS health return 200.
- New workflow definition/template APIs and image engine status respond on
  both origins; the copied-data lifecycle checks and live UI checks execute no
  inference. Temporary synthetic workflow definitions are archived after checks.
- The launchd Python process restarted while its original environment and
  runtime interpreter remained the same. No model/default/sampling/prompt change,
  native image generation, Research experiment or WS-E work was performed.

## Test output and retained attempts

- Applicable frozen-source evidence: **654 Python / 104 frontend checks** and
  one complete **615-pass browser invocation**, three existing skips; build
  passes. The completed native control pair also remains applicable. No broad
  suite rerun is claimed for this installation-only operation.
- Fresh locked production build passes; initial JS is **247,594 gzip bytes**,
  below the 256,000-byte budget. Current artifact hashes match the installation.
- Whole database/data restore and prior/candidate startup on the private copy
  pass; production old-column projections, integrity and foreign keys pass.
- First snapshot preflight stops **before live bootout**: read-only SQLite
  inspection creates an empty WAL and 32-KiB SHM in the private backup, changing
  its whole-directory manifest. Explicit connection closing and removal of only
  empty private sidecars restores the original exact manifest. Database SHA and
  all old-row projections are unchanged. Original control source/log retained.
- First browser observer incorrectly looks for the name textbox before rename
  mode is opened. The title is a button until clicked. Correcting this observer
  preserves the product source; the first failure is retained.
- Second browser attempt passes desktop controls, but the phone case reports a
  page-error/unintended-request flag without retaining the original event detail.
  The instrumented phone recheck passes with zero page errors and zero inference
  requests. This does **not** establish the initial flag's cause or a product fix;
  both results are retained. Request physical phone observations and investigate
  any recurrence rather than representing every smoke attempt as green.

## Screenshots

No live screenshots: the sidebar/Gallery can contain private user material.
Previously reviewed synthetic CI-C and native-control screenshots remain the
visual evidence; the new live DOM checks are recorded in browser JSON summaries.

## Fallback and rollback

Private full fallback:
`/Users/evilius/.local/share/workbench/qa/workflow-studio/live-deploy-20261014T220215Z`.
Contains `app/`, `data/`, `service-before.plist`, executed control sources and
private rehearsal/attempt logs. The directory is private (0700); database 0600.

Source fallback: `checkpoint/pre-workflow-studio-2026-10-14` → `dce4c49e` on GitHub.
The source tag alone does not restore a schema-13 database.

The private helper's `rollback` action stops the candidate, preserves its current
app/data, restores the whole original snapshot and exact plist, then bootstraps
the same service and verifies health. Later user work is retained in the saved
candidate data for recovery; no reverse migration or automatic merge is used.
The restore procedure was rehearsed on a data copy, not by reverting the live app.

## Open questions for Jake

Physical iPhone check: reopen/reload Atelier, open Workflows and the chat's Image
mode, then try generating/saving/sharing when convenient. Report any navigation
or keyboard issue. Browser phone geometry is not physical-phone acceptance.
Future WS-E, reference editing and Research remain separately gated.
