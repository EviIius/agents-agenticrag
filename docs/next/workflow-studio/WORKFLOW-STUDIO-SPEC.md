# Workflow Studio: redesign of Workflows

**Written:** 12 October 2026, against commit `dce4c49` · **By:** Claude (validator) · **For:** Jake to approve, Codex to build
**Reads with:** `docs/SPEC.md`, `docs/next/QA-REQUIREMENTS.md`, `docs/APP-DIRECTION-AND-WORKFLOWS.md`, `docs/WORKFLOWS.md`
**Reference prototype:** `prototype.html` in this folder. Open it in a browser. It shows the layout, interactions and motion described here. It is a picture of the intended result, not code to copy.

Place this folder at `docs/next/workflow-studio/` in the repository.

This supersedes `docs/COMPOSER-WORKFLOW-UX-PLAN.md` (Chat / Workflows tabs and the fixed step canvas). The composer image action from that plan stays.

---

## 0. The short version

Today, Workflows is a second tab next to Chat. It opens a page without the sidebar, and its "canvas" is a hard-coded column of four or five cards for two fixed templates. Nothing can be added, removed, moved, connected or branched. The server knows only those two templates.

This spec replaces it with **Workflow Studio**, a block-based builder in the style of Microsoft Copilot Studio:

1. **No tabs.** One app shell. The sidebar gains two destinations, **Workflows** and **Images**, under the search field. Chat goes back to being the whole screen. (§3)
2. **A Workflows home** with your workflows, templates and recent runs. (§4)
3. **The Studio:** a pan-and-zoom canvas. Drag blocks from a Blocks panel, or press **+** on any connection to insert one. Connect blocks by dragging between ports. Select a block to set it up in the Inspector. Branch with **If / else** and **Classify**. Autosave, undo, copy and paste, notes, tidy up, minimap. (§5)
4. **Run on the canvas.** Press **Run**: the canvas comes alive. Connections carry a moving pulse into the block that is working, the block shows live progress, finished blocks get a check, and the run pauses at approval blocks. Retry a failed block, run from any block, or test one block alone. (§9)
5. **Phones get an Outline editor**, a vertical list of the same graph with **+** between steps and settings in a bottom sheet, because canvas editing on a 390-pixel screen is poor. Running and watching work fully on the phone. (§10)
6. **A real graph engine** on the server: saved workflow definitions, a typed block registry, a deterministic step-at-a-time scheduler built on the existing durable runs, attempts, events and capacity lease. The two current templates become graphs, with a parity test proving they send byte-identical model requests. (§11)

Six checkpoints, WS-A to WS-F, each with a stop for review (§12). One new dependency, `@xyflow/react`, lazy-loaded so the initial bundle is unchanged (§14, decision J-W2). User-written prompts in blocks are a new kind of model call that `AGENTS.md` does not allow yet; Jake must approve that first (decision J-W1).

---

## 1. What is wrong with the current design

Viewed live at `https://jakes-mac-mini.tailc4d343.ts.net/workflows` and `/` in desktop Chrome on 12 October 2026, and read in source.

| # | Finding | Evidence | Effect |
|---|---|---|---|
| 1 | **Chat and Workflows are tabs.** The tab bar sits under the chat top bar on every chat screen. | `SectionTabs.tsx`, rendered in `LiveAppShell.tsx` line ~718 and `WorkflowsPage.tsx` | Chat, the main product, looks like one of two modes. The bar costs about 45 pixels of height on every chat. Jake: "slapstick". |
| 2 | **The Workflows page drops the app shell.** No sidebar, its own back arrow and title, then the same tabs again. | `router.tsx`: `/workflows` is a sibling of `LiveAppShell`, not a child | Two controls (back arrow and Chat tab) do the same thing. Leaving chat feels like leaving the app. |
| 3 | **Most of the screen is empty.** Content is a centered `max-w-4xl` (896 px) column; on a 1920-pixel window more than half is blank, and the canvas is about 370 px wide. | `WorkflowsPage.tsx` `mx-auto max-w-4xl` | The "canvas" is smaller than the settings panel. It reads as a form, not a builder. |
| 4 | **The canvas is a fixed list.** Steps are a literal array per template; arrows are `ArrowDown` icons between list items. | `WorkflowCanvas.tsx` lines 55–100 | No adding, removing, reordering, connecting, branching, pan or zoom. |
| 5 | **Only two workflows can exist.** | `WorkflowCreate.template: Literal["brief_images", "meeting_pack"]`; `templates.steps()` returns a fixed list | Every new workflow needs server code. |
| 6 | **Settings are hidden behind a panel enum.** | `StepPanel = "input" \| "model" \| "cleanup" \| "review" \| "images" \| "output"` | Settings cannot belong to a block instance; two blocks of the same kind are impossible. |
| 7 | **"Start workflow" is disabled with no reason.** | Disabled until a brief or recording and a model are chosen; nothing says so | Users do not know what is missing. |
| 8 | **Runs are a flat list below the fold.** | `WorkflowList` under the builder, latest 50 | No run page, no way to see a run on the graph. |
| 9 | **Steps are a list on the server too.** | `workflow_steps` keyed by `(run_id, position)`; `execute()` takes "the first step that is not complete" | Branches and joins cannot be expressed. |

What is solid and stays: durable runs with attempts and an event journal (`010_workflows.sql`), SSE replay with `Last-Event-ID`, idempotent `request_key`, one native invocation at a time with interactive preference (`capacity.py`), partial-output saving, owned-job cancellation, startup recovery, context-overflow rejection without truncation, the private-source local-connection rule, and the two frozen task prompts in `templates.py`. The new engine is built on all of these.

---

## 2. Goals and non-goals

**Goals**

1. Build any workflow from blocks, without server changes for each new one.
2. Feel like a premium creative tool: calm canvas, precise motion, nothing that looks like a form in a box.
3. One app shell. Workflows are a destination, not a mode.
4. Seeing a run on the graph is the main way to understand it.
5. Everything that works today keeps working, including saved runs.

**Non-goals for WS-A to WS-E** (WS-F lists the gated ones)

- Autonomous agents, tool calling, model voting, supervisors. Research stays shelved.
- External connectors (email, calendars, HTTP requests), code or shell blocks.
- Loops, schedules, triggers other than a manual Start.
- Multiple users, sharing, publishing to channels.
- Parallel execution. Branches are allowed; blocks still run one at a time.

---

## 3. Information architecture: no tabs

### 3.1 The shell

Every route renders inside the same shell: sidebar on the left, content on the right. Remove `SectionTabs.tsx` and every use of it.

**Sidebar, expanded (272 px, existing `--sidebar-w`):**

```
┌──────────────────────────────┐
│ ▣  Atelier               ✎   │  existing header: collapse, name, new chat
│ ┌──────────────────────────┐ │
│ │ ⌕  Search chats       ⌘K │ │  existing search field
│ └──────────────────────────┘ │
│  ⧉  Workflows                │  NEW nav row
│  ▢  Images                   │  NEW nav row
│                              │
│  FOLDERS                  +  │  existing
│  PREVIOUS 7 DAYS             │  existing history
│  …                           │
│ ──────────────────────────── │
│  ⚙  Settings                 │  existing footer
└──────────────────────────────┘
```

- Nav rows use the chat-row style: 40 px tall, 12 px horizontal padding, 16 px lucide icon (`Workflow`, `Images`), 14 px label. The active route gets the existing selected style (`border-l-2 border-brand bg-surface-3`).
- 8 px gap above and 12 px below the two rows. No section label; two rows do not need one.
- **Collapsed rail (56 px):** icon buttons for New chat, Search, Workflows, Images, then Settings at the bottom. Tooltips on hover.
- **Phone:** the existing drawer, with the same two rows.
- There is no "Chats" row. The history list is the chats, as in ChatGPT and Claude.

**Chat top bar:** unchanged apart from losing the tab bar under it.

### 3.2 Routes

| Route | Screen | Notes |
|---|---|---|
| `/`, `/c/:chatId` | Chat | Unchanged, minus tabs |
| `/workflows` | Workflows home (§4) | Inside the shell |
| `/workflows/:workflowId` | Studio (§5) | Sidebar collapses to the rail on entry; the previous state comes back on exit (`ui.collapsedBeforeStudio`) |
| `/workflows/:workflowId/runs/:runId` | Run view (§9.6) | Studio canvas, read-only, in run mode |
| `/workflows/runs` | All runs | Paged list |
| `/images` | Images gallery | Existing page, moved inside the shell |

All workflow routes stay lazy-loaded. The canvas library loads only with the Studio and run view.

### 3.3 Getting to workflows from chat

- **Command palette (⌘K), WS-A:** add a "Go to" group: Workflows, Images. **WS-D:** add "Run a workflow" items, one per workflow, opening its Run panel.
- **Composer "+" menu, WS-F (gated):** "Run a workflow…". The workflow's Start inputs appear inline in the composer; the run's results appear as a card in the chat. Gated because it adds a new message type to chat (`AGENTS.md`: never append notices to message content).
- **Carry the chat model:** a new workflow's default text model is the model selected in chat at the moment it is created (today's behavior, kept).

### 3.4 What is removed

- `SectionTabs.tsx` and its two uses.
- The standalone `WorkflowsPage` header (back arrow, title, connection label). The connection state moves to the Studio top bar as a dot (§5.1).
- `WorkflowCanvas.tsx` and `WorkflowForm` after WS-C. Until then they live at `/workflows/new?template=…` inside the shell (WS-A), so nothing is lost between checkpoints.

---

## 4. Workflows home

Desktop content: max width 1120 px, 32 px padding, centered in the content area (sidebar visible). Phone: 16 px padding, one column.

```
Workflows                                                     [ + New workflow ]
Chain models, search, images and recordings into repeatable steps.
Runs keep going on your Mac when you close the app.

YOUR WORKFLOWS
┌──────────────────────┐ ┌──────────────────────┐ ┌──────────────────────┐
│ ◧  Meeting pack      │ │ ◧  Product shots     │ │ ◧  Weekly research   │
│ Recording to summary │ │ Brief to three images│ │ Search, then a brief │
│ ▶─◆─✦─▤              │ │ ▶─✦─✓─▢─▤            │ │ ▶─⌕─✦─▤              │
│ ● Ran 2 h ago   Run ▸│ │ ○ Never run     Run ▸│ │ ● Failed 1 d   Run ▸ │
└──────────────────────┘ └──────────────────────┘ └──────────────────────┘

START FROM A TEMPLATE
[ Brief to images ] [ Recording to meeting pack ] [ Research a question ] [ Ask my files ] [ Summarize a document ] [ Blank ]

RECENT RUNS                                                              View all
● Meeting pack        Complete · 4 min · 2 outputs           Today 14:02      ›
◐ Product shots       Paused · Approve the prompt            Today 13:40      ›
✕ Weekly research     Failed at Search the web               Yesterday         ›
```

**Workflow card** (grid `repeat(auto-fill, minmax(300px, 1fr))`, gap 16 px, card height 168 px, radius `--radius-lg`, `bg-surface`, 1 px `--line`):
- 32 px icon tile with the workflow's icon (user-chosen, default `Workflow`).
- Name: 15 px, weight 500. Description: 13 px, `--text-2`, two-line clamp.
- **Block strip:** up to six 20 px icon tiles in category colors (§7.1), joined by 8 px lines; then "+N".
- Footer: status dot and "Ran 2 h ago" / "Never run" / "Running now" (live via SSE), and a **Run** ghost button. On pointer devices it appears on hover; on touch it is always visible.
- Hover: border `--line-strong`, `translateY(-1px)`, `--shadow-md`, 120 ms.
- Overflow menu (⋯): Rename, Duplicate, Export JSON, Delete. Delete archives the definition; its runs stay.

**Template chips:** 44 px tall pills with an icon. Clicking one creates a copy named after the template and opens the Studio, with a toast: "Created from template. Changes are yours." Templates are read-only; they are never edited in place.

**New workflow button:** a split button. Main click: Blank (Start and Save results, connected). Menu: the templates. WS-F (gated) adds "Describe it…".

**Recent runs:** 56 px rows, latest 10, live. Click opens the run view.

**Empty state** (no workflows yet): heading "Build your first workflow", one sentence, then the template chips large (88 px cards with a one-line description), and "Start blank". No illustration.

---

## 5. The Studio

### 5.1 Layout

Desktop at 1280 px and wider:

```
┌─rail─┬─────────────────────────── top bar, 52 px ──────────────────────────────┐
│ 56px │ ‹ Workflows / Meeting pack ✎   ● Saved          ⚠ 2   ↶ ↷   ⋯   [▶ Run]   │
│      ├──────────────┬────────────────────────────────────────────┬────────────────┤
│      │ BLOCKS       │                                            │ INSPECTOR      │
│      │ 264 px       │                canvas                      │ 360 px         │
│      │ ⌕ Search     │           (16 px dot grid)                 │ (--panel-w)    │
│      │ Inputs       │                                            │                │
│      │ AI           │                                            │ Setup │ Output │
│      │ Knowledge    │                                            │                │
│      │ Media        │                                            │                │
│      │ Logic        │                                            │                │
│      │ Review       │                                            │                │
│      │ Output       │ [− 100% +] [⤢] [⊞ Tidy]          [minimap] │                │
│      │ ▭ Note       │                                            │                │
└──────┴──────────────┴────────────────────────────────────────────┴────────────────┘
```

| Width | Blocks panel | Inspector | Canvas editing |
|---|---|---|---|
| ≥ 1280 | 264 px, docked | 360 px, docked; closes when nothing is selected and the run panel is not open | Full |
| 1024–1279 | 56 px icon strip (block icons with tooltips; click adds, drag drops) | 320 px, docked | Full |
| 768–1023 | Hidden; a floating **+** (56 px, bottom-left above the zoom controls) opens Quick add | Sheet from the right, 360 px, over the canvas | Full (touch) |
| < 768 | Hidden | Bottom sheet (vaul) | **Outline mode** by default (§10) |

**Top bar**, left to right:
- Back chevron and "Workflows" (link to home), "/", then the **workflow name**, editable inline (click turns it into an input; Enter saves; Escape cancels).
- **Save state** in 12 px `--text-3`: "Saved" · "Saving…" · "Couldn't save · Retry" (danger). A 6 px dot before it: success, brand pulsing, or danger. If the event stream is down, the dot is warning and the tooltip says "Reconnecting — accepted work continues on your Mac" (today's copy).
- **Problems chip** (only when there are problems): warning icon and count. Danger tone if any error. Opens the Problems panel (§5.8).
- Undo and Redo icon buttons.
- Overflow (⋯): Outline view / Canvas view, Workflow settings, Versions, View JSON, Export JSON, Import JSON, Duplicate, Delete.
- **Run** (primary, 36 px tall, play icon). With errors it stays clickable: the tooltip says "Fix {n} problems to run" and clicking opens Problems instead of doing nothing. ⌘↵ runs. While a run is active the button becomes **Running** (secondary, with the activity spinner) and reopens the Run panel.

### 5.2 Blocks panel

- Search field at the top ("Search blocks", `/` focuses it while the canvas has focus).
- Categories as collapsible groups, all expanded by default: **Inputs, AI, Knowledge, Media, Logic, Review, Output**. Each item is a 40 px row: 28 px icon tile in the category color, name, and a one-line description on hover as a tooltip after 400 ms.
- Unavailable blocks (for example Create images while the image engine is not installed) stay listed, dimmed to 50%, with the reason in the tooltip: "The image engine isn't ready. Settings › Images." They cannot be dragged.
- Footer: **Note** (adds a sticky note).
- **Add a block:** drag it onto the canvas, or drop it onto a connection to insert it there, or click it to add it below the selected block (connected) or at the viewport center (unconnected) if nothing is selected.

### 5.3 Canvas

- **Engine:** `@xyflow/react` (React Flow 12), controlled mode, custom node and edge components (§11.1).
- **Background:** dots, 16 px gap, 1 px, `--line`. Grid snap 16 px.
- **Layout direction:** top to bottom. Ports: one input at the top center, outputs at the bottom.
- **Navigation:** two-finger scroll pans; pinch or ⌘/Ctrl + scroll zooms; drag on empty canvas pans; Space + drag pans while a tool is active. Zoom range 25–175%. Shift + drag on empty canvas draws a selection box.
- **Controls** (bottom-left, one 36 px tall pill): zoom out, zoom level (click = 100%), zoom in, fit view, tidy up, Outline view, follow run (only during a run).
- **First-use hint:** a small pill at the top center, "Drag blocks from the left, or hover a connection and press +", shown until the first block is added from the Blocks panel (remembered per browser).
- **Minimap** (bottom-right, 168 × 112 px, toggle in ⋯ menu, on by default at ≥ 1280): nodes drawn as category-colored rectangles; viewport as a `--brand` outline.
- **Notes:** sticky notes in four tones (neutral, amber, rose, teal; §7.1 backgrounds), resizable, plain text with line breaks, 13 px. Not executed; not in the Outline.

### 5.4 Blocks on the canvas

Anatomy (fixed width 288 px; height grows with content, minimum 76 px):

```
            ○                      ← input port, 10 px
┌────────────────────────────────┐
│ ▣  Draft meeting pack       ⋯  │ ← 32 px icon tile, title 14/500, menu on hover
│    Generate text               │ ← kind, 11 px --text-3
│ qwen3.8 27B · temperature 0.6  │ ← summary, 12 px --text-2, two lines max
│ ‹pack.text›                    │ ← output chips, 11 px, first two then +N
└────────────────────────────────┘
        ○ True       ○ False       ← output ports; labelled only when there are several
```

- Card: `--radius-lg`, `bg-surface`, 1 px `--line`, `--shadow-sm`. Padding 12 px; 10 px gap between icon and text.
- Title is the block's name (user-editable; defaults to the block type, for example "Generate text"). Double-click edits it on the canvas.
- Summary comes from the block's configuration (§6 lists it per block). If required settings are missing, the summary says what is missing in `--warning` ("Choose a model").
- The Start block has no input port. Save results has no output port.
- Port: 10 px circle, 2 px `--line-strong` border, `bg-surface`. Hover or while connecting: 14 px, `--brand` border. Output port labels are 11 px pills 6 px under the port.

### 5.5 Connections

- **Draw:** drag from an output port to an input port. While dragging, compatible input ports glow `--brand`; incompatible ones dim to 40%. Dropping on a block's body connects to its input port.
- **Drop in empty space:** opens Quick add at the drop point; the chosen block is created there and connected.
- **Rules (checked in `isValidConnection` and again on the server):** no self-connections, no cycles ("Loops aren't supported yet"), one connection per output-port-to-input-port pair, types must be compatible (§6.2). An input port accepts many connections (a join).
- **Style:** smooth-step path, corner radius 12 px, 1.5 px `--line-strong`. Hover: `--text-3`. Selected: `--brand`, 2 px.
- **Insert:** hovering a connection shows a 24 px round **+** at its midpoint (always shown on touch at 32 px). Clicking it opens Quick add; the new block is inserted between the two blocks and every block below moves down by the new block's height plus 48 px (animated, §8).
- **Delete:** select a connection and press Delete, or use its hover ✕ next to the +.

### 5.6 Quick add

A `cmdk` popover (already a dependency), 320 px wide, max 420 px tall: search field, then blocks grouped by category with icon, name and one-line description. Arrow keys and Enter work; Escape closes. Opened by: **+** on a connection, dropping a connection in empty space, the floating + on tablet, `N` or `/` with the canvas focused, and right-click › Add block.

### 5.7 Inspector

Shown when one block is selected. With several selected it shows "3 blocks selected" and actions (Duplicate, Disable, Delete). With nothing selected it is closed; ⋯ › Workflow settings opens workflow-level settings in it.

**Header:** icon tile, editable title, kind label, ⋯ menu (Test this block, Run from here, Duplicate, Disable, Delete).

**Tabs:** **Setup** and **Output**. Output shows this block's result from the latest run (text with copy, images as thumbnails, sources as a list), or "Run the workflow or test this block to see its output."

**Setup** contents are listed per block in §6. Shared parts:
- **Reference name** (collapsed under "Advanced"): the key other blocks use, for example `pack`. Lowercase letters, digits and underscores; unique; renaming updates every reference in the workflow.
- **Connections** section at the bottom: "Gets input from" and "Sends output to", each a list with remove buttons and an "Add connection" select. This is the keyboard and screen-reader way to wire blocks, because dragging ports is pointer-only.
- **Produces:** the block's output fields, each with a copy-reference button (`{{pack.text}}`).

**Workflow settings** (nothing selected): name, description, icon picker (12 lucide icons), **Default text model** (AI blocks set to "Workflow default" use it; changing it once changes them all), and "Keep test runs for 7 days" (on).

### 5.8 Variables and the {x} picker

- Syntax: `{{key.field}}`. Only references, no expressions. One optional filter: `{{key.field | tagged:name}}` (§11.4).
- Any text field that accepts variables shows an `{x}` button on its right edge; typing `{{` also opens the picker.
- The picker lists **only upstream blocks** (ancestors), nearest first, each with its fields, type badges and the last run's value as a one-line preview.
- References render as chips: a mirrored highlight layer behind a normal `<textarea>` gives each `{{…}}` span a `--brand-soft` background and `--brand` text. Editing stays plain text (no `contenteditable`), so copy, paste, undo and IME input behave normally.
- An unknown or non-upstream reference is underlined in `--danger` and listed in Problems.

### 5.9 Problems (validation)

Checks run on every change in the browser (`graph.ts`) and on the server before a run (`graph.py`), from the same rule list:

| Rule | Level | Message |
|---|---|---|
| Exactly one Start | Error | "A workflow needs exactly one Start." |
| Every block reachable from Start | Error | "‘{title}’ isn't connected to Start." |
| No cycles | Error | "Loops aren't supported yet." |
| Required settings present | Error | "‘{title}’ needs a model." (per field) |
| References point to upstream blocks | Error | "‘{title}’ uses {{x.y}}, which comes later or doesn't exist." |
| Types compatible across connections | Error | "‘{title}’ needs audio, but ‘{source}’ gives text." |
| Chosen model or engine available | Error | "The model ‘{name}’ isn't available." |
| Private sources use a local connection | Error | "Recordings, documents and files can only go to a model on this Mac." (today's rule, generalized) |
| Branch output not connected | Warning | "The ‘False’ path of ‘{title}’ ends here." |
| Reference may be empty on some paths | Warning | "{{x.y}} is empty when ‘{title}’ takes another path." (Not raised for `tagged` references, which are designed to drop out when empty.) |
| No Save results block | Warning | "This workflow doesn't save anything." |
| A block is disabled | Info | "‘{title}’ is skipped while disabled." |

The Problems panel lists them grouped by block. Clicking one selects the block, zooms to it (320 ms) and focuses the field. On the canvas, a block with an error gets a 6 px `--danger` dot on its top-right corner; with only warnings, `--warning`.

### 5.10 Saving, undo, versions, conflicts

- **Autosave** 800 ms after the last change (drags count when they end; typing counts after 500 ms of quiet). `PUT` with the definition's `version`. No Save button.
- **Undo / Redo:** ⌘Z / ⇧⌘Z, 100 steps, in the Studio store. A drag is one step; a burst of typing in one field is one step.
- **Conflict:** if the server answers 409 (edited on the phone meanwhile), show a banner above the canvas: "This workflow changed on another device." **Load latest** / **Keep mine** (sends again with `force`).
- **Versions:** every run stores an immutable snapshot of the graph it ran (by hash). ⋯ › Versions lists snapshots with date and the runs that used them; **Restore** loads one as the current draft (undoable). "Name this version" adds a label. No publish step: this is a single-user app.
- **Offline:** if a save fails, keep the draft in memory and retry on reconnect; leaving the page while unsaved shows the browser's leave warning.

### 5.11 Interaction reference

| Action | Pointer | Keyboard | Touch (tablet) |
|---|---|---|---|
| Add block | Drag from Blocks; click in Blocks; + on a connection | `N` or `/` opens Quick add; Enter inserts below selection | Floating +; + on a connection |
| Select | Click | Tab / Shift+Tab between blocks; ↓ ↑ follow connections; ← → move between branches | Tap |
| Multi-select | Shift+click; Shift+drag box | ⌘A | Long-press then tap others |
| Move | Drag (16 px snap) | Arrow keys move 16 px with ⌥ held | Drag |
| Connect | Drag port to port | Inspector › Connections | Drag port to port |
| Rename | Double-click title | F2 | Inspector |
| Duplicate | ⋯ › Duplicate | ⌘D | ⋯ |
| Copy / paste | Context menu | ⌘C / ⌘V (pastes at pointer, else offset 32 px) | ⋯ |
| Delete | ⋯ › Delete | Delete / Backspace | ⋯ |
| Disable | ⋯ › Disable | ⌘/ | ⋯ |
| Undo / redo | Top bar | ⌘Z / ⇧⌘Z | Top bar |
| Fit view | Controls | `F`, ⇧1 | Controls |
| Zoom 100% | Click zoom level | ⌘0 | Controls |
| Run | Run | ⌘↵ | Run |
| Close menus, clear selection | Click empty canvas | Escape | Tap empty canvas |

**Deleting a block in the middle of a chain** reconnects its single input to its single output (Copilot Studio behavior), as one undo step. With several inputs or outputs, connections are removed and Problems shows what is left dangling.

**Paste** gives copied blocks new ids and unique keys (`draft` becomes `draft_2`) and rewrites references among the pasted blocks to the new keys. References to blocks outside the pasted set are kept.

**Right-click** on a block: Test this block, Run from here, Rename, Duplicate, Copy, Disable, Delete. On empty canvas: Add block, Paste, Add note, Tidy up, Fit view.

**Tidy up** lays blocks out in layers from Start (§11.1, `layout()`), centers branches under their parent, keeps notes where they are relative to their nearest block, and animates to the result (320 ms). One undo step.

---

## 6. Blocks

### 6.1 Catalog

Phase = the checkpoint that ships the block. Every block uses an engine that exists today; none adds a runtime.

| Block (kind) | Category | Phase | What it does | Ports | Model call |
|---|---|---|---|---|---|
| Start (`start`) | Inputs | WS-B | Defines the run's inputs | out | No |
| Generate text (`generate`) | AI | WS-B | One model call with your instructions and prompt | in, out | Yes (J-W1) |
| Classify (`classify`) | AI | WS-E | Picks one of your categories for some text; one output per category | in, one per category, `other` | Yes (J-W1) |
| Search the web (`web_search`) | Knowledge | WS-E | Runs your query through the existing search providers and page fetch; returns numbered sources | in, out | No |
| Search my files (`library_search`) | Knowledge | WS-E | Retrieves passages from your Library | in, out | Embedding only |
| Read a document (`read_document`) | Knowledge | WS-E | Extracts text from a PDF or Word file | in, out | No |
| Transcribe recording (`transcribe`) | Media | WS-B | Existing transcription engine | in, out | No (engine) |
| Clean up transcript (`clean_transcript`) | Media | WS-B | Existing guarded clean-up; the original stays | in, out | Existing clean-up call |
| Create images (`generate_image`) | Media | WS-B | Existing FLUX.2 klein worker, 1–3 images | in, out | No (engine) |
| If / else (`condition`) | Logic | WS-E | Compares values; `true` or `false` | in, true, false | No |
| Compose text (`compose`) | Logic | WS-E | Fills a text template from variables | in, out | No |
| Approve or edit (`review`) | Review | WS-B | Pauses; you approve, edit or reject | in, approved, rejected | No |
| Pick favorites (`pick`) | Review | WS-D | Pauses; you choose among images or texts | in, out | No |
| Save results (`output`) | Output | WS-B | Marks what the run keeps and how it exports | in | No |
| Note (`note`) | — | WS-C | Canvas annotation | — | — |

### 6.2 Types

Output fields are typed. A connection is compatible when every required input of the target block can be satisfied by some upstream field of the right type. Types: `text`, `markdown`, `number`, `boolean`, `json`, `audio`, `document`, `image`, `image_list`, `transcript` (text with timestamps and segments), `sources` (numbered list with titles, links or file names, and passage text). `markdown` is accepted wherever `text` is.

### 6.3 Each block

For each: **Setup** fields (★ = required), **Summary** shown on the canvas, **Produces** (output fields), **Runs** (how the engine executes it).

**Start**
- Setup: **Inputs**, a list of fields, each with label ★, reference name, type (Short text, Long text, Number, Yes/No, Choice, Recording, Document, Image), required toggle, help text, default value. Recording fields also allow choosing a saved recording at run time (today's behavior). Up to 12 fields.
- Summary: "Inputs: Brief, Count" or "No inputs".
- Produces: one field per input, named by its reference name (`start.brief`).
- Runs: no work. Files are uploaded through the existing attachments endpoint when the run starts; the run stores attachment ids.

**Generate text**
- Setup: **Model** ★ ("Workflow default" or a chat-capable model from `/models`, with the existing "tested with images" mark where it applies); **Instructions** (system message, variables allowed); **Prompt** ★ (user message, variables allowed); **Output format**: Text (default) · Markdown · JSON fields (a small field list: name, type, description; sent as `json_schema`, which the Ollama adapter already passes as `format`); **Thinking** (only when the model reports `reasoning` options; values from the runtime, never inferred from names); **Optional overrides** collapsed: temperature, top-p, top-k, output limit, seed. Empty fields send nothing (existing rule: overrides only what you enter; saved model defaults, then runtime defaults). **Preview prompt** button shows exactly the messages that would be sent, with the latest run's values filled in.
- Summary: model short name, then "· temperature 0.6" when set, then "· JSON" when JSON.
- Produces: `text` (markdown), and one field per JSON field when JSON.
- Runs: the existing `Workflows.text()` path, generalized: resolve model and params; build `[system: instructions][user: prompt]` with variables rendered (§11.4); context-overflow check with `tokens_per_char` (reject, never truncate); stream with `background=True` under the capacity lease; save partial text at most once per second (today's rate); require `Finish.reason == "stop"`; record messages, params and prompt hash on the attempt.

**Classify** (WS-E)
- Setup: **Model** ★; **Text to classify** ★ (variables); **Categories** ★ 2–8, each a label and a one-line description; "Other" is always present.
- Summary: "3 categories · qwen3.8".
- Produces: `category` (text), `reason` (text, one sentence).
- Runs: one model call with an app-authored prompt (frozen and hashed, G-8; eval in WS-E §13.3) and a `json_schema` restricting `category` to the category ids plus `other`. The taken port is the chosen category.

**Search the web** (WS-E)
- Setup: **Query** ★ (variables); **Results** 3–10 (default 5); **Read pages** on (fetch and extract) or off (snippets only).
- Summary: "5 results · reads pages".
- Produces: `sources` (sources), `context` (text: numbered sources ready to put in a prompt), `count` (number).
- Runs: a new `search_sources(query, limit, fetch)` service extracted from `search/pipeline.py` that returns ranked, fetched, extracted sources **without** the planner or answer call. Chat search must not change (G-9 offline replay equal or better).

**Search my files** (WS-E)
- Setup: **Query** ★; **Collections** (all, or chosen); **Passages** 3–20 (default 8).
- Summary: "8 passages · All files".
- Produces: `sources`, `context`, `count`.
- Runs: existing `library/retrieve.retrieve()` with a budget derived from the passage count. Private source (§5.9 local rule).

**Read a document** (WS-E)
- Setup: **Document** ★ (a Document input from Start, or a variable).
- Produces: `text`, `pages` (number), `filename` (text).
- Runs: existing `documents/extract`. Private source.

**Transcribe recording**
- Setup: **Recording** ★ (a Recording input from Start); **Use glossary** (existing setting, shown read-only with a link to Settings).
- Summary: "From Start · Recording".
- Produces: `transcript` (transcript), `text`, `timestamped_text`, `segments` (json), `filename`.
- Runs: existing `perform()` "transcribe" branch, unchanged: start or join the attachment's transcription, shield it, save the original source. Private source.

**Clean up transcript**
- Setup: **Transcript** ★ (from a Transcribe block); **Model** ★ (uses the existing transcription clean-up settings; overrides are not allowed, as today).
- Summary: "Original kept · qwen3.8".
- Produces: `text` (cleaned).
- Runs: existing "cleanup" branch, including the changed-source check. On a rejected clean-up the block fails with today's message, and the Run panel offers **Retry** or **Continue without clean-up** (marks the block skipped; downstream `{{clean.text}}` resolves empty).

**Create images**
- Setup: **Prompt** ★ (variables; at most 4,000 characters after filling); **Images** 1 · 2 · 3; **Seeds** Automatic (default) or Advanced (one integer per image, 0–4,294,967,295).
- Summary: "2 images · FLUX.2 klein".
- Produces: `images` (image_list), `first` (image).
- Runs: existing "image" branch, one image job per image in order, request key `workflow-{run}-{node}-{index}-{attempt}`. Automatic seeds are resolved once at run submission and stored in the run's graph snapshot, so a retried request is identical (today's rule). If the filled prompt exceeds 4,000 characters, the run pauses here with the Approve-or-edit card (today's behavior for long drafts).

**If / else** (WS-E)
- Setup: **Match** all / any; **Rules** 1–5, each: value ★ (variable), operator (is empty, is not empty, contains, does not contain, equals, does not equal, longer than N characters, greater than, less than), comparison value.
- Summary: "{{draft.text}} contains ‘urgent’".
- Produces: nothing new; takes `true` or `false`.

**Compose text** (WS-E)
- Setup: **Template** ★ (variables).
- Produces: `text`.
- Runs: render only; no model.

**Approve or edit**
- Setup: **Show** ★ (a text variable to review, for example `{{draft.text}}`); **Allow editing** on; **Message** (optional, shown above the text, for example "Check the prompt before images are made").
- Summary: "Review {{draft.text}} · editable".
- Produces: `value` (the approved text, edited or not), `edited` (boolean).
- Runs: the run state becomes `paused`, stage "Approve ‘{title}’". `POST /runs/{id}/decision` with `approve` (and optional edited value) takes `approved`; `reject` takes `rejected`. A `rejected` port with no connection ends that path.

**Pick favorites** (WS-D)
- Setup: **From** ★ (an image_list or several text fields); **Pick** one · up to N.
- Produces: `chosen` (image_list or text).
- Runs: pauses like Approve or edit; the Run panel shows the images in a grid to choose from.

**Save results**
- Setup: **Include** ★ (a list of variables, each with a label; default: every leaf block's main output); **Formats**: Markdown, JSON (images are always saved as PNG through the existing image storage); **Include original sources** (on when a transcript, document or search is upstream).
- Summary: "Markdown, JSON · 2 items".
- Produces: nothing.
- Runs: records the output manifest on the run; the run page and export use it. A run can have several Save results blocks; each appears as its own section.

---

## 7. Visual design

The existing theme stays: Geist for UI, Newsreader for long answers, cobalt `--brand`, the warm neutrals, existing radii and shadows. The Studio adds category tones and run states.

### 7.1 New tokens

Add to `globals.css` in both themes. Each category has a **tone** (icon and accents) and a **tint** (icon tile background). Tones meet 3:1 against their tint and against `--surface` (WCAG 1.4.11, non-text). Extend the contrast script to cover them.

| Token | Light | Dark | Used for |
|---|---|---|---|
| `--cat-input` / `--cat-input-tint` | `#57544e` / `#f0efea` | `#b4b0a8` / `#2b2b29` | Start |
| `--cat-ai` / `-tint` | `#2f5bea` / `#e8eefe` | `#7c9dff` / `#24304f` | Generate text, Classify |
| `--cat-knowledge` / `-tint` | `#0f766e` / `#dff2ee` | `#5cc8bb` / `#1b3330` | Search the web, Search my files, Read a document |
| `--cat-media` / `-tint` | `#7c3aed` / `#f1ebfe` | `#b49bff` / `#2e2645` | Transcribe, Clean up, Create images |
| `--cat-logic` / `-tint` | `#8a5a00` / `#fbf0dc` | `#f2b455` / `#3a2f1a` | If / else, Compose text |
| `--cat-review` / `-tint` | `#be123c` / `#fde8ec` | `#ff8fa3` / `#3d2229` | Approve or edit, Pick favorites |
| `--cat-output` / `-tint` | `#1d7a4b` / `#e3f3ea` | `#5fd394` / `#1c3527` | Save results |
| `--note-amber` · `--note-rose` · `--note-teal` · `--note-neutral` | `#fbf0dc` · `#fde8ec` · `#dff2ee` · `#f0efea` | `#3a2f1a` · `#3d2229` · `#1b3330` · `#2b2b29` | Note backgrounds |
| `--canvas-dot` | `var(--line)` | `var(--line)` | Grid dots |
| `--ring-select` | `0 0 0 2px var(--brand), 0 0 0 6px var(--brand-soft)` | same | Selected block |

Colors appear only in the icon tile, port glow and run states. Block cards stay neutral surfaces, so a large graph stays calm.

### 7.2 Icons (lucide)

Start `Play` · Generate text `Sparkles` · Classify `Split` · Search the web `Globe` · Search my files `Library` · Read a document `FileText` · Transcribe `AudioLines` · Clean up `Eraser` · Create images `ImagePlus` · If / else `GitBranch` · Compose text `TextCursorInput` · Approve or edit `UserCheck` · Pick favorites `Star` · Save results `Save` · Note `StickyNote`. Workflow default icon `Workflow`.

### 7.3 Run states on a block

| State | Card | Badge (20 px, top-right, −6 px offset) | Summary line |
|---|---|---|---|
| Waiting | Opacity 0.72 | — | Unchanged |
| Running | Sweep ring (§8.3), full opacity | — | Live progress in `--brand`: "Transcribing · 42%", "Writing · 312 tokens", "Image 2 of 3 · step 6 of 8" |
| Paused | 2 px `--warning` ring, breathing | `Pause` on `--warning` | "Waiting for you" |
| Complete | Normal | `Check` on `--success` | "Done in 14 s" |
| Reused | Normal | `RotateCcw` on `--surface-3` | "Reused from earlier run" |
| Failed | 2 px `--danger` ring | `!` on `--danger` | The error, one line |
| Skipped | Opacity 0.45, dashed 1 px border | `Minus` on `--surface-3` | "Skipped" |
| Cancelled | Opacity 0.6 | `X` on `--surface-3` | "Cancelled" |
| Disabled (editing) | Opacity 0.5, dashed border | — | "Disabled" |

Connections during a run: **active** (into the running block) = 2 px `--brand` with the moving dash; **done** = 1.5 px `--brand` at 55% opacity; **not taken** = 1 px dashed `--line-strong` at 45%.

### 7.4 Copy

Plain and short, sentence case. Name things by what they do ("Search the web", not "Web retrieval node"). Never say "node", "graph", "DAG" or "execute" in the interface: say block, workflow, run. Errors say what happened and what to do. Appendix B has the copy deck.

---

## 8. Motion

Phase 4 rules apply: CSS only, small surfaces at most 200 ms, large surfaces at most 320 ms, all keyframes in `web/src/styles/motion.css`, both reduced-motion triggers remove every animation and transition (G-13). Looping run indicators are activity indicators, like the existing `breathe` (1.5 s) and `activity-spin` (1 s).

### 8.1 Choreography

| Moment | What moves | Duration | Easing | Reduced motion |
|---|---|---|---|---|
| Studio opens | Canvas fades in; blocks rise 4 px and fade, staggered 24 ms, first 12 only | 200 ms each | `--ease-out` | Instant |
| Panel opens or closes (Blocks, Inspector, Run) | `translateX(±16px)` and opacity | 200 ms (sheet on tablet: 320 ms) | `--ease-sheet` | Instant |
| Drag from Blocks | Ghost card under the pointer, scale 1.02, `--shadow-lg`, no lag | — | — | No scale |
| Block dropped | Scale 0.96 → 1, opacity 0 → 1 | 120 ms | `--ease-pop` | Instant |
| Block hover | Border color | 120 ms | `--ease` | Instant |
| Block selected | Ring in (`--ring-select`) | 120 ms | `--ease` | Instant |
| Port hover | 10 → 14 px | 80 ms | `--ease` | Instant |
| Connection drawn | Path draws in (`stroke-dasharray` from 0 to length) | 200 ms | `--ease-out` | Instant |
| Insert on a connection | Blocks below slide down | 200 ms | `--ease-out` | Instant |
| Delete | Opacity 0, scale 0.96 | 120 ms | `--ease-in` | Instant |
| Tidy up, Restore version | Blocks move to new positions | 320 ms | `--ease-sheet` | Instant |
| Fit view, zoom to problem, follow run | Viewport transform (React Flow `duration`) | 320 ms | built-in | 0 ms |
| Run pressed | Play icon becomes the activity spinner; Start pulses once (ring scale 1 → 1.06, fade) | 200 ms | `--ease-out` | Spinner static |
| Connection active | Dash flows toward the running block | 800 ms loop | linear | Static solid `--brand` |
| Block running | Sweep ring rotates | 1.6 s loop | linear | Static 2 px `--brand` ring |
| Block completes | Badge pops in (scale 0.6 → 1) | 200 ms | `--ease-pop` | Instant |
| Path not taken | Fades to 45%, becomes dashed | 200 ms | `--ease` | Instant |
| Paused | Warning ring breathes (`breathe`) | 1.5 s loop | `--ease` | Static |
| Text streaming in Run panel | Existing rAF batching and reveal | existing | existing | existing |

No shaking on errors, no confetti, no bounce beyond `--ease-pop`.

### 8.2 Following the run

During a run the viewport pans to keep the running block in view (320 ms), unless the user panned or zoomed in the last 5 seconds. The follow button in the controls shows the state and turns following back on.

### 8.3 How to build the two loops in CSS

**Sweep ring** (transform only, so it passes the motion guard):

```css
/* motion.css */
@keyframes wf-sweep { to { transform: rotate(1turn); } }
@keyframes wf-flow  { to { stroke-dashoffset: -12; } }

/* Block wrapper: overflow hidden, 1.5 px padding shows the ring. */
.wf-block[data-run="running"] { padding: 1.5px; overflow: hidden; }
.wf-block[data-run="running"]::before {
  content: ""; position: absolute; inset: -50%;      /* square larger than the card's diagonal */
  aspect-ratio: 1; margin: auto;
  background: conic-gradient(from 0deg, transparent 0 62%, var(--brand) 82%, transparent 100%);
  animation: wf-sweep 1.6s linear infinite;
}
.wf-block-body { position: relative; background: var(--surface); border-radius: calc(var(--radius-lg) - 1.5px); }

.wf-edge[data-run="active"] path {
  stroke: var(--brand); stroke-width: 2; stroke-dasharray: 6 6;
  animation: wf-flow 800ms linear infinite;
}
```

**Tooling change:** add `stroke-dashoffset` to `ALLOWED` in `scripts/check_motion.py`. It is the only way to animate a dash along a path in CSS. Do not use React Flow's built-in `animated` edges (its keyframes live in its own stylesheet and would bypass the guard).

**Moving blocks** (tidy up, insert, restore): add the class `wf-arranging` to the canvas for 320 ms, with `.wf-arranging .react-flow__node { transition: transform var(--dur-slow) var(--ease-sheet); }`. Never leave a transform transition on during dragging.

---

## 9. Running

### 9.1 Starting a run

- **Run** opens the **Run panel** in the right column (replacing the Inspector; the Inspector returns when the run panel is closed).
- If Start has inputs, the panel shows them as a form, prefilled from the last run. Recording fields offer upload or a saved recording; Document and Image fields offer upload. Primary button: **Run workflow**.
- On submit: client creates `request_key` once, uploads files, then `POST /defs/{id}/runs`. On an uncertain response, retry with the same body and key (today's rule). The server validates, snapshots the graph, resolves automatic seeds, creates all step rows and answers 202.
- The canvas enters run mode (§7.3, §8.1).

### 9.2 The Run panel during a run

```
RUN  ·  Meeting pack                          ◼ Cancel
Started 14:02 · 1 min 12 s

✓  Start                                        0 s
✓  Transcribe recording                        48 s
◐  Draft meeting pack       Writing · 312 tokens
   │ ## Summary
   │ The team agreed to move the launch to …     ← live text, Newsreader 15 px
○  Save results

[ View original transcript ]
```

- A timeline of the blocks in run order, with state icon, title, duration or live progress. Clicking an entry selects the block on the canvas and shows its output.
- The running text block streams its text (existing streaming row behavior and batching).
- **Cancel** (ghost, danger text) sends cancel; the run shows "Cancelling…" until the engine confirms (today's rule).

### 9.3 Approvals

When a run pauses at Approve or edit, the panel shows a card: the message, the text in an editable `Textarea` (if editing is allowed), and **Approve** (primary) and **Reject** (ghost). A sonner toast also appears if the user is elsewhere in the app: "Meeting pack is waiting for you. Open". The Workflows sidebar row shows a 6 px `--warning` dot while any run is paused.

### 9.4 Failures and retry

- The failed block gets its ring and badge; the panel shows the error and **Retry block** (primary) and, when it applies, **Continue without it** (skips it, for optional blocks such as Clean up transcript).
- After an interrupted server, the run shows **Retry unfinished blocks** (today's "Retry unfinished steps"); completed outputs are reused.

### 9.5 Run from here and Test this block

- **Run from here** (block menu): creates a new run that reuses the saved outputs of every block that is not downstream of this one, from the latest complete or failed run, provided those blocks' settings are unchanged (compared by a per-block config hash); runs this block and everything after it. Reused blocks show the Reused badge. If no earlier run qualifies, it is disabled with the reason.
- **Test this block**: runs only this block. Its inputs come from the latest run's upstream outputs; if there is none, the panel asks for sample values for each referenced variable. Test runs are stored with `mode = "test"`, hidden from Recent runs, removed after 7 days (setting), and shown in the block's Output tab.

### 9.6 Run view and history

- `/workflows/:id/runs/:runId` shows the canvas as it was for that run (its graph snapshot), read-only, with run states, and the Run panel on the right showing the timeline and results. A banner says "Viewing a run from 12 Oct, 14:02. Edit workflow" when the snapshot differs from the current draft.
- **Results** (bottom of the panel when complete): one section per Save results block, with each item rendered (Markdown in Newsreader, images as a grid with the existing save/share dialog, JSON in a code block), **Export** (Markdown / JSON through the existing cancellable save dialog), and for transcripts **View original transcript** (existing dialog).
- Meeting packs and other text from private sources keep the "draft for review" label (today's rule).
- `/workflows/runs` lists all runs, filterable by workflow and state, paged 50 at a time (today's page shows only the latest 50).

---

## 10. Phone and tablet

### 10.1 Outline mode (phone default)

The same graph as a vertical list. It is also the accessible alternative on desktop (⋯ › Outline view).

```
‹  Meeting pack                 ⋯   [▶ Run]
──────────────────────────────────────────
 ▶  Start                               ›
    Inputs: Recording
          │
          ⊕                                 ← 44 px insert target
          │
 ◆  Transcribe recording                ›
    From Start · Recording
          │
          ⊕
          │
 ✦  Draft meeting pack                  ›
    qwen3.8 27B
          │
 ⑂  If / else                           ›
    {{pack.text}} contains "action"
    ┆ IF TRUE
    ┆   ▤  Save results                 ›
    ┆ IF FALSE
    ┆   ⊕  Add a block
```

- Rows: 64 px minimum, icon tile, title, summary, chevron. In run mode the right side shows state and progress instead of the chevron.
- Branches render as labeled lanes ("If true", "If false", category names) with a 1 px dashed guide 16 px in. Where lanes join again, the list continues at the outer level under a small "Then" label.
- Tapping a row opens the Inspector in a vaul bottom sheet (snap points 60% and 95%). Tapping ⊕ opens Quick add as a bottom sheet.
- Reordering: the row menu has **Move up** and **Move down** within a straight chain. No drag-and-drop on phones.
- Graphs that cannot be drawn as nested lanes (a join of lanes from different branch blocks) show a notice: "Part of this workflow is easier to change on a larger screen." Settings still open; structure changes there are disabled.
- **Canvas view** on the phone is available from ⋯ and is read-only: pinch to zoom, drag to pan, and the full run animation. It is for watching.

### 10.2 Running on the phone

The Run panel becomes a full-height sheet. Approvals, cancel, retry, results, export and share work as on desktop. This is the main phone use: start a run, put the phone away, approve when the toast or the sidebar dot says so.

### 10.3 Tablet (768–1023)

Canvas editing with touch, as in the table in §5.1. Quick add replaces the Blocks panel. Inspector and Run panel are 360 px sheets from the right.

---

## 11. Architecture

### 11.1 Frontend

**New dependency (J-W2):** `@xyflow/react`, exact version pinned (latest 12.x that is at least two weeks old at install time), MIT license. Import only `@xyflow/react/dist/base.css` and style everything with tokens. It must load only in the lazy Studio and run-view chunks; the initial bundle must not grow (G-4).

Why not hand-build it: pan, zoom, pinch, hit-testing, port dragging, selection boxes, viewport culling and keyboard focus on nodes are a large surface to get right on both Chromium and WebKit. React Flow is the standard for this, runs on React 19, and is what this design assumes.

**Files** (all new unless noted; follow the existing `components/<area>/` convention):

```
web/src/components/workflows/
  home/WorkflowsHome.tsx          /workflows
  home/WorkflowCard.tsx
  home/RunsList.tsx               recent and all runs
  studio/Studio.tsx               route component; layout grid; loads definition
  studio/StudioTopBar.tsx
  studio/BlocksPanel.tsx
  studio/Canvas.tsx               <ReactFlow> wrapper, controlled
  studio/BlockNode.tsx            one node component for every kind, driven by the registry
  studio/NoteNode.tsx
  studio/FlowEdge.tsx             smooth-step edge, + insert button, run states
  studio/QuickAdd.tsx             cmdk popover / sheet
  studio/Inspector.tsx            header, tabs, shared sections
  studio/inspectors/*.tsx         one Setup component per kind
  studio/VariableField.tsx        textarea + highlight layer + {x} picker
  studio/RunPanel.tsx
  studio/ProblemsPanel.tsx
  studio/VersionsPanel.tsx
  studio/Outline.tsx              phone editor and accessible view
  studio/store.ts                 zustand: doc, selection, history, save state
  studio/graph.ts                 pure: validate, topo, ancestors, layout, rename, paste, skip preview
  studio/registry.ts              kind → icon, category, label, description, ports(config), outputs(config), summary(config), defaults, inspector
  studio/run.ts                   subscribe to /api/workflows/stream; node states per run
  runs/RunPage.tsx                /workflows/:id/runs/:runId
web/src/components/app/Sidebar.tsx        changed: nav rows
web/src/components/app/LiveAppShell.tsx   changed: no SectionTabs; shell hosts workflow routes
web/src/router.tsx                        changed: workflow routes become shell children
```

**State.** `store.ts` holds the definition document (`GraphDoc`, §11.2), selection, viewport, the undo stack (immutable snapshots, capped at 100), dirty flag and save state. React Flow is fed `nodes` and `edges` derived from the doc; its change callbacks are applied through store actions so undo, autosave and validation see every change. Server data (definitions list, runs) uses TanStack Query as elsewhere; live run state comes from SSE batched with `requestAnimationFrame` (existing pattern in `WorkflowsPage.tsx`).

**React Flow settings:** `nodeTypes={{ block: BlockNode, note: NoteNode }}`, `edgeTypes={{ flow: FlowEdge }}`, `snapToGrid`, `snapGrid={[16, 16]}`, `minZoom={0.25}`, `maxZoom={1.75}`, `panOnScroll`, `zoomOnPinch`, `selectionOnDrag={false}` with Shift for box selection, `deleteKeyCode={null}` (the store handles Delete for auto-heal and undo), `isValidConnection` from `graph.ts`, `onlyRenderVisibleElements` above 60 blocks, `fitView` on first open. Attribution: the MIT license allows hiding it; React Flow asks non-subscribers to keep it. Jake's call (J-W2).

**Drag from Blocks:** HTML5 drag-and-drop with `dataTransfer` type `application/x-atelier-block`; on drop use `screenToFlowPosition`. Dropping onto an edge (hit test within 12 px of its path) inserts. The Blocks panel is not shown on touch layouts, so HTML5 DnD's lack of touch support does not matter.

**`graph.ts` functions** (pure, unit-tested with Vitest, mirrored by `graph.py` on the server with shared fixtures):
- `validate(doc, catalog, models) → Issue[]` (§5.9 rules).
- `topoOrder(doc) → nodeId[]`: Kahn's algorithm; ties broken by `position.y`, then `position.x`, then id. The same order is the step `position` on the server.
- `ancestors(doc, nodeId) → Set<nodeId>`.
- `layout(doc) → positions`: layer = longest path from Start; within a layer, order by the mean x of parents (barycenter), then id; x spacing 288 + 64 px; y spacing = tallest block in the layer + 72 px; branch children centered under their parent. Deterministic.
- `renameKey(doc, old, new)`: rewrites every `{{old.` reference.
- `pasteRemap(fragment, existingKeys)`.
- `outlineTree(doc) → OutlineNode | null`: series-parallel decomposition for the phone; returns null for parts that cannot nest.

**Accessibility.** Blocks are focusable with labels like "Generate text block ‘Draft meeting pack’, 3 of 5, gets input from Transcribe recording". The Inspector's Connections section gives full wiring without a pointer. Outline view is the screen-reader view. Axe zero serious/critical on Home, Studio (empty, populated, selected, running, paused, failed), Outline and run view, both themes, 390 and 1440 (G-5).

### 11.2 The workflow definition

Stored as JSON in `workflow_defs.graph_json`, validated by Pydantic on the server (discriminated union on `kind`, a config model per kind) and exported through OpenAPI to `api-types.ts` (existing pipeline).

```ts
type GraphDoc = {
  schema: "atelier.workflow/1";
  nodes: GraphNode[];
  edges: GraphEdge[];
  notes: GraphNote[];
  viewport?: { x: number; y: number; zoom: number };
  settings: { default_model?: ModelRef; keep_test_runs_days: number };
};
type GraphNode = {
  id: string;               // "n_" + 10 chars, stable
  kind: BlockKind;          // "start" | "generate" | ... (§6.1)
  key: string;              // reference name, ^[a-z][a-z0-9_]{0,31}$, unique
  title: string;            // display name, ≤ 80 chars
  position: { x: number; y: number };
  disabled?: boolean;
  config: BlockConfig;      // per-kind, §6.3
};
type GraphEdge = { id: string; source: string; source_port: string; target: string; target_port: "in" };
type GraphNote = { id: string; position: { x: number; y: number }; size: { w: number; h: number };
                   tone: "neutral" | "amber" | "rose" | "teal"; text: string };
type ModelRef = { connection_id: string; model_id: string } | "workflow_default";
```

Limits: 40 executable blocks, 12 Start fields, 8 Classify categories, 5 If rules, 3 images per Create images block, 12 images per run, 512 KB per document, text settings 20,000 characters (today's brief limit).

Appendix C has both current templates written as `GraphDoc`.

### 11.3 Server: storage

**Migration `011_workflow_graphs.sql`** (additive; G-7):

```sql
CREATE TABLE workflow_defs (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT NOT NULL DEFAULT '',
  icon TEXT NOT NULL DEFAULT 'workflow',
  graph_json TEXT NOT NULL,
  graph_hash TEXT NOT NULL,              -- sha256 of canonical JSON (sorted keys, no viewport/positions/notes)
  version INTEGER NOT NULL DEFAULT 1,    -- optimistic concurrency, +1 per save
  template_id TEXT,
  archived_at TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
CREATE TABLE workflow_def_snapshots (
  def_id TEXT NOT NULL REFERENCES workflow_defs(id) ON DELETE CASCADE,
  graph_hash TEXT NOT NULL,
  graph_json TEXT NOT NULL,              -- full document including positions
  label TEXT,
  created_at TEXT NOT NULL,
  PRIMARY KEY (def_id, graph_hash)
);
ALTER TABLE workflow_runs ADD COLUMN kind TEXT NOT NULL DEFAULT 'template';  -- 'template' | 'graph'
ALTER TABLE workflow_runs ADD COLUMN def_id TEXT;
ALTER TABLE workflow_runs ADD COLUMN graph_hash TEXT;
ALTER TABLE workflow_runs ADD COLUMN mode TEXT NOT NULL DEFAULT 'run';       -- 'run' | 'test'
ALTER TABLE workflow_runs ADD COLUMN parent_run_id TEXT;
ALTER TABLE workflow_steps ADD COLUMN node_id TEXT;
ALTER TABLE workflow_steps ADD COLUMN port TEXT;          -- output port taken
ALTER TABLE workflow_steps ADD COLUMN config_hash TEXT;   -- for Run from here reuse
ALTER TABLE workflow_steps ADD COLUMN reused_from TEXT;   -- run id
ALTER TABLE workflow_steps ADD COLUMN started_at TEXT;
ALTER TABLE workflow_steps ADD COLUMN finished_at TEXT;
CREATE INDEX workflow_runs_def ON workflow_runs (def_id, created_at);
```

Existing rows keep every value (`kind` defaults to `template`). Graph runs store `{"kind": "graph", "inputs": {...}}` in `input_json`, the resolved graph (with seeds filled) as a snapshot row, and one `workflow_steps` row per executable block with `position = topoOrder index`. Step `state` gains `skipped`. Steps' `output_json` stays a JSON object; transcripts keep using `source_json` for the original source (export and the source dialog depend on it).

### 11.4 Server: the engine

**Package layout:**

```
server/app/workflows/
  graph.py          Pydantic GraphDoc and per-kind configs; validate(); topo_order(); ancestors(); canonical_hash()
  templating.py     {{key.field}} parser and renderer
  engine.py         GraphRunner: scheduling, skip propagation, persistence of node states
  blocks/__init__.py  registry: kind → Block
  blocks/start.py generate.py transcribe.py clean_transcript.py generate_image.py review.py
         output.py condition.py compose.py classify.py web_search.py library_search.py
         read_document.py pick.py
  defs.py           definition CRUD, snapshots, optimistic concurrency
  catalog.py        block catalog with live availability
  templates/        brief_images.json, meeting_pack.json, research.json, ask_files.json, summarize_document.json
  jobs.py           changed: Workflows dispatches by run kind; legacy path untouched
```

**Block interface:**

```python
class Block(Protocol):
    kind: str
    native: bool                       # leases capacity around its invocation
    def outputs(self, config) -> dict[str, FieldType]: ...
    def ports(self, config) -> list[str]: ...
    async def run(self, ctx: BlockContext) -> BlockResult: ...

@dataclass
class BlockResult:
    output: dict[str, Any]             # typed fields
    port: str = "out"                  # which output port is taken
    pause: Pause | None = None         # Approve or edit, Pick favorites, long image prompt
```

`BlockContext` gives the block its resolved config (variables rendered), the run id, node id, attempt, `save_partial(output)`, `progress(done, total, label)`, the store, and the existing managers (`RunManager`, `Images`, `TranscriptionManager`, `Cleanups`, library, documents).

**Scheduling** (one block at a time per run):

```
on start or resume:
  load run, snapshot graph, step rows
  loop:
    resolved(e) := source step in {complete, skipped, reused} 
    active(e)   := source step complete/reused and source.port == e.source_port
    ready       := steps pending where all incoming edges resolved and ≥1 active (Start: always)
    dead        := steps pending where all incoming edges resolved and none active
    mark dead as skipped (with port = null), repeat until no change
    if no ready steps:
        if any step paused/running: return
        if all steps terminal: run complete ("Ready for review"); return
    pick first ready step in topo order
    attempt += 1; insert workflow_attempts row (config, resolved inputs, prompt hash)
    result = await block.run(ctx)      # native blocks take Capacity.lease(background=True) per invocation
    if result.pause: step paused, run paused, stage "Approve ‘title’"; return
    save output, port, finished_at; emit
```

- Cancellation, interruption, failure and recovery follow the existing `execute()` handling: owned image and clean-up jobs are stopped; running steps become `interrupted` at startup; "retry unfinished" sets failed/interrupted steps back to `pending` without touching completed ones; image steps whose job completed are reconciled to complete (existing `known_image` logic, keyed by node id).
- Disabled blocks are marked `skipped` at submission; their outgoing edges count as not taken.
- Runs of different workflows interleave only at native-invocation boundaries through the existing `Capacity`; chat keeps its preference.

**Templating rules** (`templating.py`):
- Grammar: `{{ key.field }}` or `{{ key.field | tagged:name }}`; whitespace inside braces allowed; anything else inside `{{ }}` is a validation error. `\{{` writes a literal `{{`.
- Plain references insert the value as text: strings as-is; numbers and booleans as JSON; `sources` as their `context` rendering; `json` as compact JSON; images and audio cannot be inserted into text (validation error).
- `tagged:name` escapes the value with `html.escape` and wraps it: `<name>\n{value}\n</name>`. If the value is empty and the reference is alone on its line, the line and the line break before it are removed. This reproduces today's meeting-pack material exactly (Appendix C).
- References to skipped blocks resolve to empty strings, and the attempt records a warning shown on the block. A **required** field (marked ★) that resolves empty fails the block with "‘{field}’ is empty because ‘{title}’ was skipped."
- No truncation, ever. Size checks happen after rendering; oversized input fails with the existing context-overflow message.
- No hidden text is added around user prompts. **Preview prompt** shows exactly what is sent. Upstream web or file text is untrusted; the `tagged` filter and the templates' own guard sentences are how a workflow marks it as material. App-authored prompts (Classify, template prompts) are frozen and hashed (G-8).

**Events.** Persisted, replayable (existing `workflow_events`, with `id`): `run.updated` carrying the v2 run snapshot after every state change. Ephemeral, not stored, no `id`: `node.progress` `{run_id, node_id, done, total, label}` and `node.text` `{run_id, node_id, delta}`, both coalesced to at most 10 per second per run. On reconnect the client gets the snapshot (which includes partial text saved once per second) and continues from new deltas. Never poll.

**Privacy rule, generalized.** A run fails before starting (and Problems shows an error while editing) if any model-calling block has a private-source ancestor (Transcribe, Clean up, Read a document, Search my files, a Recording or Document Start input) and uses a connection whose host is not loopback. This is today's `recording_requires_local` check, applied by graph.

### 11.5 API (grows only; G-6)

Existing routes keep their request and response shapes. New routes:

| Method and path | Request | Response | Notes |
|---|---|---|---|
| `GET /api/workflows/blocks` | — | `BlockCatalog` | kinds, labels, categories, availability and reason |
| `GET /api/workflows/templates` | — | `Template[]` | id, name, description, icon, `GraphDoc` |
| `GET /api/workflows/defs` | — | `DefSummary[]` | name, icon, description, block strip, last run |
| `POST /api/workflows/defs` | `{ name?, template_id?, graph? , default_model? }` | `Def` 201 | blank, from template, or import |
| `GET /api/workflows/defs/{id}` | — | `Def` | includes `version` |
| `PUT /api/workflows/defs/{id}` | `{ name, description, icon, graph, version, force? }` | `Def` or 409 `{ current: Def }` | autosave |
| `POST /api/workflows/defs/{id}/duplicate` | — | `Def` 201 | |
| `DELETE /api/workflows/defs/{id}` | — | 204 | archives; runs kept |
| `POST /api/workflows/defs/{id}/validate` | `{ graph? }` | `{ issues: Issue[] }` | server-side check of the same rules |
| `GET /api/workflows/defs/{id}/snapshots` | — | `Snapshot[]` | with run counts |
| `PATCH /api/workflows/defs/{id}/snapshots/{hash}` | `{ label }` | `Snapshot` | name a version |
| `POST /api/workflows/defs/{id}/runs` | `{ request_key, inputs, mode?, test_node_id?, test_values?, from_run_id?, from_node_id? }` | `RunV2` 202 | run, test a block, or run from here |
| `GET /api/workflows/runs` | `?def_id&state&mode&cursor&limit` | `{ items: RunV2[], next_cursor }` | includes legacy runs, adapted |
| `GET /api/workflows/runs/{id}/v2` | — | `RunV2` | legacy runs adapted to a synthetic graph |
| `POST /api/workflows/runs/{id}/decision` | `{ node_id, decision: "approve" \| "reject", value?, chosen? }` | `RunV2` | Approve or edit, Pick favorites |
| `GET /api/workflows/stream` | `Last-Event-ID` | SSE: `run.snapshot`, `run.updated`, `node.progress`, `node.text` | v2 stream |

`POST /runs/{id}/cancel`, `POST /runs/{id}/resume` (retry unfinished) and `GET /runs/{id}/export` work for both kinds; export of graph runs uses the Save results manifest.

```ts
type RunV2 = {
  id: string; kind: "template" | "graph"; def_id: string | null; def_name: string;
  graph_hash: string | null; mode: "run" | "test"; parent_run_id: string | null;
  state: "queued" | "running" | "paused" | "cancelling" | "cancelled" | "complete" | "failed" | "interrupted";
  stage: string; error: string | null; created_at: string; updated_at: string;
  inputs: Record<string, unknown>;
  graph: GraphDoc;                                    // snapshot (synthetic for template runs)
  nodes: Record<string, {
    state: "pending" | "running" | "paused" | "complete" | "failed" | "cancelled" | "interrupted" | "skipped";
    attempt: number; port: string | null; output: Record<string, unknown> | null; error: string | null;
    started_at: string | null; finished_at: string | null; reused_from: string | null;
    warnings: string[];
  }>;
  results: { node_id: string; label: string; items: { label: string; type: string; value: unknown }[] }[];
  source_available: boolean;
};
```

### 11.6 Templates as graphs, and the old path

- Ship the five templates as JSON under `server/app/workflows/templates/`. Template prompts are the frozen `templates.IMAGE_PROMPT` and `templates.MEETING_PACK` strings, inserted at load time, so their hashes stay covered by G-8.
- **Parity test (WS-B gate):** run "Brief to images" and "Recording to meeting pack" through the graph engine and through the legacy path against the fake runtime, same inputs and model. The recorded `messages`, `params` and `context_length` on each text attempt must be **byte-identical**; image job prompts and seeds identical; transcript and clean-up calls identical. Appendix C shows the template graphs that achieve this.
- The legacy `POST /api/workflows/runs` stays (G-6) and keeps executing through the legacy code. The new UI never calls it after WS-C. Legacy runs appear in the new runs list through the v2 adapter (a synthetic graph built from the template and its steps).

### 11.7 Security and privacy

- Definitions, runs and outputs are local data in the existing database and backups. Image files use the existing image backup manifest.
- Imported JSON is parsed with the Pydantic models only; unknown kinds or fields are rejected with a list of problems.
- No block makes network requests other than the existing search providers and page fetch, and model calls to configured connections.
- Recording, document and Library text and their filenames follow the privacy rule (G-11): never in Git, logs, fixtures, screenshots or reports. Test fixtures use synthetic content and "fake" in file names.

---

## 12. Checkpoints

**Stop for review after each.** Each ends with an H4 report (SPEC §H4) including the QA gates.

| Checkpoint | Delivers | Server | Done when |
|---|---|---|---|
| **WS-A** Shell | Tabs removed; sidebar rows; `/workflows` home inside the shell (cards for the two templates; recent runs from the existing API); the current builder moved to `/workflows/new?template=…` inside the shell; run detail page using today's run card; ⌘K "Go to" items | None | WS-AC1–AC4 |
| **WS-B** Engine | Migration 011; `graph.py`, `templating.py`, `engine.py`, blocks Start, Generate text, Transcribe, Clean up, Create images, Approve or edit, Save results; definitions API; templates as graphs; v2 runs, stream and decision endpoints; parity test | Yes | WS-AC5–AC9 |
| **WS-C** Studio editing | `@xyflow/react`; Studio layout; Blocks panel; canvas; drag, connect, insert, Quick add; Inspector with per-block Setup and VariableField; Problems; autosave, undo, conflict banner; copy/paste; notes; tidy up; minimap; Outline mode; home shows real definitions; old builder removed | Validate endpoint used | WS-AC10–AC17 |
| **WS-D** Running on the canvas | Run panel; live run states and motion; approvals; retry, continue without; Run from here; Test this block; Pick favorites; run view and all-runs page; versions panel; ⌘K run items; paused-run dot and toast | Reuse and test modes | WS-AC18–AC24 |
| **WS-E** Knowledge and logic | Search the web (with the extracted `search_sources` service), Search my files, Read a document, If / else, Compose text, Classify; three more templates | Yes | WS-AC25–AC29 |
| **WS-F** Gated extras | Each needs its own approval: Loop over a list; Schedule trigger; Run a workflow from chat; "Describe it" draft workflows (one model call that writes a `GraphDoc`); image editing from a reference | — | Separate specs |

WS-A has no dependency on WS-B and can ship first. WS-C needs WS-B. WS-E's blocks can land in any order after WS-D.

---

## 13. QA

All gates in `QA-REQUIREMENTS.md` apply at every checkpoint (G-1 to G-16). Notes for this work:

- **G-4:** the Studio and run view are lazy chunks; the initial JS budget is unchanged. Report the size of the Studio chunk.
- **G-6:** new routes only; the existing workflow routes keep their shapes.
- **G-7:** migration 011 upgrades the synthetic fixture database, including existing workflow runs, with row hashes on pre-existing columns unchanged.
- **G-8:** the Classify prompt is new and hashed; template prompts keep their hashes.
- **G-9:** applies to WS-E because `search/` changes (service extraction).
- **G-10:** an ordinary chat's golden request capture is unchanged at every checkpoint.
- **G-13:** the run loops (sweep, flow, breathe) disappear under both reduced-motion triggers; the motion spec checks computed `animation-name: none`.
- **G-14:** `/design` shows: a block in every run state; every block kind's canvas card; the Blocks panel with an unavailable block; Quick add; Inspector for each kind; Problems with an error and a warning; the conflict banner; Outline with a branch; the Run panel in running, paused, failed and complete states; home empty and populated.

### 13.1 Acceptance criteria

| ID | Criterion | Evidence |
|---|---|---|
| WS-AC1 | No route renders a Chat / Workflows tab bar; `SectionTabs` is gone from the bundle | e2e + grep |
| WS-AC2 | Sidebar shows Workflows and Images on every route, expanded and collapsed, with the active state; the phone drawer has them too | e2e 390 / 1440 |
| WS-AC3 | `/workflows` renders inside the shell; the two existing templates still run end to end from `/workflows/new` with today's behavior | existing workflow e2e, selectors updated in the ledger |
| WS-AC4 | Chat drafts survive a trip to Workflows and back (existing test kept) | e2e |
| WS-AC5 | Migration 011 upgrades the fixture database without changing existing rows | G-7 test |
| WS-AC6 | Definition CRUD, optimistic concurrency (409 on stale version) and archive work | Python tests |
| WS-AC7 | Parity: both templates as graphs send byte-identical model requests, image prompts and seeds as the legacy path | `test_workflow_parity.py` |
| WS-AC8 | Engine: skip propagation, joins, approval pause and resume, reject path, cancel, interrupt and retry unfinished, reuse of completed outputs, idempotent `request_key` | Python tests with the fake runtime and fake image worker |
| WS-AC9 | Templating: references, `tagged`, empty-line removal, escapes, skipped references, required-empty failure, no truncation | unit tests |
| WS-AC10 | Drag a block from the Blocks panel onto the canvas and onto a connection; both create and connect correctly | e2e (Chromium and WebKit) |
| WS-AC11 | Keyboard only: add blocks with `N`, connect through Inspector › Connections, run | e2e |
| WS-AC12 | Delete in a chain auto-heals as one undo step; undo/redo across 20 mixed actions restores the exact document | e2e + unit |
| WS-AC13 | Autosave persists across reload; a stale save shows the conflict banner; both choices work | e2e |
| WS-AC14 | Copy/paste remaps keys and internal references | unit |
| WS-AC15 | Problems: every §5.9 rule fires in the browser and the server with identical results on shared fixtures | unit (both sides) |
| WS-AC16 | Outline mode at 390 px: insert, edit in the sheet, move up/down, branches as lanes, non-nestable notice | e2e WebKit 390 |
| WS-AC17 | Tidy up is deterministic for the same document | unit |
| WS-AC18 | A run shows live states on the canvas and in the Run panel; text streams; follow mode pans and yields to manual panning | e2e + video |
| WS-AC19 | Approve, edit and reject from the Run panel and from the phone sheet | e2e |
| WS-AC20 | Retry block and Continue without it; Retry unfinished after a server restart reuses completed outputs | e2e with restart |
| WS-AC21 | Run from here reuses unchanged upstream outputs and refuses when settings changed | Python + e2e |
| WS-AC22 | Test this block runs one block with upstream or sample inputs and is hidden from Recent runs | e2e |
| WS-AC23 | SSE disconnect mid-run: the canvas recovers the correct state on reconnect without polling | e2e |
| WS-AC24 | Run view shows the run's snapshot, results and exports; legacy runs render through the adapter | e2e |
| WS-AC25 | Search the web block returns numbered sources; chat web eval unchanged (G-9) | eval report |
| WS-AC26 | Search my files and Read a document respect the local-only rule | Python tests |
| WS-AC27 | If / else operators behave per a table-driven test | unit |
| WS-AC28 | Classify meets its eval target (§13.3) | eval report |
| WS-AC29 | Each new template runs end to end on the fake runtime | e2e |

### 13.2 Motion evidence

Short Playwright videos with synthetic data, out of Git: drag and drop from Blocks; insert on a connection; tidy up; a full run with an approval; a failure and retry; reduced motion on.

### 13.3 Classify eval (WS-E)

Proposal for Jake to approve before WS-E: 60 synthetic cases across 3, 5 and 8 categories, including ambiguous ones that should go to Other. Target: ≥ 90% correct on clear cases, ≥ 70% Other on ambiguous ones, 100% valid outputs (schema). Run on the default chat model.

---

## 14. Decisions for Jake

| ID | Decision | Needed before | Recommendation |
|---|---|---|---|
| J-W1 | Allow model calls written by you inside workflows (Generate text and Classify blocks), beyond the current allowed list | WS-B | Yes. They only run when you build and run them, and Preview prompt shows exactly what is sent. |
| J-W2 | Approve `@xyflow/react` (web, lazy-loaded); keep or hide its small attribution mark | WS-C | Approve; keep the attribution (it is unobtrusive, bottom-right, and asked for by its authors) |
| J-W3 | Remove the Chat / Workflows tabs and the standalone Workflows page; add Workflows and Images to the sidebar | WS-A | Yes (this is your request) |
| J-W4 | Phones edit through the Outline, not the canvas | WS-C | Yes |
| J-W5 | Built-in templates become read-only graphs you copy; the old fixed builder is removed in WS-C; its API stays for old runs | WS-C | Yes |
| J-W6 | Allow `stroke-dashoffset` in the motion guard for the run pulse | WS-D | Yes |
| J-W7 | Branching: If / else (no model) and Classify (model) in WS-E | WS-E | Yes |
| J-W8 | Classify eval targets (§13.3) | WS-E | As proposed |
| J-W9 | WS-F items, one by one | Later | Decide after WS-E is in daily use |

**`AGENTS.md`, append after Jake approves:**

> **User authorization (date) — Workflow Studio:** build `docs/next/workflow-studio/WORKFLOW-STUDIO-SPEC.md` checkpoint by checkpoint, stopping for review after each. This supersedes `docs/COMPOSER-WORKFLOW-UX-PLAN.md`'s tabs and fixed canvas; the composer image action stays. Approved: user-authored model calls inside workflow blocks (Generate text, Classify) — they are user content, run only when the user runs a workflow, and are never added by the app; app-authored prompts (Classify, templates) remain frozen and hashed. Approved dependency: `@xyflow/react`, exact pin, lazy chunks only. `stroke-dashoffset` is allowed in `check_motion.py`. Phones edit through Outline mode. Loops, schedules, run-from-chat, AI-drafted workflows and image editing are not authorized. Workflow text, documents, recordings and their filenames follow the recording privacy rule.

---

## 15. Deliberately left out

- **Autonomous agents.** Copilot Studio's agent node chooses its own next step. `APP-DIRECTION-AND-WORKFLOWS.md` §5 sets the bar: only after fixed workflows show a measured need. Research stays shelved.
- **Connectors and HTTP.** No email, calendar or web-hook blocks. They would need credentials, idempotency and an approval model for external writes.
- **Parallel execution.** One native invocation at a time on this Mac; running branches concurrently would only queue on the capacity lease and complicate recovery.
- **Loops.** Durable loop state, partial retries and caps are a separate design (WS-F).
- **Publishing and sharing.** Single user.

---

## 16. Limits of this review

- The live app was viewed in desktop Chrome only; the phone was not checked. The repository was read at `dce4c49`. Nothing was run, built or tested.
- Line numbers are correct for `dce4c49` and will drift.
- Copilot Studio details come from Microsoft's topic-authoring documentation, the July 2026 message-center note on the new workflows designer, and one third-party write-up; Copilot Studio itself was not used.
- The category colors were chosen against the existing tokens by calculation; the contrast script must confirm them.
- The prototype in this folder is a hand-built mock with fake data. Where it and this document differ, this document wins.

---

## Appendix A. Copilot Studio parity

| Copilot Studio | Here | Checkpoint |
|---|---|---|
| Canvas with nodes, + between nodes to add | Canvas; + on every connection; Quick add | WS-C |
| Drag nodes onto the canvas from a left rail (new workflows designer) | Blocks panel with drag and drop | WS-C |
| Properties panel for the selected node | Inspector | WS-C |
| Variables and the {x} picker | `{{key.field}}`, {x} picker, Produces list | WS-C |
| Condition node | If / else | WS-E |
| Prompt and Classify AI actions | Generate text, Classify | WS-B, WS-E |
| Generative answers over knowledge | Search the web or Search my files, then Generate text | WS-E |
| Question node / human in the loop / approvals | Start inputs; Approve or edit; Pick favorites | WS-B, WS-D |
| Test pane | Run panel | WS-D |
| Run a single node in place | Test this block | WS-D |
| Cut, copy, paste, undo, redo | Same | WS-C |
| Notes on the canvas | Notes | WS-C |
| Health center (live problems) | Problems | WS-C |
| Tidy up, layout | Tidy up (top to bottom) | WS-C |
| Code editor (YAML) | View, export and import JSON | WS-C |
| Run analytics and history | Recent runs, all runs, run view with per-block durations | WS-D |
| Versioning | Run snapshots, named versions, restore | WS-D |
| Triggers: manual, recurrence, connector, HTTP | Manual Start; Schedule gated | WS-B, WS-F |
| Agent node, connectors, channels | Left out (§15) | — |
| Describe-to-build with Copilot | "Describe it" gated | WS-F |

## Appendix B. Copy deck

| Where | Text |
|---|---|
| Sidebar rows | Workflows · Images |
| Home title / subtitle | Workflows · Chain models, search, images and recordings into repeatable steps. Runs keep going on your Mac when you close the app. |
| Home sections | Your workflows · Start from a template · Recent runs · View all |
| New workflow menu | Blank · (template names) |
| Empty home | Build your first workflow · Pick a template or start blank. You can change every step. · Start blank |
| Template toast | Created from template. Changes are yours. |
| Card status | Never run · Ran {time} ago · Running now · Waiting for you · Failed {time} ago |
| Save state | Saved · Saving… · Couldn't save · Retry |
| Conflict banner | This workflow changed on another device. · Load latest · Keep mine |
| Blocks search | Search blocks |
| Categories | Inputs · AI · Knowledge · Media · Logic · Review · Output |
| Unavailable block | The image engine isn't ready. Settings › Images. / Add files to your Library first. / Set up web search in Settings. |
| Empty Output tab | Run the workflow or test this block to see its output. |
| Run button tooltip with errors | Fix {n} problem(s) to run. |
| Run panel | Run workflow · Cancel · Cancelling… · Retry block · Continue without it · Retry unfinished blocks · Approve · Reject · Export · View original transcript |
| Approval toast | {workflow} is waiting for you. · Open |
| Run view banner | Viewing a run from {date}. · Edit workflow |
| Phone notice | Part of this workflow is easier to change on a larger screen. |
| Run from here disabled | Run the workflow once first. / Blocks above this one changed since the last run. |
| Draft label | Draft for review. Check it against the original. |

## Appendix C. The two current templates as graphs

Positions omitted. Prompts shown by reference; at load time they are the exact strings in `templates.py`.

**Brief to images** — Start → Draft image prompt → Check the prompt → Create images → Save results

```json
{
  "schema": "atelier.workflow/1",
  "nodes": [
    { "id": "n_start", "kind": "start", "key": "start", "title": "Start",
      "config": { "fields": [ { "name": "brief", "label": "Image brief", "type": "long_text", "required": true } ] } },
    { "id": "n_draft", "kind": "generate", "key": "draft", "title": "Draft image prompt",
      "config": { "model": "workflow_default", "instructions": "$template:IMAGE_PROMPT",
                  "prompt": "{{start.brief}}", "format": "text", "params": {} } },
    { "id": "n_review", "kind": "review", "key": "review", "title": "Check the prompt",
      "config": { "show": "{{draft.text}}", "editable": true,
                  "message": "Check the prompt before images are made." } },
    { "id": "n_images", "kind": "generate_image", "key": "images", "title": "Create images",
      "config": { "prompt": "{{review.value}}", "count": 1, "seeds": "auto" } },
    { "id": "n_save", "kind": "output", "key": "save", "title": "Save results",
      "config": { "include": [ { "label": "Prompt", "ref": "{{review.value}}" },
                               { "label": "Images", "ref": "{{images.images}}" } ],
                  "formats": ["md", "json"] } }
  ],
  "edges": [
    { "id": "e1", "source": "n_start",  "source_port": "out",      "target": "n_draft",  "target_port": "in" },
    { "id": "e2", "source": "n_draft",  "source_port": "out",      "target": "n_review", "target_port": "in" },
    { "id": "e3", "source": "n_review", "source_port": "approved", "target": "n_images", "target_port": "in" },
    { "id": "e4", "source": "n_images", "source_port": "out",      "target": "n_save",   "target_port": "in" }
  ],
  "notes": [],
  "settings": { "keep_test_runs_days": 7 }
}
```

Legacy "Review prompt off" equals deleting the Check the prompt block (auto-heal connects Draft to Create images, and `{{review.value}}` must then be changed to `{{draft.text}}`; Problems flags it).

**Recording to meeting pack** — Start → Transcribe → Clean up (disabled by default) → Draft meeting pack → Save results

```json
{
  "schema": "atelier.workflow/1",
  "nodes": [
    { "id": "n_start", "kind": "start", "key": "start", "title": "Start",
      "config": { "fields": [ { "name": "recording", "label": "Recording", "type": "recording", "required": true } ] } },
    { "id": "n_tx", "kind": "transcribe", "key": "transcript", "title": "Transcribe recording",
      "config": { "recording": "{{start.recording}}" } },
    { "id": "n_clean", "kind": "clean_transcript", "key": "clean", "title": "Clean up transcript",
      "disabled": true, "config": { "transcript": "{{transcript.transcript}}", "model": "workflow_default" } },
    { "id": "n_pack", "kind": "generate", "key": "pack", "title": "Draft meeting pack",
      "config": { "model": "workflow_default", "instructions": "$template:MEETING_PACK",
                  "prompt": "{{transcript.timestamped_text | tagged:original_transcript}}\n{{clean.text | tagged:cleaned_reading_aid}}",
                  "format": "markdown", "params": {} } },
    { "id": "n_save", "kind": "output", "key": "save", "title": "Save results",
      "config": { "include": [ { "label": "Meeting pack", "ref": "{{pack.text}}" } ],
                  "formats": ["md", "json"], "include_sources": true } }
  ],
  "edges": [
    { "id": "e1", "source": "n_start", "source_port": "out", "target": "n_tx",    "target_port": "in" },
    { "id": "e2", "source": "n_tx",    "source_port": "out", "target": "n_clean", "target_port": "in" },
    { "id": "e3", "source": "n_clean", "source_port": "out", "target": "n_pack",  "target_port": "in" },
    { "id": "e4", "source": "n_tx",    "source_port": "out", "target": "n_pack",  "target_port": "in" },
    { "id": "e5", "source": "n_pack",  "source_port": "out", "target": "n_save",  "target_port": "in" }
  ],
  "notes": [],
  "settings": { "keep_test_runs_days": 7 }
}
```

Edge `e4` lets the meeting pack run when clean-up is disabled or skipped (a join: Draft meeting pack waits for both incoming connections to resolve and runs if either is taken). With clean-up disabled, `{{clean.text}}` is empty, its tagged line is removed, and the material equals today's: `<original_transcript>\n{escaped timestamped text}\n</original_transcript>`. With clean-up on, the cleaned block follows on a new line, as today. `transcript.timestamped_text` is produced by the existing `source.timestamped()` function.
