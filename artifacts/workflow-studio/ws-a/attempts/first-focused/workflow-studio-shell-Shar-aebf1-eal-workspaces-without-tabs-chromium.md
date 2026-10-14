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
          - link "New chat" [ref=e9] [cursor=pointer]:
            - /url: /
        - navigation "Chat history" [ref=e10]:
          - generic [ref=e11]:
            - textbox "Search history" [ref=e12]:
              - /placeholder: Search chats…
            - generic: ⌘K
          - navigation "Workspace" [ref=e13]:
            - link "Workflows" [active] [ref=e15] [cursor=pointer]:
              - /url: /workflows
            - link "Images" [ref=e21] [cursor=pointer]:
              - /url: /images
          - region "Folders" [ref=e27]:
            - generic [ref=e28]:
              - heading "Folders" [level=2] [ref=e29]
              - button "New folder" [ref=e30] [cursor=pointer]
            - paragraph [ref=e31]: No folders yet
          - paragraph [ref=e32]: No chats yet
        - button "Settings" [ref=e34] [cursor=pointer]
    - main [ref=e35]:
      - link "Workflows" [ref=e37] [cursor=pointer]:
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
                - link [ref=e48] [cursor=pointer]:
                  - /url: /workflows/new?template=brief_images
                  - heading "Brief to images" [level=3] [ref=e55]
                  - paragraph [ref=e56]: Turn a brief into an image prompt, review it, then create one to three images.
                  - generic "Template steps" [ref=e57]: Use template
                - link [ref=e86] [cursor=pointer]:
                  - /url: /workflows/new?template=meeting_pack
                  - heading "Recording to meeting pack" [level=3] [ref=e90]
                  - paragraph [ref=e91]: Save the original transcript and draft a summary, decisions and action items for your review.
                  - generic "Template steps" [ref=e92]: Use template
            - region "Recent workflow runs" [ref=e113]:
              - generic [ref=e114]:
                - heading "RECENT RUNS" [level=2] [ref=e115]
                - link "View all runs" [ref=e116] [cursor=pointer]:
                  - /url: /workflows/runs
              - link [ref=e118] [cursor=pointer]:
                - /url: /workflows/runs/b0f93009f82641e88559ccb4d0a53afc
                - generic [ref=e122]:
                  - paragraph [ref=e123]: Brief to images
                  - paragraph [ref=e124]: Waiting for you · Review the image prompt
                - time [ref=e125]: Oct 12, 5:08 PM
            - paragraph [ref=e128]: Text outputs are drafts for your review. Original sources and saved results stay available in each run.
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
  19  |       for (const state of ["empty", "loading", "populated"]) {
  20  |         await page.getByRole("button", { name: state, exact: true }).click();
  21  |         await settle(page);
  22  |         const scan = await new AxeBuilder({ page }).analyze();
  23  |         expect(
  24  |           scan.violations.filter((v) =>
  25  |             ["serious", "critical"].includes(v.impact ?? ""),
  26  |           ),
  27  |           state,
  28  |         ).toEqual([]);
  29  |         expect(
  30  |           await page.evaluate(
  31  |             () => document.documentElement.scrollWidth <= innerWidth,
  32  |           ),
  33  |         ).toBeTruthy();
  34  |         results.push({ state, seriousCritical: 0 });
  35  |         await page.screenshot({
  36  |           path: `${dir}/home-${state}-${width}-${theme}-${browserName}-fake.png`,
  37  |           fullPage: true,
  38  |         });
  39  |       }
  40  |       await writeFile(
  41  |         `${dir}/axe-home-${width}-${theme}-${browserName}.json`,
  42  |         JSON.stringify(results, null, 2),
  43  |       );
  44  |     });
  45  |   }
  46  | 
  47  | test("Shared sidebar, rail and palette navigate real workspaces without tabs", async ({
  48  |   page,
  49  |   browserName,
  50  | }) => {
  51  |   await page.setViewportSize({ width: 1440, height: 900 });
  52  |   await page.goto("/");
  53  |   await workspaceLink(page, "Workflows");
  54  |   await expect(
  55  |     page.getByRole("heading", { name: "Workflows", exact: true }),
  56  |   ).toBeVisible();
  57  |   await expect(
  58  |     page
  59  |       .getByRole("navigation", { name: "Workspace", exact: true })
  60  |       .getByRole("link", { name: "Workflows", exact: true }),
  61  |   ).toHaveAttribute("aria-current", "page");
  62  |   await expect(
  63  |     page.getByRole("link", { name: "Chat", exact: true }),
  64  |   ).toHaveCount(0);
> 65  |   await expect(page.getByRole("link", { name: /Use template/ })).toHaveCount(2);
      |                                                                  ^ Error: expect(locator).toHaveCount(expected) failed
  66  |   await page
  67  |     .getByRole("button", { name: "Collapse sidebar", exact: true })
  68  |     .click();
  69  |   await workspaceLink(page, "Images");
  70  |   await expect(
  71  |     page.getByRole("heading", { name: "Images", exact: true }),
  72  |   ).toBeVisible();
  73  |   await expect(page.locator(".sidebar-desktop")).toHaveAttribute(
  74  |     "data-collapsed",
  75  |     "true",
  76  |   );
  77  |   await expect(
  78  |     page
  79  |       .getByRole("navigation", { name: "Workspace", exact: true })
  80  |       .getByRole("link", { name: "Images", exact: true }),
  81  |   ).toHaveAttribute("aria-current", "page");
  82  |   await page.keyboard.press("ControlOrMeta+k");
  83  |   await page
  84  |     .getByRole("combobox", { name: "Search chats and actions" })
  85  |     .fill("Workflows");
  86  |   await page.getByRole("option", { name: "Workflows", exact: true }).click();
  87  |   await expect(page).toHaveURL(/\/workflows$/);
  88  |   await page.setViewportSize({ width: 390, height: 844 });
  89  |   await openSidebar(page);
  90  |   await expect(
  91  |     page
  92  |       .getByRole("navigation", { name: "Workspace", exact: true })
  93  |       .getByRole("link", { name: "Images", exact: true }),
  94  |   ).toBeVisible();
  95  |   await page
  96  |     .getByRole("navigation", { name: "Workspace", exact: true })
  97  |     .getByRole("link", { name: "Images", exact: true })
  98  |     .click();
  99  |   await expect(page).toHaveURL(/\/images$/);
  100 |   await expect(
  101 |     page.getByRole("dialog", { name: "Chat history", exact: true }),
  102 |   ).not.toBeVisible();
  103 |   await settle(page);
  104 |   await mkdir(dir, { recursive: true });
  105 |   await page.screenshot({
  106 |     path: `${dir}/images-shared-shell-390-${browserName}-fake.png`,
  107 |     fullPage: true,
  108 |   });
  109 | });
  110 | 
  111 | test("Home opens template and persisted run detail, reconnects through existing SSE", async ({
  112 |   page,
  113 |   request,
  114 | }) => {
  115 |   const connection = (await (await request.get("/api/connections")).json())[0];
  116 |   const response = await request.post("/api/workflows/runs", {
  117 |     data: {
  118 |       request_key: crypto.randomUUID(),
  119 |       template: "brief_images",
  120 |       model: {
  121 |         connection_id: connection.id,
  122 |         model_id: "fake-chat",
  123 |         params: {},
  124 |       },
  125 |       brief: "Synthetic shell workflow",
  126 |       review_prompt: true,
  127 |       seeds: [19],
  128 |     },
  129 |   });
  130 |   expect(response.status()).toBe(202);
  131 |   const run = await response.json();
  132 |   await page.goto("/workflows");
  133 |   const recent = page.getByRole("region", {
  134 |     name: "Recent workflow runs",
  135 |     exact: true,
  136 |   });
  137 |   const row = recent.locator(`a[href='/workflows/runs/${run.id}']`);
  138 |   await expect(row).toContainText("Waiting for you");
  139 |   await row.click();
  140 |   const card = page.getByRole("article", {
  141 |     name: "Brief to images run",
  142 |     exact: true,
  143 |   });
  144 |   await expect(
  145 |     card.getByRole("textbox", { name: "Review image prompt" }),
  146 |   ).toBeVisible();
  147 |   await page.reload();
  148 |   await expect(
  149 |     card.getByRole("textbox", { name: "Review image prompt" }),
  150 |   ).toBeVisible();
  151 |   await workspaceLink(page, "Workflows");
  152 |   await page.getByRole("link", { name: /Recording to meeting pack/ }).click();
  153 |   await expect(page).toHaveURL(/\/workflows\/new\?template=meeting_pack$/);
  154 |   await expect(
  155 |     page.getByRole("combobox", { name: "Saved recording" }),
  156 |   ).toBeVisible();
  157 | });
  158 | 
```