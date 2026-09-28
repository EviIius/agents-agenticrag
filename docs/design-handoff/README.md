# Design handoff: AgenticRAG Workbench v2 ("Graphite & Cobalt")

**Status:** approved by Jake on 28 Sep 2026. Codex implements it; Claude designed it.
**Decisions:**

- **Accent colour:** cobalt.
- **Answer typeface:** Newsreader (book font), with Geist for UI and Geist Mono for machine values.
- **Scope:** the full redesign, shipped in phases.

The design canvas with the interactive mockups is the "AgenticRAG Premium UI" artifact on claude.ai (private to Jake). Everything needed to build is in this folder; the canvas is only for browsing.

## Start here

| Read | What it is |
|---|---|
| **CODEX-PROMPT.md** | Copy-paste prompts, one per phase. Start with the first. |
| **IMPLEMENTATION-PLAN.md** | Ground rules, phases 0–5 with checklists and "done when" criteria. |
| **SPEC.md** | Screen-by-screen anatomy, states, data sources, responsive rules, accessibility, copy deck. |
| **DATA-CONTRACT.md** | The small, additive backend changes (B1–B9) plus the static-asset and font serving changes. |
| **DESIGN.md** | The v2 design system. Replaces the repo-root `DESIGN.md` in Phase 1. |
| **tokens.css** | The source of truth for colour, type, spacing, radii, layout and motion. Keeps v1 variable names, so it's a drop-in. |
| **components.reference.css** | CSP-safe CSS for the new components (pills, badge, steps, evidence cards, composer, tables, phone). |
| **QA-CHECKLIST.md** | Visual, truthfulness, accessibility (with a contrast table), regression and performance checks. |
| **fonts/** | Self-hosted Geist, Geist Mono and Newsreader (woff2, Latin and Latin Extended), with their SIL OFL 1.1 licences. |
| **reference/screens/** | The target renders (PNG). `00-*` are the current build for comparison. |
| **reference/html/** | The same screens as static HTML. Open them in a browser to measure spacing and read copy. Inline styles here are for reference only. |

## Reference screens

| File | Screen |
|---|---|
| `01-chat-answer-dark.png` | Chat answer, Evidence panel open (dark) |
| `02-chat-steps-open.png` | Steps expanded inline, Steps tab + budget |
| `03-chat-answer-light.png` | Chat answer (light), citation 2 open |
| `04-agent-running.png` | Live agent run |
| `05-new-chat-mode-menu.png` / `15-new-chat-light.png` | New chat with the mode menu |
| `06-models.png` / `14-models-light.png` | Models |
| `07-sources-light.png` / `13-sources-dark.png` | Sources with preview |
| `08-phone-chat.png` | Phone chat |
| `09-phone-evidence.png` | Phone evidence sheet |
| `00-current-chat-answer.png`, `00-current-run-trace.png` | Today's UI, for before/after |

The sample content is the repo's sample corpus (recipes and the mode guide). The Models numbers are the real 28 Sep results from `docs/evaluation-baseline-2026-09-28.md` (the Fixed RAG early check and the one-question mode smoke run). Anything else that looks like data in the mockups (version hashes, step durations, the 8-passage count) is illustrative. The app must show real values or hide the element (see DATA-CONTRACT).

## What changes, in one paragraph

The navy and blue v1 look gives way to graphite surfaces with a single cobalt action colour. The top bar, page header and warning banner go away, so the conversation gets about 75% of the screen instead of 53%. Mode and scope move into the composer. Answers are set in Newsreader and open with a verification badge and a one-line step timeline. Citations become pills that open the exact passage in an Evidence/Steps side panel, which replaces the inspector drawer. Runs show their steps live. Models becomes a measured comparison table, and Sources becomes a table with a highlighted preview. On phone, the bottom tab bar gives way to a menu drawer and evidence opens in a bottom sheet.

## Non-negotiables

1. Zero-build vanilla stack.
2. CSP-clean: no inline styles.
3. Additive API changes only.
4. Never show a value the backend didn't provide.
5. WCAG 2.2 AA.
6. Every existing flow keeps working.

## Implementation note (28 Sep 2026)

The requested implementation is a design overhaul with existing functionality preserved. The app now serves the bundled fonts and cobalt tokens, uses the new shell, composer, answer styling, evidence and steps panel, model comparison table, source preview, and phone drawer. Existing chat, model, source, project, memory, tool, upload, dictation, web search, and stop controls remain wired to their current actions.

The data-contract proposals B1–B9 are intentionally outside this visual-only pass. The UI hides per-step durations and live step claims without event timestamps or live events, shows inline citation buttons only when the answer already contains valid markers, and labels configured runtimes as configured until a probe confirms reachability. The reference files remain for later visual review.
