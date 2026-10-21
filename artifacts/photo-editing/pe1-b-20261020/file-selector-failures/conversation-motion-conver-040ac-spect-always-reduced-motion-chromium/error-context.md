# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: conversation-motion.spec.ts >> conversation preview and streaming respect always reduced motion
- Location: tests/conversation-motion.spec.ts:381:3

# Error details

```
Error: page.reload: Test ended.
Call log:
  - waiting for navigation until "load"
    - navigated to "http://127.0.0.1:5173/c/492950e114304ec8a435e0a48bd36227"

```

# Test source

```ts
  292 | 
  293 | // Exercise the native-file path independently of the existing ordinary-download tests.
  294 | test("chat save cancellation keeps formats editable and never opens a fallback download", async ({
  295 |   page,
  296 |   request,
  297 | }) => {
  298 |   const chat = await existing(page, request);
  299 |   await request.patch(`/api/chats/${chat.id}`, {
  300 |     data: { title: "Synthetic export chat" },
  301 |   });
  302 |   await page.reload();
  303 |   await page.evaluate(() => {
  304 |     let count = 0;
  305 |     Object.defineProperty(navigator, "canShare", {
  306 |       configurable: true,
  307 |       value: () => true,
  308 |     });
  309 |     Object.defineProperty(navigator, "share", {
  310 |       configurable: true,
  311 |       value: async (data: ShareData) => {
  312 |         const file = data.files![0];
  313 |         document.documentElement.dataset.shareCount = String(++count);
  314 |         document.documentElement.dataset.shareName = file.name;
  315 |         document.documentElement.dataset.shareActive = String(
  316 |           navigator.userActivation?.isActive ?? true,
  317 |         );
  318 |         document.documentElement.dataset.shareContent = await file.text();
  319 |         if (count === 1) throw new DOMException("Cancelled", "AbortError");
  320 |       },
  321 |     });
  322 |   });
  323 |   let downloads = 0;
  324 |   page.on("download", () => downloads++);
  325 |   const original = page.url();
  326 |   await page
  327 |     .getByRole("button", {
  328 |       name: "Actions for Synthetic export chat",
  329 |       exact: true,
  330 |     })
  331 |     .click();
  332 |   await page
  333 |     .getByRole("menuitem", { name: "Export JSON", exact: true })
  334 |     .click();
  335 |   const dialog = page.getByRole("dialog", { name: "Export chat", exact: true });
  336 |   await expect(
  337 |     dialog.getByRole("button", { name: "JSON (.json)", exact: true }),
  338 |   ).toHaveAttribute("aria-pressed", "true");
  339 |   await dialog
  340 |     .getByRole("button", { name: "Save or share", exact: true })
  341 |     .click();
  342 |   await expect(dialog.getByText(/Save cancelled/)).toBeVisible();
  343 |   await expect(
  344 |     dialog.getByRole("button", { name: "Close chat export", exact: true }),
  345 |   ).toBeInViewport({ ratio: 1 });
  346 |   await dialog
  347 |     .getByRole("button", { name: "Markdown (.md)", exact: true })
  348 |     .click();
  349 |   await expect(
  350 |     dialog.getByRole("button", { name: "Markdown (.md)", exact: true }),
  351 |   ).toHaveAttribute("aria-pressed", "true");
  352 |   await expect(
  353 |     dialog.getByRole("button", { name: "JSON (.json)", exact: true }),
  354 |   ).toHaveAttribute("aria-pressed", "false");
  355 |   await expect(dialog.getByLabel("Download filename")).toHaveText(
  356 |     "Synthetic export chat.md",
  357 |   );
  358 |   await dialog
  359 |     .getByRole("button", { name: "Save or share", exact: true })
  360 |     .click();
  361 |   await expect(dialog.getByText(/Returned from the save sheet/)).toBeVisible();
  362 |   await expect(page.locator("html")).toHaveAttribute("data-share-count", "2");
  363 |   await expect(page.locator("html")).toHaveAttribute(
  364 |     "data-share-active",
  365 |     "true",
  366 |   );
  367 |   await expect(page.locator("html")).toHaveAttribute(
  368 |     "data-share-name",
  369 |     "Synthetic export chat.md",
  370 |   );
  371 |   expect(
  372 |     await page.locator("html").getAttribute("data-share-content"),
  373 |   ).toContain("Synthetic export chat");
  374 |   expect(downloads).toBe(0);
  375 |   await expect(page).toHaveURL(original);
  376 |   await dialog.getByRole("button", { name: "Cancel", exact: true }).click();
  377 |   await expect(dialog).toHaveCount(0);
  378 | });
  379 | 
  380 | for (const reduce of ["system", "always"] as const) {
  381 |   test(`conversation preview and streaming respect ${reduce} reduced motion`, async ({
  382 |     page,
  383 |     request,
  384 |   }) => {
  385 |     await existing(page, request);
  386 |     if (reduce === "system")
  387 |       await page.emulateMedia({ reducedMotion: "reduce" });
  388 |     else {
  389 |       await request.patch("/api/settings", {
  390 |         data: { "appearance.reduce_motion": "always" },
  391 |       });
> 392 |       await page.reload();
      |                  ^ Error: page.reload: Test ended.
  393 |     }
  394 |     await page
  395 |       .locator(".composer textarea")
  396 |       .fill("Synthetic reduced motion #long:40 #slow:15");
  397 |     await page
  398 |       .getByRole("button", { name: "Send message", exact: true })
  399 |       .click();
  400 |     await expect(page.getByText(/token0 token1/)).toBeVisible();
  401 |     expect(await page.locator("[data-sd-animate]").count()).toBe(0);
  402 |     await expect(
  403 |       page.getByRole("button", { name: "Stop generating", exact: true }),
  404 |     ).not.toBeVisible({ timeout: 10000 });
  405 |     await page.goto("/design");
  406 |     if (reduce === "always")
  407 |       await page
  408 |         .getByRole("button", { name: "Always reduce motion", exact: true })
  409 |         .click();
  410 |     const preview = page.getByRole("region", {
  411 |       name: "Conversation motion",
  412 |       exact: true,
  413 |     });
  414 |     for (const state of [
  415 |       "optimistic",
  416 |       "waiting",
  417 |       "reasoning",
  418 |       "streaming",
  419 |       "search",
  420 |       "complete",
  421 |     ]) {
  422 |       await preview
  423 |         .getByRole("button", { name: `Preview ${state}`, exact: true })
  424 |         .click();
  425 |       await settle(page);
  426 |       const motion = await preview.locator("*").evaluateAll((elements) =>
  427 |         elements.flatMap((element) => {
  428 |           const css = getComputedStyle(element);
  429 |           return css.animationName !== "none" ||
  430 |             css.transitionDuration
  431 |               .split(",")
  432 |               .some((value) => parseFloat(value) !== 0)
  433 |             ? [element.outerHTML.slice(0, 180)]
  434 |             : [];
  435 |         }),
  436 |       );
  437 |       expect(motion).toEqual([]);
  438 |     }
  439 |     await request.patch("/api/settings", {
  440 |       data: { "appearance.reduce_motion": "system" },
  441 |     });
  442 |   });
  443 | }
  444 | 
  445 | test("model status pulse is based on a successful load, not initial cached state", async ({
  446 |   page,
  447 | }) => {
  448 |   await page.goto("/design");
  449 |   const preview = page.getByRole("region", {
  450 |     name: "Conversation motion",
  451 |     exact: true,
  452 |   });
  453 |   const status = preview.locator('[data-slot="model-status"]');
  454 |   await expect(status).not.toHaveAttribute("data-loaded-fresh", "true");
  455 |   await status.evaluate((element) =>
  456 |     new MutationObserver(() => {
  457 |       if (element.getAttribute("data-loaded-fresh") === "true")
  458 |         document.documentElement.dataset.pulseSeen = "true";
  459 |     }).observe(element, { attributes: true }),
  460 |   );
  461 |   await preview
  462 |     .getByRole("button", { name: "Choose model", exact: true })
  463 |     .click();
  464 |   await page
  465 |     .getByRole("button", { name: "Eject fake-chat", exact: true })
  466 |     .click();
  467 |   await expect(
  468 |     page.getByRole("button", { name: "Load fake-chat", exact: true }),
  469 |   ).toBeVisible();
  470 |   await page
  471 |     .getByRole("button", { name: "Load fake-chat", exact: true })
  472 |     .click();
  473 |   await expect(page.locator("html")).toHaveAttribute("data-pulse-seen", "true");
  474 |   await page
  475 |     .locator('[aria-label="Conversation motion"] [data-slot="model-status"]')
  476 |     .waitFor();
  477 |   await expect(
  478 |     page.locator(
  479 |       '[aria-label="Conversation motion"] [data-slot="model-status"]',
  480 |     ),
  481 |   ).not.toHaveAttribute("data-loaded-fresh", "true");
  482 | });
  483 | 
  484 | test("sidebar candidate width motion keeps the existing 300-message frame budget", async ({
  485 |   page,
  486 |   request,
  487 | }) => {
  488 |   const chat = await existing(page, request);
  489 |   await request.post(`${fakeAppURL}/tests/long-chat/${chat.id}`);
  490 |   await page.setViewportSize({ width: 1440, height: 900 });
  491 |   await page.reload();
  492 |   await expect(page.getByRole("article")).toHaveCount(300);
```