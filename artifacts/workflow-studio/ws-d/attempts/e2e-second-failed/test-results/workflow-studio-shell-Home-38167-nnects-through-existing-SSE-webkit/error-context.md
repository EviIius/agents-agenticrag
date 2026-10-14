# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: workflow-studio-shell.spec.ts >> Home opens template and persisted run detail, reconnects through existing SSE
- Location: tests/workflow-studio-shell.spec.ts:121:1

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
- generic [active]:
  - generic:
    - generic [aria-hidden]:
      - main:
        - generic:
          - button
          - link:
            - /url: /workflows
            - text: Workflows
          - generic: / Run
        - generic:
          - generic:
            - link:
              - /url: /workflows/runs
              - text: All runs
            - heading [level=1]: Brief to images
            - generic: paused
            - button: Run details
          - generic: Viewing a run from 10/13/2026, 10:10:54 AM. This saved version is read-only.
          - generic:
            - generic:
              - generic:
                - generic:
                  - button:
                    - generic:
                      - generic: Start
                      - generic: Done
                - generic:
                  - button [disabled]
              - generic:
                - generic:
                  - button:
                    - generic:
                      - generic: Draft image prompt
                      - generic: Done
                - generic:
                  - button [disabled]
              - generic:
                - generic:
                  - button:
                    - generic:
                      - generic: Check the prompt
                      - generic: Waiting for you
                - generic:
                  - button [disabled]
              - generic:
                - generic:
                  - button:
                    - generic:
                      - generic: Create images
                      - generic: Waiting
                - generic:
                  - button [disabled]
              - generic:
                - generic:
                  - button:
                    - generic:
                      - generic: Save results
                      - generic: Waiting
    - region "Notifications alt+T"
  - dialog [ref=f1e2]:
    - heading "Run details" [level=2] [ref=f1e4]
    - paragraph [ref=f1e5]: Saved states and results for this run.
    - article "Brief to images run" [ref=f1e7]:
      - generic [ref=f1e8]:
        - heading "Brief to images" [level=3] [ref=f1e9]
        - generic [ref=f1e10]: 10/13/2026, 10:10:54 AM
      - status [ref=f1e11]: Review the image prompt · paused
      - paragraph [ref=f1e12]: "Text model: fake-chat"
      - list [ref=f1e13]:
        - listitem [ref=f1e14]:
          - generic [ref=f1e15]:
            - generic [ref=f1e16]: 1. Draft image prompt
            - generic [ref=f1e17]: complete · attempt 1
          - generic [ref=f1e18]: "Fake runtime reply. - A clear first step - A useful second step ```python print('Hello') ``` | Item | Value | | --- | --- | | Example | 42 |"
        - listitem [ref=f1e19]:
          - generic [ref=f1e20]:
            - generic [ref=f1e21]: 2. Generate image 1
            - generic [ref=f1e22]: pending
      - generic [ref=f1e23]:
        - generic [ref=f1e24]:
          - text: Review image prompt
          - textbox "Review image prompt" [ref=f1e25]: "Fake runtime reply. - A clear first step - A useful second step ```python print('Hello') ``` | Item | Value | | --- | --- | | Example | 42 |"
        - button "Approve prompt and generate" [ref=f1e26] [cursor=pointer]
      - generic [ref=f1e27]:
        - button "Cancel workflow" [ref=f1e28] [cursor=pointer]
        - button "Save outputs" [ref=f1e29] [cursor=pointer]
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