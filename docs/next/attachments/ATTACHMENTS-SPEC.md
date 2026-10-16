# Attachments and the composer: adding files on iPhone and desktop

**Written:** 15 October 2026, against commit `55477ff1` · **By:** Claude (validator) · **For:** Jake to approve, Codex to build **on its own branch**
**Reads with:** `docs/SPEC.md`, `docs/next/QA-REQUIREMENTS.md`, `docs/next/PHASE-4-POLISH-AND-MOTION.md`, `docs/next/chat-images/CHAT-IMAGES-SPEC.md` (viewer, and image mode A2)
**Reference prototype:** `prototype.html` in this folder. Open it on the Mac and on the iPhone. Pick real files (they never leave the device in the prototype), drag files onto the window, paste an image, open **Tools**, or press "Add sample files". Where it and this document differ, this document wins.

Place this folder at `docs/next/attachments/`.

**Branch rule (Jake's request):** all work happens on `codex/attachments-redesign`, created from the current `main`. Nothing is merged into `main` or published to the installed app until Jake approves. See §9.

---

## 0. The short version

Adding a file today takes two menus, shows images as file names, stacks every file as a full-width row above the message, and reports problems as toasts at the top of the screen. The tool row shows four pills all the time and wraps on the phone. This redesign makes adding a file one tap, makes files look like what they are, and gives the composer the calm shape people already know from Claude and ChatGPT:

1. **One tap.** The **+** opens the system picker directly. On iPhone that is the native Photo Library / Take Photo / Choose Files menu, anchored to the + button. The app works out the file type afterwards. The in-app "Add image / Add text file / Add document / Add recording" menu goes away.
2. **A tray, not a list.** Picked files appear as a horizontal row of tiles inside the composer: **photo thumbnails** that show instantly, and **file cards** with a type badge, the name, and real details (pages, tokens, duration). Each tile shows its own upload progress, then a small check.
3. **Problems on the file, not in a toast.** A file that is too large, unsupported, or an image on a model that cannot see images is marked on its own tile with one plain sentence and a fix ("Switch model").
4. **Drop and paste, done properly.** On desktop, dragging files over the window shows a calm drop card; pasting a screenshot attaches it; a very long paste can become a text file (decision J-U2).
5. **Sent messages show the files.** Images appear as thumbnails above your message and open in the existing image viewer; documents and recordings appear as compact cards that open their sheets.
6. **A familiar composer.** One soft, rounded box: files at the top, the message in 16 px, and one quiet row underneath with **+** and **Tools** on the left and Send on the right. Search, Library, Create image and Thinking live in the Tools menu; whatever is switched on shows as a small removable chip next to it. The empty composer is two rows on every screen size (decision J-U4). It uses Atelier's own colors, mark and wording; nothing is taken from either product's branding.

Web only. No server change, no new dependency, no new model call.

---

## 1. What is there today

From Jake's iPhone screenshots (15 October) and the source at `55477ff1`.

| # | Finding | Evidence | Effect |
|---|---|---|---|
| 1 | **Two menus to add a file.** + opens an in-app menu (Add image, Add text file, Add document (PDF, Word), Add recording); choosing one sets `accept` on a hidden input and clicks it, so iOS then shows its own menu. | `Composer.tsx` lines ~467–542 | Two decisions before seeing a file. |
| 2 | **The iOS menu floats in the middle of the screen,** detached from the button. | Screenshots: "Photo Library / Take Photo / Choose Files" over the answer text | iOS anchors its menu to the hidden input, not to +. |
| 3 | **You choose the file type first.** Images, text, documents and recordings are separate menu items; recordings even get a "Take Video" sheet. | Same menu; per-item `accept` | The app could detect the type itself (it already does in `useUploads`). |
| 4 | **Images appear as file names.** In the composer, an image is a small name chip; in a sent message, a blue file-name link. | `Composer.tsx` fallback chip; `LiveThread.tsx` ~line 409 | You cannot see what you attached. |
| 5 | **Files stack as full-width rows** above the text box, each with its own long warning paragraph. | `UploadChip`, `DocumentChip`, `AudioChip` all `mb-2 flex max-w-full` | Three files push the message box off a phone screen. |
| 6 | **Images and text files show no progress.** Documents and recordings use `uploadWithProgress`; images and text use a plain fetch. | `useUploads.ts` | A large photo looks like nothing is happening. |
| 7 | **Problems arrive as toasts,** away from the file: "Images need a vision model.", "Image limit is 20 MB.", "Library and web search can't be combined in one message." | `useUploads.ts` `toast.error`; `LiveAppShell.tsx` line 477 | Easy to miss; no fix offered. |
| 8 | **The phone tool row wraps.** + · Search · Image · Library · a lone chevron · Think, then the context ring and Send on a second row. Four pills are always visible on desktop too, whether or not they are on. | Screenshots; `Composer.tsx`, `LibraryControl.tsx` | The composer is three rows tall when empty; the controls compete with the message. |
| 9 | **The drop overlay is a dashed box with one sentence.** | `LiveAppShell.tsx` ~line 781 | Works; looks unfinished. |

What stays: type detection and limits in `useUploads`, HEIC handling and resizing in `prepareImage`, `uploadWithProgress` with cancel, document extraction and token estimates, recording transcription and its actions, the context budget check, the DocumentSheet and TranscriptSheet, and the image viewer from chat images.

---

## 2. One way in

### 2.1 The + button

- **Phone and touch** (`pointer: coarse`): the + is a 44 × 44 button with a **transparent file input laid exactly over it** (`position: absolute; inset: 0; opacity: 0`, `multiple`, `accept` = every supported type, §2.2). A tap lands on the input itself, so iOS opens its native menu anchored to the button, in one step: Photo Library, Take Photo or Video, Choose Files. Never call `.click()` on a hidden input on touch devices.
- **Desktop** (`pointer: fine`): clicking + opens the system file dialog directly with the same `accept`. Tooltip: "Attach files · ⌘U". **⌘U / Ctrl+U** opens it from anywhere in a chat.
- **Disabled** only when the tray holds 8 files (the `Send.attachment_ids` limit); the tooltip says "8 files is the limit for one message".
- In image mode the + stays hidden, as today (chat images A2).

### 2.2 Accepted types

One `accept` string built from what the server allows:

- Images: `image/*,.heic,.heif` (`image/*` is what makes iOS offer Photo Library and the camera).
- Documents: `bootstrap.attachment_extensions.document` (`.pdf`, `.docx`).
- Text: `bootstrap.attachment_extensions.text`.
- Recordings: the transcription engine's `audio_extensions`, only when `features.transcription` is on.

The app classifies each picked file with the existing rules in `useUploads` (extension and MIME, HEIF header sniffing). A file that matches nothing becomes an error tile (§3.4), not a silent drop.

### 2.3 Limits (unchanged, shown where they apply)

Images 20 MB (resized to 2048 px on the device, HEIC converted on the Mac); text files 512 KB; documents 50 MB and 1,500 pages; recordings 4 GB; 8 files per message.

---

## 3. The tray

### 3.1 Placement

Inside the composer, above the text box, as one horizontal row with 8 px gaps. It scrolls sideways when it overflows (scroll-snap to tiles, no visible scrollbar, a 24 px fade on the overflowing edge). Badges and remove buttons sit inside the tiles, so nothing is clipped by the scroll area. When several files are added at once, the tray keeps the first new tile in view. The tray is absent when there are no files, so the empty composer does not change.

```
┌───────────────────────────────────────────────────────────────────────────┐
│ ┌──────┐ ┌──────┐ ┌───────────────────────┐ ┌───────────────────────┐     │
│ │ img  │ │ img ◔│ │ PDF  Spring-plan.pdf  │ │ M4A  Team sync.m4a     │ ›  │ ← tray (scrolls)
│ │    ✕ │ │    ✕ │ │      12 pages · ≈8.4k │ │      Transcribing 1:12 │     │
│ └──────┘ └──────┘ └───────────────────────┘ └───────────────────────┘     │
│ Message gemma4:27b-vision-32k…                                            │ ← text box, 16 px
│ (+) (🔧 Tools)  [🌐 Search ✕] [🧠 Think · Xhigh ✕]                   ◌   (↑)   │ ← tool row (§6)
└───────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Photo tile

- 72 × 72 px (64 × 64 on phones), `--radius-md`, 1 px `--line`, `object-fit: cover`.
- The thumbnail appears **immediately** from a local object URL of the picked file (before resizing or upload). HEIC files that the browser cannot draw show a neutral tile with the `Image` icon and "HEIC" until the server's converted copy is ready; then `/api/attachments/{id}` replaces it.
- Remove: a 22 px ✕ circle **inside** the top-right corner (4 px inset, black at 62% with a white ✕). With a mouse it appears on hover or focus; on touch it is always visible. Its hit area is 36 × 36 px and must never reach the center of the tile, so tapping the photo opens it rather than removing it.
- Warning and error badges (`!`) sit inside the top-left corner.
- Tap or click opens the image in the existing image viewer (chat images CI-C), with all photo tiles in the tray as the set.

### 3.3 File card

- 232 × 72 px (208 × 64 on phones), `--radius-md`, `--surface-2` fill, 1 px `--line`.
- Left: a 40 × 40 **type badge** with the extension in 10 px Geist Mono caps on a tinted tile. Tints reuse the category tokens from Workflow Studio §7.1: PDF `--cat-review`, Word `--cat-ai`, text and code `--cat-input`, CSV and JSON `--cat-knowledge`, recordings `--cat-media`.
- Right: the name on one line with a **middle ellipsis** that keeps the end of the name and the extension ("Spring-ma… -2026.pdf"), then one meta line in 12 px `--text-2`. Build the ellipsis in CSS so it adapts to the width: the name is two spans in a flex row, the start shrinks with `text-overflow: ellipsis`, the end never shrinks. The end starts at the last space, hyphen, underscore or opening bracket within 10 characters before the extension (otherwise the last 4 characters plus the extension). Both spans use `white-space: pre` so spaces survive. The full name is the tooltip and the accessible name.
  - PDF: "12 pages · ≈8,400 tokens"; Word: "Word · ≈2,100 tokens"; text: "Markdown · 18 KB"; CSV: "CSV · 18 KB".
  - Recording: the existing AudioChip status text, shortened: "Queued", "Transcribing 1:12", "Ready · 12:04", "Cleaning up 3 of 8", "Cleaned".
- Tap or click opens DocumentSheet, TranscriptSheet, or a plain text preview for text files.
- Recording actions (Cancel transcription, Transcribe again, Clean up, Download) move into a ⋯ button in the card's bottom-right corner; the ✕ stays top-right for removal.

### 3.4 Tile states

| State | Photo tile | File card | Announced (aria-live polite) |
|---|---|---|---|
| Preparing (resizing, HEIC check) | Thumbnail at 60% opacity, small spinner | — | "Preparing {name}" |
| Uploading | Thumbnail at 60% opacity, 24 px progress ring in the center | 2 px progress bar along the bottom edge; meta "Uploading 45%" | "Uploading {name}" once |
| Reading (upload done, server extracting) | — | Bar full; meta "Reading pages…" with the existing activity shimmer | — |
| Ready | Ring scales out, a 16 px check pops and fades (600 ms total) | Meta shows details | "{name} attached" |
| Warning (attached, but blocks sending) | Amber 2 px ring, `!` badge | Amber border, `!` badge | The reason |
| Error (not attached) | Red 2 px ring, `!` badge, image dimmed | Red border, `!` badge, meta shows the reason | The reason |

Every warning or error is also written once in a **status line** under the tray, in 12.5 px with the matching color and an action when there is one. Rules:

- Warnings come before errors. Issues of the same kind are grouped into one line ("…or remove the 2 photos.").
- When more than one kind is present, the line ends with a quiet "+1 more".
- Hovering or focusing a flagged tile shows that tile's line instead.
- **On phones only the first sentence shows** ("qwen3.8 can't see images. Switch model"), so the line stays on one row.

| Situation | Status line | Action |
|---|---|---|
| Image, model cannot see images | "{model} can't see images. Switch to a model that can, or remove the photo." | **Switch model** (menu of models that report `vision`) |
| Document over the input allowance | "‘{name}’ is about {n} tokens; this model takes {m} after reserving {r} for the answer." | **Chat controls** |
| Too large | "‘{name}’ is over {limit}." | Remove |
| Unsupported | "Can't attach .{ext} files. Images, PDF, Word, text and recordings work." | Remove |
| Recordings unavailable | "Recordings need the transcription engine." | **Settings** |
| Unreadable image | Existing copy: "Couldn't open this image. Export it as a JPEG or PNG and try again." | Remove |
| Network | "‘{name}’ didn't finish uploading." | **Retry** |

Error tiles are not attached and do not block sending. They clear when removed, when the message is sent, or automatically 8 s after they appear; the timer waits while the tile or the status line is hovered or focused. Warning tiles block sending until fixed or removed (today's behavior for oversize documents, now also used for images on non-vision models instead of refusing them).

### 3.5 Count and Send

- At 5 or more files, the tray ends with a quiet "5 of 8". At 8, the + dims and says why in its tooltip; files added beyond 8 become error tiles ("8 files is the limit for one message.").
- While anything is preparing, uploading, reading or transcribing, Send shows a thin progress ring around its arrow with the combined upload progress (transcription shows an indeterminate ring), and its tooltip says "Waiting for 2 files". You can keep typing. This replaces silent disabling.

---

## 4. Drop and paste

### 4.1 Drop (desktop, and iPad with a pointer)

- Entering the chat area with files shows an overlay: `--bg` at 72% over the thread and a centered **drop card** (360 × 196 px, `--surface`, 2 px dashed `--brand` border, `--radius-xl`, `--shadow-lg`). Inside: three small type badges fanned out (photo, PDF, text) that bob gently while the drag is held, "Drop to attach" in 16 px 500, and "Images, PDF, Word, text and recordings · up to 8 files" in 12 px `--text-3`.
- During the drag the composer sits above the scrim, and when the pointer is over it its border turns `--brand`.
- On drop, the overlay fades and the tiles pop into the tray.
- Dropping onto Workflows, Settings or other routes keeps their own behavior (Library pane, workflow inputs).

### 4.2 Paste

- **Files and images** in the clipboard (screenshots included) become tiles. Pasted images get names like "Pasted image 1.png".
- **Long text** (decision J-U2): when a paste is longer than 4,000 characters, it becomes a text file tile "Pasted text 1.txt · 12,400 characters", and a one-line note under the tray says "Long paste attached as a file. **Keep as text**" (undo puts the text in the box). The note stays for 10 s. Shorter pastes behave as today.

---

## 5. Files in the thread

### 5.1 Your message

Attachments render **above** your bubble, right-aligned, in the order they were added:

- **Photos:** one photo shows at up to 240 × 240 px (aspect kept, `--radius-lg`); two show side by side at 160 px; three or more form a grid of 112 px squares, at most 6 visible, the last showing "+{n}". Clicking opens the image viewer with this message's photos as the set.
- **Files:** read-only file cards (§3.3) at 240 × 60 px with no ✕. On desktop they wrap two to a row, right-aligned, with 6 px gaps (at most 486 px wide); on phones they stack. Clicking opens the same sheets as in the composer.
- The optimistic pending row (before the server confirms) shows the same tiles from local previews, so nothing flickers when it becomes real.

### 5.2 History and branches

Rows loaded from history never animate (C2). Thumbnails use `loading="lazy"` and `decoding="async"`; their boxes have fixed sizes, so the thread does not jump while images load.

---

## 6. The composer and its tools

The composer takes the shape people already know from Claude and ChatGPT, built from Atelier's own tokens. It does not copy either product's colors, logo, icons or wording.

```
Empty (desktop and phone: two rows)
┌───────────────────────────────────────────────────────────────────────────┐
│ Message gemma4:27b-vision-32k…                                            │
│ (+) (🔧 Tools)                                                     ◌  (↑) │
└───────────────────────────────────────────────────────────────────────────┘

With tools on                                         Tools menu (opens upward)
│ (+) (🔧 Tools)  [🌐 Search ✕] [🧠 Think · Xhigh ✕]     ┌──────────────────────────────┐
                                                     │ TOOLS                        │
                                                     │ 🌐 Search the web        ◯━  │
                                                     │ 📖 Library               ━◯  │
                                                     │ 🖼 Create image               │
                                                     │ ──────────────────────────── │
                                                     │ 🧠 Thinking                   │
                                                     │ [Auto|Off|Low|Medium|Xhigh]      │
                                                     └──────────────────────────────┘
```

### 6.1 The box

- `--surface`, 1 px `--line-strong`, **24 px radius**, `--shadow-composer`, 12 px padding (10 px on phones).
- Focus inside the box: the border moves to `--line-input` and a soft 4 px halo of `--line-strong` at 35% appears (200 ms).
- The text box is **16 px** (this also stops iOS Safari from zooming when the box is focused), at least 48 px tall on desktop and 30 px on phones, growing to 200 px. The placeholder stays "Message {model}…".
- Image mode keeps the chat images A2 look: the border tints to `--brand` at 40%.

### 6.2 The tool row

Left to right: **+** (§2.1) · **Tools** · active-tool chips · space · context ring · Send.

- **+** and **Tools** are outlined circles/pills (1 px `--line-strong`, transparent fill, `--surface-2` on hover): 36 px on desktop, 44 px on phones. Tools shows the `Wrench` icon and the word "Tools" on desktop, the icon only on phones. It is a menu button (`aria-haspopup="menu"`, `aria-expanded`).
- **Send** stays the cobalt circle with the waiting ring from §3.5.
- The four always-visible pills (Search, Image, Library, Think) go away.

### 6.3 The Tools menu

A popover above the button, 328 px wide (never wider than the screen minus 24 px), `--radius-md`, `--shadow-lg`. It stays open while you change things and closes on outside click, Escape (focus returns to Tools) or choosing Create image.

| Row | Control | Behavior |
|---|---|---|
| Search the web · "Look things up while answering" | Switch | Same as today's Search toggle |
| Library · "Answer from your saved files" | Switch | Same as today's Library toggle; scope is chosen from its chip |
| Create image · "Describe it and get pictures in the chat" | — | Enters image mode (chat images A2); same as typing `/image ` |
| Thinking | Segmented: Auto · Off · Low · Medium · Xhigh | Today's Think menu and its levels (Model default, Off, Low, Medium, Xhigh); "Model default" is shown as Auto with the full name as its tooltip. Hidden when the model has no thinking control |

Search and Library stay one at a time. Switching one on switches the other off, and a one-line note under the composer says so for 4 s ("Search is off while Library is on. They work one at a time."). The toast goes away.

### 6.4 Active-tool chips

- A chip appears for each tool that is on and differs from the default: **Search**, **Library** (or the scope's name, with a ▾), **Think · Low**, **Think · Medium**, **Think · Xhigh** or **No thinking**. Thinking on Auto shows no chip.
- Chip: 32 px tall (36 px on phones), fully rounded, `--brand-soft` fill, `--brand` text, icon + label + a 24 px ✕ (30 px on phones). On phones the label is hidden; the icon and ✕ remain.
- Tapping the ✕ turns that tool off (Thinking returns to Auto) and moves focus to Tools. Tapping the Library chip opens "Search files in" with the scopes and "Turn Library off". Tapping any other chip opens the Tools menu.
- At 390 px the worst case (Library and Thinking on) fits on one row with the context ring and Send.

### 6.5 Image mode

Unchanged from chat images A2, except the entry point: **Create image** in Tools (or `/image `). In image mode, +, Tools, the tray, the context ring and the other chips are hidden. The row shows A2's Image chip (✕ leaves), the count pill and ⋯. Escape in an empty prompt leaves, as A2 says.

---

## 7. Motion

Phase 4 rules: CSS only, 200 ms or less for small things, 320 ms or less for large surfaces, keyframes in `motion.css`, everything off under both reduced-motion triggers.

| Moment | What moves | Duration | Easing | Reduced motion |
|---|---|---|---|---|
| Tile appears | Scale 0.92 → 1, opacity 0 → 1, staggered 40 ms for multiple files | 160 ms | `--ease-pop` | Instant |
| Tile removed | Opacity → 0 and scale 0.92 (120 ms), then its width collapses so neighbors slide over | 120 + 200 ms | `--ease-in`, `--ease-out` | Instant |
| Upload progress | Ring `stroke-dasharray` and bar `width` follow progress | 120 ms per update | linear | Jumps |
| Upload done | Ring scales out; check pops in (scale 0.6 → 1), holds, fades | 600 ms total | `--ease-pop` | Check appears and goes |
| Reading | Existing activity shimmer on the meta line | 1.6 s loop | linear | None |
| Drop overlay | Scrim and card fade in; card scale 0.98 → 1 | 120 ms / 200 ms | `--ease-out` | Instant |
| Drop card badges | Three badges bob 3 px, staggered | 1.6 s loop | ease-in-out | Still |
| Status line | Fades and rises 4 px | 200 ms | `--ease-out` | Instant |
| Send ring | `stroke-dasharray` follows combined progress | 120 ms | linear | Jumps |
| Tools menu | Fades in, rises 4 px, scale 0.97 → 1 | 120 ms | `--ease-out` | Instant |
| Switch | Knob slides 12 px; track color changes | 120 ms | `--ease` | Instant |
| Chip appears | Scale 0.92 → 1, opacity 0 → 1 (chips already shown do not replay) | 160 ms | `--ease-pop` | Instant |
| Composer focus | Border color and halo | 120 / 200 ms | `--ease` | Instant |

No new keyframe property is needed (`transform`, `opacity`, `width`, `stroke-dasharray` are already allowed by `check_motion.py`). Border, halo and switch changes are transitions, not keyframes.

---

## 8. Build notes

**Files.**
- New `web/src/components/chat/AttachmentTray.tsx` (tray, scroll, count, status line), `AttachmentTile.tsx` (photo tile and file card, all states), `DropOverlay.tsx`, `MessageAttachments.tsx` (thread rendering), `ToolsMenu.tsx` (Radix DropdownMenu with switch rows and the Thinking segmented control), `ToolChips.tsx`, `web/src/lib/file-kinds.ts` (one place for classification, labels, tints and the `accept` string).
- `useUploads.ts`: every upload goes through `uploadWithProgress` (images and text included), with a local object URL created at pick time and revoked on removal or after the server copy loads; errors become tile states instead of `toast.error`; images on non-vision models are uploaded and flagged (warning) instead of refused.
- `Composer.tsx`: remove the attachment `DropdownMenu` and the four tool pills; add the overlaid file input on touch and the direct dialog plus ⌘U on desktop; render `AttachmentTray`, Tools and `ToolChips`; the box, text size and focus halo from §6.1; Send gets the progress ring and tooltip. The existing state for search, library scope, thinking level and image mode is reused unchanged; only the controls move.
- `DocumentChip.tsx` and `AudioChip.tsx` keep their logic and become the file card's data and actions (no long inline paragraphs; reasons move to the status line).
- `LiveAppShell.tsx`: `DropOverlay` replaces the dashed box; the Library/Search toast becomes the composer note.
- `LiveThread.tsx`: `MessageAttachments` above the user bubble, replacing file-name links and stacked chips.
- `LibraryControl.tsx`: its scope menu is reused by the Library chip; the separate button and chevron go away.

**Server.** None. `/api/attachments/{id}` already serves the stored image for thumbnails. If phone thumbnail weight becomes a measured problem, a thumbnail endpoint is a separate, later change.

**Privacy (G-11).** Test fixtures and screenshots use synthetic files with "fake" in their names. Never capture the iOS document picker, which shows real file names.

---

## 9. Branch and release

| Step | Who | What |
|---|---|---|
| 1 | Codex | `git switch main && git pull --ff-only` (if a remote is configured), then `git switch -c codex/attachments-redesign`. Record the base commit in the report. |
| 2 | Codex | All commits for AT-A and AT-B go on that branch only. Add the `AGENTS.md` amendment (§12) on the branch. |
| 3 | Codex | Push the branch (`git push -u origin codex/attachments-redesign`) and, if `gh` is available, open a **draft** pull request against `main` titled "Attachments redesign (AT-A, AT-B)". Never merge it. |
| 4 | Codex | Do not run the publisher, change the installed app, restart the service, or touch `main`. Verify with `make check`, `make e2e` (Chromium and WebKit, including iPhone 390 px) and the fake runtime only. |
| 5 | Jake | Reviews the report, screenshots and videos, and tries the prototype on the phone. |
| 6 | Codex, after Jake says so | Merge with `git merge --no-ff codex/attachments-redesign` on `main`, publish with the existing static-only publisher (web assets only; server hashes unchanged), keep the private rollback, then ask Jake for the five-minute phone check (QA §7). |

---

## 10. Checkpoints

**Stop for review after each.** H4 report with QA gates.

| Checkpoint | Delivers | Done when |
|---|---|---|
| **AT-A** One way in, the tray and the composer | §2, §3, §6: one-tap +, ⌘U, `file-kinds.ts`, tray with photo tiles and file cards in every state, status line, Send ring, progress for every upload, warnings instead of refusals, the new box, Tools menu and chips, Library/Search note | AT-AC1–AC9, AT-AC16 |
| **AT-B** Drop, paste and the thread | §4, §5: drop overlay, pasted images, long paste as a file (if J-U2), thumbnails and cards in sent messages, viewer and sheets from the thread | AT-AC10–AC15 |

---

## 11. QA

All gates in `QA-REQUIREMENTS.md` apply. Notes: G-6, G-7, G-8, G-9 and G-10 must show **no change** (web only). G-4: the tray and overlay are small; the viewer is already lazy. G-13: every loop and transition stops under both reduced-motion triggers. G-14: `/design` shows every tile state for photos and each file type, the tray at 1, 4 and 8 files, the status line for each situation in §3.4, the drop overlay, the Send ring, the composer empty, focused and in image mode, the Tools menu, each chip, and sent messages with 1, 2, 3 and 7 photos plus files. G-10: the request body for a message sent with each tool combination is identical to the same combination sent before the change.

| ID | Criterion | Evidence |
|---|---|---|
| AT-AC1 | One tap on + opens the system picker on WebKit touch (no in-app menu); the input covers the button | e2e WebKit iPhone profile: element at the + center is the file input |
| AT-AC2 | Desktop + and ⌘U open the dialog with the combined `accept`; recordings are included only when transcription is on | e2e |
| AT-AC3 | Mixed picks are classified correctly: photo, HEIC, PDF, DOCX, text, CSV, recording, unsupported | unit tests on `file-kinds.ts` with synthetic files |
| AT-AC4 | Photo thumbnails appear before upload finishes; object URLs are revoked on removal and after the server copy loads | e2e + unit |
| AT-AC5 | Every upload shows progress and can be cancelled from its tile; the final state matches the server | e2e with a throttled fake upload |
| AT-AC6 | Each §3.4 situation shows the right tile state and status line, with no toast | e2e |
| AT-AC7 | An image on a non-vision model is kept with a warning that blocks Send; Switch model clears it | e2e |
| AT-AC8 | Send shows the waiting ring and tooltip while any file is in progress, and sends once everything is ready | e2e |
| AT-AC9 | At 390 px the empty composer is two rows (text box and one tool row), and stays one tool row with Library and Thinking chips on; the text box is 16 px (no zoom on focus); the Library/Search note replaces the toast | e2e WebKit 390 + screenshot |
| AT-AC10 | Dragging files over the chat shows the drop card; dropping adds tiles; leaving or Escape hides it; other routes keep their own drop behavior | e2e |
| AT-AC11 | Pasting a screenshot adds a photo tile; pasting text over 4,000 characters becomes a text file with a working Keep as text (if J-U2) | e2e |
| AT-AC12 | Sent messages show photos as a grid and files as cards, with fixed boxes (no layout shift on load) | e2e + CLS check |
| AT-AC13 | Photos in a sent message open the viewer with that message's photos; files open their sheets | e2e |
| AT-AC14 | The optimistic row shows the same tiles as the confirmed row (no flicker) | e2e |
| AT-AC15 | Axe zero serious or critical on the composer with tiles in every state, the Tools menu, chips, the drop overlay and sent messages, both themes, 390 and 1440 | axe |
| AT-AC16 | Tools opens with click, Enter and Space; arrow keys move through rows; switches and the Thinking control are announced with their state; Escape closes and returns focus; each chip's ✕ turns its tool off and returns focus to Tools; Create image enters A2 image mode | e2e + keyboard test |

---

## 12. Decisions for Jake

| ID | Decision | Recommendation |
|---|---|---|
| J-U1 | One-tap + with the system picker; the in-app type menu goes away | Yes |
| J-U2 | Pastes longer than 4,000 characters become a text file, with "Keep as text" to undo | Yes |
| J-U3 | Images on a model that cannot see images are kept with a warning and a Switch model button, instead of being refused | Yes |
| J-U4 | The composer takes the familiar shape (§6): Search, Library, Create image and Thinking move into one Tools menu, and what is on shows as removable chips. The four always-visible pills go away | Yes |
| J-U5 | Build on `codex/attachments-redesign`; merge and publish only after you approve | Yes (your request) |

**`AGENTS.md`, append on the branch after Jake approves:**

> **User authorization (date) — attachments and composer redesign:** build `docs/next/attachments/ATTACHMENTS-SPEC.md` on branch `codex/attachments-redesign` only, stopping for review after AT-A and AT-B. Do not merge into `main`, publish, restart or change the installed app until Jake approves the merge. Web only: no server, schema, prompt, model-call or dependency change; the composer reuses its existing state and request fields. Test files and screenshots are synthetic; never capture the device file picker.

---

## 13. Limits of this review

- Based on Jake's iPhone screenshots and the source at `55477ff1`; the desktop drop flow and the in-app chips were read in code, not used live. Nothing was run.
- iOS decides the exact items in its native menu (for example "Take Photo or Video" when recordings are accepted); the app controls only the `accept` list and where the input sits.
- The prototype fakes uploads and server details (pages, tokens, durations). Files you pick in it stay in the browser. Image mode in the prototype only shows the entry and the chip; the full A2 behavior is in the chat images prototype.
- "Like Claude or ChatGPT" is taken as their shared layout pattern (rounded box, files inside, + and a tools menu on the left, Send on the right, active tools as chips), not their visual identity.
