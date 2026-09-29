# SPEC v2.1: themes, fonts, popups, launch intro, offline

**Approved by Jake on 29 Sep 2026.** This builds on the v2 handoff in `docs/design-handoff/` and doesn't replace it.

**The target renders** are `reference/screens/20–37`. The mockup sources are in `reference/canvas/`, and they hold the exact spacing and copy.

**Jake's decisions (29 Sep):**

1. Ship all four themes, and add font choices.
2. Accent is Claude's call. It's a user setting with three options: Cobalt (the default), Amber and Graphite.
3. The launch intro is a setting. It defaults to "Every launch", and "Only when something's slow" is the alternative.

The non-negotiables from v2 still apply:

- zero-build vanilla JS;
- CSP-clean, with no inline styles;
- additive API changes only;
- never show a value the backend didn't provide;
- WCAG 2.2 AA;
- every existing flow keeps working.

---

## 1. Appearance settings

### 1.1 Where it lives

- **The Settings dialog.** Add a `<dialog id="settings-dialog" class="settings-dialog">` with a left section list: General, Appearance, Models, Tools & agents, Privacy, About.
  - Only **Appearance** is new content.
  - The other sections can link to the existing views for now.
- **Title bar.** The theme button (`#theme-toggle`) becomes **Appearance** (`aria-label="Appearance"`). It opens Settings at Appearance.
- **Keyboard.** `⌘,` (or `Ctrl+,`) opens Settings.
- **Phone.** Below 640 px, Settings goes full-screen. The section list is one screen, and each section is a second screen with a back button.

### 1.2 Controls

| Control | Values (default in bold) | Applies as |
|---|---|---|
| Theme | **System**, Graphite Dark, Graphite Light, Midnight, Paper | `html[data-theme]` = the *resolved* theme |
| When System is chosen: light theme | **Graphite Light**, Paper | used when `prefers-color-scheme: light` |
| When System is chosen: dark theme | **Graphite Dark**, Midnight | used when `prefers-color-scheme: dark` |
| Accent | **Cobalt**, Amber, Graphite | `html[data-accent]` (omit it for cobalt) |
| Interface font | **Geist**, Atkinson Hyperlegible, System | `html[data-font-ui]` |
| Answer font | **Newsreader**, Literata, Geist, Atkinson | `html[data-font-read]` |
| Answer size | S, **M**, L | `html[data-text-size]` |
| Increase contrast | **off** (turned on automatically when the OS asks for more contrast and the user hasn't chosen) | `html[data-contrast="more"]` |
| Reduce motion | **follow the OS** / on | `html[data-motion="reduce"]` |
| Launch intro | **Every launch**, Only when something's slow, Off | read by the launch code (§3) |

**What the controls look like:**

- **Theme cards** (`.theme-card`, `aria-pressed`) show a 62 px swatch built from that theme's own tokens.
  - Put `data-theme` and `data-accent` on the swatch element itself. The token selectors aren't limited to `<html>`, so the swatch paints itself.
  - The System card shows a split swatch of the two themes it will switch between.
- **When System is selected,** a panel appears under the grid with the two pickers. Below them goes the line "This device is dark right now, so you're seeing Midnight."
- **The other controls:**
  - Accents are pill buttons with a dot.
  - Fonts and size are segmented controls (`.seg`, `aria-pressed` on each option).
  - Increase contrast and Reduce motion are switches (`role="switch"`, `aria-checked`).
- **The live preview** under Fonts shows one answer sentence with a citation pill, in the chosen font and size.
- **No Save button.** Changes apply instantly; the dialog has Close only.

**Rules:**

- **Size applies to reading text only.** S, M and L scale answers and evidence passages; UI chrome doesn't change.
- **The phone composer input stays at 16 px,** because anything smaller makes iOS zoom in.
- **Font swaps keep the apparent size.** Each reading font carries an optical scale (`--read-font-scale` in `tokens-themes.css`), so switching fonts doesn't make answers jump in size.
- **"Geist" as the answer font uses the current interface font,** so Atkinson for UI plus Geist for answers stays consistent.

### 1.3 Persistence and boot (no flash of the wrong theme)

**Storage.** Store everything in `localStorage["agenticrag.appearance"]`:

```json
{"v":1,"theme":"system","light":"light","dark":"dark","accent":"cobalt","fontUi":"geist","fontRead":"newsreader","textSize":"m","contrast":"auto","motion":"auto","intro":"always"}
```

**Migration.** Carry over the existing `agenticrag.theme` value (`dark`/`light`) once, as `theme`, then delete the old key.

**The boot script.** Add `ui/boot.js`, loaded **synchronously** as the first script in `<head>`, before the stylesheets. CSP allows it because it's `'self'` and not inline. It:

1. Reads the settings. Any error falls back to the defaults, so wrap it in try/catch; it must never throw.
2. Resolves System using `matchMedia('(prefers-color-scheme: dark)')`.
3. Sets every `data-*` attribute on `<html>`.
4. Sets `<meta name="theme-color">` to the theme's `--theme-color`. Use these hex values: dark `#0C0C0D`, midnight `#000000`, light `#FAFAF8`, paper `#F5F0E6`. At boot time CSS might not be parsed yet, so don't read the value from `getComputedStyle`.
5. Sets `html[data-launch="on"]` when the intro should show (§3.1).

**Also:**

- `app.js` listens to the `prefers-color-scheme` and `prefers-contrast` media queries and re-resolves live.
- Settings are per device: the phone and the Mac can differ, and that's intended.
- Fix `manifest.webmanifest`: its `background_color` and `theme_color` are still the old navy `#090e18`. Use `#0C0C0D`.

### 1.4 Fonts

**New files** in `fonts/` (SIL OFL 1.1, licences included):

- Literata, variable, with opsz + wght axes: Latin, Latin Extended and Italic.
- Atkinson Hyperlegible Next, variable: Latin, Latin Extended and Italic.

**System** needs no file. It uses `-apple-system`, which is SF Pro on Apple devices.

**Loading:**

- The `@font-face` rules use `font-display: swap`.
- Browsers only download a face when text actually uses it, so unused choices cost nothing.
- The service worker (§4.3) pre-caches only the default faces. Other faces are cached the first time they're used.

**Code font:** stays Geist Mono, with no setting.

### 1.5 Themes and accents: tokens and contrast

- **All values are in `tokens-themes.css`.** Midnight and Paper define the full token set with the same variable names as Dark and Light.
- **Every combination passes WCAG AA.** That's 4 themes × 3 accents × normal/increased contrast = 24 combinations, checked by `tools/check_contrast.py`:
  - body, secondary and muted text ≥ 4.5:1 on every surface;
  - text on the primary fill ≥ 4.5:1;
  - the primary fill and the focus ring ≥ 3:1 against every surface.
- **Amber in the light themes is darker (`#BB6E0A`) than in the mockup.** The mockup's `#E8962A` fill fell below 3:1 on Paper.
- **Destructive buttons use `--danger-fill: #C93A31`** with white text (5.1:1) in every theme.

---

## 2. The popup system

### 2.1 Types and when to use each

| Type | Use for | Blocks? | Build it as |
|---|---|---|---|
| **Dialog** | A decision the user must make now: delete, a tool approval, connection forms, Settings | Yes | Native `<dialog>` + `showModal()` (focus trap, Esc and top layer built in) |
| **Sheet** | The phone form of a dialog (≤ 640 px) | Yes | The same `<dialog>` with `.as-sheet` |
| **Inline card** | The agent needs something, but the conversation remains the context: a question, or an approval on its way | No | An element in the thread |
| **Toast** | Result or status reports | No | `#toast-region` |
| **Menu** | Actions on one object (a chat row, a source row) | No | A button with `aria-haspopup="menu"` + `role="menu"` |
| **Popover** | Details anchored to a control (runtime status, model picker) | No | An anchored panel; the model picker is a `listbox` |
| **Tooltip** | A short label for a control or badge. Never essential information | No | Shown on hover or focus after 400 ms; not shown on touch |

**Rules for all popups:**

- **One modal at a time.**
- **Esc closes the top popup,** and focus returns to whatever opened it.
- **Clicking outside closes** menus, popovers and tooltips, but not dialogs.
- **Motion:**
  - Dialogs fade and scale from 0.96 to 1 over 220 ms.
  - Sheets slide up over 320 ms.
  - Toasts rise 8 px and fade in.
  - With reduced motion, everything only fades.
- **Stacking order:** dialogs and sheets sit in the top layer. Popovers are at `--z-popover`, toasts at `--z-toast` and tooltips at `--z-tooltip`.
- **The backdrop** uses `var(--scrim, rgba(0,0,0,.55))`. Older Safari doesn't pass custom properties to `::backdrop`, so give it a literal fallback.

### 2.2 The confirm dialog (replaces `window.confirm`)

**Where.** `app.js` still calls `window.confirm` in `deleteChat()` ("Delete this conversation and all its messages?…"). Replace it with a `confirmDialog({title, body, confirmLabel, danger:true})` that returns a promise.

**Copy.** The title is a question. The body states the consequence. The copy for deleting a chat is:

> **Delete this chat?**
> "Least-cleanup recipe" and its answers will be removed from your Mac mini. Your sources aren't affected.
> [Cancel] [Delete chat]

**Behaviour:**

- Focus starts on **Cancel**.
- Enter doesn't trigger the destructive button unless it has focus.
- The destructive button uses `.btn-danger`.

**Undo vs confirm.** Deleting a chat is permanent in the backend today, so keep the confirmation. If DATA-CONTRACT **B15** (soft delete) ships, switch Delete chat to "delete immediately + **Undo** toast for 8 s" and drop the dialog.

### 2.3 Tool approval (dialog on desktop, sheet on phone)

**When it appears.** It appears when a run reaches `waiting_for_user` for an approval (see agent roadmap A7/E1). Build the component now; wire it in when the backend event exists.

**Content comes from the event.** Never write this copy from the model's own text:

- the tool name (`web.fetch`), in mono;
- a summary of the arguments (for example, the URL);
- "Agentic run · step 3 of 8";
- a one-line reason, taken from the action's `purpose`, but limited in length and shown as quoted data;
- a **host-computed** statement of what leaves the Mac mini ("Only this address leaves your Mac mini. Sources and memory stay private.").

**Buttons.** **Deny**, **Always for this site** and **Allow once**.

- Initial focus goes to **Deny**, the safe choice.
- On phone, stack them as full-width 48 px buttons: Allow once, Deny, then "Always allow ⟨site⟩" as a text button.

**Dismissing it.** Esc or the scrim closes the dialog but **doesn't deny**.

- The run keeps waiting.
- The same request stays in the thread as an inline card, so it can be answered later.
- The chat's history row shows "Waiting for you".

### 2.4 Agent question (an inline card)

**When.** It appears when the agent calls `ask_user` (roadmap D4).

**Layout:** a card with a `--primary-line` border, containing:

- the label "The agent has a question" with a **Paused** chip;
- the question itself, in the reading font;
- up to 4 choice buttons, numbered 1–4, where the number key picks one while the card has focus;
- a free-text input with a send button;
- the footer "3 of 8 steps used. The run waits for your answer."

**The composer.** Its placeholder changes to "Answer the agent…". Sending from the composer answers the question.

### 2.5 Toasts (replace `toast(message, isError)`)

**API:**

```js
toast({ kind: "success" | "info" | "error" | "progress", title, detail?, action?: { label, run }, duration? })
```

Returns `{ update(patch), dismiss() }`. `progress` is used for things like "Reconnecting…" and is updated in place.

**Durations:**

- success and info: 5 s;
- a toast with an action (Undo or Retry): 8 s;
- **error:** stays until dismissed;
- progress: stays until updated.

Hovering or focusing a toast pauses its timer.

**Semantics:**

- the region is `aria-live="polite"`;
- errors use `role="alert"`;
- never let a toast be the only place important information appears.

**Placement:**

- desktop: bottom-left, starting beside the sidebar;
- phone: above the composer (`--composer-h` + 8 px + the bottom safe area);
- at most 3 visible, newest at the bottom.

**While a modal is open:** queue toasts until it closes. The exception is errors about that dialog, which render inline inside the dialog.

**Copy used by this release:**

- "Source added · ⟨file⟩"
- "Chat deleted · Undo" (only with B15)
- "Back online · Mac mini reconnected after N min"
- "Reconnecting… · Your run keeps going on the Mac mini"
- "Couldn't save the note · Retry"

### 2.6 Menus, popovers and tooltips

**Menus:**

- Arrow keys move between items (roving focus), Enter activates, and Home/End jump to the first and last items.
- Destructive items go last, after a separator, and use `.menu-item.is-danger`.
- Keyboard hints sit on the right.
- Menus flip to stay inside the viewport.
- On phone, a menu with more than 4 items becomes a sheet.

**Chat row menu:** Rename, Pin to top, Move to project…, Export as Markdown, then a separator, then Delete chat.

**Model picker popover:**

- The first row is **Auto**, only once the router exists (agent roadmap C). Until then, leave it out.
- Each model row shows a status dot and its display name, plus a mono line with the typical time from the evaluation report, and "not loaded" or "unloads others" when the registry says so.
- The footer names where the times come from, for example "Times from your 28 Sep check: Fixed RAG, 8 questions."
- If there's no report, show no times rather than invented ones.

**Tooltips:** use `aria-describedby`. Example: the badge "Review passed" gets the tooltip "Checked by the review step · 0 unsupported claims".

---

## 3. The launch intro

### 3.1 When it shows

**Cold start only.** That means the document loading: opening the Home Screen app, a reload, or the first visit.

**Resume from background doesn't replay it.** On `visibilitychange` to visible, run the same checks quietly, and show a toast only if the status changed ("Back online", or "LM Studio isn't responding").

**The Launch intro setting:**

| Setting | Behaviour |
|---|---|
| **Every launch** (default) | The overlay shows from the first paint and stays at least **900 ms**, so the mark and all three checks are seen, then fades out. When everything is warm it lasts about 1 s in total. |
| **Only when something's slow** | `boot.js` doesn't set `data-launch`. If the checks haven't all passed after **400 ms**, or one fails, the overlay fades in and continues from the current state. Otherwise the app just appears. |
| **Off** | No overlay. Problems show through the in-app states (§4). |
| **Reduce motion (any setting)** | No scale, draw or pop animation; a 150 ms fade only. The checks and timings are the same. |

### 3.2 Structure

**Markup.** The overlay is static markup in `index.html`: `<div class="launch" id="launch" role="status" aria-live="polite">`, containing:

- the mark (`aria-hidden`);
- the wordmark;
- three rows (`.launch-row[data-state]`);
- the status line;
- an actions slot.

`html[data-launch="on"]` shows it before `app.js` runs.

**Behaviour:**

- `app.js` initialises underneath as usual. The intro must never delay app loading.
- Any key press or a tap on the overlay skips straight to the app once the Mac mini check has passed. Don't trap the user.
- The **Replay intro** button in the mockup is a design control. **Don't build it.**

### 3.3 The checks, all started at once

| Row | Source | Detail text by state |
|---|---|---|
| **Mac mini** · "on your tailnet" | `GET /api/v1/health` (B10), 4 s timeout; latency is the client-measured round trip | run "connecting" → ok "38 ms" → fail "no response" |
| **⟨chat model display name⟩** · ⟨runtime name⟩ | `GET /api/v1/runtime-status` (`chat` role), plus B11 fields | run "checking" → ok "ready" → `loaded:false` "loading · 4 s" (elapsed time, counted client-side) → fail "not responding" / "model missing" |
| **⟨project name⟩** · "sources" | The existing project and sources data | run "opening" → ok "3 ready" / "no sources yet" (neutral, not a failure) |

**Timing:**

- Show results as they arrive, but reveal consecutive row transitions **at least 150 ms apart**, so it reads as a sequence.
- When all three are OK, show **Ready**, hold for 200 ms, then fade out over 320 ms (`.launch.is-leaving`).
- **A slow model never blocks the app.** After **3 s** of `loading`, continue into the app anyway. The title-bar model pill then shows "Loading…" until it's ready.

**Failure handoffs** (no dead ends):

- **Mac mini fails.** Status: "Can't reach your Mac mini". Actions: **Continue offline** (the offline screen, §4.2) and **Try again**.
- **The model is down or missing.** Status: "⟨Runtime⟩ isn't responding on your Mac mini". Actions: **Open anyway** (the app in the runtime-down state, §4.4) and **Try again**.
- **This device is offline** (`navigator.onLine === false`). Skip the network call and go straight to the offline screen with the "This device is offline" copy.

**Optional warm-up (B12).** If "Warm up the model when the app opens" is on (default on; it lives in Settings › Models), `loaded:false` triggers the warm-up call, and the row shows the elapsed load time.

---

## 4. Offline and degraded states

### 4.1 Connection states (one source of truth in `app.js`)

| State | Detected by | UI |
|---|---|---|
| `ok` | health OK and chat reachable | normal |
| `device_offline` | `navigator.onLine === false` | offline screen, "This device is offline" copy |
| `server_unreachable` | `/api/v1/health` fails or times out **twice in a row** | offline screen, "Your Mac mini isn't answering" copy |
| `runtime_down` | health OK; `runtime-status.chat.reachable === false` | runtime-down state (§4.4) |
| `model_missing` | reachable; `model_present === false` | runtime-down state, "model missing" copy |
| `embedding_down` | chat OK; embedding unreachable | Sources search shows "Keyword search only" (with B14) or "Search is unavailable" (without it); grounded modes are disabled with that reason |

**When to re-check:**

- every 60 s while visible (the existing interval);
- on `online` and `offline` events;
- on `visibilitychange`;
- on any failed API call.

**A single network error from an ordinary API call doesn't change the state.** It triggers one health check, and that decides.

### 4.2 The offline screen (`server_unreachable`, `device_offline`)

**Where it comes from.** It's served from the service-worker cache (§4.3), because nothing on the Mac mini can answer. Without a service worker the browser shows its own error page instead; this is the main reason B13 exists.

**Layout** (see `reference/screens/32`, `33` and `37`):

- **Illustration:** Mac mini ─ ✕ ─ phone, with the ✕ in `--danger`. For `device_offline`, the break moves next to the phone and the Mac mini's LED goes green. Mark it `aria-hidden`.
- **Heading and body** (the exact copy is in the mockup):
  - "Your Mac mini isn't answering" / "This device is offline" (desktop);
  - "This phone is offline" (phone).
- **Status line:** "Trying again in 8 s", with a pulsing `--warning` dot.
  - Retries run every 8 s, then 16 s, then every 30 s.
  - A retry also runs immediately on `online` and on becoming visible.
  - While a check is running it shows a spinner and "Trying to reach your Mac mini…".
- **Buttons:**
  - **Try now** (primary) resets the backoff to 8 s.
  - **Show details / Hide details** toggles a `<dl>` with: the address (`location.host`), the last attempt time and result, this device's online state, and the retry schedule.
- **Things to check:**
  - for `server_unreachable`: 3 items (Mac mini awake and powered; Tailscale connected on both devices; AgenticRAG running);
  - for `device_offline`: 2 items;
  - on phone the list is collapsed behind **What to check**.
- **Sidebar and navigation:**
  - The project card says "Saved on this device".
  - **New chat** is disabled ("needs Mac mini").
  - Models and Tools are disabled (`aria-disabled`).
  - Sources is list-only, from the cache.
  - The "Readable offline" group lists cached chats. Opening one shows it read-only.
- **The draft composer** (dashed border): "Write a draft. You can send it when your Mac mini is back."
  - Drafts are saved to `localStorage["agenticrag.drafts"][chatId]`.
  - Nothing is ever sent automatically. When the connection returns, the draft is simply there in the composer.
- **Reconnecting:**
  - Hide the offline screen, reload data, and keep the scroll position.
  - Toast "Back online · Mac mini reconnected after N min".

### 4.3 The service worker (B13)

**What `ui/sw.js` does:**

- **Pre-caches the app shell:** `index.html`, CSS, JS, vendor files, icons, the manifest and the default fonts. The versioned asset URLs identify the cache.
- **Navigation is network-first** with a 4 s timeout, then falls back to the cached `index.html`. Updates still arrive, and the offline screen can still load.
- **The app's GET data** (`/api/v1/chats`, `/api/v1/chats/{id}`, `/api/v1/projects`, `/api/v1/sources` list only): network first, falling back to the cache. Each response stored in the cache records the time it was cached, so the UI can say "Saved on this device".
- **Never caches** POST/PUT/DELETE, streams, `/api/v1/runtime-status`, `/api/v1/health` or source text.
- **Settings › Privacy** gains:
  - "Keep chats readable offline on this device" (default on; turning it off clears the cache);
  - a **Clear offline copy** button.

Private chat text on the user's own phone is expected, but the user must be able to remove it.

**Limits to document:**

- Service workers need a secure context: HTTPS through Tailscale Serve, or `localhost`. Plain `http://` on a LAN IP won't register one, so there's no offline screen there.
- Update flow: on a new version, the worker waits; the app shows a toast "Update ready · Reload" with an action. Never auto-reload mid-run.

### 4.4 The model runtime is down (the app stays usable)

See `reference/screens/34` and `35`.

**The title-bar runtime pill turns to the danger style:** "Qwen3 30B | Not responding" (or "Model missing"). It opens a popover with:

- **Title:**
  - "⟨Runtime⟩ isn't responding", with the body "Your Mac mini is online, but ⟨Runtime⟩ didn't answer. It may have quit or still be starting."
  - For missing: "⟨Model⟩ isn't in ⟨Runtime⟩", with the body "⟨Runtime⟩ is running on your Mac mini, but the chat model you picked isn't in its model list. It may have been removed or renamed."
- **A table with one row per role** (Chat, Embeddings): model display name, plus mono state text from `error_kind`:
  - `refused` → "connection refused";
  - `timeout` → "no response";
  - `model_missing` → "not in model list";
  - OK → "ok · 12 ms".
  - The footer shows `runtime` + `endpoint` (host:port only) and "checked N s ago".
- **Still works:** a list computed from the state. Only list what's actually true:
  - "Reading chats and sources"
  - "Project memory"
  - "Keyword search in sources", **only with B14**
  - "Answers with another installed model", for `model_missing` when another model is reachable
- **Actions:**
  - down: **Retry now** (`runtime-status?fresh=1`) and **How to restart it** (a short, runtime-specific help popover);
  - missing: **Choose a model** (opens Models) and **Retry**.

**The composer:**

- It shows a status strip at the top, `.composer-status` on `--warning-soft`: "Answers are paused until ⟨Runtime⟩ responds on your Mac mini." plus **Retry**.
- The textarea stays editable, with the placeholder "Write your next question. Send it once the model is back."
- Send is disabled, with an `aria-label` that says why.

**Elsewhere:**

- The sidebar Models row shows a danger dot.
- The readiness footer shows "⟨Runtime⟩ not responding" and `runtime · endpoint`.

### 4.5 Disconnects during a run

Runs already continue on the server (`run_store`). While a stream is interrupted:

1. Show the progress toast "Reconnecting… · Your run keeps going on the Mac mini".
2. Poll `/api/v1/runs/{id}` with backoff (1, 2, 4, 8 s).
3. Once reconnected, resume rendering from the run record and turn the toast into "Back online".

If the run finished while the phone was away, render the final answer once. Never duplicate it.

---

## 5. Copy rules for this release

- **Say who is affected:** "your Mac mini", "this device" or "this phone". Don't say "the server".
- **Name the runtime the user configured** (LM Studio, Ollama). Never show a raw URL outside the details, the popover footer and the mono lines.
- **Times:**
  - use relative times for recency ("checked 4 s ago");
  - use absolute local time for "Last connected 21:02";
  - count elapsed time for loading ("loading · 4 s"), never percentages.
- **No blame and no exclamation marks.** Each failure state offers one primary action.
