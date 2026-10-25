# Design critique: assessment and implementation order

25 October 2026. Supplied review: `docs/next/design-critique/` in Jake's original
workspace. The original documents and screenshots remain unchanged there. Private
live-screen captures are inputs for review, not new committed QA evidence.

## Assessment

| Finding | Evidence and response |
| --- | --- |
| Aero production blur | Independently reproduced: the unchanged release build emits `index-Bels1uGb.css` with seven prefixed-only rules. Reordering restores the standard declaration. This is a shipped regression. |
| Earlier QA gap | The material/contrast tests used Vite development CSS. The installed-assets observer did load the production build, but did not assert computed blur. Add a built-output guard and actual production-app browser coverage. |
| Missing photo provenance and stopped-answer state | The supplied screenshots show the user-facing ambiguity. Prioritize source thumbnails/mode labels and visible stopped/empty states in Part B. A generated follow-up is not evidence that the edit engine ignored an attached source; distinguish Create from Edit explicitly. |
| Gallery/settings/history hierarchy | The review identifies concrete interaction and layout costs. Retain the functioning graph editor and chat architecture while addressing them in separate checkpoints. |
| Branch changes activity time | Confirmed in code: the generic chat patch updates `updated_at` even when only `current_leaf_id` changes. Fix without altering generation requests or overwriting historic dates. |
| Models and memory | Friendly labels must remain separate from capability detection. Hide variants only through a stored preference; do not add name-based capability or routing rules. Any manual memory-release action must identify affected models and follow the existing scheduler/unload policy. |

## Approved decisions

Jake answered **“Approve all four”** to J22–J25 on 25 October:

- **J22:** in image mode, a follow-up visibly references the last result by default;
  an explicit Create image choice starts a new image. Ordinary text sends remain
  text sends. Show the chosen source before sending and do not silently reuse an
  unrelated branch's image.
- **J23:** feature starters replace Explain / Write / Code. Recent prompts need
  the same local data/privacy treatment as chat history.
- **J24:** Library becomes a page beside Workflows and Images; operational
  embedding settings remain in Settings.
- **J25:** archive greeting-only chats after a day, reversibly. The supplied plan
  requires presenting the schema before writing a migration. Define a narrow,
  tested rule, protect renamed/pinned/branched/attachment chats, provide an archive
  and restore action, and leave uncertain cases alone. No model classification
  call, deletion or prompt change is authorized by this decision.

## Checkpoints

### A — production glass repair

Branch/PR: `codex/aero-blur-fix`, based on main `6138e1f4`.

- Apply the seven declaration-order repairs.
- Dedicated 96%-opaque overlay token in light/dark; preserve the composer's and
  sidebar's existing surface tokens.
- Test all first-party source declaration order and check actual minified output
  after production builds, including `make check` and builds before `make e2e`.
- Test production Settings over a gallery image, Tools over a chat image, and
  composer/topbar/sidebar filters. Use invented data only, both engines, both
  themes, 390/1440 widths. Sample rendered contrast with and without blur.
- Run existing gates, retain failed attempts, record H4 and stop for review with a
  small PR. Do not treat the supplied prompt's deployment command as a new merge
  or release approval.

### B — truthful chat state, provenance and controls

Separate branch/PR after A's review. Implement the supplied B1–B9 requirements:
source/mode labels, visible image follow-up reference, stopped/empty state,
consistent model labels/picker, one settings commit action, thinking in Tools,
feature starters and spacing/actions. Preserve user-selected parameters and
ordinary provider requests; Continue and Retry are explicit user actions.

Investigate reference lifetime/availability before promising historic thumbnails
or a before/after view. Report any required schema change before implementing it.
Do not claim old references can be reconstructed if their source bytes are gone.

### C — gallery, Library, Settings, Studio and history

Separate checkpoint/PR, with sub-checkpoints if the diff is too large to review.
Implement C1–C6 from the supplied prompt. Lead with gallery-first Images and
explicit destructive confirmations, then Library/Settings and Studio clarity.

Before C5, present the additive archive schema, classification boundaries,
restore behavior and migration/data-preservation tests. Branch selection must
not advance activity time. Reuse existing capabilities and request paths.

### D — Aero decoration

Separate branch/PR: remove duplicated scene glow, soften the new-chat top band,
and keep bubbles out of the greeting/composer. Preserve approved motion bounds,
reduced-motion behavior, production glass and rendered contrast/performance.

## QA and release

Each checkpoint has the SPEC H4 report, test-diff ledger and applicable
`docs/next/QA-REQUIREMENTS.md` gates. Source CSS tests alone do not qualify a
production material change. Keep all earlier evidence and use new output paths.
No extra dependency, native inference, model download, automatic model routing,
Research restart, watcher or schedule is part of this work.

Physical iPhone review remains pending from the theme release (Jake said he would
check later). Chromium/WebKit emulation is not a physical device pass. VoiceOver's
historical limitation remains unresolved. A later approved web-only publication
must preserve current data and the reference-aware backend/worker; never restore
an old database over newer user data.
