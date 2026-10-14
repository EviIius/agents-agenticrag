# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: workflow-studio-running.spec.ts >> Palette selects the correct paused run when workflow names repeat
- Location: web/tests/workflow-studio-running.spec.ts:415:1

# Error details

```
Error: expect(locator).toHaveCount(expected) failed

Locator:  getByRole('option', { name: 'Resume Synthetic running workflow', exact: true })
Expected: 2
Received: 4
Timeout:  5000ms

Call log:
  - Expect "toHaveCount" getByRole('option', { name: 'Resume Synthetic running workflow', exact: true }) with timeout 5000ms
  - waiting for getByRole('option', { name: 'Resume Synthetic running workflow', exact: true })
    14 × locator resolved to 4 elements
       - unexpected value "4"

```

# Page snapshot

```yaml
- generic:
  - generic:
    - generic [aria-hidden]:
      - complementary:
        - generic:
          - generic:
            - button
            - generic: Atelier
            - link:
              - /url: /
          - navigation:
            - generic:
              - textbox:
                - /placeholder: Search chats…
              - generic: ⌘K
            - navigation:
              - generic:
                - link:
                  - /url: /workflows
                  - text: Workflows
              - generic:
                - link:
                  - /url: /images
                  - text: Images
            - region:
              - generic:
                - heading [level=2]: Folders
                - button
              - paragraph: No folders yet
            - paragraph: No chats yet
          - generic:
            - button: Settings
      - main:
        - generic:
          - generic:
            - button:
              - generic [aria-hidden]: ●
              - generic: fake-chat
              - generic: Fake runtime
          - button
        - generic:
          - heading [level=1]: Good morning
          - generic:
            - form:
              - generic:
                - button:
                  - generic: Synthetic-workflow.wav
                  - status: 1:15 · 16 words · ≈29 tokens
                  - generic: Transcript saved · audio removed
                - button
              - textbox:
                - /placeholder: Message fake-chat…
              - generic:
                - button
                - button [disabled]:
                  - generic: Search
                - button:
                  - generic: Image
                - generic:
                  - button [disabled]:
                    - generic: Library
                  - button
                - generic:
                  - generic:
                    - button [disabled]
            - generic:
              - button: Summarize
              - button: Action items
              - button: Decisions
          - paragraph: Your models. Your Mac.
    - region "Notifications alt+T"
  - dialog [ref=e2]:
    - heading "Command palette" [level=2] [ref=e3]
    - paragraph [ref=e4]: Search chats or run a command
    - generic [ref=e5]:
      - combobox "Search chats and actions" [expanded] [active] [ref=e11]: Resume Synthetic running workflow
      - listbox "Suggestions" [ref=e12]:
        - generic [ref=e13]:
          - generic [aria-hidden] [ref=e14]: Go to
          - group "Go to" [ref=e15]:
            - option "Resume Synthetic running workflow" [selected] [ref=e16]
            - option "Resume Synthetic running workflow" [ref=e17]
            - option "Resume Synthetic running workflow" [ref=e18]
            - option "Resume Synthetic running workflow" [ref=e19]
          - option "No chats or actions found" [disabled]
```

# Test source

```ts
  341 |     data: {
  342 |       name: d.name,
  343 |       description: d.description,
  344 |       icon: d.icon,
  345 |       graph: changed,
  346 |       version: d.version,
  347 |     },
  348 |   });
  349 |   await page.goto(`/workflows/${d.id}/runs/${run.id}`);
  350 |   await expect(
  351 |     page.getByText("The current workflow has changed.", { exact: false }),
  352 |   ).toBeVisible();
  353 |   await expect(page.locator(".wf-canvas")).toHaveAttribute(
  354 |     "aria-label",
  355 |     "Read-only workflow canvas",
  356 |   );
  357 |   await expect(
  358 |     page.getByRole("region", { name: "Workflow results" }),
  359 |   ).toBeVisible();
  360 |   await shot(page, `run-view-${browserName}`);
  361 | });
  362 | 
  363 | test("Failed image block retries without repeating the finished text and shows paused notification", async ({
  364 |   page,
  365 |   request,
  366 | }) => {
  367 |   const d = await create(request, { review: false });
  368 |   const image = d.graph.nodes.find((n) => n.kind === "generate_image")!;
  369 |   image.config.prompt = `Synthetic image ${d.id} #fail-once`;
  370 |   const saved = await (
  371 |     await request.put(`/api/workflows/defs/${d.id}`, {
  372 |       data: {
  373 |         name: d.name,
  374 |         description: d.description,
  375 |         icon: d.icon,
  376 |         graph: d.graph,
  377 |         version: d.version,
  378 |       },
  379 |     })
  380 |   ).json();
  381 |   await start(request, saved);
  382 |   await page.goto(`/workflows/${d.id}?run=1`);
  383 |   await expect(page.locator('.wf-block[data-run="failed"]')).toContainText(
  384 |     "Image could not be completed or validated",
  385 |   );
  386 |   await expect(
  387 |     page.getByRole("button", { name: "Retry block", exact: true }),
  388 |   ).toBeVisible();
  389 |   await page.getByRole("button", { name: "Retry block", exact: true }).click();
  390 |   await done(page);
  391 |   const recovered = await (
  392 |     await request.get(`/api/workflows/runs?def_id=${d.id}`)
  393 |   ).json();
  394 |   expect(recovered.items[0].nodes.n_draft.attempt).toBe(1);
  395 |   expect(recovered.items[0].nodes.n_images.attempt).toBe(2);
  396 |   const paused = await create(request, { review: true });
  397 |   await page.goto("/");
  398 |   await start(request, paused);
  399 |   await expect(
  400 |     page.getByRole("button", { name: "Open", exact: true }),
  401 |   ).toBeVisible();
  402 |   await expect(
  403 |     page.locator(
  404 |       'nav[aria-label="Workspace"] [aria-label="A workflow is waiting for you"]',
  405 |     ),
  406 |   ).toBeVisible();
  407 |   await page.getByRole("button", { name: "Open", exact: true }).click();
  408 |   await expect(
  409 |     page.getByRole("textbox", { name: "Review result", exact: true }),
  410 |   ).toBeVisible();
  411 |   await page.getByRole("button", { name: "Reject", exact: true }).click();
  412 |   await done(page);
  413 | });
  414 | 
  415 | test("Palette selects the correct paused run when workflow names repeat", async ({
  416 |   page,
  417 |   request,
  418 | }) => {
  419 |   const first = await create(request);
  420 |   const second = await create(request);
  421 |   const runs = [await start(request, first), await start(request, second)];
  422 |   const duplicateKeys: string[] = [];
  423 |   page.on("console", (message) => {
  424 |     if (message.type() === "error" && message.text().includes("same key"))
  425 |       duplicateKeys.push(message.text());
  426 |   });
  427 |   await page.goto("/");
  428 |   await expect(
  429 |     page.locator(
  430 |       'nav[aria-label="Workspace"] [aria-label="A workflow is waiting for you"]',
  431 |     ),
  432 |   ).toBeVisible();
  433 |   await page.keyboard.press("ControlOrMeta+k");
  434 |   await page
  435 |     .getByRole("combobox", { name: "Search chats and actions" })
  436 |     .fill("Resume Synthetic running workflow");
  437 |   const options = page.getByRole("option", {
  438 |     name: "Resume Synthetic running workflow",
  439 |     exact: true,
  440 |   });
> 441 |   await expect(options).toHaveCount(2);
      |                         ^ Error: expect(locator).toHaveCount(expected) failed
  442 |   const values = await options.evaluateAll((items) =>
  443 |     items.map((item) => item.getAttribute("data-value")),
  444 |   );
  445 |   expect(new Set(values).size).toBe(2);
  446 |   const selected = values[1]!.slice("resume:".length);
  447 |   expect(runs.map((run) => run.id)).toContain(selected);
  448 |   await options.nth(1).click();
  449 |   await expect(page).toHaveURL(new RegExp(`/runs/${selected}$`));
  450 |   await expect(
  451 |     page.getByRole("textbox", { name: "Review result", exact: true }),
  452 |   ).toBeVisible();
  453 |   expect(duplicateKeys).toEqual([]);
  454 | });
  455 | 
  456 | test("Full application lifecycle restart preserves completed blocks and resumes unfinished work", async ({
  457 |   page,
  458 |   request,
  459 |   browserName,
  460 | }) => {
  461 |   const d = await create(request, { review: false });
  462 |   const image = d.graph.nodes.find((n) => n.kind === "generate_image")!;
  463 |   image.config.prompt = "Synthetic restart image #restart";
  464 |   const saved = await (
  465 |     await request.put(`/api/workflows/defs/${d.id}`, {
  466 |       data: {
  467 |         name: d.name,
  468 |         description: d.description,
  469 |         icon: d.icon,
  470 |         graph: d.graph,
  471 |         version: d.version,
  472 |       },
  473 |     })
  474 |   ).json();
  475 |   const run = await start(request, saved);
  476 |   await page.goto(`/workflows/${d.id}?run=1`);
  477 |   await expect(page.locator('.wf-block[data-run="running"]')).toContainText(
  478 |     "Create images",
  479 |   );
  480 |   expect(
  481 |     (await request.post(`${fakeAppURL}/tests/restart-lifecycle`)).ok(),
  482 |   ).toBe(true);
  483 |   await page.reload();
  484 |   await expect(
  485 |     page.getByRole("button", { name: "Retry unfinished steps", exact: true }),
  486 |   ).toBeVisible();
  487 |   const interrupted = await (
  488 |     await request.get(`/api/workflows/runs/${run.id}/v2`)
  489 |   ).json();
  490 |   expect(interrupted.state).toBe("interrupted");
  491 |   expect(interrupted.nodes.n_draft.state).toBe("complete");
  492 |   await page
  493 |     .getByRole("button", { name: "Retry unfinished steps", exact: true })
  494 |     .click();
  495 |   await done(page);
  496 |   const recovered = await (
  497 |     await request.get(`/api/workflows/runs/${run.id}/v2`)
  498 |   ).json();
  499 |   expect(recovered.nodes.n_draft.attempt).toBe(1);
  500 |   expect(recovered.nodes.n_draft.output).toEqual(
  501 |     interrupted.nodes.n_draft.output,
  502 |   );
  503 |   expect(recovered.nodes.n_images.attempt).toBe(2);
  504 |   await shot(page, `restart-recovered-${browserName}`);
  505 | });
  506 | 
  507 | for (const width of [390, 1440])
  508 |   for (const theme of ["dark", "light"])
  509 |     test(`Run design states ${width} ${theme}`, async ({
  510 |       page,
  511 |       browserName,
  512 |     }) => {
  513 |       const results = [];
  514 |       await page.setViewportSize({ width, height: 900 });
  515 |       for (const state of [
  516 |         "run-running",
  517 |         "run-paused",
  518 |         "run-complete",
  519 |         "run-failed",
  520 |         "run-interrupted",
  521 |         "run-reused",
  522 |         "run-skipped",
  523 |         "pick-paused",
  524 |         "block-test",
  525 |         "setup-pick",
  526 |       ]) {
  527 |         await page.goto("/design?studio");
  528 |         await page.getByRole("button", { name: theme, exact: true }).click();
  529 |         await page.getByRole("button", { name: state, exact: true }).click();
  530 |         await settle(page);
  531 |         const scan = await new AxeBuilder({ page }).analyze();
  532 |         expect(
  533 |           scan.violations.filter((v) =>
  534 |             ["serious", "critical"].includes(v.impact ?? ""),
  535 |           ),
  536 |           `${state} ${width} ${theme}`,
  537 |         ).toEqual([]);
  538 |         results.push({ width, theme, state, seriousCritical: 0 });
  539 |         await shot(page, `${state}-${width}-${theme}-${browserName}`);
  540 |       }
  541 |       await mkdir(dir, { recursive: true });
```