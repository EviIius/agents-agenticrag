# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: workflow-studio-running.spec.ts >> Failed image block retries without repeating the finished text and shows paused notification
- Location: tests/workflow-studio-running.spec.ts:356:1

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: getByRole('button', { name: 'Open', exact: true })
Expected: visible
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" getByRole('button', { name: 'Open', exact: true }) with timeout 5000ms
  - waiting for getByRole('button', { name: 'Open', exact: true })

```

```yaml
- complementary:
  - button "Collapse sidebar"
  - text: Atelier
  - link "New chat":
    - /url: /
  - navigation "Chat history":
    - textbox "Search history":
      - /placeholder: Search chats…
    - text: ⌘K
    - navigation "Workspace":
      - link "Workflows":
        - /url: /workflows
        - text: Workflows
        - img "A workflow is waiting for you"
      - link "Images":
        - /url: /images
    - region "Folders":
      - heading "Folders" [level=2]
      - button "New folder"
      - paragraph: No folders yet
    - paragraph: No chats yet
  - button "Settings"
- main:
  - button "Choose model": fake-chat Fake runtime
  - button "Chat controls"
  - heading "Good morning" [level=1]
  - form "Message":
    - textbox "Message fake-chat":
      - /placeholder: Message fake-chat…
    - button "Add attachment"
    - button "Web search": Search
    - button "Create image": Image
    - button "Library" [disabled]
    - button "Choose Library collections"
    - img "0 of 16,384 total tokens; 12,032 input allowance; 4,096 reserved for response; 256 safety margin"
    - button "Send message" [disabled]
  - button "Explain"
  - button "Write"
  - button "Code"
  - button "Search the web"
  - paragraph: Your models. Your Mac.
- region "Notifications alt+T"
```

# Test source

```ts
  294 |     await request.get(`/api/workflows/defs/${d.id}/tests?node_id=n_draft`)
  295 |   ).json();
  296 |   expect(tests).toHaveLength(1);
  297 |   expect(tests[0].mode).toBe("test");
  298 |   expect(tests[0].nodes.n_images.attempt).toBe(0);
  299 |   await page.getByRole("button", { name: "Close Run", exact: true }).click();
  300 |   await configureStudioBlock(page, "Draft image prompt");
  301 |   await page.getByRole("tab", { name: "Output", exact: true }).click();
  302 |   await expect(page.locator(".wf-panel-body").last()).toContainText(
  303 |     "Block test",
  304 |   );
  305 | });
  306 | 
  307 | test("Favorites select actual image outputs and saved run uses an immutable canvas snapshot", async ({
  308 |   page,
  309 |   request,
  310 |   browserName,
  311 | }) => {
  312 |   const d = await create(request, { review: false, count: 2, pick: true });
  313 |   const run = await start(request, d);
  314 |   await page.goto(`/workflows/${d.id}?run=1`);
  315 |   await expect(
  316 |     page.getByRole("region", { name: "Pick favorites" }),
  317 |   ).toBeVisible();
  318 |   await page
  319 |     .getByRole("button", { name: "Pick result 2", exact: true })
  320 |     .click();
  321 |   await page
  322 |     .getByRole("button", { name: "Keep favorites", exact: true })
  323 |     .click();
  324 |   await done(page);
  325 |   const completed = await (
  326 |     await request.get(`/api/workflows/runs/${run.id}/v2`)
  327 |   ).json();
  328 |   expect(completed.results[0].items[0].value[0].id).toBe(
  329 |     completed.nodes.n_images.output.images[1].id,
  330 |   );
  331 |   const changed: Doc = structuredClone(d.graph);
  332 |   changed.nodes[0].position.x += 300;
  333 |   await request.put(`/api/workflows/defs/${d.id}`, {
  334 |     data: {
  335 |       name: d.name,
  336 |       description: d.description,
  337 |       icon: d.icon,
  338 |       graph: changed,
  339 |       version: d.version,
  340 |     },
  341 |   });
  342 |   await page.goto(`/workflows/${d.id}/runs/${run.id}`);
  343 |   await expect(
  344 |     page.getByText("The current workflow has changed.", { exact: false }),
  345 |   ).toBeVisible();
  346 |   await expect(page.locator(".wf-canvas")).toHaveAttribute(
  347 |     "aria-label",
  348 |     "Read-only workflow canvas",
  349 |   );
  350 |   await expect(
  351 |     page.getByRole("region", { name: "Workflow results" }),
  352 |   ).toBeVisible();
  353 |   await shot(page, `run-view-${browserName}`);
  354 | });
  355 | 
  356 | test("Failed image block retries without repeating the finished text and shows paused notification", async ({
  357 |   page,
  358 |   request,
  359 | }) => {
  360 |   const d = await create(request, { review: false });
  361 |   const image = d.graph.nodes.find((n) => n.kind === "generate_image")!;
  362 |   image.config.prompt = `Synthetic image ${d.id} #fail-once`;
  363 |   const saved = await (
  364 |     await request.put(`/api/workflows/defs/${d.id}`, {
  365 |       data: {
  366 |         name: d.name,
  367 |         description: d.description,
  368 |         icon: d.icon,
  369 |         graph: d.graph,
  370 |         version: d.version,
  371 |       },
  372 |     })
  373 |   ).json();
  374 |   await start(request, saved);
  375 |   await page.goto(`/workflows/${d.id}?run=1`);
  376 |   await expect(page.locator('.wf-block[data-run="failed"]')).toContainText(
  377 |     "Image could not be completed or validated",
  378 |   );
  379 |   await expect(
  380 |     page.getByRole("button", { name: "Retry block", exact: true }),
  381 |   ).toBeVisible();
  382 |   await page.getByRole("button", { name: "Retry block", exact: true }).click();
  383 |   await done(page);
  384 |   const recovered = await (
  385 |     await request.get(`/api/workflows/runs?def_id=${d.id}`)
  386 |   ).json();
  387 |   expect(recovered.items[0].nodes.n_draft.attempt).toBe(1);
  388 |   expect(recovered.items[0].nodes.n_images.attempt).toBe(2);
  389 |   const paused = await create(request, { review: true });
  390 |   await page.goto("/");
  391 |   await start(request, paused);
  392 |   await expect(
  393 |     page.getByRole("button", { name: "Open", exact: true }),
> 394 |   ).toBeVisible();
      |     ^ Error: expect(locator).toBeVisible() failed
  395 |   await expect(
  396 |     page.locator(
  397 |       'nav[aria-label="Workspace"] [aria-label="A workflow is waiting for you"]',
  398 |     ),
  399 |   ).toBeVisible();
  400 |   await page.getByRole("button", { name: "Open", exact: true }).click();
  401 |   await expect(
  402 |     page.getByRole("textbox", { name: "Review result", exact: true }),
  403 |   ).toBeVisible();
  404 |   await page.getByRole("button", { name: "Reject", exact: true }).click();
  405 |   await done(page);
  406 | });
  407 | 
  408 | for (const width of [390, 1440])
  409 |   for (const theme of ["dark", "light"])
  410 |     test(`Run design states ${width} ${theme}`, async ({
  411 |       page,
  412 |       browserName,
  413 |     }) => {
  414 |       const results = [];
  415 |       await page.setViewportSize({ width, height: 900 });
  416 |       for (const state of [
  417 |         "run-running",
  418 |         "run-paused",
  419 |         "run-complete",
  420 |         "run-failed",
  421 |         "run-interrupted",
  422 |         "run-reused",
  423 |         "run-skipped",
  424 |         "pick-paused",
  425 |         "block-test",
  426 |         "setup-pick",
  427 |       ]) {
  428 |         await page.goto(`/design?studio&state=${state}`);
  429 |         await page.getByRole("button", { name: theme, exact: true }).click();
  430 |         await settle(page);
  431 |         const scan = await new AxeBuilder({ page }).analyze();
  432 |         expect(
  433 |           scan.violations.filter((v) =>
  434 |             ["serious", "critical"].includes(v.impact ?? ""),
  435 |           ),
  436 |           `${state} ${width} ${theme}`,
  437 |         ).toEqual([]);
  438 |         results.push({ width, theme, state, seriousCritical: 0 });
  439 |         await shot(page, `${state}-${width}-${theme}-${browserName}`);
  440 |       }
  441 |       await mkdir(dir, { recursive: true });
  442 |       await writeFile(
  443 |         `${dir}/axe-states-${width}-${theme}-${browserName}.json`,
  444 |         JSON.stringify(results, null, 2),
  445 |       );
  446 |     });
  447 | test("Run activity stops for system and Always reduced motion", async ({
  448 |   page,
  449 | }) => {
  450 |   await page.setViewportSize({ width: 1440, height: 900 });
  451 |   await page.goto("/design?studio&state=run-running");
  452 |   await settle(page);
  453 |   const block = page.locator('.wf-block[data-run="running"]');
  454 |   await expect(block).toBeVisible();
  455 |   expect(
  456 |     await block.evaluate(
  457 |       (el) => getComputedStyle(el, "::before").animationName,
  458 |     ),
  459 |   ).toBe("wf-sweep");
  460 |   await page.emulateMedia({ reducedMotion: "reduce" });
  461 |   expect(
  462 |     await block.evaluate(
  463 |       (el) => getComputedStyle(el, "::before").animationName,
  464 |     ),
  465 |   ).toBe("none");
  466 |   await page.emulateMedia({ reducedMotion: "no-preference" });
  467 |   await page.evaluate(
  468 |     () => (document.documentElement.dataset.reduceMotion = "always"),
  469 |   );
  470 |   expect(
  471 |     await block.evaluate(
  472 |       (el) => getComputedStyle(el, "::before").animationName,
  473 |     ),
  474 |   ).toBe("none");
  475 | });
  476 | 
  477 | test.describe("Phone", () => {
  478 |   test.use({
  479 |     viewport: { width: 390, height: 844 },
  480 |     hasTouch: true,
  481 |     isMobile: true,
  482 |   });
  483 |   test("Outline opens review in a sheet and keeps edit and reject decisions", async ({
  484 |     page,
  485 |     request,
  486 |     browserName,
  487 |   }) => {
  488 |     const d = await create(request);
  489 |     const run = await start(request, d);
  490 |     await page.goto(`/workflows/${d.id}?run=1`);
  491 |     await expect(
  492 |       page.locator('.wf-outline-row[data-run="paused"]'),
  493 |     ).toContainText("Waiting for you");
  494 |     await page
```