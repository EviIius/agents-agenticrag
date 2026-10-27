# Design critique Part B — chat report

Started 25 October 2026; QA completed on 27 October. Branch:
`codex/design-critique-b`, based on main `e7bab217`. **Technical QA complete; ready for isolated review. Not merged or deployed.** The installed Part A build remains the release.

## Summary

Image requests show Create/Edit provenance and retained source previews. Image
mode offers the last visible reply's last available image as a visible edit
reference, with an explicit Create alternative. Ordinary text sends stay text.
Stopped/empty answers have visible outcomes and explicit continuation/retry.
Controls, model identity, picker variants, starters and spacing follow B1–B9.

## Done-when checklist

| Item | Status | Evidence |
| --- | --- | --- |
| Source/mode labels and unavailable references | Pass | ImagePrompt; chat-state source/reload/clear case |
| Visible default image edit; explicit Create | Pass | Composer, useChatImages; parent pinning/reference-failure case |
| Stopped/empty state and explicit Continue/Retry | Pass | LiveThread; retained-draft and explicit-parent request assertions |
| Consistent names and runtime family variants | Pass | Explicit alias helper; model-groups unit tests; accessible picker grid |
| One Save, scoped settings and retained thinking | Pass | Partial failure/retry case; full parameter regression gates pass |
| Thinking only in Tools, Max label | Pass | Same runtime `xhigh`; existing Tools tests updated only for label |
| Feature and recent-prompt starters | Pass | Existing attachment/Library flows; synthetic `/design` starter state |
| Spacing without blocked actions | Pass | Product containment repair; unchanged actions test passes in the complete run |
| Full gates, privacy and preserved evidence | Pass, device review pending | Final logs; verification.json; privacy-final.json |
| Main/live/device acceptance | Not changed / pending | Separate review stop; real iPhone/Safari not claimed |

## Changed files

- **Web chat:** Composer, LiveThread, ImagePrompt, ImageTurn, MessageActions,
  StatsLine, ToolsMenu, ToolChips and useChatImages.
- **Web app/settings:** LiveAppShell, ModelPicker, LiveChatSettings,
  SamplingFields, control-drafts, model display/grouping helpers, status copy and
  the Studio model field; spacing styles use existing tokens.
- **QA/design:** new production-component `/design?chat-state` states and browser
  cases; six new frontend unit cases; existing selector/approved-flow updates
  are itemized in the test-diff ledger.
- **Server/schema/provider/worker/dependencies:** unchanged.

## Deviations and runtime observations

- Original filenames were not retained by the photo-reference API. Historic
  source labels use “Photo reference”, not an invented filename. Existing
  schema-14 previews and availability are sufficient; no migration was added.
- The reference viewer shows the normalized engine input, not a reconstructed
  private original. Cleared/missing source bytes stay visibly unavailable.
- Keep stored model names and visibility. The reviewed exact Qwen tag gets an
  explicit presentation alias; unknown tags are literal. No regex prettifying,
  model-name capabilities, automatic hiding or routing.
- Defaults apply to new prompts in image mode. Existing Refine/More like this
  retain their generation lineage and Create label; explicit Edit image binds
  source pixels. The default picks the last available image in the last visible
  image reply, with its thumbnail shown before send.
- Model picker actions need a grid, not buttons nested inside listbox options.
  Existing cmdk forces its default roles; local `asChild` elements preserve its
  keyboard behavior while providing grid/row/cell semantics. No vendor or
  dependency change.
- One Save is the approved replacement for context Apply and separate commits.
  It saves only dirty groups, preserves thinking values, and retains any failed
  group for retry without repeating completed groups. Reset stages a change.
- Recent prompts come from the two latest nonempty chats in the loaded main
  history view, through existing read-only chat queries; no separate history
  store, prompt rewriting or automatic send.

## Test output and retained attempts

**Final single complete browser run: 918 passed, four unchanged skips, zero
failures (1.4 hours), Chromium and WebKit.** The executed 526-file source manifest
verifies unchanged after both gates. The focused runs below are retained as
diagnostics and are not combined into this gate result.

At 100 tokens/s, render p95 is Cobalt 3.6/3.0 ms and Aero 3.4/3.0 ms
(Chromium/WebKit); only the streaming row renders. 300-message scroll median is
16.7/17 ms. First-token overhead is 91.5/76.2 ms, below 150 ms.


- Final `make check`: **785 Python /157 frontend /969 contrast pairs**; earlier
  complete 785/156/969 pass retained,
  all lint/type/API/privacy/motion/build guards pass. Backend coverage is above
  80% for every guarded package (images: 83.5%).
- Initial module JS: **255,345 /256,000 gzip bytes**, compared with 252,228 at
  Part A (+3,117 bytes). Only 655 bytes of this budget remain; later page work
  should retain lazy loading. This uses the unchanged static-import measurement.
- Initial browser fixtures: two provenance cases passed; readiness, wrong fake
  model reasoning and unscoped selector errors were retained and corrected.
- Next browser pass: all eight functional cases pass; all eight design cases
  expose nested-interactive controls in the new picker. Subsequent retained
  trials identify the listbox role restriction and cmdk's forced-role/asChild
  behavior. The final grid smoke passes with real variant expansion, search,
  keyboard selection and axe, without excluding any axe rule.
- An accidentally duplicated make-check process was stopped; its partial log is
  retained and contributes no gate result.
- The QA wrapper initially recalculated the bundle with different compression
  and an extra classic script, then stopped before browsers. It now calls the
  unchanged repository measurement directly; the wrapper error is retained in
  `bundle-controller-error.md`. No product or threshold change was needed.
- The affected regression run passes 126 cases, with two 320px keyboard-space
  failures retained. Restoring outer drawer scrolling passes all four 320/390px
  cases in both engines without changing the 99% visibility requirement.
- Recency review found pinned-first history could select old prompts. Activity
  sorting now excludes empty chats; a sixth unit case proves pinned records do
  not displace the recent prompts. One fixture initially omitted required
  `title_source`; the failed type check is retained, and corrected frontend
  preflight passes all 157 tests.
- The shared-state fix passes 45 focused cases with one unchanged real-time
  WebKit skip. A subsequent visual review found the mobile follow-up preview
  squeezed by the Create button. The button now wraps below the fixed 56px
  preview, with explicit geometry assertions. All 18 new cases pass both engines.
  The earlier check was stopped before browser startup; its partial log remains.
- A pre-ordering browser invocation was stopped after its first 25 passing cases
  to include that recency repair; no aggregate gate is claimed from it.
- A subsequent full invocation found shared fake-model preferences leaking from
  the new controls case into ordinary chat tests. New cases now snapshot and
  restore those global preferences after every test, including failures; the
  original core assertions stay unchanged. The failed full log is retained.
- The later complete-run attempt reached 206 cases and found two stale keyboard
  selectors still expecting Stopped in hidden stats. Both now assert the visible
  outcome status; keyboard regeneration uses its explicit Retry button. Existing
  focus, request, branch and citation assertions are retained. The two failures
  and interrupted run are preserved in `make-e2e-keyboard-failure.log`.
- The corrected keyboard walkthrough and early-Escape cases pass in Chromium
  and WebKit: 12 focused cases, with no relaxed timeout or missing focus step.
  Final frontend preflight also passes all 157 tests.
- First full browser invocation was stopped after its unchanged actions case
  exposed a covered Edit button. Removing paint containment from user rows keeps
  floating controls above the following assistant. Earlier results are retained;
  a fresh complete run is required.

Raw tool logs and automated failure contexts retain their original generated
whitespace. Source/docs diff checks pass; retained evidence is not reformatted
to silence whitespace diagnostics.

## Test-diff ledger

See `artifacts/design-critique-b-20261025/test-diff-ledger.md` for each edited test.
No threshold/timeout/skip change or forced interaction is used.

## Screenshots and evidence

`artifacts/design-critique-b-20261025/`: browser/check logs, failure contexts,
source and bundle manifests, synthetic design captures and final verification.
Raw traces and intermediate captures are retained privately under
`~/.local/share/workbench/qa/design-critique-b-20261025/`. Supplied Claude live
screenshots remain in the original workspace and outside new committed evidence.

## Evals, migrations and deployment

No server/runs/providers/search prompt or request pipeline changed; G9 inference
is not applicable. No new schema, migration or rollback rehearsal, package,
download or native model call. Continue/Retry use existing user-triggered answer
paths, and image follow-ups use existing explicit reference creation/acceptance.
No new background model work or schedule is added.

## Open questions and carried limitations

Part B stops for review before merge/publication. Physical iPhone/installed Safari
review remains pending; Jake previously said “I’ll check later”. Historical
VoiceOver and the prior unproven iOS keyboard-focus incident remain unresolved.
The broader gallery/Library/Settings/history/Studio and Aero scene changes remain
Part C/D work; archiving still requires presenting the schema/rule first.

## Gates (technical checks complete; device review pending)

| Gate | Evidence / status |
| --- | --- |
| G1 | Pass: final make check 785 Python /157 frontend /969 contrast; initial complete 785/156/969 pass retained |
| G2 | Pass: one complete make e2e, 918 passed / four existing skips / zero failures, 1.4 h |
| G3 | All sixteen existing edited test files are in the ledger; unchanged actions test exposed the repaired hit-area bug |
| G4 | Pass: 255,345 bytes; render p95 ≤3.6 ms; scroll median ≤17 ms; first-token overhead ≤91.5 ms |
| G5 | Pass: 56 new design-state audits, zero serious/critical findings; 72 final captures including 16 source/cleared views |
| G6–G8 | API, schema and frozen prompts unchanged; their existing guards remain in make check |
| G9 | Not applicable: no server search/runs/providers change; no new inference eval |
| G10 | Exact parameter captures pass in both engines; test_default_request_matches_phase3_golden remains unchanged |
| G11 | Synthetic evidence only; privacy-final.json and verification.json; prior artifacts and supplied inputs verified |
| G12 | Pass: installed files, PID 77443, plist/bind/port/route unchanged; local/verified HTTPS health and PWA/API-cache tests pass |
| G13 | Pass: existing motion guards and both reduced-motion triggers in the complete run |
| G14 | Production components on /design?chat-state; source/cleared/stop/empty/control/follow-up/variant/starter states |
| G15 | Not applicable: no migration or deployment |
| G16 | Physical iPhone/installed Safari review pending; no acceptance attributed to Jake |

## Core coverage

All rows below pass the complete browser/backend gates, with explicitly approved
presentation/commit changes. This covers ordinary keyboard/axe behavior; it does
not claim physical-device or VoiceOver acceptance:

| Core | Evidence |
| --- | --- |
| C1 Send/stream/stats | chat.spec.ts |
| C2 Stop/partial/disconnect | chat.spec.ts, phase3-accessibility.spec.ts |
| C3 Reopen/resume | chat.spec.ts, web.spec.ts |
| C4 Long/stalled streams | chat.spec.ts |
| C5 Edit/regenerate/branches/actions | actions.spec.ts (unchanged); source containment repaired |
| C6 Load/eject/context | load-selection.spec.ts, ui-regressions.spec.ts |
| C7 User-set parameters only | parameters.spec.ts; Python golden and chat request captures |
| C8 Web/citations/failures | web.spec.ts; unchanged Python search/evidence tests |
| C9 Recording/documents/retention | transcription, recording-download and audio-storage suites |
| C10 Mobile/safe areas/keyboard | mobile-layout, mobile-composer, deferred-polish and tools-menu-layout suites |
| C11 Palette/PWA/updates | polish.spec.ts, pwa.spec.ts |
| C12 Read-only legacy import | test_legacy_import.py |
| C13 Service invariants | test_deployment.py plus installed hash/health verification |
| C14 Untrusted markup/SSRF | foundation.spec.ts; Python search security tests |
| C15 Performance | performance.spec.ts and chat.spec.ts; final copied metrics |
| C16 Ordinary accessibility | foundation, review, phase3-accessibility and new design-state axe |

## Preservation and review

`verification.json` verifies all 32,377 historical artifacts and 15 supplied
critique files. Fresh bytes from 2,290 regenerated historical files were retained
privately before restoring their original tracked versions; 108 additional old
checkpoint captures were also archived. No earlier result was rewritten as a pass.

All 520 installed static files, 126 backend/lock/shared files and four worker files
remain unchanged, along with runtimes/selectors, plist and Tailscale route. The
same service PID 77443 and local/normally verified HTTPS health pass. No live API
mutation, native inference, download, dependency, schema, prompt or sampling-policy
change; no merge, publication or database restore.

The full run contains two Vite dynamic-import console messages around the
existing rapid workflow navigation test. The Part A full log contains six of the
same messages. Navigation and subsequent workflow assertions pass; no global
zero-console-error claim is made. The new design cases and 16 provenance captures
explicitly check for application errors and report zero.

Synthetic preview: http://127.0.0.1:5173/design?chat-state. Choose thread, cleared,
followup, variants, controls, image-controls or starters. Only fake data/runtimes
are connected. This is a review candidate; the live app is still Part A.

Stop for Part B review. Part C/D, physical iPhone/installed Safari checks and any
merge or deployment remain separate. No new phone acceptance is attributed to Jake.
