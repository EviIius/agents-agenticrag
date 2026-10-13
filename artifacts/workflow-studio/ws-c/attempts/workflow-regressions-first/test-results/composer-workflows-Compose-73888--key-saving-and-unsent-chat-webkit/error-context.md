# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: composer-workflows.spec.ts >> Composer image acceptance retry preserves seed/key, saving and unsent chat
- Location: tests/composer-workflows.spec.ts:25:1

# Error details

```
Test timeout of 45000ms exceeded.
```

```
Error: locator.focus: Test timeout of 45000ms exceeded.
Call log:
  - waiting for locator('.react-flow__node-block').filter({ has: locator('.wf-block-title').filter({ hasText: /^Draft image prompt$/ }) })

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
        - button "Brief to images" [ref=e11] [cursor=pointer]
        - button "Workflow menu" [ref=e12] [cursor=pointer]
        - button "Run" [ref=e13] [cursor=pointer]
      - generic "Workflow Outline" [ref=e15]:
        - generic [ref=e16]:
          - generic [ref=e17]:
            - button "Configure Start" [ref=e18] [cursor=pointer]:
              - generic [ref=e20]:
                - generic [ref=e21]: Start
                - generic [ref=e22]: "Inputs: Image brief"
            - button "Actions for Start" [ref=e23] [cursor=pointer]
          - button "Insert after Start" [ref=e25] [cursor=pointer]
        - generic [ref=e26]:
          - generic [ref=e27]:
            - button "Configure Draft image prompt" [ref=e28] [cursor=pointer]:
              - generic [ref=e30]:
                - generic [ref=e31]: Draft image prompt
                - generic [ref=e32]: fake-chat
            - button "Actions for Draft image prompt" [ref=e33] [cursor=pointer]
          - button "Insert after Draft image prompt" [ref=e35] [cursor=pointer]
        - generic [ref=e36]:
          - generic [ref=e37]:
            - button "Configure Check the prompt" [ref=e38] [cursor=pointer]:
              - generic [ref=e40]:
                - generic [ref=e41]: Check the prompt
                - generic [ref=e42]: "Review {{draft.text}} · editable"
            - button "Actions for Check the prompt" [ref=e43] [cursor=pointer]
          - button "Insert after Check the prompt" [ref=e45] [cursor=pointer]
        - generic [ref=e46]:
          - generic [ref=e47]:
            - button "Configure Create images" [ref=e48] [cursor=pointer]:
              - generic [ref=e50]:
                - generic [ref=e51]: Create images
                - generic [ref=e52]: 1 image · FLUX.2 klein
            - button "Actions for Create images" [ref=e53] [cursor=pointer]
          - button "Insert after Create images" [ref=e55] [cursor=pointer]
        - generic [ref=e57]:
          - button "Configure Save results" [ref=e58] [cursor=pointer]:
            - generic [ref=e60]:
              - generic [ref=e61]: Save results
              - generic [ref=e62]: Markdown, JSON · 2 items
          - button "Actions for Save results" [ref=e63] [cursor=pointer]
      - button "Import workflow JSON" [ref=e64]
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
  18 |     const node = page
  19 |       .locator(".react-flow__node-block")
  20 |       .filter({
  21 |         has: page
  22 |           .locator(".wf-block-title")
  23 |           .filter({ hasText: new RegExp("^" + title + "$") }),
  24 |       });
> 25 |     await node.focus();
     |                ^ Error: locator.focus: Test timeout of 45000ms exceeded.
  26 |     await page.keyboard.press("Enter");
  27 |   }
  28 | }
  29 | export async function chooseStudioModel(page: Page) {
  30 |   await page.getByRole("combobox", { name: "Model", exact: true }).click();
  31 |   await page
  32 |     .getByRole("option")
  33 |     .filter({ hasText: "fake-chat" })
  34 |     .first()
  35 |     .click();
  36 | }
  37 | export async function openStudioRun(page: Page) {
  38 |   await expect(page.locator(".wf-save-status")).toHaveText("Saved");
  39 |   await page.getByRole("button", { name: "Run", exact: true }).click();
  40 |   await expect(
  41 |     page.getByRole("button", { name: "Run workflow", exact: true }),
  42 |   ).toBeVisible();
  43 | }
  44 | 
```