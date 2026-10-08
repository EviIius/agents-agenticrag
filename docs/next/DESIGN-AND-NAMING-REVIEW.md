# Workbench: theme, design and naming review

**Date:** 3 October 2026 · **Commit reviewed:** `66a8c6b` (Phase 3 closed) · **Author:** Claude (validator)

**What I looked at.** Every file under `web/src`, the built CSS in `server/app/static/assets`, `docs/SPEC.md` Part G, and the synthetic screenshots in `artifacts/phase-3/regression/` and `artifacts/phase-t/` at 390 and 1440 px in both themes.

**What I did not look at.** The running app, your phone, or any real chat. Stills cannot show motion, so every motion finding below comes from the code and the compiled CSS, not from watching the app.

---

## 1. Verdict

The theme is right. Keep it. Warm paper, one cobalt accent and serif answers give the app a calm, distinct look, and none of the fixes below change a color or a font.

Three things stop it from feeling premium:

1. **Almost nothing moves, and that is a bug rather than a choice.** The shadcn components carry enter and exit animation classes that compile to no CSS at all (finding F1). Dialogs, menus, popovers, sheets and tooltips appear and vanish in a single frame.
2. **The production message row drifted from the spec.** `/design` renders spec-faithful lookalike components; the real thread uses a different one. Alignment, borders and density differ (V1 to V4).
3. **Small things sit in heavy boxes, and a few labels read like developer output.** Search activity, thinking, code blocks and tables are each wrapped in one border too many (V5 to V8); copy such as "Waiting for first token…" and raw `TypeError` strings reach the screen (N-table, V15).

The fixes are specified in `PHASE-4-POLISH-AND-MOTION.md`. This document is the evidence and the reasoning.

## 2. What should not change

Codex should treat these as locked so that "polish" does not turn into redesign:

- Every color token in `globals.css` (§G2). Two additions are proposed (a warmer overlay, a dialog shadow); nothing existing changes value.
- Geist for UI, Newsreader for answers, Geist Mono for code, and the §G3 type scale.
- Thread width 768 px, composer shape (22 px radius, soft shadow, brand-soft focus ring), sidebar structure, Settings information architecture.
- The greeting, the suggestion chips and the tagline "Your models. Your Mac."
- Composer outside the scrolling thread; 44 px touch targets; safe-area handling.

## 3. Motion findings

| ID | Severity | Finding | Evidence |
|---|---|---|---|
| F1 | **High** | **Overlay animations are dead code.** `components/ui/{dialog,alert-dialog,popover,dropdown-menu,select,sheet,tooltip,drawer}.tsx` use `animate-in`, `fade-in-0`, `zoom-in-95`, `slide-in-from-*`, `animate-out` and friends. Those utilities come from `tw-animate-css`, which is not installed and not imported. Tailwind v4 emits nothing for them. | `web/package.json` has no such package; `globals.css` line 1 imports only `tailwindcss`; the built `index-*.css` contains exactly four keyframes: `breathe`, `pulse`, `spin`, `workbench-reveal`, and zero occurrences of `animate-in`. `globals.css` lines 629–641 set `animation-duration` on overlays that have no animation. |
| F2 | **High** | **Nothing announces a new message.** No entrance for the user bubble or the assistant row, no streaming caret, no per-word fade. Text appears in frame-sized jumps. | `LiveThread.tsx` `MessageRow`; `Markdown.tsx` passes `isAnimating` but not `animated` or `caret`, both of which Streamdown 2.7.0 (installed) supports. §G4.6 specifies a soft caret. |
| F3 | Medium | **The waiting state is a spinner with developer wording.** `LoaderCircle` plus "Waiting for first token…". §G4.6 specifies a three-dot pulse. | `LiveThread.tsx` lines 359–376. |
| F4 | Medium | **A sent message first appears as a gray paragraph above the composer**, then jumps into the thread as a bubble when the server answers. | `LiveAppShell.tsx` line 994: `{pending && <p className="mx-6 text-sm text-fg-2">…`. |
| F5 | Medium | **Thinking and Search activity open and close instantly.** Thinking uses Radix `Collapsible` with no height animation; Search activity and "What the model saw" use native `<details>`, which cannot animate closed in Safari. | `LiveThread.tsx` `Thinking`; `SearchActivity.tsx`; `SourcesSheet.tsx`. |
| F6 | Low | **Layout changes pop.** Sidebar collapse, the right-hand chat panel, the scroll-to-bottom button and the drop overlay all mount and unmount with no transition. | `.sidebar-desktop[data-collapsed]` has no transition; `{ui.panel && wide && <aside …>}`; `{above && <Button …>}`; `{dragging && <div …>}` in `LiveAppShell.tsx`. |
| F7 | Low | **The motion that does exist is inconsistent.** The Settings pane fades in over 200 ms, inside a dialog that itself appears instantly. Vaul drawers and Sonner toasts animate with their own curves; nothing else does. | `.settings-pane, .model-selected-mark { animation: workbench-reveal … }` are the only bespoke animations. |
| F8 | Low | **Every copy action raises a toast.** Premium apps confirm in place (icon becomes a check for 1.5 s). §G4.6 already asks for this on code blocks. | `MessageActions.tsx`: `.then(() => toast("Copied"))`. |

Bundle note for whoever is tempted by a JavaScript motion library: initial JS is 224,491 bytes gzip against a 256,000 budget (`artifacts/phase-3/bundle.json`). There are about 31 KB left. Phase 4 is CSS-first for that reason as much as for taste.

## 4. Visual findings

| ID | Severity | Finding | Evidence | Spec |
|---|---|---|---|---|
| V1 | **High** | **`/design` shows components production does not use.** `AssistantMessage.tsx`, `UserMessage.tsx`, `Thread.tsx`, `AppShell.tsx`, `TopBar.tsx` and `ChatSettingsPanel.tsx` are imported only by the design route. The real thread renders `MessageRow` inside `LiveThread.tsx`. The "every state on /design" rule is being met by lookalikes, so drift is invisible. | Import graph; `router.tsx`. | H3 rule 4 |
| V2 | High | **User message actions sit on the wrong side.** The bubble is right-aligned; its Copy and Edit icons render at the left edge of the column, 64 px below. | `chat-1440-dark-fake-runtime.png`; `MessageRow` renders `MessageActions` after the bubble with no alignment. | G4.5 |
| V3 | Medium | **User bubble uses the wrong tokens.** Production: `rounded-2xl border border-line bg-surface-2 px-4 py-3`. Spec and fixture: `--user-bubble`, `--radius-lg`, no border, 15/23 type, max 85% width. | `LiveThread.tsx` line 330 vs `UserMessage.tsx`. | G4.5 |
| V4 | Medium | **Assistant footer is two stacked rows, always visible.** Stats line, then a row of four 44 px icon buttons. Spec: one footer row, actions left, stats right, revealed on hover on desktop. Every finished answer currently ends with about 90 px of chrome. | `web-chat-1440-light-fake-web.png`. | G4.6 |
| V5 | Medium | **Search activity is a full-width bordered card for one line of text.** Its expanded steps print raw event fields (`read · https://…`). | `SearchActivity.tsx`: `rounded-lg border border-line p-3`, `{s.label} · {s.detail}`. | G4.8 |
| V6 | Medium | **Code blocks and tables are double-boxed.** An outer rounded card holds an inner bordered box; code also shows a darker strip behind the line. | `chat-1440-dark-fake-runtime.png`, `reasoning-chat-1440-light-fake-runtime.png`. | G4.6, G3 |
| V7 | Medium | **Sidebar search appears twice.** A "Search chats ⌘K" row opens the palette; directly under it, a bordered "Search chats…" input filters the list. | `new-chat-1440-light-fake-runtime.png`; `Sidebar.tsx` plus `list` in `LiveAppShell.tsx` line 791. | B2 rule 7 |
| V8 | Medium | **Sidebar rows are 44 px on desktop.** Spec: 36 px with a fine pointer, 44 px on touch. Fourteen chats fill a 1250 px tall window. | `ChatList.tsx`: `min-h-11` unconditionally. | G4.2 |
| V9 | Medium | **Citation pills show a number, not a site.** "1 +1" in a serif sentence reads as arithmetic. Spec and the original "confusing citations" complaint both call for `nba.com +1`. | `CitationPill.tsx`: `{sources[0]!.n}`. | E9, G4.7 |
| V10 | Medium | **Chat settings shows empty disabled boxes.** With "Model default" on, each parameter renders a blank disabled input. It reads as broken. Spec: show the default as "Model default". | `chat-settings-1440-dark-fake-runtime.png`; `LiveChatSettings.tsx`. | G4.12 |
| V11 | Medium | **Two focus systems are active at once.** Global `:focus-visible { outline: 2px solid var(--brand); outline-offset: 3px }` is unlayered, so it beats Tailwind's `outline-none`; shadcn's `focus-visible:ring-[3px]` also applies. Result: thick doubled rings, most visible on the model search field. | `model-picker-1440-light-fake-runtime.png`; `globals.css` line 216; `button.tsx`, `input.tsx`. | G7.5 |
| V12 | Medium | **The command palette opens with a title, a subtitle and a close button above the input.** A palette should be input-first. | `palette-1440-dark-fake.png`; `CommandPalette.tsx`. | — |
| V13 | Low | **Selected state is styled three ways in one pane.** Theme: solid brand. Answer font and Text size: gray fill. Settings nav: brand-soft. | `review-settings-appearance-1440-light.png`; `SettingsDialog.tsx`. | G1 |
| V14 | Low | **Model picker rows carry permanent outlined Eject/Load buttons** and a two-line provenance footer. Spec: actions on hover, "Manage models…" in the footer. The trigger hard-codes the word "Ollama". | `ModelPicker.tsx` lines 104–106, 195–221, 311–320. | G4.3 |
| V15 | Low | **Raw exception text reaches the user.** Nine toasts use `String(e)` as their text; the offline screen prints `TypeError: Load failed`. | `LiveAppShell.tsx` lines 346, 503, 589, 652, 917; `LiveSettings.tsx` 85; `TranscriptionSettings.tsx` 123, 142; `AudioChip.tsx` 133, 139. | G6, C12 |
| V16 | Low | **The scrim is cold and heavy on the light theme.** `--overlay: rgb(0 0 0 / 0.5)` for both themes. | `review-settings-appearance-1440-light.png`. | — |
| V17 | Low | **Top bar title is small gray text at the right, not editable.** Spec: centered, double-click to rename, hairline appears when the thread scrolls. | `LiveAppShell.tsx` line 903; `.topbar` has no border state. | G4.4 |
| V18 | Low | **Destructive menu items look like any other.** "Delete" in the chat menu has no danger color and no separator. | `LiveAppShell.tsx` lines 778–785. | G1 rule 5 |
| V19 | Low | **Phone status bar color follows the system, not the app theme.** `theme-color` is set by media query only. Choosing Dark in the app on a light-mode phone leaves a light status bar. | `web/index.html`; `ThemeProvider.tsx` never updates the meta tag. | G9 |
| V20 | Low | **The app mark is three horizontal bars.** It reads as a menu icon. `icon-512.png` is 1.8 KB. | `web/public/icons/mark.svg`. | — |
| V21 | Low | **Loading states are sentences, not skeletons.** "Loading chats…", "Loading formatted answer…". | `LiveAppShell.tsx`, `LiveThread.tsx`. | G4.2, G4.14 |
| V22 | Low | **The web toggle is an unlabeled globe.** Spec: a pill reading "Search" at ≥ 640 px. Icon-only works on a phone; on desktop it is a guess. | `Composer.tsx` lines 255–274. | G4.9 |
| V23 | Low | **The drop target is an opaque panel with a solid border.** Spec: dashed brand outline over the thread. | `LiveAppShell.tsx` `dragging`. | G4.9 |

## 5. Naming

### 5.1 Product name

`docs/SPEC.md` §B1 says "The name is a placeholder; it lives in one config constant". "Workbench" describes a tool surface. The product has become something you read and think in, with a serif reading face and a greeting. The name should catch up.

Constraints I used: one word, at most eight letters (so the iPhone home-screen label is not truncated), reads well in every sentence the UI already uses ("Welcome to …", "Can't reach …", "What should … call you?"), and not already the name of a known local-model chat app.

| Name | Why it fits | Watch out for |
|---|---|---|
| **Atelier** (recommended) | French for workshop and for studio. It keeps the meaning of Workbench, moves it up-market, and sits naturally beside "LM Studio control" in §G1. Set in Newsreader it looks like a wordmark without any design work. | Seven letters with a silent R; some people will ask how to say it ("at-el-YAY"). The follow-up review found an existing [Atelier AI workspace](https://getatelier.app/) and [Atelier desktop AI assistant](https://github.com/BowgartField/atelier). Suitable for this personal app, but not a distinctive public product name. |
| **Cobalt** | The accent color is already the identity. Short, hard consonants, obvious icon. | Shares a word with unrelated tools (Cobalt Strike, a media downloader). No chat-app collision found. |
| **Alcove** | A private recess for reading. Matches the privacy story and the reading-first surface. | A Mac notch utility uses the name. |
| **Bureau** | A writing desk, and an office that handles errands, which will suit agents later. | Slightly formal; also an identity-verification company. |
| Hearth (considered, not recommended) | Warm, home, always on. | Crowded: an App Store app "Hearth Cmd", "Hearth: An AI Household OS" for Home Assistant, and the Hearth Display family product all use it. |
| Workbench (keep) | Zero work. | Still reads as a placeholder; generic in search and on the home screen. |

**Recommendation: Atelier.** If you want something punchier, Cobalt.

Collision checks were a single web search per name on 3 October 2026, reading result titles only. For a personal app that is enough; it is not a trademark search.

**Renaming is cheap and safe if it is display-only.** Phase 4 step 4D.7 lists the exact strings. Internal identifiers do not change: the launchd label `dev.agenticrag.workbench`, the `WORKBENCH_` environment prefix, `~/.local/share/workbench`, `workbench.db`, the `workbench-shell-` cache name, the `workbench-theme` storage key and the `workbench:*` event names all stay. `AGENTS.md` already forbids touching the first of those. On the phone you delete the old home-screen icon and add it again to pick up the new label.

### 5.2 Labels and copy

Current wording is mostly good: plain, sentence case, no exclamation marks. These are the exceptions.

| Where | Now | Proposed | Why |
|---|---|---|---|
| Waiting state | "Waiting for first token…" | three-dot pulse, no text; `aria-label="Generating response"` | Developer vocabulary (§G6). |
| Queued | "Waiting in line…" | "Waiting for {model}… (#2 in line)" | Spec wording; says what it is waiting for. |
| Edit a message | "Save & submit" | "Send" | Spec wording (§G4.5). |
| Right panel, tooltip, palette action | "Chat settings" | **"Chat controls"** | Two things are called "settings" today (this panel and the app dialog). The palette lists them one above the other. *Your call, J2.* |
| Settings section | "Search" | **"Web search"** | "Search chats" is a different feature. *Your call, J2.* |
| Settings › Models | "Utility model · search queries and titles" | Label "Helper model"; description "Plans web searches and writes chat titles." | Label plus description, not a label with a dot. |
| Model picker footer | "3 models · capabilities reported by Ollama" / "Load selects the model for this chat." | "Manage models…" (opens Settings › Models) | Spec §G4.3. The provenance line is for developers. |
| Model picker trigger | hard-coded "Ollama" | the connection's name | Wrong as soon as a second runtime exists. |
| Attachment menu, disabled items | "Images need a vision model" replaces the label | Keep "Add image"; reason on a second muted line | The action name should not disappear. |
| Web toggle | `aria-label` "Search on" / "Search off" | visible "Search" at ≥ 640 px; `aria-label="Web search"`, `aria-pressed` | A pressed button should not change its name. |
| Search activity steps | "read · https://example.org/page" | "Read example.org" · "Searched: 2021 NBA Finals result" | Humanize; show the site, not the URL. |
| Sources sheet | "Ranking: keyword" · "Plan: 0.08s" grid | one meta line: "via DuckDuckGo · plan 0.1 s · search 1.2 s · read 2.4 s"; ranking moves to Message info | Spec §G4.8. |
| Offline screen | "Can't reach Workbench" + `TypeError: Load failed` | "Can't reach {APP_NAME}" · "Your Mac may be asleep or off the tailnet." · Try again · "Details" disclosure | Say what happened and what to do (§G6). |
| Generic failures | `toast(String(e))` | route through `errorCopy()`; unknown errors read "Something went wrong. Try again." with the detail in the description | No raw exception text. |
| Message info popover | keys shown as `tokens per sec`, `ttft ms`, raw JSON for params | fixed, formatted list: Model · Speed · Tokens · Time to first token · Context used · Parameters sent | §G6 allows parameter names here; it does not ask for raw keys. |
| Command palette | visible title "Command palette" | title for screen readers only; placeholder "Search chats or run a command…" | V12. |
| Future toggles (Phases 7, 8) | — | composer row reads **Search · Library · Think · Research** | One word each, same grammar. |
| Future features (Phase 5) | — | **Presets**, **Folders** | Not "modes", "personas" or "projects". |

"Eject", "Load", "Sources", "What the model saw", "Read, not cited", "Couldn't read", "Recording" and "Transcript" are all good. Keep them.

## 6. Order of work

1. F1, then F2 to F5: this is what you asked for and it is the largest visible gain.
2. V1 first among the visual items, because it decides whether `/design` can be trusted for everything after it.
3. V2 to V12: each is small; together they remove most of the "almost right" feeling.
4. Naming, icon and the remaining Low items last.

`PHASE-4-POLISH-AND-MOTION.md` turns this into checkpoints with acceptance criteria.
