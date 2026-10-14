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
- complementary:
  - button "Collapse sidebar"
  - text: Atelier
  - link "New chat":
    - /url: /
  - navigation "Chat history":
    - textbox "Search history":
      - /placeholder: Search chats…
    - text: ⌘K
    - navigation "Workspace":
      - link "Workflows":
        - /url: /workflows
      - link "Images":
        - /url: /images
    - region "Folders":
      - heading "Folders" [level=2]
      - button "New folder"
      - paragraph: No folders yet
    - paragraph: Today
    - link "Synthetic composer circle":
      - /url: /c/cc990ae1a3d948bb85da44ee8fcad27d
    - button "Actions for Synthetic composer circle"
    - 'link "Synthetic paused lanterns #pause-step"':
      - /url: /c/411522d2188e40b1bbdeee2610c0fa81
    - 'button "Actions for Synthetic paused lanterns #pause-step"'
    - 'link "Synthetic saved cobalt circle #slow"':
      - /url: /c/eaf9e6ce8abb4ba6a6a08f9ce75064ca
    - 'button "Actions for Synthetic saved cobalt circle #slow"'
  - button "Settings"
- main:
  - button "Choose model": fake-chat Fake runtime
  - text: Synthetic composer circle
  - button "Chat controls"
  - button "Actions for Synthetic composer circle"
  - status
  - log "Conversation":
    - article "user message":
      - heading "You said" [level=2]
      - paragraph: Image
      - paragraph: Synthetic composer circle
    - article "assistant message":
      - heading "Assistant replied" [level=2]
      - paragraph: FLUX.2 klein 4B
      - group "Images in this turn":
        - img "Synthetic composer circle"
        - button "Save image"
        - button "Copy image prompt":
          - status
        - button "Image details"
        - button "More image actions"
      - status: 1 image · 0 s
      - button "Try again"
      - button "Copy prompt":
        - status
        - text: Copy prompt
  - form "Message":
    - textbox "Image prompt":
      - /placeholder: Describe an image…
    - button "Leave image mode" [pressed]: Image
    - button "Image count": 1 image
    - button "Image options"
    - text: FLUX.2 klein 4B · 1024²
    - button "Create image" [disabled]
- region "Notifications alt+T"
```

# Test source

```ts
  13  |   await page.getByRole("button", { name: "Choose model", exact: true }).click();
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
  45  |   await page.route("**/api/chats/*/images", async (route) => {
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
  66  |     .getByRole("textbox", { name: "Image prompt", exact: true })
  67  |     .fill("Synthetic composer circle");
  68  |   await page.getByRole("button", { name: "Create image", exact: true }).click();
  69  |   await expect(
  70  |     page
  71  |       .getByRole("alert")
  72  |       .filter({ hasText: /Failed to fetch|Load failed|NetworkError/ }),
  73  |   ).toBeVisible();
  74  |   await page.getByRole("button", { name: "Create image", exact: true }).click();
  75  |   await expect.poll(() => bodies.length).toBe(2);
  76  |   expect(bodies[1]).toEqual(bodies[0]);
  77  |   expect(Number.isInteger((bodies[0].seeds as number[])[0])).toBe(true);
  78  |   expect((bodies[0].seeds as number[])[0]).toBeGreaterThanOrEqual(0);
  79  |   expect((bodies[0].seeds as number[])[0]).toBeLessThanOrEqual(4294967295);
  80  |   const job = page.locator('[data-slot="image-turn"]').last();
  81  |   await expect(
  82  |     job.getByRole("button", { name: "Save image", exact: true }),
  83  |   ).toBeVisible();
  84  |   const scan = await new AxeBuilder({ page }).analyze();
  85  |   expect(
  86  |     scan.violations.filter((v) =>
  87  |       ["critical", "serious"].includes(v.impact ?? ""),
  88  |     ),
  89  |   ).toEqual([]);
  90  |   await job.getByRole("button", { name: "Save image", exact: true }).click();
  91  |   await expect(
  92  |     page.getByRole("dialog", { name: "Save image", exact: true }),
  93  |   ).toBeVisible();
  94  |   await page
  95  |     .getByRole("button", { name: "Close image save", exact: true })
  96  |     .click();
  97  |   await page
  98  |     .getByRole("button", { name: "Leave image mode", exact: true })
  99  |     .click();
  100 |   await expect(message).toHaveValue("Synthetic unsent chat draft");
  101 |   await expect(message).toBeFocused();
  102 |   expect(chatCalls).toBe(1); // Approved: the image is now a saved chat turn.
  103 |   await workspaceLink(page, "Workflows");
  104 |   await page
  105 |     .getByRole("button", { name: "Use Brief to images template", exact: true })
  106 |     .click();
  107 |   await configureStudioBlock(page, "Draft image prompt");
  108 |   await expect(
  109 |     page.getByRole("combobox", { name: "Model", exact: true }),
  110 |   ).toContainText("fake-chat");
  111 |   await page.goBack();
  112 |   await page.goBack();
> 113 |   await expect(message).toHaveValue("Synthetic unsent chat draft");
      |                         ^ Error: expect(locator).toHaveValue(expected) failed
  114 | });
  115 | 
  116 | test("Workflow count uses automatic seeds and repeats uncertain acceptance exactly", async ({
  117 |   page,
  118 | }) => {
  119 |   await page.goto("/workflows/new?template=brief_images");
  120 |   await configureStudioBlock(page, "Draft image prompt");
  121 |   await chooseStudioModel(page);
  122 |   await configureStudioBlock(page, "Create images");
  123 |   await expect(
  124 |     page.getByRole("spinbutton", { name: "Seed 1", exact: true }),
  125 |   ).not.toBeVisible();
  126 |   await page.getByRole("button", { name: "3", exact: true }).click();
  127 |   await openStudioRun(page);
  128 |   await page
  129 |     .getByRole("textbox", { name: "Image brief", exact: true })
  130 |     .fill("Synthetic automatic variants");
  131 |   const bodies: { request_key: string; inputs: Record<string, unknown> }[] = [];
  132 |   const accepted: {
  133 |     id: string;
  134 |     graph: {
  135 |       nodes: {
  136 |         kind: string;
  137 |         config: {
  138 |           count?: number;
  139 |           seeds?: number[];
  140 |           params?: Record<string, unknown>;
  141 |         };
  142 |       }[];
  143 |     };
  144 |   }[] = [];
  145 |   await page.route("**/api/workflows/defs/*/runs", async (route) => {
  146 |     bodies.push(route.request().postDataJSON());
  147 |     if (bodies.length === 1) {
  148 |       const response = await route.fetch();
  149 |       accepted.push(await response.json());
  150 |       await route.abort("failed");
  151 |     } else {
  152 |       const response = await route.fetch();
  153 |       accepted.push(await response.json());
  154 |       await route.fulfill({ response });
  155 |     }
  156 |   });
  157 |   await page.getByRole("button", { name: "Run workflow", exact: true }).click();
  158 |   await expect(
  159 |     page
  160 |       .getByRole("alert")
  161 |       .filter({ hasText: /Failed to fetch|Load failed|NetworkError/ }),
  162 |   ).toBeVisible();
  163 |   await page.getByRole("button", { name: "Run workflow", exact: true }).click();
  164 |   await expect.poll(() => bodies.length).toBe(2);
  165 |   expect(bodies[1]).toEqual(bodies[0]);
  166 |   await expect.poll(() => accepted.length).toBe(2);
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
  210 |     .getByRole("textbox", { name: "Image prompt", exact: true })
  211 |     .fill("Synthetic cancellable composer #slow");
  212 |   await page.getByRole("button", { name: "Create image", exact: true }).click();
  213 |   const job = page.locator('[data-slot="image-turn"]').last();
```