# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: composer-workflows.spec.ts >> Visual builder reflows and every node opens its settings with keyboard
- Location: tests/composer-workflows.spec.ts:235:1

# Error details

```
Test timeout of 45000ms exceeded.
```

```
Error: locator.click: Test timeout of 45000ms exceeded.
Call log:
  - waiting for getByRole('button', { name: 'dark', exact: true })

```

# Page snapshot

```yaml
- generic:
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
          - generic:
            - generic:
              - paragraph: Workflow Studio · fake runtime states
              - button: light
              - button: dark
              - button: canvas
              - button: empty
              - button: selected
              - button: problems
              - button: conflict
              - button: outline
              - button: non-nestable
              - button: settings
              - button: run-inputs
              - button: cards
            - generic [active]:
              - generic:
                - button
                - link:
                  - /url: /workflows
                - button: Synthetic image workflow
                - button
                - button: Run
              - generic:
                - generic:
                  - generic:
                    - generic:
                      - button:
                        - generic:
                          - generic: Start
                          - generic: "Inputs: Image brief"
                      - button
                    - generic:
                      - button
                  - generic:
                    - generic:
                      - button:
                        - generic:
                          - generic: Draft image prompt
                          - generic: fake-chat
                      - button
                    - generic:
                      - button
                  - generic:
                    - generic:
                      - button:
                        - generic:
                          - generic: Check the prompt
                          - generic: "Review {{draft.text}} · editable"
                      - button
                    - generic:
                      - button
                  - generic:
                    - generic:
                      - button:
                        - generic:
                          - generic: Create images
                          - generic: 1 image · FLUX.2 klein
                      - button
                    - generic:
                      - button
                  - generic:
                    - generic:
                      - button:
                        - generic:
                          - generic: Save results
                          - generic: Markdown, JSON · 2 items
                      - button
              - button
    - region "Notifications alt+T"
  - dialog [ref=e2]:
    - heading "Start" [level=2] [ref=e4]
    - paragraph [ref=e5]: Edit this workflow's settings.
    - generic [ref=e6]:
      - banner [ref=e7]:
        - generic [ref=e11]:
          - textbox "Block name" [ref=e12]: Start
          - paragraph [ref=e13]: Start
        - button "Actions for Start" [ref=e14] [cursor=pointer]
        - button "Close Inspector" [ref=e15] [cursor=pointer]
      - generic [ref=e16]:
        - tablist "Block settings" [ref=e17]:
          - tab "Setup" [selected] [ref=e18] [cursor=pointer]
          - tab "Output" [ref=e19] [cursor=pointer]
        - tabpanel "Setup" [ref=e20]:
          - heading "Inputs" [level=3] [ref=e21]
          - group "Input 1" [ref=e22]:
            - generic [ref=e24]:
              - generic [ref=e25]:
                - generic [ref=e26]: Input label
                - textbox "Input label" [ref=e27]: Image brief
              - button "Remove input Image brief" [ref=e28] [cursor=pointer]
            - generic [ref=e29]:
              - generic [ref=e30]: Input reference name
              - textbox "Input reference name" [ref=e31]: brief
            - generic [ref=e32]:
              - generic [ref=e33]: Input type
              - combobox "Input type" [ref=e34] [cursor=pointer]:
                - generic: Long text
            - generic [ref=e36]:
              - generic [ref=e37]: Required input
              - switch "Required input" [checked] [ref=e38] [cursor=pointer]
            - generic [ref=e39]:
              - generic [ref=e40]: Default value
              - textbox "Default value" [ref=e41]
            - generic [ref=e42]:
              - generic [ref=e43]: Help text
              - textbox "Help text" [ref=e44]
          - button "+ Add an input" [ref=e45] [cursor=pointer]
          - region "Connections" [ref=e46]:
            - heading "GETS INPUT FROM" [level=3] [ref=e47]
            - paragraph [ref=e48]: Start begins the run.
            - heading "SENDS OUTPUT TO" [level=3] [ref=e49]
            - generic [ref=e50]:
              - generic [ref=e51]: Draft image prompt
              - button "Remove output connection e_start_draft" [ref=e52] [cursor=pointer]
            - generic [ref=e53]:
              - generic [ref=e54]: Add an output connection
              - combobox "Add an output connection" [ref=e55] [cursor=pointer]:
                - generic: Add connection…
          - generic [ref=e56]:
            - heading "PRODUCES" [level=3] [ref=e57]
            - button "Copy reference start.brief" [ref=e59] [cursor=pointer]: "{{start.brief}}"
          - group [ref=e60]:
            - generic "Advanced" [ref=e61] [cursor=pointer]
```

# Test source

```ts
  145 |   }[] = [];
  146 |   await page.route("**/api/workflows/defs/*/runs", async (route) => {
  147 |     bodies.push(route.request().postDataJSON());
  148 |     if (bodies.length === 1) {
  149 |       const response = await route.fetch();
  150 |       accepted.push(await response.json());
  151 |       await route.abort("failed");
  152 |     } else {
  153 |       const response = await route.fetch();
  154 |       accepted.push(await response.json());
  155 |       await route.fulfill({ response });
  156 |     }
  157 |   });
  158 |   await page.getByRole("button", { name: "Run workflow", exact: true }).click();
  159 |   await expect(
  160 |     page
  161 |       .getByRole("alert")
  162 |       .filter({ hasText: /Failed to fetch|Load failed|NetworkError/ }),
  163 |   ).toBeVisible();
  164 |   await page.getByRole("button", { name: "Run workflow", exact: true }).click();
  165 |   await expect.poll(() => bodies.length).toBe(2);
  166 |   expect(bodies[1]).toEqual(bodies[0]);
  167 |   expect(accepted[1].id).toBe(accepted[0].id);
  168 |   const images = accepted[0].graph.nodes.find(
  169 |     (n) => n.kind === "generate_image",
  170 |   )!;
  171 |   expect(images.config.seeds).toHaveLength(3);
  172 |   expect(
  173 |     accepted[1].graph.nodes.find((n) => n.kind === "generate_image")!.config
  174 |       .seeds,
  175 |   ).toEqual(images.config.seeds);
  176 |   for (const seed of images.config.seeds!) {
  177 |     expect(Number.isInteger(seed)).toBe(true);
  178 |     expect(seed).toBeGreaterThanOrEqual(0);
  179 |     expect(seed).toBeLessThanOrEqual(4294967295);
  180 |   }
  181 |   const params = accepted[0].graph.nodes.find((n) => n.kind === "generate")!
  182 |     .config.params!;
  183 |   expect(Object.values(params).every((v) => v == null)).toBe(true);
  184 |   await expect(
  185 |     page
  186 |       .getByRole("article", { name: "Brief to images run" })
  187 |       .first()
  188 |       .getByRole("textbox", { name: "Review result" }),
  189 |   ).toBeVisible();
  190 | });
  191 | 
  192 | test("Image cancellation stays in composer and Workflows returns to the same saved chat", async ({
  193 |   page,
  194 |   request,
  195 |   browserName,
  196 | }) => {
  197 |   const connection = (await (await request.get("/api/connections")).json())[0];
  198 |   const response = await request.post("/api/chats", {
  199 |     data: { connection_id: connection.id, model_id: "fake-chat" },
  200 |   });
  201 |   const chat = await response.json();
  202 |   await page.goto(`/c/${chat.id}`);
  203 |   const message = page.getByRole("textbox", {
  204 |     name: "Message fake-chat",
  205 |     exact: true,
  206 |   });
  207 |   await message.fill("Synthetic saved-chat draft");
  208 |   await page.getByRole("button", { name: "Create image", exact: true }).click();
  209 |   await page
  210 |     .getByRole("textbox", { name: "Prompt", exact: true })
  211 |     .fill("Synthetic cancellable composer #slow");
  212 |   await page.getByRole("button", { name: "Generate one image" }).click();
  213 |   const job = page
  214 |     .getByRole("article")
  215 |     .filter({ hasText: "Synthetic cancellable composer #slow" })
  216 |     .first();
  217 |   await job.getByRole("button", { name: "Cancel", exact: true }).click();
  218 |   await expect(
  219 |     job.getByText("cancelled", { exact: true }).first(),
  220 |   ).toBeVisible();
  221 |   await settle(page);
  222 |   const dir = "../artifacts/composer-workflows/browser/composer";
  223 |   await mkdir(dir, { recursive: true });
  224 |   await page.screenshot({
  225 |     path: `${dir}/cancel-${browserName}-fake.png`,
  226 |     fullPage: true,
  227 |   });
  228 |   await page.getByRole("button", { name: "Message", exact: true }).click();
  229 |   await workspaceLink(page, "Workflows");
  230 |   await page.goBack();
  231 |   await expect(page).toHaveURL(new RegExp(`/c/${chat.id}$`));
  232 |   await expect(message).toHaveValue("Synthetic saved-chat draft");
  233 | });
  234 | 
  235 | test("Visual builder reflows and every node opens its settings with keyboard", async ({
  236 |   page,
  237 |   browserName,
  238 | }) => {
  239 |   const dir = "../artifacts/composer-workflows/browser/builder";
  240 |   await mkdir(dir, { recursive: true });
  241 |   for (const width of [320, 390, 1440]) {
  242 |     await page.setViewportSize({ width, height: 900 });
  243 |     await page.goto("/design?studio");
  244 |     for (const theme of ["light", "dark"]) {
> 245 |       await page.getByRole("button", { name: theme, exact: true }).click();
      |                                                                    ^ Error: locator.click: Test timeout of 45000ms exceeded.
  246 |       await configureStudioBlock(page, "Draft image prompt");
  247 |       await expect(
  248 |         page.getByRole("combobox", { name: "Model", exact: true }),
  249 |       ).toBeVisible();
  250 |       if (width < 768)
  251 |         await expect(
  252 |           page.locator(".wf-outline-row[data-selected=true]"),
  253 |         ).toContainText("Draft image prompt");
  254 |       else
  255 |         await expect(
  256 |           page.locator(".wf-block[data-selected=true]"),
  257 |         ).toContainText("Draft image prompt");
  258 |       await settle(page);
  259 |       expect(
  260 |         await page.evaluate(
  261 |           () => document.documentElement.scrollWidth <= innerWidth,
  262 |         ),
  263 |       ).toBe(true);
  264 |       const scan = await new AxeBuilder({ page }).analyze();
  265 |       expect(
  266 |         scan.violations.filter((v) =>
  267 |           ["critical", "serious"].includes(v.impact ?? ""),
  268 |         ),
  269 |       ).toEqual([]);
  270 |       await page.screenshot({
  271 |         path: `${dir}/model-${width}-${theme}-${browserName}-fake.png`,
  272 |         fullPage: true,
  273 |       });
  274 |       await configureStudioBlock(page, "Create images");
  275 |       await expect(
  276 |         page.getByRole("group", { name: "Images", exact: true }),
  277 |       ).toBeVisible();
  278 |       await configureStudioBlock(page, "Check the prompt");
  279 |       await expect(
  280 |         page.getByRole("switch", { name: "Allow editing", exact: true }),
  281 |       ).toBeVisible();
  282 |       await configureStudioBlock(page, "Start");
  283 |       await expect(
  284 |         page.getByRole("textbox", { name: "Input label", exact: true }),
  285 |       ).toHaveValue("Image brief");
  286 |     }
  287 |   }
  288 | });
  289 | 
```