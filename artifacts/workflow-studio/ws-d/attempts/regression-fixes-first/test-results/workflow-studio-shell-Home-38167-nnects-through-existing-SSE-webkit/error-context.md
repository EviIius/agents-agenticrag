# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: workflow-studio-shell.spec.ts >> Home opens template and persisted run detail, reconnects through existing SSE
- Location: web/tests/workflow-studio-shell.spec.ts:121:1

# Error details

```
Test timeout of 45000ms exceeded.
```

```
Error: locator.click: Test timeout of 45000ms exceeded.
Call log:
  - waiting for getByRole('button', { name: 'Open sidebar', exact: true })

```

# Page snapshot

```yaml
- generic [active] [ref=f1e1]:
  - generic [ref=f1e2]:
    - main [ref=f1e4]:
      - generic [ref=f1e5]:
        - button [ref=f1e6] [cursor=pointer]
        - link [ref=f1e7]:
          - /url: /workflows
          - text: Workflows
        - generic [ref=f1e8]: / Run
      - generic [ref=f1e9]:
        - generic [ref=f1e10]:
          - link [ref=f1e11]:
            - /url: /workflows/runs
            - text: All runs
          - heading [level=1] [ref=f1e12]: Brief to images
          - generic [ref=f1e13]: paused
          - button [ref=f1e14] [cursor=pointer]: Run details
        - generic [ref=f1e15]: Viewing a run from 10/13/2026, 10:20:45 AM. This saved version is read-only.
        - generic [ref=f1e17]:
          - generic [ref=f1e18]:
            - button [ref=f1e20] [cursor=pointer]:
              - generic [ref=f1e22]:
                - generic [ref=f1e23]: Start
                - generic [ref=f1e24]: Done
            - generic [ref=f1e25]:
              - button [disabled]
          - generic [ref=f1e26]:
            - button [ref=f1e28] [cursor=pointer]:
              - generic [ref=f1e30]:
                - generic [ref=f1e31]: Draft image prompt
                - generic [ref=f1e32]: Done
            - generic [ref=f1e33]:
              - button [disabled]
          - generic [ref=f1e34]:
            - button [ref=f1e36] [cursor=pointer]:
              - generic [ref=f1e38]:
                - generic [ref=f1e39]: Check the prompt
                - generic [ref=f1e40]: Waiting for you
            - generic [ref=f1e41]:
              - button [disabled]
          - generic [ref=f1e42]:
            - button [ref=f1e44] [cursor=pointer]:
              - generic [ref=f1e46]:
                - generic [ref=f1e47]: Create images
                - generic [ref=f1e48]: Waiting
            - generic [ref=f1e49]:
              - button [disabled]
          - button [ref=f1e52] [cursor=pointer]:
            - generic [ref=f1e54]:
              - generic [ref=f1e55]: Save results
              - generic [ref=f1e56]: Waiting
    - region "Notifications alt+T"
  - dialog [ref=f1e57]:
    - banner [ref=f1e59]:
      - heading "Run details" [level=2] [ref=f1e60]
      - button "Close Run details" [ref=f1e61] [cursor=pointer]
    - paragraph [ref=f1e62]: Saved states and results for this run.
    - article "Brief to images run" [ref=f1e64]:
      - generic [ref=f1e65]:
        - heading "Brief to images" [level=3] [ref=f1e66]
        - generic [ref=f1e67]: 10/13/2026, 10:20:45 AM
      - status [ref=f1e68]: Review the image prompt · paused
      - paragraph [ref=f1e69]: "Text model: fake-chat"
      - list [ref=f1e70]:
        - listitem [ref=f1e71]:
          - generic [ref=f1e72]:
            - generic [ref=f1e73]: 1. Draft image prompt
            - generic [ref=f1e74]: complete · attempt 1
          - generic [ref=f1e75]: "Fake runtime reply. - A clear first step - A useful second step ```python print('Hello') ``` | Item | Value | | --- | --- | | Example | 42 |"
        - listitem [ref=f1e76]:
          - generic [ref=f1e77]:
            - generic [ref=f1e78]: 2. Generate image 1
            - generic [ref=f1e79]: pending
      - generic [ref=f1e80]:
        - generic [ref=f1e81]:
          - text: Review image prompt
          - textbox "Review image prompt" [ref=f1e82]: "Fake runtime reply. - A clear first step - A useful second step ```python print('Hello') ``` | Item | Value | | --- | --- | | Example | 42 |"
        - button "Approve prompt and generate" [ref=f1e83] [cursor=pointer]
      - generic [ref=f1e84]:
        - button "Cancel workflow" [ref=f1e85] [cursor=pointer]
        - button "Save outputs" [ref=f1e86] [cursor=pointer]
```

# Test source

```ts
  1  | import { expect, type Page } from "@playwright/test";
  2  | 
  3  | export async function openSidebar(page: Page) {
  4  |   if (
  5  |     !(await page
  6  |       .getByRole("navigation", { name: "Workspace", exact: true })
  7  |       .isVisible())
  8  |   )
  9  |     await page
  10 |       .getByRole("button", { name: "Open sidebar", exact: true })
> 11 |       .click();
     |        ^ Error: locator.click: Test timeout of 45000ms exceeded.
  12 | }
  13 | export async function workspaceLink(page: Page, label: "Workflows" | "Images") {
  14 |   await openSidebar(page);
  15 |   await page
  16 |     .getByRole("navigation", { name: "Workspace", exact: true })
  17 |     .getByRole("link", { name: label, exact: true })
  18 |     .click();
  19 |   await expect(page).toHaveURL(
  20 |     label === "Workflows" ? /\/workflows$/ : /\/images$/,
  21 |   );
  22 | }
  23 | 
```