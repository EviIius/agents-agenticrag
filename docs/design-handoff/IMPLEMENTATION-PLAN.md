# Implementation plan: v2 UI redesign (for Codex)

**Owner:** Codex. **Design sign-off:** Jake. **Design source:** this folder.

**Approach:** rebuild the shell and answer anatomy on the existing zero-build stack (`index.html`, `styles.css`, `app.js` + vendored marked/DOMPurify). Keep the engine: the API, workflows, stores and tests. Ship in phases. Each phase leaves the app fully usable and ends with a screenshot comparison against `reference/screens/`.

## Ground rules (every phase)

1. **No framework, no bundler, no CDN, no new runtime dependency.** Plain HTML, CSS and ES2020 in the three existing files, plus `tokens.css` and `fonts/`.
2. **CSP-clean.** No `style=""` in markup or in `innerHTML`, and no `<style>` in HTML. Dynamic values go through `el.style.setProperty('--value', '37%')`.
3. **Additive API only** (see `DATA-CONTRACT.md`). Old saved chats must still render.
4. **Truth over decoration.** If a value isn't in the data, hide the element. No placeholder numbers in production UI.
5. **Keep behaviour:** stop, retry, attachments, dictation consent, project memory, projects, web-search consent, the mobile keyboard handling, PWA manifest and icons.
6. **Tests stay green** (`python -m pytest`). Add tests for every backend change.
7. **Don't touch** retrieval, ingestion, store or provider logic beyond what the DATA-CONTRACT items say.
8. After each phase, render the app at 1440×900 and 390×844 in dark and light, and compare with the references (QA-CHECKLIST §1).

---

## Phase 0: Foundations (small)

**Goal:** new fonts and tokens available, with zero visual change so far.

- [ ] Copy `design-handoff/fonts/*` to `src/agenticrag/ui/fonts/` (including the LICENSE files).
- [ ] Copy `design-handoff/tokens.css` to `src/agenticrag/ui/tokens.css`.
- [ ] `server.py`:
  - Add the `/tokens.css` and `/fonts/...woff2` routes to `UI_FILES`.
  - Send fonts as binary `font/woff2` with long caching (DATA-CONTRACT, Static assets).
- [ ] `pyproject.toml`: add the package data for the fonts.
- [ ] `index.html`: `<link rel="stylesheet" href="/tokens.css?v=2">` **before** `styles.css`. Don't delete anything yet.
- [ ] Test: `GET /fonts/Geist-Variable.woff2` returns 200 with `Content-Type: font/woff2` and no charset. `GET /tokens.css` returns 200.

**Done when** the fonts load in DevTools (Network → Font), nothing looks different yet, and the tests pass.

---

## Phase 1: Visual system swap (no layout change)

**Goal:** the current layout rendered in the new system. This is the cheapest big win.

- [ ] Delete the `:root { … }` and `[data-theme="light"] { … }` token blocks at the top of `styles.css`. `tokens.css` provides the same names.
- [ ] Remove the radial-gradient wash on `.workspace`, and any other gradients or glows.
- [ ] Typography:
  - Body uses `--font-ui`, mono uses `--font-mono`.
  - Assistant message content (`.message.assistant .message-content`) uses `--font-read` at `--text-read` / `--leading-read`, max 75ch. Tables and code inside it stay in UI and mono fonts.
- [ ] Remove every `text-transform: uppercase` eyebrow (`.eyebrow`, `.nav-label`, form labels). Make labels sentence case at 12px / 500 / `--ink-muted`.
- [ ] Radii: buttons and inputs 8, cards and panels 12, composer 16.
- [ ] One model display name (`modelDisplayName` → returns "Gemma 4 12B" style names with no "·" between family and size; context suffix " · 16K context"). Use it in the top-bar chip too: **no raw IDs in primary UI**. The raw ID goes in `title` tooltips and mono secondary lines.
- [ ] Fix the "You You · agent" meta. `appendMessage("user", …)` should render no speaker label (the full label removal comes in Phase 3; for now just drop the duplicated "You").
- [ ] `<meta name="theme-color">`: set it from JS in `setTheme()` to `--theme-color` (`#0C0C0D` / `#FAFAF8`). Update `manifest.webmanifest` `theme_color` / `background_color` to `#0C0C0D`.
- [ ] Readiness honesty, part 1: stop showing a green dot or "Configured 4/4" as if it meant *working*. Change the copy to "Configured · 4 of 4" with a hollow dot until B5 exists.
- [ ] Backend **B5** (runtime-status endpoint), then wire it into the top-bar chip dot, the readiness footer and the Models status labels.
- [ ] Replace the repo-root `DESIGN.md` with `design-handoff/DESIGN.md`, and update `.impeccable/design.json` to match (colours, typography, rounded, components), or delete it if nothing reads it.

**Done when:** the existing screens use graphite, cobalt, Geist and Newsreader answers; no uppercase labels remain; no raw model IDs appear in primary UI; the readiness dot only turns green when B5 says reachable; the tests pass.

---

## Phase 2: Shell and composer

**Goal:** the new frame (SPEC §1, §2, §8, §11). References: `01`, `05`, `08`, `15`.

- [ ] **Remove** `.topbar`, `.chat-header` (page title, eyebrow, session actions, workflow segmented control) and `#corpus-notice`.
- [ ] **Sidebar** rebuild (SPEC §1.1):
  - Brand row, project switcher (with a menu containing Project settings, into which Collection ID and Access label move), New chat + search, 4 nav rows with counts, date-grouped history (`updated_at`), running-chat spinner, readiness footer.
  - Delete the "Knowledge settings" `<details>` and the "Setup status" ring.
- [ ] **Title bar** (SPEC §1.2): breadcrumb, runtime pill (boundary states from `syncHostedCapabilities()`), theme toggle, panel toggle.
- [ ] **Composer** (SPEC §2):
  - Mode pill + **mode menu** (SPEC §8.2; typical times from `/api/v1/evaluation`, hidden when missing).
  - Scope pill with popover.
  - Icon buttons for attach, skills and web (with disabled explanation).
  - Dictate moves into the attach menu.
  - Send label per mode; Stop state; caption variants.
- [ ] **New chat / empty state** (SPEC §8.1): Newsreader headline, lede per mode, starter pills, readiness row, the no-sources variant (replaces the banner), and the unreachable-model notice card.
- [ ] **Chat management** (SPEC §6): delete from the history row menu; rename if you implement B9.
- [ ] **Responsive:** 1024–1279 panel drawer; 601–1023 sidebar drawer; **phone** layout with no bottom tab bar, a menu drawer, and a 60-high title bar (SPEC §11). Keep `updateMobileViewport()` behaviour.
- [ ] Keyboard: ⌘/Ctrl+K search, ⌘/Ctrl+N new chat, Esc closes the top layer.

**Done when** screenshots match references `05`, `15` and `08` (layout, spacing, type) and all existing flows still work: send, stop, retry, attach, dictate, projects, memory, web consent, theme.

---

## Phase 3: Answer anatomy, evidence and live runs

**Goal:** the product's signature: inspectable answers (SPEC §3, §4, §5). References: `01`, `02`, `03`, `04`, `09`.

Backend first:

- [ ] **B1** `at_ms` on events.
- [ ] **B2** tool argument summaries.
- [ ] **B3** SSE `event` / `evidence` frames and `started.limits`.
- [ ] **B4** `[n]` markers in the answer prompts, plus host-side marker repair.
- [ ] Tests for each (see DATA-CONTRACT).

Front end:

- [ ] Rewrite `appendMessage` / `appendLoading` / `renderResult` into an **answer component**: meta row, verification badge (SPEC §3.3 table), steps summary (event mapping SPEC §3.4), answer body (Newsreader), citation pills (text-node walk, SPEC §3.5), source chips, actions.
- [ ] **Streaming:** incremental markdown render (≤ every 120 ms) with a caret. No plain-to-markdown jump at the end.
- [ ] **Live run:** consume `event` frames to build the expanded steps list with running and pending rows; live elapsed counter; budget readout next to Stop; history-row spinner; readiness "1 run active".
- [ ] **Side panel** replaces `.inspector` / `renderRunInspector()` / `openSource()`-in-inspector:
  - Evidence tab (cards, uncited list, trust note, Copy citation).
  - Steps tab (full list + Budget card).
  - Tabs, Esc, focus return.
- [ ] Desktop grid column at ≥1280; drawer below that; **phone bottom sheet** with prev/next (`09`).
- [ ] Saved chats (`loadChat`) render with the same component. Missing `at_ms` or markers degrade as specified.

**Done when:**

- The Agentic, Fixed, Supervisor and Direct answers each show the right badge.
- Pills open the right passage.
- Steps show durations (B1).
- A live agent run fills the timeline step by step (B3).
- Old chats still render.
- Screenshots match `01`–`04` and `09`.

---

## Phase 4: Library screens

References: `06`, `14` (Models), `07`, `13` (Sources).

- [ ] **Models** (SPEC §9):
  - Active pair card.
  - Installed table from `installedChatModels` + `evaluation.groups` (fixed_rag): memory and time meters, failure and speed notes, In use / Use.
  - Mode timing card (hidden if fewer than 2 workflows).
  - Connections card, with the Advanced connection forms moved into a dialog.
  - Optional **B7** for the "of 64 GB" meter.
- [ ] **Sources** (SPEC §10):
  - Header with search and Add source, drop strip (with the OCR option popover and inline progress), filter chips, table.
  - Preview panel with outline, highlighted cited range (from `start_char`/`end_char` when opened via a citation), details, and actions.
  - Remove the old dropzone layout.
- [ ] **Tools & agents** restyle (SPEC §12): tabs + ruled table, tags, status labels.
- [ ] **Dialogs, toasts and popovers** restyle (SPEC §12).
- [ ] Optional: ⌘K command palette, "Rerun with another model", **B6**, **B8** (sentence-level highlights), **B9**.

**Done when** screenshots match `06`, `07`, `13` and `14`, and all Models and Sources actions still work (probe, configure, contract check, discover, select model, ingest, open source).

---

## Phase 5: QA and polish

- [ ] Run the full `QA-CHECKLIST.md`: visual, accessibility, keyboard, reduced motion, phone Safari (PWA standalone), light and dark.
- [ ] Remove dead CSS left over from v1 (`.topbar`, `.runtime-strip`, `.chat-header`, `.workflow-control`, `.corpus-notice`, `.inspector`, `.readiness-ring`, `.mobile-*` that no longer apply). Delete unused IDs from `app.js`.
- [ ] Update `README.md` screenshots and the "Open the workbench" section if the UI changed meaningfully.
- [ ] Bump the asset cache-busting query strings in `index.html` (`?v=`).

---

## Suggested commit and PR slicing

One PR per phase. Phase 3 can split into 3a (backend B1–B4 + tests) and 3b (front end). Each PR description should include before/after screenshots at 1440×900 dark and 390×844 light.
