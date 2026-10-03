# Phase T — iPhone review and recording downloads

## Summary

Jake's physical-phone recording upload and transcript review worked; his remaining
issue was the browser/OS file preview replacing the usable Workbench screen.
Recording downloads now open a cancellable Workbench dialog with a format chooser
and filename. Compatible phones get a native file share sheet; unsupported hosts
and original audio use a separate browser download while retaining Workbench.
This refines T1. T2 and Phase 3 have not started.

## Done-when checklist

| Item | Status | Evidence |
|---|---|---|
| Phone upload and transcription | User exercised | Numeric metadata only in `mobile-recording-metrics.json`: 2,945,884 bytes, 120.35 s audio, 2.9 s transcription, 42× real time; ready. Exact upload time and memory pressure remain unmeasured. |
| Choose TXT/SRT/JSON before saving | Passed focused checks | `format choice, cancel and downloads retain Workbench` verifies extension, contents, subtitles and valid JSON. |
| Cancel/Close without saving | Passed focused checks | No browser download on Cancel; original URL retained. |
| Share-sheet cancellation and wrong-format recovery | Passed with simulated native API | `native save cancellation permits a different format without a fallback download`: first share cancelled, JSON selected and delivered, transient activation present; no automatic fallback download. |
| Native sharing unavailable/denied | Passed with simulated capability/denial | Fallback is explicit, separate and cancellable. A denied share never automatically downloads. |
| Failed preparation and Retry | Passed focused checks | 503 is shown in the dialog, Retry succeeds and Cancel remains available. |
| Original audio avoids browser buffering | Passed focused checks | Opening its chooser makes zero original-audio GETs; the final link streams separately. |
| Nested transcript/save panels after viewport shrink | Passed focused checks | Close and Cancel remain visible at 320/390 widths, 480-pixel shortened viewport, simulated 47/34-pixel safe areas; cancelling returns to the usable transcript drawer. |
| Touch targets, overflow and accessibility | Passed focused checks | 44-pixel close target, no horizontal page overflow, no serious/critical axe findings in light/dark at 320/390/1440. |
| Every new state on `/design` | Passed | Ready, preparing, failed, sharing, cancelled, share denied, returned; 28 synthetic screenshots and 28 axe scans, zero serious/critical findings (`mobile-design-review.json`). |
| Regression gate | Passed after correction | Full run: 178 passed, two expected skips, two failed; both corrected via test cleanup. All 34 affected download/review checks then passed on Chromium/WebKit. `make check` and build passed. |
| Physical iPhone share sheet after this change | Pending Jake | The actual OS sheet cannot be driven by headless browser tests; check Save to Files and native Cancel on the phone. |

## Comprehensive iPhone review

The review combines Jake's provided phone screenshots, inspected synthetic screens,
and existing/new automated interactions. Headless WebKit and simulated safe areas
verify layout and app behavior; they do not reproduce every native iOS overlay.

| Area | Finding / decision | Evidence |
|---|---|---|
| Welcome and composer | Preserve the compact toolbar and recording starters; Send remains blocked until the transcript is ready. | Transcription T-1/T-3; review and live-chat tests. |
| Keyboard / scrolling | Existing composer remains above the shortened viewport. Fix the nested recording panel's outer scrolling so focus restoration cannot move its header and footer out of view. Only the transcript body scrolls. | New nested-panel regression; review keyboard layout checks. |
| Recording chip and menu | Preserve duration/word/token summary and distinct Stop/Remove actions. Bound menu width and wrap the long channel action on narrow screens. Downloads now open the format chooser. | Transcription T-3/T-10 and download checks. |
| Transcript panel | Left-align the title/metadata for easier scanning. Preserve fixed Close, Copy and Download; text remains plain text. | Text/timestamp fixture screenshots; nested-panel test. |
| Downloads | Replace the immediate handoff with format choice, filename, preparation state, Cancel and Close. Prepare a small transcript file before the final sharing tap; keep the dialog after sharing/cancellation. | New download suite. |
| Original audio | Retain the original file and stream separately, avoiding a multi-GiB JavaScript `File`. Native browser presentation is outside Workbench's control. | Original-audio request-count/download test. |
| Model picker and loading | Preserve search bounds, reachable Close, loading selection and configured 16K/32K limits. | `ui-regressions.spec.ts`, `load-selection.spec.ts`. |
| Chat settings | Preserve reachable close control, actual sampling payloads, context ceiling and capitalized reasoning values. | UI regression and parameter tests. |
| History/sidebar | Preserve safe-area placement, searchable chats and reachable close/settings controls. | Review/sidebar and action tests. |
| Rename, pin/unpin, delete | Preserve confirmation and readable notifications. | Action tests, notification/keyboard checks. |
| Chat exports | Preserve Cancel and title-based filenames; open the final download separately so the Workbench tab stays available. | Markdown/JSON action tests. |
| Sources/citations | Preserve compact numbered citations and dismissible source cards/drawers. | Web citation and UI regression tests. |
| Settings — Connections/Models | Preserve connection and runtime status, Load/Eject, configured context and defaults. | Settings pane review and load selection tests. |
| Settings — Search/Transcription | Preserve redacted search-key controls and recording privacy/status settings. Add Transcription to the comprehensive settings-pane loop. | Search key tests, transcription T-9, UI regression loop. |
| Settings — Appearance | Preserve theme, font, size and reduced motion; no new motion or raw colors added. | Light/dark screens, theme/reduced-motion and contrast checks. |
| Settings — Data | Open the archive download separately; preserve import/delete confirmations. | Data action tests. |
| Settings — Shortcuts/About | Preserve navigation, reachable Close and build details. | Review/UI regression and About checks. |

## Changed files

- Web: new `RecordingDownloadDialog.tsx`, `lib/recording-download.ts`; integrate
  the shared chooser from `AudioChip` and `TranscriptSheet`; fixed panel clipping
  and header alignment; separate chat/data export links.
- Design: synthetic save-dialog states in `TranscriptionPreview`.
- Tests: new `recording-download.spec.ts`; Transcription settings added to the
  existing pane-review loop.
- Docs: user amendment in `SPEC.md`, this review, updated Phase T checkpoint report.
- Evidence: numeric metadata, command logs and synthetic screens under `artifacts/phase-t/`.

## Deviations from SPEC.md

The user's mobile correction replaces immediate recording download links with a
confirmation/format chooser. The download endpoints and formats are unchanged.
No packages, model calls, backend, launchd, port, bind or Tailscale changes.

## Runtime observations

The black file screen in the supplied image appears to be browser/OS-owned; a web
page cannot put its own Close button into that view. The app now controls the steps
before the handoff and retains its tab for fallback downloads.

Web Share requires a secure context, file support and a transient user activation.
The file is fetched before the final Save or share click, with no awaited request
before `navigator.share()`. Cancellation (`AbortError`) is a normal outcome and
never triggers a fallback download. Original audio is deliberately not buffered.
Sources: [WebKit user activation](https://webkit.org/blog/13862/the-user-activation-api/),
[MDN navigator.share](https://developer.mozilla.org/en-US/docs/Web/API/Navigator/share).

The shortened-viewport regression exposed an `overflow: hidden` container scrolling
programmatically when focus returned from a nested modal. Using `overflow: clip`
on the outer panel leaves scrolling to its body and preserves its fixed controls.

## Test output

- Focused preflight: 31 passed, nine failed. Eight found the nested viewport/focus
  regression; one test read a simulated share result before its asynchronous file
  read completed. Both were corrected.
- Second focused run: 17 passed; one setup failure attached a file before the live
  bootstrap UI had replaced its placeholder. Setup now waits for Add recording.
- Final focused download run: **18 passed** in Chromium/WebKit, 31.2 s.
- `make check`: **199 Python tests, 36 frontend tests, 56 contrast pairs passed**;
  lint/types/format/API contract passed (`mobile-check.txt`).
- Full `make e2e`: **178 passed, two expected skips, two failed** in 11.7 min (`mobile-e2e.txt`). Both failed reasoning-screen cases inherited a pending synthetic recording from the new download tests; its transcript changed the fake runtime prompt. The new suite now removes its pending uploads in `afterEach`, including failed tests. The affected download/review suites were rerun together in original order: **34 passed** in 1.1 min (`mobile-e2e-corrected.txt`), including both failed cases and all 18 new download cases. No unresolved failures remain; the unaffected 178 checks were not repeated.
- `make build`: **passed** (`mobile-build.txt`); existing bundle-size warning retained.

The restored background preview uses the same port, bind and transcription environment. `mobile-preview-status.json` verifies HTTP 200 and the compiled index hash on localhost and the existing Tailscale URL, with the real transcription engine ready (0.1.0). Launchd and Tailscale configuration remain unchanged.

## Screenshots

Synthetic recordings only; the supplied real screenshots were not copied into the repo.

- `artifacts/phase-t/mobile-save-{320,390,1440}-{light,dark}-fake.png`
- `artifacts/phase-t/download-{ready,preparing,failed,sharing,cancelled,share-failed,returned}-{390,1440}-{light,dark}-fake.png`: all seven states, phone/desktop and light/dark.
- `artifacts/phase-t/mobile-settings-transcription-{390,1440}-{light,dark}.png`: synthetic settings review.
- Updated `recording-menu-*`, `states-*`, `transcript-text-*`, `transcript-timestamps-*`
  synthetic fixture screens.

Privacy audit: `mobile-privacy-audit.json` found no real filename matches or added audio media in the changed/new files. Only numeric real-run metadata was examined; no real transcript was read for this review.

## Open questions for Jake

After the preview update, check Download → Details (.json) → Save or share on the
physical iPhone. Cancel the native sheet, switch to Text, then reopen it and use
Save to Files. Verify that the transcript and chat remain available. If the host
browser doesn't support file sharing, use the explicitly separate download and
return to the retained Workbench tab.

Exact real-file upload time and Mac memory pressure were not measured in either
physical-device check. The report does not claim those values or verified transcript
accuracy. Review remains at T1 before T2 and Phase 3.
