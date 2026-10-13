# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: composer-workflows.spec.ts >> Visual builder reflows and every node opens its settings with keyboard
- Location: tests/composer-workflows.spec.ts:236:1

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator:  locator('.wf-studio')
Expected: visible
Received: hidden
Timeout:  5000ms

Call log:
  - Expect "toBeVisible" locator('.wf-studio') with timeout 5000ms
  - waiting for locator('.wf-studio')
    14 × locator resolved to <div tabindex="-1" class="wf-studio">…</div>
       - unexpected value "hidden"

```

```yaml
- main:
  - button "Open sidebar"
  - button "Choose model": fake-chat
  - button "Chat controls"
  - button "Chat actions"
  - paragraph: Workflow Studio · fake runtime states
  - button "light"
  - button "dark"
  - button "canvas"
  - button "empty"
  - button "selected"
  - button "problems"
  - button "conflict"
  - button "outline"
  - button "non-nestable"
  - button "settings"
  - button "run-inputs"
  - button "run-running"
  - button "run-paused"
  - button "run-complete"
  - button "run-failed"
  - button "run-interrupted"
  - button "run-reused"
  - button "run-skipped"
  - button "pick-paused"
  - button "block-test"
  - button "cards"
  - button "home-cards"
  - button "quick-add"
  - button "setup-start"
  - button "setup-generate"
  - button "setup-transcribe"
  - button "setup-clean_transcript"
  - button "setup-generate_image"
  - button "setup-review"
  - button "setup-pick"
  - button "setup-output"
  - button "Open sidebar"
  - link "Back to Workflows":
    - /url: /workflows
  - button "Synthetic image workflow"
  - button "Workflow menu"
  - button "Run"
  - button "Configure Start": "Start Inputs: Image brief"
  - button "Actions for Start"
  - button "Insert after Start"
  - button "Configure Draft image prompt": Draft image prompt fake-chat
  - button "Actions for Draft image prompt"
  - button "Insert after Draft image prompt"
  - button "Configure Check the prompt": "Check the prompt Review {{draft.text}} · editable"
  - button "Actions for Check the prompt"
  - button "Insert after Check the prompt"
  - button "Configure Create images": Create images 1 image · FLUX.2 klein
  - button "Actions for Create images"
  - button "Insert after Create images"
  - button "Configure Save results": Save results Markdown, JSON · 2 items
  - button "Actions for Save results"
  - button "Import workflow JSON"
- region "Notifications alt+T"
```

# Test source

```ts
  1  | import { expect, type Page } from "@playwright/test";
  2  | import { settle } from "./helpers";
  3  | export async function configureStudioBlock(page: Page, title: string) {
> 4  |   await expect(page.locator(".wf-studio")).toBeVisible();
     |                                            ^ Error: expect(locator).toBeVisible() failed
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
  42 |   const close = page.getByRole("button", {
  43 |     name: "Close Inspector",
  44 |     exact: true,
  45 |   });
  46 |   if (await close.isVisible()) {
  47 |     await close.click();
  48 |     await settle(page);
  49 |   }
  50 |   await expect(page.locator(".wf-save-status")).toHaveText("Saved");
  51 |   await page.getByRole("button", { name: "Run", exact: true }).click();
  52 |   await expect(
  53 |     page.getByRole("button", { name: "Run workflow", exact: true }),
  54 |   ).toBeVisible();
  55 | }
  56 | 
```