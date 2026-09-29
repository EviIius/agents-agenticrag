# QA checklist v2.1

Run this with the v2 `QA-CHECKLIST.md`. Report pass or fail for each line.

## Themes, accents, fonts

- [ ] `python docs/design-handoff/v2.1/tools/check_contrast.py src/agenticrag/ui/tokens.css` prints "All pass" (24 combinations). Add it as a pytest test.
- [ ] Each theme matches `reference/screens/20` at 1440×900.
- [ ] With Midnight, the page background is pure `#000000`, and `<meta name="theme-color">` is `#000000`.
- [ ] System follows the OS live, with no reload:
  - [ ] toggle macOS/iOS appearance while the app is open;
  - [ ] the chosen light and dark themes are used.
- [ ] No flash of the wrong theme on a cold load. Test Paper, with DevTools throttled to "Slow 3G".
- [ ] The existing `agenticrag.theme` value migrates once, then that key is removed.
- [ ] Accent choices:
  - [ ] Amber and Graphite change primary buttons, the send button, focus rings, selected cards, meters and the highlight;
  - [ ] they don't change evidence pills, which stay teal.
- [ ] Each interface font applies to all UI chrome, and to nothing inside answers.
- [ ] Each answer font applies to answers, evidence passages and the new-chat headline.
- [ ] Switching answer fonts keeps the apparent size. Compare one line with a screenshot.
- [ ] S, M and L change only reading text. The phone composer input stays at 16 px.
- [ ] Increase contrast raises secondary text, muted text and borders in all four themes, and it turns on by itself under OS "Increase contrast" when the user hasn't chosen.
- [ ] Reduce motion (the setting, and separately the OS setting):
  - [ ] no scale, slide or draw animations anywhere;
  - [ ] fades of 150 ms or less.
- [ ] The new fonts return `font/woff2` with long caching, and aren't downloaded until they're selected (check the Network tab).

## Popups

- [ ] No `window.confirm`, `window.alert` or `window.prompt` is left anywhere in `app.js`.
- [ ] Delete chat opens the confirm dialog:
  - [ ] focus starts on Cancel;
  - [ ] Esc cancels;
  - [ ] focus returns to the row menu button.
- [ ] Only one modal at a time. A toast raised while a modal is open appears after it closes, unless it's an error shown inside the dialog.
- [ ] Toast behaviour:
  - [ ] success and info leave after 5 s, and 8 s when they have an action;
  - [ ] errors stay until dismissed;
  - [ ] hover or focus pauses the timer;
  - [ ] at most 3 are visible.
- [ ] Toasts sit above the composer on phone and never cover the Send button (test at 390×844 with the keyboard open).
- [ ] Menus:
  - [ ] arrow keys, Home/End, Enter and Esc all work;
  - [ ] the destructive item is last and red;
  - [ ] a menu with more than 4 items becomes a sheet on phone.
- [ ] Popovers close on an outside click and on Esc. The model picker is a listbox with `aria-selected`.
- [ ] Tooltips show on hover or focus after 400 ms, and never on touch.
- [ ] Tool approval, with a stubbed `waiting_for_user` event:
  - [ ] initial focus is on Deny;
  - [ ] Esc closes the dialog but the run keeps waiting, and the inline card stays in the thread;
  - [ ] the tool name, the arguments and the "what leaves the Mac mini" line come from host data, not from model text.
- [ ] Agent question card:
  - [ ] number keys pick a choice;
  - [ ] sending from the composer answers it;
  - [ ] it shows the Paused chip.

## Launch intro

- [ ] "Every launch": the overlay is visible on the first paint and lasts at least 900 ms. When everything is warm it's gone within about 1.3 s.
- [ ] "Only when something's slow": with a healthy, warm server there's no overlay. With a 1 s delay injected on `/api/v1/health`, the overlay appears after 400 ms.
- [ ] "Off": no overlay, even when the Mac mini is down. The offline screen still appears.
- [ ] Rows use real data:
  - [ ] the latency is measured;
  - [ ] the model display name and runtime come from the settings;
  - [ ] the source count comes from the project.
- [ ] A cold model shows "loading · N s" and hands off to the app after 3 s at most, with the model pill showing "Loading…".
- [ ] Mac mini down leads to Continue offline or Try again. The runtime down leads to Open anyway or Try again.
- [ ] Resuming from background doesn't replay the intro. A status change shows a toast.
- [ ] A key press or tap skips the intro after the Mac mini check passes.
- [ ] Screen readers announce the status line (it's a live region). The mark is `aria-hidden`.

## Offline and degraded states

- [ ] The service worker registers over the Tailscale HTTPS address. Over plain LAN `http://` the app still works, just with no offline mode.
- [ ] Stop the server:
  - [ ] the offline screen loads from the cache on reload, and after opening the Home Screen app;
  - [ ] cached chats open read-only;
  - [ ] New chat, Models and Tools are disabled.
- [ ] Retries run at 8, 16, then 30 s. Try now resets to 8 s. The `online` and visible events retry immediately.
- [ ] Turn on airplane mode: the copy is "This phone is offline", and the illustration's break moves next to the phone.
- [ ] Drafts survive a reload and are never sent automatically.
- [ ] Restart the server: the "Back online · … after N min" toast appears, the data refreshes, and the scroll position is kept.
- [ ] Stop LM Studio or Ollama while the server is up:
  - [ ] the runtime pill and popover show the right `error_kind` text, `endpoint` and "checked N s ago";
  - [ ] the composer strip appears, Send is disabled, and typing still works.
- [ ] Rename the configured model in the runtime: the "model missing" copy appears, and "Choose a model" opens Models.
- [ ] "Keyword search in sources" appears only if B14 is built.
- [ ] A run in progress while the phone disconnects:
  - [ ] the Reconnecting toast appears;
  - [ ] the final answer renders once after reconnecting.
- [ ] Settings › Privacy › "Clear offline copy" empties the cache. The next offline reload shows no cached chats.
- [ ] Nothing the service worker caches includes source text, and the worker never caches health, runtime-status, streams or writes.
