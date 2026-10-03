# Phase 3 report

## Summary

Phase 3 implements the command palette, installable PWA shell, update prompt, read-only legacy import and deployment tooling.
Finished message rows are memoized; streaming and long-chat budgets have synthetic browser measurements.
Transcription source now lives under the Workbench repo. Audio copies are temporary by default; saved transcript outputs remain available.
**Deployed; physical acceptance pending.** Workbench is running under the existing launchd identity. Audio cleanup freed 1,434,891,416 bytes while preserving both existing transcripts and all six output downloads. Physical iPhone installation, human keyboard review and warm-load acceptance remain open; Phase 3 is not complete. Jake reported VoiceOver did not work and deferred it for this build; it is a known limitation, not a release blocker.

## Done-when checklist

| Item | Status | Evidence (test name / file / screenshot / command output) |
|---|---|---|
| Command palette: chat FTS and seven actions | Passed browser verification | `polish.spec.ts`, `CommandPalette.tsx`; `/design` includes ready/empty/loading/error |
| PWA manifest, public shell cache and update prompt | Automated verification; phone installation pending | `pwa.spec.ts`; API responses never cached; Chromium offline navigation and both engines' update/privacy checks |
| Accessibility: all screens, both themes, keyboard | Passed automated audits | Existing screen audits plus `phase3-accessibility.spec.ts`; loading/error listbox semantics and citation focus/close corrected |
| iPhone VoiceOver | **Reported failure; deferred by Jake** | 3 October user report; failure mechanism not diagnosed, support not claimed; release gate waived by user amendment |
| Human keyboard walkthrough | **Pending review** | Automated keyboard walkthrough passes; a human check is still separate |
| Initial JS ≤250 KiB gzip | Passed: 224,491 bytes (219.2 KiB) | `artifacts/phase-3/bundle.json`; recursive static imports, heavy lazy renderers excluded |
| Warm Tailscale iPhone interactive <1.5 s | **Pending physical measurement** | The app records `workbench:time-to-interactive`; desktop/headless timing cannot establish the iPhone budget |
| Streaming ≤8 ms/frame at 100 tok/s, only streaming row renders | Passed isolated measurement | `performance.spec.ts`, `performance-chromium.json`, `performance-webkit.json`; terminal history synchronization excluded from streaming sample |
| 300-message scrolling at ~60 fps | Passed isolated measurement | 119 animation-frame samples per browser, medians 16.7/17 ms and p95 16.8/18 ms; finished rows use `content-visibility: auto` |
| First-token overhead ≤150 ms versus raw fake runtime | Passed isolated measurement; browser rendering check passed | `ttft-overhead.json`: paired HTTP samples, max 7.15 ms; `first-token-*.json`: runtime-emission-to-UI delay 74.75 ms Chromium / 69.84 ms WebKit |
| Legacy import idempotent, read-only, linear chain, title retained | Passed | `test_legacy_import.py`: source database/WAL/SHM hashes and mtimes unchanged; committed WAL data imported, concurrent/idempotent behavior, invalid input rolls back; actual legacy schema read check in `legacy-readonly-live.json` |
| Delete legacy source; retain old installed data | Implemented | `legacy-removal.json`: 92 source files removed, zero data files; recoverable branch/tag retained |
| Architecture and setup/run/deploy/rollback docs | Written | `architecture.md`, `README.md` |
| launchd installation and phone confirmation | **Deployed; phone confirmation pending** | `deploy.py`, `test_deployment.py`, `deploy-plan.json`, `deployment-verification.json`; existing label/bind/Tailscale route retained |
| Transcript-preserving audio cleanup | Passed synthetic and live storage checks | `test_temporary_audio_keeps_outputs_and_bulk_clear_skips_active`, `audio-storage.spec.ts`, `storage-after-deployment.json`; startup cleanup, opt-in retention, active-job exclusion and idempotence |

## Changed files

- **Server:** audio availability migration/schema/API, temporary-audio lifecycle and bulk storage cleanup; legacy import migration, read-only importer and API; operational config.
- **Web:** command palette and shortcuts; PWA registration/manifest/icons/service worker; legacy import UI and `/design` states; transcription retention/storage controls and removed-audio states; memoized message rows, streaming announcements, citation keyboard focus and focus preservation after a first send.
- **Deployment/tools:** `scripts/deploy.sh`, `deploy.py`, `measure_bundle.py`, `import_legacy.py`, launchd template and Makefile target.
- **Engine:** public `transcribe/` source vendored from Transcription commit `1019564`; weights/config/glossary/interpreter ignored. Source repo remains intact; installed engine belongs inside `app/transcribe`.
- **Tests:** storage/import/deployment unit and API tests; palette/PWA/performance/accessibility browser cases; synthetic latency script. Deleted the independent `legacy/` source tree.
- **Docs/evidence:** README, one-page architecture, user amendments in AGENTS/SPEC/transcription spec, this report and synthetic `artifacts/phase-3/` files. Earlier phase evidence is preserved.

## Deviations from SPEC.md

- The user prefers the engine under Workbench. Public source is vendored in the repo and the deployed copy sits inside the installed app; private runtime assets remain outside Git. No dependency or model-call addition.
- The user requested transcript outputs without long-term recordings. Successful uploads are released by default, including historical completed uploads at startup. Failed/cancelled uploads remain for Retry until cleared or their unsent expiry. Completed unsent transcripts are preserved indefinitely until explicitly removed.
- Playwright WebKit's offline reload returns an internal navigation error. That one offline-navigation test is skipped with its reason; worker install/cache privacy/update checks run on both engines. Physical Safari offline verification remains open.
- Jake reported VoiceOver did not work and explicitly deferred it for this build. Its physical acceptance gate is waived by his amendment; the issue remains recorded and was not diagnosed.
- Optional presets and PDF attachments are deferred. T2 cleanup/glossary editing and Part F agents are outside this phase.
- Failed exploratory runs remain attached for transparency; only the final green run is acceptance evidence. Physical iPhone gates cannot be replaced by emulation.

## Runtime observations

- The vendored real engine passes its doctor checks and 44 tests. Public source and installed private assets are separated; no real audio/name/transcript is committed or used in screenshots.
- Native Ollama sampling/capability behavior is unchanged from the accepted Phase 2 evidence. Phase 3 does not claim universal answer accuracy or add model calls.
- The installed package's Documents-folder restriction motivates installing under `~/.local/share/workbench/app`; the original engine repository and old installed legacy database remain intact.
- A read-only compatibility check of the actual legacy source read three conversations/six messages including its WAL. Database/WAL/SHM stayed unchanged; no chats were automatically imported and no content was logged.
- Deployment retains `dev.agenticrag.workbench`, loopback port 8787, one worker and the existing Tailscale route. `/api/health` is HTTP 200, `/design` is HTTP 404 in production, the standalone manifest is served and the engine is ready under `app/transcribe`. A consistent database backup and original plist are saved privately. New engine workspace folders are empty/private; original watched recordings were not copied.
- Startup released two uploaded copies totaling 1,434,891,416 bytes (1.43 GB / 1.34 GiB). A private pre-deployment digest confirms transcript text/raw text/segments/metadata are unchanged. All six existing text/SRT/JSON downloads return HTTP 200; removed audio returns HTTP 404. Original user files remain untouched.
- The deployed launchd subprocess also transcribed generated synthetic speech, removed its audio and retained all three exports; its temporary test attachment was removed afterward (`live-synthetic-transcription.json`).
- Actual Tailscale HTTPS fresh-context readiness on this host: Chromium 88.8–114.1 ms; WebKit 106–119 ms across three samples each (`tailscale-headless-warmload.json`). This is **not physical iPhone evidence** and cannot close the phone performance gate.

## Test output

- `make check`: 207 Python tests; 36 frontend tests; lint/types/API types and 56 contrast pairs pass in the current run. Coverage: providers 85.8%, runs 89.2%, search 88.9%, transcription 90.7%.
- Vendored engine: 44 tests pass (`engine-tests.txt`).
- `make e2e`: full run recorded **220 passed, 1 failed, 3 skipped** in 14.3 minutes (`e2e-final.txt`). The failed WebKit case uploaded while the attachment menu still held its modal state. The fixture now explicitly focuses/closes that menu before upload. Its complete format/cancel/download case passes on **both engines, 2/2** (`e2e-download-closeout.txt`). Thus **all 221 runnable cases are covered by passing results across the full run and targeted closeout**, with no unresolved automated failures; this is not a claim that one monolithic run returned green. Earlier failed runs remain attached.
- The three skips are the duplicated WebKit real-time timeout gate (Chromium runs it), WebKit clipboard fixture limitation, and WebKit offline-navigation engine limitation. Physical Safari offline review remains open. Worker privacy/install/update checks pass on both engines.
- Dedicated keyboard walkthrough and pre-response Escape: **4/4** (`e2e-keyboard-final.txt`). New ready/empty/loading/error palette and six import states pass axe in both themes/widths/engines in the full run. Earlier corrections address palette ARIA semantics, citation Escape/focus and first-send focus without changing inference prompts.
- Streaming measurement: Chromium p95 1.3 ms / max 1.6 ms; WebKit p95 2 ms / max 3 ms, only the active message row rendered. Scroll medians 16.7/17 ms; p95 16.8/18 ms. These synthetic measurements are not a guarantee for every physical device.
- Paired fake-runtime HTTP first-token overhead: median 6.42 ms, maximum 7.15 ms across five samples. This excludes browser rendering. The separate runtime-emission-to-UI delay is 74.75/69.84 ms (Chromium/WebKit); adding the maximum measured HTTP overhead gives conservative sample totals below 82 ms, within the 150 ms target. These are local synthetic samples, not a universal latency guarantee.

## Screenshots

All contain synthetic data. Representative screenshots under `artifacts/phase-3/`:

- `palette-ready-390-dark-chromium-fake.png`, plus empty/loading/error in both themes at 390 and 1440 px, Chromium/WebKit.
- `palette-320-light-fake.png`, `palette-1440-dark-fake.png`.
- `legacy-import-ready-390-dark-chromium-fake.png`, plus loading/missing/status-error/importing/failed states.
- `audio-clear-390-dark-fake.png`, `audio-clear-1440-light-fake.png`.
- `update-toast-390-dark-chromium-fake.png`.

## Open questions for Jake

Confirm Home Screen installation/standalone launch, keyboard/composer behavior and the offline connection error. A physical warm-load timing below 1.5 seconds is still needed. Jake supplied a screenshot of the live phone home screen showing the updated audio-removal state; the screenshot is not archived because it contains real recording metadata. It does not establish installation, performance or screen-reader support. VoiceOver is explicitly deferred after Jake reported it did not work. The other checks remain Phase 3 acceptance gates; deployment is already complete.
