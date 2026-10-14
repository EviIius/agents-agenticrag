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
Error: locator.click: Test timeout of 45000ms exceeded.
Call log:
  - waiting for getByRole('button', { name: 'Run', exact: true })

```

# Page snapshot

```yaml
- generic:
  - generic:
    - generic [aria-hidden]:
      - main:
        - generic:
          - generic:
            - button
            - link:
              - /url: /workflows
            - button: Brief to images
            - button
            - button: Run
          - generic:
            - generic:
              - generic:
                - generic:
                  - button:
                    - generic:
                      - generic: Start
                      - generic: "Inputs: Image brief"
                  - button
                - generic:
                  - button
              - generic:
                - generic:
                  - button:
                    - generic:
                      - generic: Draft image prompt
                      - generic: fake-chat
                  - button
                - generic:
                  - button
              - generic:
                - generic:
                  - button:
                    - generic:
                      - generic: Check the prompt
                      - generic: "Review {{draft.text}} · editable"
                  - button
                - generic:
                  - button
              - generic:
                - generic:
                  - button:
                    - generic:
                      - generic: Create images
                      - generic: 3 images · FLUX.2 klein
                  - button
                - generic:
                  - button
              - generic:
                - generic:
                  - button:
                    - generic:
                      - generic: Save results
                      - generic: Markdown, JSON · 2 items
                  - button
          - button
    - region "Notifications alt+T"
  - dialog [ref=e2]:
    - heading "Create images" [level=2] [ref=e4]
    - paragraph [ref=e5]: Edit this workflow's settings.
    - generic [ref=e6]:
      - banner [ref=e7]:
        - generic [ref=e13]:
          - textbox "Block name" [ref=e14]: Create images
          - paragraph [ref=e15]: Create images
        - button "Actions for Create images" [ref=e16] [cursor=pointer]
        - button "Close Inspector" [ref=e17] [cursor=pointer]
      - generic [ref=e18]:
        - tablist "Block settings" [ref=e19]:
          - tab "Setup" [selected] [ref=e20] [cursor=pointer]
          - tab "Output" [ref=e21] [cursor=pointer]
        - tabpanel "Setup" [active] [ref=e22]:
          - generic [ref=e23]:
            - generic [ref=e24]: Prompt
            - generic [ref=e25]:
              - generic [aria-hidden]:
                - mark: "{{review.value}}"
              - textbox "Prompt" [ref=e26]: "{{review.value}}"
              - button "Insert a variable in Prompt" [ref=e27] [cursor=pointer]: "{x}"
            - paragraph [ref=e28]: At most 4,000 characters after variables are filled.
          - generic [ref=e29]:
            - generic [ref=e30]: Images
            - group "Images" [ref=e31]:
              - button "1" [ref=e32] [cursor=pointer]
              - button "2" [ref=e33] [cursor=pointer]
              - button "3" [pressed] [ref=e34] [cursor=pointer]
          - generic [ref=e35]:
            - generic [ref=e36]: Seeds
            - group "Seeds" [ref=e37]:
              - button "Automatic" [pressed] [ref=e38] [cursor=pointer]
              - button "Advanced" [ref=e39] [cursor=pointer]
          - region "Connections" [ref=e40]:
            - heading "GETS INPUT FROM" [level=3] [ref=e41]
            - generic [ref=e42]:
              - generic [ref=e43]: Check the prompt · approved
              - button "Remove input connection e_review_images" [ref=e44] [cursor=pointer]
            - generic [ref=e45]:
              - generic [ref=e46]: Add an input connection
              - combobox "Add an input connection" [ref=e47] [cursor=pointer]:
                - generic: Add connection…
            - heading "SENDS OUTPUT TO" [level=3] [ref=e48]
            - generic [ref=e49]:
              - generic [ref=e50]: Save results
              - button "Remove output connection e_images_save" [ref=e51] [cursor=pointer]
            - generic [ref=e52]:
              - generic [ref=e53]: Add an output connection
              - combobox "Add an output connection" [ref=e54] [cursor=pointer]:
                - generic: Add connection…
          - generic [ref=e55]:
            - heading "PRODUCES" [level=3] [ref=e56]
            - generic [ref=e57]:
              - button "Copy reference images.images" [ref=e58] [cursor=pointer]: "{{images.images}}"
              - button "Copy reference images.prompt" [ref=e59] [cursor=pointer]: "{{images.prompt}}"
          - group [ref=e60]:
            - generic "Advanced" [ref=e61] [cursor=pointer]
```

# Test source

```ts
  1  | import { expect, type Page } from "@playwright/test";
  2  | import { settle } from "./helpers";
  3  | export async function configureStudioBlock(page: Page, title: string) {
  4  |   await expect(page.locator(".wf-studio")).toBeVisible();
  5  |   await settle(page);
  6  |   const close = page.getByRole("button", {
  7  |     name: "Close Inspector",
  8  |     exact: true,
  9  |   });
  10 |   if (await close.isVisible()) {
  11 |     await close.click();
  12 |     await settle(page);
  13 |   }
  14 |   const outline = page.getByRole("button", {
  15 |     name: `Configure ${title}`,
  16 |     exact: true,
  17 |   });
  18 |   if (await outline.isVisible()) await outline.click();
  19 |   else {
  20 |     const node = page.locator(".react-flow__node-block").filter({
  21 |       has: page
  22 |         .locator(".wf-block-title")
  23 |         .filter({ hasText: new RegExp("^" + title + "$") }),
  24 |     });
  25 |     await node.focus();
  26 |     await expect(node).toBeFocused();
  27 |     await page.keyboard.press("Enter");
  28 |   }
  29 |   await expect(
  30 |     page.getByRole("textbox", { name: "Block name", exact: true }),
  31 |   ).toHaveValue(title);
  32 | }
  33 | export async function chooseStudioModel(page: Page) {
  34 |   await page.getByRole("combobox", { name: "Model", exact: true }).click();
  35 |   await page
  36 |     .getByRole("option")
  37 |     .filter({ hasText: "fake-chat" })
  38 |     .first()
  39 |     .click();
  40 | }
  41 | export async function openStudioRun(page: Page) {
  42 |   await expect(page.locator(".wf-save-status")).toHaveText("Saved");
> 43 |   await page.getByRole("button", { name: "Run", exact: true }).click();
     |                                                                ^ Error: locator.click: Test timeout of 45000ms exceeded.
  44 |   await expect(
  45 |     page.getByRole("button", { name: "Run workflow", exact: true }),
  46 |   ).toBeVisible();
  47 | }
  48 | 
```