# Aero integration report — local UI review candidate

> Release update — 24 October 2026: Jake clarified that Claude UI review is after
> integration. PR #11 is merged and the paired update is live. See
> `THEMES-AERO-RELEASE-REPORT.md` for actual publication evidence and pending phone
> checks. The local-candidate report below is retained as checkpoint history.

24 October 2026 · `codex/themes-aero-integration`, building on `89aac412`
(Aero preview) and the preserved seven-theme `c7758120` candidate.

## Summary

Jake approved integration and requested independent Claude UI evaluation afterward.
Aero is wired into saved preferences and actual new chats on the isolated branch.
Rendered-material review found and repaired label contrast over sky and glossy
controls. No dependency, native/model call, main merge or deployment is included.
**Technical QA passed. Ready for independent local UI review; main merge and
deployment remain unapproved, and physical-device checks remain pending.**

## Done-when checklist

| Item | Status | Evidence |
|---|---|---|
| Aero saves and reloads; actual new-chat scene; scene absent after send | Pass, both engines | `aero-integration.spec.ts`; complete `make-e2e.log` |
| Material readability, 390/1440, light/dark | Pass in current complete invocation | 64 rendered audits, 1,553 sampled text runs; `material-rollup.json` and fake PNG captures |
| System/Always reduced motion; complete greeting | Pass, both engines | `aero-preview.spec.ts`, existing motion/greeting suites |
| All eight settings values and invalid-value rejection | Pass | 11 focused server tests, `appearance-server-tests.log` |
| Full checks | Pass | 778 Python /151 frontend tests, 969 contrast pairs; `make-check.log` |
| Complete browser suite | Pass | One complete invocation: 892 passed, four existing skips, zero failures; 1.4 h |
| Startup/streaming/scene budgets | Pass within measured browser scope | `bundle.json`, `final-rollup.json`, scene diagnostics |
| Installed app, original inputs and historical evidence preserved | Pass | 611 installed/677 candidate files; 1,727 historical files restored; `preservation-after.json` |
| Physical iPhone / saved Home Screen icon / independent UI review | Pending | No device result invented |
| Merge/deployment | Separate approval | Local candidate only |

Evidence root: `artifacts/themes/aero-integration-20261024/`.

## Changed files

Relative to the committed Aero preview:

- Server: allow `aero` in settings; parameterize the existing round-trip test over
  all eight palettes. No migration, provider, search, run, prompt or sampling edit.
- Web: mount `PaletteScene` in the real `EmptyState`; update the local theme lab's
  description; correct Aero material contrast and selector scope.
- Tests: actual-app settings/reload/send and screen audits; repeat the existing
  300-message, 100 tok/s workload with Aero; narrowly add `greet-bubble` to the
  existing bounded greeting helper.
- Docs/evidence: approval, this H4 report and retained before/after outcomes.

Aero's icons, manifest, registry, scene, motion and font stack were already in the
preview commit. Vite's dynamic palette list now includes its public assets without
adding another cache path. The origin-loss cache test includes Aero automatically.

## Deviations from SPEC.md and supplied design

The previously approved J18–J20 exceptions remain unchanged. J21's glass/scene
appearance is accepted for this isolated integration. Nine bubbles and sidebar
blur are retained; focused browser diagnostics did not require either fallback.

Readability repairs keep the materials:

- Give real and preview top bars a glass backing, including the muted runtime label.
- Restrict transparent main-column styling to a **direct** empty-chat child. A
  nested theme-lab new-chat example must not remove the design page's backing.
- Keep the gel highlight in the top six and bottom three pixels instead of crossing
  the label. The original light-theme gloss reduced label contrast below 4.5:1.

The preview's 340→320 ms Aero letter correction remains. No new motion exception,
startup budget, dependency, model call or per-topic behavior is introduced.

## Test-diff ledger

| Existing file/test | Change | Why / behavior still asserted |
|---|---|---|
| `server/tests/test_appearance_settings.py` round-trip | Repeat unchanged assertions over all eight palettes | Seven extra valid cases; all invalid-setting rejection assertions retained |
| `web/tests/helpers.ts` settle | Add only `greet-bubble` to known greeting keyframe names | Exact heading target, CSS-animation type, ≤900 ms timing and 1,000 ms deadline remain; generic ambient bypass negative test retained |
| `web/tests/performance.spec.ts` | Run the original workload for Cobalt and Aero; write Aero metrics separately | Original >50 samples, one rendered row, p95≤8 ms and scroll median<20 ms assertions remain; restore saved appearance after unmount and verify the measured palette; no timeout/threshold/skip change |

The newly written rendered audit initially had harness defects: an unavailable
Pillow import, mask glyphs from occluded content, and antialias pixels treated as
CSS text colors. It now uses browser-native PNG decoding, an unoccluded glyph mask,
computed CSS foregrounds and actual rendered background pixels. Page timers are frozen across the PNG passes so expiring UI remains one coherent
measurement, then resumed in `finally`. Each sampled glyph
is hit-tested against the restored page, so a partially covering notification is
not treated as visible text. A two-engine negative control retains exposed
low-contrast failure detection and checks the remaining visible covered-label
pixels. PNG/CSS viewport width must agree. Gradient stops
are checked conservatively. No package was added. These are corrections to new
measurement code, with failed logs/captures retained, not changes to an existing
gate. Quantization tolerance is 0.02; final samples exceed their threshold without it.

## Runtime observations and retained failures

All app integration checks use the existing isolated fake app/runtime on
18787/18080. Installed Ollama, image workers, port 8787, launchd and Tailscale
are untouched. No new inference evaluation is needed for unchanged provider,
run, search and prompt code; frozen hashes and payload goldens remain required.

- Initial harness run: six passes/eight failures from the missing Pillow import.
- Early mask runs retain false failures from hidden background text and font
  antialiasing. Real material failures are retained separately before repairs.
- One overlapping focused invocation attempted to use an occupied test port and
  removed an active Playwright trace directory, causing a trace-close ENOENT.
  This was runner coordination, not an app failure. Subsequent runs are sequential;
  the final full-suite result must come from one complete fresh invocation.
- The first full run was stopped after a real test-isolation failure: the new Aero
  performance workload persisted its palette into the shared fake settings. The
  next unchanged baseline message-layout test therefore saw Aero's intentional
  1 px gel border instead of Cobalt's 0 px border. Its trace confirms the saved
  Aero palette. Preserve 290 passed, one failed, one interrupted, one skipped and
  601 not run in `make-e2e-initial-aborted.log`. This is not qualification.
- The performance fixture now waits for hydration, verifies the selected/saved
  palette, unmounts preference synchronization before restoring the original
  setting, and asserts restoration. The new app-audit fixture also unmounts before
  restoring its settings. No product or original layout assertion was changed.
  A six-case ordered performance→layout comparison passes both engines;
  final strengthened fixture checks and a fresh full invocation follow.
- A second full invocation completed Chromium with no failure, then hit two new
  WebKit phone audit failures: a paused-workflow toast partially covered the
  Images “New image” label. The center of the line was visible, but the old mask
  counted covered glyphs against the toast background. Preserve 464 passed, two
  failed, one interrupted, one existing skip and 426 not run (44.1 minutes) in
  `make-e2e-second-aborted.log`; this is not qualification. No product change
  resulted. Individual glyph hit testing and the negative control repair the
  measurement. The first control fixture lacked a mobile viewport meta tag;
  its 980/390 coordinate mismatch is retained, fixed and guarded explicitly.
- The third invocation completed with 891 passes, four existing skips and one
  failure (1.3 h): a notification expired between PNG passes in the WebKit dark
  desktop Tools audit. `make-e2e-third-complete-failed.log` and
  `third-executed-source.json` preserve that failed complete gate. The new audit
  now freezes page timers only during capture/analysis, after installing the clock
  before app timers are created. It resumes in `finally`. Its two-engine negative
  control requires an expiring notification to be measured and then expire after
  resuming; exposed low-contrast text must still fail the calculation.
- The first clock probe rejected a just-read timestamp as past after IPC delay;
  its failures are retained in `clock-control.log`. Choosing a future pause point
  before text collection fixes that protocol error. An accidentally repeated
  uncorrected probe was interrupted and retained, not counted as a passing run.
- The corrected focused material/control run passes all ten cases across both
  engines (`clock-control-fixed.log`). The final frontend lint/type/format/unit
  run also passes all 151 cases (`final-frontend-check-v7.log`). Product source
  remains identical to the complete `make check`; only the two browser test files
  changed afterward. Previous logs/captures/traces remain in the QA archive.

## Test output

Full `make check` passes: 778 Python and 151 frontend cases, 969 token pairs, all
coverage floors, lint/types/format, API types/additivity, motion and privacy. Final
initial JavaScript is 252,235 gzip bytes (budget 256,000), 1,255 above the seven-theme
candidate and 3,713 below the installed build. One complete Chromium/WebKit invocation passes 892 cases with four unchanged
skips and zero failures (1.4 h). Focused: 11 server cases; ten material/integration cases;
initial Cobalt/Aero performance workload passes both engines. Preview has 12
passing isolated design cases, retained as preview evidence rather than final QA.

The four skips are unchanged: Chromium-only real-time timeout and base screenshot
gates, WebKit-only native HEIC decoding, and the existing WebKit offline-navigation
emulation limitation. The theme asset origin-loss/cache checks pass in both
engines. There is no new skip, raised timeout or weakened original assertion.

## Screenshots

Fake-only `<engine>-<mode>-<width>-<state>-fake-normal.png` captures cover settings,
new chat, the scene at a 15-second animation phase, Tools, conversation, Workflows,
Images and theme-lab gel controls. Background-only and glyph masks reproduce the
material measurements. Their PNGs contain synthetic data only.

## Preservation

`preservation-after.json` verifies 611 installed public/source files and 677
executed candidate/tooling files with zero mismatch. All four supplied inputs
match their recorded hashes. The original workspace remains at `8f38ef7b`; remote
main remains `4d33913c`. Local and normally verified Tailscale HTTPS health both
return 200, with no TLS bypass. No merge, deployment or native model call occurred.

The suite regenerated 1,727 historical tracked artifacts. Each fresh copy is
archived privately, JSON metrics retained under the new evidence root, and every
old tracked file restored to its prior hash. Another 108 new synthetic captures
are archived privately with their hashes. Raw failure traces, older material
measurements and unnormalized logs remain in the private QA archive; normalized
public logs carry raw/normalized SHA provenance. No historical trial was regraded
or overwritten. New current fake captures remain under this checkpoint. The final marker audit
scans 2,361 paths with zero findings (`final-privacy.json`).

## Migrations and rollback

No migration or private-data change. For a later approved release, install the
server and web together: an old server rejects new appearance settings. First
preserve the current installed tree and a database backup, then verify health,
asset hashes, settings and phone checks. Restore the paired old tree and backup
if rollback is needed. This report does not authorize that release or perform it.

## Known limitations and next review

- Independent Claude UI review is pending. Local fake-runtime behavior is for UI
  review and does not benchmark the real models.
- Browser rAF intervals and React render duration do not certify phone GPU FPS,
  battery cost, backdrop blur or real Safari performance. Real iPhone J21 check
  remains pending; if it stutters, remove sidebar blur first, then reduce bubbles.
- A retained synthetic phone Images capture shows an existing paused-workflow
  notification temporarily overlapping its header/button. Notification placement
  was not redesigned in this palette scope; include it in the independent UI review.
- Home Screen icon caching remains unverified on a real device; no remove/re-add
  instruction is asserted as proven.
- Historical VoiceOver failure remains unresolved and excluded by Jake. The
  earlier keyboard issue recovered after restart; its cause was not proven.
- Source/evidence from the shelved Research, agent and precision-editing trials
  remain historical. This integration does not restart those tasks or automation.

## Local review

Open <http://127.0.0.1:5173/design?themes>. The isolated fake app is running;
`/`, `/workflows` and `/images` also return 200 and its saved palette is Aero.
Use Settings → Appearance to review actual app surfaces. Its database is
temporary, and its engines are fake; the phone/live app is unchanged.
`next/themes/IMPLEMENTATION-STATUS.md` has the review entry point.

## Open questions for Jake

Review the local candidate with Claude. A later approval must cover main merge
and paired server/web deployment, with physical-device validation and rollback
kept in that release scope. This local preview does not change the phone app.

## Gates

| Gate | Evidence/status |
|---|---|
| G1 | Pass: complete `make-check.log`; 778 Python/151 frontend, coverage floors≥80% |
| G2 | Pass: 892 passed, four unchanged skips, zero failures in one complete 1.4 h invocation |
| G3 | Ledger above; no original assertion removed, timeout raised or new skip |
| G4 | Pass: JS 252,235≤256,000; streaming p95 3.4/3.0 ms, scroll median 16.7/17 ms, first-token 76.7/67.1 ms |
| G5 | Pass: 969 token pairs; complete browser axe checks and 64 actual-material audits; 1,553 sampled text runs, normal-text minimum 5.19:1 |
| G6 | API additive/type checks pass |
| G7 | No migration; existing row-preservation tests pass |
| G8 | Frozen prompts pass; no prompt edit |
| G9 | Search/runs/providers unchanged; no new inference eval required or performed |
| G10 | Default-request golden and unset-parameter guards pass in full Python run |
| G11 | Pass: final privacy scan 2,361 paths/zero findings (`final-privacy.json`); synthetic captures and preservation inventories |
| G12 | Deployment invariants pass; no service/configuration/publication change |
| G13 | Pass: normal motion, named bounded greeting, system/Always reduced motion and existing guards in complete suite |
| G14 | Actual production components on `/design?themes` and existing fixture routes |
| G15 | No migration; release backup/paired rollback prepared as later steps |
| G16 | Physical iPhone check not yet performed for this candidate |

## Core unchanged

The complete suite must remain green; these existing guards are retained:

| Core | Guard |
|---|---|
| C1 Send/stream/stats | `chat.spec.ts` |
| C2 Stop/partial persistence | `chat.spec.ts`, `phase3-accessibility.spec.ts` |
| C3 Resume/reconnect | `chat.spec.ts`, `web.spec.ts` |
| C4 Long answer/timeouts | `chat.spec.ts` |
| C5 Edit/regenerate/branch/rename/pin/export/delete | `actions.spec.ts` |
| C6 Model select/load/eject/context | `load-selection.spec.ts`, `ui-regressions.spec.ts` |
| C7 Exact user-set parameters | `parameters.spec.ts`, server request captures |
| C8 Search/citations/retry | `web.spec.ts`, Python search/evidence/grading guards |
| C9 Transcription/retention/download/ask | `transcription.spec.ts`, `recording-download.spec.ts`, `audio-storage.spec.ts` |
| C10 Phone layout/keyboard/safe areas | `mobile-layout.spec.ts`, `mobile-composer.spec.ts` |
| C11 Shortcuts/PWA/update/no API caching | `polish.spec.ts`, `pwa.spec.ts`, theme origin-loss test |
| C12 Read-only legacy import | `test_legacy_import.py` |
| C13 Deployment identity | `test_deployment.py` |
| C14 Injection/remote media/SSRF | `foundation.spec.ts`, `test_search.py` |
| C15 Size/frames/streaming | `performance.spec.ts`, `chat.spec.ts`, bundle JSON |
| C16 Accessibility | `foundation.spec.ts`, `review.spec.ts`, `phase3-accessibility.spec.ts`, new Aero audit |

## Budgets

| Measure | Previous seven-theme candidate | Aero candidate | Limit |
|---|---:|---:|---:|
| Initial JS gzip bytes | 250,980 | 252,235 | 256,000; growth≤8,192 |
| Streaming row p95 CPU | 3.3/3.0 ms | 3.4/3.0 ms | ≤8 ms |
| First-token overhead | 82.36/65.49 ms | 76.68/67.12 ms | ≤150 ms |
| 300-message scroll median | Existing pass | 16.7/17 ms | <20 ms |
| Complete greeting | ≤4,500 ms | Pass, both engines | ≤4,500 ms |

Values are ordered Chromium/WebKit. First-token values are client render
overhead against the fake runtime in the ordinary default-palette chat test;
they do not measure model latency. The Aero 300-message workload separately
measures the selected palette.

The separate day/night scene diagnostic records 179 frame intervals per mode
and engine, with 16.7/17 ms medians and 16.8/18 ms p95 in both modes. Twelve day
and ten night scene animations run; the design page makes zero API calls. Its
script, JSON and log are retained as `scene-day-night-diagnostic.*`. These are
Mac browser diagnostics, not real-phone GPU/FPS certification.

Python coverage remains providers89.7%, runs89.5%, search89.8%, transcription93.2%,
documents96.6%, Library92.6%, images83.6%, workflows89.8%, backup95.5% and
capacity96.6%. This does not measure model answer accuracy or physical phone FPS.
