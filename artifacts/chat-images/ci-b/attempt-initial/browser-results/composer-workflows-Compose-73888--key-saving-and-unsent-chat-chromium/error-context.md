# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: composer-workflows.spec.ts >> Composer image acceptance retry preserves seed/key, saving and unsent chat
- Location: tests/composer-workflows.spec.ts:25:1

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: getByRole('article').filter({ hasText: 'Synthetic composer circle' }).first().getByRole('button', { name: 'Save image', exact: true })
Expected: visible
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" getByRole('article').filter({ hasText: 'Synthetic composer circle' }).first().getByRole('button', { name: 'Save image', exact: true }) with timeout 5000ms
  - waiting for getByRole('article').filter({ hasText: 'Synthetic composer circle' }).first().getByRole('button', { name: 'Save image', exact: true })

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
      - /url: /c/7d1f297df2e141b782af0b4be1ca43f8
    - button "Actions for Synthetic composer circle"
    - 'link "Synthetic cancel circle #slow"':
      - /url: /c/6b6c2fcf6b554d2cb5d49eb902f60c5e
    - 'button "Actions for Synthetic cancel circle #slow"'
    - 'link "Synthetic paused lanterns #pause-step"':
      - /url: /c/8e2bc0e0c72045ad9a21d8b0ca36c7ad
    - 'button "Actions for Synthetic paused lanterns #pause-step"'
    - 'link "Synthetic saved cobalt circle #slow"':
      - /url: /c/78f912f1e52d4ecb9832fff3e435fe68
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
      - status: Waiting for your Mac · after 3 images
      - button "Cancel"
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
  1   | import { test, expect, type Page } from "@playwright/test";
  2   | import { mkdir } from "node:fs/promises";
  3   | import AxeBuilder from "@axe-core/playwright";
  4   | import {
  5   |   configureStudioBlock,
  6   |   chooseStudioModel,
  7   |   openStudioRun,
  8   | } from "./studio-helpers";
  9   | import { settle } from "./helpers";
  10  | import { workspaceLink } from "./workspace-helpers";
  11  | 
  12  | async function chatModel(page: Page) {
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
  80  |   const job = page
  81  |     .getByRole("article")
  82  |     .filter({ hasText: "Synthetic composer circle" })
  83  |     .first();
  84  |   await expect(
  85  |     job.getByRole("button", { name: "Save image", exact: true }),
> 86  |   ).toBeVisible();
      |     ^ Error: expect(locator).toBeVisible() failed
  87  |   const scan = await new AxeBuilder({ page }).analyze();
  88  |   expect(
  89  |     scan.violations.filter((v) =>
  90  |       ["critical", "serious"].includes(v.impact ?? ""),
  91  |     ),
  92  |   ).toEqual([]);
  93  |   await job.getByRole("button", { name: "Save image", exact: true }).click();
  94  |   await expect(
  95  |     page.getByRole("dialog", { name: "Save image", exact: true }),
  96  |   ).toBeVisible();
  97  |   await page
  98  |     .getByRole("button", { name: "Close image save", exact: true })
  99  |     .click();
  100 |   await page
  101 |     .getByRole("button", { name: "Leave image mode", exact: true })
  102 |     .click();
  103 |   await expect(message).toHaveValue("Synthetic unsent chat draft");
  104 |   await expect(message).toBeFocused();
  105 |   expect(chatCalls).toBe(1); // Approved: the image is now a saved chat turn.
  106 |   await workspaceLink(page, "Workflows");
  107 |   await page
  108 |     .getByRole("button", { name: "Use Brief to images template", exact: true })
  109 |     .click();
  110 |   await configureStudioBlock(page, "Draft image prompt");
  111 |   await expect(
  112 |     page.getByRole("combobox", { name: "Model", exact: true }),
  113 |   ).toContainText("fake-chat");
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
```