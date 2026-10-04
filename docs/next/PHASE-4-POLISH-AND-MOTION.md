# Phase 4: polish and motion

**For:** Codex · **Depends on:** Phase 3 closed (`66a8c6b`) · **Reads with:** `DESIGN-AND-NAMING-REVIEW.md` (evidence), `QA-REQUIREMENTS.md` (gates)

This phase changes how Workbench looks and moves. C1 explicitly changes send timing and draft rollback; test rejection, chat switching and newly typed drafts before accepting that change. No endpoint, schema, prompt, model call or database table is added or altered.

**Review decisions — 4 October 2026:** Jake authorized proceeding after the roadmap review. Use Atelier and the two J2 display labels in 4D; preserve internal Workbench identifiers and compact numbered citations. J5 is accepted for this phase. Future phases, dependencies and runtime additions require their own approvals.

Four checkpoints. **Stop for review after 4B and after 4D.**

| Checkpoint | What | Visible change |
|---|---|---|
| 4A | Guardrails and structure | None |
| 4B | Motion foundation: tokens, overlays, reduced motion | Dialogs, menus, sheets and popovers animate |
| 4C | Conversation motion | Sending, waiting, streaming, thinking, searching |
| 4D | Visual fixes, copy, icon, optional rename | The V and N items from the review |

---

## 1. Decisions Jake makes before or during this phase

Record each answer in `AGENTS.md` as a dated user amendment, the same way earlier amendments were recorded.

| ID | Decision | Default if unanswered |
|---|---|---|
| J1 | Product name: Atelier, Cobalt, another, or keep Workbench | Keep Workbench; skip 4D.7 and 4D.8 |
| J2 | Rename "Chat settings" to "Chat controls" and Settings › "Search" to "Web search" | Do not rename |
| J5 | Allow large surfaces to animate for up to 320 ms (changes §G1 rule 4) | Accepted with the reviewed Phase 4 plan on 4 October; no retrospective assumed approval |

## 2. Amendments

Add these verbatim, then follow them.

**`docs/SPEC.md` §G1, replace rule 4 with:**

> 4. Motion is functional and brief. Small elements (hover, press, menus, popovers, tooltips, dialogs, reveals) take at most 200 ms. Large surfaces (sheets, drawers, the sidebar, the side panel) take at most 320 ms. Only activity indicators loop. Animate `opacity` and `transform`; exceptions are collapsible height, sidebar width and the context ring’s stroke-dasharray. Every animation and transition is removed under `prefers-reduced-motion: reduce` and under Appearance › Reduce motion › Always.

**`docs/SPEC.md` §G2, add after the motion tokens:** the token block in §4.1 below.

**`docs/SPEC.md` §G4, add:** "All motion lives in `web/src/styles/motion.css`, selected by `data-slot`, `data-state` and `data-*` attributes. Components do not carry animation utility classes."

**`AGENTS.md`, append:**

> **User amendment (Phase 4, October 2026):** motion per `docs/next/PHASE-4-POLISH-AND-MOTION.md`. CSS-first: no JavaScript animation library, no `tw-animate-css`. All keyframes and transitions live in `web/src/styles/motion.css`; `make check` runs `scripts/check_motion.py`. Phase 4 adds no endpoints, tables, prompts, model calls or dependencies.

## 3. Checkpoint 4A: guardrails and structure

Purpose: make it hard to break anything in 4B to 4D, and make `/design` trustworthy. **No pixel changes.** A before/after screenshot diff of the twelve review screens must be empty apart from anti-aliasing.

| Step | Work | Why |
|---|---|---|
| 4A.1 | **Baseline.** Before touching code, run `make check`, `make e2e`, `make build`, `python scripts/measure_bundle.py`, and save outputs to `artifacts/phase-4/baseline/`. Capture the twelve review screens (§8.3). | Every later gate compares against this. |
| 4A.2 | **Pin dependencies.** In `web/package.json`, replace every `"latest"` with a caret range on the version currently in `package-lock.json`. Update only root range metadata in the lockfile; every resolved version and integrity remains identical. `npm ci` must then leave it unchanged. Caret ranges permit compatible updates; the lockfile pins installed versions. | Today an `npm install` for any reason can jump majors of Streamdown, Vite, TypeScript, ESLint, Sonner or Vaul. |
| 4A.3 | **`settle(page)` helper** in a new `web/tests/helpers.ts`: waits until `document.getAnimations()` contains no running finite animation (cap 1 s). Call it before every axe scan and every screenshot. | Phase T already hit a contrast failure from a mid-fade screenshot. Phase 4 adds many more fades. |
| 4A.4 | **`scripts/check_motion.py`**, wired into `make check`. It fails when `web/src` contains (a) any `tw-animate` utility: `animate-in`, `animate-out`, `fade-in-N`, `fade-out-N`, `zoom-in-N`, `zoom-out-N`, `slide-in-from-*`, `slide-out-to-*`; (b) `transition-all`; (c) an `@keyframes` outside `styles/motion.css`, `styles/globals.css` (until 4B moves them) or a vendored stylesheet; (d) a keyframe defined in `motion.css` and never referenced. At 4A it runs in report-only mode and lists the current violations; 4B flips it to enforcing. | The dead classes went unnoticed for three phases. |
| 4A.5 | **`/design` renders production components.** Export `MessageRow` from `LiveThread.tsx`. Replace the fixture-only `AssistantMessage`, `UserMessage`, `Thread`, `ReasoningBlock` and `ChatSettingsPanel` on `/design` with the production components fed by typed fixture objects (`Message`, `Source`, `Model`). Then delete the fixture-only files. Keep every state §G4.6 lists. `AppShell.tsx` and `TopBar.tsx` remain only as the frame for the `/design` route. Also remove the fixture branches that live inside production components and ship in the bundle today: `Composer.tsx` (`attached`, the "notes.md · fixture" chip, "Message fake-chat", "6.2K of 16K tokens · fixture"), `ModelPicker.tsx` (the hard-coded `fake-*` list and "Fixture models only…"), `SettingsDialog.tsx` (the "foundation preview" panes). `/design` passes fixture data through the same props production uses. | Review finding V1. From here on, what `/design` shows is what ships. |
| 4A.6 | **Split `LiveAppShell.tsx`** (1,124 lines; 15 `useState` calls, 8 refs, 8 queries). Pure moves into: `hooks/useSend.ts` (send, regenerate, stop), `hooks/useUploads.ts`, `hooks/useModelOps.ts` (load, eject, change), `hooks/useShortcuts.ts`, `components/app/ChatMenu.tsx`, `components/app/HistoryList.tsx`, `components/app/EmptyState.tsx`, `components/app/Panels.tsx`. No logic edits, no renamed props, no new state library. | Phases 5 to 8 each add state here. It is the single largest regression risk in the web app. |
| 4A.7 | Housekeeping: add `.DS_Store` to `.gitignore` and remove the tracked one; one source for the audio extension list (the server already reports `audio_extensions`; the web currently repeats the list in `Composer.tsx` and `LiveAppShell.tsx`). | |

Keep 4A.5 and 4A.6 in separate checkpoints and commits, with a full test run between them.

**Abort rule for 4A.6.** If one complete `make e2e` run is not green after the split, revert 4A.6 in full, say so in the report, and continue with 4B on the unsplit file. Do not patch tests to make a refactor pass.

**4A is done when:** all Phase 3 tests pass in a single run with counts at or above baseline; the screenshot diff is empty; initial JS is within ±2 KB of baseline; `check_motion.py` prints the violation list.

## 4. Checkpoint 4B: motion foundation

### 4.1 Tokens (add to `:root` in `globals.css`; identical in both themes)

```css
/* Motion */
--dur-instant: 80ms;   /* press feedback */
--dur-fast: 120ms;     /* existing: hover, color, small fades, exits */
--dur-med: 200ms;      /* existing: popovers, menus, dialogs, reveals */
--dur-slow: 320ms;     /* sheets, drawers, sidebar, side panel */
--ease: cubic-bezier(0.2, 0.8, 0.2, 1);        /* existing: standard */
--ease-out: cubic-bezier(0.16, 1, 0.3, 1);     /* entrances */
--ease-in: cubic-bezier(0.4, 0, 1, 1);         /* exits */
--ease-sheet: cubic-bezier(0.32, 0.72, 0, 1);  /* large surfaces */
--ease-pop: cubic-bezier(0.34, 1.4, 0.64, 1);  /* tiny confirmations only */
--shift-sm: 4px;
--shift-md: 8px;
```

Also add two non-motion tokens used in 4D: `--overlay` per theme (light `rgb(29 28 26 / 0.32)`, dark `rgb(0 0 0 / 0.55)`) and `--shadow-lg` (light `0 2px 6px rgb(20 20 18 / 0.06), 0 16px 48px rgb(20 20 18 / 0.14)`; dark `0 2px 6px rgb(0 0 0 / 0.4), 0 20px 56px rgb(0 0 0 / 0.5)`).

### 4.2 `web/src/styles/motion.css`

Create it, import it in `main.tsx` after `globals.css`, and move the existing motion rules into it (`breathe`, `workbench-reveal`, the button press rule, the overlay duration block at `globals.css` 629–641, both reduced-motion blocks).

House rules, enforced by review and by `check_motion.py`:

1. Selectors are `[data-slot=…]`, `[data-state=…]`, `[data-side=…]` or a small set of `data-*` flags set by components (`data-fresh`, `data-live`, `data-scrolled`). No animation classes in TSX.
2. Keyframes animate `opacity` and `transform` only. Exceptions: `height` for collapsibles (via `--radix-collapsible-content-height`), `width` for the desktop sidebar, `stroke-dasharray` for the context ring.
3. Keyframes use `transform`, never the individual `translate`/`scale` properties. Dialogs are centered with Tailwind's `translate` utilities and the phone Settings dialog sets `translate: none`; animating `transform` composes with both.
4. Exits are shorter than entrances (`--dur-fast` against `--dur-med`; 240 ms against `--dur-slow`) and use `--ease-in`.
5. An element is interactive from its first frame. Never set `pointer-events: none` during an entrance.
6. `will-change` is not set statically anywhere.

### 4.3 Remove the dead classes

Delete every `tw-animate` utility and every `duration-*`/`ease-*` utility that only served them from `components/ui/*.tsx`. Keep Radix `origin-(--radix-…-transform-origin)` classes. Replace `transition-all` in `button.tsx` and `tabs.tsx` with nothing; `motion.css` owns the property list. Flip `check_motion.py` to enforcing.

### 4.4 Overlay choreography

Radix keeps a closing element mounted until its `animationend` fires, so each overlay needs an animation on `[data-state="closed"]`, not only on open.

| ID | Surface (`data-slot`) | Enter | Exit |
|---|---|---|---|
| M1 | `popover-content` (including the citation card), `dropdown-menu-content`, `dropdown-menu-sub-content`, `select-content` | opacity 0→1, scale 0.97→1, 4 px slide away from the trigger (`data-side`), origin from the Radix variable; `--dur-med`, `--ease-out` | opacity→0, scale→0.98; `--dur-fast`, `--ease-in` |
| M2 | `tooltip-content` | opacity 0→1, 2 px slide; `--dur-fast` | opacity→0; `--dur-instant` |
| M3 | `dialog-overlay`, `alert-dialog-overlay`, `sheet-overlay` | opacity 0→1; `--dur-med` | opacity→0; `--dur-fast` |
| M4 | `dialog-content`, `alert-dialog-content` (Settings on desktop, palette, confirmations, chat actions, downloads) | opacity 0→1, `translateY(8px) scale(0.98)`→none; `--dur-med`, `--ease-out` | opacity→0, `scale(0.98)`; `--dur-fast`, `--ease-in` |
| M5 | `.settings-dialog` below 640 px (full screen) | opacity 0→1, `translateY(16px)`→none; `--dur-slow`, `--ease-sheet` | opacity→0, `translateY(16px)`; 240 ms |
| M6 | `sheet-content` by `data-side` (sidebar on tablet and phone, Sources, Chat settings on tablet, transcript) | `translateX(±100%)`→none; `--dur-slow`, `--ease-sheet` | reverse; 240 ms, `--ease-in` |
| M7 | `drawer-content` (Vaul) | Keep Vaul's own transform and drag physics. Change the current 200 ms override to `--dur-slow` with `--ease-sheet`. Do not add keyframes: they would fight the drag. | same |
| M8 | Sonner toasts | Leave as they are. | |
| M9 | `.settings-pane` on section change | existing `workbench-reveal`, unchanged | none |

Command palette specifics: results must not re-animate on each keystroke; only the dialog animates.

### 4.5 Reduced motion

One block at the end of `motion.css` covers both triggers (`@media (prefers-reduced-motion: reduce)` and `[data-reduce-motion="always"]`). Keep the existing universal kill-switch and add:

- `::view-transition-group(*)`, `::view-transition-old(*)`, `::view-transition-new(*)`: `animation: none !important`.
- `[data-sd-animate]`, `[data-sd-animate-marker]::marker` (Streamdown): `animation: none !important`.
- The `html` element itself (the current `[data-reduce-motion="always"] *` selector does not match it).

Under reduced motion, looping indicators become static: three dots at full opacity, the caret solid, the skeleton flat, no shimmer. With `animation: none`, Radix unmounts closing overlays immediately; that is the intended behavior.

In React, read reduced motion once (`useReducedMotion()`: media query OR the `reduceMotion` store value) and use it to pass `animated={false}` to Streamdown and to skip `startViewTransition`. CSS alone is not enough for those two.

**4B is done when:** P4-AC1 to P4-AC6 in §9 pass. **Stop for review.** Jake should try the preview on the phone at this point; the feel of M4, M6 and M7 is easier to judge by hand than in a report.

## 5. Checkpoint 4C: conversation motion

| ID | Moment | Behavior | Files |
|---|---|---|---|
| C1 | **A message you just sent** | In an existing chat, the text appears as a user bubble at the end of the thread within one frame of Send, with the waiting indicator (C3) beneath it. The bubble rises 8 px and fades in (`--dur-med`, `--ease-out`). The composer clears at the same moment. If the server rejects the send, remove the bubble, put the text back in the composer unless the user has typed something new, and show the existing `sendError`. Replace the gray `{pending && <p…>}` paragraph. In a new chat, keep today's behavior (the empty state gives way to the thread when the server confirms) and apply the same entrance to the first bubble. | `Composer.tsx` (`send`), `LiveAppShell.tsx` or `useSend.ts`, `LiveThread.tsx` |
| C2 | **Fresh rows only** | Entrance animations apply to rows created by this session's send, edit or regenerate, flagged `data-fresh="true"`. Rows loaded from history, branch switches and reloads never animate. Clear the flag on `animationend` (or after 400 ms): finished rows use `content-visibility: auto`, and a flag left in place can replay the animation when a row scrolls back into view. The real row that replaces an optimistic bubble must not animate a second time. | `LiveThread.tsx` |
| C3 | **Waiting for the model** | Three dots, 6 px, `--text-3`, opacity wave 0.3→1 with 160 ms stagger, 1.2 s loop. `role="status"` with visually hidden text "Generating response". Queued and loading-model states keep their text ("Waiting for {model}… (#2 in line)", "Loading {model}… 8 s") with the existing spinner. | `LiveThread.tsx` |
| C4 | **Streaming text** | Enable Streamdown's built-in animation: `animated={{ animation: "fadeIn", duration: 200, easing: "ease-out", sep: "word" }}` and `caret="block"`, both only while `streaming` and only when motion is allowed; import `streamdown/styles.css` inside the lazy `Markdown` chunk. Streamdown draws the caret as an `::after` on the last block, with its glyph in `--streamdown-caret`; give it `--text-3` and a 1 s blink in `motion.css`. After completion the row renders with `animated={false}` and no caret. | `Markdown.tsx`, `motion.css` |
| C5 | **Thinking** | Collapsible content animates height with `--radix-collapsible-content-height` (`--dur-med`); chevron rotates 180° (`--dur-fast`). While live, the label "Thinking… 12s" carries a slow text shimmer (1.6 s). When the first answer token arrives the block collapses with the same animation rather than snapping. | `LiveThread.tsx` (`Thinking`), `collapsible.tsx` |
| C6 | **Searching the web** | Replace `<details>` with the Radix `Collapsible` in `SearchActivity` and in "What the model saw" (`SourcesSheet`). Steps enter one by one (4 px rise, `--dur-fast`); favicons pop in with 40 ms stagger (`scale(0.8)`→1, `--ease-pop`); the live label shimmers like C5; on completion it collapses to the summary row with a height animation. Keep `data-testid="search-activity"` and the existing 300 ms time-to-visible budget. | `SearchActivity.tsx`, `SourcesSheet.tsx` |
| C7 | **Copy** | The Copy icon becomes a check for 1.5 s (`scale(0.8)`→1, `--ease-pop`), with `aria-live="polite"` text "Copied". No toast. Applies to message copy, code copy and transcript copy. | `MessageActions.tsx`, `Markdown.tsx`, `TranscriptSheet.tsx` |
| C8 | **Scroll to bottom** | The button stays mounted; `data-state` toggles opacity and an 8 px slide (`--dur-fast`). When hidden it is `inert`. | `LiveAppShell.tsx` |
| C9 | **Composer** | Border and focus ring transition (`--dur-fast`). Send becomes enabled with a color transition. Send and Stop swap with a `scale(0.8)`→1 cross-fade. Attachment and recording chips enter with `scale(0.96)`→1 and fade; upload percent drives a 2 px progress bar with a 120 ms linear width transition; a transcribing chip shows the same shimmer as C5. The context ring animates `stroke-dasharray` (`--dur-med`). | `Composer.tsx`, `AudioChip.tsx` |
| C10 | **Sidebar** | Rows: background transition `--dur-fast`. Current row: the 2 px brand bar scales in from the center (`--dur-med`). A chat with an active run shows a 6 px pulsing dot (§G4.2 specifies it; it is not implemented). An auto-generated title cross-fades in when `chat.title` arrives. Desktop collapse: `width` transitions over 240 ms with `--ease-sheet`, **only if** P4-AC9 holds; otherwise width snaps and the labels fade. | `ChatList.tsx`, `Sidebar.tsx`, `motion.css` |
| C11 | **Model status** | When a model changes from not loaded to loaded, its dot scales 1→1.35→1 once (200 ms). Never on first paint and never from a cached value: status stays truthful. | `ModelPicker.tsx` |
| C12 | **Empty state** | On first paint of a new chat: greeting, then composer, then chips, each fading in with an 8 px rise, 60 ms apart (`--dur-med`). Once per page load, not on every return to `/`. | `EmptyState` |
| C13 | **Theme change** | Wrap the theme switch in `document.startViewTransition` when it exists and motion is allowed, giving a 200 ms root cross-fade. Otherwise switch instantly. No shared-element transitions anywhere in this phase. | `ThemeProvider.tsx` |
| C14 | **Thread edges** | Top bar gains a hairline when the thread is scrolled (`data-scrolled`, `--dur-fast`), per §G4.4. A 24 px gradient from `--bg` to transparent sits above the composer row so text fades out instead of being cut. | `LiveAppShell.tsx`, `globals.css` |
| C15 | **Side panel (≥ 1280 px)** | Chat settings slides in 16 px and fades (`--dur-med`). The thread width change is not animated. | `LiveAppShell.tsx` |

Notes that will save time:

- **C1 and remounts.** The composer is rendered in two different parents (empty state, thread). React remounts it when the parent changes, which resets its draft text. That is why C1 keeps today's timing for new chats. If you want the optimistic bubble there too, lift the draft into the shell first, and say so in the report.
- **C4 and performance.** Word animation adds one span per word while streaming. `performance.spec.ts` (≤ 8 ms per frame at 100 tokens per second, only the streaming row renders) must pass unchanged with animation on. If it does not, ship the caret without the word fade and report the measurement. Do not raise the budget.
- **C4 and citations.** The citation renderer reads `node.position` from the Markdown AST. Verify a citation pill renders correctly mid-stream with animation on (`web.spec.ts`).
- **C6 and `<details>`.** Tests that query `summary` or `details` need new selectors. List each in the test-diff ledger (QA §4).

## 6. Checkpoint 4D: visual fixes, copy, icon, name

Each row closes a review finding. "Spec" means the target is already written in `docs/SPEC.md` Part G; implement it as written.

| Step | Closes | Target |
|---|---|---|
| 4D.1 | V2, V3 | **User message.** Bubble: `--user-bubble`, `--radius-lg`, no border, 15/23, padding 10/14, max 85% (spec G4.5). Actions right-aligned directly under the bubble; on fine pointers they appear on hover or focus-within, on touch they are always visible. Edit mode: full-width textarea, "Cancel" and "Send". |
| 4D.2 | V4 | **Assistant footer.** One row: actions left, stats right (spec G4.6). On fine pointers the stats line appears on hover or focus-within of the message; actions stay visible on the last message and appear on hover for earlier ones. Always visible on touch. Message info: a fixed, formatted list (see review §5.2). |
| 4D.3 | V5, V9 | **Search activity and citations.** Collapsed activity is a borderless single row: favicon stack, "Searched the web · 5 sources · 3.1 s", chevron (spec G4.8). Expanded steps are humanized. Citation pills retain compact source numbers plus `+N`, per the 3 October user correction; domain, title and passage remain in the card. `aria-label` remains descriptive. Source card and sheet passages in Newsreader 14/21 and 15/23 (spec). |
| 4D.4 | V6 | **Code and tables.** One surface each. Code: `--code-bg`, `--radius-md`, a header strip with the language label and Copy, body below, no inner border, no line-highlight strip. Tables: one rounded wrapper with a hairline, header row on `--surface-2`, horizontal scroll inside with a fade at the edge (spec G3, G4.6). Target the `data-streamdown` attributes; do not fork Streamdown. |
| 4D.5 | V7, V8 | **Sidebar.** One search control: a quiet field (`--surface-2` fill, no border, search icon, "⌘K" hint at the right) that filters the list as it does today and keeps `aria-label="Search history"`; ⌘K still opens the palette. Remove the separate ghost row when expanded; keep the icon button on the collapsed rail. Rows 36 px on fine pointers, 44 px on touch (spec G4.2). |
| 4D.6 | V10 to V19, V21 to V23 | **Remaining items.** V10: when "Model default" is on, hide the number field and show "Model default" as muted text; group as System prompt · Sampling · Length and context · Reasoning (spec G4.12). V11: one focus style everywhere: the global 2 px brand outline (offset 2 px, inset in lists); remove shadcn's `focus-visible:ring-*` and `focus-visible:border-ring` utilities. V12: palette is input-first; title and description become `sr-only`; close button only on coarse pointers; shortcut hints at the right of each action. V13: one segmented-control style for Theme, Answer font and Text size (selected: `--brand-soft` fill, `--brand` text). V14: Load and Eject are ghost buttons shown on hover or focus (always on touch); footer is "Manage models…"; trigger shows the connection name. V15: no raw exception text (review §5.2). V16: `--overlay` and `--shadow-lg` tokens from §4.1; dialogs and popovers use `--radius-lg`, menus `--radius-md`. V17: title centered, double-click to rename inline, hidden on phones. V18: Delete uses `--danger` and sits after a separator. V19: `ThemeProvider` updates both `theme-color` meta tags to the resolved theme's `--bg`. V21: skeleton rows replace "Loading chats…" and "Loading formatted answer…". V22: web toggle is a labeled pill at ≥ 640 px (spec G4.9). V23: drop overlay is a dashed `--brand` outline over a translucent `--bg`. |
| 4D.7 | N-table, J1, J2 | **Copy.** Apply every row of review §5.2 that does not depend on J2. Apply the two J2 renames only if Jake said yes. If J1 names a new product name: change `shared/config.json` `APP_NAME`, `web/index.html` (title and `apple-mobile-web-app-title`), `web/public/manifest.webmanifest` (`name`, `short_name`), and replace every hard-coded "Workbench" in `web/src` with `config.APP_NAME` (twelve occurrences across `SettingsDialog`, `LiveSettings`, `LegacyImportDialog`, `TranscriptionSettings`, `ChatActionDialog`, `RecordingDownloadDialog`, `LiveAppShell`, `router`). **Do not** change the launchd label, the `WORKBENCH_` prefix, data paths, `workbench.db`, the `workbench-shell-` cache prefix, the `workbench-theme` key, `workbench:*` events or the fetcher's User-Agent. |
| 4D.8 | V20, J1 | **Icon.** One mark, five files: `mark.svg` (`currentColor`), `icon-192.png`, `icon-512.png`, `maskable-512.png` (mark inside the central 80%), `apple-touch-icon.png` (180 px). Cobalt tile `#2f5bea`, paper glyph `#faf9f6`. For Atelier, start from the concept below (an easel-shaped A); for another name, draw its initial with two or three round-capped strokes in the same weight. Show Jake the 512 px render before committing. |

```svg
<!-- Concept for "Atelier"; adjust freely. -->
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <rect width="512" height="512" rx="112" fill="#2f5bea"/>
  <path d="M152 372 256 136l104 236" fill="none" stroke="#faf9f6"
        stroke-width="44" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="256" cy="322" r="26" fill="#faf9f6"/>
</svg>
```

Every state touched in 4C and 4D appears on `/design` using the production component.

## 7. Not in this phase

- Shared-element or layout transitions (the composer gliding from center to bottom, list reordering). They need a motion library and Jake chose the restrained option.
- Any JavaScript animation library, `tw-animate-css`, Lottie, confetti, sound or haptics.
- New colors, fonts, themes or an accent picker.
- Changes to endpoints, schemas, prompts, the search pipeline, run handling or the service worker's caching rules.
- VoiceOver repair. It stays a recorded limitation (AGENTS amendment of 3 October). Phase 4 must not make it worse: no new focus traps, no content moved out of the accessibility tree.

## 8. Tests and evidence

### 8.1 New: `web/tests/motion.spec.ts` (Chromium and WebKit)

1. **Overlays animate in and out.** For Settings, palette, model picker, message info, chat menu, the Reduce motion select, Sources (1440), sidebar sheet (768) and a tooltip: immediately after opening, `getComputedStyle(el).animationName` is not `none`; after closing, the element is still attached on the next frame and detached within 400 ms.
2. **Reduced motion, both triggers.** With `reducedMotion: "reduce"`, and separately with `appearance.reduce_motion = "always"`: for every selector in §4.4 and §5, `animationName === "none"` and `transitionDuration === "0s"`; closing overlays detach within one frame; no caret blink; Streamdown renders without `data-sd-animate`.
3. **Fresh rows only.** A sent message's row has `data-fresh` and an animation; after reload the same row has neither. Scroll a fresh row out of view and back: no animation replays.
4. **Send feels immediate (C1).** With the fake runtime delayed 500 ms on `POST /messages`: the bubble is visible and the composer empty within 100 ms; on a forced 422 the bubble disappears and the composer holds the original text.
5. **No layout shift.** During a fresh assistant row's entrance, the thread stays pinned: `scrollHeight - clientHeight - scrollTop < 80` on every frame.
6. **Caret.** Present while streaming, absent afterwards.
7. **Copy feedback (C7).** The check icon appears, the polite live region says "Copied", no toast element is created.

### 8.2 Existing suites

All must pass unchanged in a single run, with motion on. `performance.spec.ts`, the two frame-trace tests in `chat.spec.ts`, and the 300 ms search-activity test keep their thresholds. Axe scans and screenshots call `settle()` first.

### 8.3 Evidence under `artifacts/phase-4/`

- `baseline/` and `final/`: `check.txt`, `e2e.txt`, `bundle.json`, and the twelve review screens at 390 and 1440 px, light and dark: new chat, active chat, web chat, reasoning chat, model picker, chat settings, Settings › Appearance, Settings › Models, command palette, Sources, sidebar drawer (390 only), transcript states.
- `motion/*.webm`: eight short Playwright recordings with synthetic data: open and close Settings; model picker; phone sidebar; send and stream with reasoning; web search answer; copy; theme switch; the same send under reduced motion. Add `artifacts/phase-*/motion/` to `.gitignore`; the repository is already 279 MB. The report lists the files.
- `test-diff-ledger.md` (QA §4).

## 9. Acceptance criteria

Each needs a test name or a file under `artifacts/phase-4/` in the report.

| ID | Criterion |
|---|---|
| P4-AC1 | 4A complete: single green run of `make check` and `make e2e`; test counts ≥ baseline; screenshot diff empty; dependency ranges constrained without any resolved version or integrity change. |
| P4-AC2 | `web/src` contains no `tw-animate` utilities and no `transition-all`; `check_motion.py` enforces this inside `make check`. |
| P4-AC3 | Every overlay in §4.4 has an enter and an exit animation using the §4.1 tokens (motion.spec 1). |
| P4-AC4 | Both reduced-motion triggers remove every animation and transition (motion.spec 2). |
| P4-AC5 | No keyframe animates a property outside the rule 2 list in §4.2 (`check_motion.py` plus review). |
| P4-AC6 | Initial JS ≤ 250 KiB gzip and no more than 8 KiB above the 4A baseline. No new entry in `dependencies` or `devDependencies`. |
| P4-AC7 | C1 to C15 implemented; motion.spec 3 to 7 pass. |
| P4-AC8 | Streaming with C4 on: `performance.spec.ts` passes at the existing thresholds in Chromium and WebKit. If not, the word fade is off, the caret is on, and the numbers are in the report. |
| P4-AC9 | Sidebar width animation: on the 300-message fixture, p95 frame time ≤ 18 ms during collapse and expand. If not, width snaps. |
| P4-AC10 | Each V item in §6 is closed, with a before and after screenshot. |
| P4-AC11 | `/design` renders production components only; the five fixture-only files named in 4A.5 are deleted. |
| P4-AC12 | Axe: zero serious or critical violations on every screen, both themes, after `settle()`. `scripts/check_contrast.py` passes, extended to cover any new token that carries text. |
| P4-AC13 | Deployment invariants unchanged: `127.0.0.1:8787`, launchd label, Tailscale route, `/design` returns 404 in production, service worker never caches `/api`. |
| P4-AC14 | No file under `server/app` changes. A rename under J1 needs none: the server reads the name from `shared/config.json`. The API-type step of `make check` reports no drift. |
| P4-AC15 | Jake's phone check (QA §7) after 4B and after 4D. |

Report as `docs/PHASE-4-REPORT.md` using the §H4 template plus the additions in QA §8.
