# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: phase5a.spec.ts >> 5A controls wait for the requested chat instead of exposing an empty draft
- Location: tests/phase5a.spec.ts:459:1

# Error details

```
Error: expect(locator).toHaveText(expected) failed

Locator: getByRole('region', { name: 'Chat controls', exact: true }).getByRole('status')
Expected: "Loading chat controls…"
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toHaveText" getByRole('region', { name: 'Chat controls', exact: true }).getByRole('status') with timeout 5000ms
  - waiting for getByRole('region', { name: 'Chat controls', exact: true }).getByRole('status')

```

```yaml
- main:
  - button "Open sidebar"
  - button "Choose model": fake-chat
  - button "Chat controls"
  - status
  - log "Conversation"
  - form "Message":
    - textbox "Message fake-chat":
      - /placeholder: Message fake-chat…
    - button "Add attachment"
    - button "Web search"
    - button "Create image"
    - button "Library" [disabled]
    - button "Choose Library collections"
    - img "0 of 16,384 total tokens; 12,032 input allowance; 4,096 reserved for response; 256 safety margin"
    - button "Send message" [disabled]
- region "Notifications alt+T":
  - list:
    - listitem:
      - button "Close toast"
      - text: Brief to images is waiting for you.
      - button "Open"
```

# Test source

```ts
  383 | });
  384 | 
  385 | test("5A Settings presets rename, order, default and deletion keep chat copies", async ({
  386 |   page,
  387 |   request,
  388 | }) => {
  389 |   const conn = await setup(page, request);
  390 |   const first = await (
  391 |     await request.post("/api/presets", {
  392 |       data: { name: "Synthetic One", params: { top_k: 21 } },
  393 |     })
  394 |   ).json();
  395 |   const second = await (
  396 |     await request.post("/api/presets", { data: { name: "Synthetic Two" } })
  397 |   ).json();
  398 |   const chat = await (
  399 |     await request.post("/api/chats", {
  400 |       data: {
  401 |         connection_id: conn.id,
  402 |         model_id: "fake-chat",
  403 |         preset_id: first.id,
  404 |       },
  405 |     })
  406 |   ).json();
  407 |   await page.keyboard.press("Control+,");
  408 |   const settings = page.getByRole("dialog", { name: "Settings", exact: true });
  409 |   await settings.getByRole("button", { name: "Presets", exact: true }).click();
  410 |   const one = settings.getByRole("article", { name: "Preset Synthetic One" });
  411 |   await one.getByRole("button", { name: "Move Synthetic One down" }).click();
  412 |   await expect
  413 |     .poll(async () =>
  414 |       (await (await request.get("/api/presets")).json()).map(
  415 |         (p: { id: string }) => p.id,
  416 |       ),
  417 |     )
  418 |     .toEqual([second.id, first.id]);
  419 |   await one.getByRole("button", { name: "Edit / rename" }).click();
  420 |   const editor = page.getByRole("dialog", { name: "Edit preset", exact: true });
  421 |   await editor
  422 |     .getByRole("textbox", { name: "Preset name" })
  423 |     .fill("Synthetic Renamed");
  424 |   await editor.getByRole("button", { name: "Save preset" }).click();
  425 |   await expect(editor).not.toBeVisible();
  426 |   const renamed = settings.getByRole("article", {
  427 |     name: "Preset Synthetic Renamed",
  428 |   });
  429 |   await renamed
  430 |     .getByRole("switch", { name: "Use Synthetic Renamed for new chats" })
  431 |     .click();
  432 |   await expect
  433 |     .poll(
  434 |       async () =>
  435 |         (await (await request.get("/api/settings")).json()).default_preset_id,
  436 |     )
  437 |     .toBe(first.id);
  438 |   await renamed.getByRole("button", { name: "Delete", exact: true }).click();
  439 |   const confirmation = page.getByRole("alertdialog", {
  440 |     name: "Delete preset?",
  441 |   });
  442 |   await expect(confirmation).toContainText(
  443 |     "Existing chats keep their copied settings.",
  444 |   );
  445 |   await confirmation
  446 |     .getByRole("button", { name: "Delete preset", exact: true })
  447 |     .click();
  448 |   await expect(confirmation).not.toBeVisible();
  449 |   await expect(renamed).toHaveCount(0);
  450 |   expect(
  451 |     (await (await request.get("/api/settings")).json()).default_preset_id,
  452 |   ).toBeNull();
  453 |   expect(
  454 |     (await (await request.get("/api/chats/" + chat.id)).json()).chat,
  455 |   ).toEqual(chat);
  456 |   await request.delete(`/api/presets/${second.id}`);
  457 | });
  458 | 
  459 | test("5A controls wait for the requested chat instead of exposing an empty draft", async ({
  460 |   page,
  461 |   request,
  462 | }) => {
  463 |   const conn = await setup(page, request);
  464 |   const chat = await (
  465 |     await request.post("/api/chats", {
  466 |       data: { connection_id: conn.id, model_id: "fake-chat" },
  467 |     })
  468 |   ).json();
  469 |   await request.patch(`/api/chats/${chat.id}`, {
  470 |     data: { params: { top_k: 42 } },
  471 |   });
  472 |   let release: () => void = () => {};
  473 |   const loaded = new Promise<void>((resolve) => {
  474 |     release = resolve;
  475 |   });
  476 |   await page.route(`**/api/chats/${chat.id}`, async (route) => {
  477 |     await loaded;
  478 |     await route.continue();
  479 |   });
  480 |   await page.goto("/c/" + chat.id);
  481 |   await open(page);
  482 |   const panel = controls(page);
> 483 |   await expect(panel.getByRole("status")).toHaveText("Loading chat controls…");
      |                                           ^ Error: expect(locator).toHaveText(expected) failed
  484 |   await expect(
  485 |     panel.getByRole("button", { name: "Save settings", exact: true }),
  486 |   ).toHaveCount(0);
  487 |   release();
  488 |   await expect(
  489 |     panel.getByRole("spinbutton", { name: "Top K", exact: true }),
  490 |   ).toHaveValue("42");
  491 |   await expect(
  492 |     panel.getByRole("button", { name: "Save settings", exact: true }),
  493 |   ).toBeDisabled();
  494 | });
  495 | 
```