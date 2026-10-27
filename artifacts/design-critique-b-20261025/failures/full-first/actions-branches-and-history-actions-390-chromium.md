# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: actions.spec.ts >> branches and history actions 390
- Location: tests/actions.spec.ts:5:3

# Error details

```
Test timeout of 45000ms exceeded.
```

```
Error: locator.click: Test timeout of 45000ms exceeded.
Call log:
  - waiting for getByRole('button', { name: 'Edit message', exact: true })
    - locator resolved to <button data-size="icon" data-state="closed" data-variant="ghost" aria-label="Edit message" data-slot="tooltip-trigger" class="inline-flex shrink-0 items-center justify-center gap-2 rounded-md text-sm font-medium whitespace-nowrap outline-none disabled:pointer-events-none disabled:opacity-50 aria-invalid:border-destructive aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-4 hover:bg-accent hover:text-a…>…</button>
  - attempting click action
    2 × waiting for element to be visible, enabled and stable
      - element is not stable
    - retrying click action
    - waiting 20ms
    2 × waiting for element to be visible, enabled and stable
      - element is visible, enabled and stable
      - scrolling into view if needed
      - done scrolling
      - <p class="mb-4 text-xs text-fg-3 break-all">fake-chat</p> from <article aria-busy="false" aria-label="assistant message" class="message-row min-w-0 py-4 " id="m-1d2d3514753a4aabb70ccf69630b9884" data-message-id="1d2d3514753a4aabb70ccf69630b9884">…</article> subtree intercepts pointer events
    - retrying click action
      - waiting 100ms
    83 × waiting for element to be visible, enabled and stable
       - element is visible, enabled and stable
       - scrolling into view if needed
       - done scrolling
       - <p class="mb-4 text-xs text-fg-3 break-all">fake-chat</p> from <article aria-busy="false" aria-label="assistant message" class="message-row min-w-0 py-4 " id="m-1d2d3514753a4aabb70ccf69630b9884" data-message-id="1d2d3514753a4aabb70ccf69630b9884">…</article> subtree intercepts pointer events
     - retrying click action
       - waiting 500ms

```

# Page snapshot

```yaml
- generic [ref=f1e2]:
  - main [ref=f1e4]:
    - generic [ref=f1e5]:
      - generic [ref=f1e6]:
        - button "Open sidebar" [ref=f1e7] [cursor=pointer]
        - button "Choose model" [ref=f1e9] [cursor=pointer]:
          - generic [aria-hidden] [ref=f1e10]: ●
          - generic [ref=f1e11]: fake-chat
      - button "Chat controls" [ref=f1e12] [cursor=pointer]
      - button "Actions for Original branch 390 chromium" [ref=f1e13] [cursor=pointer]
    - status [ref=f1e14]
    - log "Conversation" [ref=f1e15]:
      - generic [ref=f1e16]:
        - article "user message" [ref=f1e17]:
          - heading "You said" [level=2] [ref=f1e18]
          - paragraph [ref=f1e20]: Original branch 390 chromium
          - generic [ref=f1e23]:
            - button "Copy message" [ref=f1e24] [cursor=pointer]:
              - status [ref=f1e25]
            - button "Edit message" [ref=f1e26] [cursor=pointer]
        - article "assistant message" [ref=f1e27]:
          - heading "fake-chat replied" [level=2] [ref=f1e28]
          - paragraph [ref=f1e29]: fake-chat
          - generic [ref=f1e30]:
            - status [ref=f1e31]
            - generic [ref=f1e32]:
              - paragraph [ref=f1e33]: Fake runtime reply.
              - list [ref=f1e34]:
                - listitem [ref=f1e35]: A clear first step
                - listitem [ref=f1e36]: A useful second step
              - generic [ref=f1e37]:
                - generic [ref=f1e38]: python
                - button "Copy Code" [ref=f1e41] [cursor=pointer]
                - region "Code example" [ref=f1e44]:
                  - code [ref=f1e46]:
                    - generic [ref=f1e47]: print('Hello')
              - region "Answer table" [ref=f1e48]:
                - region "Answer table" [ref=f1e49]:
                  - table [ref=f1e50]:
                    - rowgroup [ref=f1e51]:
                      - row [ref=f1e52]:
                        - columnheader "Item" [ref=f1e53]
                        - columnheader "Value" [ref=f1e54]
                    - rowgroup [ref=f1e55]:
                      - row [ref=f1e56]:
                        - cell "Example" [ref=f1e57]
                        - cell "42" [ref=f1e58]
          - generic [ref=f1e59]:
            - generic [ref=f1e61]:
              - button "Copy message" [ref=f1e62] [cursor=pointer]:
                - status [ref=f1e63]
              - button "Regenerate answer" [ref=f1e64] [cursor=pointer]
              - button "Regenerate with another model" [ref=f1e65] [cursor=pointer]
              - button "Message info" [ref=f1e66] [cursor=pointer]
              - button "Previous branch" [disabled]
              - generic [ref=f1e67]: 1 / 2
              - button "Next branch" [ref=f1e68] [cursor=pointer]
            - paragraph [ref=f1e70]: fake-chat · 31.0 tok/s · 31 tokens · 0.0s to first token
    - generic [ref=f1e71]:
      - button [aria-hidden] [ref=f1e72] [cursor=pointer]
      - form "Message" [ref=f1e73]:
        - textbox "Message fake-chat" [ref=f1e74]:
          - /placeholder: Message…
        - generic [ref=f1e75]:
          - generic "Attach files · ⌘U" [ref=f1e76]:
            - button "Attach files" [ref=f1e77] [cursor=pointer]
          - button "Tools" [ref=f1e78] [cursor=pointer]
          - generic [ref=f1e79]:
            - img "58 of 16,384 total tokens; 12,032 input allowance; 4,096 reserved for response; 256 safety margin" [ref=f1e80]
            - generic [ref=f1e84]:
              - button "Send message" [disabled]
  - region "Notifications alt+T"
```

# Test source

```ts
  1   | import { settle } from "./helpers";
  2   | import { test, expect } from "@playwright/test";
  3   | import { readFile } from "node:fs/promises";
  4   | for (const width of [390, 1440]) {
  5   |   test(`branches and history actions ${width}`, async ({
  6   |     page,
  7   |     request,
  8   |     browserName,
  9   |   }) => {
  10  |     await page.addInitScript(() => {
  11  |       Object.defineProperty(navigator, "share", {
  12  |         configurable: true,
  13  |         value: undefined,
  14  |       });
  15  |       Object.defineProperty(navigator, "canShare", {
  16  |         configurable: true,
  17  |         value: undefined,
  18  |       });
  19  |     });
  20  |     const original = `Original branch ${width} ${browserName}`;
  21  |     const edited = `Edited branch ${width} ${browserName}`;
  22  |     const renamed = `Reviewed branches ${width} ${browserName}`;
  23  |     await page.setViewportSize({ width, height: 900 });
  24  |     const connection = (
  25  |       await (await request.get("/api/connections")).json()
  26  |     )[0];
  27  |     await request.patch("/api/settings", {
  28  |       data: {
  29  |         default_connection_id: connection.id,
  30  |         default_model_id: "fake-chat",
  31  |         auto_title: false,
  32  |       },
  33  |     });
  34  |     await page.goto("/");
  35  |     await expect(
  36  |       page.getByRole("button", { name: "Choose model" }),
  37  |     ).toContainText("fake-chat");
  38  |     await page.locator(".composer textarea").fill(original);
  39  |     await page.getByRole("button", { name: "Send message" }).click();
  40  |     await expect(page).toHaveURL(/\/c\//);
  41  |     const id = page.url().split("/c/")[1]!;
  42  |     const detail = async () =>
  43  |       await (await request.get(`/api/chats/${id}`)).json();
  44  |     await expect
  45  |       .poll(
  46  |         async () =>
  47  |           (await detail()).messages.filter(
  48  |             (m: { role: string; status: string }) =>
  49  |               m.role === "assistant" && m.status === "complete",
  50  |           ).length,
  51  |       )
  52  |       .toBe(1);
  53  |     await page
  54  |       .getByRole("button", { name: "Regenerate answer", exact: true })
  55  |       .click();
  56  |     await expect
  57  |       .poll(
  58  |         async () =>
  59  |           (await detail()).messages.filter(
  60  |             (m: { role: string; status: string }) =>
  61  |               m.role === "assistant" && m.status === "complete",
  62  |           ).length,
  63  |       )
  64  |       .toBe(2);
  65  |     const assistant = page.getByRole("article", { name: "assistant message" });
  66  |     await expect(assistant).toContainText("2 / 2");
  67  |     await assistant.getByRole("button", { name: "Previous branch" }).click();
  68  |     await expect(assistant).toContainText("1 / 2");
  69  |     await page.reload();
  70  |     await expect(assistant).toContainText("1 / 2");
  71  |     await page
  72  |       .getByRole("button", { name: "Edit message", exact: true })
> 73  |       .click();
      |        ^ Error: locator.click: Test timeout of 45000ms exceeded.
  74  |     await page
  75  |       .getByRole("textbox", { name: "Edit message", exact: true })
  76  |       .fill(edited);
  77  |     await page.getByRole("button", { name: "Send", exact: true }).click();
  78  |     await expect
  79  |       .poll(
  80  |         async () =>
  81  |           (await detail()).messages.filter(
  82  |             (m: { role: string; status: string }) =>
  83  |               m.role === "assistant" && m.status === "complete",
  84  |           ).length,
  85  |       )
  86  |       .toBe(3);
  87  |     const user = page.getByRole("article", { name: "user message" });
  88  |     await expect(user).toContainText(edited);
  89  |     await user.getByRole("button", { name: "Previous branch" }).click();
  90  |     await expect(user).toContainText(original);
  91  |     await page.reload();
  92  |     await expect(user).toContainText(original);
  93  |     if (width < 640)
  94  |       await page.getByRole("button", { name: "Open sidebar" }).click();
  95  |     await page.getByRole("textbox", { name: "Search history" }).fill(original);
  96  |     const row = page.getByRole("link", {
  97  |       name: original,
  98  |       exact: true,
  99  |     });
  100 |     await expect(row).toBeVisible();
  101 |     const history = page.getByRole("navigation", { name: "Chat history" });
  102 |     const actions = history.getByRole("button", {
  103 |       name: `Actions for ${original}`,
  104 |       exact: true,
  105 |     });
  106 |     await actions.click();
  107 |     await page.getByRole("menuitem", { name: "Pin", exact: true }).click();
  108 |     await expect(page.locator('[role="menu"]')).toHaveCount(0);
  109 |     await expect.poll(async () => (await detail()).chat.pinned).toBe(true);
  110 |     await expect(
  111 |       row.locator("..").getByRole("img", { name: "Pinned chat" }),
  112 |     ).toBeVisible();
  113 |     await expect(page.getByText("Chat pinned", { exact: true })).toBeVisible();
  114 |     const toast = page
  115 |       .locator("[data-sonner-toast]")
  116 |       .filter({ hasText: "Chat pinned" });
  117 |     await expect(toast).toHaveAttribute("data-mounted", "true");
  118 |     await toast.evaluate(async (element) => {
  119 |       await Promise.all(
  120 |         element
  121 |           .getAnimations()
  122 |           .map((animation) => animation.finished.catch(() => {})),
  123 |       );
  124 |     });
  125 |     const toastClose = await toast.locator("[data-close-button]").boundingBox();
  126 |     const toastBounds = await toast.boundingBox();
  127 |     expect(toastClose!.width).toBeGreaterThanOrEqual(44);
  128 |     expect(toastClose!.height).toBeGreaterThanOrEqual(44);
  129 |     expect(toastClose!.x).toBeGreaterThanOrEqual(toastBounds!.x);
  130 |     await settle(page);
  131 |     await page.screenshot({
  132 |       path: `../artifacts/phase-2/review-pin-${width}-${browserName}.png`,
  133 |     });
  134 |     await toast.locator("[data-close-button]").click();
  135 |     await expect(toast).not.toBeVisible();
  136 |     await actions.click();
  137 |     await page.getByRole("menuitem", { name: "Unpin", exact: true }).click();
  138 |     await expect(page.locator('[role="menu"]')).toHaveCount(0);
  139 |     await expect.poll(async () => (await detail()).chat.pinned).toBe(false);
  140 |     await actions.click();
  141 |     let exportsDownloaded = 0;
  142 |     page.on("download", () => exportsDownloaded++);
  143 |     await page.getByRole("menuitem", { name: "Export Markdown" }).click();
  144 |     await settle(page);
  145 |     await page.screenshot({
  146 |       path: `../artifacts/phase-2/review-export-${width}-${browserName}.png`,
  147 |     });
  148 |     await page.getByRole("button", { name: "Cancel", exact: true }).click();
  149 |     expect(exportsDownloaded).toBe(0);
  150 |     await expect(page.getByRole("dialog", { name: "Export chat" })).toHaveCount(
  151 |       0,
  152 |     );
  153 |     if (width < 640)
  154 |       await page.getByRole("button", { name: "Open sidebar" }).click();
  155 |     await actions.click();
  156 |     await page.getByRole("menuitem", { name: "Export Markdown" }).click();
  157 |     const markdownReady = page.waitForEvent("download");
  158 |     await page.getByRole("link", { name: "Download", exact: true }).click();
  159 |     const markdown = await markdownReady;
  160 |     expect(markdown.suggestedFilename()).toBe(original + ".md");
  161 |     expect(await readFile((await markdown.path())!, "utf8")).toContain(
  162 |       original,
  163 |     );
  164 |     await expect(
  165 |       page.getByRole("dialog", { name: "Export chat" }),
  166 |     ).toBeVisible();
  167 |     await page.getByRole("button", { name: "Cancel", exact: true }).click();
  168 |     await expect(page.getByRole("dialog", { name: "Export chat" })).toHaveCount(
  169 |       0,
  170 |     );
  171 |     if (width < 640)
  172 |       await page.getByRole("button", { name: "Open sidebar" }).click();
  173 |     await actions.click();
```