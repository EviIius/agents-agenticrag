# Phase T — T1 checkpoint report

## Summary

T1 implements upload → local transcription → transcript review/download → local chat.
Recordings can be added from the picker, drop or paste; unsent recordings return after reload.
The existing Ollama models, parameter controls, port 8787 and Tailscale route are preserved.
The real engine and synthetic large-file checks passed. Jake exercised both desktop and iPhone uploads and accepted their general layout. His iPhone feedback prompted a cancellable format/save dialog and a comprehensive mobile review; Jake accepted the revised native save flow; selected formats now have a brand highlight and checkmark. Upload time and memory pressure remain unmeasured. T2 and Phase 3 have not started.

## Done-when checklist

| Item | Status | Evidence |
|---|---|---|
| T-AC1: engine contract, 44 tests, doctor, private-file exclusions | Passed | Engine commit `1019564`; `artifacts/phase-t/engine-tests.txt`, `engine-status.json`. Real config, glossary and model weights are ignored; no private files tracked. |
| T-AC2: engine unavailable | Passed | `test_upload_limits_disk_headroom_and_pending`; browser T-9; ready/not-set-up fixtures on `/design`. |
| T-AC3: 1 GB progress, memory, over-limit cleanup | Passed | `upload-memory.json`, `upload-memory-run.txt`; actual Chromium XHR upload of **1,073,741,824 bytes**, observed percentages 0–100. `ps` sampled the uvicorn process RSS every 50 ms: baseline **105.20 MiB**, peak **105.39 MiB**, growth **0.19 MiB**, 542 samples over **27.45 s**. Network upload throttled to 40 MiB/s. This measured a warm server; the preceding upload observed 2.25 MiB growth. The small patched-limit integration test returns 413 and leaves no partial file; insufficient disk headroom returns 507 before parsing the body. |
| T-AC4: real `say` engine result and UI/downloads | Passed | `real-engine-check.json`, `real-engine-run.txt`, `real-say-*.png`. Synthetic speech duration **14.88 s**, processing **1.4 s**, **40 words**, **≈78 tokens**, six segments. Browser opened text and timestamp views and downloaded/read all three formats. No actual meeting recording used. |
| T-AC5: transcript context, follow-up, regenerate | Passed | `test_send_context_guard_downloads_delete`; browser T-1/T-2. Fake runtime captures prove the transcript precedes the question and remains in follow-up/regenerate history. |
| T-AC6: refuse sends until ready | Passed | Same integration test: API 422 `transcript_not_ready`; browser T-3: Send disabled while textarea stays editable. |
| T-AC7: reload and server restart | Passed | Browser T-3 reload during the job; `test_jobs_replay_snapshots_retry_cancel_recover_housekeeping` tests persisted interrupted state and retry. Startup removes scratch folders; graceful server shutdown also stores the interrupted state. |
| T-AC8: cancel processes and remove audio | Passed | `cancellation.json`: `pgrep -f <synthetic attachment uuid>` observed PID 41064 before cancel and **no matches** afterward. `pgrep -x ffmpeg` and `pgrep -x whisper-cli`: **no matches**. Real recording removal returned 404 on subsequent file access; integration test verifies physical file deletion. |
| T-AC9: unreadable file and retry | Passed | Fake engine error detail is preserved and shown with Retry/Remove; browser T-4 and engine contract integration test. |
| T-AC10: recording web guard, including forced search | Passed | Integration test replaces the web hook with a failing sentinel: normal chat, follow-up and forced regenerate never call it. Turning the setting off calls the hook. Browser T-5 shows the disabled/off toggle and the separate notice, with no Search anyway action. |
| T-AC11: transcript exceeds model budget | Passed | `test_overflow_silence_glossary_local_only` refuses before generation; browser T-6 shows the warning and clears it after switching from the fake 16K model to the fake 32K model. |
| T-AC12: Jake's desktop + iPhone recordings with Qwen 32K loaded | **Both exercised and download flow accepted; two measurements unrecorded** | Desktop: **717,445,708 bytes**, **1,245.57 s** audio, **30.0 s** transcription, **41.5×** real time. iPhone: **2,945,884 bytes**, **120.35 s** audio, **2.9 s** transcription, **42×** real time. Both ready; screenshots show the configured 32K variant. Exact upload time and Mac memory pressure were not measured. Numbers only in `desktop-recording-metrics.json` / `mobile-recording-metrics.json`; Jake accepted revised native saving on the physical phone. |
| T-AC13: private-content audit | Passed for this checkpoint | Only synthetic fake-engine/`say` audio was exercised. Audio and downloaded JSON remain outside the repo; real engine JSON/glossary content is not in artifacts. The preview log is outside the repo and has no synthetic audio filenames or transcript phrases. `privacy-audit.json` records the audit scope. |
| T-AC14: chat deletion cascades | Passed | `test_send_context_guard_downloads_delete` verifies the audio file and transcript row disappear and sent attachment deletion returns 409. Chat deletion cancels jobs first. |
| T-AC15: cleanup progress, guard, versions and discard | T2, not started | Deliberately outside T1 checkpoint. |
| T-AC16: five-minute real-model cleanup comparison | T2, not started | Deliberately outside T1 checkpoint. |
| T-AC17: glossary editing/validation | T2, not started | Existing engine glossary corrections are displayed in T1; editing follows in T2. |
| T-AC18: design, axe, checks and coverage | Passed | `check.txt`: 199 Python tests, 36 frontend tests, 56 contrast pairs; transcription coverage **90.7%**. `e2e.txt`: **162 passed, two expected skips**. Every T1 state appears on `/design`; screenshots at 390/1440, light/dark. Cleanup/version fixtures belong to T2. |

## Changed files

- **Rules/spec:** `AGENTS.md`, `docs/SPEC.md` gain the verbatim Phase T amendment. Provided transcription specification and supporting patch/guard vectors are retained in `docs/`.
- **External engine:** contract patch, restored `.gitignore`, public engine sources/tests and README contract table in the separate Transcription repository; commit `1019564`.
- **Server:** environment configuration; migration `002_audio.sql`; generated schemas; one shared attachment projection; audio upload/pending/remove API; transcript/status/download/retry/cancel/SSE API; subprocess wrapper and sequential job manager; context insertion, ready/local-only checks, web guard, chat deletion and housekeeping.
- **Web:** XHR upload transport; transcript store and typed SSE subscription; `AudioChip`, `TranscriptSheet`, composer progress/readiness/privacy/starters/context meter; sent-message audio chips and edit notice; Settings → Transcription; synthetic `/design` states.
- **Verification:** fake executable engine, transcription integration/browser tests, migration preservation test, coverage gate, and repeatable synthetic upload/real-engine browser verification scripts under `web/scripts/`.
- **Evidence:** `artifacts/phase-t/` and the consolidated `artifacts/coverage.json`.

## Deviations from SPEC.md

- No added packages. No new model calls in T1. No changes to runtime bind/port, launchd label or Tailscale configuration. Legacy data was not modified.
- Added `recording_requires_local`: the privacy rule is enforced against the connection's loopback address before transcript context is assembled, rather than relying on UI labels.
- Added attachment lifecycle locks across send validation/context assembly/claim to prevent concurrent remove or retranscribe from changing the attachment under a send.
- Graceful shutdown marks jobs interrupted too, so a controlled server restart behaves like recovery from a crashed server.
- Used the **exact §5.13** failed/overflow/blocked-search copy. §8's toggle tooltip remains its specified shorter wording.
- A review screenshot captured settings partway through an opacity animation and triggered transient contrast failure. Finite animations are now settled for that screenshot; normal UI animation and reduced-motion behavior remain intact.

## Runtime observations

- Real `doctor --json` reports ready, version 0.1.0; the engine patch applied without adaptation.
- Browser upload progress comes from `XMLHttpRequest.upload`, not a timer. Transcription provides elapsed time, not invented percentages.
- Jobs survive browser disconnects; SSE replays with Last-Event-ID and expired jobs provide a persisted snapshot. There is no transcription status polling.
- The full source file is never read into server memory. Incoming multipart data spools to disk, then the upload handler copies it in 1 MiB chunks to a private `.part` file and renames it.
- Downloads preserve the recording stem, including Unicode-safe Content-Disposition. SRT uses timestamped original/raw segments.
- The preview uses the existing Mac/Tailscale address. `WORKBENCH_TRANSCRIBE_HOME` is supplied to the preview process; deployment/launchd environment changes remain Phase 3 work (§12).
- The new Workbench database was backed up outside the repo before migration: `~/.local/share/workbench/data/backups/before-phase-t-2026-10-03.db` (mode 0600).

## Test output

- External engine: **44 tests passed**, doctor ready.
- `make check`: **199 Python tests passed**, **36 frontend tests passed**, types/lint/format/API contracts passed, **56 contrast pairs passed**.
- Coverage: providers 85.8%, runs 89.2%, search 88.9%, **transcribe 90.7%**.
- `make e2e`: **162 passed, two expected skips** (the >90-second timing gate runs once in Chromium; the foundation screenshot set is captured once in Chromium). No serious/critical axe findings.
- Browser verification: real engine transcription, all three downloads, cancellation and remove passed.
- 1 GiB synthetic browser upload: progress and server memory criteria passed.

## Screenshots

All screenshots are fake-engine or `say` fixtures; no real recording appears.

- `artifacts/phase-t/states-{390,1440}-{light,dark}-fake.png`
- `artifacts/phase-t/transcript-text-{390,1440}-{light,dark}-fake.png`
- `artifacts/phase-t/transcript-timestamps-{390,1440}-{light,dark}-fake.png`
- `artifacts/phase-t/real-say-chip-1440.png`
- `artifacts/phase-t/real-say-text-1440.png`
- `artifacts/phase-t/real-say-timestamps-1440.png`

## Desktop review — 3 October 2026

Jake accepted the desktop flow after uploading a 717.4 MB recording. Its saved numeric
engine metadata records 30 seconds processing for 20:45 of audio. No real filename,
recording, transcript, or user-provided screenshot is copied into the repo.

| Area | Finding | Refinement / decision |
|---|---|---|
| Processing controls | Cancel and Remove both used X, despite having different effects. | Use a stop square for Cancel and a trash icon for Remove. Keep descriptive tooltips and accessible labels. |
| Completed recording menu | Downloads, reprocessing and removal formed one continuous list. | Add separators between review, download, reprocessing and removal; mark Remove with the existing destructive token. |
| Menu accessibility | The new open-menu audit flagged `aria-hidden-focus`: the default modal menu hid the page's otherwise focusable controls. | Make this contextual recording menu nonmodal. Escape dismisses it and returns focus to its trigger; the accessibility audit passes. |
| Composer and sent recording | Duration, word/token count and model label are visible; transcript opens from the chip. | Retain the layout. |
| Transcript panel | Close control and Copy/Download remain outside the scrolling text; text and timestamps are separate views. | Retain the layout. |
| Downloads | The user's text download completed and retained the recording stem. | Retain the native browser download flow. |
| Mobile | Physical-phone review has not happened yet. | Ready for Jake's next review after these refinements are verified and the preview is updated. |

Changed files for this review: `web/src/components/chat/AudioChip.tsx`,
`web/tests/transcription.spec.ts`, this report, and numeric/synthetic evidence under
`artifacts/phase-t/`. No backend, prompt, runtime configuration or dependency changes.

Review verification: `make check` passed (199 Python tests, 36 frontend tests,
56 contrast pairs); `make build` passed. The full `make e2e` run had **154 passed,
two expected skips, eight failures**, all in the newly added open-menu accessibility
check (`desktop-e2e-initial.txt`). After the nonmodal fix, the complete affected
transcription suite passed **16/16** on Chromium and WebKit, including all eight
previous failures (`desktop-e2e-corrected.txt`). There are no unresolved failures;
the unaffected 154 checks were not repeated. `desktop-check.txt` and
`desktop-build.txt` were regenerated after the fix.
Menu screenshots: `recording-menu-{390,1440}-{light,dark}-fake.png`.
`desktop-privacy-audit.json` found no real filenames or added audio media in the
changed/new files. `desktop-recording-metrics.json` contains numeric metadata only.
`desktop-preview-status.json` confirms both localhost and the existing Tailscale
URL serve the current build (HTTP 200), with the real transcription engine ready.
The preview was restarted in the background with the same environment; launchd
and Tailscale configuration remain unchanged.

## iPhone review — 3 October 2026

Recording downloads now use a cancellable format/filename dialog, with native file
sharing when supported and separate fallback downloads that preserve Workbench.
Transcript Close/Copy/Download remain reachable after returning from the nested
chooser on a shortened viewport. Recording menus wrap within the phone width;
chat/archive export links also retain the Workbench tab.

The comprehensive option review and accepted physical-phone check are in
`docs/PHASE-T-MOBILE-REVIEW.md`. `make check` passed (199 Python, 36 frontend,
56 contrast pairs), and build passed. The complete E2E run had 178 passed, two
expected skips and two failures caused by pending synthetic recordings left by
new tests. Test cleanup corrected that isolation issue; all 34 affected download
and review checks then passed in Chromium/WebKit. No unresolved failures remain.
All seven new design states have 28 synthetic screenshots/axe scans with no
serious or critical violations. Privacy evidence found zero real filename matches
or added audio media. Both localhost and Tailscale serve the current build, with
the real engine ready; the same background preview environment is restored.

## Open questions for Jake

Both device uploads succeeded, and Jake accepted the physical-phone download flow. The final selected-format refinement passed 14 focused browser checks, `make check` and build. See `docs/PHASE-T-MOBILE-REVIEW.md` for screenshots/evidence. Exact upload time and memory pressure remain unmeasured; acceptance does not invent those numbers.

Jake accepted this T1 mobile checkpoint and requested moving to Phase 3 after the selected-format refinement. T2 (manual model cleanup and glossary editing) remains unstarted. Phase 3 is ready to begin; its implementation and physical iPhone installation/VoiceOver checks remain future work.
