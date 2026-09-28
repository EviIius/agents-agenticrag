# Design review: Codex build vs the v2 design (28 Sep 2026)

**What I tested.** The working tree as of 15:47 UTC, run unchanged in a sandbox. Model, corpus and Ollama responses were faked at the network layer with the same sample answer used in the mockups. That answer already contains `[1]`/`[2]` markers; see gap 1 for why real answers may not. The screens were compared against `docs/design-handoff/reference/screens/` at 1440×900 and 390×844, in dark and light, and every gap below was checked in the code, not just in screenshots.

**Where it stands.**

- Phase 0 is done.
- Phase 1 is mostly done.
- About half of Phase 2 and the front-end half of Phase 3 are done.
- None of the backend items (B1–B5) are done.
- Phase 4 is partial.

Codex restyled the v1 markup with an overlay stylesheet (`design-v2.css`) plus DOM moves in `prepareDesignShell()`, rather than rebuilding it. The chat screen already looks close to the design.

## Done well (keep)

- Tokens are the only source of colour: no hard-coded colours in `styles.css` or `design-v2.css`, and the old `:root` blocks are gone.
- Fonts are self-hosted and served as `font/woff2` with long caching, and a test covers it. CSP stays clean, with no inline styles anywhere.
- `DESIGN.md` has been replaced with v2.
- Graphite and cobalt in both themes, Newsreader answers, and incremental markdown while streaming.
- Title bar with breadcrumb; the page header and warning banner are gone.
- Date-grouped history.
- The verification badge follows the SPEC §3.3 table.
- Inline citation pills (text-node walk, code blocks skipped).
- An Evidence/Steps panel as a real grid column.
- Honest readiness wording ("Configured · 4 of 4", hollow dot).
- Model display names are consistent everywhere.
- Models table driven by the evaluation data.
- The Sources preview highlights the cited range when opened from a citation.
- Phone: bottom tab bar removed and menu drawer added.

## What's missing, most important first

### P1: fix before calling Phase 3 done

1. **Citation markers aren't requested from the model (B4).**
   - `agent.py` and `workflows.py` are unchanged, so no answer prompt asks for `[n]`.
   - The pill code works, but in real runs most answers will have no markers, so you'll only get the source chips.
   - Add the prompt instruction and host-side marker repair from DATA-CONTRACT B4.
2. **No reachability check (B5).**
   - There's no `/api/v1/runtime-status` endpoint.
   - As a result, the dot never turns green even when Ollama is fine, and nothing warns you when it's down.
3. **Steps are still raw log lines.**
   - The expanded list and the Steps tab show `obligation_count: 3 · host_simplified: false`, because `eventDetailText()` falls back to key: value pairs.
   - Missing:
     - The title and detail mapping in SPEC §3.4.
     - The chain summary ("Plan › Search › Read ×2 › Draft › Review › Validate").
     - Success checks instead of hollow circles.
4. **Evidence cards are unfinished** (SPEC §4.1).
   - The chunk isn't highlighted, and raw markdown shows (`## Minimal-mess method`).
   - The passage is clipped mid-line.
   - There's no section label, "cited N×" count, version/type/size footer or **Copy citation** button.
   - The cards use native `<details>` triangles.
   - The uncited list shows file names without sections.
   - The panel shows the title "Evidence" and then the tabs again.
5. **No active-pill state.** When the panel shows source 1, the matching pills aren't marked (`aria-pressed` and cobalt style are missing).
6. **The phone layout breaks** (see `7-phone.png`).
   - The answer table wraps words mid-word ("Cookin g vessel"). It needs horizontal scroll.
   - The composer toolbar overflows: the "Attach" label is clipped, the skills count shows as a lone "0", and an extra icon is squeezed in beside it.
   - The badge is truncated.
   - The runtime pill shows only an empty circle.
   - Nav labels in the drawer are centred instead of left-aligned.

### P2: shell and running state

7. **Live runs (B1–B3).**
   - The running state is still "working within configured budgets · Planning, retrieving, and reviewing…".
   - Missing:
     - The live step timeline.
     - Per-step times.
     - The "Review pending" badge.
     - The budget readout next to Stop.
     - The history-row spinner.
     - "1 run active" in the footer.
8. **Composer controls.**
   - "Skills 0", "Attach" and "Dictate" are text buttons. They should be icon buttons, with Dictate moved into the attach menu.
   - The scope pill has no icon.
   - The mode pill uses ◇ instead of the mode glyphs.
9. **Mode menu.**
   - Missing the source tags (No sources / Cites sources / Cites + reviews / Usually cites), the typical times from the evaluation, the glyph boxes and the footnote.
   - It opens about 70 px below the composer and covers the starter prompts. It should be anchored right under the composer.
10. **Sidebar leftovers.**
    - "Knowledge settings" and "Refresh state" are still in the sidebar; they belong in Project settings.
    - The project switcher has no avatar or "3 sources · research" line, and shows a "+ New project" link instead.
    - New chat has no ⌘N hint.
    - The search button is a text glyph (⌕), not the icon.
    - Nav order should be Sources, Models, Tools & agents, Project memory.
    - "Delete chat" sits in the title bar instead of the history row menu.
11. **New chat.**
    - The old lede copy is still there.
    - The readiness row at the bottom is missing.

### P3: library screens

12. **Models.**
    - Three filled cobalt **Use** buttons break the one-signal rule. Make them bordered.
    - No memory or time bars.
    - No "1 of 8 runs failed" note for GPT-OSS.
    - Scores show as percentages instead of "6 / 6".
    - The old "Local model library" header and the old "Model comparison" cards are still below the table. They should be replaced by the **Mode timing** and **Connections** cards.
    - The active pair lacks reachability, the mono ID and **Test agent contract**.
    - The advanced forms are still inline instead of in a dialog.
13. **Sources.**
    - The big drop box and the full-width OCR select are still there. The design has a slim drop strip, plus search and **Add source** in the header.
    - Missing: filter chips, Version and Status columns, and document titles. Rows show `markdown-v1 · sv4f1c9a2e11`.
    - The "Current versions / Sources" heading is duplicated.
    - The preview shows raw markdown with the file name as its title.
    - The preview has no outline, details list, "Ask about this source" or "Upload new version".
14. **Tools & agents** is fine. The left tab rail instead of top tabs is acceptable.

### P4: cleanup (Phase 5)

15. **Uppercase rules are still in `styles.css`.** These cover `.eyebrow`, form labels, `.citation-label` and `.source-type`. `design-v2.css` hides most eyebrows, but "PDF OCR" on Sources still renders in caps.
16. **v1 markup is hidden or moved, not removed.** `.topbar`, `#workflow-options`, `#knowledge-settings`, the mobile selects and the "You"/"AgenticRAG" speaker labels remain in the DOM, hidden with CSS. That's fine for now, but delete them in Phase 5.

## Suggested next prompt for Codex

```
Read docs/design-handoff/GAP-REVIEW-2026-09-28.md. Fix the P1 items first:
1. B4: update the Fixed, Agentic and Supervisor answer prompts to emit [n] markers, and add host-side marker repair plus tests.
2. B5: add GET /api/v1/runtime-status and wire it to the readiness dot, the runtime pill and the Models status.
3. Map steps with the SPEC §3.4 table: human titles and details, the chain summary, success icons.
4. Finish the evidence cards per SPEC §4.1: mark the chunk, strip markdown syntax, show the section, "cited N×", the footer and Copy citation, and remove the duplicate panel title.
5. Add the aria-pressed active state on citation pills.
6. Phone fixes: table horizontal scroll, composer toolbar overflow (icon buttons, Dictate in the attach menu), badge copy, runtime pill label, left-aligned drawer nav.
Then do P2 (B1–B3 live runs, composer and mode menu, sidebar leftovers).
Screenshot each fix next to docs/design-handoff/reference/screens.
```
