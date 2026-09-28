---
name: AgenticRAG Workbench
description: A calm, inspectable, premium workbench for private local-model agents. v2 "Graphite & Cobalt".
version: 2
supersedes: DESIGN.md v1 (neutral + honey amber; never fully shipped — code drifted to navy + blue)
decided: 2026-09-28 (Jake): cobalt accent, Newsreader for answers, full redesign
colors:
  dark:
    canvas: "#0C0C0D"
    sidebar: "#111113"
    surface: "#161618"
    raised: "#1C1C1F"
    hover: "#222226"
    active: "#242429"
    ink: "#EDEDEF"
    ink-secondary: "#A8A8B0"
    ink-muted: "#85858D"
    line: "#232327"
    line-strong: "#33333A"
    primary: "#6E95FF"
    primary-hover: "#86A7FF"
    primary-ink: "#07102A"
    primary-text: "#9DB7FF"
    evidence: "#7CCFE0"
    success: "#62CF8F"
    warning: "#E9B949"
    danger: "#F2786D"
  light:
    canvas: "#FAFAF8"
    sidebar: "#F3F3F0"
    surface: "#FFFFFF"
    raised: "#FFFFFF"
    hover: "#ECECE8"
    active: "#E6E6E1"
    ink: "#17171A"
    ink-secondary: "#52525A"
    ink-muted: "#6A6A72"
    line: "#E5E5E0"
    line-strong: "#D2D2CC"
    primary: "#2F5BEA"
    primary-hover: "#2448C4"
    primary-ink: "#FFFFFF"
    primary-text: "#2448C4"
    evidence: "#0B7285"
    success: "#1A7340"
    warning: "#8A5F00"
    danger: "#B83227"
typography:
  ui:
    fontFamily: "Geist, ui-sans-serif, system-ui, -apple-system, sans-serif"
    sizes: { caption: 11.5px, small: 12.5px, row: 13px, body: 14px, input: 15px, title: 24px }
    weights: { regular: 400, medium: 500, strong: 550, heading: 600 }
  read:
    fontFamily: "Newsreader, 'Iowan Old Style', Georgia, serif"
    answer: { fontSize: 17.5px, lineHeight: 1.62, maxWidth: 75ch }
    passage: { fontSize: 15px, lineHeight: 1.6 }
    display: { fontSize: 46px, fontWeight: 400, letterSpacing: -0.015em, use: empty states only }
  mono:
    fontFamily: "Geist Mono, ui-monospace, SFMono-Regular, Menlo, monospace"
    sizes: { value: 11.5px, count: 11px }
rounded: { xs: 6px, sm: 8px, md: 12px, lg: 16px, pill: 999px }
spacing: { base: 4px, scale: [4, 8, 12, 16, 20, 24, 28, 32, 40] }
layout:
  titlebar: 52px
  sidebar: 256px
  side-panel: 384px
  sources-preview: 440px
  thread-max: 736px
  composer-max: 680px
  library-max: 1040px
components:
  button-primary: { background: "{primary}", text: "{primary-ink}", radius: "{rounded.sm}", height: 34px, padding: "0 12px" }
  button-secondary: { background: transparent, border: "1px {line-strong}", text: "{ink}", radius: "{rounded.sm}", height: 34px }
  pill: { height: 30px, border: "1px {line}", radius: "{rounded.sm}", font: "500 12.5px ui" }
  citation-pill: { height: 18px, minWidth: 19px, radius: 5px, font: "500 11px mono", color: "{evidence}", active: "{primary-text} on primary-soft" }
  composer: { background: "{surface}", border: "1px {line-strong}", radius: "{rounded.lg}", shadow: composer, maxWidth: 680px }
  card: { background: "{surface}", border: "1px {line}", radius: "{rounded.md}" }
---

# Design System v2: AgenticRAG Workbench — "Graphite & Cobalt"

## North star

**A premium instrument for reading evidence.** The workbench should feel like a quiet, expensive tool, closer to Linear or a well-made desktop app than a dashboard. The answer and its evidence are what matter, and everything else steps back. The agent's work (plan → search → read → draft → review → validate) is shown with pride, because inspectability is what sets this product apart. But it's summarised first and expanded on request.

Premium here comes from four things:

1. **Restraint.** Graphite neutrals, one action colour (cobalt), and no decoration.
2. **Typography.** A crisp UI sans (Geist) and a book face (Newsreader) for anything you *read*.
3. **Space for the content.** The conversation gets ~75% of the viewport. Chrome is thin.
4. **Evidence that connects.** Every citation opens the exact passage it rests on.

Interaction references: ChatGPT/Claude desktop for the conversation, Linear for density and navigation, LM Studio for model management. They're references for feel, not visual copies.

## Colour

Graphite neutrals are almost chroma-free, and every tint in the UI means something. Tokens live in `tokens.css`, the single source of truth. If a mockup and `tokens.css` disagree, `tokens.css` wins; for example, the light-theme green was darkened for AA.

- **Cobalt (`--primary`)** is the only action and selection colour. Use it for the send button, primary buttons, the selected mode pill, the active citation and card, the current step, focus rings, and meters that represent "this run".
- **Evidence (`--evidence`, cyan)** marks citation pills and evidence affordances. It says "this links to a source". It is never used for actions.
- **Status (success/warning/danger)** always comes with a word or an icon. Colour alone never carries meaning.

**The One Signal rule.** Cobalt fills cover under 5% of any screen. On the chat screen at rest, the only cobalt fills are the send button and small tinted chips. Never use cobalt as a background wash, a gradient, or on inactive controls.

**The Evidence rule.** A cyan pill always opens evidence. If something is cyan, clicking it shows a source.

## Typography

| Role | Face | Size / line height | Notes |
|---|---|---|---|
| Assistant answer | Newsreader 400 (600 for bold) | 17.5 / 1.62 (phone 17 / 1.58) | Max 75ch. Tables and code inside answers switch to Geist / Geist Mono. |
| Evidence passage | Newsreader 400 | 15 / 1.6 | Cited text is highlighted with `--highlight`. |
| Empty-state display | Newsreader 400 | 46 / 1.1, −0.015em | Only on New chat. Never in controls. |
| View title (H1) | Geist 600 | 24, −0.02em | One per library view (Models, Sources, Tools). Chat has no H1. The chat title lives in the title bar. |
| UI body | Geist 400 | 14 / 1.5 | |
| Rows, buttons | Geist 400–500 | 13 | |
| Secondary, pills | Geist 400–500 | 12.5 | |
| Captions, meta | Geist 400 | 11.5–12 | |
| Machine values | Geist Mono 400 | 11–12.5 | Model IDs, hashes, versions, timings, endpoints, counts. |

**The Sentence-case rule.** No uppercase eyebrow labels anywhere. Group labels ("Today", "Retrieved but not cited") are 12 px Geist 500 in `--ink-muted`, sentence case. This replaces v1's `YOUR WORKSPACE` / `CONVERSATION` style labels.

**The Semantic Mono rule** (kept from v1). A value that someone might copy into a command or compare byte for byte is monospace. Everything else is sans.

**The One Name rule.** Models get a display name ("Gemma 4 12B") everywhere, with the runtime ID (`gemma4:12b-mlx`) as a secondary mono line where there's room. Never show only the raw ID in primary UI.

## Shape, depth and motion

- **Radii:** 6 for chips and tags, 8 for buttons, pills, rows and inputs, 12 for cards, panels and tables, and 16 for the composer and chat bubbles. Use the full pill radius only for the runtime pill, filter chips and starter prompts.
- **Borders:** permanent regions are separated by 1 px `--line` rules, never by shadows.
- **Shadows** are used on exactly three things: the composer (it floats over a scrolling thread), popovers and menus, and phone sheets. Nothing else.
- **Motion:** 140 ms for hover and colour, 220 ms for panels and sheets, using `--ease`. Motion explains a state change and is never decorative. Live-run indicators use a small spinner or pulse, and every animation honours `prefers-reduced-motion`.
- **No** gradients, glassmorphism, neon or glow. The only exception is the light skeleton pulse while an answer is pending.

## Layout

```
┌──────────┬──────────────────────────────────────────┬──────────────┐
│ Sidebar  │ Title bar (52): breadcrumb · runtime pill │ Panel head   │
│ 256      ├──────────────────────────────────────────┤ Evidence|Steps│
│          │ Thread (max 736, centred)                 │ 384          │
│ brand    │   user bubble                             │ (optional,   │
│ project  │   answer: meta · steps · body · sources   │  closable)   │
│ new/search│                                          │              │
│ nav (4)  ├──────────────────────────────────────────┤              │
│ history  │ Composer dock (max 680, centred)          │              │
│ readiness│                                           │              │
└──────────┴──────────────────────────────────────────┴──────────────┘
```

- **Breakpoints:**
  - **≥ 1280:** full layout.
  - **1024–1279:** the side panel overlays the right edge as a drawer with a scrim, instead of taking a grid column.
  - **601–1023:** the sidebar collapses to an off-canvas drawer, toggled from the title bar.
  - **≤ 600:** phone layout: title bar 60, no bottom tab bar, navigation in the drawer, evidence as a bottom sheet, 44 px touch targets.

## Components

`SPEC.md` gives the anatomy and states, and `components.reference.css` has CSP-safe starting CSS.

- **Sidebar:**
  - Brand.
  - Project switcher: avatar, name, "N sources · collection".
  - New chat (⌘N) and search (⌘K).
  - Four nav rows with counts: Sources, Models, Tools & agents, Project memory.
  - Date-grouped history.
  - Readiness footer: "Ready · 4 of 4 checks reachable" plus the endpoint in mono.
- **Title bar:** breadcrumb (project / chat title), runtime pill (status dot, model display name, "On this Mac"), theme toggle, and a panel toggle when the panel is closed.
- **Composer:** textarea, then a toolbar with the **mode pill** (menu), **scope pill** (project · source count), attach, skills and web search (disabled with an explanation outside Direct and Supervisor), then send. A caption sits under it. While running, send becomes **Stop**.
- **Answer anatomy:** meta row (mode glyph · mode · model · elapsed) with a **verification badge** on the right, then the **steps summary** (expandable), the **answer body** (Newsreader) with **citation pills**, **source chips**, and **actions** (Copy · Save to memory · Rerun with another model).
- **Side panel:** tabs **Evidence** and **Steps**.
  - **Evidence:** evidence cards (one expanded at a time), a "Retrieved but not cited" list and the trust note.
  - **Steps:** a detailed timeline and a Budget card.
- **Library tables:** a single bordered table with ruled rows and a tinted current row. No card grids.

## Do / Don't

**Do:**

- Keep the conversation dominant, with thin chrome.
- Derive every badge, count and status from backend data (`DATA-CONTRACT.md`). If the data isn't there, hide the element rather than invent it.
- Pair every status colour with words.
- Keep machine values in mono.
- Keep the whole stack zero-build and CSP-clean.

**Don't:**

- Use uppercase eyebrows.
- Use a full-bleed warning banner.
- Use more than one filled cobalt control per region.
- Use inline `style=""`.
- Load remote fonts or scripts.
- Use emoji as icons.
- Anthropomorphise the agent ("I'm thinking…"). Describe what it did ("Reading sheet-pan-nachos.md").
- Show a capability the backend didn't report.

## Kept from v1

The local-first honesty (the "On this Mac" boundary, no silent cloud fallback), the accessibility baseline (WCAG 2.2 AA, visible focus, live regions, reduced motion), ruled capability rows, and the caveat copy on measurements.
