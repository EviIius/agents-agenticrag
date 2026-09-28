# UI Specification: AgenticRAG Workbench v2

How to use this document: every section names its reference screenshot (`reference/screens/`), the static HTML you can open and inspect (`reference/html/`), the element anatomy, the states, and where each value comes from. Measurements are in CSS px at 1440 × 900 unless noted. Token names refer to `tokens.css`, and class names to `components.reference.css`.

> The reference HTML files are static renders with inline styles. Use them to read exact spacing and copy. **Don't copy the inline styles into the app.** The server's CSP (`style-src 'self'`) blocks them. Translate them into classes.

Existing code references (`app.js` functions, element IDs) are accurate as of 28 Sep 2026 and are there to help you find things. If Codex has since moved something, follow the intent.

---

## 1. Global shell

Reference: `01-chat-answer-dark.png`, `03-chat-answer-light.png`

| Region | Size | Background | Notes |
|---|---|---|---|
| Sidebar | 256 wide, full height | `--sidebar` | Right border 1 px `--line` |
| Main column | fluid | `--bg` | Title bar, then thread (scrolls), then composer dock |
| Side panel | 384 wide, optional | `--sidebar` | Left border. Opened by a citation, a source chip or the panel toggle. Remember open/closed per session. |

- The **top bar and page header from v1 are removed.** The brand moves into the sidebar, the runtime chips into the title bar's runtime pill, the workflow segmented control into the composer's mode pill, and the "Saved on this Mac · earlier turns…" line into the composer caption and the Project memory dialog.
- The **full-width "No sources in this library" banner is removed** (see §8, empty and no-source states).
- **Breakpoints:**
  - **≥1280:** 3-column grid when the panel is open.
  - **1024–1279:** the panel overlays as a right drawer (`--shadow-overlay`, scrim `--scrim`, Esc closes).
  - **601–1023:** the sidebar becomes an off-canvas drawer toggled by a title-bar button, and the panel is a drawer.
  - **≤600:** phone layout (§11).

### 1.1 Sidebar (top to bottom)

1. **Brand row** (52 high, aligned with the title bar):
   - Brand mark: a 26 px ink square with a document glyph and a 10 px cobalt dot, bottom right.
   - "AgenticRAG" in Geist 600 14.5.
   - Collapse button (icon, `aria-label="Collapse sidebar"`).
2. **Project switcher** (46 high, bordered card):
   - Avatar with initials on `--primary-soft`.
   - Project name (13 / 550).
   - Sub-line "N sources · {collection}" (11.5 muted).
   - Up/down chevron.
   - Opens a menu: projects list, "New project…", "Project settings…". Project settings holds **Collection ID** and **Access label**, which move out of the sidebar's "Knowledge settings".
   - Data: `state.projects` and `activeProjectId` for the name, `state.sourceCount` for N, `#collection-input` for the collection.
3. **New chat** (34 high, bordered, "⌘N" kbd right-aligned) and a **Search** icon button (34 × 34). Search opens a command palette (⌘K) that searches chats (existing `q` param on `/api/v1/chats`) and jumps to views. The palette can ship in Phase 4; until then the icon focuses an inline search field.
4. **Nav** (4 rows, 32 high, 16 px icon, label, mono count right):
   - Sources (`sourceCount`).
   - Models (number of installed chat models).
   - Tools & agents (`capabilityTotal()`).
   - Project memory (note count). Opens the existing memory dialog.
   - The current view has `aria-current="page"`, `--surface-active` and a cobalt icon. Chat isn't a nav row: clicking a history item or New chat returns to chat.
5. Divider (1 px, 16 px side inset).
6. **History**, grouped by `updated_at`: Today, Yesterday, Previous 7 days, Earlier (group labels 12 / 500 muted, sentence case).
   - Rows are 32 high, single line, with ellipsis.
   - The active chat has `aria-current="true"` and `--surface-active`.
   - A running chat shows a 13 px cobalt spinner at the right (reference `04`).
   - Keyboard: ↑/↓ moves between rows, Enter opens, Delete asks to confirm deletion (moves the existing Delete chat action here and into a row "…" menu).
7. **Readiness footer** (border-top): status dot and a sentence, plus the mono endpoint line.
   - "Ready · 4 of 4 checks reachable". Dot `ok`.
   - "Chat model unreachable" (or similar). Dot `error`, and clicking opens Models.
   - "1 run active · Gemma 4 12B". Dot `busy`, during a run.
   - The endpoint is `{runtime} · {host:port}` from `bootstrap.providers.chat.base_url`.
   - **Reachability requires B5** (DATA-CONTRACT). Until then the text says "Configured · 4 of 4" and the dot is `off` (hollow), never green.

### 1.2 Title bar (52 high, border-bottom)

- **Left:** breadcrumb. `{project}` (muted) / `{chat title}` (ink 550, ellipsis). For library views it shows just the view name.
- **Right:**
  - **Runtime pill.** Status dot, then the model display name (ink 500), a 1 px divider, a shield icon and the boundary label. Boundary label states (from `syncHostedCapabilities()`): "On this Mac" · "On this Mac · web on" · "Hosted model active" (the hosted state uses the warning dot and text). Clicking opens Models.
  - **Theme toggle** (icon button).
  - **Panel toggle** (shown only when the panel is closed and the current chat has evidence).

### 1.3 Model display names (all screens)

A single function `modelLabel(id) → { name, id }` is used everywhere. The name is the human label, e.g. "Gemma 4 12B", "Qwen3 30B A3B", "GPT-OSS 20B", "Llama 3.3 70B · 16K context". The runtime ID is shown in mono only as a secondary line (Models table, Evidence footer, tooltips). This replaces the three current spellings (`gemma4:12b-mlx` in the top bar, "Gemma 4 · 12B" in the composer, and mono "Gemma 4 · 12B" on Models).

---

## 2. Composer

Reference: `01`, `04`, `05`

- **Dock:** padding 6 / 28 / 16, centred at max 680. The composer card uses `--surface`, 1 px `--line-strong`, radius 16 and `--shadow-composer`. On `:focus-within` the border becomes `--primary-line`.
- **Textarea:**
  - Starts at 50 high and auto-grows to at most 40vh. Placeholder text: "Ask a follow-up…" in a chat with turns, "Ask a question about {project}…" in a new chat, "Ask the local model…" in Direct.
  - Enter sends, and Shift+Enter adds a newline, as today.
- **Toolbar** (left to right):
  1. **Mode pill.** Mode glyph (cobalt) and the mode name, plus a chevron. It opens the **mode menu** (§8.2). `aria-haspopup="menu"`, `aria-expanded`. Replaces the v1 segmented control.
  2. **Scope pill.** Stack icon, then "{project}", then muted "· {sourceCount}". It opens a small popover with the source count, a link to Sources and "Project settings…". Hidden in Direct mode.
  3. **Attach** (paperclip icon button). Same behaviour as the existing `#chat-attachment-input`.
  4. **Skills** (hexagon icon). Shows a count badge when skills are selected, and opens the existing skill picker popover. Only shown in Agentic and Supervisor, as today.
  5. **Web search** (globe icon toggle, `aria-pressed`). Shown in Direct and Supervisor. In other modes it's disabled at 45% opacity with the tooltip and `aria-label` "Web search is available in Direct and Supervisor".
  6. **Dictate.** Keep it, but move it into the attach menu (Attach → "Dictate…") to cut toolbar clutter. It keeps the existing consent dialog.
  7. **Send** (34 × 34 cobalt square, radius 10, arrow-up icon). Its `aria-label` follows the mode: "Run agent", "Run supervisor" or "Send".
- **While running,** Send is replaced by **Stop** (bordered, square icon and "Stop"). A mono budget readout "3 / 8 actions · 6.2 s" sits left of Stop (Agentic and Supervisor only, needs B3). The textarea stays enabled so the user can draft the next question, but sending is disabled until the run finishes.
- **Caption** under the card (11.5 muted, centred): "Runs on this Mac · answers cite {project} · retrieved text is evidence, never instructions". In Direct: "Runs on this Mac · Direct mode doesn't search your sources". With web on: "Web search is on for this question · queries leave this Mac". While running: "Stopping keeps your question so you can retry it".

---

## 3. Conversation messages

Reference: `01` (at rest), `02` (steps open), `04` (running)

### 3.1 User message
Right-aligned bubble, max 520, `--surface-raised`, 1 px `--line`, radius 16 16 5 16, 15 / 1.55, `white-space: pre-wrap`. **No "You" label.** This also fixes the v1 "You You · agent" duplication. Attachments show as a tag row under the bubble ("📎" is not allowed: use the paperclip icon plus the file name).

### 3.2 Assistant answer anatomy (top to bottom, 14 px gaps)

1. **Meta row:**
   - Mode glyph (24 square, `--primary-soft`), then mode name (ink-secondary 500) · model display name · elapsed (mono).
   - **Verification badge** on the right (§3.3).
   - No "AgenticRAG" speaker label: don't anthropomorphise.
2. **Steps summary row:**
   - A 36-high bordered button: success check, then step chain labels joined by small chevrons, then a right-aligned "Show steps" / "Hide steps" with a chevron. Expanding reveals the **steps list** inline (§3.4).
   - Collapsed by default when complete, expanded while running.
   - Shown for Agentic, Supervisor and Fixed. Direct shows it only if web search ran.
3. **Answer body:**
   - `.answer-body`: Newsreader 17.5 / 1.62, max 75ch, markdown via marked + DOMPurify (unchanged).
   - Tables and code switch to Geist / Geist Mono (see CSS).
   - **Citation pills** replace `[n]` markers (§3.5).
4. **Source chips:** one per citation, `[n] {file name} {section}`. Clicking opens the panel on that card. External web sources render as chips with a globe icon and the site title, and open in a new tab (existing `external_sources`).
5. **Actions:**
   - Copy.
   - Save to memory (existing dialog).
   - Rerun with another model ▾ (menu of installed chat models; reruns the same question in a new turn with the chosen model; optional, can ship in Phase 4).
   - "View steps" is removed: the steps row replaces it.

### 3.3 Verification badge: states and data

All of these are derived from `result.events` and `result.abstained`. Show nothing when the data doesn't support a claim.

| State | Condition | Copy | Tone |
|---|---|---|---|
| passed | `review_completed.accepted === true` and `answer_validated` present | "Review passed · no unsupported claims" (if `unsupported_claim_count === 0`) | success |
| validated | Fixed RAG: `answer_validated` present, no review event | "{citation_count} citations validated" | success |
| abstained | `result.abstained` or an `abstained` event | "Not enough evidence to answer" | warning |
| budget | `budget_exhausted` event | "Stopped at {kind} budget" (steps / time / stalled) | warning |
| failed | run error | "Run failed safely" | danger |
| pending | running | "Review pending" | neutral, bordered |
| none | Direct without web | *(no badge)*, plus a muted "No sources used" meta item | none |

### 3.4 Steps: chain labels, list rows and durations

Map events to chain labels. Collapse consecutive duplicates into "×N".

| Event | Chain label | List title | List detail (muted) |
|---|---|---|---|
| `plan_created` | Plan | Plan created | "{obligation_count} obligations" (+ texts if B6) · Supervisor: "{delegation_count} specialists" |
| `skill_loaded` | Skill | Skill loaded | `{name}` (mono) |
| `retrieval_completed` | Search | Searched library | query (mono, needs B2) · "{evidence_delta} new passages" |
| `tool_called` action=search | Search | Searched library | as above |
| `tool_called` action=lookup | Read | Read source | "{source_path} › {section}" (needs B2) |
| `tool_called` action=calculate | Calc | Calculated | expression (mono, B2) |
| `tool_called` success=false | (same) | title in `--danger` | error text |
| `validation_rejected` | *(not in chain)* | Output rejected, retried | reason |
| `generation_completed` | Draft | Drafted answer | "{prompt_tokens} in · {completion_tokens} out" when present |
| `review_completed` | Review | Evidence review | "Accepted · {unsupported_claim_count} unsupported claims · {missing_obligation_count} missing obligations", or "Sent back for revision" |
| `answer_validated` | Validate | Citations validated | "{citation_count} citation IDs resolve to the evidence set" |
| `delegation_started` / `_completed` | Specialist | "{agent} specialist" | status · summary (from `result.delegations`) |
| `web_search_completed` | Web | Web search | "{source_count} sources" (existing detail) |
| `synthesis_completed` | Synthesize | Supervisor synthesis | |
| `abstained` | Abstain | Safe abstention | reason |
| `budget_exhausted` | Budget | Budget reached | kind / phase |

- **Durations** (right column, mono) come from B1 (`at_ms`): each row shows `next.at_ms − this.at_ms`, and the final row runs to `result.elapsed_ms`. Without B1, show no per-row times: never fabricate them.
- **Row states:** `done` (check), `running` (spinner, `--primary-soft` row background, "running" in cobalt mono), `pending` (hollow circle, muted), `error` (danger title).

### 3.5 Citation pills

- **Source of truth:** `result.citations` (ordered). A pill `[n]` refers to `citations[n-1]`.
- **Inline placement** needs B4: the answer text contains `[n]` markers.
  - After markdown rendering, walk the text nodes (not `innerHTML` string replace) and replace `\[(\d+)\]` with `<button class="cite" aria-label="Source n: {file}" aria-pressed="false">n</button>` when `1 ≤ n ≤ citations.length`.
  - Leave out-of-range markers as text.
  - Skip `code` and `pre` blocks.
- **Fallback when there are no markers** (older chats, or a model that ignores the instruction): no inline pills, and the source chips row still lists every citation. Never guess positions.
- **Interaction:**
  - Click (or Enter/Space) opens the side panel on the Evidence tab with card n expanded.
  - The pill for the currently expanded card gets `aria-pressed="true"` (cobalt style).
  - Hover shows a native tooltip: `{file} — {section}`.
- A per-card count "cited N×" in the panel is the number of pills referring to that citation.

### 3.6 States of the whole answer

- **Streaming.**
  - Token events append to a text buffer, and markdown is rendered incrementally: re-render at most every 120 ms, with a trailing cobalt caret. No plain-text-then-swap jump at the end.
  - Pills are only linked once `completed` arrives. Before that, `[n]` shows as plain text in the muted colour.
- **Waiting for first token.** Three pulsing skeleton lines (100 / 94 / 62% width) and a muted line: "The answer appears once sources are read."
- **Stopped.** Same behaviour as today: remove the turn and restore the question. Toast: "Run stopped. Your question is ready to retry."
- **Failed.** Answer body replaced by the error message (ink-secondary), badge `failed`, and a "Retry question" action.

---

## 4. Side panel: Evidence and Steps

Reference: `01` (Evidence), `02` (Steps), `04` (live)

- **Head (52):**
  - Tabs "Evidence {citations.length}" and "Steps {events.length}" (`role="tablist"`, arrow-key navigation).
  - Close button on the right.
  - Esc closes the panel and returns focus to the invoking pill or chip.
- The panel shows the **currently focused answer** (the last answer by default, or the one whose pill or chip was clicked). This replaces `renderRunInspector()` and the `.inspector` drawer.

### 4.1 Evidence tab

1. **Meta line:** "{evidence.length} retrieved · {citations.length} cited", and on the right a mono tag "{collection} · {scopes}". No wrapping.
2. **Evidence cards**, one per citation, in citation order.
   - Exactly one card is expanded at a time (`aria-expanded`).
   - **Collapsed card:** pill n, file name (13 / 550), and "{section} · {first sentence of chunk}" with ellipsis, plus a chevron.
   - **Expanded card** (border `--primary-line`):
     - Header: pill n, file name, "{section} · cited N×", and an **Open source** icon button.
     - Passage: the cited chunk's text from `result.evidence` (match `chunk.id === citation.chunk_id`), in Newsreader 15 / 1.6. **v1 highlighting:** wrap the chunk text in `<mark>`. If you show neighbouring context (see Open source), the context is `--ink-muted` and only the chunk range is marked. Sentence-level highlights like in the mockup need B8 (supporting quotes). Until then, mark the whole chunk.
     - Footer: mono short version `v·{source_version_id.slice(0,8)}` · media type · size (from the Sources API if cached), and a **Copy citation** button. It copies `{logical_path} §{section_path.join(" › ")} [{source_version_id}:{start_char}-{end_char}]`.
   - The section label comes from `citation.section_path` (last item), else `chunk.heading`, else `p. {page_start}`, else hidden.
3. **Retrieved but not cited:** `result.evidence` minus cited chunk IDs. Show up to 3 rows with the path (no wrap) and section (ellipsis), then "+ N more passages", which expands.
4. **Trust note** (shield icon, 11.5 muted): "Retrieved text is evidence, never executable instruction. The host validates every model-selected action." (existing copy).

**Open source** navigates to Sources with that version selected, the preview scrolled to `start_char`, and the range `start_char…end_char` highlighted with `<mark>` in the full parsed text from `GET /api/v1/sources/{id}`.

### 4.2 Steps tab

- A vertical list of every event with a 20 px circular state icon (success check / running spinner / pending hollow / error), a title (13 / 500), a detail line (12 muted) and the duration (mono, right-aligned).
- It uses the same mapping as §3.4, but shows **every** event (including `validation_rejected`), plus delegation summaries from `result.delegations`.
- **Budget card** at the bottom (surface card, 14 px padding):
  - **Tool actions:** `count(tool_called) + 1` (the initial search) / `max_steps` (8, sent in the request). Meter.
  - **Elapsed:** `elapsed_ms` / agent `max_seconds` (180 s default; expose it via B3's `started` event or bootstrap). Meter.
  - Fixed and Direct show Elapsed only. Meters use `.meter` with `--value` set from JS.

---

## 5. Run in progress

Reference: `04-agent-running.png`

- Needs **B3** (live events). As each `event` SSE frame arrives, append or update a row in the inline steps list, which is expanded while running. The current row is `running`, and the expected remaining stages show as `pending`:
  - Agentic: Draft, Review, Validate.
  - Fixed: Search, Draft, Validate.
  - Supervisor: Specialists, Synthesize.
- The meta row shows a spinner in the mode glyph and a live elapsed counter (mono, updates every 100 ms from the `started` time). The badge shows "Review pending".
- The side panel's Evidence tab fills live when events include evidence (B3 `evidence` frames), with card states "read" (check) and "reading now" (cobalt). The Steps tab mirrors the list.
- Sidebar: the running chat's history row shows a spinner, and the readiness footer says "1 run active · {model}".
- **Without B3,** show the existing progress message in the meta row and the skeleton only. Don't simulate steps.

---

## 6. Chat management (moved out of the removed page header)

- **Rename:** double-click the title in the breadcrumb, or use the history row menu, then "Rename". Save on Enter or blur, revert on Esc. (Needs a small `PATCH /api/v1/chats/{id}` with `{title}` if one isn't available; this is additive.)
- **Delete:** history row menu → "Delete chat…", with a confirm dialog. Same endpoint as today.
- **New chat:** sidebar button, ⌘N, or the phone title bar "+".
- **Memory status:** the v1 line "Saved on this Mac · previous turns available to the model" moves into the Project memory dialog header and the composer caption tooltip. Direct mode still receives recent turns (unchanged behaviour).

---

## 7. Answer typography details

- Bold → Newsreader 600.
- Lists: 1.5em indent, 6 px between items.
- Headings inside answers: Geist 600 at 15 / 1.4, with 18 px space above.
- Links: `--primary-text`, underline on hover, open in a new tab (existing).
- Blockquote: Newsreader italic, `--ink-secondary`, no left border. Use a 12 px indent and a 1 px `--line` rule above and below.
- Code blocks: `--surface` background, radius 10, Geist Mono 13, with a "Copy code" ghost button top-right (existing behaviour, restyled).

---

## 8. New chat and empty states

Reference: `05-new-chat-mode-menu.png`, `15-new-chat-light.png`

### 8.1 Layout

- The thread area is centred with 104 px top padding.
- **Headline** in Newsreader 46 / 400.
- A one-line **lede** (15, ink-secondary, max 520, centred).
- The **composer** at 720 max width, with a 74-high textarea and 16 px text.
- **Starter prompts:** 3 pill buttons, 18 px under the composer. Keep the existing prompt sets in `updateEmptyState()`.
- A **readiness row** pinned to the bottom (12 muted): status dots and text for the chat model, embedding model and source count.

Headline and lede by mode (replace the `descriptions` map):

| Mode | Headline | Lede |
|---|---|---|
| Agentic | Ask your sources. | Answers come from {project} and are checked against their citations before you see them. |
| Fixed | Answers with sources. | Finds the most relevant passages in {project} and answers with citations. |
| Supervisor | Explore a bigger question. | Up to three specialists investigate, then their evidence is combined and checked. |
| Direct | Start with a question. | Chats with the local model and remembers this conversation. It doesn't search your sources. |

**No sources in the project** (replaces the v1 banner):
- The lede becomes "There's nothing in {project} to cite yet. Add a document to ask grounded questions."
- The starter prompts become one primary button, **Add a source**, plus a quiet "or switch to Direct".
- The scope pill shows "· 0" in `--warning` with the tooltip "No sources".

**Readiness problems:** if the chat model is unreachable (B5), the readiness row item turns `error` and a single inline notice appears above the composer: a bordered card, not a banner, reading "Gemma 4 12B isn't reachable at 127.0.0.1:11434. Start Ollama, or choose another model." with a **Models** button.

### 8.2 Mode menu

- A popover anchored 8 px under the composer card, left-aligned with the mode pill, 480 wide.
- `role="menu"` with `menuitemradio` items. Arrow keys move, Enter selects, Esc closes. It's a single menu instance used in both the new-chat and follow-up composers.
- Each item has:
  - A 30 px bordered glyph box.
  - The name (13.5 / 550) and a **source tag** (No sources / Cites sources / Cites + reviews / Usually cites).
  - A one-line description (12.5 secondary).
  - A right-aligned mono **typical time**.
- The selected item is tinted `--primary-soft`.
- **Typical time:** the mean latency for (active chat model, workflow) from `GET /api/v1/evaluation`. Omit the time when there's no data. Footnote: "Times from {report.case_count} test question(s) on {model}, {date}." Add "Web search is available in Direct and Supervisor." when relevant.
- Changing mode updates `state.workflow` (same as today) and the placeholder, send label, and visibility of the scope, skills and web controls.

---

## 9. Models

Reference: `06-models.png` (dark), `14-models-light.png`

- A library layout (max 1040, padding 32 / 40) with H1 "Models" and the lede "Everything runs on this Mac through {runtime}. Hosted models are off, and nothing falls back to the cloud." The lede switches to the hosted warning copy if any provider is hosted. Header action: **Refresh** (`discoverLocalModels()` + `refreshEvaluation()`).
- **Active pair card** (2 columns, one bordered card, divided by a 1 px rule).
  - **Chat model:**
    - Label "Chat model", with a reachability status on the right (B5).
    - Display name at 19 / 600, and the mono ID.
    - Meta row: runtime · structured-output mode (mono) · request timeout.
    - Button: **Test agent contract** (existing `checkAgentContract()`).
  - **Document search:** the same anatomy, with "Indexes {sourceCount} sources in {project}" and a **Change** button.
- **Installed on this Mac** table (`.models-table`).
  - Heading row: "Installed on this Mac" · the "Fixed RAG early check · {case_count} questions · {repeat} run(s) each" caption · an **Early check** tag when `repeat < 2 || case_count < 20` (same rule as today).
  - Columns: Model (name + mono ID + optional note) | Loaded memory | Avg answer time | Answer checks | No-evidence | action.
  - Data: one row per `state.installedChatModels`. Metrics come from `evaluation.groups` where `workflow === "fixed_rag"` and `model === id`:
    - **Loaded memory:** `mean_model_loaded_gb`, with a meter against system memory (B7). Without B7, the meter compares against the largest value in the table and the header reads "Loaded memory".
    - **Avg answer time:** `mean_latency_ms` as seconds, with a meter against the slowest row.
    - **Answer checks:** `round(answer_substring_accuracy × answer_cases)` / `answer_cases`.
    - **No-evidence:** `round(appropriate_abstention × unanswerable_cases)` / `unanswerable_cases`.
    - "—" when there's no group.
  - **Notes under the name:**
    - Warning (triangle icon, `--warning`): "{failed} of {run_count} runs failed" when `completed_count < run_count`.
    - Info (clock icon, muted): "About N output tokens/s, slow for phone requests" for ≥70B models, where N comes from the evaluation if present, else the text "Large model · slower replies" (existing heuristic).
  - **Current row:** tinted `--primary-soft`, with an "In use" label in `--primary-text` instead of a button. Other rows get a **Use** button (existing select logic).
  - **Caption** under the table: keep the existing honest caveat text word for word, prefixed with "Measured on this Mac on {date}. Averages exclude failed runs."
- **Bottom row** (2 cards):
  - **Mode timing** (for the active model, one bar per workflow that has a group).
    - The active mode's bar is cobalt, the others `--meter-neutral`.
    - Footnote: "Verifies each mode path; not a quality comparison." (keep this).
    - Hide the card if fewer than 2 workflows have data.
  - **Connections:**
    - Rows: Ollama (status and endpoint), "LM Studio · llama.cpp · vLLM" (Not connected), and Hosted OpenAI ("Off · would send prompts off-device", or On in warning tone).
    - **Add endpoint** opens the existing Advanced connections forms inside a dialog (same fields, same endpoints: probe, configure, check-model).

---

## 10. Sources

Reference: `07-sources-light.png`, `13-sources-dark.png`

- Grid: the main column, plus a 440-wide **preview panel** (`--surface`, left border) when a source is selected.
- **Header:**
  - H1 "Sources" and the lede "Immutable versions with stable citation anchors."
  - On the right: a search field (220, filters by name and title client-side) and the primary **Add source** button (upload icon; opens the file picker).
- **Drop strip** (46 high, dashed border): "Drop PDF, DOCX, Markdown or TXT here" · "Up to {max_file_bytes} · processed on this Mac".
  - While dragging a file over the page, the strip gets `.is-over`.
  - The OCR select moves into an "Options" popover on the strip (default "Auto when needed").
  - Upload progress shows inline in the strip ("Adding one-pot-chicken-alfredo.md…", then ✓ "Added · v·4f1c9a2e").
- **Filter chips:** All · Markdown · PDF · DOCX · TXT, with counts from the file extension or `media_type`. Hide chips with a count of 0, except All.
- **Table** (`.sources-table`):
  - Columns: Name (32 px file icon, title, sub-line) | Size (mono) | Version (mono `v·` + 8 chars) | Status.
  - **Title** is the first markdown `#` heading or the PDF title if known, else the file name. The **sub-line** is "{file name} · {type} · added {date}" (`created_at`).
  - **Status:** "Indexed" with a success dot. Future states (Processing, Failed) use warning or danger.
  - The selected row is tinted `--primary-soft`. Rows are buttons with `aria-selected`.
- **Preview panel:**
  - **Head:** mono file name, Open original (if an original is stored), close.
  - **Title:** Newsreader 26 / 500.
  - **Tags:** type · "N sections" (count of markdown headings, or pages for PDFs) · version. When the preview was opened from a citation, add an evidence tag "Opened from citation n".
  - **Outline:** numbered headings. The section containing the cited range is emphasised and labelled "cited passage" in `--evidence`. Clicking a heading scrolls to it.
  - **Text:** a bordered `--bg` block with the parsed text in Newsreader 15.5 and `<mark>` over cited ranges. Long documents render lazily, starting around the cited range.
  - **Details:** a `dl` with Collection, Access label, Parser, Size (bytes), Original SHA and Parsed SHA (mono, truncated with copy).
  - **Actions:** "Ask about this source" (starts a new chat whose first question is pre-filled with `About {file}: `; no backend change needed) and "Upload new version".
- **Removed from v1:** the giant dashed drop zone and the 50/50 empty split.
- **Empty state:** the drop strip grows to 160 high with the copy "Add your first source" and the supported types.

---

## 11. Phone (≤ 600 px)

Reference: `08-phone-chat.png`, `09-phone-evidence.png`

- **Title bar** (60 high, including an 8 px top pad):
  - Menu button (44), title and a project sub-line (12 muted), a runtime pill ("● Gemma 4", tap opens Models) and New chat (44).
  - Honour `env(safe-area-inset-top)`.
- **No bottom tab bar** (remove the v1 four-item bar). The menu opens the sidebar as a left drawer at 86vw, max 320, with the full sidebar content.
- **Thread:** padding 18, answer text in Newsreader 17 / 1.58, pills 22 × 21.
- **Steps row:** a single 44-high summary "7 steps · 2 sources cited · 0 unsupported" with a chevron. It expands inline.
- **Source chips** scroll horizontally (`overflow-x: auto`, `scroll-snap`).
- **Composer:** radius 20, textarea font 16 (prevents iOS zoom), toolbar controls ≥ 44 high: mode pill, attach, then send (44, radius 14) on the right. Honour `env(safe-area-inset-bottom)`.
- **Evidence sheet:**
  - Tapping a pill or chip opens a bottom sheet (max 72dvh, radius 22 top, grabber, scrim).
  - Header: "Source n of N" with prev / next / close (44 each).
  - Then the card anatomy from §4.1, full width.
  - Footer: two 48-high buttons: **Open source** (secondary) and **Next source** (primary).
  - Swipe down or tap the scrim to close. Focus is trapped while open.
- The Steps tab on phone is reachable from the steps row ("Open all steps"), which opens the same sheet on the Steps tab.
- Keep the existing mobile keyboard handling (`updateMobileViewport`, `is-composing`), but remove `#mobile-writing-bar` if the new composer stays visible above the keyboard.

---

## 12. Tools & agents, dialogs, toasts (no dedicated mockup)

- **Tools & agents:** library layout (max 1040).
  - H1 "Tools & agents", with the lede "The exact tools and trusted instruction bundles available to the active agent. The model can't expand this list." (existing).
  - Tabs (`.tab` style): Tools · Agents · Skills · Plugins · Policy, with mono counts.
  - Content is a `.data-table` with ruled rows: name (13 / 550), description (12.5 secondary), tags (`.tag`: "read-only", "sandboxed", "external · per-run consent"), and a status label on the right with a dot ("Enabled", success / "Unavailable", muted).
  - No uppercase.
- **Dialogs** (Project memory, New project, Voice consent, Advanced connections):
  - `--surface-raised`, radius 14, `--shadow-overlay`, scrim, max width 520 (memory 640).
  - Title in Geist 600 18. No eyebrow labels.
  - Buttons right-aligned: secondary, then primary.
- **Toasts:** bottom-centre above the composer, `--surface-raised`, radius 10, 13 px, auto-dismiss after 4 s. Errors get a danger icon and stay until dismissed. `aria-live="polite"` (existing region).
- **Popovers** (skills picker, scope, project switcher, rerun menu) use `.menu`.

---

## 13. Motion

| What | Duration | Easing |
|---|---|---|
| Hover / pressed colours | 140 ms | ease |
| Steps list expand, chevron rotate | 180 ms | `--ease` |
| Side panel open / close (desktop grid) | none: immediate reflow. Drawer variants slide 220 ms. | `--ease` |
| Phone sheet / drawer | 220 ms | `--ease` |
| Running indicators | spinner 1 s linear, pulse 1.6 s | |
| Streaming caret | blink 1 s steps(2) | |

`prefers-reduced-motion: reduce` disables every animation (tokens.css already has the global rule). The spinner falls back to a static half-ring.

---

## 14. Accessibility (WCAG 2.2 AA, from PRODUCT.md)

- **Landmarks:** `nav` (sidebar nav), `main` (thread), `aside` (sidebar, side panel), `header` (title bar). The skip link targets the thread.
- **Live regions:**
  - The thread is `aria-live="polite"` only for completed answers. Streaming tokens are **not** announced token by token: announce "Answer ready" on completion.
  - The steps list announces the current step title (throttled to at most one per 2 s).
- **Focus:**
  - Opening the panel from a pill moves focus to the expanded card's heading. Esc returns it to the pill.
  - The mode menu, popovers and dialogs trap focus and restore it on close.
- **Keyboard:**
  - ⌘/Ctrl+K search, ⌘/Ctrl+N new chat, ⌘/Ctrl+. stop run, Esc closes the top layer.
  - Keep the existing 1–4 view shortcuts, now mapped to Chat, Sources, Models and Tools.
- **Contrast:** every text token pair in `tokens.css` meets 4.5:1 (see the comments there and the table in QA-CHECKLIST.md). Pills and badges were checked on their tinted fills.
- **Touch targets:** 44 × 44 minimum on phone. Desktop controls are ≥ 28 high with ≥ 32 hit areas.
- **Status** never relies on colour: dots always come with text.

---

## 15. Copy deck (new or changed strings)

| Key | Copy |
|---|---|
| composer.placeholder.followup | Ask a follow-up… |
| composer.placeholder.new | Ask a question about {project}… |
| composer.placeholder.direct | Ask the local model… |
| composer.caption.default | Runs on this Mac · answers cite {project} · retrieved text is evidence, never instructions |
| composer.caption.direct | Runs on this Mac · Direct mode doesn't search your sources |
| composer.caption.web | Web search is on for this question · queries leave this Mac |
| composer.caption.running | Stopping keeps your question so you can retry it |
| web.disabled | Web search is available in Direct and Supervisor |
| badge.passed | Review passed · no unsupported claims |
| badge.validated | {n} citations validated |
| badge.abstained | Not enough evidence to answer |
| badge.budget | Stopped at {kind} budget |
| badge.pending | Review pending |
| steps.show / hide | Show steps / Hide steps |
| evidence.meta | {n} retrieved · {m} cited |
| evidence.uncited | Retrieved but not cited |
| evidence.more | + {n} more passages |
| evidence.copy | Copy citation |
| running.skeleton | The answer appears once sources are read. |
| readiness.ok | Ready · {n} of {n} checks reachable |
| readiness.configured | Configured · {n} of 4 (reachability unknown) |
| readiness.busy | 1 run active · {model} |
| empty.nosources | There's nothing in {project} to cite yet. Add a document to ask grounded questions. |
| models.lede.local | Everything runs on this Mac through {runtime}. Hosted models are off, and nothing falls back to the cloud. |
| sources.lede | Immutable versions with stable citation anchors. |
| sources.drop | Drop PDF, DOCX, Markdown or TXT here |
