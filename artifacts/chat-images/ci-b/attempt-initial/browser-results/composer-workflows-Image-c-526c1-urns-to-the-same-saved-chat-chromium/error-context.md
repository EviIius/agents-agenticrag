# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: composer-workflows.spec.ts >> Image cancellation stays in composer and Workflows returns to the same saved chat
- Location: tests/composer-workflows.spec.ts:195:1

# Error details

```
Test timeout of 45000ms exceeded.
```

```
Error: locator.fill: Test timeout of 45000ms exceeded.
Call log:
  - waiting for getByRole('textbox', { name: 'Prompt', exact: true })

```

# Page snapshot

```yaml
- generic [ref=e2]:
  - generic [ref=e3]:
    - complementary [ref=e4]:
      - generic [ref=e5]:
        - generic [ref=e6]:
          - button "Collapse sidebar" [ref=e7] [cursor=pointer]
          - generic [ref=e8]: Atelier
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
              - text: Workflows
              - img "A workflow is waiting for you" [ref=e20]
            - link "Images" [ref=e22] [cursor=pointer]:
              - /url: /images
          - region "Folders" [ref=e28]:
            - generic [ref=e29]:
              - heading "Folders" [level=2] [ref=e30]
              - button "New folder" [ref=e31] [cursor=pointer]
            - paragraph [ref=e32]: No folders yet
          - generic [ref=e33]:
            - paragraph [ref=e34]: Today
            - generic [ref=e35]:
              - link "Synthetic composer circle" [ref=e36] [cursor=pointer]:
                - /url: /c/7d1f297df2e141b782af0b4be1ca43f8
              - button "Actions for Synthetic composer circle" [ref=e37] [cursor=pointer]
          - generic [ref=e39]:
            - 'link "Synthetic cancel circle #slow" [ref=e40] [cursor=pointer]':
              - /url: /c/6b6c2fcf6b554d2cb5d49eb902f60c5e
            - 'button "Actions for Synthetic cancel circle #slow" [ref=e41] [cursor=pointer]'
          - generic [ref=e43]:
            - 'link "Synthetic paused lanterns #pause-step" [ref=e44] [cursor=pointer]':
              - /url: /c/8e2bc0e0c72045ad9a21d8b0ca36c7ad
            - 'button "Actions for Synthetic paused lanterns #pause-step" [ref=e45] [cursor=pointer]'
          - generic [ref=e47]:
            - 'link "Synthetic saved cobalt circle #slow" [ref=e48] [cursor=pointer]':
              - /url: /c/78f912f1e52d4ecb9832fff3e435fe68
            - 'button "Actions for Synthetic saved cobalt circle #slow" [ref=e49] [cursor=pointer]'
        - button "Settings" [ref=e52] [cursor=pointer]
    - main [ref=e53]:
      - generic [ref=e54]:
        - button "Choose model" [ref=e56] [cursor=pointer]:
          - generic [aria-hidden] [ref=e57]: ●
          - generic [ref=e58]: fake-chat
          - generic [ref=e59]: Fake runtime
        - generic "Double-click to rename" [ref=e60]: New chat
        - button "Chat controls" [ref=e61] [cursor=pointer]
        - button "Actions for New chat" [ref=e62] [cursor=pointer]
      - status [ref=e63]
      - log "Conversation" [ref=e64]
      - generic [ref=e66]:
        - button [aria-hidden] [ref=e67] [cursor=pointer]
        - form "Message" [ref=e68]:
          - textbox "Image prompt" [active] [ref=e69]:
            - /placeholder: Describe an image…
          - generic [ref=e70]:
            - button "Leave image mode" [pressed] [ref=e71] [cursor=pointer]:
              - generic [ref=e72]: Image
            - button "Image count" [ref=e73] [cursor=pointer]: 1 image
            - button "Image options" [ref=e74] [cursor=pointer]
            - generic [ref=e75]:
              - generic [ref=e76]: FLUX.2 klein 4B · 1024²
              - generic [ref=e77]:
                - button "Create image" [disabled]
  - region "Notifications alt+T"
```

# Test source

```ts
  114 |   await page.goBack();
  115 |   await page.goBack();
  116 |   await expect(message).toHaveValue("Synthetic unsent chat draft");
  117 | });
  118 | 
  119 | test("Workflow count uses automatic seeds and repeats uncertain acceptance exactly", async ({
  120 |   page,
  121 | }) => {
  122 |   await page.goto("/workflows/new?template=brief_images");
  123 |   await configureStudioBlock(page, "Draft image prompt");
  124 |   await chooseStudioModel(page);
  125 |   await configureStudioBlock(page, "Create images");
  126 |   await expect(
  127 |     page.getByRole("spinbutton", { name: "Seed 1", exact: true }),
  128 |   ).not.toBeVisible();
  129 |   await page.getByRole("button", { name: "3", exact: true }).click();
  130 |   await openStudioRun(page);
  131 |   await page
  132 |     .getByRole("textbox", { name: "Image brief", exact: true })
  133 |     .fill("Synthetic automatic variants");
  134 |   const bodies: { request_key: string; inputs: Record<string, unknown> }[] = [];
  135 |   const accepted: {
  136 |     id: string;
  137 |     graph: {
  138 |       nodes: {
  139 |         kind: string;
  140 |         config: {
  141 |           count?: number;
  142 |           seeds?: number[];
  143 |           params?: Record<string, unknown>;
  144 |         };
  145 |       }[];
  146 |     };
  147 |   }[] = [];
  148 |   await page.route("**/api/workflows/defs/*/runs", async (route) => {
  149 |     bodies.push(route.request().postDataJSON());
  150 |     if (bodies.length === 1) {
  151 |       const response = await route.fetch();
  152 |       accepted.push(await response.json());
  153 |       await route.abort("failed");
  154 |     } else {
  155 |       const response = await route.fetch();
  156 |       accepted.push(await response.json());
  157 |       await route.fulfill({ response });
  158 |     }
  159 |   });
  160 |   await page.getByRole("button", { name: "Run workflow", exact: true }).click();
  161 |   await expect(
  162 |     page
  163 |       .getByRole("alert")
  164 |       .filter({ hasText: /Failed to fetch|Load failed|NetworkError/ }),
  165 |   ).toBeVisible();
  166 |   await page.getByRole("button", { name: "Run workflow", exact: true }).click();
  167 |   await expect.poll(() => bodies.length).toBe(2);
  168 |   expect(bodies[1]).toEqual(bodies[0]);
  169 |   await expect.poll(() => accepted.length).toBe(2);
  170 |   expect(accepted[1].id).toBe(accepted[0].id);
  171 |   const images = accepted[0].graph.nodes.find(
  172 |     (n) => n.kind === "generate_image",
  173 |   )!;
  174 |   expect(images.config.seeds).toHaveLength(3);
  175 |   expect(
  176 |     accepted[1].graph.nodes.find((n) => n.kind === "generate_image")!.config
  177 |       .seeds,
  178 |   ).toEqual(images.config.seeds);
  179 |   for (const seed of images.config.seeds!) {
  180 |     expect(Number.isInteger(seed)).toBe(true);
  181 |     expect(seed).toBeGreaterThanOrEqual(0);
  182 |     expect(seed).toBeLessThanOrEqual(4294967295);
  183 |   }
  184 |   const params = accepted[0].graph.nodes.find((n) => n.kind === "generate")!
  185 |     .config.params!;
  186 |   expect(Object.values(params).every((v) => v == null)).toBe(true);
  187 |   await expect(
  188 |     page
  189 |       .getByRole("article", { name: "Brief to images run" })
  190 |       .first()
  191 |       .getByRole("textbox", { name: "Review result" }),
  192 |   ).toBeVisible();
  193 | });
  194 | 
  195 | test("Image cancellation stays in composer and Workflows returns to the same saved chat", async ({
  196 |   page,
  197 |   request,
  198 |   browserName,
  199 | }) => {
  200 |   const connection = (await (await request.get("/api/connections")).json())[0];
  201 |   const response = await request.post("/api/chats", {
  202 |     data: { connection_id: connection.id, model_id: "fake-chat" },
  203 |   });
  204 |   const chat = await response.json();
  205 |   await page.goto(`/c/${chat.id}`);
  206 |   const message = page.getByRole("textbox", {
  207 |     name: "Message fake-chat",
  208 |     exact: true,
  209 |   });
  210 |   await message.fill("Synthetic saved-chat draft");
  211 |   await page.getByRole("button", { name: "Create image", exact: true }).click();
  212 |   await page
  213 |     .getByRole("textbox", { name: "Prompt", exact: true })
> 214 |     .fill("Synthetic cancellable composer #slow");
      |      ^ Error: locator.fill: Test timeout of 45000ms exceeded.
  215 |   await page.getByRole("button", { name: "Generate one image" }).click();
  216 |   const job = page
  217 |     .getByRole("article")
  218 |     .filter({ hasText: "Synthetic cancellable composer #slow" })
  219 |     .first();
  220 |   await job.getByRole("button", { name: "Cancel", exact: true }).click();
  221 |   await expect(
  222 |     job.getByText("cancelled", { exact: true }).first(),
  223 |   ).toBeVisible();
  224 |   await settle(page);
  225 |   const dir = "../artifacts/composer-workflows/browser/composer";
  226 |   await mkdir(dir, { recursive: true });
  227 |   await page.screenshot({
  228 |     path: `${dir}/cancel-${browserName}-fake.png`,
  229 |     fullPage: true,
  230 |   });
  231 |   await page.getByRole("button", { name: "Message", exact: true }).click();
  232 |   await workspaceLink(page, "Workflows");
  233 |   await page.goBack();
  234 |   await expect(page).toHaveURL(new RegExp(`/c/${chat.id}$`));
  235 |   await expect(message).toHaveValue("Synthetic saved-chat draft");
  236 | });
  237 | 
  238 | test("Visual builder reflows and every node opens its settings with keyboard", async ({
  239 |   page,
  240 |   browserName,
  241 | }) => {
  242 |   const dir = "../artifacts/composer-workflows/browser/builder";
  243 |   await mkdir(dir, { recursive: true });
  244 |   for (const width of [320, 390, 1440]) {
  245 |     await page.setViewportSize({ width, height: 900 });
  246 |     await page.goto("/design?studio");
  247 |     for (const theme of ["light", "dark"]) {
  248 |       await page.getByRole("button", { name: theme, exact: true }).click();
  249 |       await configureStudioBlock(page, "Draft image prompt");
  250 |       await expect(
  251 |         page.getByRole("combobox", { name: "Model", exact: true }),
  252 |       ).toBeVisible();
  253 |       if (width < 768)
  254 |         await expect(
  255 |           page.locator(".wf-outline-row[data-selected=true]"),
  256 |         ).toContainText("Draft image prompt");
  257 |       else
  258 |         await expect(
  259 |           page.locator(".wf-block[data-selected=true]"),
  260 |         ).toContainText("Draft image prompt");
  261 |       await settle(page);
  262 |       expect(
  263 |         await page.evaluate(
  264 |           () => document.documentElement.scrollWidth <= innerWidth,
  265 |         ),
  266 |       ).toBe(true);
  267 |       const scan = await new AxeBuilder({ page }).analyze();
  268 |       expect(
  269 |         scan.violations.filter((v) =>
  270 |           ["critical", "serious"].includes(v.impact ?? ""),
  271 |         ),
  272 |       ).toEqual([]);
  273 |       await page.screenshot({
  274 |         path: `${dir}/model-${width}-${theme}-${browserName}-fake.png`,
  275 |         fullPage: true,
  276 |       });
  277 |       await configureStudioBlock(page, "Create images");
  278 |       await expect(
  279 |         page.getByRole("group", { name: "Images", exact: true }),
  280 |       ).toBeVisible();
  281 |       await configureStudioBlock(page, "Check the prompt");
  282 |       await expect(
  283 |         page.getByRole("switch", { name: "Allow editing", exact: true }),
  284 |       ).toBeVisible();
  285 |       await configureStudioBlock(page, "Start");
  286 |       await expect(
  287 |         page.getByRole("textbox", { name: "Input label", exact: true }),
  288 |       ).toHaveValue("Image brief");
  289 |       await page
  290 |         .getByRole("button", { name: "Close Inspector", exact: true })
  291 |         .click();
  292 |       await settle(page);
  293 |     }
  294 |   }
  295 | });
  296 | 
```