# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: chat-state.spec.ts >> Part B design states 390 light
- Location: tests/chat-state.spec.ts:387:5

# Error details

```
Error: expect(received).toBeTruthy()

Received: false
```

# Page snapshot

```yaml
- generic [ref=e2]:
  - heading "Unexpected Application Error!" [level=2] [ref=e3]
  - heading "Cannot use 'in' operator to search for 'render' in div" [level=3] [ref=e4]
  - generic [ref=e5]: "TypeError: Cannot use 'in' operator to search for 'render' in div at Me (http://127.0.0.1:5173/node_modules/.vite/deps/cmdk.js?v=bea25bad:487:56) at B (http://127.0.0.1:5173/node_modules/.vite/deps/cmdk.js?v=bea25bad:490:73) at http://127.0.0.1:5173/node_modules/.vite/deps/cmdk.js?v=bea25bad:383:5 at Object.react_stack_bottom_frame (http://127.0.0.1:5173/node_modules/.vite/deps/react-dom_client.js?v=bea25bad:14142:12) at renderWithHooks (http://127.0.0.1:5173/node_modules/.vite/deps/react-dom_client.js?v=bea25bad:4400:19) at updateForwardRef (http://127.0.0.1:5173/node_modules/.vite/deps/react-dom_client.js?v=bea25bad:5597:16) at beginWork (http://127.0.0.1:5173/node_modules/.vite/deps/react-dom_client.js?v=bea25bad:6455:21) at runWithFiberInDEV (http://127.0.0.1:5173/node_modules/.vite/deps/react-dom_client.js?v=bea25bad:944:66) at performUnitOfWork (http://127.0.0.1:5173/node_modules/.vite/deps/react-dom_client.js?v=bea25bad:9148:92) at workLoopSync (http://127.0.0.1:5173/node_modules/.vite/deps/react-dom_client.js?v=bea25bad:9044:37)"
  - paragraph [ref=e6]: 💿 Hey developer 👋
  - paragraph [ref=e7]:
    - text: You can provide a way better UX than this when your app throws errors by providing your own
    - code [ref=e8]: ErrorBoundary
    - text: or
    - code [ref=e9]: errorElement
    - text: prop on your route.
```

# Test source

```ts
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
  391 |       await page.setViewportSize({ width, height: 900 });
  392 |       await page.route("**/api/images/jobs/*/output/png", (route) =>
  393 |         route.fulfill({ contentType: "image/png", body: png }),
  394 |       );
  395 |       await page.goto("/design?chat-state");
  396 |       await page.getByRole("button", { name: theme, exact: true }).click();
  397 |       await page.getByRole("button", { name: "Aero", exact: true }).click();
  398 |       await mkdir(directory, { recursive: true });
  399 |       const audits = [];
  400 |       for (const state of [
  401 |         "thread",
  402 |         "cleared",
  403 |         "controls",
  404 |         "image-controls",
  405 |         "followup",
  406 |         "variants",
  407 |       ]) {
  408 |         await page.getByRole("button", { name: state, exact: true }).click();
  409 |         if (state === "variants")
  410 |           await page
  411 |             .locator(".design-page")
  412 |             .getByRole("button", { name: "Choose model", exact: true })
  413 |             .click();
  414 |         await settle(page);
  415 |         const audit = await new AxeBuilder({ page }).analyze();
  416 |         const violations = audit.violations.filter((v) =>
  417 |           ["serious", "critical"].includes(v.impact ?? ""),
  418 |         );
  419 |         expect(violations, state).toEqual([]);
  420 |         expect(
  421 |           await page.evaluate(
  422 |             () => document.documentElement.scrollWidth <= innerWidth,
  423 |           ),
> 424 |         ).toBeTruthy();
      |           ^ Error: expect(received).toBeTruthy()
  425 |         await page.screenshot({
  426 |           path: `${directory}/${state}-${width}-${theme}-${browserName}-fake.png`,
  427 |           fullPage: true,
  428 |         });
  429 |         audits.push({ state, seriousCritical: violations.length });
  430 |         if (state === "variants") await page.keyboard.press("Escape");
  431 |       }
  432 |       await writeFile(
  433 |         `${directory}/axe-${width}-${theme}-${browserName}-fake.json`,
  434 |         JSON.stringify(audits, null, 2),
  435 |       );
  436 |     });
  437 | 
```