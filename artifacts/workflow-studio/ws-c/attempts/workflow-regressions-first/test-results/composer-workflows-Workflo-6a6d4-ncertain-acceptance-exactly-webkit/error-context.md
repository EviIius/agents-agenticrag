# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: composer-workflows.spec.ts >> Workflow count uses automatic seeds and repeats uncertain acceptance exactly
- Location: tests/composer-workflows.spec.ts:117:1

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
        - button "1 workflow problems" [ref=e12] [cursor=pointer]: "1"
        - button "Workflow menu" [ref=e13] [cursor=pointer]
        - button "Run" [ref=e14] [cursor=pointer]
      - generic "Workflow Outline" [ref=e16]:
        - generic [ref=e17]:
          - generic [ref=e18]:
            - button "Configure Start" [ref=e19] [cursor=pointer]:
              - generic [ref=e21]:
                - generic [ref=e22]: Start
                - generic [ref=e23]: "Inputs: Image brief"
            - button "Actions for Start" [ref=e24] [cursor=pointer]
          - button "Insert after Start" [ref=e26] [cursor=pointer]
        - generic [ref=e27]:
          - generic [ref=e28]:
            - button "Configure Draft image prompt" [ref=e29] [cursor=pointer]:
              - generic [ref=e31]:
                - generic [ref=e32]: Draft image prompt
                - generic [ref=e33]: Workflow default
            - button "Actions for Draft image prompt" [ref=e34] [cursor=pointer]
          - button "Insert after Draft image prompt" [ref=e36] [cursor=pointer]
        - generic [ref=e37]:
          - generic [ref=e38]:
            - button "Configure Check the prompt" [ref=e39] [cursor=pointer]:
              - generic [ref=e41]:
                - generic [ref=e42]: Check the prompt
                - generic [ref=e43]: "Review {{draft.text}} · editable"
            - button "Actions for Check the prompt" [ref=e44] [cursor=pointer]
          - button "Insert after Check the prompt" [ref=e46] [cursor=pointer]
        - generic [ref=e47]:
          - generic [ref=e48]:
            - button "Configure Create images" [ref=e49] [cursor=pointer]:
              - generic [ref=e51]:
                - generic [ref=e52]: Create images
                - generic [ref=e53]: 1 image · FLUX.2 klein
            - button "Actions for Create images" [ref=e54] [cursor=pointer]
          - button "Insert after Create images" [ref=e56] [cursor=pointer]
        - generic [ref=e58]:
          - button "Configure Save results" [ref=e59] [cursor=pointer]:
            - generic [ref=e61]:
              - generic [ref=e62]: Save results
              - generic [ref=e63]: Markdown, JSON · 2 items
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