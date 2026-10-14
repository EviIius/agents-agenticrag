# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: workflow-studio-running.spec.ts >> Full application lifecycle restart preserves completed blocks and resumes unfinished work
- Location: tests/workflow-studio-running.spec.ts:408:1

# Error details

```
Error: expect(received).toBe(expected) // Object.is equality

Expected: true
Received: false
```

# Page snapshot

```yaml
- generic [ref=e2]:
  - generic [ref=e3]:
    - complementary [ref=e4]:
      - generic [ref=e5]:
        - button "Expand sidebar" [ref=e7] [cursor=pointer]
        - link "New chat" [ref=e8] [cursor=pointer]:
          - /url: /
        - button "Search chats" [ref=e9] [cursor=pointer]
        - navigation "Chat history" [ref=e10]:
          - navigation "Workspace" [ref=e11]:
            - link "Workflows" [ref=e12] [cursor=pointer]:
              - /url: /workflows
            - link "Images" [ref=e13] [cursor=pointer]:
              - /url: /images
        - button "Settings" [ref=e15] [cursor=pointer]
    - main [ref=e16]:
      - generic [ref=e17]:
        - generic [ref=e18]:
          - link "Back to Workflows" [ref=e19] [cursor=pointer]:
            - /url: /workflows
            - generic [ref=e22]: Workflows
          - generic [ref=e23]: /
          - button "Synthetic running workflow" [ref=e24] [cursor=pointer]
          - status [ref=e25]: Saved
          - button "Undo" [disabled]
          - button "Redo" [disabled]
          - button "Workflow menu" [ref=e27] [cursor=pointer]
          - button "Run" [ref=e28] [cursor=pointer]
        - generic [ref=e29]:
          - complementary "Blocks" [ref=e30]:
            - textbox "Search blocks" [ref=e35]
            - generic [ref=e36]:
              - group [ref=e37]:
                - generic "Inputs" [ref=e38] [cursor=pointer]
                - button "Start" [ref=e39] [cursor=pointer]
              - group [ref=e42]:
                - generic "AI" [ref=e43] [cursor=pointer]
                - button "Generate text" [ref=e44] [cursor=pointer]
                - button "Classify" [disabled] [ref=e47]
              - group [ref=e50]:
                - generic "Knowledge" [ref=e51] [cursor=pointer]
                - button "Search the web" [disabled] [ref=e52]
                - button "Search my files" [disabled] [ref=e55]
                - button "Read a document" [disabled] [ref=e58]
              - group [ref=e61]:
                - generic "Media" [ref=e62] [cursor=pointer]
                - button "Transcribe recording" [ref=e63] [cursor=pointer]
                - button "Clean up transcript" [ref=e66] [cursor=pointer]
                - button "Create images" [ref=e69] [cursor=pointer]
              - group [ref=e72]:
                - generic "Logic" [ref=e73] [cursor=pointer]
                - button "If / else" [disabled] [ref=e74]
                - button "Compose text" [disabled] [ref=e77]
              - group [ref=e80]:
                - generic "Review" [ref=e81] [cursor=pointer]
                - button "Approve or edit" [ref=e82] [cursor=pointer]
                - button "Pick favorites" [ref=e85] [cursor=pointer]
              - group [ref=e88]:
                - generic "Output" [ref=e89] [cursor=pointer]
                - button "Save results" [ref=e90] [cursor=pointer]
            - button "Note" [ref=e94] [cursor=pointer]
          - generic "Read-only workflow canvas" [ref=e97]:
            - application [ref=e98]:
              - generic [ref=e100]:
                - generic:
                  - generic:
                    - img:
                      - img "Connection from Start to Draft image prompt"
                    - img:
                      - img "Connection from Create images to Save results" [ref=e101] [cursor=pointer]
                    - img:
                      - img "Connection from Draft image prompt to Create images" [ref=e104] [cursor=pointer]
                  - generic:
                    - group "Start block ‘Start’, 1 of 4" [ref=e107] [cursor=pointer]:
                      - generic [ref=e110]:
                        - generic [ref=e115]:
                          - generic [ref=e116]: Start
                          - generic [ref=e117]: Start
                        - paragraph [ref=e118]: Done in 0 s
                        - generic [ref=e119]: start.brief
                        - img "complete" [ref=e121]
                    - group "Generate text block ‘Draft image prompt’, 2 of 4" [ref=e125] [cursor=pointer]:
                      - generic [ref=e129]:
                        - generic [ref=e135]:
                          - generic [ref=e136]: Draft image prompt
                          - generic [ref=e137]: Generate text
                        - paragraph [ref=e138]: Done in 0 s
                        - generic [ref=e139]: draft.text
                        - img "complete" [ref=e141]
                    - group "Create images block ‘Create images’, 3 of 4" [ref=e145] [cursor=pointer]:
                      - generic [ref=e149]:
                        - generic [ref=e156]:
                          - generic [ref=e157]: Create images
                          - generic [ref=e158]: Create images
                        - paragraph [ref=e159]: Generating image · 1 of 4
                        - generic [ref=e160]:
                          - generic [ref=e161]: images.images
                          - generic [ref=e162]: images.prompt
                    - group "Save results block ‘Save results’, 4 of 4" [ref=e164] [cursor=pointer]:
                      - generic [ref=e168]:
                        - generic [ref=e175]:
                          - generic [ref=e176]: Save results
                          - generic [ref=e177]: Save results
                        - paragraph [ref=e178]: Waiting
              - img "Mini Map" [ref=e180]
              - link "React Flow attribution" [ref=e186] [cursor=pointer]:
                - /url: https://reactflow.dev/attribution
                - text: React Flow
            - generic [ref=e187]:
              - button "Following run" [pressed] [ref=e188] [cursor=pointer]
              - button "Zoom out" [ref=e189] [cursor=pointer]
              - button "Zoom 100%" [ref=e190] [cursor=pointer]: 100%
              - button "Zoom in" [ref=e191] [cursor=pointer]
              - button "Fit view" [ref=e192] [cursor=pointer]
              - button "Outline view" [ref=e193] [cursor=pointer]
              - button "Canvas actions" [ref=e194] [cursor=pointer]
          - complementary "run" [ref=e195]:
            - generic [ref=e196]:
              - generic [ref=e197]:
                - heading "Run" [level=2] [ref=e198]
                - button "Close Run" [ref=e199] [cursor=pointer]
              - article "Synthetic running workflow run" [ref=e201]:
                - generic [ref=e202]:
                  - heading "Synthetic running workflow" [level=3] [ref=e203]
                  - time [ref=e204]: 10/13/2026, 8:47:35 AM
                - status [ref=e205]: Create images · running
                - list [ref=e206]:
                  - listitem [ref=e207]:
                    - button "View result for Start" [ref=e208] [cursor=pointer]:
                      - generic [ref=e211]: Start
                      - generic [ref=e212]: Done in 0 s
                  - listitem [ref=e213]:
                    - button "View result for Draft image prompt" [ref=e214] [cursor=pointer]:
                      - generic [ref=e217]: Draft image prompt
                      - generic [ref=e218]: Done in 0 s
                    - generic [ref=e220]:
                      - status [ref=e221]
                      - generic [ref=e222]:
                        - paragraph [ref=e223]: Fake runtime reply.
                        - list [ref=e224]:
                          - listitem [ref=e225]: A clear first step
                          - listitem [ref=e226]: A useful second step
                        - generic [ref=e227]:
                          - generic [ref=e228]: python
                          - button "Copy Code" [ref=e231] [cursor=pointer]
                          - region "Code example" [ref=e234]:
                            - code [ref=e236]:
                              - generic [ref=e237]: print('Hello')
                        - region "Answer table" [ref=e238]:
                          - region "Answer table" [ref=e239]:
                            - table [ref=e240]:
                              - rowgroup [ref=e241]:
                                - row [ref=e242]:
                                  - columnheader "Item" [ref=e243]
                                  - columnheader "Value" [ref=e244]
                              - rowgroup [ref=e245]:
                                - row [ref=e246]:
                                  - cell "Example" [ref=e247]
                                  - cell "42" [ref=e248]
                  - listitem [ref=e249]:
                    - button "View result for Create images" [ref=e250] [cursor=pointer]:
                      - generic [ref=e253]: Create images
                      - generic [ref=e254]: Generating image · 1 of 4
                    - progressbar "Progress for Create images" [ref=e255]
                    - link "View and save in Images" [ref=e257] [cursor=pointer]:
                      - /url: /images
                  - listitem [ref=e258]:
                    - button "View result for Save results" [ref=e259] [cursor=pointer]:
                      - generic [ref=e262]: Save results
                      - generic [ref=e263]: Waiting
                - generic [ref=e264]:
                  - button "Cancel workflow" [ref=e265] [cursor=pointer]
                  - button "Save outputs" [ref=e266] [cursor=pointer]
                - paragraph [ref=e267]: Draft for review. Check it against the original.
        - button "Import workflow JSON" [ref=e268]
  - region "Notifications alt+T"
```

# Test source

```ts
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
  408 | test("Full application lifecycle restart preserves completed blocks and resumes unfinished work", async ({
  409 |   page,
  410 |   request,
  411 |   browserName,
  412 | }) => {
  413 |   const d = await create(request, { review: false });
  414 |   const image = d.graph.nodes.find((n) => n.kind === "generate_image")!;
  415 |   image.config.prompt = "Synthetic restart image #restart";
  416 |   const saved = await (
  417 |     await request.put(`/api/workflows/defs/${d.id}`, {
  418 |       data: {
  419 |         name: d.name,
  420 |         description: d.description,
  421 |         icon: d.icon,
  422 |         graph: d.graph,
  423 |         version: d.version,
  424 |       },
  425 |     })
  426 |   ).json();
  427 |   const run = await start(request, saved);
  428 |   await page.goto(`/workflows/${d.id}?run=1`);
  429 |   await expect(page.locator('.wf-block[data-run="running"]')).toContainText(
  430 |     "Create images",
  431 |   );
> 432 |   expect((await request.post("/tests/restart-lifecycle")).ok()).toBe(true);
      |                                                                 ^ Error: expect(received).toBe(expected) // Object.is equality
  433 |   await page.reload();
  434 |   await expect(
  435 |     page.getByRole("button", { name: "Retry unfinished steps", exact: true }),
  436 |   ).toBeVisible();
  437 |   const interrupted = await (
  438 |     await request.get(`/api/workflows/runs/${run.id}/v2`)
  439 |   ).json();
  440 |   expect(interrupted.state).toBe("interrupted");
  441 |   expect(interrupted.nodes.n_draft.state).toBe("complete");
  442 |   await page
  443 |     .getByRole("button", { name: "Retry unfinished steps", exact: true })
  444 |     .click();
  445 |   await done(page);
  446 |   const recovered = await (
  447 |     await request.get(`/api/workflows/runs/${run.id}/v2`)
  448 |   ).json();
  449 |   expect(recovered.nodes.n_draft.attempt).toBe(1);
  450 |   expect(recovered.nodes.n_draft.output).toEqual(
  451 |     interrupted.nodes.n_draft.output,
  452 |   );
  453 |   expect(recovered.nodes.n_images.attempt).toBe(2);
  454 |   await shot(page, `restart-recovered-${browserName}`);
  455 | });
  456 | 
  457 | for (const width of [390, 1440])
  458 |   for (const theme of ["dark", "light"])
  459 |     test(`Run design states ${width} ${theme}`, async ({
  460 |       page,
  461 |       browserName,
  462 |     }) => {
  463 |       const results = [];
  464 |       await page.setViewportSize({ width, height: 900 });
  465 |       for (const state of [
  466 |         "run-running",
  467 |         "run-paused",
  468 |         "run-complete",
  469 |         "run-failed",
  470 |         "run-interrupted",
  471 |         "run-reused",
  472 |         "run-skipped",
  473 |         "pick-paused",
  474 |         "block-test",
  475 |         "setup-pick",
  476 |       ]) {
  477 |         await page.goto("/design?studio");
  478 |         await page.getByRole("button", { name: theme, exact: true }).click();
  479 |         await page.getByRole("button", { name: state, exact: true }).click();
  480 |         await settle(page);
  481 |         const scan = await new AxeBuilder({ page }).analyze();
  482 |         expect(
  483 |           scan.violations.filter((v) =>
  484 |             ["serious", "critical"].includes(v.impact ?? ""),
  485 |           ),
  486 |           `${state} ${width} ${theme}`,
  487 |         ).toEqual([]);
  488 |         results.push({ width, theme, state, seriousCritical: 0 });
  489 |         await shot(page, `${state}-${width}-${theme}-${browserName}`);
  490 |       }
  491 |       await mkdir(dir, { recursive: true });
  492 |       await writeFile(
  493 |         `${dir}/axe-states-${width}-${theme}-${browserName}.json`,
  494 |         JSON.stringify(results, null, 2),
  495 |       );
  496 |     });
  497 | test("Run activity stops for system and Always reduced motion", async ({
  498 |   page,
  499 | }) => {
  500 |   await page.setViewportSize({ width: 1440, height: 900 });
  501 |   await page.goto("/design?studio&state=run-running");
  502 |   await settle(page);
  503 |   const block = page.locator('.wf-block[data-run="running"]');
  504 |   await expect(block).toBeVisible();
  505 |   expect(
  506 |     await block.evaluate(
  507 |       (el) => getComputedStyle(el, "::before").animationName,
  508 |     ),
  509 |   ).toBe("wf-sweep");
  510 |   await page.emulateMedia({ reducedMotion: "reduce" });
  511 |   expect(
  512 |     await block.evaluate(
  513 |       (el) => getComputedStyle(el, "::before").animationName,
  514 |     ),
  515 |   ).toBe("none");
  516 |   await page.emulateMedia({ reducedMotion: "no-preference" });
  517 |   await page.evaluate(
  518 |     () => (document.documentElement.dataset.reduceMotion = "always"),
  519 |   );
  520 |   expect(
  521 |     await block.evaluate(
  522 |       (el) => getComputedStyle(el, "::before").animationName,
  523 |     ),
  524 |   ).toBe("none");
  525 | });
  526 | 
  527 | test.describe("Phone", () => {
  528 |   test.use({
  529 |     viewport: { width: 390, height: 844 },
  530 |     hasTouch: true,
  531 |     isMobile: true,
  532 |   });
```