# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: workflow-studio-shell.spec.ts >> Shared sidebar, rail and palette navigate real workspaces without tabs
- Location: tests/workflow-studio-shell.spec.ts:47:1

# Error details

```
Error: expect(locator).toHaveCount(expected) failed

Locator:  getByRole('link', { name: /Use template/ })
Expected: 2
Received: 0
Timeout:  5000ms

Call log:
  - Expect "toHaveCount" getByRole('link', { name: /Use template/ }) with timeout 5000ms
  - waiting for getByRole('link', { name: /Use template/ })
    14 × locator resolved to 0 elements
       - unexpected value "0"

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
          - link "New chat" [ref=e9]:
            - /url: /
        - navigation "Chat history" [ref=e10]:
          - generic [ref=e11]:
            - textbox "Search history" [ref=e12]:
              - /placeholder: Search chats…
            - generic: ⌘K
          - navigation "Workspace" [ref=e13]:
            - link "Workflows" [ref=e15]:
              - /url: /workflows
            - link "Images" [ref=e21]:
              - /url: /images
          - region "Folders" [ref=e27]:
            - generic [ref=e28]:
              - heading "Folders" [level=2] [ref=e29]
              - button "New folder" [ref=e30] [cursor=pointer]
            - paragraph [ref=e31]: No folders yet
          - paragraph [ref=e32]: No chats yet
        - button "Settings" [ref=e34] [cursor=pointer]
    - main [ref=e35]:
      - link "Workflows" [ref=e37]:
        - /url: /workflows
      - region "Workflows" [ref=e38]:
        - generic [ref=e39]:
          - status [ref=e40]: Connected
          - generic [ref=e41]:
            - generic [ref=e42]:
              - heading "Workflows" [level=1] [ref=e43]
              - paragraph [ref=e44]: Turn images and recordings into repeatable steps. Accepted runs keep going on your Mac when you close the app.
            - region "Workflow templates" [ref=e45]:
              - heading "START FROM A TEMPLATE" [level=2] [ref=e46]
              - generic [ref=e47]:
                - link "Use Brief to images template" [ref=e48]:
                  - /url: /workflows/new?template=brief_images
                  - heading "Brief to images" [level=3] [ref=e55]
                  - paragraph [ref=e56]: Turn a brief into an image prompt, review it, then create one to three images.
                  - generic [ref=e83]: Use template
                - link "Use Recording to meeting pack template" [ref=e86]:
                  - /url: /workflows/new?template=meeting_pack
                  - heading "Recording to meeting pack" [level=3] [ref=e90]
                  - paragraph [ref=e91]: Save the original transcript and draft a summary, decisions and action items for your review.
                  - generic [ref=e110]: Use template
            - region "Recent workflow runs" [ref=e113]:
              - generic [ref=e114]:
                - heading "RECENT RUNS" [level=2] [ref=e115]
                - link "View all runs" [ref=e116]:
                  - /url: /workflows/runs
              - generic [ref=e117]:
                - link "Brief to images — Waiting for you · Review the image prompt" [ref=e118]:
                  - /url: /workflows/runs/734a0fb75db84f999fdb2dc34e6942bd
                  - generic [ref=e122]:
                    - paragraph [ref=e123]: Brief to images
                    - paragraph [ref=e124]: Waiting for you · Review the image prompt
                  - time [ref=e125]: Oct 12 at 5:09 PM
                - link "Recording to meeting pack — Complete · Ready for review" [ref=e128]:
                  - /url: /workflows/runs/c0023a4053b14b019f7e639c00cf9967
                  - generic [ref=e131]:
                    - paragraph [ref=e132]: Recording to meeting pack
                    - paragraph [ref=e133]: Complete · Ready for review
                  - time [ref=e134]: Oct 12 at 5:09 PM
                - link "Brief to images — Complete · Ready for review" [ref=e137]:
                  - /url: /workflows/runs/a6bceab1bdfd47caa1c7edef754e5fa7
                  - generic [ref=e140]:
                    - paragraph [ref=e141]: Brief to images
                    - paragraph [ref=e142]: Complete · Ready for review
                  - time [ref=e143]: Oct 12 at 5:09 PM
                - link "Brief to images — Waiting for you · Review the image prompt" [ref=e146]:
                  - /url: /workflows/runs/dac67fe001f04b09b5456d0cf1925c1b
                  - generic [ref=e150]:
                    - paragraph [ref=e151]: Brief to images
                    - paragraph [ref=e152]: Waiting for you · Review the image prompt
                  - time [ref=e153]: Oct 12 at 5:09 PM
                - link "Brief to images — Waiting for you · Review the image prompt" [ref=e156]:
                  - /url: /workflows/runs/b0f93009f82641e88559ccb4d0a53afc
                  - generic [ref=e160]:
                    - paragraph [ref=e161]: Brief to images
                    - paragraph [ref=e162]: Waiting for you · Review the image prompt
                  - time [ref=e163]: Oct 12 at 5:08 PM
            - paragraph [ref=e166]: Text outputs are drafts for your review. Original sources and saved results stay available in each run.
  - region "Notifications alt+T"
```

# Test source

```ts
  1   | import { test, expect } from "@playwright/test";
  2   | import AxeBuilder from "@axe-core/playwright";
  3   | import { mkdir, writeFile } from "node:fs/promises";
  4   | import { settle } from "./helpers";
  5   | import { openSidebar, workspaceLink } from "./workspace-helpers";
  6   | 
  7   | const dir = "../artifacts/workflow-studio/ws-a/browser";
  8   | for (const width of [390, 1440])
  9   |   for (const theme of ["light", "dark"]) {
  10  |     test(`Workflow home design states ${width} ${theme}`, async ({
  11  |       page,
  12  |       browserName,
  13  |     }) => {
  14  |       await page.setViewportSize({ width, height: 900 });
  15  |       await page.goto("/design?workflow-home");
  16  |       await page.getByRole("button", { name: theme, exact: true }).click();
  17  |       await mkdir(dir, { recursive: true });
  18  |       const results = [];
  19  |       for (const state of [
  20  |         "empty",
  21  |         "loading",
  22  |         "populated",
  23  |         "error",
  24  |         "reconnecting",
  25  |         "run-loading",
  26  |         "run-unavailable",
  27  |       ]) {
  28  |         await page.getByRole("button", { name: state, exact: true }).click();
  29  |         await settle(page);
  30  |         const scan = await new AxeBuilder({ page }).analyze();
  31  |         expect(
  32  |           scan.violations.filter((v) =>
  33  |             ["serious", "critical"].includes(v.impact ?? ""),
  34  |           ),
  35  |           state,
  36  |         ).toEqual([]);
  37  |         expect(
  38  |           await page.evaluate(
  39  |             () => document.documentElement.scrollWidth <= innerWidth,
  40  |           ),
  41  |         ).toBeTruthy();
  42  |         results.push({ state, seriousCritical: 0 });
  43  |         await page.screenshot({
  44  |           path: `${dir}/home-${state}-${width}-${theme}-${browserName}-fake.png`,
  45  |           fullPage: true,
  46  |         });
  47  |       }
  48  |       await writeFile(
  49  |         `${dir}/axe-home-${width}-${theme}-${browserName}.json`,
  50  |         JSON.stringify(results, null, 2),
  51  |       );
  52  |     });
  53  |   }
  54  | 
  55  | test("Shared sidebar, rail and palette navigate real workspaces without tabs", async ({
  56  |   page,
  57  |   browserName,
  58  | }) => {
  59  |   await page.setViewportSize({ width: 1440, height: 900 });
  60  |   await page.goto("/");
  61  |   await workspaceLink(page, "Workflows");
  62  |   await expect(
  63  |     page.getByRole("heading", { name: "Workflows", exact: true }),
  64  |   ).toBeVisible();
> 65  |   await expect(
      |                                                                  ^ Error: expect(locator).toHaveCount(expected) failed
  66  |     page
  67  |       .getByRole("navigation", { name: "Workspace", exact: true })
  68  |       .getByRole("link", { name: "Workflows", exact: true }),
  69  |   ).toHaveAttribute("aria-current", "page");
  70  |   await expect(
  71  |     page.getByRole("link", { name: "Chat", exact: true }),
  72  |   ).toHaveCount(0);
  73  |   await expect(page.getByRole("link", { name: /Use .* template/ })).toHaveCount(
  74  |     2,
  75  |   );
  76  |   await page
  77  |     .getByRole("button", { name: "Collapse sidebar", exact: true })
  78  |     .click();
  79  |   await workspaceLink(page, "Images");
  80  |   await expect(
  81  |     page.getByRole("heading", { name: "Images", exact: true }),
  82  |   ).toBeVisible();
  83  |   await expect(page.locator(".sidebar-desktop")).toHaveAttribute(
  84  |     "data-collapsed",
  85  |     "true",
  86  |   );
  87  |   await expect(
  88  |     page
  89  |       .getByRole("navigation", { name: "Workspace", exact: true })
  90  |       .getByRole("link", { name: "Images", exact: true }),
  91  |   ).toHaveAttribute("aria-current", "page");
  92  |   await page.keyboard.press("ControlOrMeta+k");
  93  |   await page
  94  |     .getByRole("combobox", { name: "Search chats and actions" })
  95  |     .fill("Workflows");
  96  |   await page.getByRole("option", { name: "Workflows", exact: true }).click();
  97  |   await expect(page).toHaveURL(/\/workflows$/);
  98  |   await page.setViewportSize({ width: 390, height: 844 });
  99  |   await openSidebar(page);
  100 |   await expect(
  101 |     page
  102 |       .getByRole("navigation", { name: "Workspace", exact: true })
  103 |       .getByRole("link", { name: "Images", exact: true }),
  104 |   ).toBeVisible();
  105 |   await page
  106 |     .getByRole("navigation", { name: "Workspace", exact: true })
  107 |     .getByRole("link", { name: "Images", exact: true })
  108 |     .click();
  109 |   await expect(page).toHaveURL(/\/images$/);
  110 |   await expect(
  111 |     page.getByRole("dialog", { name: "Chat history", exact: true }),
  112 |   ).not.toBeVisible();
  113 |   await settle(page);
  114 |   await mkdir(dir, { recursive: true });
  115 |   await page.screenshot({
  116 |     path: `${dir}/images-shared-shell-390-${browserName}-fake.png`,
  117 |     fullPage: true,
  118 |   });
  119 | });
  120 | 
  121 | test("Home opens template and persisted run detail, reconnects through existing SSE", async ({
  122 |   page,
  123 |   request,
  124 | }) => {
  125 |   const connection = (await (await request.get("/api/connections")).json())[0];
  126 |   const response = await request.post("/api/workflows/runs", {
  127 |     data: {
  128 |       request_key: crypto.randomUUID(),
  129 |       template: "brief_images",
  130 |       model: {
  131 |         connection_id: connection.id,
  132 |         model_id: "fake-chat",
  133 |         params: {},
  134 |       },
  135 |       brief: "Synthetic shell workflow",
  136 |       review_prompt: true,
  137 |       seeds: [19],
  138 |     },
  139 |   });
  140 |   expect(response.status()).toBe(202);
  141 |   const run = await response.json();
  142 |   await page.goto("/workflows");
  143 |   const recent = page.getByRole("region", {
  144 |     name: "Recent workflow runs",
  145 |     exact: true,
  146 |   });
  147 |   const row = recent.locator(`a[href='/workflows/runs/${run.id}']`);
  148 |   await expect(row).toContainText("Waiting for you");
  149 |   await row.click();
  150 |   const card = page.getByRole("article", {
  151 |     name: "Brief to images run",
  152 |     exact: true,
  153 |   });
  154 |   await expect(
  155 |     card.getByRole("textbox", { name: "Review image prompt" }),
  156 |   ).toBeVisible();
  157 |   await page.reload();
  158 |   await expect(
  159 |     card.getByRole("textbox", { name: "Review image prompt" }),
  160 |   ).toBeVisible();
  161 |   await workspaceLink(page, "Workflows");
  162 |   await page.getByRole("link", { name: /Recording to meeting pack/ }).click();
  163 |   await expect(page).toHaveURL(/\/workflows\/new\?template=meeting_pack$/);
  164 |   await expect(
  165 |     page.getByRole("combobox", { name: "Saved recording" }),
```