# Prompts for Codex (v2.1)

Paste one prompt per phase. Each one is self-contained. After each phase, stop for Jake's review of the screenshots.

These phases can run alongside the agent-roadmap work. The approval and question UI in Phase B plugs into roadmap items A7, E1 and D4 once those exist.

---

## Phase A: themes, accents, fonts, Appearance settings

```
Read docs/design-handoff/v2.1/README.md, then SPEC.md §1 and DATA-CONTRACT.md
("Static assets"). Implement Phase A only.

1. Tokens: merge docs/design-handoff/v2.1/tokens-themes.css into
   src/agenticrag/ui/tokens.css (after the Light block, before Base). Wherever answer
   and evidence text uses a fixed size, switch it to var(--text-read) or
   var(--text-read-panel).
2. Fonts: copy the six woff2 files and two licences from docs/design-handoff/v2.1/fonts
   into src/agenticrag/ui/fonts. Add them to UI_FILES and test that each one is served
   as font/woff2 with long caching.
3. Boot: add ui/boot.js (under 2 KB, never throws). Load it synchronously as the first
   script in <head>. It reads localStorage "agenticrag.appearance", migrates the old
   "agenticrag.theme" key, resolves System, sets the data-* attributes and theme-color
   on <html>, and sets data-launch when needed (SPEC §3.1). No inline script: CSP
   stays as it is.
4. Settings dialog: add Settings › Appearance per SPEC §1.1–1.2 (theme cards with
   self-painting swatches, System light/dark pickers, accent, interface font, answer
   font, S/M/L, Increase contrast, Reduce motion, Launch intro). Use the components in
   components-v21.reference.css. The title-bar theme button opens it; ⌘, or Ctrl+,
   does too. Changes apply instantly. Listen to prefers-color-scheme and
   prefers-contrast.
5. Fix manifest.webmanifest colours to #0C0C0D and bump its version.
6. Add tools/check_contrast.py as a pytest test run against tokens.css.

Constraints: zero-build vanilla JS, CSP style-src 'self' (no style attributes; set
dynamic values with el.style.setProperty), additive API changes only, and every
existing flow keeps working. Run python -m pytest.

Screenshot Settings › Appearance in all four themes plus one Amber and one Graphite
accent at 1440×900 and 390×844. Compare them with reference/screens/20–23.
```

---

## Phase B: the popup system

```
Implement SPEC §2 from docs/design-handoff/v2.1/.

- Build one small popup module in app.js: confirmDialog(), toast() v2 (the kind,
  title, detail, action and duration API; returns update and dismiss), menus with
  roving focus, anchored popovers, tooltips, and dialog → sheet below 640 px.
  Use native <dialog>/showModal for modals, and give ::backdrop a literal fallback.
- Replace window.confirm in deleteChat() with confirmDialog. Remove every remaining
  window.confirm, alert and prompt.
- Move existing callers to toast() v2. Errors persist, and toasts are queued while a
  modal is open.
- Build the tool-approval dialog/sheet and the agent-question inline card as
  components with a test harness (stubbed events). Wire them to real run events only
  when the agent roadmap's waiting_for_user state exists.
- Chat row menu: Rename, Pin, Move to project…, Export as Markdown, Delete.

Keyboard and screen-reader behaviour must match SPEC §2 and QA-CHECKLIST "Popups".
Screenshot each component in dark and light next to reference/screens/24–26.
```

---

## Phase C: the launch intro

```
Implement SPEC §3 and DATA-CONTRACT B10 + B11 (B12 is optional; do it if time allows).

Backend:
- GET /api/v1/health: no provider calls, no-store. Test that it answers in under
  50 ms while a provider endpoint is dead.
- Add runtime, endpoint (host:port, credentials stripped), error_kind and loaded to
  each runtime-status role. Add ?fresh=1 with a 3 s rate limit. Tests for each
  error_kind and for the redaction.

Front end:
- Static overlay markup in index.html. boot.js shows it before app.js runs, and it
  never delays app initialisation.
- Run the three checks at once. Reveal row transitions at least 150 ms apart, with a
  900 ms minimum for "Every launch" and a 400 ms trigger for "Only when something's
  slow". A cold model hands off to the app after 3 s. Failure handoffs follow SPEC
  §3.3. Skip on key press or tap.
- Resume from background runs a quiet recheck and shows a toast only on change.
- Reduced motion: fade only.

Screenshot each state against reference/screens/27–31 and 36. Record a short screen
capture of a healthy launch.
```

---

## Phase D: offline and degraded states

```
Implement SPEC §4 and DATA-CONTRACT B13 (B14 and B15 are optional).

- ui/sw.js, served from the root with no-cache: pre-cache the app shell and default
  fonts; network-first navigation with a 4 s timeout and a cached fallback; cache the
  app's GET JSON for chats, chat detail, projects and the sources list only, recording
  when each response was cached; never cache writes, streams, health, runtime-status
  or source text. Add an update-ready toast.
- One connection-state machine in app.js (SPEC §4.1) that drives the offline screen,
  the runtime-down state, the embedding-down state and the toasts.
- Offline screen per reference/screens/32, 33 and 37: backoff 8/16/30 s, Try now,
  details, things to check, read-only cached chats, drafts in localStorage (never
  sent automatically), and the "Back online" toast on recovery.
- Runtime-down: pill, popover, composer strip, disabled Send, and Retry
  (runtime-status?fresh=1), per reference/screens/34–35. Only list "Still works" items
  that are actually true.
- Mid-run disconnect: Reconnecting toast, poll the run, render the final answer once.
- Settings › Privacy: "Keep chats readable offline on this device" and
  "Clear offline copy".

Test by stopping the server, stopping the model runtime, and turning on airplane mode
on the iPhone over the Tailscale HTTPS address.
```

---

## Phase E: QA

```
Run docs/design-handoff/v2.1/QA-CHECKLIST.md plus the v2 checklist. Fix what fails.
Bump the asset versions. Report pass or fail for each line, with screenshots for
anything visual.
```
