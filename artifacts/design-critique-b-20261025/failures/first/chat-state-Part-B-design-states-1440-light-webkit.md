# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: chat-state.spec.ts >> Part B design states 1440 light
- Location: web/tests/chat-state.spec.ts:378:5

# Error details

```
Error: locator.click: Error: strict mode violation: getByRole('button', { name: 'Choose model', exact: true }) resolved to 2 elements:
    1) <button type="button" data-size="default" data-state="closed" data-variant="ghost" aria-expanded="false" aria-haspopup="dialog" aria-label="Choose model" data-slot="popover-trigger" class="inline-flex shrink-0 items-center justify-center rounded-md text-sm font-medium whitespace-nowrap outline-none disabled:pointer-events-none disabled:opacity-50 aria-invalid:border-destructive aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:no…>…</button> aka getByText('●fake-chat')
    2) <button type="button" data-size="default" data-state="closed" data-variant="ghost" aria-expanded="false" aria-haspopup="dialog" aria-label="Choose model" data-slot="popover-trigger" class="inline-flex shrink-0 items-center justify-center rounded-md text-sm font-medium whitespace-nowrap outline-none disabled:pointer-events-none disabled:opacity-50 aria-invalid:border-destructive aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:no…>…</button> aka getByText('●Qwen 3.8 27B · Atelier eval')

Call log:
  - waiting for getByRole('button', { name: 'Choose model', exact: true })

```

# Page snapshot

```yaml
- generic [ref=e2]:
  - generic [ref=e3]:
    - complementary [ref=e4]:
      - generic [ref=e5]:
        - generic [ref=e6]:
          - button "Collapse sidebar" [ref=e7] [cursor=pointer]
          - generic [ref=e8]: Aether
          - link "New chat" [ref=e9]:
            - /url: /design/chat
        - navigation "Chat history" [ref=e10]:
          - navigation "Workspace" [ref=e11]:
            - link "Workflows" [ref=e13]:
              - /url: /workflows
            - link "Images" [ref=e19]:
              - /url: /images
          - paragraph [ref=e25]: TODAY
          - link "A clearer way to learn" [ref=e27]:
            - /url: /design/chat/fixture
          - link "Planning a weekend" [ref=e34]:
            - /url: /design/chat/fixture
          - link "Understanding a short function" [ref=e41]:
            - /url: /design/chat/fixture
          - link "Making a useful checklist" [ref=e48]:
            - /url: /design/chat/fixture
          - paragraph [ref=e54]: YESTERDAY
          - link "A fresh perspective" [ref=e55]:
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
          - button "light" [ref=e75] [cursor=pointer]
          - button "dark" [ref=e76] [cursor=pointer]
          - button "thread" [ref=e77] [cursor=pointer]
          - button "cleared" [ref=e78] [cursor=pointer]
          - button "controls" [ref=e79] [cursor=pointer]
          - button "image-controls" [ref=e80] [cursor=pointer]
          - button "followup" [ref=e81] [cursor=pointer]
          - button "variants" [pressed] [ref=e82] [cursor=pointer]
        - status
        - button "Choose model" [ref=e83] [cursor=pointer]:
          - generic [aria-hidden] [ref=e84]: ●
          - generic [ref=e85]: Qwen 3.8 27B · Atelier eval · 32K
  - region "Notifications alt+T"
```

# Test source

```ts
  302 |         body: JSON.stringify({
  303 |           error: { code: "unavailable", message: "Synthetic defaults failure" },
  304 |         }),
  305 |       });
  306 |     }
  307 |     return route.continue();
  308 |   });
  309 |   await page.goto(`/c/${chat.id}`);
  310 |   await page
  311 |     .getByRole("button", { name: "Chat controls", exact: true })
  312 |     .click();
  313 |   const controls = page.getByRole("region", { name: "Chat controls" });
  314 |   await expect(
  315 |     controls.getByRole("combobox", { name: "Reasoning" }),
  316 |   ).toHaveCount(0);
  317 |   await controls
  318 |     .getByRole("switch", {
  319 |       name: "Use model default for Temperature",
  320 |       exact: true,
  321 |     })
  322 |     .click();
  323 |   await controls
  324 |     .getByRole("spinbutton", { name: "Temperature", exact: true })
  325 |     .fill("0.4");
  326 |   await controls
  327 |     .locator("summary")
  328 |     .filter({ hasText: "Every chat with this model" })
  329 |     .click();
  330 |   await controls
  331 |     .getByRole("switch", {
  332 |       name: "Use model default for Model Top K",
  333 |       exact: true,
  334 |     })
  335 |     .click();
  336 |   await controls
  337 |     .getByRole("spinbutton", { name: "Model Top K", exact: true })
  338 |     .fill("23");
  339 |   await controls
  340 |     .getByRole("spinbutton", { name: "Context length" })
  341 |     .fill("8192");
  342 |   const save = controls.getByRole("button", {
  343 |     name: "Save settings",
  344 |     exact: true,
  345 |   });
  346 |   await save.click();
  347 |   await expect(
  348 |     page.getByText("Synthetic defaults failure", { exact: true }),
  349 |   ).toBeVisible();
  350 |   await expect(save).toBeEnabled();
  351 |   expect(patches).toBe(1);
  352 |   expect(
  353 |     (await (await request.get(`/api/chats/${chat.id}`)).json()).chat.params,
  354 |   ).toEqual({ temperature: 0.4, reasoning: "off" });
  355 |   await save.click();
  356 |   await expect(save).toContainText("Saved");
  357 |   expect(patches).toBe(1);
  358 |   const models = await (await request.get("/api/models")).json();
  359 |   const updated = models.find(
  360 |     (m: { model_id: string }) => m.model_id === "fake-chat",
  361 |   );
  362 |   expect(updated.params_defaults).toEqual({ top_k: 23, reasoning: "on" });
  363 |   expect(updated.context_length).toBe(8192);
  364 |   await page.keyboard.press("Escape");
  365 |   await expect(controls).not.toBeVisible();
  366 |   await request.put("/api/models/prefs", {
  367 |     data: {
  368 |       connection_id: connection.id,
  369 |       model_id: "fake-chat",
  370 |       params: {},
  371 |       context_length: 16384,
  372 |     },
  373 |   });
  374 | });
  375 | 
  376 | for (const width of [390, 1440])
  377 |   for (const theme of ["light", "dark"])
  378 |     test(`Part B design states ${width} ${theme}`, async ({
  379 |       page,
  380 |       browserName,
  381 |     }) => {
  382 |       await page.setViewportSize({ width, height: 900 });
  383 |       await page.route("**/api/images/jobs/*/output/png", (route) =>
  384 |         route.fulfill({ contentType: "image/png", body: png }),
  385 |       );
  386 |       await page.goto("/design?chat-state");
  387 |       await page.getByRole("button", { name: theme, exact: true }).click();
  388 |       await mkdir(directory, { recursive: true });
  389 |       const audits = [];
  390 |       for (const state of [
  391 |         "thread",
  392 |         "cleared",
  393 |         "controls",
  394 |         "image-controls",
  395 |         "followup",
  396 |         "variants",
  397 |       ]) {
  398 |         await page.getByRole("button", { name: state, exact: true }).click();
  399 |         if (state === "variants")
  400 |           await page
  401 |             .getByRole("button", { name: "Choose model", exact: true })
> 402 |             .click();
      |              ^ Error: locator.click: Error: strict mode violation: getByRole('button', { name: 'Choose model', exact: true }) resolved to 2 elements:
  403 |         await settle(page);
  404 |         const audit = await new AxeBuilder({ page }).analyze();
  405 |         const violations = audit.violations.filter((v) =>
  406 |           ["serious", "critical"].includes(v.impact ?? ""),
  407 |         );
  408 |         expect(violations, state).toEqual([]);
  409 |         expect(
  410 |           await page.evaluate(
  411 |             () => document.documentElement.scrollWidth <= innerWidth,
  412 |           ),
  413 |         ).toBeTruthy();
  414 |         await page.screenshot({
  415 |           path: `${directory}/${state}-${width}-${theme}-${browserName}-fake.png`,
  416 |           fullPage: true,
  417 |         });
  418 |         audits.push({ state, seriousCritical: violations.length });
  419 |         if (state === "variants") await page.keyboard.press("Escape");
  420 |       }
  421 |       await writeFile(
  422 |         `${directory}/axe-${width}-${theme}-${browserName}-fake.json`,
  423 |         JSON.stringify(audits, null, 2),
  424 |       );
  425 |     });
  426 | 
```