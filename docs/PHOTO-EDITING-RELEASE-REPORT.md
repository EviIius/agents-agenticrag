# PE1 photo-editing publication report

21 October 2026. PR #6 merged as `87a1a925`; photo editing is live in Aether.

## Summary

Jake authorized merge/publication after accepting the native edit quality and
reviewing integration preparation. The exact tested backend, compiled UI and
four-file worker are installed with the original service and runtime. A fresh
private production bundle was verified before publication. Existing data passed
the additive schema migration unchanged; physical iPhone acceptance is pending.

## Done-when checklist

| Item | Status | Evidence under `artifacts/photo-editing/release-20261021/` |
| --- | --- | --- |
| Explicit release approval and main merge | Pass | AGENTS.md; `merged-source.json`, PR #6 |
| Merged main equals tested candidate | Pass | All 574 frozen source hashes match |
| Idle service/native lease before shutdown | Pass | `preflight.json`; no user job cancelled |
| Fresh production app/worker/data/plist bundle | Pass | 2,352 private files, manifest reverified |
| Exact installed application/static/worker | Pass | 555 app/shared/lock files including 429 static; four worker files |
| Additive migration 13→14 | Pass | 1,688 rows across 55 pre-existing tables unchanged; integrity/FKs pass |
| Retained non-DB data files | Pass | All 59 files byte-identical before restart |
| Runtime/transcription/selectors/plist/Tailscale unchanged | Pass | Before/after aggregate hashes and exact service/route checks |
| Local and normally verified HTTPS | Pass | Health, workflow definitions/templates, image status, index/SW hashes |
| Live photo-edit capability advertised | Pass | `verification.json`; editing available |
| Actual installed UI at desktop/phone widths | Pass, synthetic API | Chromium 1440 and WebKit 390; `installed-ui.json` |
| Prior evidence and exhausted budgets preserved | Pass | Frozen B/C, integration and PE0 manifests, stopped agent ledgers |
| Physical iPhone upload/edit/save/share/comparison | Pending | Requested from Jake; browser device profile is not a phone pass |

## Changed files

The production application changes are the reviewed PR #6 photo-reference
feature and qualified guard. This release adds documentation and operational
evidence only; no additional product code, dependency, prompt or model change.
`publish_release.py` records the dedicated publication sequence. The generic
deployment command remains blocked for migration 014.

## Deviations from SPEC.md

The approved photo-edit scope adds schema 14 and the reference-aware worker.
Keep the existing port 8787, bind 127.0.0.1, launchd label, plist and Tailscale
route. No framework/runtime/default/sampling change or additional inference was
required. The deployment uses the already verified compiled build from the
isolated worktree; all 574 source hashes match merged main.

The compatibility fallback restores the previous UI while retaining the new
schema-aware backend, worker and **current data**. It is not an old-backend
rollback. Never restore the pre-release database over newer messages/edits.
See `PHOTO-EDITING-RELEASE-RUNBOOK.md`.

## Runtime observations

The original service was stopped only after chat, image, workflow, Library and
transcription checks were idle. The native lock was free. No task was cancelled.
The fresh production bundle is private at
`~/.local/share/workbench/releases/photo-editing-20261021/bundle`; it contains
real application data and must stay out of Git. Its full manifest still verifies.
The earlier synthetic rehearsal bundle was never applied to production.

The four-file installer preserved the image interpreter/model selectors byte
for byte. Only the reviewed app/shared trees were replaced; the 3,542-file server
environment and 33-file transcription tree remain identical. Offline migration
was checked before restarting. All 1,688 pre-existing rows and 59 non-DB files
were preserved. Observed service downtime was **3.948 seconds**.

Local/HTTPS health, image availability/editing, workflows and exact index/service
worker bytes pass. Ollama remains **0.35.0**. No native/model qualification call,
model load, download, automatic chat unloading or user-data mutation was made by
the browser observers. PE0 remains six calls, the separate private edit one, and
PE1-C four plus its single preload. Stopped agent trials remain stopped.

## Test output

The unchanged candidate's completed release gates remain **759 Python**, **132
frontend**, **110 contrast pairs** and **739 browser passes with three existing
skips**, with 83.6% image coverage. They were not rerun broadly after a docs-only
approval change; exact merged/installed source hashes establish payload parity.

The post-publication observer passes in Chromium and WebKit against actual HTTPS
assets. Every API request is intercepted with invented fixtures: reference
upload/preparation, one-image reference-bound submission, completed edit card,
reference/edited comparison, Save control, ordinary draft/typing/Send availability
and Workflows opening pass. There are no observer page errors or failed assets.
Service workers are blocked in these contexts to guarantee interception. Native
share sheets, physical keyboard behavior and actual edit quality are not
established by this observer.

### Retained preparation observations

- GitHub rejected the first merge request because its supplied expected-head pin
  was incorrect. The exact local/remote OID was read, then the guarded merge
  succeeded. No history was rewritten and no server operation occurred on the
  rejected attempt; see `merge-attempts.json`.
- The first installed-UI observer omitted reasoning metadata on its fake vision
  model, then incorrectly expected the Thinking menu. Its source/log are retained.
  Adding that synthetic metadata makes the observer representative; no product
  code or assertion was weakened. The corrected two-browser run passes.
- The observer followed system appearance. Its initial hardcoded screenshot
  filenames said dark; those labels were corrected to system after capture,
  preserving pixel bytes and hashes. This is not an extra dark-theme invocation.
- The earlier full-suite ResizeObserver warnings remain in integration evidence.
  The narrow installed observer has no page errors; this does not resolve those
  earlier warnings or establish a clean physical PWA console.

## Screenshots

Four synthetic installed-UI screenshots are under the release evidence folder:
`editor-1440-system-chromium-synthetic.png`,
`editor-390-system-webkit-synthetic.png`,
`viewer-1440-system-chromium-synthetic.png` and
`viewer-390-system-webkit-synthetic.png`. Codex inspected the phone-width editor
capture; no real photo, recording, transcript or filename is in this evidence.

## Open questions / next step

The release is live. Jake's requested physical iPhone check remains open:
reopen/update Aether, Tools → Edit photo, upload/edit, Show reference, Save/share,
and ordinary typing/sending. The accepted generative limitation remains: faces,
lighting and framing may change beyond the requested edit. Automatic workflows
remain the separately reviewed WS-F/folder-pilot backlog, not part of this release.
