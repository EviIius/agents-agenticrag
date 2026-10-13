# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: workflows.spec.ts >> Recording workflow retains source and sends only explicit overrides
- Location: tests/workflows.spec.ts:159:1

# Error details

```
Test timeout of 45000ms exceeded.
```

```
Error: locator.focus: Test timeout of 45000ms exceeded.
Call log:
  - waiting for locator('.react-flow__node-block').filter({ has: locator('.wf-block-title').filter({ hasText: /^Draft meeting pack$/ }) })

```

# Page snapshot

```yaml
- generic [ref=e2]:
  - main [ref=e4]:
    - generic [ref=e5]:
      - generic [ref=e6]:
        - button "Open sidebar" [ref=e7] [cursor=pointer]
        - link "Back to Workflows" [ref=e8]:
          - /url: /workflows
        - button "Recording to meeting pack" [ref=e11] [cursor=pointer]
        - button "1 workflow problems" [ref=e12] [cursor=pointer]: "1"
        - button "Workflow menu" [ref=e13] [cursor=pointer]
        - button "Run" [ref=e14] [cursor=pointer]
      - generic "Workflow Outline" [ref=e16]:
        - generic [ref=e17]:
          - generic [ref=e18]:
            - button "Configure Start" [ref=e19] [cursor=pointer]:
              - generic [ref=e21]:
                - generic [ref=e22]: Start
                - generic [ref=e23]: "Inputs: Recording"
            - button "Actions for Start" [ref=e24] [cursor=pointer]
          - button "Insert after Start" [ref=e26] [cursor=pointer]
        - generic [ref=e27]:
          - generic [ref=e28]:
            - button "Configure Transcribe recording" [ref=e29] [cursor=pointer]:
              - generic [ref=e31]:
                - generic [ref=e32]: Transcribe recording
                - generic [ref=e33]: "{{start.recording}}"
            - button "Actions for Transcribe recording" [ref=e34] [cursor=pointer]
          - button "Insert after Transcribe recording" [ref=e36] [cursor=pointer]
        - generic [ref=e37]:
          - generic [ref=e38]:
            - button "Configure Clean up transcript" [ref=e39] [cursor=pointer]:
              - generic [ref=e41]:
                - generic [ref=e42]: Clean up transcript
                - generic [ref=e43]: Disabled · skipped when the workflow runs
            - button "Actions for Clean up transcript" [ref=e44] [cursor=pointer]
          - button "Insert after Clean up transcript" [ref=e46] [cursor=pointer]
        - generic [ref=e47]:
          - generic [ref=e48]:
            - button "Configure Draft meeting pack" [ref=e49] [cursor=pointer]:
              - generic [ref=e51]:
                - generic [ref=e52]: Draft meeting pack
                - generic [ref=e53]: Workflow default · Markdown
            - button "Actions for Draft meeting pack" [ref=e54] [cursor=pointer]
          - button "Insert after Draft meeting pack" [ref=e56] [cursor=pointer]
        - generic [ref=e58]:
          - button "Configure Save results" [ref=e59] [cursor=pointer]:
            - generic [ref=e61]:
              - generic [ref=e62]: Save results
              - generic [ref=e63]: Markdown, JSON · 1 items
          - button "Actions for Save results" [ref=e64] [cursor=pointer]
      - button "Import workflow JSON" [ref=e65]
  - region "Notifications alt+T"
```

# Test source

```ts
  1  | import { expect, type Page } from "@playwright/test";
  2  | import { settle } from "./helpers";
  3  | export async function configureStudioBlock(page: Page, title: string) {
  4  |   const close = page.getByRole("button", {
  5  |     name: "Close Inspector",
  6  |     exact: true,
  7  |   });
  8  |   if (await close.isVisible()) {
  9  |     await close.click();
  10 |     await settle(page);
  11 |   }
  12 |   const outline = page.getByRole("button", {
  13 |     name: `Configure ${title}`,
  14 |     exact: true,
  15 |   });
  16 |   if (await outline.isVisible()) await outline.click();
  17 |   else {
  18 |     const node = page.locator(".react-flow__node-block").filter({
  19 |       has: page
  20 |         .locator(".wf-block-title")
  21 |         .filter({ hasText: new RegExp("^" + title + "$") }),
  22 |     });
  23 |     await node.focus();
  24 |     await expect(node).toBeFocused();
> 25 |     await page.keyboard.press("Enter");
     |                ^ Error: locator.focus: Test timeout of 45000ms exceeded.
  26 |   }
  27 |   await expect(
  28 |     page.getByRole("textbox", { name: "Block name", exact: true }),
  29 |   ).toHaveValue(title);
  30 | }
  31 | export async function chooseStudioModel(page: Page) {
  32 |   await page.getByRole("combobox", { name: "Model", exact: true }).click();
  33 |   await page
  34 |     .getByRole("option")
  35 |     .filter({ hasText: "fake-chat" })
  36 |     .first()
  37 |     .click();
  38 | }
  39 | export async function openStudioRun(page: Page) {
  40 |   await expect(page.locator(".wf-save-status")).toHaveText("Saved");
  41 |   await page.getByRole("button", { name: "Run", exact: true }).click();
  42 |   await expect(
  43 |     page.getByRole("button", { name: "Run workflow", exact: true }),
  44 |   ).toBeVisible();
  45 | }
  46 | 
```