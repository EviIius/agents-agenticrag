# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: chat-state.spec.ts >> one Save retains reasoning, saves only changed scopes, and retries a partial failure without repeating the chat save
- Location: web/tests/chat-state.spec.ts:274:1

# Error details

```
Error: expect(received).toEqual(expected) // deep equality

- Expected  - 1
+ Received  + 0

  Object {
-   "reasoning": "on",
    "top_k": 23,
  }
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
          - link "New chat" [ref=e9] [cursor=pointer]:
            - /url: /
        - navigation "Chat history" [ref=e10]:
          - generic [ref=e11]:
            - textbox "Search history" [ref=e12]:
              - /placeholder: Search chats…
            - generic: ⌘K
          - navigation "Workspace" [ref=e13]:
            - link "Workflows" [ref=e15] [cursor=pointer]:
              - /url: /workflows
            - link "Images" [ref=e21] [cursor=pointer]:
              - /url: /images
          - region "Folders" [ref=e27]:
            - generic [ref=e28]:
              - heading "Folders" [level=2] [ref=e29]
              - button "New folder" [ref=e30] [cursor=pointer]
            - paragraph [ref=e31]: No folders yet
          - generic [ref=e32]:
            - paragraph [ref=e33]: Today
            - generic [ref=e34]:
              - link "Synthetic Part B image" [ref=e35] [cursor=pointer]:
                - /url: /c/3eff3365af6d4ca59ba2c9bd16c40cf1
              - button "Actions for Synthetic Part B image" [ref=e36] [cursor=pointer]
          - generic [ref=e38]:
            - link "Synthetic Part B image" [ref=e39] [cursor=pointer]:
              - /url: /c/d695b0518cfb4ec2928bf982b50f7c95
            - button "Actions for Synthetic Part B image" [ref=e40] [cursor=pointer]
        - button "Settings" [ref=e43] [cursor=pointer]
    - main [ref=e44]:
      - generic [ref=e45]:
        - button "Choose model" [ref=e47] [cursor=pointer]:
          - generic [aria-hidden] [ref=e48]: ●
          - generic [ref=e49]: fake-chat
          - generic [ref=e50]: Fake runtime
        - generic "Double-click to rename" [ref=e51]: New chat
        - button "Chat controls" [ref=e52] [cursor=pointer]
        - button "Actions for New chat" [ref=e53] [cursor=pointer]
      - status [ref=e54]
      - log "Conversation" [ref=e55]
      - generic [ref=e57]:
        - button [aria-hidden] [ref=e58] [cursor=pointer]
        - form "Message" [ref=e59]:
          - textbox "Message fake-chat" [ref=e60]:
            - /placeholder: Message…
          - generic [ref=e61]:
            - generic "Attach files · ⌘U" [ref=e62]:
              - button "Attach files" [ref=e63] [cursor=pointer]
            - button "Tools" [ref=e64] [cursor=pointer]
            - generic [ref=e67]:
              - button "No thinking" [ref=e68] [cursor=pointer]
              - button "Use model default thinking" [ref=e78] [cursor=pointer]
            - generic [ref=e82]:
              - img "24 of 8,192 total tokens; 5,888 input allowance; 2,048 reserved for response; 256 safety margin" [ref=e83]
              - generic [ref=e87]:
                - button "Send message" [disabled]
    - complementary [ref=e88]:
      - region "Chat controls" [ref=e89]:
        - generic [ref=e90]:
          - heading "Chat controls" [level=2] [ref=e91]
          - button "Close chat controls" [ref=e92] [cursor=pointer]
        - group [ref=e93]:
          - paragraph [ref=e94]: fake-chat
          - heading "This chat" [level=3] [ref=e95]
          - generic [ref=e96]:
            - text: Preset
            - combobox "Preset" [ref=e97] [cursor=pointer]:
              - generic: None
          - heading "System prompt" [level=3] [ref=e98]
          - generic [ref=e99]:
            - switch "Use default system prompt" [checked] [ref=e100] [cursor=pointer]
            - text: Use default system prompt
          - textbox "System prompt" [disabled] [ref=e101]
          - heading "Sampling" [level=3] [ref=e102]
          - group "Temperature 0.4" [ref=e103]:
            - generic [ref=e104]:
              - generic [ref=e105]: Temperature
              - generic [ref=e106]: "0.4"
            - generic [ref=e107]:
              - switch "Use model default for Temperature" [ref=e108] [cursor=pointer]
              - generic [ref=e109]: Use model default
            - generic "Temperature slider" [ref=e110]:
              - slider "Temperature slider" [ref=e114]
            - spinbutton "Temperature" [ref=e115]: "0.4"
          - group "Top P Model default" [ref=e116]:
            - generic [ref=e117]:
              - generic [ref=e118]: Top P
              - generic [ref=e119]: Model default
            - generic [ref=e120]:
              - switch "Use model default for Top P" [checked] [ref=e121] [cursor=pointer]
              - generic [ref=e122]: Use model default
          - group "Top K Model default" [ref=e123]:
            - generic [ref=e124]:
              - generic [ref=e125]: Top K
              - generic [ref=e126]: Model default
            - generic [ref=e127]:
              - switch "Use model default for Top K" [checked] [ref=e128] [cursor=pointer]
              - generic [ref=e129]: Use model default
          - group "Max output tokens Model default" [ref=e130]:
            - generic [ref=e131]:
              - generic [ref=e132]: Max output tokens
              - generic [ref=e133]: Model default
            - generic [ref=e134]:
              - switch "Use model default for Max output tokens" [checked] [ref=e135] [cursor=pointer]
              - generic [ref=e136]: Use model default
          - group "Seed Model default" [ref=e137]:
            - generic [ref=e138]:
              - generic [ref=e139]: Seed
              - generic [ref=e140]: Model default
            - generic [ref=e141]:
              - switch "Use model default for Seed" [checked] [ref=e142] [cursor=pointer]
              - generic [ref=e143]: Use model default
          - group [ref=e144]:
            - generic "Every chat with this model" [ref=e145] [cursor=pointer]
            - paragraph [ref=e146]: Saved model defaults. Explicit chat and preset values take precedence.
            - group "Model Temperature Model default" [ref=e147]:
              - generic [ref=e148]:
                - generic [ref=e149]: Model Temperature
                - generic [ref=e150]: Model default
              - generic [ref=e151]:
                - switch "Use model default for Model Temperature" [checked] [ref=e152] [cursor=pointer]
                - generic [ref=e153]: Use model default
            - group "Model Top P Model default" [ref=e154]:
              - generic [ref=e155]:
                - generic [ref=e156]: Model Top P
                - generic [ref=e157]: Model default
              - generic [ref=e158]:
                - switch "Use model default for Model Top P" [checked] [ref=e159] [cursor=pointer]
                - generic [ref=e160]: Use model default
            - group "Model Top K 23" [ref=e161]:
              - generic [ref=e162]:
                - generic [ref=e163]: Model Top K
                - generic [ref=e164]: "23"
              - generic [ref=e165]:
                - switch "Use model default for Model Top K" [ref=e166] [cursor=pointer]
                - generic [ref=e167]: Use model default
              - generic "Model Top K slider" [ref=e168]:
                - slider "Model Top K slider" [ref=e172]
              - spinbutton "Model Top K" [ref=e173]: "23"
            - group "Model Max output tokens Model default" [ref=e174]:
              - generic [ref=e175]:
                - generic [ref=e176]: Model Max output tokens
                - generic [ref=e177]: Model default
              - generic [ref=e178]:
                - switch "Use model default for Model Max output tokens" [checked] [ref=e179] [cursor=pointer]
                - generic [ref=e180]: Use model default
            - group "Model Seed Model default" [ref=e181]:
              - generic [ref=e182]:
                - generic [ref=e183]: Model Seed
                - generic [ref=e184]: Model default
              - generic [ref=e185]:
                - switch "Use model default for Model Seed" [checked] [ref=e186] [cursor=pointer]
                - generic [ref=e187]: Use model default
          - group "Context length" [ref=e188]:
            - paragraph [ref=e190]: Applies to fake-chat in every chat.
            - spinbutton "Context length" [ref=e191]: "8192"
            - paragraph [ref=e192]: "Configured limit: 16K tokens."
            - generic [ref=e193]:
              - button "4K" [ref=e194] [cursor=pointer]
              - button "8K" [pressed] [ref=e195] [cursor=pointer]
              - button "16K" [ref=e196] [cursor=pointer]
          - generic [ref=e197]:
            - button "Save settings" [disabled]: Saved
            - button "Reset to model defaults" [ref=e198] [cursor=pointer]
  - region "Notifications alt+T":
    - list:
      - listitem [ref=e199]:
        - button "Close toast" [ref=e200] [cursor=pointer]
        - generic [ref=e207]:
          - generic [ref=e208]: Something went wrong. Try again.
          - generic [ref=e209]: Synthetic defaults failure
```

# Test source

```ts
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
> 362 |   expect(updated.params_defaults).toEqual({ top_k: 23, reasoning: "on" });
      |                                   ^ Error: expect(received).toEqual(expected) // deep equality
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