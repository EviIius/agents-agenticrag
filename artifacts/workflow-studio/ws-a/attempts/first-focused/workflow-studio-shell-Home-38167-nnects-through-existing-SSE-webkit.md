# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: workflow-studio-shell.spec.ts >> Home opens template and persisted run detail, reconnects through existing SSE
- Location: tests/workflow-studio-shell.spec.ts:111:1

# Error details

```
Error: locator.click: Error: strict mode violation: getByRole('link', { name: /Recording to meeting pack/ }) resolved to 2 elements:
    1) <a data-discover="true" href="/workflows/new?template=meeting_pack" aria-label="Use Recording to meeting pack template" class="group flex flex-col gap-4 rounded-xl border border-line bg-surface p-5 hover:border-line-strong hover:bg-surface-2">…</a> aka getByRole('link', { name: 'Use Recording to meeting pack' })
    2) <a data-discover="true" href="/workflows/runs/c0023a4053b14b019f7e639c00cf9967" aria-label="Recording to meeting pack — Complete · Ready for review" class="flex min-h-16 items-center gap-3 border-b border-line px-4 py-3 last:border-b-0 hover:bg-surface-2">…</a> aka getByRole('link', { name: 'Recording to meeting pack —' })

Call log:
  - waiting for getByRole('link', { name: /Recording to meeting pack/ })

```

# Page snapshot

```yaml
- generic [ref=f1e2]:
  - main [ref=f1e4]:
    - generic [ref=f1e5]:
      - button "Open sidebar" [ref=f1e6] [cursor=pointer]
      - link "Workflows" [ref=f1e7]:
        - /url: /workflows
    - region "Workflows" [ref=f1e8]:
      - generic [ref=f1e9]:
        - status [ref=f1e10]: Connected
        - generic [ref=f1e11]:
          - generic [ref=f1e12]:
            - heading "Workflows" [level=1] [ref=f1e13]
            - paragraph [ref=f1e14]: Turn images and recordings into repeatable steps. Accepted runs keep going on your Mac when you close the app.
          - region "Workflow templates" [ref=f1e15]:
            - heading "START FROM A TEMPLATE" [level=2] [ref=f1e16]
            - generic [ref=f1e17]:
              - link "Use Brief to images template" [ref=f1e18]:
                - /url: /workflows/new?template=brief_images
                - heading "Brief to images" [level=3] [ref=f1e25]
                - paragraph [ref=f1e26]: Turn a brief into an image prompt, review it, then create one to three images.
                - generic [ref=f1e53]: Use template
              - link "Use Recording to meeting pack template" [ref=f1e56]:
                - /url: /workflows/new?template=meeting_pack
                - heading "Recording to meeting pack" [level=3] [ref=f1e60]
                - paragraph [ref=f1e61]: Save the original transcript and draft a summary, decisions and action items for your review.
                - generic [ref=f1e80]: Use template
          - region "Recent workflow runs" [ref=f1e83]:
            - generic [ref=f1e84]:
              - heading "RECENT RUNS" [level=2] [ref=f1e85]
              - link "View all runs" [ref=f1e86]:
                - /url: /workflows/runs
            - generic [ref=f1e87]:
              - link "Brief to images — Waiting for you · Review the image prompt" [ref=f1e88]:
                - /url: /workflows/runs/bd9a4a787d2e46be9a777703c6ce086c
                - generic [ref=f1e92]:
                  - paragraph [ref=f1e93]: Brief to images
                  - paragraph [ref=f1e94]: Waiting for you · Review the image prompt
              - link "Brief to images — Waiting for you · Review the image prompt" [ref=f1e97]:
                - /url: /workflows/runs/734a0fb75db84f999fdb2dc34e6942bd
                - generic [ref=f1e101]:
                  - paragraph [ref=f1e102]: Brief to images
                  - paragraph [ref=f1e103]: Waiting for you · Review the image prompt
              - link "Recording to meeting pack — Complete · Ready for review" [ref=f1e106]:
                - /url: /workflows/runs/c0023a4053b14b019f7e639c00cf9967
                - generic [ref=f1e109]:
                  - paragraph [ref=f1e110]: Recording to meeting pack
                  - paragraph [ref=f1e111]: Complete · Ready for review
              - link "Brief to images — Complete · Ready for review" [ref=f1e114]:
                - /url: /workflows/runs/a6bceab1bdfd47caa1c7edef754e5fa7
                - generic [ref=f1e117]:
                  - paragraph [ref=f1e118]: Brief to images
                  - paragraph [ref=f1e119]: Complete · Ready for review
              - link "Brief to images — Waiting for you · Review the image prompt" [ref=f1e122]:
                - /url: /workflows/runs/dac67fe001f04b09b5456d0cf1925c1b
                - generic [ref=f1e126]:
                  - paragraph [ref=f1e127]: Brief to images
                  - paragraph [ref=f1e128]: Waiting for you · Review the image prompt
              - link "Brief to images — Waiting for you · Review the image prompt" [ref=f1e131]:
                - /url: /workflows/runs/b0f93009f82641e88559ccb4d0a53afc
                - generic [ref=f1e135]:
                  - paragraph [ref=f1e136]: Brief to images
                  - paragraph [ref=f1e137]: Waiting for you · Review the image prompt
          - paragraph [ref=f1e140]: Text outputs are drafts for your review. Original sources and saved results stay available in each run.
  - region "Notifications alt+T"
```

# Test source

```ts
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
  65  |   await expect(
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
> 152 |     exact: true,
      |                                                                       ^ Error: locator.click: Error: strict mode violation: getByRole('link', { name: /Recording to meeting pack/ }) resolved to 2 elements:
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
  166 |   ).toBeVisible();
  167 | });
  168 | 
```