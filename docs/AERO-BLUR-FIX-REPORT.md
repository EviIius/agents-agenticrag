# Design critique Part A — production glass report

25 October 2026 · branch `codex/aero-blur-fix` · draft PR #12.

> **Technical QA complete:** one full run passes 900 browser tests with four
> existing skips and zero failures. Main and the installed app remain unchanged.
> This is ready for the Part A review; no physical-phone pass is claimed.

## Summary

Claude's main diagnosis is correct. The unchanged release builds the exact CSS
file served live, `index-Bels1uGb.css`, with seven prefixed-only backdrop rules.
Chrome loses Aero's blur. The candidate reverses all seven declaration pairs and
uses a separate 96%-opaque token for reading overlays in light and dark.

The previous material audit used development CSS. The installed-assets observer
loaded the production app but did not assert computed blur. This repair closes
both gaps: source/build guards and a test of the actual minified app over an
asserted high-contrast synthetic image, with rendered contrast and no-blur fallback.

## Done-when checklist

| Item | Status | Evidence |
| --- | --- | --- |
| Confirm shipped regression | Pass | `artifacts/aero-blur-fix/baseline-glass.json`, `live-baseline-css.json`: same SHA; seven broken rules |
| Restore standard filter | Pass | `web/src/styles/aero.css`; source negative control rejects the original seven pairs; candidate build guard passes |
| Stronger overlays, unchanged composer/sidebar tokens | Pass | Light/dark `--aero-glass-overlay` 0.96; dialog/menu/popover/select/sheet/drawer use it |
| Prevent production recurrence | Pass | `scripts/check_glass_css.py`; seven new Python cases; guard runs after every npm production build, including make check/e2e |
| Actual production app, two themes/widths/engines | Pass | `web/tests/aero-production.spec.ts`, `production-focused.log`: 8/8; production CSS URLs and computed standard filter asserted |
| Settings over gallery / Tools over image | Pass | Synthetic checkerboard/dot image; route hit and decoded width asserted; no private photograph |
| Readability with and without blur | Pass | `browser/*-contrast.json`; final values in `production-rollup.json` |
| Existing suite, performance and keyboard regressions | Pass | One complete `make e2e`: 900 passed, four existing skips, zero failures (1.3 h) |
| Supplied inputs and installed app preserved | Pass | `verification.json`: 15 input files, 600 installed public files and 456 executed source files unchanged; original workspace/main unchanged |
| Merge/deployment | Not performed | Separate review stop; draft PR #12 |

## Changed files

- **Product:** `web/src/styles/aero.css` only.
- **Build:** Makefile and `web/package.json` invoke the compiled CSS guard.
- **QA:** new source/build guard, Python negative controls and production browser
  coverage. Extract existing contrast helper into `web/tests/material-contrast.ts`.
- **Docs:** AGENTS authorization/closeout, this report, and
  `docs/DESIGN-CRITIQUE-IMPLEMENTATION-PLAN.md`.
- **Server/runtime/data:** no application, schema, dependency, worker or model
  change. No real model call, automatic unload or download.

## Test output

- `make check`: **785 Python tests**, **151 frontend tests**, **969 contrast pairs**;
  lint, typing, API types/additivity, privacy and motion all pass. Backend coverage
  remains above 80% for every guarded package (images is lowest at 83.5%).
- Rechecked frontend lint/types/format/unit tests after the final browser fixture
  correction: **151 pass**.
- Original built CSS guard: **fails seven rules**. Original source guard:
  **fails seven unsafe pairs**. Candidate production build: **five stylesheets pass**;
  source guard: **eight stylesheets pass**.
- Focused corrected production browser run: **8 pass**, no skips, both engines.
- Full browser output: `artifacts/aero-blur-fix/make-e2e.log`: **900 passed, four existing skips, zero failures (1.3 h)** in a fresh single invocation.

### Retained test attempts

1. First focused run: one pass, seven failures. Reusing the same synthetic prompt
   made the gallery selector ambiguous as job history accumulated. Give each case
   a unique prompt; keep the strict image assertion.
2. Next focused run: eight passes. Visual inspection found that WebKit's service
   worker bypassed the image route and used the plain fake-engine output. These
   results do not establish the intended busy-image coverage.
3. The first full invocation was deliberately interrupted early after that fixture
   gap was found. Its log is retained; it is not assembled into the final gate.
4. Block service workers only in this production-material test, assert that the
   replacement response was used and the 1024px fixture decoded. The corrected
   focused run passes all eight; start a fresh complete run from there.

Raw traces/intermediate images remain privately under
`~/.local/share/workbench/qa/aero-blur-fix-20261025/`. Failure logs are retained in
the new artifact folder. A stop-script encountered an already-terminated owned
Vite child; no installed service was stopped. An initial patch-context mismatch
made no file changes and was corrected before the focused rerun.

## Test-diff ledger

| File/test | Change | Why | Behavior still asserted? |
| --- | --- | --- | --- |
| `aero-integration.spec.ts` / existing material and negative-control cases | Extract measurement into shared helper, add import/wrapper | Reuse the same pixel/hit-test/clock method for production-app tests | Yes; body compared after signature/format normalization and identical; no assertions/thresholds/skips/timeouts changed |
| `aero-production.spec.ts` | New production-build cases | Catch minification and image-behind-overlay regressions | Builds, images, computed filter, alpha, axe and sampled contrast all asserted |
| `test_glass_css_guard.py` | Seven new cases | Source order, minified nesting, comments, missing output and CLI behavior | Both positive and negative controls |

No existing assertion is removed or weakened. `material-contrast.ts` contains the
same implementation as the previous in-file helper.

## Deviations and runtime observations

- Adapt the supplied check from `web/dist/assets` to this repository's actual
  production output, `server/app/static/assets`, and add source-order controls.
- Use 0.96 overlay alpha, within the supplied minimum of 0.92. Do not change the
  composer/sidebar surface values or the blur strength.
- Run the material regression against built assets, not Vite development CSS.
  Block service workers only for that routing-controlled fixture; the existing
  PWA/browser tests keep their normal worker behavior.
- No real model/runtime experiment was needed. A read-only static fetch confirmed
  that the live stylesheet and the reproduced unchanged build have identical SHA.
- Publication is held at the repo's phase review checkpoint. No supplied shell
  command was taken as permission to restore a database or old backend.

## Core-flow coverage

The complete green full-run log and make check are the evidence for these
unchanged flows. No partial-run assembly was used.

| Core | Existing evidence retained |
| --- | --- |
| C1 send/stream/stats | `chat.spec.ts` |
| C2 stop/partial text | `chat.spec.ts`, `phase3-accessibility.spec.ts` |
| C3 resume | `chat.spec.ts`, `web.spec.ts` |
| C4 long answers/timeouts | `chat.spec.ts` (existing engine-specific skip unchanged) |
| C5 branches/actions | `actions.spec.ts` |
| C6 model/context | `load-selection.spec.ts`, `ui-regressions.spec.ts` |
| C7 exact parameters | `parameters.spec.ts`, Python golden request |
| C8 search/citations/retry | `web.spec.ts`, Python search/grounding tests |
| C9 transcription | `transcription.spec.ts`, `recording-download.spec.ts`, `audio-storage.spec.ts` |
| C10 phone layout | `mobile-layout.spec.ts`, `mobile-composer.spec.ts` |
| C11 shortcuts/PWA | `polish.spec.ts`, `pwa.spec.ts` |
| C12 read-only import | Python legacy-import tests in make check |
| C13 service invariants | Python deployment tests; unchanged installed-file inventory |
| C14 inert untrusted content | `foundation.spec.ts`, Python fetch/SSRF checks |
| C15 budgets | `performance.spec.ts`, `chat.spec.ts`, `bundle.json` |
| C16 labels/focus/axe | `foundation.spec.ts`, `review.spec.ts`, `phase3-accessibility.spec.ts` |

## Gates

| Gate | Status/evidence |
| --- | --- |
| G1 checks | Pass: make-check.log; frontend-final.log |
| G2 one full browser run | Pass: 900 passed / four existing skips / zero failures; interrupted invocation retained separately |
| G3 no weakening | Ledger above |
| G4 performance | Pass: 252,228 initial gzip bytes; Aero render p95 2.8/3.0 ms, scroll median 16.7/17 ms; first-token gate passes |
| G5 accessibility | Pass: full axe/keyboard regression; eight production material cases, 584 sampled text runs, minimum 5.64:1 with or without blur |
| G6 API | Additivity/types pass; no API change |
| G7 schema | No migration/data change |
| G8 frozen prompts | Python prompt-hash checks pass; no prompt change |
| G9 web eval | Not triggered: no search/run/provider changes |
| G10 runtime payload | Existing golden-request test passes in make check; no provider change |
| G11 privacy | Scanner passes; only synthetic new screenshots; originals remain outside evidence |
| G12 deployment invariants | No deployment/service/Tailscale change; existing tests retained |
| G13 motion | Pass: motion guard and complete normal/system/always browser regression |
| G14 design states | Existing production components/design states; no new interaction state |
| G15 rollback | Not applicable: no migration or publication |
| G16 phone | Pending: Jake previously said “I’ll check later” |

## Screenshots and limitations

New synthetic screenshots are under `artifacts/aero-blur-fix/browser/`:
`{chromium,webkit}-{light,dark}-{390,1440}-{tools,settings,fallback}-fake-normal.png`.
Mask/background and per-text contrast measurements accompany them. Codex reviewed
the dark desktop Settings and light phone-width Tools captures; these are Codex
observations, not Jake's acceptance.

WebKit automation is not the installed Safari application or a physical iPhone.
The device check and historical VoiceOver limitation remain pending/unresolved.
No live user screen was recaptured, no user messages sent, and no data changed.

## Next checkpoint / open questions

J22–J25 are approved and recorded in the implementation plan. After A's review,
Part B starts with image-source/mode visibility and stopped/empty replies, then
controls and starters. Part C's archive schema/rule must be presented before a
migration is written. No larger chat/page change is in this PR.

## Final verification update

All technical gates pass. The complete run has 900 passes and the same four
engine-specific skips: real HEIC on WebKit only; long-duration chat and base
screenshots on Chromium only; existing WebKit offline-navigation emulation limit.
No skip, timeout, assertion or performance threshold was loosened.

- Actual production app: eight cases; **584 sampled text runs**, no failures.
  Minimum normal and no-blur contrast both **5.6366:1**, above 4.5:1 without the
  helper's existing 0.02 PNG quantization allowance. Different fake histories in
  the complete run give a more conservative minimum than the focused run.
- Initial JS **252,228 / 256,000 bytes**, seven bytes below the installed theme
  release. Aero p95 render **2.8 / 3.0 ms** and scroll median **16.7 / 17 ms**
  (Chromium/WebKit); only the streaming row renders. First-token client overhead
  is **73.30 / 61.86 ms**, under 150 ms. Fresh metrics are in
  `artifacts/aero-blur-fix/metrics/`.
- All **456 executed source files**, **600 installed public files**, **15 supplied
  inputs**, main and the original worktree HEAD verify unchanged. Health is 200.
  No installed API mutation or native model call occurred.
- **1,908 regenerated tracked artifacts** were copied to the private full-run
  archive, then the old committed artifacts restored exactly. **108 additional
  captures** are archived privately. New Part A screenshots/JSON/logs remain in
  this PR's own artifact folder. See `historical-evidence-preserved.json`.
- The PR is isolated; main merge and web-only publication are not performed.
  Preserve current data and the reference-aware backend/worker when publishing.
  The physical iPhone/Safari application check remains pending.

This closes Part A's technical work at the AGENTS.md / SPEC H4 review stop.
J22–J25 are accepted decisions for the later checkpoints, not changes already
implemented by this CSS PR.

Local review is restored at [the built app with fake engines](http://127.0.0.1:18787/)
and [the development theme lab](http://127.0.0.1:5173/design?themes). These use
a temporary synthetic database; the installed app remains on 8787.
