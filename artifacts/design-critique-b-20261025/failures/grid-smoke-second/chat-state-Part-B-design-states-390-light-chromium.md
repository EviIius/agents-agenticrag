# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: chat-state.spec.ts >> Part B design states 390 light
- Location: tests/chat-state.spec.ts:387:5

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: getByRole('heading', { name: 'Part B · synthetic chat states' })
Expected: visible
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" getByRole('heading', { name: 'Part B · synthetic chat states' }) with timeout 5000ms
  - waiting for getByRole('heading', { name: 'Part B · synthetic chat states' })

```

```yaml
- region "Notifications alt+T"
- dialog "Choose model":
  - heading "Choose model" [level=2]
  - paragraph: Local models on your Mac
  - combobox "Search models" [expanded]
  - group "Filter models":
    - button "All" [pressed]
    - button "Loaded"
    - button "Vision"
    - button "Reasoning"
    - button "Tools"
  - grid "Models":
    - rowgroup "Ollama":
      - row "Ollama":
        - columnheader "Ollama"
      - row "Qwen 3.8 27B · Atelier eval · 32K Thinks 16K context · Loaded Selected for chat Model actions":
        - gridcell "Qwen 3.8 27B · Atelier eval · 32K Thinks 16K context · Loaded Selected for chat" [selected]:
          - text: Qwen 3.8 27B · Atelier eval · 32K Thinks
          - paragraph: 16K context · Loaded
          - img "Selected for chat"
        - gridcell "Model actions":
          - button "Variants for synthetic-family": 2 variants
      - row "Synthetic second family Thinks other 16K context · Loaded Model actions":
        - gridcell "Synthetic second family Thinks other 16K context · Loaded":
          - text: Synthetic second family Thinks
          - paragraph: other
          - paragraph: 16K context · Loaded
        - gridcell "Model actions"
  - button "Manage models…"
  - button "Close"
```

# Test source

```ts
  318 |   await page.goto(`/c/${chat.id}`);
  319 |   await page
  320 |     .getByRole("button", { name: "Chat controls", exact: true })
  321 |     .click();
  322 |   const controls = page.getByRole("region", { name: "Chat controls" });
  323 |   await expect(
  324 |     controls.getByRole("combobox", { name: "Reasoning" }),
  325 |   ).toHaveCount(0);
  326 |   await controls
  327 |     .getByRole("switch", {
  328 |       name: "Use model default for Temperature",
  329 |       exact: true,
  330 |     })
  331 |     .click();
  332 |   await controls
  333 |     .getByRole("spinbutton", { name: "Temperature", exact: true })
  334 |     .fill("0.4");
  335 |   await controls
  336 |     .locator("summary")
  337 |     .filter({ hasText: "Every chat with this model" })
  338 |     .click();
  339 |   await controls
  340 |     .getByRole("switch", {
  341 |       name: "Use model default for Model Top K",
  342 |       exact: true,
  343 |     })
  344 |     .click();
  345 |   await controls
  346 |     .getByRole("spinbutton", { name: "Model Top K", exact: true })
  347 |     .fill("23");
  348 |   await controls
  349 |     .getByRole("spinbutton", { name: "Context length" })
  350 |     .fill("8192");
  351 |   const save = controls.getByRole("button", {
  352 |     name: "Save settings",
  353 |     exact: true,
  354 |   });
  355 |   await save.click();
  356 |   await expect(
  357 |     page.getByText("Synthetic defaults failure", { exact: true }),
  358 |   ).toBeVisible();
  359 |   await expect(save).toBeEnabled();
  360 |   expect(patches).toBe(1);
  361 |   expect(
  362 |     (await (await request.get(`/api/chats/${chat.id}`)).json()).chat.params,
  363 |   ).toEqual({ temperature: 0.4, reasoning: "off" });
  364 |   await save.click();
  365 |   await expect(save).toContainText("Saved");
  366 |   expect(patches).toBe(1);
  367 |   const models = await (await request.get("/api/models")).json();
  368 |   const updated = models.find(
  369 |     (m: { model_id: string }) => m.model_id === "fake-reasoning",
  370 |   );
  371 |   expect(updated.params_defaults).toEqual({ top_k: 23, reasoning: "on" });
  372 |   expect(updated.context_length).toBe(8192);
  373 |   await page.keyboard.press("Escape");
  374 |   await expect(controls).not.toBeVisible();
  375 |   await request.put("/api/models/prefs", {
  376 |     data: {
  377 |       connection_id: connection.id,
  378 |       model_id: "fake-reasoning",
  379 |       params: {},
  380 |       context_length: 16384,
  381 |     },
  382 |   });
  383 | });
  384 | 
  385 | for (const width of [390, 1440])
  386 |   for (const theme of ["light", "dark"])
  387 |     test(`Part B design states ${width} ${theme}`, async ({
  388 |       page,
  389 |       browserName,
  390 |     }) => {
  391 |       const pageErrors: string[] = [];
  392 |       page.on("pageerror", (error) => pageErrors.push(error.message));
  393 |       await page.setViewportSize({ width, height: 900 });
  394 |       await page.route("**/api/images/jobs/*/output/png", (route) =>
  395 |         route.fulfill({ contentType: "image/png", body: png }),
  396 |       );
  397 |       await page.goto("/design?chat-state");
  398 |       await page.getByRole("button", { name: theme, exact: true }).click();
  399 |       await page.getByRole("button", { name: "Aero", exact: true }).click();
  400 |       await mkdir(directory, { recursive: true });
  401 |       const audits = [];
  402 |       for (const state of [
  403 |         "thread",
  404 |         "cleared",
  405 |         "controls",
  406 |         "image-controls",
  407 |         "followup",
  408 |         "variants",
  409 |       ]) {
  410 |         await page.getByRole("button", { name: state, exact: true }).click();
  411 |         if (state === "variants")
  412 |           await page
  413 |             .locator(".design-page")
  414 |             .getByRole("button", { name: "Choose model", exact: true })
  415 |             .click();
  416 |         await expect(
  417 |           page.getByRole("heading", { name: "Part B · synthetic chat states" }),
> 418 |         ).toBeVisible();
      |           ^ Error: expect(locator).toBeVisible() failed
  419 |         expect(pageErrors).toEqual([]);
  420 |         await settle(page);
  421 |         const audit = await new AxeBuilder({ page }).analyze();
  422 |         const violations = audit.violations.filter((v) =>
  423 |           ["serious", "critical"].includes(v.impact ?? ""),
  424 |         );
  425 |         expect(violations, state).toEqual([]);
  426 |         expect(
  427 |           await page.evaluate(
  428 |             () => document.documentElement.scrollWidth <= innerWidth,
  429 |           ),
  430 |         ).toBeTruthy();
  431 |         await page.screenshot({
  432 |           path: `${directory}/${state}-${width}-${theme}-${browserName}-fake.png`,
  433 |           fullPage: true,
  434 |         });
  435 |         audits.push({ state, seriousCritical: violations.length });
  436 |         if (state === "variants") await page.keyboard.press("Escape");
  437 |       }
  438 |       await writeFile(
  439 |         `${directory}/axe-${width}-${theme}-${browserName}-fake.json`,
  440 |         JSON.stringify(audits, null, 2),
  441 |       );
  442 |     });
  443 | 
```