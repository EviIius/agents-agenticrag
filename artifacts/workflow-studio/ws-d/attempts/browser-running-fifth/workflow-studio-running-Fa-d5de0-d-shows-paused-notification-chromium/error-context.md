# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: workflow-studio-running.spec.ts >> Failed image block retries without repeating the finished text and shows paused notification
- Location: tests/workflow-studio-running.spec.ts:356:1

# Error details

```
Error: expect(locator).toContainText(expected) failed

Locator: locator('.wf-block[data-run="failed"]')
Expected substring: "Synthetic failure"
Received string:    "Create imagesCreate imagesImage could not be completed or validated. No output was accepted. Retry this job.images.imagesimages.prompt"
Timeout: 5000ms

Call log:
  - Expect "toContainText" locator('.wf-block[data-run="failed"]') with timeout 5000ms
  - waiting for locator('.wf-block[data-run="failed"]')
    11 × locator resolved to <div class="wf-block" data-run="failed" data-selected="false" data-disabled="false">…</div>
       - unexpected value "Create imagesCreate imagesImage could not be completed or validated. No output was accepted. Retry this job.images.imagesimages.prompt"

```

```yaml
- text: Create images Create images
- paragraph: Image could not be completed or validated. No output was accepted. Retry this job.
- text: images.images images.prompt
- img "failed"
```

# Test source

```ts
  276 |   await page
  277 |     .getByRole("menuitem", { name: "Test this block", exact: true })
  278 |     .click();
  279 |   await page
  280 |     .getByRole("textbox", { name: "Sample start.brief", exact: true })
  281 |     .fill("Synthetic test brief");
  282 |   await page.getByRole("button", { name: "Test block", exact: true }).click();
  283 |   await done(page);
  284 |   await page.reload();
  285 |   await done(page);
  286 |   await expect(page.locator(".wf-run-card")).toContainText(
  287 |     "Draft image prompt",
  288 |   );
  289 |   const list = await (
  290 |     await request.get(`/api/workflows/runs?def_id=${d.id}`)
  291 |   ).json();
  292 |   expect(list.items).toEqual([]);
  293 |   const tests = await (
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
> 376 |   await expect(page.locator('.wf-block[data-run="failed"]')).toContainText(
      |                                                              ^ Error: expect(locator).toContainText(expected) failed
  377 |     "Synthetic failure",
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
  408 | test("All run design states pass axe and stop motion in both preferences", async ({
  409 |   page,
  410 |   browserName,
  411 | }) => {
  412 |   const results = [];
  413 |   for (const width of [390, 1440])
  414 |     for (const theme of ["dark", "light"]) {
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
  441 |     }
  442 |   await page.setViewportSize({ width: 1440, height: 900 });
  443 |   await page.goto("/design?studio&state=run-running");
  444 |   await settle(page);
  445 |   await expect(page.locator('.wf-block[data-run="running"]')).toBeVisible();
  446 |   expect(
  447 |     await page
  448 |       .locator('.wf-block[data-run="running"]')
  449 |       .evaluate((el) => getComputedStyle(el, "::before").animationName),
  450 |   ).toBe("wf-sweep");
  451 |   await page.emulateMedia({ reducedMotion: "reduce" });
  452 |   expect(
  453 |     await page
  454 |       .locator('.wf-block[data-run="running"]')
  455 |       .evaluate((el) => getComputedStyle(el, "::before").animationName),
  456 |   ).toBe("none");
  457 |   await page.emulateMedia({ reducedMotion: "no-preference" });
  458 |   await page.evaluate(
  459 |     () => (document.documentElement.dataset.reduceMotion = "always"),
  460 |   );
  461 |   expect(
  462 |     await page
  463 |       .locator('.wf-block[data-run="running"]')
  464 |       .evaluate((el) => getComputedStyle(el, "::before").animationName),
  465 |   ).toBe("none");
  466 |   await mkdir(dir, { recursive: true });
  467 |   await writeFile(
  468 |     `${dir}/axe-states-${browserName}.json`,
  469 |     JSON.stringify(results, null, 2),
  470 |   );
  471 | });
  472 | 
  473 | test.describe("Phone", () => {
  474 |   test.use({
  475 |     viewport: { width: 390, height: 844 },
  476 |     hasTouch: true,
```