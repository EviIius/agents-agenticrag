# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: working-indicator.spec.ts >> ticker keeps geometry, expands the original text, follows until manual scrolling and closes on answer
- Location: tests/working-indicator.spec.ts:44:1

# Error details

```
Error: expect(received).toBe(expected) // Object.is equality

Expected: 19.600006103515625
Received: 19.920318603515625
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
            - /url: /design/chat
        - navigation "Chat history" [ref=e10]:
          - navigation "Workspace" [ref=e11]:
            - link "Workflows" [ref=e13] [cursor=pointer]:
              - /url: /workflows
            - link "Images" [ref=e19] [cursor=pointer]:
              - /url: /images
          - paragraph [ref=e25]: TODAY
          - link "A clearer way to learn" [ref=e27] [cursor=pointer]:
            - /url: /design/chat/fixture
          - link "Planning a weekend" [ref=e34] [cursor=pointer]:
            - /url: /design/chat/fixture
          - link "Understanding a short function" [ref=e41] [cursor=pointer]:
            - /url: /design/chat/fixture
          - link "Making a useful checklist" [ref=e48] [cursor=pointer]:
            - /url: /design/chat/fixture
          - paragraph [ref=e54]: YESTERDAY
          - link "A fresh perspective" [ref=e55] [cursor=pointer]:
            - /url: /design/chat/fixture
        - button "Settings" [ref=e59] [cursor=pointer]
    - main [ref=e60]:
      - generic [ref=e61]:
        - button "Choose model" [ref=e63] [cursor=pointer]:
          - generic [aria-hidden] [ref=e64]: ●
          - generic [ref=e65]: fake-chat
        - generic [ref=e66]: A clearer way to learn
        - generic [ref=e67]:
          - button "Chat controls" [ref=e68] [cursor=pointer]
          - button "Chat actions" [ref=e69] [cursor=pointer]
      - main [ref=e71]:
        - heading "Working indicator" [level=1] [ref=e72]
        - paragraph [ref=e73]: Synthetic states, rendered by the production chat components. No model requests.
        - generic [ref=e74]:
          - button "Preview Waiting" [ref=e75] [cursor=pointer]
          - button "Preview Queued" [ref=e76] [cursor=pointer]
          - button "Preview Loading" [ref=e77] [cursor=pointer]
          - button "Preview Web search" [ref=e78] [cursor=pointer]
          - button "Preview Reading pages" [ref=e79] [cursor=pointer]
          - button "Preview Library search" [ref=e80] [cursor=pointer]
          - button "Preview Thinking" [ref=e81] [cursor=pointer]
          - button "Preview Answer" [ref=e82] [cursor=pointer]
          - button "Preview Complete" [ref=e83] [cursor=pointer]
          - button "Preview Stopped" [ref=e84] [cursor=pointer]
          - button "Preview Error" [ref=e85] [cursor=pointer]
          - button "Append thought" [active] [ref=e86] [cursor=pointer]
          - button "Restart clock" [ref=e87] [cursor=pointer]
        - generic "Preview preferences" [ref=e88]:
          - button "Toggle theme" [ref=e89] [cursor=pointer]
          - button "Plain status" [ref=e90] [cursor=pointer]
          - button "Reduce motion" [ref=e91] [cursor=pointer]
        - generic [ref=e92]:
          - status [ref=e93]
          - log "Conversation" [ref=e94]:
            - article "assistant message" [ref=e96]:
              - heading "fake-chat replied" [level=2] [ref=e97]
              - paragraph [ref=e98]: Fake runtime · fake-chat
              - generic [ref=e100]:
                - status [ref=e101]: Thinking
                - button "Show thinking" [ref=e102] [cursor=pointer]:
                  - generic [ref=e103]: Thinking
                  - generic [ref=e113]: "…Synthetic reasoning line 40: preserve the source and inspect the context. Newest synthetic reasoning: compare the original evidence and preserve its wording."
              - status [ref=e114]
  - region "Notifications alt+T"
```

# Test source

```ts
  1   | import { test, expect, type Page } from "@playwright/test";
  2   | import AxeBuilder from "@axe-core/playwright";
  3   | import { mkdir, writeFile } from "node:fs/promises";
  4   | import { settle } from "./helpers";
  5   | 
  6   | const dir = "../artifacts/chat-images/ci-a/browser";
  7   | test.use({ video: { mode: "on" } });
  8   | const line = (page: Page) =>
  9   |   page.locator('[data-slot="working-line"][data-state="open"]');
  10  | const word = (page: Page) => line(page).locator(".word-in");
  11  | async function preview(page: Page) {
  12  |   await page.goto("/design?indicator");
  13  |   await expect(
  14  |     page.getByRole("heading", { name: "Working indicator" }),
  15  |   ).toBeVisible();
  16  | }
  17  | 
  18  | test("seeded words change at 2.4 seconds while phase announcements stay quiet; Plain persists", async ({
  19  |   page,
  20  | }) => {
  21  |   await page.clock.install();
  22  |   await preview(page);
  23  |   await page.getByRole("button", { name: "Restart clock" }).click();
  24  |   const first = await word(page).textContent();
  25  |   await page.clock.runFor(2200);
  26  |   await expect(word(page)).toHaveText(first!);
  27  |   await page.clock.runFor(400);
  28  |   await expect(word(page)).not.toHaveText(first!);
  29  |   await expect(line(page).getByRole("status")).toHaveText("Working");
  30  |   await page.getByRole("button", { name: "Plain status" }).click();
  31  |   await expect(word(page)).toHaveText("Working");
  32  |   await page.clock.runFor(5000);
  33  |   await expect(word(page)).toHaveText("Working");
  34  |   await page.reload();
  35  |   await expect(word(page)).toHaveText("Working");
  36  |   await page
  37  |     .getByRole("button", { name: "Preview Queued", exact: true })
  38  |     .click();
  39  |   await expect(word(page)).toHaveText(
  40  |     "Waiting for Fake runtime · fake-chat · #2 in line",
  41  |   );
  42  | });
  43  | 
  44  | test("ticker keeps geometry, expands the original text, follows until manual scrolling and closes on answer", async ({
  45  |   page,
  46  | }) => {
  47  |   await preview(page);
  48  |   await page
  49  |     .getByRole("button", { name: "Preview Thinking", exact: true })
  50  |     .click();
  51  |   const toggle = page.getByRole("button", { name: "Show thinking" });
  52  |   await expect(toggle).toHaveAttribute("aria-expanded", "false");
  53  |   await expect(
  54  |     page.getByRole("region", { name: "Model reasoning" }),
  55  |   ).toHaveCount(0);
  56  |   const ticker = page.locator(".thought-ticker");
  57  |   const before = await ticker.boundingBox();
  58  |   await page.getByRole("button", { name: "Append thought" }).click();
  59  |   await expect(ticker).toContainText("Newest synthetic reasoning");
  60  |   expect((await ticker.textContent())!.length).toBeLessThanOrEqual(161);
  61  |   const after = await ticker.boundingBox();
> 62  |   expect(after!.height).toBe(before!.height);
      |                         ^ Error: expect(received).toBe(expected) // Object.is equality
  63  |   expect(after!.y).toBe(before!.y);
  64  |   await toggle.click();
  65  |   const full = page.getByRole("region", { name: "Model reasoning" });
  66  |   await expect(full).toBeVisible();
  67  |   await settle(page);
  68  |   await expect
  69  |     .poll(() =>
  70  |       full.evaluate((el) => el.scrollHeight - el.clientHeight - el.scrollTop),
  71  |     )
  72  |     .toBeLessThan(3);
  73  |   await full.evaluate((el) => {
  74  |     el.scrollTop = 0;
  75  |     el.dispatchEvent(new Event("scroll", { bubbles: true }));
  76  |   });
  77  |   await page.getByRole("button", { name: "Append thought" }).click();
  78  |   expect(await full.evaluate((el) => el.scrollTop)).toBe(0);
  79  |   await page.getByRole("button", { name: "Hide thinking" }).click();
  80  |   await page.getByRole("button", { name: "Show thinking" }).click();
  81  |   await settle(page);
  82  |   await expect
  83  |     .poll(() =>
  84  |       full.evaluate((el) => el.scrollHeight - el.clientHeight - el.scrollTop),
  85  |     )
  86  |     .toBeLessThan(3);
  87  |   await page
  88  |     .getByRole("button", { name: "Preview Answer", exact: true })
  89  |     .click();
  90  |   await expect(
  91  |     page.getByRole("button", { name: "Thought for 12 s" }),
  92  |   ).toHaveAttribute("data-state", "closed");
  93  |   await expect(line(page)).toHaveCount(0);
  94  |   await expect(
  95  |     page.getByRole("region", { name: "Model reasoning" }),
  96  |   ).toHaveCount(0);
  97  |   await page.getByRole("button", { name: "Thought for 12 s" }).click();
  98  |   await expect(full).toContainText("Synthetic reasoning line 1:");
  99  |   await expect(full).toContainText("Newest synthetic reasoning");
  100 | });
  101 | 
  102 | for (const mode of ["always", "system"] as const)
  103 |   test(`indicator motion is static for ${mode}, while words still change`, async ({
  104 |     page,
  105 |   }) => {
  106 |     await page.clock.install();
  107 |     await page.emulateMedia({
  108 |       reducedMotion: mode === "system" ? "reduce" : "no-preference",
  109 |     });
  110 |     await preview(page);
  111 |     if (mode === "always")
  112 |       await page.getByRole("button", { name: "Reduce motion" }).click();
  113 |     const first = await word(page).textContent();
  114 |     await page.clock.runFor(2800);
  115 |     await expect(word(page)).not.toHaveText(first!);
  116 |     const styles = await line(page).evaluate((el) => {
  117 |       const mark = el.querySelector(".mark-a")!,
  118 |         dot = el.querySelector(".mark-dot")!,
  119 |         text = el.querySelector(".word-in")!;
  120 |       return [mark, dot, text].map((node) => ({
  121 |         animation: getComputedStyle(node).animationName,
  122 |         opacity: getComputedStyle(node).opacity,
  123 |         transform: getComputedStyle(node).transform,
  124 |       }));
  125 |     });
  126 |     for (const style of styles)
  127 |       expect(style).toMatchObject({
  128 |         animation: "none",
  129 |         opacity: "1",
  130 |         transform: "none",
  131 |       });
  132 |     await page
  133 |       .getByRole("button", { name: "Preview Thinking", exact: true })
  134 |       .click();
  135 |     expect(
  136 |       await page
  137 |         .locator(".mark-dot")
  138 |         .evaluate((el) => getComputedStyle(el).animationName),
  139 |     ).toBe("none");
  140 |   });
  141 | 
  142 | for (const width of [390, 1440])
  143 |   for (const theme of ["dark", "light"])
  144 |     test(`indicator production states ${width} ${theme}`, async ({ page }) => {
  145 |       await page.setViewportSize({ width, height: width === 390 ? 844 : 900 });
  146 |       await page.addInitScript(
  147 |         (value) => localStorage.setItem("workbench-theme", value),
  148 |         theme,
  149 |       );
  150 |       await preview(page);
  151 |       await mkdir(dir, { recursive: true });
  152 |       const checks: unknown[] = [];
  153 |       for (const state of [
  154 |         "Waiting",
  155 |         "Queued",
  156 |         "Loading",
  157 |         "Web search",
  158 |         "Reading pages",
  159 |         "Library search",
  160 |         "Thinking",
  161 |         "Answer",
  162 |         "Complete",
```