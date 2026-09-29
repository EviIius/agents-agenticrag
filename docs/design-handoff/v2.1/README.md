# Design handoff v2.1: themes, fonts, popups, launch intro, offline

**Status:** approved by Jake on 29 Sep 2026. Claude designed it; Codex implements it.

This builds on the v2 handoff in `docs/design-handoff/` (Graphite & Cobalt), and everything there still applies.

**Where the mockups live.** The interactive mockups are rows 4–6 of the "AgenticRAG Premium UI" design canvas on claude.ai (private to Jake). Everything needed to build is in this folder.

## What Jake decided

1. **Themes:** all four ship (Graphite Dark, Graphite Light, Midnight, Paper), plus System, which follows the device. Also add font choices.
2. **Accent:** Claude's call. It's a setting with Cobalt (default), Amber or Graphite. All 24 theme × accent × contrast combinations pass WCAG AA.
3. **Launch intro:** a setting. It defaults to *Every launch*, with *Only when something's slow* and *Off* as the alternatives.

## Start here

| Read | What it is |
|---|---|
| **CODEX-PROMPT.md** | Copy-paste prompts for Phases A–E. Start with A. |
| **SPEC.md** | What to build:<br>• §1 Appearance settings<br>• §2 popup system<br>• §3 launch intro<br>• §4 offline and degraded states<br>• §5 copy rules |
| **DATA-CONTRACT.md** | Additive backend and asset changes:<br>• health endpoint<br>• runtime-status fields<br>• warm-up<br>• service worker<br>• optional keyword fallback and soft delete |
| **tokens-themes.css** | The new tokens: Midnight, Paper, accents, font and size switches, increased contrast, reduced motion, popup and status tokens. It uses the variable names `tokens.css` already has; merge it in. |
| **components-v21.reference.css** | CSP-safe CSS for Settings, theme cards, the segmented control, switches, dialogs and sheets, tool approval, the agent question, toasts, menus, popovers, the runtime pill and popover, the launch overlay and the offline screen. |
| **QA-CHECKLIST.md** | The v2.1 checks, run together with the v2 checklist. |
| **tools/check_contrast.py** | Verifies every theme × accent × contrast combination. Wire it into pytest. |
| **fonts/** | Literata and Atkinson Hyperlegible Next (variable woff2: Latin, Latin Extended and Italic) with their OFL licences. |
| **reference/screens/** | Target renders (PNG), listed below. |
| **reference/canvas/** | The mockup sources (`.dc.html`), for exact spacing, copy and state logic. See the variable map below. |

## Reference screens

| File | Screen |
|---|---|
| `20-themes-gallery.png` | The four themes side by side |
| `21-appearance-dark.png` | Settings › Appearance (defaults) |
| `22-appearance-system-paper-literata.png` | System theme using Paper/Midnight, Literata answers |
| `23-appearance-paper-atkinson-large.png` | Paper, Atkinson for UI and answers, large text |
| `24-popups-dark.png`, `25-popups-light.png` | Popup system: confirm, tool approval, agent question, toasts, menu, model picker, tooltip |
| `26-phone-approval-sheet.png` | Tool approval as a phone sheet (Midnight) |
| `27`–`31` `launch-*.png` | Launch intro: checking, ready, cold model, Mac mini offline, model app down |
| `32-offline-mac-details.png` | Mac mini unreachable, details open |
| `33-offline-this-device-light.png` | This device offline (light) |
| `34-runtime-not-responding.png` | LM Studio not responding: pill, popover, composer strip |
| `35-runtime-model-missing-paper.png` | Configured model missing (Paper) |
| `36-phone-launch-checking.png`, `37-phone-offline-checks.png` | Phone launch and offline |

These are stills. The motion is specified in SPEC §2.1 and §3, and the canvas plays it (Launch, Offline and RuntimeDown are interactive there).

The sample content is illustrative: model names, 38 ms, "3 sources" and 21:02. The app must show real values or hide the element.

**Two things in the mockups are not product:**

- the **Replay intro** button;
- the **Auto** row in the model picker, which only appears once the router exists.

## Mockup variables → real tokens

The `.dc.html` sources use short mockup names. Map them like this:

| Mockup | tokens.css |
|---|---|
| `--side` | `--sidebar` |
| `--surf` / `--raised` / `--hover` | `--surface` / `--surface-raised` / `--surface-hover` |
| `--line2` | `--line-strong` |
| `--ink2` / `--ink3` | `--ink-secondary` / `--ink-muted` |
| `--acc` / `--acc-ink` / `--acc-text` / `--acc-soft` / `--acc-line` | `--primary` / `--primary-ink` / `--primary-text` / `--primary-soft` / `--primary-line` |
| `--hl` | `--highlight` |
| `--ev`, `--ev-soft`, `--ev-line` | `--evidence`, `--evidence-soft`, `--evidence-line` |
| `--ok` / `--warn` / `--err` (+ `-soft`) | `--success` / `--warning` / `--danger` (+ `-soft`) |
| `--err-line` | `--danger-line` (new) |
| `--shadow` / `--pop-shadow` | `--shadow-composer` / `--shadow-overlay` |
| classes `theme-*`, `acc-*`, `read-*`, `ui-*`, `size-*`, `hc`, `rm` | attributes `data-theme`, `data-accent`, `data-font-read`, `data-font-ui`, `data-text-size`, `data-contrast`, `data-motion` |

## What changes, in one paragraph

Appearance becomes a proper Settings section: five theme cards that paint themselves, an accent picker, interface and answer fonts, answer size, and switches for contrast and motion. All of it is applied by a tiny boot script before first paint, so the wrong theme never flashes. Every popup follows one system: native dialogs that turn into sheets on phone, inline cards when the agent needs you, toasts that never block, and menus and popovers anchored to what opened them. Opening the app runs a one-second launch intro that is the real connection check (Mac mini, model, library), and it hands off cleanly when something is wrong. When the Mac mini is unreachable, a cached copy of the app (a new service worker) shows an offline screen that retries by itself, explains what to check and keeps saved chats readable. When only the model app is down, the app stays usable and just pauses answers.

## Non-negotiables (unchanged from v2)

1. Zero-build vanilla stack.
2. CSP-clean: no inline styles or scripts.
3. Additive API changes only.
4. Never show a value the backend didn't provide.
5. WCAG 2.2 AA.
6. Every existing flow keeps working.
