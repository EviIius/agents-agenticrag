# QA checklist: v2 UI

Run this at the end of every phase, covering the items that phase touched. Everything must pass before Phase 5 closes.

## 1. Visual comparison

Render the app with the sample corpus (`scripts/seed_sample_corpus.py`) and compare against `reference/screens/` at the same size.

| Reference | Viewport | Theme | App state to reproduce |
|---|---|---|---|
| `01-chat-answer-dark.png` | 1440×900 | dark | Agentic answer, panel open on citation 1 |
| `02-chat-steps-open.png` | 1440×900 | dark | Same, steps expanded, panel on Steps |
| `03-chat-answer-light.png` | 1440×900 | light | Same, citation 2 open |
| `04-agent-running.png` | 1440×900 | dark | Mid-run (pause a fake provider, or throttle Ollama) |
| `05-new-chat-mode-menu.png` / `15-new-chat-light.png` | 1440×900 | dark / light | New chat, mode menu open |
| `06-models.png` / `14-models-light.png` | 1440×1040 | dark / light | Models with `.data/workbench-evaluation.json` present |
| `07-sources-light.png` / `13-sources-dark.png` | 1440×900 | light / dark | Sources, first file selected, opened from a citation |
| `08-phone-chat.png` | 390×844 | dark | Phone, answered chat |
| `09-phone-evidence.png` | 390×844 | light | Phone, evidence sheet open |

**Pass criteria.**

- **Structure and alignment match:** the same regions, the same order, and edges within about 4 px.
- **Type matches:** faces, sizes and weights per `DESIGN.md`.
- **Colours come only from `tokens.css`.** Run `grep -nE '#[0-9a-fA-F]{3,8}|rgb\(|oklch\(' src/agenticrag/ui/styles.css`. It should return nothing except inside comments.
- **Copy may differ where it's data-driven.** Real model names, counts and times replace the mockup values, and elements without data are hidden.

The static references in `reference/html/` open directly in a browser (fonts load from `../../fonts/`). Use DevTools to read exact spacing.

## 2. Truthfulness

- [ ] With Ollama stopped, the readiness dot, runtime pill and Models status show *unreachable* (B5), never green.
- [ ] No per-step durations appear for chats saved before B1.
- [ ] An answer without `[n]` markers shows no inline pills, only the source chips.
- [ ] Mode-menu times and the Mode timing card are hidden when the evaluation report has no matching groups.
- [ ] The verification badge follows the SPEC §3.3 table for Agentic, Fixed, Supervisor, Direct, abstained, budget-exhausted and failed runs. Force each state with fake providers in the tests.
- [ ] Hosted OpenAI active → the runtime pill reads "Hosted model active" in warning tone, and the Models lede changes.

## 3. Accessibility (WCAG 2.2 AA)

Contrast (computed from `tokens.css`; re-check if tokens change):

| Pair | Dark | Light |
|---|---|---|
| `--ink` on `--bg` | 16.7 | 17.1 |
| `--ink-secondary` on `--bg` | 8.3 | 7.4 |
| `--ink-muted` on `--bg` / `--surface` | 5.3 / 4.9 | 5.1 / 5.4 |
| `--ink-muted` on `--sidebar` | 5.2 | 4.8 |
| `--primary-text` on `--surface` | 9.2 | 7.5 |
| `--primary-ink` on `--primary` (send, primary buttons) | 6.6 | 5.5 |
| `--evidence` on its soft fill (citation pill) | 8.5 | 5.1 |
| `--success` on its soft fill (badge) | 8.6 | 5.0 |
| `--ink` on `--highlight` (cited text) | 10.9 | 14.6 |

Checks:

- [ ] Keyboard only: reach and operate every control (sidebar, history, composer pills, mode menu, pills, panel tabs, cards, dialogs). Focus is always visible (2 px `--focus` ring).
- [ ] Esc closes the top-most layer (menu, then sheet or panel, then dialog), and focus returns to the invoking control.
- [ ] Screen reader: landmarks present; the mode menu announces as a menu with a checked item; citation pills announce "Source n: {file}"; tabs announce selected state; "Answer ready" is announced once; streaming tokens are not read out.
- [ ] Every status dot comes with text.
- [ ] Phone: every interactive element is at least 44×44, and the composer textarea font-size is 16 (no iOS zoom).
- [ ] `prefers-reduced-motion: reduce` gives no spinners, pulses, caret blink or sheet slide (a static state is shown instead).
- [ ] Zoom to 200%: no loss of content. The sidebar collapses to a drawer.

## 4. Regression: flows that must still work

- [ ] Ask in each mode. Stop mid-run: the question is restored and the empty chat is cleaned up (existing behaviour).
- [ ] Retry after a failure.
- [ ] Attach an image in Direct with a vision model; attach a document (ingests, then asks).
- [ ] Dictation consent dialog, then dictation.
- [ ] Web search consent (Direct and Supervisor only). It resets after each question.
- [ ] Projects: create, switch; chats and sources follow the project.
- [ ] Project memory: add, edit, delete, "Save to memory" from an answer, activity list.
- [ ] Chat history: search, open, delete (and rename if B9).
- [ ] Models: discover, select a model, probe, configure, contract check, advanced connection forms (now in a dialog).
- [ ] Sources: upload by button and by drag-and-drop, OCR option, open a source, highlight from a citation.
- [ ] Tools & agents: all tabs render the backend inventory; web search shows Unavailable when not configured.
- [ ] Theme toggle persists; `theme-color` meta updates.
- [ ] PWA: installs, launches standalone, respects safe areas on iPhone.

## 5. Performance and hygiene

- [ ] Fonts: 3 woff2 files on first paint (Latin), each loaded once, `font-display: swap`, no layout shift after load beyond the swap.
- [ ] Streaming a long answer (~1,500 tokens) keeps the main thread responsive (render throttle ≤ 1 per 120 ms).
- [ ] No console errors, and no CSP violations in the console.
- [ ] `python -m pytest` passes, including the new tests for B1–B5 and the font routes.
