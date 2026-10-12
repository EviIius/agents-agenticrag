# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: composer-workflows.spec.ts >> Composer image acceptance retry preserves seed/key, saving and unsent chat
- Location: tests/composer-workflows.spec.ts:20:1

# Error details

```
Error: locator.click: Error: strict mode violation: getByRole('link', { name: /Brief to images/ }) resolved to 4 elements:
    1) <a data-discover="true" href="/workflows/new?template=brief_images" class="group flex flex-col gap-4 rounded-xl border border-line bg-surface p-5 hover:border-line-strong hover:bg-surface-2">…</a> aka getByRole('link', { name: 'Brief to images Turn a brief' })
    2) <a data-discover="true" href="/workflows/runs/a6bceab1bdfd47caa1c7edef754e5fa7" class="flex min-h-16 items-center gap-3 border-b border-line px-4 py-3 last:border-b-0 hover:bg-surface-2">…</a> aka getByRole('link', { name: 'Brief to images Complete ·' })
    3) <a data-discover="true" href="/workflows/runs/dac67fe001f04b09b5456d0cf1925c1b" class="flex min-h-16 items-center gap-3 border-b border-line px-4 py-3 last:border-b-0 hover:bg-surface-2">…</a> aka getByText('Brief to imagesWaiting for you · Review the image promptOct 12 at 5:09 PM')
    4) <a data-discover="true" href="/workflows/runs/b0f93009f82641e88559ccb4d0a53afc" class="flex min-h-16 items-center gap-3 border-b border-line px-4 py-3 last:border-b-0 hover:bg-surface-2">…</a> aka getByText('Brief to imagesWaiting for you · Review the image promptOct 12 at 5:08 PM')

Call log:
  - waiting for getByRole('link', { name: /Brief to images/ })

```

# Page snapshot

```yaml
- generic [ref=e2]:
  - main [ref=e4]:
    - generic [ref=e5]:
      - button "Open sidebar" [ref=e6] [cursor=pointer]
      - link "Workflows" [ref=e7]:
        - /url: /workflows
    - region "Workflows" [ref=e8]:
      - generic [ref=e9]:
        - status [ref=e10]: Connected
        - generic [ref=e11]:
          - generic [ref=e12]:
            - heading "Workflows" [level=1] [ref=e13]
            - paragraph [ref=e14]: Turn images and recordings into repeatable steps. Accepted runs keep going on your Mac when you close the app.
          - region "Workflow templates" [ref=e15]:
            - heading "START FROM A TEMPLATE" [level=2] [ref=e16]
            - generic [ref=e17]:
              - link [ref=e18]:
                - /url: /workflows/new?template=brief_images
                - heading "Brief to images" [level=3] [ref=e25]
                - paragraph [ref=e26]: Turn a brief into an image prompt, review it, then create one to three images.
                - generic "Template steps" [ref=e27]: Use template
              - link [ref=e56]:
                - /url: /workflows/new?template=meeting_pack
                - heading "Recording to meeting pack" [level=3] [ref=e60]
                - paragraph [ref=e61]: Save the original transcript and draft a summary, decisions and action items for your review.
                - generic "Template steps" [ref=e62]: Use template
          - region "Recent workflow runs" [ref=e83]:
            - generic [ref=e84]:
              - heading "RECENT RUNS" [level=2] [ref=e85]
              - link "View all runs" [ref=e86]:
                - /url: /workflows/runs
            - generic [ref=e87]:
              - link [ref=e88]:
                - /url: /workflows/runs/c0023a4053b14b019f7e639c00cf9967
                - generic [ref=e91]:
                  - paragraph [ref=e92]: Recording to meeting pack
                  - paragraph [ref=e93]: Complete · Ready for review
              - link [ref=e96]:
                - /url: /workflows/runs/a6bceab1bdfd47caa1c7edef754e5fa7
                - generic [ref=e99]:
                  - paragraph [ref=e100]: Brief to images
                  - paragraph [ref=e101]: Complete · Ready for review
              - link [ref=e104]:
                - /url: /workflows/runs/dac67fe001f04b09b5456d0cf1925c1b
                - generic [ref=e108]:
                  - paragraph [ref=e109]: Brief to images
                  - paragraph [ref=e110]: Waiting for you · Review the image prompt
              - link [ref=e113]:
                - /url: /workflows/runs/b0f93009f82641e88559ccb4d0a53afc
                - generic [ref=e117]:
                  - paragraph [ref=e118]: Brief to images
                  - paragraph [ref=e119]: Waiting for you · Review the image prompt
          - paragraph [ref=e122]: Text outputs are drafts for your review. Original sources and saved results stay available in each run.
  - region "Notifications alt+T"
```

# Test source

```ts
  1   | import { test, expect, type Page } from "@playwright/test";
  2   | import { mkdir } from "node:fs/promises";
  3   | import AxeBuilder from "@axe-core/playwright";
  4   | import { settle } from "./helpers";
  5   | import { workspaceLink } from "./workspace-helpers";
  6   | 
  7   | async function chatModel(page: Page) {
  8   |   await page.getByRole("button", { name: "Choose model", exact: true }).click();
  9   |   await page.getByPlaceholder("Search models…").fill("fake-chat");
  10  |   await page
  11  |     .getByRole("option")
  12  |     .filter({ hasText: "fake-chat" })
  13  |     .first()
  14  |     .click();
  15  |   await expect(
  16  |     page.getByRole("textbox", { name: "Message fake-chat", exact: true }),
  17  |   ).toBeEnabled();
  18  | }
  19  | 
  20  | test("Composer image acceptance retry preserves seed/key, saving and unsent chat", async ({
  21  |   page,
  22  | }) => {
  23  |   await page.goto("/");
  24  |   await chatModel(page);
  25  |   const message = page.getByRole("textbox", {
  26  |     name: "Message fake-chat",
  27  |     exact: true,
  28  |   });
  29  |   await message.fill("Synthetic unsent chat draft");
  30  |   const bodies: Record<string, unknown>[] = [];
  31  |   let chatCalls = 0;
  32  |   page.on("request", (request) => {
  33  |     if (
  34  |       request.method() === "POST" &&
  35  |       (new URL(request.url()).pathname.endsWith("/api/chats") ||
  36  |         /\/api\/chats\/[^/]+\/messages$/.test(new URL(request.url()).pathname))
  37  |     )
  38  |       chatCalls++;
  39  |   });
  40  |   await page.route("**/api/images/jobs", async (route) => {
  41  |     if (route.request().method() !== "POST") return route.continue();
  42  |     bodies.push(route.request().postDataJSON());
  43  |     if (bodies.length === 1) {
  44  |       await route.fetch();
  45  |       await route.abort("failed");
  46  |     } else await route.continue();
  47  |   });
  48  |   const createImage = page.getByRole("button", {
  49  |     name: "Create image",
  50  |     exact: true,
  51  |   });
  52  |   const target = await createImage.boundingBox();
  53  |   expect(target?.width).toBeGreaterThanOrEqual(44);
  54  |   expect(target?.height).toBeGreaterThanOrEqual(44);
  55  |   await createImage.click();
  56  |   await expect(message).not.toBeVisible();
  57  |   await expect(
  58  |     page.getByRole("textbox", { name: "Seed", exact: true }),
  59  |   ).not.toBeVisible();
  60  |   await page
  61  |     .getByRole("textbox", { name: "Prompt", exact: true })
  62  |     .fill("Synthetic composer circle");
  63  |   await page.getByRole("button", { name: "Generate one image" }).click();
  64  |   await expect(
  65  |     page
  66  |       .getByRole("status")
  67  |       .filter({ hasText: /Failed to fetch|Load failed|NetworkError/ }),
  68  |   ).toBeVisible();
  69  |   await page.getByRole("button", { name: "Generate one image" }).click();
  70  |   await expect.poll(() => bodies.length).toBe(2);
  71  |   expect(bodies[1]).toEqual(bodies[0]);
  72  |   expect(Number.isInteger(bodies[0].seed)).toBe(true);
  73  |   expect(bodies[0].seed as number).toBeGreaterThanOrEqual(0);
  74  |   expect(bodies[0].seed as number).toBeLessThanOrEqual(4294967295);
  75  |   const job = page
  76  |     .getByRole("article")
  77  |     .filter({ hasText: "Synthetic composer circle" })
  78  |     .first();
  79  |   await expect(
  80  |     job.getByRole("button", { name: "Save", exact: true }),
  81  |   ).toBeVisible();
  82  |   const scan = await new AxeBuilder({ page }).analyze();
  83  |   expect(
  84  |     scan.violations.filter((v) =>
  85  |       ["critical", "serious"].includes(v.impact ?? ""),
  86  |     ),
  87  |   ).toEqual([]);
  88  |   await job.getByRole("button", { name: "Save", exact: true }).click();
  89  |   await expect(
  90  |     page.getByRole("dialog", { name: "Save image", exact: true }),
  91  |   ).toBeVisible();
  92  |   await page
  93  |     .getByRole("button", { name: "Close image save", exact: true })
  94  |     .click();
  95  |   await page.getByRole("button", { name: "Message", exact: true }).click();
  96  |   await expect(message).toHaveValue("Synthetic unsent chat draft");
  97  |   await expect(message).toBeFocused();
  98  |   expect(chatCalls).toBe(0);
  99  |   await workspaceLink(page, "Workflows");
> 100 |   await page.getByRole("link", { name: /Brief to images/ }).click();
      |                                                             ^ Error: locator.click: Error: strict mode violation: getByRole('link', { name: /Brief to images/ }) resolved to 4 elements:
  101 |   await page
  102 |     .getByRole("button", { name: "Configure Draft image prompt" })
  103 |     .click();
  104 |   await expect(
  105 |     page.getByRole("combobox", { name: "Prompt draft model" }),
  106 |   ).toContainText("fake-chat");
  107 |   await page.goBack();
  108 |   await page.goBack();
  109 |   await expect(message).toHaveValue("Synthetic unsent chat draft");
  110 | });
  111 | 
  112 | test("Workflow count uses automatic seeds and repeats uncertain acceptance exactly", async ({
  113 |   page,
  114 | }) => {
  115 |   await page.goto("/workflows/new?template=brief_images");
  116 |   await page
  117 |     .getByRole("textbox", { name: "Image brief" })
  118 |     .fill("Synthetic automatic variants");
  119 |   await page
  120 |     .getByRole("button", { name: "Configure Draft image prompt" })
  121 |     .click();
  122 |   await page.getByRole("combobox", { name: "Prompt draft model" }).click();
  123 |   await page
  124 |     .getByRole("option")
  125 |     .filter({ hasText: "fake-chat" })
  126 |     .first()
  127 |     .click();
  128 |   await page.getByRole("button", { name: "Configure Generate images" }).click();
  129 |   await expect(
  130 |     page.getByRole("textbox", { name: "Image variant seeds" }),
  131 |   ).not.toBeVisible();
  132 |   await page.getByRole("button", { name: "3", exact: true }).click();
  133 |   const bodies: {
  134 |     seeds: number[];
  135 |     request_key: string;
  136 |     model: { params: unknown };
  137 |   }[] = [];
  138 |   await page.route("**/api/workflows/runs", async (route) => {
  139 |     bodies.push(route.request().postDataJSON());
  140 |     if (bodies.length === 1) {
  141 |       await route.fetch();
  142 |       await route.abort("failed");
  143 |     } else await route.continue();
  144 |   });
  145 |   await page
  146 |     .getByRole("button", { name: "Start workflow", exact: true })
  147 |     .click();
  148 |   await expect(
  149 |     page
  150 |       .getByRole("status")
  151 |       .filter({ hasText: /Failed to fetch|Load failed|NetworkError/ }),
  152 |   ).toBeVisible();
  153 |   await page
  154 |     .getByRole("button", { name: "Start workflow", exact: true })
  155 |     .click();
  156 |   await expect.poll(() => bodies.length).toBe(2);
  157 |   expect(bodies[1]).toEqual(bodies[0]);
  158 |   expect(bodies[0].seeds).toHaveLength(3);
  159 |   expect(bodies[0].model.params).toEqual({});
  160 |   await expect(
  161 |     page
  162 |       .getByRole("article", { name: "Brief to images run" })
  163 |       .first()
  164 |       .getByRole("textbox", { name: "Review image prompt" }),
  165 |   ).toBeVisible();
  166 | });
  167 | 
  168 | test("Image cancellation stays in composer and Workflows returns to the same saved chat", async ({
  169 |   page,
  170 |   request,
  171 |   browserName,
  172 | }) => {
  173 |   const connection = (await (await request.get("/api/connections")).json())[0];
  174 |   const response = await request.post("/api/chats", {
  175 |     data: { connection_id: connection.id, model_id: "fake-chat" },
  176 |   });
  177 |   const chat = await response.json();
  178 |   await page.goto(`/c/${chat.id}`);
  179 |   const message = page.getByRole("textbox", {
  180 |     name: "Message fake-chat",
  181 |     exact: true,
  182 |   });
  183 |   await message.fill("Synthetic saved-chat draft");
  184 |   await page.getByRole("button", { name: "Create image", exact: true }).click();
  185 |   await page
  186 |     .getByRole("textbox", { name: "Prompt", exact: true })
  187 |     .fill("Synthetic cancellable composer #slow");
  188 |   await page.getByRole("button", { name: "Generate one image" }).click();
  189 |   const job = page
  190 |     .getByRole("article")
  191 |     .filter({ hasText: "Synthetic cancellable composer #slow" })
  192 |     .first();
  193 |   await job.getByRole("button", { name: "Cancel", exact: true }).click();
  194 |   await expect(
  195 |     job.getByText("cancelled", { exact: true }).first(),
  196 |   ).toBeVisible();
  197 |   await settle(page);
  198 |   const dir = "../artifacts/composer-workflows/browser/composer";
  199 |   await mkdir(dir, { recursive: true });
  200 |   await page.screenshot({
```