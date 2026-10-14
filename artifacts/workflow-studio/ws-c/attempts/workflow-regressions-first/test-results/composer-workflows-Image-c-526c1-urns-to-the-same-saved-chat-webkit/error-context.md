# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: composer-workflows.spec.ts >> Image cancellation stays in composer and Workflows returns to the same saved chat
- Location: tests/composer-workflows.spec.ts:192:1

# Error details

```
Error: expect(page).toHaveURL(expected) failed

Expected pattern: /\/c\/86172d9c745c4c36a066796d0699fbfc$/
Received string:  "about:blank"
Timeout: 5000ms

Call log:
  - Expect "toHaveURL" with timeout 5000ms
    - waiting for navigation to finish...
    - navigated to "about:blank"
    14 × locator resolved to <html>…</html>
       - unexpected value "about:blank"

```

# Test source

```ts
  131 |     .fill("Synthetic automatic variants");
  132 |   const bodies: { request_key: string; inputs: Record<string, unknown> }[] = [];
  133 |   const accepted: {
  134 |     id: string;
  135 |     graph: {
  136 |       nodes: {
  137 |         kind: string;
  138 |         config: {
  139 |           count?: number;
  140 |           seeds?: number[];
  141 |           params?: Record<string, unknown>;
  142 |         };
  143 |       }[];
  144 |     };
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
> 231 |   await expect(page).toHaveURL(new RegExp(`/c/${chat.id}$`));
      |                      ^ Error: expect(page).toHaveURL(expected) failed
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
  245 |       await page.getByRole("button", { name: theme, exact: true }).click();
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