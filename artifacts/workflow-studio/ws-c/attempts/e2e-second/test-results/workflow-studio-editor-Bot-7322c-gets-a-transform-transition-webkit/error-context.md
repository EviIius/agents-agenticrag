# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: workflow-studio-editor.spec.ts >> Both reduced-motion triggers remove Studio motion; dragging never gets a transform transition
- Location: tests/workflow-studio-editor.spec.ts:315:1

# Error details

```
Error: expect(locator).toHaveAttribute(expected) failed

Locator:  locator('html')
Expected: "always"
Received: "system"
Timeout:  5000ms

Call log:
  - Expect "toHaveAttribute" locator('html') with timeout 5000ms
  - waiting for locator('html')
    13 × locator resolved to <html lang="en" data-theme="dark" data-text-size="M" data-answer-font="serif" data-reduce-motion="system">…</html>
       - unexpected value "system"

```

```yaml
- document:
  - complementary
  - main
  - region "Notifications alt+T"
```

# Test source

```ts
  233 |   await block(page, "n_draft");
  234 |   await page.getByText("Advanced", { exact: true }).click();
  235 |   await page
  236 |     .getByRole("textbox", { name: "Reference name", exact: true })
  237 |     .fill("draft_new");
  238 |   await page
  239 |     .getByRole("textbox", { name: "Reference name", exact: true })
  240 |     .press("Enter");
  241 |   await saved(page);
  242 |   const renamed = await def(request, d.id);
  243 |   expect(
  244 |     renamed.graph.nodes.find((n) => n.kind === "review")?.config,
  245 |   ).toMatchObject({ show: "{{draft_new.text}}" });
  246 |   await page
  247 |     .getByRole("button", { name: "Insert a variable in Prompt", exact: true })
  248 |     .click();
  249 |   await expect(
  250 |     page.getByRole("button", { name: /Start.*start.brief/ }),
  251 |   ).toBeVisible();
  252 |   await page.keyboard.press("Escape");
  253 |   await page.getByRole("button", { name: "Note", exact: true }).click();
  254 |   await page
  255 |     .getByRole("textbox", { name: "Note text", exact: true })
  256 |     .fill("Synthetic annotation");
  257 |   await saved(page);
  258 |   await page
  259 |     .getByRole("button", { name: "Tidy up", exact: true })
  260 |     .first()
  261 |     .click();
  262 |   await saved(page);
  263 |   expect((await def(request, d.id)).graph.notes[0].text).toBe(
  264 |     "Synthetic annotation",
  265 |   );
  266 | });
  267 | test("New UI states match tokens and have no serious/critical axe findings in both themes", async ({
  268 |   page,
  269 |   request,
  270 |   browserName,
  271 | }) => {
  272 |   const d = await create(request, "meeting_pack");
  273 |   await mkdir(dir, { recursive: true });
  274 |   const results = [];
  275 |   for (const theme of ["light", "dark"]) {
  276 |     await page.addInitScript(
  277 |       (v) => localStorage.setItem("workbench-theme", v),
  278 |       theme,
  279 |     );
  280 |     await page.goto(`/workflows/${d.id}`);
  281 |     await page.evaluate(
  282 |       (v) => (document.documentElement.dataset.theme = v),
  283 |       theme,
  284 |     );
  285 |     await settle(page);
  286 |     for (const state of ["canvas", "selected", "problems"]) {
  287 |       if (state === "selected") await block(page, "n_pack");
  288 |       if (state === "problems") {
  289 |         await page
  290 |           .getByRole("button", { name: "Workflow menu", exact: true })
  291 |           .click();
  292 |         await page
  293 |           .getByRole("menuitem", { name: "Problems", exact: true })
  294 |           .click();
  295 |       }
  296 |       await settle(page);
  297 |       const scan = await new AxeBuilder({ page }).analyze();
  298 |       expect(
  299 |         scan.violations.filter((v) =>
  300 |           ["serious", "critical"].includes(v.impact ?? ""),
  301 |         ),
  302 |         state,
  303 |       ).toEqual([]);
  304 |       results.push({ theme, state, seriousCritical: 0 });
  305 |       await page.screenshot({
  306 |         path: `${dir}/${state}-1440-${theme}-${browserName}-fake.png`,
  307 |       });
  308 |     }
  309 |   }
  310 |   await writeFile(
  311 |     `${dir}/axe-editor-${browserName}.json`,
  312 |     JSON.stringify(results, null, 2),
  313 |   );
  314 | });
  315 | test("Both reduced-motion triggers remove Studio motion; dragging never gets a transform transition", async ({
  316 |   page,
  317 |   request,
  318 | }) => {
  319 |   const d = await create(request, "brief_images");
  320 |   await page.emulateMedia({ reducedMotion: "reduce" });
  321 |   await page.goto(`/workflows/${d.id}`);
  322 |   await block(page, "n_draft");
  323 |   expect(
  324 |     await page
  325 |       .locator(".wf-right")
  326 |       .evaluate((e) => getComputedStyle(e).animationName),
  327 |   ).toBe("none");
  328 |   await page.emulateMedia({ reducedMotion: "no-preference" });
  329 |   await request.patch("/api/settings", {
  330 |     data: { "appearance.reduce_motion": "always" },
  331 |   });
  332 |   await page.reload();
> 333 |   await expect(page.locator("html")).toHaveAttribute(
      |                                      ^ Error: expect(locator).toHaveAttribute(expected) failed
  334 |     "data-reduce-motion",
  335 |     "always",
  336 |   );
  337 |   await block(page, "n_draft");
  338 |   expect(
  339 |     await page
  340 |       .locator(".wf-right")
  341 |       .evaluate((e) => getComputedStyle(e).animationName),
  342 |   ).toBe("none");
  343 |   expect(
  344 |     await page
  345 |       .locator(".react-flow__node[data-id='n_draft']")
  346 |       .evaluate((e) => getComputedStyle(e).transitionDuration),
  347 |   ).toBe("0s");
  348 |   await request.patch("/api/settings", {
  349 |     data: { "appearance.reduce_motion": "system" },
  350 |   });
  351 | });
  352 | test.describe("Phone Outline", () => {
  353 |   test.use({
  354 |     viewport: { width: 390, height: 844 },
  355 |     isMobile: true,
  356 |     hasTouch: true,
  357 |   });
  358 |   test("Inserts and edits through the real bottom sheets at 390px", async ({
  359 |     page,
  360 |     request,
  361 |     browserName,
  362 |   }) => {
  363 |     const d = await create(request, "brief_images");
  364 |     await page.goto(`/workflows/${d.id}`);
  365 |     await page
  366 |       .getByRole("button", { name: "Insert after Start", exact: true })
  367 |       .tap();
  368 |     const quick = page.getByRole("dialog", { name: "Add a block" });
  369 |     await quick.getByRole("combobox").fill("Generate text");
  370 |     await quick.getByRole("option").filter({ hasText: "Generate text" }).tap();
  371 |     const inspector = page.getByRole("dialog");
  372 |     await inspector
  373 |       .getByRole("textbox", { name: "Block name", exact: true })
  374 |       .fill("Synthetic phone block");
  375 |     await inspector
  376 |       .getByRole("textbox", { name: "Prompt", exact: true })
  377 |       .fill("Synthetic phone prompt");
  378 |     await page
  379 |       .getByRole("button", { name: "Close Inspector", exact: true })
  380 |       .tap();
  381 |     await expect(
  382 |       page.getByRole("button", {
  383 |         name: "Configure Synthetic phone block",
  384 |         exact: true,
  385 |       }),
  386 |     ).toBeVisible();
  387 |     await saved(page);
  388 |     await page.reload();
  389 |     await page
  390 |       .getByRole("button", {
  391 |         name: "Configure Synthetic phone block",
  392 |         exact: true,
  393 |       })
  394 |       .tap();
  395 |     await settle(page);
  396 |     expect(
  397 |       await page.evaluate(
  398 |         () => document.documentElement.scrollWidth <= innerWidth,
  399 |       ),
  400 |     ).toBeTruthy();
  401 |     const scan = await new AxeBuilder({ page }).analyze();
  402 |     expect(
  403 |       scan.violations.filter((v) =>
  404 |         ["serious", "critical"].includes(v.impact ?? ""),
  405 |       ),
  406 |     ).toEqual([]);
  407 |     await mkdir(dir, { recursive: true });
  408 |     await page.screenshot({
  409 |       path: `${dir}/phone-inspector-390-light-${browserName}-fake.png`,
  410 |     });
  411 |   });
  412 |   test("Outline reorders a chain, displays branch lanes and prevents structural edits to non-nestable graphs", async ({
  413 |     page,
  414 |     request,
  415 |     browserName,
  416 |   }) => {
  417 |     const d = await create(request, "brief_images");
  418 |     const chain = remove(d.graph, ["n_review"]);
  419 |     const put = async (graph: Definition["graph"]) => {
  420 |       const current = await def(request, d.id);
  421 |       const response = await request.put(`/api/workflows/defs/${d.id}`, {
  422 |         data: {
  423 |           name: current.name,
  424 |           description: current.description,
  425 |           icon: current.icon,
  426 |           version: current.version,
  427 |           graph,
  428 |         },
  429 |       });
  430 |       expect(response.ok()).toBeTruthy();
  431 |     };
  432 |     await put(chain);
  433 |     await page.goto(`/workflows/${d.id}`);
```