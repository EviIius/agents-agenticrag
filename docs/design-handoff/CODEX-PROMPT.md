# Prompts for Codex

Paste one prompt per phase. Each is self-contained. Wait for Jake's review of the screenshots before starting the next phase.

---

## Kickoff + Phase 0 and Phase 1

```
You're implementing an approved UI redesign for the AgenticRAG workbench. Everything you need is in docs/design-handoff/. Read these first, in order: README.md, DESIGN.md, IMPLEMENTATION-PLAN.md (ground rules + Phase 0 and 1), DATA-CONTRACT.md (the "Static assets" section and B5), and tokens.css.

Do Phase 0 and Phase 1 only.
- Phase 0: bundle the fonts from docs/design-handoff/fonts into src/agenticrag/ui/fonts, add tokens.css, serve both from server.py (allowlist, font/woff2 without charset, long cache), update pyproject package data, link tokens.css before styles.css.
- Phase 1: swap the visual system with no layout changes: delete the old token blocks in styles.css, remove gradients, apply Geist/Geist Mono/Newsreader (Newsreader for assistant answers only), remove all uppercase eyebrow labels, apply the new radii, unify model display names (no raw IDs in primary UI), drop the duplicated "You" label, set theme-color from the theme, implement B5 (GET /api/v1/runtime-status) and make the readiness dot/label honest.
- Replace the root DESIGN.md with docs/design-handoff/DESIGN.md and update .impeccable/design.json to match.

Constraints: zero-build vanilla JS/CSS; no CDN, no new dependencies; CSP is style-src 'self', so no inline style attributes (use classes; dynamic values via el.style.setProperty). API changes must be additive. Keep all existing behaviour. Add tests for the font routes and B5. Run python -m pytest.

When done, give me:
1. A summary of the changed files.
2. Screenshots of Chat, Models and Sources at 1440x900 in dark and light.
3. Anything in the spec you couldn't follow, and why.
```

---

## Phase 2: Shell and composer

```
Continue the redesign in docs/design-handoff/. Do Phase 2 of IMPLEMENTATION-PLAN.md. The spec is SPEC.md §1, §2, §6, §8 and §11. The visual references are reference/screens/05-new-chat-mode-menu.png, 15-new-chat-light.png, 01-chat-answer-dark.png (shell only) and 08-phone-chat.png. The static HTML versions in reference/html/ have exact spacing; translate them into classes (components.reference.css is a CSP-safe starting point). Do not paste inline styles.

Remove the top bar, the chat page header, the workflow segmented control and the corpus banner. Build the new sidebar (project switcher with Project settings for collection and access label, nav with counts, date-grouped history, readiness footer), the title bar with the runtime pill, and the new composer (mode pill + mode menu, scope pill, icon buttons, Stop state, captions). Build the new-chat empty state with the no-sources and unreachable-model variants, and the responsive drawers. On phone, remove the bottom tab bar.

Every existing flow must keep working: see QA-CHECKLIST §4. Screenshot at 1440x900 dark/light and 390x844, next to the references.
```

---

## Phase 3: Answer anatomy, evidence and live runs

```
Continue the redesign. Do Phase 3 of docs/design-handoff/IMPLEMENTATION-PLAN.md.

Backend first (DATA-CONTRACT.md): B1 at_ms on RunEvent, B2 tool_called summaries, B3 SSE "event"/"evidence" frames plus started.limits, and B4 [n] citation markers in the Fixed, Agentic and Supervisor answer prompts with host-side marker repair. Add the tests each item describes. Keep everything additive.

Then the front end (SPEC.md §3, §4, §5, §7, §11 evidence sheet):
- the answer component (meta, verification badge per the §3.3 table, steps summary with the §3.4 event mapping, Newsreader body, citation pills via a text-node walk, source chips, actions);
- incremental streaming markdown;
- the live run timeline;
- the Evidence/Steps side panel, which replaces the inspector drawer;
- the phone bottom sheet.

Saved chats without at_ms or markers must degrade gracefully and must never show fabricated values.

References: 01, 02, 03, 04 and 09 in reference/screens/. Screenshot a real Agentic run against the sample corpus, both themes.
```

---

## Phase 4: Library screens

```
Continue the redesign. Do Phase 4 of docs/design-handoff/IMPLEMENTATION-PLAN.md:
- Models (SPEC §9; references 06 and 14): active pair, installed table driven by /api/v1/evaluation fixed_rag groups, Mode timing, Connections, and the advanced connection forms moved into a dialog.
- Sources (SPEC §10; references 07 and 13): header, drop strip, filter chips, table, and a preview with the cited range highlighted when opened from a citation.
- Tools & agents, dialogs, toasts and popovers restyled per SPEC §12.

Optional if time allows: ⌘K palette, Rerun with another model, B6, B7, B8, B9. Screenshot each view in both themes next to the references.
```

---

## Phase 5: QA and cleanup

```
Finish the redesign. Run the whole docs/design-handoff/QA-CHECKLIST.md and fix what fails. Delete the dead v1 CSS and IDs (listed in IMPLEMENTATION-PLAN Phase 5), bump the asset cache-busting versions, and update README screenshots. Report the checklist with pass/fail per line.
```
