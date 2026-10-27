# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: chat-state.spec.ts >> one Save retains reasoning, saves only changed scopes, and retries a partial failure without repeating the chat save
- Location: web/tests/chat-state.spec.ts:274:1

# Error details

```
Test timeout of 45000ms exceeded.
```

```
Error: locator.fill: Test timeout of 45000ms exceeded.
Call log:
  - waiting for getByRole('region', { name: 'Chat controls' }).getByRole('spinbutton', { name: 'Model Top K', exact: true })

```

# Page snapshot

```yaml
- generic:
  - generic:
    - generic:
      - main:
        - generic [aria-hidden]:
          - generic:
            - button
            - generic:
              - button:
                - generic [aria-hidden]: ●
                - generic: fake-chat
          - button:
            - generic: Unsaved changes
          - button
        - status [aria-hidden]
        - log "Conversation"
        - generic [aria-hidden]:
          - button [aria-hidden]
          - form:
            - textbox:
              - /placeholder: Message…
            - generic:
              - generic:
                - button [aria-hidden]
                - button
              - button
              - generic:
                - generic:
                  - button
                  - button
              - generic:
                - generic:
                  - button [disabled]
    - region "Notifications alt+T"
  - dialog [active] [ref=e2]:
    - generic [ref=e4]:
      - button "Close chat controls" [ref=e5] [cursor=pointer]
      - heading "Chat controls" [level=2] [ref=e6]
      - paragraph [ref=e7]: Sampling and context for this conversation
    - region "Chat controls" [ref=e9]:
      - group [ref=e10]:
        - paragraph [ref=e11]: fake-chat
        - heading "This chat" [level=3] [ref=e12]
        - generic [ref=e13]:
          - text: Preset
          - combobox "Preset" [ref=e14] [cursor=pointer]:
            - generic: None
        - heading "System prompt" [level=3] [ref=e15]
        - generic [ref=e16]:
          - switch "Use default system prompt" [checked] [ref=e17] [cursor=pointer]
          - text: Use default system prompt
        - textbox "System prompt" [disabled] [ref=e18]
        - heading "Sampling" [level=3] [ref=e19]
        - group "Temperature 0.4" [ref=e20]:
          - generic [ref=e21]:
            - generic [ref=e22]: Temperature
            - generic [ref=e23]: "0.4"
          - generic [ref=e24]:
            - switch "Use model default for Temperature" [ref=e25] [cursor=pointer]
            - generic [ref=e26]: Use model default
          - generic "Temperature slider" [ref=e27]:
            - slider "Temperature slider" [ref=e31]
          - spinbutton "Temperature" [ref=e32]: "0.4"
        - group "Top P Model default" [ref=e33]:
          - generic [ref=e34]:
            - generic [ref=e35]: Top P
            - generic [ref=e36]: Model default
          - generic [ref=e37]:
            - switch "Use model default for Top P" [checked] [ref=e38] [cursor=pointer]
            - generic [ref=e39]: Use model default
        - group "Top K Model default" [ref=e40]:
          - generic [ref=e41]:
            - generic [ref=e42]: Top K
            - generic [ref=e43]: Model default
          - generic [ref=e44]:
            - switch "Use model default for Top K" [checked] [ref=e45] [cursor=pointer]
            - generic [ref=e46]: Use model default
        - group "Max output tokens Model default" [ref=e47]:
          - generic [ref=e48]:
            - generic [ref=e49]: Max output tokens
            - generic [ref=e50]: Model default
          - generic [ref=e51]:
            - switch "Use model default for Max output tokens" [checked] [ref=e52] [cursor=pointer]
            - generic [ref=e53]: Use model default
        - group "Seed Model default" [ref=e54]:
          - generic [ref=e55]:
            - generic [ref=e56]: Seed
            - generic [ref=e57]: Model default
          - generic [ref=e58]:
            - switch "Use model default for Seed" [checked] [ref=e59] [cursor=pointer]
            - generic [ref=e60]: Use model default
        - group [ref=e61]:
          - generic "Every chat with this model" [ref=e62] [cursor=pointer]
          - paragraph [ref=e63]: Saved model defaults. Explicit chat and preset values take precedence.
          - group "Model Temperature Model default" [ref=e64]:
            - generic [ref=e65]:
              - generic [ref=e66]: Model Temperature
              - generic [ref=e67]: Model default
            - generic [ref=e68]:
              - switch "Use model default for Model Temperature" [checked] [ref=e69] [cursor=pointer]
              - generic [ref=e70]: Use model default
          - group "Model Top P Model default" [ref=e71]:
            - generic [ref=e72]:
              - generic [ref=e73]: Model Top P
              - generic [ref=e74]: Model default
            - generic [ref=e75]:
              - switch "Use model default for Model Top P" [checked] [ref=e76] [cursor=pointer]
              - generic [ref=e77]: Use model default
          - group "Model Top K Model default" [ref=e78]:
            - generic [ref=e79]:
              - generic [ref=e80]: Model Top K
              - generic [ref=e81]: Model default
            - generic [ref=e82]:
              - switch "Use model default for Model Top K" [checked] [ref=e83] [cursor=pointer]
              - generic [ref=e84]: Use model default
          - group "Model Max output tokens Model default" [ref=e85]:
            - generic [ref=e86]:
              - generic [ref=e87]: Model Max output tokens
              - generic [ref=e88]: Model default
            - generic [ref=e89]:
              - switch "Use model default for Model Max output tokens" [checked] [ref=e90] [cursor=pointer]
              - generic [ref=e91]: Use model default
          - group "Model Seed Model default" [ref=e92]:
            - generic [ref=e93]:
              - generic [ref=e94]: Model Seed
              - generic [ref=e95]: Model default
            - generic [ref=e96]:
              - switch "Use model default for Model Seed" [checked] [ref=e97] [cursor=pointer]
              - generic [ref=e98]: Use model default
        - group "Context length" [ref=e99]:
          - paragraph [ref=e101]: Applies to fake-chat in every chat.
          - spinbutton "Context length" [ref=e102]: "8192"
          - paragraph [ref=e103]: "Configured limit: 16K tokens."
          - generic [ref=e104]:
            - button "4K" [ref=e105] [cursor=pointer]
            - button "8K" [pressed] [ref=e106] [cursor=pointer]
            - button "16K" [ref=e107] [cursor=pointer]
        - generic [ref=e108]:
          - status [ref=e109]: Unsaved changes
          - button "Save settings" [ref=e110] [cursor=pointer]
          - button "Reset to model defaults" [ref=e111] [cursor=pointer]
```

# Test source

```ts
  238 |           message: "Synthetic rejected continuation",
  239 |         },
  240 |       }),
  241 |     });
  242 |   });
  243 |   await page.goto(`/c/${chat.id}`);
  244 |   const stopped = page.locator('[data-message-id="stopped-synthetic"]');
  245 |   const empty = page.locator('[data-message-id="empty-synthetic"]');
  246 |   await expect(stopped.locator('[data-slot="reply-outcome"]')).toContainText(
  247 |     "Stopped",
  248 |   );
  249 |   await expect(
  250 |     stopped.getByRole("button", { name: "Retry", exact: true }),
  251 |   ).toHaveCount(1);
  252 |   await expect(
  253 |     stopped.getByRole("button", { name: "Regenerate answer", exact: true }),
  254 |   ).toHaveCount(0);
  255 |   await expect(empty.locator('[data-slot="reply-outcome"]')).toContainText(
  256 |     "No answer",
  257 |   );
  258 |   await page.locator(".composer textarea").fill("An unsent draft");
  259 |   await stopped.getByRole("button", { name: "Continue", exact: true }).click();
  260 |   await expect(page.getByRole("alert")).toContainText(
  261 |     "Synthetic rejected continuation",
  262 |   );
  263 |   expect(body).toMatchObject({
  264 |     content: "Continue your previous answer.",
  265 |     parent_id: "stopped-synthetic",
  266 |     attachment_ids: [],
  267 |   });
  268 |   await expect(page.locator(".composer textarea")).toHaveValue(
  269 |     "An unsent draft",
  270 |   );
  271 |   await expect(stopped).toContainText("I'd begin");
  272 | });
  273 | 
  274 | test("one Save retains reasoning, saves only changed scopes, and retries a partial failure without repeating the chat save", async ({
  275 |   page,
  276 |   request,
  277 | }) => {
  278 |   const { connection, chat } = await setup(request);
  279 |   await request.put("/api/models/prefs", {
  280 |     data: {
  281 |       connection_id: connection.id,
  282 |       model_id: "fake-chat",
  283 |       params: { reasoning: "on" },
  284 |       context_length: 16384,
  285 |     },
  286 |   });
  287 |   await request.patch(`/api/chats/${chat.id}`, {
  288 |     data: { params: { reasoning: "off" } },
  289 |   });
  290 |   let patches = 0,
  291 |     failed = false;
  292 |   page.on("request", (req) => {
  293 |     if (req.method() === "PATCH" && req.url().endsWith(`/api/chats/${chat.id}`))
  294 |       patches++;
  295 |   });
  296 |   await page.route("**/api/models/prefs", (route) => {
  297 |     if (!failed && route.request().postDataJSON().params) {
  298 |       failed = true;
  299 |       return route.fulfill({
  300 |         status: 503,
  301 |         contentType: "application/json",
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
> 338 |     .fill("23");
      |      ^ Error: locator.fill: Test timeout of 45000ms exceeded.
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
  402 |             .click();
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