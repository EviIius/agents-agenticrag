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

## T2 checkpoint — Phase 6A, 5 October 2026

### Summary

Manual clean-up uses the model selected in the composer, one guarded call per
section, with progress and cancellation. Cleaned, As transcribed and Raw Whisper
remain available; discard removes only the cleaned version. Settings ›
Transcription now edits the engine's private glossary with validation and atomic
saving. Original text, raw text and timestamps are preserved. The checkpoint is
validated and deployed, with the required 6A review stop; 6B is not started.

### Done-when checklist

| Item | Status | Evidence |
|---|---|---|
| T-AC15: progress, rejected sections, versions, context and discard | Focused pass | `cleanup.spec.ts`; `test_cleanup_guard_progress_versions_context_discard_and_request` |
| T-AC16: approximately five-minute generated speech with real Qwen | Pass | `real-cleanup.json`: 294.16 s audio, 21.606 s clean-up, three sections, two kept, zero accepted changed words |
| T-AC17: glossary, validation and next engine prompt | Pass | Both widths/engines in `cleanup.spec.ts`; glossary unit tests |
| P6-AC1: unchanged guard vectors | Pass | `test_guard_vectors_chunking_and_frozen_active_prompt`; `shared/cleanup_guard_cases.json` |
| P6-AC2: same-model chat streams before 12-section clean-up finishes | Pass | `test_twelve_chunks_yield_to_chat_and_split_labels` |
| P6-AC3: cancellation preserves original fields | Pass | Original-field SHA comparisons in server tests; browser cancellation |
| P6-AC4: glossary survives deployment | Pass | API save, actual `install_engine` in a private temporary directory, redeploy and byte comparison |
| P6-AC5: all T1 tests unchanged | Pass | Complete `e2e.txt`: 403 passed, three existing skips, 33.2 minutes |
| P6-AC6: privacy | Pass | `privacy-audit.json`; invented fixtures only |
| Phone review | Not checked | Stop after 6A for Jake's review |

All evidence paths in this checkpoint are under `artifacts/phase-6/6a/` unless
otherwise stated. Implementation source is committed at `533418b`; application
and test hashes are recorded in `source-freeze.json`.

### Changed files

- Server: `transcribe/cleanup.py`, `transcribe/glossary.py`, shared job lifecycle,
  additive cleanup/glossary endpoints and schemas, application wiring.
- Web: clean-up controls in `AudioChip` and `TranscriptSheet`, `useCleanup`,
  attachment SSE handling, `GlossaryEditor`, Transcription settings, API types.
- Design: production components at `/design?cleanup`, 18 states, both themes,
  390/1440 widths, Chromium/WebKit.
- Tests: seven new server tests, 18 new browser cases, invented support-fake
  extensions and isolated glossary path. Generated-speech rehearsal script.
- Docs: authorization and accepted 5C review, retry clarification, this H4 report.
  Reference guard removed only after all unchanged vectors passed; vectors moved
  to `shared/`; `docs/transcription/engine.patch` retained.

### Deviations and clarifications

Jake delegated the retry-visibility conflict with “Do what you think is best.”
The frozen T1 behavior wins: unavailable-audio retry entries remain visible and
disabled, with the existing re-upload explanation. No unavailable audio can retry.
This decision is recorded in AGENTS and the 6A plan; existing assertions are intact.

Jake accepted 5C with “5C is sufficient. Continue on.” This authorizes 6A and
does not invent individual physical-phone results. The sidebar/other motion
regression remains deferred as he requested. No second runtime is implemented.

The exact frozen clean-up prompt is compared with both the spec and the Phase 3
SHA baseline. Only the allowed clean-up utility call is added, one call per chunk,
without a retry, extra judge or provider stage. Existing chat defaults, search,
providers and run pipeline are unchanged. No dependencies or migrations added.

### Runtime observations

All actual speech used for verification is generated by macOS `say`. The engine
and API use a private temporary workspace and invented glossary; production
recordings and transcripts are never read. Production connection/model metadata
is read only. The private glossary is compared by hash without printing content.
The isolated workspace is removed when the rehearsal exits.

The first 800-word sample was 224.12 seconds, shorter than the approximately
five-minute target: transcribed in 6.353 seconds, cleaned in 13.165 seconds,
three sections, one kept as original, zero changed words in accepted sections.
The second sample uses 1,050 words: **294.16 seconds** of audio, transcription
in **8.696 seconds**, clean-up in **21.606 seconds**, three sections, **two kept
as original**, **zero changed words** in accepted sections. Original fields and
production glossary were identical. The longer invocation changes only the
in-memory generated-speech fixture count; application/test source is unchanged.
Runtime measurements are evidence for these
synthetic samples, not a promise of timing on arbitrary recordings.

### Test output

- `make check`: **257 Python**, **36 frontend**, **74 contrast** checks pass.
- Coverage: providers **85.8%**, runs **89.2%**, search **88.9%**, transcription
  **93.1%**. Additive API, prompt freeze, motion, privacy, formatting and types pass.
- Vendored engine: **44 tests pass**, unchanged production engine source.
- Focused browser run: **18 passed in 3.1 minutes**, both engines and widths.
- Final complete `make e2e`: **403 passed, three existing skips, 33.2 minutes**,
  one invocation against the recorded source hashes. The existing WebKit skips
  remain: real-time timeout gate runs once in Chromium; all-size foundation
  screenshot capture runs once in Chromium; offline service-worker navigation
  remains a Playwright WebKit limitation with separate prior phone evidence.
- Initial new-test failures are retained: incorrect navigation role in four
  glossary browser cases; initial unit fixture/import expectations; formatting.
  The new selector was corrected to Settings' existing button semantics.
  No existing test was weakened or skipped and no timeout was raised.
- Evidence text logs have only trailing whitespace normalized; test outcomes
  and failure details are retained.
- The first rehearsal launch omitted `PYTHONPATH=.` and failed before executing
  the app. The corrected command uses the server directory on the import path.

### Screenshots and accessibility

`cleanup-*-fake.png` provides **144 synthetic images**: 18 states × two widths ×
two themes × two engines. `cleanup-axe-*-fake.json` covers the same matrix with
zero serious/critical findings. The images come only from invented `/design`
fixtures. Representative mobile and desktop partial/ready/cleaning/glossary
images were inspected by Codex; this is not a physical iPhone review by Jake.
All glossary preview terms are invented; no private glossary was captured.

### Budgets

| Measure | 4A baseline | Previous 5C | 6A |
|---|---|---|---|
| Initial JS gzip | 224,491 B | 236,159 B | **237,675 B**, +1,516 B |
| Budget | 256,000 B | Pass | Pass; increase below 8 KiB |
| Streaming p95 frame | 1.3 / 2 ms | See 5C | **3.1 / 3.0 ms**, pass |
| First-token overhead | ≤82 ms | See 5C | **70.79 / 59.12 ms**, pass |
| 300-message scroll | Passing suite | Pass | Pass, median **16.7 / 17 ms** |

Settings remains lazy loaded. Runtime request and streaming thresholds are
unchanged. Final regenerated timing evidence is archived here under `regenerated/phase-1/`
and `regenerated/phase-3/`; historical phase artifacts were restored. The new
clean-up module has 94.2% line coverage and the glossary module 100%.

### Gates

| Gate | Status | Evidence |
|---|---|---|
| G-1 check/coverage | Pass | `check.txt`, 257/36/74; transcription 93.1% |
| G-2 complete browser run | Pass | One final `make e2e`, `e2e.txt`: 403 passed, three existing skips |
| G-3 no weakened tests | Pass | Ledger below; no pre-existing assertion edits |
| G-4 performance | Pass | `bundle.json`, final performance tests |
| G-5 axe/contrast/keyboard | Pass automated | 144 state scans, 74 contrast pairs |
| G-6 additive API | Pass | `check_api_additive.py`, `check.txt` |
| G-7 row preservation | Pass | `test_phase4_guards.py`; no migration |
| G-8 prompt freeze | Pass | `test_prompt_hashes.py`; active clean-up prompt matches frozen hash and exact spec |
| G-9 web replay after pipeline changes | Not triggered | No search, providers or runs source changed |
| G-10 ordinary runtime payload | Pass | Golden request and exact parameter unit captures |
| G-11 privacy | Pass | `privacy-audit.json`; isolated generated speech and invented fixtures |
| G-12 deployment invariants | Pass | `test_deployment.py`, deployment metadata |
| G-13 reduced motion | Pass automated; physical issue deferred | Existing motion tests unchanged; physical regression deferred |
| G-14 production design states | Pass | `/design?cleanup`, 144 synthetic captures |
| G-15 migration rollback | Not triggered | Existing schema version 7; no migration |
| G-16 Jake's phone check | Not checked for 6A | Required review stop; no invented results |

### Test-diff ledger

No existing test assertion or threshold changed, and no new skip was added.
The support changes below are additive; all core suites run unchanged.

| Existing support file | Change | Why | Existing behavior retained? |
|---|---|---|---|
| `server/tests/fake_runtime.py` | Recognizes the exact clean-up prompt and an invented rejection directive | Test one-call-per-chunk formatting and guard | Yes; ordinary chat/search behavior retained |
| `server/tests/fake_transcribe/bin/transcribe` | Invented clean-up and cancellation inputs; prompt reflects isolated glossary terms | T2 progress, guard, cancellation and glossary verification | Yes; prior directives retained |
| `server/tests/serve_app.py` | Per-test-server temporary glossary path | Prevent synthetic terms from leaking across runs or into private files | Yes; engine/runtime routes unchanged |
| `scripts/privacy_audit.py` | Adds Phase 6 evidence coverage | Scan new evidence and synthetic image names | Yes; earlier phase scans and secret/media checks retained |

The failed new glossary test used a nonexistent `tab` role. Its selector now
uses the existing Transcription navigation button; no interaction was mocked.
The frozen T1 retry assertions were preserved after Jake delegated the conflict.

### Core unchanged

Every browser row refers to the final single complete `e2e.txt` invocation;
unit guards refer to `check.txt`. No partial-run assembly was used.

| Core | Suite |
|---|---|
| C1 send/stream/stats | `chat.spec.ts` |
| C2 stop/partial | `chat.spec.ts`, `phase3-accessibility.spec.ts` |
| C3 reopen/reconnect | `chat.spec.ts`, `web.spec.ts` |
| C4 long answer/idle timeout | `chat.spec.ts` |
| C5 chat actions/export | `actions.spec.ts`, `chat-export.spec.ts` |
| C6 model operations/context | `load-selection.spec.ts`, `ui-regressions.spec.ts` |
| C7 explicit parameters | `parameters.spec.ts`, `test_chat.py`, `test_presets.py` |
| C8 web/citations/failure | `web.spec.ts`, unchanged search unit tests |
| C9 recording/download/retention | `transcription.spec.ts`, `recording-download.spec.ts`, `audio-storage.spec.ts`, `test_transcription.py` |
| C10 phone layouts/composer | `mobile-layout.spec.ts`, `mobile-composer.spec.ts` |
| C11 palette/PWA/update | `polish.spec.ts`, `pwa.spec.ts` |
| C12 legacy read-only import | `test_legacy_import.py` |
| C13 deployment | `test_deployment.py`, live metadata |
| C14 untrusted content | `foundation.spec.ts`, SSRF unit guards |
| C15 budgets | `performance.spec.ts`, chat timing tests |
| C16 axe/keyboard | `foundation.spec.ts`, `review.spec.ts`, `phase3-accessibility.spec.ts`, new cleanup design tests |

### Migrations, deployment and fallback

No migration is added; the existing T1 transcript columns store clean-up state.
Original transcription fields are preserved by byte/hash comparisons on success,
rejection, timeout, cancellation and discard. The synthetic Phase 3 fixture
upgrade and legacy-import guards remain unchanged. Schema remains version 7.

`deploy.txt` and `deployment.json` confirm live local/Tailscale health 200,
engine ready, a new deployment backup, byte-identical installed build, unchanged
private doctor-reported glossary, bind/port, one worker, launchd arguments and
Tailscale configuration. Production `/design` returns 404; schema remains 7 and
database integrity is OK. The live probes used a nonexistent synthetic attachment
ID and read glossary metadata without emitting terms; zero model calls and no
production recording/transcript reads. An initial probe incorrectly expected
production OpenAPI documentation; it is intentionally disabled. The corrected
endpoint probes passed without any application change. 5C source `48fbb9f` and evidence `47f2389` provide the prior fallback.
Clean-up does not modify the original transcript, so the previous application
can continue reading the existing schema without a down migration.

### Evals

No aggregate web eval was required: search, runs, providers and all existing
prompts are unchanged. Active clean-up prompt bytes match the already frozen
spec hash. Guard vectors, fake-runtime request captures, section concurrency,
and real generated-speech timings are this utility's evidence. No claim is made
that the word-change guard proves semantic accuracy or perfect transcription.

### Known limitations and review

- VoiceOver previously failed according to Jake and remains unresolved/deferred.
  Automated axe checks do not establish physical VoiceOver support.
- The earlier iOS keyboard failure recovered after an iPhone restart; its cause
  remains unproven. No new device-level input result is claimed here.
- Jake reported sidebar/other animation regression after 5B and asked to diagnose
  it later. It is still deferred; no physical motion pass is claimed by this phase.
- Clean-up retains sections rejected by the word guard. Originals remain available,
  and timestamps/subtitles always use the original transcript. Clean-up is manual.
- Jake's 6A phone review is pending. This report stops at 6A; 6B requires a named,
  explicitly approved second runtime. Library and Research remain separately gated.

### Open questions for Jake

Open a saved transcript on your phone, run
“Clean up with …”, switch versions, and check cancellation/discard. In Settings ›
Transcription, review the glossary editor. Do not send private terms or recording
text as review evidence; reporting whether the controls work is sufficient.
