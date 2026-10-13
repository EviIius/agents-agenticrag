# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: workflow-studio-running.spec.ts >> Run design states 390 dark
- Location: tests/workflow-studio-running.spec.ts:410:5

# Error details

```
Test timeout of 45000ms exceeded.
```

```
Error: locator.click: Test timeout of 45000ms exceeded.
Call log:
  - waiting for getByRole('button', { name: 'dark', exact: true })

```

# Page snapshot

```yaml
- generic:
  - generic:
    - generic [aria-hidden]:
      - main:
        - generic:
          - generic:
            - button
            - generic:
              - button:
                - generic [aria-hidden]: ●
                - generic: fake-chat
          - generic:
            - button
            - button
        - generic:
          - generic:
            - region:
              - paragraph: Workflow Studio · fake runtime states
              - button: light
              - button: dark
              - button: canvas
              - button: empty
              - button: selected
              - button: problems
              - button: conflict
              - button: outline
              - button: non-nestable
              - button: settings
              - button: run-inputs
              - button: run-running
              - button: run-paused
              - button: run-complete
              - button: run-failed
              - button: run-interrupted
              - button: run-reused
              - button: run-skipped
              - button: pick-paused
              - button: block-test
              - button: cards
              - button: home-cards
              - button: quick-add
              - button: setup-start
              - button: setup-generate
              - button: setup-transcribe
              - button: setup-clean_transcript
              - button: setup-generate_image
              - button: setup-review
              - button: setup-pick
              - button: setup-output
            - generic:
              - generic:
                - button
                - link:
                  - /url: /workflows
                - button: Synthetic image workflow
                - button
                - button: Run
              - generic:
                - generic:
                  - generic:
                    - generic:
                      - button:
                        - generic:
                          - generic: Start
                          - generic: Done
                    - generic:
                      - button [disabled]
                  - generic:
                    - generic:
                      - button:
                        - generic:
                          - generic: Draft image prompt
                          - generic: Writing · 51 characters
                    - generic:
                      - button [disabled]
                  - generic:
                    - generic:
                      - button:
                        - generic:
                          - generic: Check the prompt
                          - generic: Waiting
                    - generic:
                      - button [disabled]
                  - generic:
                    - generic:
                      - button:
                        - generic:
                          - generic: Create images
                          - generic: Waiting
                    - generic:
                      - button [disabled]
                  - generic:
                    - generic:
                      - button:
                        - generic:
                          - generic: Save results
                          - generic: Waiting
              - button
    - region "Notifications alt+T"
  - dialog [active] [ref=e2]:
    - heading "run" [level=2] [ref=e4]
    - paragraph [ref=e5]: Edit this workflow's settings.
    - generic [ref=e6]:
      - banner [ref=e7]:
        - heading "Run" [level=2] [ref=e8]
        - button "Close Run" [ref=e9] [cursor=pointer]
      - article "Synthetic image workflow run" [ref=e11]:
        - generic [ref=e12]:
          - heading "Synthetic image workflow" [level=3] [ref=e13]
          - time [ref=e14]: 10/13/2026, 8:00:00 AM
        - status [ref=e15]: Writing · running
        - list [ref=e16]:
          - listitem [ref=e17]:
            - button "View result for Start" [ref=e18] [cursor=pointer]:
              - generic [ref=e21]: Start
              - generic [ref=e22]: Done
          - listitem [ref=e23]:
            - button "View result for Draft image prompt" [ref=e24] [cursor=pointer]:
              - generic [ref=e27]: Draft image prompt
              - generic [ref=e28]: Writing · 51 characters
            - generic [ref=e30]:
              - status [ref=e31]
              - paragraph [ref=e33]: A synthetic blue circle on a warm paper background.
          - listitem [ref=e34]:
            - button "View result for Check the prompt" [ref=e35] [cursor=pointer]:
              - generic [ref=e38]: Check the prompt
              - generic [ref=e39]: Waiting
          - listitem [ref=e40]:
            - button "View result for Create images" [ref=e41] [cursor=pointer]:
              - generic [ref=e44]: Create images
              - generic [ref=e45]: Waiting
          - listitem [ref=e46]:
            - button "View result for Save results" [ref=e47] [cursor=pointer]:
              - generic [ref=e50]: Save results
              - generic [ref=e51]: Waiting
        - generic [ref=e52]:
          - button "Cancel workflow" [ref=e53] [cursor=pointer]
          - button "Save outputs" [ref=e54] [cursor=pointer]
        - paragraph [ref=e55]: Draft for review. Check it against the original.
```

# Test source

```ts
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
  394 |   ).toBeVisible();
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
> 429 |         await page.getByRole("button", { name: theme, exact: true }).click();
      |                                                                      ^ Error: locator.click: Test timeout of 45000ms exceeded.
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
  495 |       .getByRole("textbox", { name: "Review result", exact: true })
  496 |       .fill("Synthetic phone edit");
  497 |     await shot(page, `phone-paused-${browserName}`);
  498 |     await page.getByRole("button", { name: "Approve", exact: true }).click();
  499 |     await done(page);
  500 |     const result = await (
  501 |       await request.get(`/api/workflows/runs/${run.id}/v2`)
  502 |     ).json();
  503 |     expect(result.nodes.n_review.output.value).toBe("Synthetic phone edit");
  504 |     expect(
  505 |       await page.evaluate(
  506 |         () => document.documentElement.scrollWidth <= innerWidth,
  507 |       ),
  508 |     ).toBe(true);
  509 |   });
  510 | });
  511 | 
```