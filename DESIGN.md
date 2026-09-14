---
name: AgenticRAG Workbench
description: A calm, inspectable control plane for private local-model agents.
colors:
  midnight-canvas: "oklch(0.115 0 0)"
  work-surface: "oklch(0.145 0 0)"
  raised-surface: "oklch(0.18 0 0)"
  primary-ink: "oklch(0.955 0 0)"
  secondary-ink: "oklch(0.72 0 0)"
  boundary: "oklch(0.27 0 0)"
  signal-amber: "oklch(0.58 0.15 70)"
  signal-amber-hover: "oklch(0.64 0.16 70)"
  evidence-cyan: "oklch(0.76 0.12 190)"
  verified-green: "oklch(0.74 0.14 145)"
  warning-gold: "oklch(0.79 0.14 82)"
  failure-red: "oklch(0.69 0.18 28)"
typography:
  headline:
    fontFamily: "Segoe UI Variable, Aptos, Inter, ui-sans-serif, system-ui, sans-serif"
    fontSize: "34px"
    fontWeight: 580
    lineHeight: 1.13
    letterSpacing: "-0.045em"
  title:
    fontFamily: "Segoe UI Variable, Aptos, Inter, ui-sans-serif, system-ui, sans-serif"
    fontSize: "22px"
    fontWeight: 620
    lineHeight: 1.2
    letterSpacing: "-0.03em"
  body:
    fontFamily: "Segoe UI Variable, Aptos, Inter, ui-sans-serif, system-ui, sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.5
  label:
    fontFamily: "Segoe UI Variable, Aptos, Inter, ui-sans-serif, system-ui, sans-serif"
    fontSize: "10px"
    fontWeight: 700
    lineHeight: 1.4
    letterSpacing: "0.09em"
  mono:
    fontFamily: "Cascadia Code, SFMono-Regular, Consolas, monospace"
    fontSize: "10px"
    fontWeight: 400
    lineHeight: 1.45
rounded:
  precise: "5px"
  panel: "8px"
  composer: "12px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "14px"
  lg: "18px"
  xl: "26px"
components:
  button-primary:
    backgroundColor: "{colors.signal-amber}"
    textColor: "oklch(0.99 0 0)"
    rounded: "{rounded.precise}"
    padding: "7px 12px"
    height: "36px"
  button-primary-hover:
    backgroundColor: "{colors.signal-amber-hover}"
    textColor: "oklch(0.99 0 0)"
    rounded: "{rounded.precise}"
  input:
    backgroundColor: "{colors.raised-surface}"
    textColor: "{colors.primary-ink}"
    rounded: "{rounded.precise}"
    padding: "7px 9px"
    height: "36px"
  panel:
    backgroundColor: "{colors.work-surface}"
    textColor: "{colors.primary-ink}"
    rounded: "{rounded.panel}"
    padding: "14px"
---

# Design System: AgenticRAG Workbench

## Overview

**Creative North Star: "The Local Model Workbench"**

AgenticRAG should feel like a serious desktop instrument: calm enough for sustained research, direct enough for debugging, and familiar to users of LM Studio and the ChatGPT desktop app. Conversation is the center of gravity; model, corpus, capability, and trace state stay one interaction away without competing with it.

The system uses restrained neutral architecture, compact operational density, and a single scarce action color. Responsive behavior is structural: the inspector becomes a drawer, the side navigation collapses, and mobile navigation moves to the bottom. Motion lasts 140–220ms and always explains feedback or state.

It explicitly rejects sci-fi terminals, gamer neon, generic SaaS card grids, excessive gradients, anthropomorphic agent theater, and opaque automation.

**Key Characteristics:**

- Conversation-led, inspectable, and local-first.
- Dense enough for a developer; ordered enough for a later nontechnical layer.
- Flat neutral surfaces with one scarce honey-amber signal.
- LM Studio, ChatGPT desktop, and Linear as interaction references—not visual copies.

## Colors

The dark workbench uses neutral, chroma-free surfaces so state and action colors remain unambiguous. A literal white canvas and neutral near-white layers carry the light theme; warmth lives only in the amber signal family.

### Primary

- **Signal Amber:** the only primary-action fill, active glyph color, and meaningful focus family.
- **Signal Amber Hover:** the brighter response state for primary controls and active icon emphasis.

### Secondary

- **Evidence Cyan:** links from answers into evidence and informational trace affordances.
- **Verified Green:** positive readiness and validated execution state.
- **Warning Gold / Failure Red:** explicit warning and error state, always paired with text or an icon.

### Neutral

- **Midnight Canvas:** the uninterrupted conversation and source-reading plane.
- **Work Surface / Raised Surface:** sidebars, toolbars, fields, and temporary elevated controls.
- **Primary Ink / Secondary Ink:** the readable hierarchy for conclusions and supporting context.
- **Boundary:** one-pixel structure separating functional regions.

**The One Signal Rule.** Amber occupies less than ten percent of a screen and marks the primary action, current focus, or one critical state—never decoration.

**The Color-Plus-Language Rule.** No success, warning, connection, or failure state relies on color alone.

## Typography

**Display Font:** none; product UI does not use a display face.
**Body Font:** Segoe UI Variable with Aptos, Inter, and system sans fallbacks.
**Label/Mono Font:** Cascadia Code with SFMono-Regular and Consolas fallbacks.

**Character:** a technical humanist sans keeps conversation comfortable and controls familiar. Monospace is a semantic cue reserved for model IDs, hashes, endpoints, timings, versions, and budgets.

### Hierarchy

- **Headline** (580, 34px, 1.13): teaching empty states only; 28px on compact mobile.
- **Title** (620, 22px, 1.2): one workspace heading per view.
- **Body** (400, 14px, 1.5): interface prose; assistant answers increase to 15px/1.7 and remain below 75ch.
- **Label** (700, 10px, 0.09em): short operational eyebrows and field labels in uppercase.
- **Mono** (400, 10–11px, 1.45): machine values and trace metadata, never long prose.

**The Reading First Rule.** Conversation and explanation stay in sentence case; uppercase is restricted to compact operational labels.

**The Semantic Mono Rule.** If a value is copied into a command or compared byte-for-byte, it may be monospace. Everything else is sans.

## Elevation

The workbench is flat by default. Tonal layering and one-pixel boundaries define permanent regions. Only transient popovers, toasts, the mobile inspector drawer, and the composer receive ambient shadow; no resting content row floats.

### Shadow Vocabulary

- **Overlay Ambient** (`0 24px 60px oklch(0.02 0 0 / 0.55)`): temporary overlays in dark mode.
- **Composer Grounding** (`0 10px 35px oklch(0.02 0 0 / 0.22)`): keeps the input anchored above a scrolling conversation.

**The Surface Truth Rule.** A panel earns separation through hierarchy and state, never through decorative floating-card shadows.

**The Flat-by-Default Rule.** Shadows are a response to temporary elevation, not a component style.

## Components

### Buttons

- **Shape:** precise, gently squared corners (5px) and a minimum 34–36px desktop height.
- **Primary:** Signal Amber with near-white text and compact 7px × 12px padding.
- **Hover / Focus:** brighten to Signal Amber Hover in 140ms; use a two-pixel visible focus ring; active state returns to the base tone and moves by one pixel.
- **Secondary / Ghost:** neutral surface or transparent fill with a one-pixel boundary; never use amber for inactive choices.

### Chips

- **Style:** neutral outlined metadata with monospace text; status chips include language and a shape indicator.
- **State:** selected workflow choices use a raised neutral surface rather than a saturated fill.

### Cards / Containers

- **Corner Style:** 8px only for bounded temporary or explanatory containers.
- **Background:** permanent regions use canvas or work surfaces; rows are separated by rules rather than individual cards.
- **Shadow Strategy:** flat at rest; follow the elevation vocabulary.
- **Border:** one pixel using Boundary or its stronger neutral.
- **Internal Padding:** 14px compact panels, 18–26px workspace regions.

### Inputs / Fields

- **Style:** raised neutral fill, one-pixel strong boundary, 5px corners, and 36px minimum height.
- **Focus:** amber border plus a restrained two-pixel translucent outer ring.
- **Error / Disabled:** errors combine failure text with color; disabled fields retain legible value and reduce opacity.

### Navigation

Top bar plus side navigation on desktop. The current view receives a low-chroma active surface and amber icon, not a filled accent rail. At 820px labels collapse; at 600px primary navigation becomes a four-item bottom bar.

### Conversation Composer

The composer is the largest radius in the system (12px) because it is the primary tactile surface. Skills and context sit inside its toolbar; the only amber fill is the current send action.

### Capability Row

Tools, skills, plugins, and policy use full-width ruled rows. Each row shows provenance, access class or hash, plus a text-labeled state so backend truth remains scannable.

## Do's and Don'ts

### Do:

- **Do** keep conversation as the dominant workspace and cap explanatory prose near 75ch.
- **Do** derive every capability and readiness signal from the backend response.
- **Do** use 140–220ms transitions for feedback and honor `prefers-reduced-motion`.
- **Do** pair status color with a label, icon, or both.
- **Do** preserve the versioned HTTP boundary so a simpler nontechnical frontend can reuse it.

### Don't:

- **Don't** use sci-fi terminal styling or gamer neon.
- **Don't** compose the screen as a generic SaaS card grid; use functional regions and ruled rows.
- **Don't** use excessive gradients or decorative glassmorphism.
- **Don't** anthropomorphize agents or imply capabilities that the backend has not reported.
- **Don't** hide automation, fallback behavior, tool calls, evidence state, or access scope.
- **Don't** use decorative motion, orchestrated page entrances, display fonts in controls, or custom scrollbars.
- **Don't** use amber on inactive controls or as a decorative background wash.
