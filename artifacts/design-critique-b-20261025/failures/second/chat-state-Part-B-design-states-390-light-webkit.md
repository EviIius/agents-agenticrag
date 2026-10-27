# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: chat-state.spec.ts >> Part B design states 390 light
- Location: web/tests/chat-state.spec.ts:387:5

# Error details

```
Error: variants

expect(received).toEqual(expected) // deep equality

- Expected  -  1
+ Received  + 49

- Array []
+ Array [
+   Object {
+     "description": "Ensure interactive controls are not nested as they are not always announced by screen readers or can cause focus problems for assistive technologies",
+     "help": "Interactive controls must not be nested",
+     "helpUrl": "https://dequeuniversity.com/rules/axe/4.13/nested-interactive?application=playwright",
+     "id": "nested-interactive",
+     "impact": "serious",
+     "nodes": Array [
+       Object {
+         "all": Array [],
+         "any": Array [
+           Object {
+             "data": null,
+             "id": "no-focusable-content",
+             "impact": "serious",
+             "message": "Element has focusable descendants",
+             "relatedNodes": Array [
+               Object {
+                 "html": "<button data-slot=\"button\" data-variant=\"ghost\" data-size=\"sm\" class=\"inline-flex items-ce...\" aria-label=\"Variants for synthet...\" aria-expanded=\"false\">",
+                 "target": Array [
+                   "button[aria-label=\"Variants for synthetic-family\"]",
+                 ],
+               },
+             ],
+           },
+         ],
+         "failureSummary": "Fix any of the following:
+   Element has focusable descendants",
+         "html": "<div data-slot=\"command-item\" class=\"relative flex cursor...\" data-active-model=\"true\" id=\"radix-_r_5c_\" cmdk-item=\"\" role=\"option\" aria-disabled=\"false\" aria-selected=\"true\" data-disabled=\"false\" data-selected=\"true\" data-value=\"qwen3.8:27b-atelier-...\">",
+         "impact": "serious",
+         "none": Array [],
+         "target": Array [
+           "#radix-_r_5c_",
+         ],
+       },
+     ],
+     "tags": Array [
+       "cat.keyboard",
+       "wcag2a",
+       "wcag412",
+       "TTv5",
+       "TT6.a",
+       "EN-301-549",
+       "EN-9.4.1.2",
+       "RGAAv4",
+       "RGAA-7.1.1",
+     ],
+   },
+ ]
```

# Page snapshot

```yaml
- generic [active]:
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
          - main:
            - heading [level=1]: Part B · synthetic chat states
            - paragraph: Invented data only. Preview actions make no model calls.
            - generic:
              - button: Aero
              - button: light
              - button: dark
              - button: thread
              - button: cleared
              - button: controls
              - button: image-controls
              - button: followup
              - button [pressed]: variants
            - generic:
              - button:
                - generic [aria-hidden]: ●
                - generic: Qwen 3.8 27B · Atelier eval · 32K
    - region "Notifications alt+T"
  - dialog [ref=e2]:
    - generic [ref=e4]:
      - heading "Choose model" [level=2] [ref=e5]
      - paragraph [ref=e6]: Local models on your Mac
    - generic [ref=e7]:
      - combobox "Search models" [expanded] [ref=e13]
      - group "Filter models" [ref=e14]:
        - button "All" [pressed] [ref=e15] [cursor=pointer]
        - button "Loaded" [ref=e16] [cursor=pointer]
        - button "Vision" [ref=e17] [cursor=pointer]
        - button "Reasoning" [ref=e18] [cursor=pointer]
        - button "Tools" [ref=e19] [cursor=pointer]
      - listbox "Suggestions" [ref=e21]:
        - generic [ref=e22]:
          - generic [aria-hidden] [ref=e23]: Ollama
          - group "Ollama" [ref=e24]:
            - option [selected] [ref=e25]:
              - generic [aria-hidden] [ref=e26]: ●
              - generic [ref=e27]:
                - generic [ref=e28]:
                  - text: Qwen 3.8 27B · Atelier eval · 32K
                  - generic [ref=e29]: Thinks
                - paragraph [ref=e30]: 16K context · Loaded
              - button "Variants for synthetic-family" [ref=e31] [cursor=pointer]: 2 variants
              - img "Selected for chat"
            - option [ref=e32]:
              - generic [aria-hidden] [ref=e33]: ●
              - generic [ref=e34]:
                - generic [ref=e35]:
                  - text: Synthetic second family
                  - generic [ref=e36]: Thinks
                - paragraph [ref=e37]: other
                - paragraph [ref=e38]: 16K context · Loaded
      - button "Manage models…" [ref=e40] [cursor=pointer]
    - button "Close" [ref=e41] [cursor=pointer]
```

# Test source

```ts
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
> 419 |         expect(violations, state).toEqual([]);
      |                                   ^ Error: variants
  420 |         expect(
  421 |           await page.evaluate(
  422 |             () => document.documentElement.scrollWidth <= innerWidth,
  423 |           ),
  424 |         ).toBeTruthy();
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