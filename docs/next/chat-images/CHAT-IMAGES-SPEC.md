# Images in chat, and the working indicator

**Written:** 13 October 2026, against commit `dce4c49` · **By:** Claude (validator) · **For:** Jake to approve, Codex to build
**Reads with:** `docs/SPEC.md`, `docs/next/QA-REQUIREMENTS.md`, `docs/next/PHASE-4-POLISH-AND-MOTION.md` (C1–C4), `docs/IMAGES-STORAGE.md`, `docs/next/workflow-studio/WORKFLOW-STUDIO-SPEC.md` (shell and sidebar)
**Reference prototype:** `prototype.html` in this folder. Open it in a browser: send a message with Think on, then switch on Image and create two images. It shows the layout and motion described here. Where it and this document differ, this document wins.

Place this folder at `docs/next/chat-images/` in the repository.

---

## 0. The short version

Two changes, shipped in that order:

1. **A working indicator worth looking at (Part B, checkpoint CI-A).** When you send a message, the three grey dots are replaced by a status line: your Atelier "A" mark draws itself in cobalt, next to a word that changes every couple of seconds: *Spelunking… Mixing pigments… Percolating…*. Real stages always win over playful words: "Waiting for qwen3.8 · #2 in line", "Loading qwen3.8", "Reading 4 pages". When a thinking model starts reasoning, the line becomes **Thinking** with a one-line live ticker of what it is actually thinking, and collapses to "Thought for 12 s ›" when the answer starts. Web only; no server change.

2. **Images become part of the conversation (Part A, CI-B and CI-C).** Today the Image button swaps the composer for a separate form with its own job list, and results never appear in the chat. Instead, Image becomes a mode of the same composer. You type a prompt and send it; the prompt appears as your message, and the reply is an **image card** that "develops" in place (a soft moving field of color with a four-step progress bar that follows the real denoising steps), then reveals the picture. Images are saved with the chat. Each image has Save, More like this, Refine, Copy prompt and Details; the turn has Try again (a new branch, like regenerating an answer). Clicking an image opens a full-screen viewer that zooms out of the card.

No new dependencies. One additive migration. No new model calls (an optional "Improve prompt" is listed for later, gated).

About the logo: Claude's starburst is Anthropic's trademark and does not belong in your app. The indicator uses your own easel-"A" mark from `web/public/icons/mark.svg`, animated.

---

## 1. What is there today

Viewed in the screenshot Jake shared (fake runtime) and read in source.

| # | Finding | Evidence | Effect |
|---|---|---|---|
| 1 | **Image mode replaces the composer with a mini-app.** "← Message · Images · Gallery · Connected", a "Create an image" card, a Prompt box, "Advanced", "Generate one image", then job filter chips and a job list. | `Composer.tsx` lines ~198–222 mount `ImagesWorkspace` and hide the composer | It feels like leaving the chat. Two prompt boxes with different behavior. |
| 2 | **Images never enter the conversation.** Generated images live in the job list under the composer and in the Gallery; the thread has no record. | Composer image path posts to `/api/images/jobs` without a chat request (COMPOSER-WORKFLOW-UX-REPORT) | You cannot scroll back to see what you made in this chat, or iterate on it in context. |
| 3 | **Engineering copy on screen.** "Connected", "One native task at a time. Chat may wait for an image to finish; models are never unloaded automatically." | `ImagesPage.tsx` | True, but it reads like a log. |
| 4 | **Progress is text only.** The job card shows a stage string. No sense of the four steps, no reveal. | `ImageJob.stage`, `completed_steps` exist but are shown as text | Ten seconds feels long. |
| 5 | **The wait before an answer is three grey dots.** Queued and loading states have text; the rest is dots. | `WaitingDots.tsx`, `LiveThread.tsx` lines ~428–445 | Functional, not premium. Nothing says what is happening. |
| 6 | **Live reasoning opens as a full panel.** While a model thinks, the Thinking collapsible is open and streams every token of reasoning into a 288 px scroll box. | `LiveThread.tsx` `Thinking`, `open = live` | Noisy, and it pushes the answer down when it arrives. |

What is solid and stays: durable image jobs with events, idempotent `request_key`, real progress (`initializing` → `denoising` 0–4 → `decoding` → saved), cancellation, recovery, the cancellable save/share dialog, `parent_id` lineage for versions, the existing reasoning stream (`reasoning.delta`, `stats.reasoning_ms`), search step events, C1 send timing and C4 streaming animation.

Measured facts used below: a warm image takes about 10–13 s (`IMAGE-TRIAL-REPORT.md`, `IMAGES-I1-REPORT.md`); the engine runs 4 denoising steps at 1024 × 1024 and gives no preview frames; `parent_id` records lineage only (reference-image editing is not built).

---

## Part B. The working indicator (checkpoint CI-A)

Built first: it is web-only and every chat benefits.

### B1. Anatomy

The status line sits where the three dots are today, under the model name in the assistant row.

```
qwen3.8:27b-atelier-eval-32k                         ← existing model name line (12 px, --text-3)
[A]  Spelunking…   4 s                               ← status line: mark 18 px · word 14 px --text-2 · elapsed 12 px --text-3
```

While the model reasons:

```
[A]  Thinking   6 s                              ⌄
     …so the series went 4–2 and I should keep the table to one row per finals game
     ↑ thought ticker: latest reasoning, one line (two on phones), 13 px --text-3, left edge fades out
```

When the answer starts, the line collapses into the existing collapsed Thinking row:

```
[🧠] Thought for 12 s                             ⌄   ← existing component, closed
The Bucks won the 2021 finals 4–2 …                  ← answer streams with the existing caret (C4)
```

Height: 32 px for the line, plus 20 px per ticker line. Left edge aligns with the answer text.

### B2. Phases (truthful first)

The label is chosen by this order. Playful words appear only when the app does not know anything more specific.

| Phase | Trigger (existing data) | Label | Mark |
|---|---|---|---|
| Queued | `stage === "queued"` | "Waiting for {model} · #{n} in line" (today's text) | Draw loop |
| Loading model | `stage === "loading-model"` | "Loading {model}… {s} s" (today's text) | Draw loop |
| Searching | `stage === "search"` | The latest live search step label, for example "Searching the web", "Reading 4 pages", "Searching your files" (from the step events SearchActivity already receives) | Draw loop |
| Waiting for the first token | Streaming, no content, no reasoning, no known stage | A playful word (B3), changing every 2.4 s | Draw loop |
| Thinking | `message.reasoning` non-empty and `message.content` empty | "Thinking" + elapsed + thought ticker (B4) | Think loop |
| Answering | First `text.delta` | Line collapses (B6); answer streams | — |
| Stopped / error | Existing statuses | Line removed; existing notices | — |

SearchActivity's step list stays below the line exactly as today; only the dots are replaced.

Elapsed seconds appear after 3 s, in tabular numerals, updated once per second (one shared timer; never a timer per word).

### B3. Status words

- **Setting:** Settings › Appearance › "Status words": **Playful** (default) · **Plain**. Plain always shows "Working". Stored with the other UI preferences (`useUI`, next to `reduceMotion`).
- **List** (in `web/src/lib/status-words.ts`): Spelunking, Pondering, Mulling, Percolating, Noodling, Tinkering, Musing, Ruminating, Brewing, Simmering, Untangling, Sketching, Priming the canvas, Mixing pigments, Stretching canvas, Blocking in shapes, Sharpening pencils, Composing, Framing, Underpainting, Glazing, Shading, Drafting, Whittling, Weaving, Distilling, Marinating, Assembling, Calibrating, Deliberating, Contemplating, Puzzling, Conjuring, Doodling, Polishing, Rummaging. Each shown with "…".
- **Order:** shuffled once per message with a seed from the message id (so a re-render or reconnect shows the same sequence), no repeats until the list is used up. The first word is shown immediately on send.
- **Change rate:** every 2.4 s. A word never changes in the 400 ms before a phase change is due (no flicker when the first token arrives).
- **Never** shown for image turns, which always know their real stage (A4).

### B4. Thought ticker

- Shows the **end** of `message.reasoning`: the last 160 characters, trimmed to a word boundary, newlines turned into spaces, prefixed with "…". Desktop: one line in a clipped flex box aligned to the end, so the newest words are always visible and older words slide off the left edge under a 24 px `mask-image` fade. Phones: two lines, bottom-aligned in a 40 px box, with the top edge fading.
- Updates from the existing `reasoning.delta` stream, batched to one paint per animation frame (existing rAF batching). No extra request, no summarizing model call: it is the model's own text.
- Clicking the line (or the chevron) expands the full reasoning in the existing Thinking content area, scrolled to the bottom and following new text while open. Collapsing returns to the ticker.
- When the answer starts, the line becomes the existing closed "Thought for {n} s" row. `Thinking` is no longer opened automatically while live (finding 6); its `open` state starts closed.

### B5. The mark

Source: `web/public/icons/mark.svg` (an easel "A": a chevron stroke and a dot). Make a 24-unit inline React component `AtelierMark` with `stroke="currentColor"`, color `--brand`:

```svg
<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">
  <path class="mark-base" d="M5.6 19.4 12 4.6l6.4 14.8"
        fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" opacity="0.22"/>
  <path class="mark-a" d="M5.6 19.4 12 4.6l6.4 14.8" pathLength="40"
        fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>
  <circle class="mark-dot" cx="12" cy="16.3" r="1.7" fill="currentColor"/>
</svg>
```

Two loops, both pass the current motion guard (`stroke-dasharray`, `transform` and `opacity` only):

| Loop | Used for | What moves | Timing |
|---|---|---|---|
| **Draw** | queued, loading, searching, first-token wait, image preparing | A faint copy of the A (22% opacity) stays put so the mark never disappears. Over it, the A draws from the left foot over the apex to the right foot (`stroke-dasharray: 0 40` → `40 0`, 0–50%); the dot drops in (translateY −3 px → 0, scale 0.4 → 1, 45–60%); both hold (60–85%); both fade (85–100%) | 1.8 s, `--ease-out` for the stroke |
| **Think** | reasoning, image denoising | The A stays drawn at full opacity (the faint copy is hidden); the dot bobs up the easel and back (translateY 0 → −3.5 px → 0) with scale 1 → 0.85 → 1 | 1.2 s, ease-in-out |

The mark pops in when the assistant row appears (scale 0.8 → 1, opacity 0 → 1, 120 ms, `--ease-pop`). Under reduced motion the mark is static and fully drawn.

### B6. Motion

| Moment | What moves | Duration | Easing | Reduced motion |
|---|---|---|---|---|
| Row appears after send | Mark pops; status line fades in | 120 ms | `--ease-pop` | Instant |
| Word changes | Old word: translateY 0 → −4 px, opacity → 0. New word: translateY 4 px → 0, opacity 0 → 1 | 120 ms out, 200 ms in | `--ease-in` / `--ease-out` | Text swaps, no movement |
| Label shimmer | Existing `activity-shimmer` veil on the label | 1.6 s loop | linear | None |
| Phase change | Label crossfades (same as word change) | 200 ms | `--ease-out` | Swap |
| Ticker text | No animation; text replaces per frame | — | — | — |
| Answer starts | Status line height → 0 and opacity → 0 while the Thinking row appears in its place | 200 ms | `--ease-out` | Instant |

Keyframes live in `motion.css` (G-13 and `check_motion.py` apply). No `will-change`.

### B7. Accessibility

- The status line is `role="status"` with a visually hidden text that changes **only on phase changes**: "Waiting for {model}", "Loading {model}", "Searching the web", "Working", "Thinking", then nothing (the answer has its own semantics). Playful words and the ticker are `aria-hidden`.
- The ticker is a button ("Show thinking", `aria-expanded`).
- Contrast: label `--text-2` and ticker `--text-3` on `--bg` already pass in both themes.

### B8. Files

`WaitingDots.tsx` is replaced by `WorkingLine.tsx` (status line, words, ticker) and `AtelierMark.tsx`. `LiveThread.tsx` uses `WorkingLine` where it rendered the dots and the queued/loading paragraph, and starts `Thinking` closed. New `web/src/lib/status-words.ts`. `SettingsDialog.tsx` Appearance pane gets the Status words control. `motion.css` gets `mark-draw`, `mark-dot-drop`, `mark-dot-bob`, `word-in`, `word-out`, `line-collapse`.

---

## Part A. Images in chat (checkpoints CI-B and CI-C)

### A1. Principles

1. **One composer.** Image is a mode of the composer, not a second form.
2. **Images are turns.** A prompt and its images are messages in the thread, saved with the chat, branchable like any turn.
3. **Truthful progress.** Every label and every progress tick comes from the job's real state. Nothing is faked to look faster.
4. **The image engine is not a chat model.** Image turns are never sent to the text model's context, and no chat model is called to make an image unless Jake later approves "Improve prompt" (A11).
5. **The Gallery stays** as the library of every image across chats (Images in the sidebar).

### A2. The composer in image mode

```
┌──────────────────────────────────────────────────────────────────────────┐
│ ┌ ▣ Refining image 2 · seed 18342   ✕ ┐            ← only when refining  │
│ A quiet harbor at dawn, paper lanterns on the water, soft fog            │
│                                                                          │
│ [✦ Image ✕]  [1 image ▾]  [⋯]                 FLUX.2 klein · 1024²  [↑]  │
└──────────────────────────────────────────────────────────────────────────┘
```

- **Entering:** the Image chip, or typing `/image ` at the start of an empty message (an explicit command, not keyword detection). Leaving: the ✕ on the chip, Escape in an empty prompt, or the chip again.
- **Look:** the chip becomes `--brand-soft` with `--brand` text and a ✕. The composer border tints to `--brand` at 40% (120 ms). Search, Library, Think and attach fade out (120 ms) because they do not apply; the count and options controls fade in. Placeholder: "Describe an image…". Send button tooltip and label: "Create image" (⌘↵ / Enter as today).
- **Count:** a pill "1 image ▾" opening a small menu: 1 · 2 · 3 images. Images run one after another.
- **Options (⋯):** Seed: Automatic (default) or a number per image (existing validation, 0–4,294,967,295). Seeds are resolved once on the client before sending (existing `imageSeeds` helper) so a retried request is identical.
- **Right side:** "FLUX.2 klein · 1024²" in 12 px `--text-3` (from `/api/images/status`). There is no size picker because the engine has one size.
- **Unavailable engine:** the Image chip is disabled with the status reason as its tooltip ("The local image worker or pinned model is unavailable.").
- **Drafts:** image and chat drafts stay separate per chat (existing `imageDrafts`). Leaving image mode keeps the image draft.
- **Phone:** the same composer; the count pill and ⋯ share one row with the chip; the engine label is hidden.

### A3. The image turn in the thread

**Your message** is a normal user bubble with the prompt, plus a small 12 px "Image" tag with the `ImagePlus` icon above the text, and "2 images" when more than one.

**The reply** is an image card in the assistant column. In place of the model name line it shows "FLUX.2 klein 4B" (from status). Below, the frames:

| Count | Desktop | Phone (< 768 px) |
|---|---|---|
| 1 | One frame, 1:1, width min(440 px, column) | Full column width |
| 2 | Two frames side by side, gap 8 px | Two columns |
| 3 | Three frames, gap 8 px | Horizontal scroll-snap row, each frame 78% wide, 8 px gap, with three 6 px dots under it |

Frames: `--radius-lg`, 1 px `--line`, overflow hidden, `aspect-ratio: 1`.

Under the frames: the **status line** of the turn (same component family as B1, with the mark): "Creating image 1 of 2 · step 3 of 4", "Waiting for your Mac", "2 images · 23 s" when done. Then the turn actions (A5).

### A4. Frame states and the "develop" animation

Each frame follows its own job (`ImageJob.state`, `stage`, `completed_steps`):

| Job | Frame | Status line text | Mark |
|---|---|---|---|
| `queued` (another job or a chat is using the Mac) | Placeholder, still: `--surface-2` with grain, no motion; a small "Next" label for frames waiting behind a sibling | "Waiting for your Mac" ; with an image ahead: "Waiting for your Mac · after 1 image" | Draw loop |
| `preparing` ("Initializing image model", "Loading image weights") | **Develop field** starts (below); progress bar empty with an indeterminate sheen | "Loading the image model" | Draw loop |
| `running` "Generating image", `completed_steps` 0–4 | Develop field; progress bar shows four segments, filled = `completed_steps` | "Creating · step {n+1} of 4" (or "Creating image {i} of {count} · step …") | Think loop |
| `running` "Decoding image" | Develop field brightens slightly (opacity 0.85 → 1); all four segments filled | "Finishing" | Think loop |
| `complete` | **Reveal** (below), then the image | "{count} images · {seconds} s" | Hidden |
| `cancelling` | Field freezes (animation paused) | "Cancelling…" | Static |
| `cancelled` | Placeholder with "Cancelled" and **Retry** | "Cancelled" | Hidden |
| `failed` | Placeholder with the error message (`--danger` icon) and **Retry** | "Couldn't create this image" | Hidden |
| `interrupted` | Placeholder with "Interrupted" and **Retry** | "Interrupted — retry available" (today's copy) | Hidden |
| Output removed later | Placeholder "Image removed" with the prompt still copyable | — | — |

**Develop field** (a stand-in for preview frames the engine does not provide):
- Three large blurred color blobs (`radial-gradient`, static `filter: blur(28px)` on the layer) in `--brand`, `--brand-soft` and a warm neutral, each drifting slowly with `transform: translate()` keyframes (7 s, 9 s and 11 s, alternate, ease-in-out). Static SVG grain on top at 8% opacity.
- A sheen (a 40%-wide soft white band at 6% opacity) crosses the frame with `transform: translateX()` every 2.4 s while `preparing`.
- **Progress bar:** 3 px tall, 12 px from the bottom, inset 12 px, four segments with 4 px gaps, `--brand` fill on a `--surface-3`-at-60% track. A segment fills with a `width` transition of 320 ms `--ease-out` when `completed_steps` increases. The bar fades out at reveal.

**Reveal** (on `complete`): the image loads (`decoding="async"`, `/api/images/jobs/{id}/output/png`); when its `load` event fires, the image goes from opacity 0 and `scale(1.03)` to opacity 1 and `scale(1)` over 320 ms `--ease-out`, while the develop field fades out over 200 ms. If loading fails, show the placeholder with "Couldn't load the image · Retry". Only frames that completed during this session reveal; images loaded from history appear without animation (same rule as C2's fresh rows).

### A5. Actions

**Per image** (on desktop, a row of 32 px icon buttons appears at the frame's bottom edge on hover or focus, on a gradient scrim; on touch, the same row sits under the frame, always visible):

| Action | Icon | Does |
|---|---|---|
| Open | (click the image) | Viewer (A6) |
| Save | `Download` | Existing cancellable save/share dialog (PNG, or JSON metadata) |
| More like this | `Sparkles` | New image turn with the same prompt, one image, a new seed, `parent_id` = this job |
| Refine | `Pencil` | Enters image mode with a "Refining image {n}" chip (thumbnail, seed, ✕) and the prompt prefilled, cursor at the end. Sending makes a new turn with `parent_id` = this job |
| Copy prompt | `Copy` | Existing copy feedback (C7) |
| Details | `Info` | Popover: prompt, seed, model, 1024 × 1024, 4 steps, time taken, file size, created |
| Remove | `Trash` (in the ⋯ menu) | Existing remove-output confirmation; the frame becomes "Image removed" |
| Ask about it (CI-C, vision models only) | `MessageSquare` (in ⋯) | Attaches the PNG to the composer in chat mode through the existing image-attachment path, for a model that reports `vision` |

**Per turn** (under the status line, existing message-action style): **Try again** (new seeds for the same prompt and count; creates a sibling assistant turn, so the existing branch navigator "‹ 2 / 2 ›" appears), **Cancel** while any job is active (cancels this turn's active and queued jobs), **Copy prompt**.

### A6. Viewer

- Opens from a click or Enter on a frame. **Shared-element zoom:** the image animates from its frame rectangle to its centered full-screen rectangle with a transform (FLIP), 320 ms `--ease-sheet`; the `--overlay` scrim fades in (200 ms). Closing reverses it back to the frame.
- Layout: the image fit to the viewport with 24 px margins (16 px on phones); a top bar with the prompt (two-line clamp, expandable), position "2 / 3", and Close; a bottom bar with Save, More like this, Refine, Copy prompt, Details.
- Navigation: ← → keys and on-screen arrows (desktop), horizontal swipe with the image following the finger (phones), across every image in **this chat** in thread order. Changing image slides 24 px and crossfades (200 ms).
- Zoom: double-click or double-tap toggles 1:1 (pixel size); pinch zoom on phones.
- Escape, the scrim or swipe-down (phones) closes. Focus returns to the frame that opened it. Built on the existing Radix Dialog with the existing `full-screen-in/out` keyframes for the scrim.

### A7. Data model

**Migration `0NN_chat_images.sql`** (next free number; `012` if Workflow Studio's `011` has landed). Additive (G-7):

```sql
ALTER TABLE messages ADD COLUMN kind TEXT NOT NULL DEFAULT 'text';   -- 'text' | 'image'
CREATE TABLE message_images (
  message_id TEXT NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
  position INTEGER NOT NULL,                       -- 0, 1, 2 within the turn
  job_id TEXT NOT NULL REFERENCES image_jobs(id),
  PRIMARY KEY (message_id, position)
);
CREATE INDEX message_images_job ON message_images (job_id);
```

- An image turn is two messages in the existing tree: a **user** message (`kind = 'image'`, `content` = the prompt) and an **assistant** message (`kind = 'image'`, `content = ''`, `params_json` = `{"engine": "FLUX.2 klein 4B", "count": n, "seeds": [...], "source_job_id": id | null}`), linked to its jobs through `message_images`.
- The assistant message's `status` stays `complete`. The turn's live state is **derived from its jobs** when read, so chat startup recovery never touches image turns and there is one source of truth.
- Deleting a chat deletes its `message_images` rows, not the images. Images stay in the Gallery until removed there (existing storage and backup rules).

### A8. API (grows only; G-6)

| Method and path | Request | Response | Notes |
|---|---|---|---|
| `POST /api/chats/{id}/images` | `{ request_key, prompt, count: 1–3, seeds: int[count], parent_id?: message id, source_job_id?: job id }` | 202 `{ user: Message, assistant: Message }` | Creates both messages and `count` image jobs (request keys `{request_key}-{i}`) in one transaction; idempotent: a repeat returns the existing turn; a different body with the same key is 409 (existing rule). `parent_id` defaults to the chat's current leaf. Jobs get `parent_id = source_job_id`. |
| `POST /api/chats/{id}/messages/{message_id}/images/retry` | `{ request_key, seeds: int[count] }` | 202 `{ assistant: Message }` | Try again: a sibling assistant image turn under the same user message |
| `POST /api/chats/{id}/messages/{message_id}/images/cancel` | — | `{ assistant: Message }` | Cancels that turn's queued and running jobs through the existing job cancel |

`Message` gains two optional fields: `kind: "text" | "image"` (default `"text"`) and `images: ImageJob[] | null` (in position order; `null` for text). `ChatDetail` returns them. Existing routes and fields are unchanged.

**Live updates:** while the open chat has an active image job, the client subscribes to the existing `/api/images/events` stream (snapshot plus changes, `Last-Event-ID` replay) and updates frames from it, batched per animation frame. It unsubscribes when no job in the chat is active. Never poll. "Waiting … after 1 image" is computed in the client from that snapshot (jobs `queued` with an earlier `created_at`, plus a `running` one).

**Titles:** a chat whose first turn is an image gets a title from the prompt (first 48 characters at a word boundary). No title model call: the Mac is busy with the image, and the allowed call list does not need to grow.

**Context:** `runs/context.py` skips every `kind = 'image'` message (both roles) when assembling a text request. An ordinary chat's golden request capture is unchanged (G-10). If a thread is image, text, image, text, the text model sees only the text turns.

**Export:** chat Markdown export writes an image turn as the prompt and one line per image, `Image {n}: Atelier-image-{id8}.png · seed {seed}`; JSON export includes `kind`, the prompt and the job ids and seeds. Image files are not embedded; they are saved through the existing image save flow.

### A9. Gallery

`/images` stays as the library of all images, inside the app shell (per the Workflow Studio spec). Each image shows "From ‹chat title›" linking to the turn (`/c/{chat}#m-{message}`), or "From a deleted chat". The Gallery's own create form is removed in CI-B; "New image" on the Gallery opens a new chat in image mode.

### A10. Copy

| Where | Text |
|---|---|
| Image chip (off / on / unavailable) | Image · Image ✕ · (tooltip) {status reason} |
| Placeholder | Describe an image… |
| Count menu | 1 image · 2 images · 3 images |
| Options | Seed · Automatic · Use a fixed seed |
| Refine chip | Refining image {n} · seed {seed} |
| User tag | Image · {n} images |
| Status line | Waiting for your Mac · Waiting for your Mac · after {n} image(s) · Loading the image model · Creating · step {s} of 4 · Creating image {i} of {n} · step {s} of 4 · Finishing · {n} image(s) · {t} s · Cancelling… |
| Frame states | Next · Cancelled · Couldn't create this image · Interrupted · Image removed · Retry |
| Turn actions | Try again · Cancel · Copy prompt |
| Image actions | Save · More like this · Refine · Copy prompt · Details · Remove · Ask about it |
| Remove confirm | Remove this image? It's deleted from your Mac and from every chat that shows it. · Remove · Keep |

Removed from the interface: "Connected", "One native task at a time…", "Generate one image", "All jobs / In progress / Saved images" filters inside the composer.

### A11. Later and gated (CI-D)

Each needs Jake's separate approval:

- **Improve prompt.** A ✦ button in image mode asks the selected chat model to rewrite the prompt (one new model call, frozen prompt, eval required, G-8). The suggestion appears as an inline diff you accept or dismiss. Never automatic.
- **Edit from a reference image.** FLUX.2 klein supports reference edits, but the engine path and file handling are not built (`IMAGES-STORAGE.md`). Needs its own spec.
- **Let the chat model make images.** Tool calling; out of scope while tools are reserved for Research.
- **Other sizes.** Only after memory and latency are measured per size.

---

## C. Checkpoints

**Stop for review after each.** H4 report with QA gates.

| Checkpoint | Delivers | Server | Done when |
|---|---|---|---|
| **CI-A** Working indicator | Part B complete: `AtelierMark`, `WorkingLine`, status words and setting, thought ticker, Thinking closed while live, motion and accessibility | None | CI-AC1–AC6 |
| **CI-B** Image turns | Migration; `POST /chats/{id}/images`, retry, cancel; `Message.kind` and `images`; context skip; title from prompt; composer image mode (A2); image card with every frame state, develop field, progress bar and reveal (A3, A4); Save, Copy prompt, Details, Remove, Try again, Cancel; events subscription; `ImagesWorkspace` removed from the composer; Gallery "From chat" links | Yes | CI-AC7–AC16 |
| **CI-C** Viewer and iteration | Viewer (A6); More like this; Refine; Ask about it; export of image turns; phone scroll-snap row | Export only | CI-AC17–AC22 |
| **CI-D** Gated | A11 items, one at a time | — | Separate specs |

---

## D. QA

All gates in `QA-REQUIREMENTS.md` apply (G-1 to G-16). Notes:

- **G-4:** the viewer and image-mode controls are lazy where possible; the initial bundle must not grow by more than the existing allowance. `AtelierMark` and `WorkingLine` are tiny and may be in the main chunk.
- **G-6, G-7:** additive fields, routes and one migration only.
- **G-10:** golden request capture for an ordinary chat unchanged; plus a new capture for a chat containing image turns that proves they are absent from the request.
- **G-11:** image prompts in tests, fixtures and screenshots are synthetic; file names say "fake". Use the fake image worker (`server/tests/fake_image.py`).
- **G-13:** both reduced-motion triggers remove the mark loops, word slides, shimmer, develop drift, sheen, reveal and viewer zoom; frames still show the correct state and the image.
- **G-14:** `/design` shows the status line in every phase, the mark in both loops, every frame state at 1, 2 and 3 images, the composer in image and refine modes, and the viewer.

### D1. Acceptance criteria

| ID | Criterion | Evidence |
|---|---|---|
| CI-AC1 | The status line replaces the dots in every streaming state; real stages (queued, loading, search step) always win over playful words | e2e with delayed fake runtime |
| CI-AC2 | Words change every 2.4 s, follow a stable seeded order per message, never repeat until exhausted, and Plain shows "Working" | unit + e2e |
| CI-AC3 | With a reasoning fake model: the ticker shows the last ≤ 160 characters, updates without layout shift, expands and collapses, and becomes "Thought for n s" when text starts | e2e |
| CI-AC4 | Screen readers hear only phase changes (aria-live content checked) | e2e |
| CI-AC5 | Streaming performance unchanged (`performance.spec.ts` thresholds) with the indicator and ticker on | perf report |
| CI-AC6 | Reduced motion: static mark, no slides or shimmer; words still change as text | motion.spec |
| CI-AC7 | Migration upgrades the fixture database without changing existing rows; image turns survive reload and appear in branch navigation | G-7 test + e2e |
| CI-AC8 | `POST /chats/{id}/images` is idempotent per request key; a repeated uncertain request creates no duplicate jobs or messages | Python + e2e (dropped first response) |
| CI-AC9 | Image turns never reach the text model (golden capture) | Python |
| CI-AC10 | Each frame state renders from fake worker events: queued, preparing, steps 0–4, decoding, complete, cancelled, failed, interrupted, removed | e2e + /design |
| CI-AC11 | Progress segments follow `completed_steps` only; no client timers advance progress | e2e (worker paused between steps) |
| CI-AC12 | Reveal plays once for images completed this session and never for history | e2e |
| CI-AC13 | Two or three images run in order; the waiting frames show "Next" and the status line counts correctly | e2e |
| CI-AC14 | Try again creates a sibling turn with new seeds and the branch navigator; Cancel stops only that turn's jobs | e2e |
| CI-AC15 | SSE reconnect mid-generation restores the correct frame states without polling | e2e |
| CI-AC16 | The composer no longer mounts `ImagesWorkspace`; chat drafts and image drafts stay separate; `/image ` enters image mode | e2e |
| CI-AC17 | Viewer opens with the shared-element zoom from the clicked frame and closes back to it; keyboard and swipe navigation cover every image in the chat | e2e + video |
| CI-AC18 | More like this and Refine create new turns with `parent_id` set to the source job | Python + e2e |
| CI-AC19 | Ask about it is offered only for models reporting `vision` and attaches the PNG through the existing path | e2e |
| CI-AC20 | Markdown and JSON exports include image turns as specified | Python |
| CI-AC21 | Phone: three images scroll-snap with dots; actions always visible; viewer swipe and pinch work (WebKit 390) | e2e WebKit |
| CI-AC22 | Axe zero serious or critical on chat with image turns, image mode and the viewer, both themes, 390 and 1440 | axe |

### D2. Motion evidence

Short videos with synthetic data, out of Git: send with playful words then a reasoning ticker; an image turn of two images from send to reveal; Try again; viewer open, swipe, close; reduced motion on.

---

## E. Decisions for Jake

| ID | Decision | Needed before | Recommendation |
|---|---|---|---|
| J-I1 | Status words default: Playful or Plain | CI-A | Playful, with Plain in Appearance |
| J-I2 | Live reasoning shows as a one-line ticker instead of the auto-opened panel | CI-A | Yes |
| J-I3 | Images become chat turns, saved with the chat; the composer's image panel goes away | CI-B | Yes |
| J-I4 | Image turns are left out of the text model's context | CI-B | Yes. The alternative (sending the prompt as text) changes chat requests and confuses models that cannot see images |
| J-I5 | Image-first chats are titled from the prompt, without a title model call | CI-B | Yes |
| J-I6 | Each item in A11, separately | Later | Decide after CI-C is in daily use |

**`AGENTS.md`, append after Jake approves:**

> **User authorization (date) — chat images and working indicator:** build `docs/next/chat-images/CHAT-IMAGES-SPEC.md` checkpoint by checkpoint, stopping for review after CI-A, CI-B and CI-C. The working indicator uses the Atelier mark and the approved status-word setting; playful words never replace a known stage. Image turns are chat messages (`kind = 'image'`) linked to image jobs, excluded from text-model context; image-first chats are titled from the prompt without a model call. No new dependency and no new model call. Improve prompt, reference edits, image tools and other sizes are not authorized. Image prompts in tests and evidence are synthetic.

---

## F. Limits of this review

- The current image mode was seen in Jake's screenshot of the fake runtime, not on the phone. The repository was read at `dce4c49`; nothing was run or built.
- Timing figures come from the existing image reports, not new measurements.
- The develop field is a deliberate stand-in: the engine reports steps, not preview frames. If preview frames are added later, they replace the field and keep the same progress bar.
- The prototype in this folder fakes the model, the reasoning and the images (painted procedurally on a canvas). Where it and this document differ, this document wins.
