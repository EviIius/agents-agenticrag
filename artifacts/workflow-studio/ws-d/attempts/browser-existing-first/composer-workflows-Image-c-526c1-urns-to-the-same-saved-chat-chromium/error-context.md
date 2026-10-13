# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: composer-workflows.spec.ts >> Image cancellation stays in composer and Workflows returns to the same saved chat
- Location: tests/composer-workflows.spec.ts:193:1

# Error details

```
Test timeout of 45000ms exceeded.
```

```
Error: locator.click: Test timeout of 45000ms exceeded.
Call log:
  - waiting for getByRole('navigation', { name: 'Workspace', exact: true }).getByRole('link', { name: 'Workflows', exact: true })

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
            - link [ref=e15] [cursor=pointer]:
              - /url: /workflows
              - text: Workflows
              - img "A workflow is waiting for you" [ref=e20]
            - link "Images" [ref=e22] [cursor=pointer]:
              - /url: /images
          - region "Folders" [ref=e28]:
            - generic [ref=e29]:
              - heading "Folders" [level=2] [ref=e30]
              - button "New folder" [ref=e31] [cursor=pointer]
            - paragraph [ref=e32]: No folders yet
          - paragraph [ref=e33]: No chats yet
        - button "Settings" [ref=e35] [cursor=pointer]
    - main [ref=e36]:
      - generic [ref=e37]:
        - button "Choose model" [ref=e39] [cursor=pointer]:
          - generic [aria-hidden] [ref=e40]: ●
          - generic [ref=e41]: fake-chat
          - generic [ref=e42]: Fake runtime
        - generic "Double-click to rename" [ref=e43]: New chat
        - button "Chat controls" [ref=e44] [cursor=pointer]
        - button "Actions for New chat" [ref=e45] [cursor=pointer]
      - status [ref=e46]
      - log "Conversation" [ref=e47]
      - generic [ref=e49]:
        - button [aria-hidden] [ref=e50] [cursor=pointer]
        - form "Message" [ref=e52]:
          - textbox "Message fake-chat" [active] [ref=e53]:
            - /placeholder: Message fake-chat…
            - text: Synthetic saved-chat draft
          - generic [ref=e54]:
            - button "Add attachment" [ref=e55] [cursor=pointer]
            - button "Web search" [ref=e56] [cursor=pointer]:
              - generic [ref=e57]: Search
            - button "Create image" [ref=e58] [cursor=pointer]:
              - generic [ref=e59]: Image
            - generic [ref=e60]:
              - button "Library" [disabled] [ref=e61] [cursor=pointer]
              - button "Choose Library collections" [ref=e63] [cursor=pointer]
            - generic [ref=e64]:
              - img "33 of 16,384 total tokens; 12,032 input allowance; 4,096 reserved for response; 256 safety margin" [ref=e65]
              - button "Send message" [ref=e70] [cursor=pointer]
  - region "Notifications alt+T"
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
  11 |       .click();
  12 | }
  13 | export async function workspaceLink(page: Page, label: "Workflows" | "Images") {
  14 |   await openSidebar(page);
  15 |   await page
  16 |     .getByRole("navigation", { name: "Workspace", exact: true })
  17 |     .getByRole("link", { name: label, exact: true })
> 18 |     .click();
     |      ^ Error: locator.click: Test timeout of 45000ms exceeded.
  19 |   await expect(page).toHaveURL(
  20 |     label === "Workflows" ? /\/workflows$/ : /\/images$/,
  21 |   );
  22 | }
  23 | 
```