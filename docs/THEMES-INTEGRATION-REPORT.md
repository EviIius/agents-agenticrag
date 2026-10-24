# TH1/TH2 report — palettes and theme motion

23–24 October 2026 · `codex/themes-th1-th2`, based on main `4d33913c`.

## Summary

Claude's seven-palette implementation is integrated on an isolated branch with
Jake's explicit J18–J20 approval. Review found and repaired stale theme callbacks,
interrupted greeting state, incomplete duration accounting, an overly broad test
exemption, excess startup JavaScript and a phone-size keyboard-access issue.
No dependency, native model call, production prompt, main merge or deployment is included.
The recording-folder workflow remains a separate concrete proposal.

## Done-when checklist

| Item | Status | Evidence |
|---|---|---|
| Seven palettes, Settings, tokens, icons, greeting and per-palette motion | Pass in isolated build; visual review prepared | Supplied code plus repairs in `THEMES-INTEGRATION-PLAN.md` |
| `make check` | Pass | 771 Python / 151 frontend tests; Ruff, mypy, format, coverage, API, motion, privacy; `make-check.log` |
| Contrast | Pass | 855 token pairs; `make-check.log` |
| Initial JS ≤256,000 bytes | Pass | 250,980 gzip bytes; `bundle.json` |
| Complete browser suite, both engines | Pass | 856 passed / four unchanged skips / zero failures in one 1.3-hour invocation; `make-e2e.log`, `browser-result.json` |
| Every palette/mode at 390/1440, serious/critical axe, Paper settings | Pass | `theme-screens.spec.ts`, `theme-preferences.spec.ts` and `screens/` |
| Complete greeting, English-only, reduced motion and latest theme wins | Pass in complete suite | Retained before/failure logs and new regression tests |
| Ordinary chat payload unchanged | Pass | Existing `test_default_request_matches_phase3_golden` in full Python run |
| API/schema/dependencies | Pass | Additive/API-type guards; settings keys only, no migration/lockfile edit |
| Original source and installed runtime/static preserved | Pass; 611 installed and 504 frozen source files match | `preservation-before.json`, `preservation-after.json` |
| Real iPhone / saved Home Screen icon behavior | Pending | No new physical-device result claimed; VoiceOver historical limitation retained |
| Merge and deployment | Not authorized here | Explicit isolated-branch approval |

Evidence root: `artifacts/themes/review-20261023/`.

## Changes and reasons

- Web: retain all seven palettes, Claude's layout and theme-specific motion,
  before-React palette/mode, synchronized preferences and icons/manifests.
- Web repairs: revision-bound snapshot callbacks, cancellation of old transitions,
  keyboard-origin reset, language/reduced-motion cancellation, full name/glow
  duration accounting. Slots are 700 ms rather than 780; the name fade is 200 ms.
  No palette color values were changed.
- Performance: lazy design fixture shell and non-Appearance Settings panes. The
  supplied patch is 259,983 bytes, the repaired candidate 250,980 and the live
  installed build 255,948, all with the same measurement method. This saves
  9,003 bytes versus the supplied patch and 4,968 versus live.
- PWA: cache/fingerprint the 36 new public icon/manifest files (213,425 bytes).
  No API/private data enters that cache. Qualify Home Screen icon copy until a
  real device check rather than instructing removal/re-addition as a fact.
- Server: validate/store two additional appearance preferences. Existing settings
  storage/schema suffices; no migration or request pipeline change.
- Tooling/tests: all-palette contrast, named snapshot-only clip-path permission,
  bounded greeting exception, and regression/appearance/browser coverage.
- Paper settings: explain the forced Newsreader interface, disable ineffective
  answer-font controls while Paper is selected, and retain the saved choice for
  the next palette. Eight browser cases cover the override/return and persistence.
- Docs: authorization, integration plan/report and `AUTOMATION-FOLDER-PILOT-PLAN.md`.

## Changed files

- Server: `server/app/db/settings.py` and appearance/Phase 4 guard tests. No
  provider, run, prompt, model, workflow engine or database-schema edit.
- Theme behavior: `web/public/theme-init.js`, `web/src/lib/{appearance,greetings,
  palettes,status-words}`, preference synchronization, UI store, ThemeProvider,
  AnimatedGreeting, EmptyState, WorkingLine and AtelierMark.
- UI/style: PalettePicker, SettingsDialog, AppShell/LiveAppShell, Composer,
  Button/Switch/Slider, global/palette/motion styles and the design theme lab.
- Loading/public assets: router/main lazy routes, Vite cache fingerprint,
  six new palette icon directories and manifests (Cobalt retains existing assets).
- QA/tooling: `scripts/check_{contrast,motion}.py`, appearance/greeting/palette
  unit tests, existing-test ledger below and four new theme browser files.
- Docs: AGENTS amendment, integration plan/report, supplied source documents,
  future-plans index and local-automation/recording-folder proposals.

The final evidence inventory records exact tracked web/server-app/tooling file
hashes; it is not a claim to hash model weights or private data. Historical
artifacts overwritten by browser capture are archived separately and restored;
their earlier committed results are not replaced with this checkpoint's output.

## Test-diff ledger and deviations

| Existing file | Change | Why it does not conceal an existing failure |
|---|---|---|
| `web/tests/helpers.ts` | Exempt only known CSS greeting animations within the exact greeting heading and ≤900 ms per animation | J18 specifically approved the ≤4.5 s decorative sequence. The 1,000 ms deadline/assertion is unchanged; a new negative browser test proves a generic ambient wrapper cannot bypass it |
| `server/tests/test_phase4_guards.py` | Add positive named snapshot case and negative regular-element/old-snapshot cases | Existing dead utility, forbidden color and API/payload/migration assertions remain |
| `scripts/check_motion.py` | Named `theme-reveal` clip-path exception, restricted to new root snapshot selectors | J19 approval; arbitrary keyframes and regular-element reuse remain forbidden |
| `scripts/check_contrast.py` | Check all palettes and fill/label tokens | Extends coverage; existing thresholds remain |
| `web/tests/foundation.spec.ts` | Wait for the lazy design shell to be visible and settled before Ctrl+, | The actual shortcut, theme-toggle and Escape assertions remain; no timeout increase |
| `web/tests/qa-repairs.spec.ts` | Expect compact visible Default, retain exact Model default accessible name and require its tooltip | Matches the already-approved 21 October mobile Tools correction recorded in AGENTS.md; option/selection/runtime semantics remain asserted |

J20 changes Paper's interface font as approved. Existing themes and original
prompt/sampling settings are preserved. These are the named, reviewed deviations;
no blanket ambient-motion exception or enlarged startup budget is used.

The new pre-React test checks the root palette/mode before React executes, then
checks the resolved body color while React remains intercepted. It no longer
requires a stylesheet to finish synchronously at module start or an exact hex
serialization (`#000` versus `#000000`). It does not measure physical first-paint
timing or prove a no-flash result on an iPhone.

New theme tests explicitly settle before axe. The proposed unsupported-browser
transition skip is replaced with assertions for the immediate fallback. Those
test-only strengthenings were made before the fresh complete invocation;
product source stayed unchanged. `test-hardening.json` and the final source
inventory retain their hashes. The full frontend check was repeated and passed
after the edits. Eight readiness/color checks pass in both engines in
`ready-state-browser.log`.

## Gates and frozen core

The complete invocation passes in both engines: 856 passed, four unchanged
engine-specific skips, zero failures. All 88 new theme cases pass. Focused runs
and the earlier interrupted attempts are not substituted for this result.

| Gate | Checkpoint evidence / status |
|---|---|
| G1 | Full check passes, all server coverage floors exceed 80%; final frontend hardening check also passes |
| G2 | Pass: one complete Chromium/WebKit run, 856 passed / four existing skips / zero failures, exit 0 |
| G3 | Ledger above; named user-approved exceptions only; no raised threshold, removed assertion or added skip |
| G4 | 250,980-byte initial JS, 4,968 bytes below installed; frame/scroll/first-token tests pass in the complete run; metrics below |
| G5 | 855 contrast pairs pass; all-palette/Settings axe and keyboard checks pass in the complete run; VoiceOver not claimed |
| G6 | API additive/type checks pass |
| G7 | No migration; existing Phase 3 row-preservation fixture passes |
| G8 | Existing frozen-prompt hash tests pass; no prompt edits |
| G9 | No search/runs/providers source change; no new inference eval required or executed |
| G10 | Ordinary-chat golden capture and unset-parameter assertions pass |
| G11 | Marker-based audit passes; synthetic screenshots only; 60 fake-labelled theme captures with byte-preserving lineage; 1,718 historical files restored and fresh captures retained separately |
| G12 | Deployment tests pass; no deployment performed; public-only PWA cache checks pass in the complete run |
| G13 | System and Always motion tests plus greeting interruption checks pass in both engines |
| G14 | `/design?themes`, existing design routes and production Settings components cover new states |
| G15 | No migration, so migration rollback rehearsal is not applicable; joint-release fallback remains a later publication step |
| G16 | New physical iPhone review not checked |

| Core | Guard retained |
|---|---|
| C1 send/stream/stats | `chat.spec.ts` live chat; final browser invocation |
| C2 Stop/partial/connection | `chat.spec.ts` Stop and `phase3-accessibility.spec.ts` Escape |
| C3 reconnect | `chat.spec.ts` close/reopen and `web.spec.ts` late-snapshot protection |
| C4 long reply/idle | `chat.spec.ts` timed long-answer/idle-timeout test |
| C5 chat actions | `actions.spec.ts` branches/rename/pin/export/delete |
| C6 model operations/context | `load-selection.spec.ts`, `ui-regressions.spec.ts` |
| C7 user parameters | `parameters.spec.ts` and full Python request captures |
| C8 Search/citations/retry | `web.spec.ts` plus Python search/evidence/grading tests; production prompt/payload frozen |
| C9 recordings/retention | `transcription.spec.ts`, `recording-download.spec.ts`, `audio-storage.spec.ts`, Python transcription tests |
| C10 phone/keyboard/safe areas | `mobile-layout.spec.ts`, `mobile-composer.spec.ts`, new Paper width cases |
| C11 commands/PWA/update | `polish.spec.ts`, `pwa.spec.ts`, exact offline theme-asset test |
| C12 legacy import | Full Python read-only/idempotency tests pass |
| C13 deployment identity | Full Python deployment tests pass; installed source/health preservation separately audited |
| C14 untrusted content | `foundation.spec.ts` Markdown and Python SSRF tests |
| C15 rendering budgets | `performance.spec.ts`, frame/first-token tests and bundle JSON |
| C16 labels/focus/axe | Foundation/review/Phase 3 accessibility and new palette/Settings matrix; historical VoiceOver failure retained |

## Retained failures

- Original supplied candidate: 259,983-byte startup bundle exceeds the unchanged
  256,000-byte ceiling by 3,983 (`original-bundle.json`).
- All three new transition-race unit tests fail against the original patch
  (`original-race-tests.log`), then pass after repair.
- English-only during exit and resuming an abandoned greeting fail in both
  engines against the original patch (`original-greeting-tests.log`).
- Expanded visual/axe run: 52 pass, 26 phone-size cases fail on the same serious
  keyboard-focus issue in the Theme Lab's scrollable comparison table
  (`table-keyboard-failure.log`). Add a named focusable region; keep the axe rule.
- A temporary TypeScript narrowing error in the stricter helper is retained in
  `repair-types-failure.log`; the final check uses explicit numeric narrowing.

- First full browser attempt: deliberately interrupted after 86 passed / one
  interrupted case to repair Paper's misleading font control; 773 did not run.
  It is not a release pass (`full-browser-interrupted-for-font-review.log`).
- A subsequent full invocation was interrupted after three failures: the two
  shortcut checks ran before the lazy shell mounted, and the old QA test expected
  the pre-21-October visible label. Retain 247 passed / three failed / one
  interrupted / one skipped / 608 unrun in
  `full-browser-stale-label-failure.log`; it is not a release pass.
- The combined theme preflight retained 97 passes / three failures in
  `first-style-timing-failure.log`. All palette/width axe cases passed; the new
  before-React test assumed synchronous stylesheet application and identical hex
  spelling. The corrected test preserves both pre-React attributes and actual
  resolved-color assertions without either assumption.
- The initial new offline-assets check fails only in WebKit under `setOffline`;
  reloading does not fix it. The old icon/manifest fail identically, while direct
  Cache Storage reads succeed. Both old/new fetches pass in Chromium. Original
  diagnostics and the executed diagnostic source are retained.
- This matches [Playwright #42775](https://github.com/microsoft/playwright/issues/42775).
  Replace emulation with actual loss of an isolated loopback origin: no-store
  responses, exact SHA-256 checks of the 21 selected palette chrome icon/manifest URLs
  and an uncached
  request that must fail. This adds no skip and passes in both engines. It does
  not claim physical iPhone offline verification.

## Test output

- Full `make check`: **771 Python / 151 frontend tests pass**, 855 contrast
  pairs, API contract/additive checks, frozen prompts, payload golden, motion
  guard and privacy marker scan pass (`make-check.log`).
- Line coverage: providers 89.7%, runs 89.5%, search 89.8%, transcription 93.2%,
  documents 96.6%, Library 92.6%, images 83.6%, workflows 89.8%; all exceed 80%.
- Complete browser invocation: **856 passed / four unchanged skips / zero
  failures, 1.3 hours, exit 0**. Chromium: 429 passed / one skip; WebKit: 427
  passed / three skips. All 88 new theme cases pass. The unchanged suite contains four
  pre-existing engine-specific skips: real-time timeout gate once on Chromium,
  base screenshot set once on Chromium, native HEIC decoder once on WebKit,
  and WebKit's existing offline-navigation emulation limitation. No skip added.
- Latest frontend type/lint/format/unit check and eight readiness/color checks
  pass. Retained partial/failed trials above are diagnostic, not qualification.

### Measured browser budgets

| Measure | Chromium | WebKit | Existing limit |
|---|---:|---:|---:|
| Streaming render p95 at 100 tok/s | 3.30 ms | 3.00 ms | ≤8 ms |
| First-token display overhead | 82.36 ms | 65.49 ms | ≤150 ms |
| 300-message scroll rAF interval p95 | 16.80 ms | 20.00 ms | Existing scroll test passes |

Only the streaming row renders in both measurements. Render CPU duration and
scroll rAF interval are different measures. Fresh JSONs are preserved under
`regression-metrics/artifacts/phase-3/` and `phase-1/`; original tracked metrics
are restored. Initial JavaScript is 250,980 gzip bytes, below the 256,000 ceiling.
The complete greeting tests assert the name/glow finish within 4,500 ms in both
engines; no physical timing result is claimed.

## Runtime observations and preservation

All browser work uses the existing isolated fake runtime; no native image,
chat, embedding or transcription experiment is run. Model/framework/Research
trials remain stopped. The four source theme inputs match the supplied originals in both workspaces.
The final audit verifies all 611 installed public files and 504 frozen web/server
app/tooling files unchanged. Remote main remains `4d33913c`; the original working
checkout remains `codex/masked-photo-editing` at `8f38ef7b`. Both final local and
normally verified Tailscale HTTPS health checks return 200.
Framework Python's local CA lookup failed; system curl verified HTTPS without
a verification bypass. Production process 40583 still listens on `127.0.0.1:8787`; no restart, route
change, model refresh, package installation or deployment was performed.

Fresh captures of 1,718 overwritten historical artifacts and 40 untracked
synthetic Settings captures are retained privately. All 1,718 historical files
were restored and their previous hashes verified. Sixty new theme captures are
fake-labelled without changing bytes. Twenty-five unnormalized logs are kept
privately; public copies normalize only trailing whitespace, terminal blank lines and line endings, with
both hashes in `log-provenance.json`. See `historical-artifact-preservation.json`,
`screenshot-lineage.json` and `visual-review.json`.

## Screenshots and release limits

Theme/new-chat and Paper Settings captures are under `screens/`, labeled with
palette, mode, width, browser and fake/synthetic provenance. The clean `visual/`
set includes Lime/Paper light and Midnight/Orchid dark at 390 and 1440. Manual
inspection of these selected captures found no clipping of the greeting,
composer or sidebar. The Paper Settings override explanation also fits at phone
width. This is a sampled visual review, not a physical-device result.

Eight synthetic motion clips (seven palette examples and one Always reduced
motion) are retained outside Git; paths are in `motion-review.json`. Sampled
Lime clip frames show the language sequence, final greeting, fake send/thinking
and answer; recordings do not establish animation feel on Jake's phone. Full
browser timing/reduced-motion assertions remain the automated gate.

The historical VoiceOver failure remains unresolved and outside this work list.
The previously reported iOS keyboard-focus incident recovered after restart;
its cause was not proven. No physical phone/icon/offline pass is inferred from
Chromium or Playwright WebKit.

Release must include compatible server and web together: the old server rejects
the new preference keys. Before publication retain the installed app/static
fallback and normal database backup. No migration needs reversal; a rollback to
the prior matched server/web should retain current chat data and ignore the
additional appearance keys, rather than blindly restoring an older database.

## Open questions for Jake

Review the theme appearance and motion, then decide whether to authorize a joint
server/web release. After that, check the real Home Screen app, keyboard, theme
persistence, greeting/reduced-motion behavior and saved icon. A phone result is
currently **not checked**. The recording-folder NS0 proposal is a separate next
implementation decision, not already enabled by this report.

## Next checkpoint

Review this branch, then authorize a joint release separately and perform the
real iPhone check. After the theme checkpoint, NS0 is the proposed first automation
step: CPU/fake-runtime recording intake, deduplication, recovery and local output
writing. NS1 folder selection, unattended enablement and native quality tests
remain separate. No watcher, schedule or agent framework is started here.
