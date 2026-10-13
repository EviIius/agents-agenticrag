# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: composer-workflows.spec.ts >> Composer image acceptance retry preserves seed/key, saving and unsent chat
- Location: tests/composer-workflows.spec.ts:25:1

# Error details

```
Error: expect(locator).toHaveValue(expected) failed

Locator: getByRole('textbox', { name: 'Message fake-chat', exact: true })
Expected: "Synthetic unsent chat draft"
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toHaveValue" getByRole('textbox', { name: 'Message fake-chat', exact: true }) with timeout 5000ms
  - waiting for getByRole('textbox', { name: 'Message fake-chat', exact: true })

```

```yaml
- region "Notifications alt+T"
- dialog "Leave with unsaved changes?":
  - heading "Leave with unsaved changes?" [level=2]
  - paragraph: Your current changes haven't been saved. Stay here to retry saving.
  - button "Stay here"
  - button "Leave without saving"
  - button "Close"
```

# Test source

```ts
  14  |   await page.getByPlaceholder("Search models…").fill("fake-chat");
  15  |   await page
  16  |     .getByRole("option")
  17  |     .filter({ hasText: "fake-chat" })
  18  |     .first()
  19  |     .click();
  20  |   await expect(
  21  |     page.getByRole("textbox", { name: "Message fake-chat", exact: true }),
  22  |   ).toBeEnabled();
  23  | }
  24  | 
  25  | test("Composer image acceptance retry preserves seed/key, saving and unsent chat", async ({
  26  |   page,
  27  | }) => {
  28  |   await page.goto("/");
  29  |   await chatModel(page);
  30  |   const message = page.getByRole("textbox", {
  31  |     name: "Message fake-chat",
  32  |     exact: true,
  33  |   });
  34  |   await message.fill("Synthetic unsent chat draft");
  35  |   const bodies: Record<string, unknown>[] = [];
  36  |   let chatCalls = 0;
  37  |   page.on("request", (request) => {
  38  |     if (
  39  |       request.method() === "POST" &&
  40  |       (new URL(request.url()).pathname.endsWith("/api/chats") ||
  41  |         /\/api\/chats\/[^/]+\/messages$/.test(new URL(request.url()).pathname))
  42  |     )
  43  |       chatCalls++;
  44  |   });
  45  |   await page.route("**/api/images/jobs", async (route) => {
  46  |     if (route.request().method() !== "POST") return route.continue();
  47  |     bodies.push(route.request().postDataJSON());
  48  |     if (bodies.length === 1) {
  49  |       await route.fetch();
  50  |       await route.abort("failed");
  51  |     } else await route.continue();
  52  |   });
  53  |   const createImage = page.getByRole("button", {
  54  |     name: "Create image",
  55  |     exact: true,
  56  |   });
  57  |   const target = await createImage.boundingBox();
  58  |   expect(target?.width).toBeGreaterThanOrEqual(44);
  59  |   expect(target?.height).toBeGreaterThanOrEqual(44);
  60  |   await createImage.click();
  61  |   await expect(message).not.toBeVisible();
  62  |   await expect(
  63  |     page.getByRole("textbox", { name: "Seed", exact: true }),
  64  |   ).not.toBeVisible();
  65  |   await page
  66  |     .getByRole("textbox", { name: "Prompt", exact: true })
  67  |     .fill("Synthetic composer circle");
  68  |   await page.getByRole("button", { name: "Generate one image" }).click();
  69  |   await expect(
  70  |     page
  71  |       .getByRole("status")
  72  |       .filter({ hasText: /Failed to fetch|Load failed|NetworkError/ }),
  73  |   ).toBeVisible();
  74  |   await page.getByRole("button", { name: "Generate one image" }).click();
  75  |   await expect.poll(() => bodies.length).toBe(2);
  76  |   expect(bodies[1]).toEqual(bodies[0]);
  77  |   expect(Number.isInteger(bodies[0].seed)).toBe(true);
  78  |   expect(bodies[0].seed as number).toBeGreaterThanOrEqual(0);
  79  |   expect(bodies[0].seed as number).toBeLessThanOrEqual(4294967295);
  80  |   const job = page
  81  |     .getByRole("article")
  82  |     .filter({ hasText: "Synthetic composer circle" })
  83  |     .first();
  84  |   await expect(
  85  |     job.getByRole("button", { name: "Save", exact: true }),
  86  |   ).toBeVisible();
  87  |   const scan = await new AxeBuilder({ page }).analyze();
  88  |   expect(
  89  |     scan.violations.filter((v) =>
  90  |       ["critical", "serious"].includes(v.impact ?? ""),
  91  |     ),
  92  |   ).toEqual([]);
  93  |   await job.getByRole("button", { name: "Save", exact: true }).click();
  94  |   await expect(
  95  |     page.getByRole("dialog", { name: "Save image", exact: true }),
  96  |   ).toBeVisible();
  97  |   await page
  98  |     .getByRole("button", { name: "Close image save", exact: true })
  99  |     .click();
  100 |   await page.getByRole("button", { name: "Message", exact: true }).click();
  101 |   await expect(message).toHaveValue("Synthetic unsent chat draft");
  102 |   await expect(message).toBeFocused();
  103 |   expect(chatCalls).toBe(0);
  104 |   await workspaceLink(page, "Workflows");
  105 |   await page
  106 |     .getByRole("button", { name: "Use Brief to images template", exact: true })
  107 |     .click();
  108 |   await configureStudioBlock(page, "Draft image prompt");
  109 |   await expect(
  110 |     page.getByRole("combobox", { name: "Model", exact: true }),
  111 |   ).toContainText("fake-chat");
  112 |   await page.goBack();
  113 |   await page.goBack();
> 114 |   await expect(message).toHaveValue("Synthetic unsent chat draft");
      |                         ^ Error: expect(locator).toHaveValue(expected) failed
  115 | });
  116 | 
  117 | test("Workflow count uses automatic seeds and repeats uncertain acceptance exactly", async ({
  118 |   page,
  119 | }) => {
  120 |   await page.goto("/workflows/new?template=brief_images");
  121 |   await configureStudioBlock(page, "Draft image prompt");
  122 |   await chooseStudioModel(page);
  123 |   await configureStudioBlock(page, "Create images");
  124 |   await expect(
  125 |     page.getByRole("spinbutton", { name: "Seed 1", exact: true }),
  126 |   ).not.toBeVisible();
  127 |   await page.getByRole("button", { name: "3", exact: true }).click();
  128 |   await openStudioRun(page);
  129 |   await page
  130 |     .getByRole("textbox", { name: "Image brief", exact: true })
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
  167 |   await expect.poll(() => accepted.length).toBe(2);
  168 |   expect(accepted[1].id).toBe(accepted[0].id);
  169 |   const images = accepted[0].graph.nodes.find(
  170 |     (n) => n.kind === "generate_image",
  171 |   )!;
  172 |   expect(images.config.seeds).toHaveLength(3);
  173 |   expect(
  174 |     accepted[1].graph.nodes.find((n) => n.kind === "generate_image")!.config
  175 |       .seeds,
  176 |   ).toEqual(images.config.seeds);
  177 |   for (const seed of images.config.seeds!) {
  178 |     expect(Number.isInteger(seed)).toBe(true);
  179 |     expect(seed).toBeGreaterThanOrEqual(0);
  180 |     expect(seed).toBeLessThanOrEqual(4294967295);
  181 |   }
  182 |   const params = accepted[0].graph.nodes.find((n) => n.kind === "generate")!
  183 |     .config.params!;
  184 |   expect(Object.values(params).every((v) => v == null)).toBe(true);
  185 |   await expect(
  186 |     page
  187 |       .getByRole("article", { name: "Brief to images run" })
  188 |       .first()
  189 |       .getByRole("textbox", { name: "Review result" }),
  190 |   ).toBeVisible();
  191 | });
  192 | 
  193 | test("Image cancellation stays in composer and Workflows returns to the same saved chat", async ({
  194 |   page,
  195 |   request,
  196 |   browserName,
  197 | }) => {
  198 |   const connection = (await (await request.get("/api/connections")).json())[0];
  199 |   const response = await request.post("/api/chats", {
  200 |     data: { connection_id: connection.id, model_id: "fake-chat" },
  201 |   });
  202 |   const chat = await response.json();
  203 |   await page.goto(`/c/${chat.id}`);
  204 |   const message = page.getByRole("textbox", {
  205 |     name: "Message fake-chat",
  206 |     exact: true,
  207 |   });
  208 |   await message.fill("Synthetic saved-chat draft");
  209 |   await page.getByRole("button", { name: "Create image", exact: true }).click();
  210 |   await page
  211 |     .getByRole("textbox", { name: "Prompt", exact: true })
  212 |     .fill("Synthetic cancellable composer #slow");
  213 |   await page.getByRole("button", { name: "Generate one image" }).click();
  214 |   const job = page
```