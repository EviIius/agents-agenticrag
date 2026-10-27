# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: chat-state.spec.ts >> Part B design states 1440 light
- Location: tests/chat-state.spec.ts:387:5

# Error details

```
Error: variants

expect(received).toEqual(expected) // deep equality

- Expected  -   1
+ Received  + 198

- Array []
+ Array [
+   Object {
+     "description": "Ensure elements with an ARIA role that require child roles contain them",
+     "help": "Certain ARIA roles must contain particular children",
+     "helpUrl": "https://dequeuniversity.com/rules/axe/4.13/aria-required-children?application=playwright",
+     "id": "aria-required-children",
+     "impact": "critical",
+     "nodes": Array [
+       Object {
+         "all": Array [],
+         "any": Array [
+           Object {
+             "data": Object {
+               "messageKey": "unallowed",
+               "values": "[role=rowgroup]",
+             },
+             "id": "aria-required-children",
+             "impact": "critical",
+             "message": "Element has children which are not allowed: [role=rowgroup]",
+             "relatedNodes": Array [
+               Object {
+                 "html": "<div role=\"rowgroup\" class=\"p-1\" aria-label=\"Ollama\">",
+                 "target": Array [
+                   ".p-1",
+                 ],
+               },
+             ],
+           },
+         ],
+         "failureSummary": "Fix any of the following:
+   Element has children which are not allowed: [role=rowgroup]",
+         "html": "<div data-slot=\"command-list\" class=\"max-h-[300px] scroll-py-1 overflow-x-hidden overflow-y-auto min-h-0 flex-1\" role=\"listbox\" aria-label=\"Suggestions\" cmdk-list=\"\" tabindex=\"-1\" id=\"radix-_r_52_\" style=\"--cmdk-list-height: 172.0px;\">",
+         "impact": "critical",
+         "none": Array [],
+         "target": Array [
+           "#radix-_r_52_",
+         ],
+       },
+       Object {
+         "all": Array [],
+         "any": Array [
+           Object {
+             "data": Object {
+               "messageKey": "unallowed",
+               "values": "[role=option]",
+             },
+             "id": "aria-required-children",
+             "impact": "critical",
+             "message": "Element has children which are not allowed: [role=option]",
+             "relatedNodes": Array [
+               Object {
+                 "html": "<div data-slot=\"model-choice\" class=\"relative flex cursor...\" role=\"option\" data-active-model=\"true\" id=\"radix-_r_55_\" cmdk-item=\"\" aria-disabled=\"false\" aria-selected=\"true\" data-disabled=\"false\" data-selected=\"true\" data-value=\"qwen3.8:27b-atelier-...\">",
+                 "target": Array [
+                   "#radix-_r_55_",
+                 ],
+               },
+             ],
+           },
+         ],
+         "failureSummary": "Fix any of the following:
+   Element has children which are not allowed: [role=option]",
+         "html": "<div role=\"row\" class=\"flex min-w-0 items-center gap-1\">",
+         "impact": "critical",
+         "none": Array [],
+         "target": Array [
+           ".gap-1.min-w-0[role=\"row\"]:nth-child(2)",
+         ],
+       },
+       Object {
+         "all": Array [],
+         "any": Array [
+           Object {
+             "data": Object {
+               "messageKey": "unallowed",
+               "values": "[role=option]",
+             },
+             "id": "aria-required-children",
+             "impact": "critical",
+             "message": "Element has children which are not allowed: [role=option]",
+             "relatedNodes": Array [
+               Object {
+                 "html": "<div data-slot=\"model-choice\" class=\"relative flex cursor...\" role=\"option\" data-active-model=\"false\" id=\"radix-_r_56_\" cmdk-item=\"\" aria-disabled=\"false\" aria-selected=\"false\" data-disabled=\"false\" data-selected=\"false\" data-value=\"Synthetic second fam...\">",
+                 "target": Array [
+                   "#radix-_r_56_",
+                 ],
+               },
+             ],
+           },
+         ],
+         "failureSummary": "Fix any of the following:
+   Element has children which are not allowed: [role=option]",
+         "html": "<div role=\"row\" class=\"flex min-w-0 items-center gap-1\">",
+         "impact": "critical",
+         "none": Array [],
+         "target": Array [
+           ".gap-1.min-w-0[role=\"row\"]:nth-child(3)",
+         ],
+       },
+     ],
+     "tags": Array [
+       "cat.aria",
+       "wcag2a",
+       "wcag131",
+       "EN-301-549",
+       "EN-9.1.3.1",
+       "RGAAv4",
+       "RGAA-9.3.1",
+     ],
+   },
+   Object {
+     "description": "Ensure elements with an ARIA role that require parent roles are contained by them",
+     "help": "Certain ARIA roles must be contained by particular parents",
+     "helpUrl": "https://dequeuniversity.com/rules/axe/4.13/aria-required-parent?application=playwright",
+     "id": "aria-required-parent",
+     "impact": "critical",
+     "nodes": Array [
+       Object {
+         "all": Array [],
+         "any": Array [
+           Object {
+             "data": Array [
+               "grid",
+               "table",
+               "treegrid",
+             ],
+             "id": "aria-required-parent",
+             "impact": "critical",
+             "message": "Required ARIA parents role not present: grid, table, treegrid",
+             "relatedNodes": Array [],
+           },
+         ],
+         "failureSummary": "Fix any of the following:
+   Required ARIA parents role not present: grid, table, treegrid",
+         "html": "<div role=\"rowgroup\" class=\"p-1\" aria-label=\"Ollama\">",
+         "impact": "critical",
+         "none": Array [],
+         "target": Array [
+           ".p-1",
+         ],
+       },
+       Object {
+         "all": Array [],
+         "any": Array [
+           Object {
+             "data": Array [
+               "group",
+               "listbox",
+             ],
+             "id": "aria-required-parent",
+             "impact": "critical",
+             "message": "Required ARIA parents role not present: group, listbox",
+             "relatedNodes": Array [],
+           },
+         ],
+         "failureSummary": "Fix any of the following:
+   Required ARIA parents role not present: group, listbox",
+         "html": "<div data-slot=\"model-choice\" class=\"relative flex cursor...\" role=\"option\" data-active-model=\"true\" id=\"radix-_r_55_\" cmdk-item=\"\" aria-disabled=\"false\" aria-selected=\"true\" data-disabled=\"false\" data-selected=\"true\" data-value=\"qwen3.8:27b-atelier-...\">",
+         "impact": "critical",
+         "none": Array [],
+         "target": Array [
+           "#radix-_r_55_",
+         ],
+       },
+       Object {
+         "all": Array [],
+         "any": Array [
+           Object {
+             "data": Array [
+               "group",
+               "listbox",
+             ],
+             "id": "aria-required-parent",
+             "impact": "critical",
+             "message": "Required ARIA parents role not present: group, listbox",
+             "relatedNodes": Array [],
+           },
+         ],
+         "failureSummary": "Fix any of the following:
+   Required ARIA parents role not present: group, listbox",
+         "html": "<div data-slot=\"model-choice\" class=\"relative flex cursor...\" role=\"option\" data-active-model=\"false\" id=\"radix-_r_56_\" cmdk-item=\"\" aria-disabled=\"false\" aria-selected=\"false\" data-disabled=\"false\" data-selected=\"false\" data-value=\"Synthetic second fam...\">",
+         "impact": "critical",
+         "none": Array [],
+         "target": Array [
+           "#radix-_r_56_",
+         ],
+       },
+     ],
+     "tags": Array [
+       "cat.aria",
+       "wcag2a",
+       "wcag131",
+       "EN-301-549",
+       "EN-9.1.3.1",
+       "RGAAv4",
+       "RGAA-9.3.1",
+     ],
+   },
+ ]
```

# Page snapshot

```yaml
- generic [ref=e1]:
  - generic [ref=e2]:
    - generic [ref=e3]:
      - complementary [ref=e4]:
        - generic [ref=e5]:
          - generic [ref=e6]:
            - button "Collapse sidebar" [ref=e7] [cursor=pointer]
            - generic [ref=e8]: Aether
            - link "New chat" [ref=e9] [cursor=pointer]:
              - /url: /design/chat
          - navigation "Chat history" [ref=e10]:
            - navigation "Workspace" [ref=e11]:
              - link "Workflows" [ref=e13] [cursor=pointer]:
                - /url: /workflows
              - link "Images" [ref=e19] [cursor=pointer]:
                - /url: /images
            - paragraph [ref=e25]: TODAY
            - link "A clearer way to learn" [ref=e27] [cursor=pointer]:
              - /url: /design/chat/fixture
            - link "Planning a weekend" [ref=e34] [cursor=pointer]:
              - /url: /design/chat/fixture
            - link "Understanding a short function" [ref=e41] [cursor=pointer]:
              - /url: /design/chat/fixture
            - link "Making a useful checklist" [ref=e48] [cursor=pointer]:
              - /url: /design/chat/fixture
            - paragraph [ref=e54]: YESTERDAY
            - link "A fresh perspective" [ref=e55] [cursor=pointer]:
              - /url: /design/chat/fixture
          - button "Settings" [ref=e59] [cursor=pointer]
      - main [ref=e60]:
        - generic [ref=e61]:
          - button "Choose model" [ref=e63] [cursor=pointer]:
            - generic [aria-hidden] [ref=e64]: ●
            - generic [ref=e65]: fake-chat
          - generic [ref=e66]: A clearer way to learn
          - generic [ref=e67]:
            - button "Chat controls" [ref=e68] [cursor=pointer]
            - button "Chat actions" [ref=e69] [cursor=pointer]
        - main [ref=e71]:
          - heading "Part B · synthetic chat states" [level=1] [ref=e72]
          - paragraph [ref=e73]: Invented data only. Preview actions make no model calls.
          - generic [ref=e74]:
            - button "Aero" [ref=e75] [cursor=pointer]
            - button "light" [ref=e76] [cursor=pointer]
            - button "dark" [ref=e77] [cursor=pointer]
            - button "thread" [ref=e78] [cursor=pointer]
            - button "cleared" [ref=e79] [cursor=pointer]
            - button "controls" [ref=e80] [cursor=pointer]
            - button "image-controls" [ref=e81] [cursor=pointer]
            - button "followup" [ref=e82] [cursor=pointer]
            - button "variants" [pressed] [ref=e83] [cursor=pointer]
          - status
          - button "Choose model" [expanded] [ref=e84] [cursor=pointer]:
            - generic [aria-hidden] [ref=e85]: ●
            - generic [ref=e86]: Qwen 3.8 27B · Atelier eval · 32K
    - region "Notifications alt+T"
  - dialog "Choose model" [ref=e88]:
    - generic [ref=e89]:
      - combobox "Search models" [expanded] [active] [ref=e95]
      - group "Filter models" [ref=e96]:
        - button "All" [pressed] [ref=e97] [cursor=pointer]
        - button "Loaded" [ref=e98] [cursor=pointer]
        - button "Vision" [ref=e99] [cursor=pointer]
        - button "Reasoning" [ref=e100] [cursor=pointer]
        - button "Tools" [ref=e101] [cursor=pointer]
      - listbox "Suggestions" [ref=e103]:
        - rowgroup "Ollama" [ref=e105]:
          - row [ref=e106]:
            - columnheader "Ollama" [ref=e107]
          - row [ref=e108]:
            - option [selected] [ref=e109]:
              - generic [aria-hidden] [ref=e110]: ●
              - generic [ref=e111]:
                - generic [ref=e112]:
                  - text: Qwen 3.8 27B · Atelier eval · 32K
                  - generic [ref=e113]: Thinks
                - paragraph [ref=e114]: 16K context · Loaded
              - img "Selected for chat"
            - gridcell "Model actions" [ref=e115]:
              - button "Variants for synthetic-family" [ref=e116] [cursor=pointer]: 2 variants
          - row [ref=e117]:
            - option [ref=e118]:
              - generic [aria-hidden] [ref=e119]: ●
              - generic [ref=e120]:
                - generic [ref=e121]:
                  - text: Synthetic second family
                  - generic [ref=e122]: Thinks
                - paragraph [ref=e123]: other
                - paragraph [ref=e124]: 16K context · Loaded
            - gridcell "Model actions"
      - button "Manage models…" [ref=e126] [cursor=pointer]
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