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

Expected: 39.51336669921875
Received: 39.96905517578125
```

# Page snapshot

```yaml
- generic [ref=e2]:
  - main [ref=e4]:
    - generic [ref=e5]:
      - generic [ref=e6]:
        - button "Open sidebar" [ref=e7] [cursor=pointer]
        - button "Choose model" [ref=e9] [cursor=pointer]:
          - generic [aria-hidden] [ref=e10]: ●
          - generic [ref=e11]: fake-chat
      - generic [ref=e12]:
        - button "Chat controls" [ref=e13] [cursor=pointer]
        - button "Chat actions" [ref=e14] [cursor=pointer]
    - main [ref=e16]:
      - heading "Working indicator" [level=1] [ref=e17]
      - paragraph [ref=e18]: Synthetic states, rendered by the production chat components. No model requests.
      - generic [ref=e19]:
        - button "Preview Waiting" [ref=e20] [cursor=pointer]
        - button "Preview Queued" [ref=e21] [cursor=pointer]
        - button "Preview Loading" [ref=e22] [cursor=pointer]
        - button "Preview Web search" [ref=e23] [cursor=pointer]
        - button "Preview Reading pages" [ref=e24] [cursor=pointer]
        - button "Preview Library search" [ref=e25] [cursor=pointer]
        - button "Preview Thinking" [ref=e26] [cursor=pointer]
        - button "Preview Answer" [ref=e27] [cursor=pointer]
        - button "Preview Complete" [ref=e28] [cursor=pointer]
        - button "Preview Stopped" [ref=e29] [cursor=pointer]
        - button "Preview Error" [ref=e30] [cursor=pointer]
        - button "Append thought" [ref=e31] [cursor=pointer]
        - button "Restart clock" [ref=e32] [cursor=pointer]
      - generic "Preview preferences" [ref=e33]:
        - button "Toggle theme" [ref=e34] [cursor=pointer]
        - button "Plain status" [ref=e35] [cursor=pointer]
        - button "Reduce motion" [ref=e36] [cursor=pointer]
      - generic [ref=e37]:
        - status [ref=e38]
        - log "Conversation" [ref=e39]:
          - article "assistant message" [ref=e41]:
            - heading "fake-chat replied" [level=2] [ref=e42]
            - paragraph [ref=e43]: Fake runtime · fake-chat
            - generic [ref=e45]:
              - status [ref=e46]: Thinking
              - button "Show thinking" [ref=e47] [cursor=pointer]:
                - generic [ref=e48]: Thinking
                - generic [ref=e58]: "…Synthetic reasoning line 40: preserve the source and inspect the context. Newest synthetic reasoning: compare the original evidence and preserve its wording."
            - status [ref=e59]
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
  57  |   await settle(page);
  58  |   const before = await ticker.boundingBox();
  59  |   await page.getByRole("button", { name: "Append thought" }).click();
  60  |   await expect(ticker).toContainText("Newest synthetic reasoning");
  61  |   expect((await ticker.textContent())!.length).toBeLessThanOrEqual(161);
> 62  |   const after = await ticker.boundingBox();
      |                         ^ Error: expect(received).toBe(expected) // Object.is equality
  63  |   expect(after!.height).toBe(before!.height);
  64  |   expect(after!.y).toBe(before!.y);
  65  |   await toggle.click();
  66  |   const full = page.getByRole("region", { name: "Model reasoning" });
  67  |   await expect(full).toBeVisible();
  68  |   await settle(page);
  69  |   await expect
  70  |     .poll(() =>
  71  |       full.evaluate((el) => el.scrollHeight - el.clientHeight - el.scrollTop),
  72  |     )
  73  |     .toBeLessThan(3);
  74  |   await full.evaluate((el) => {
  75  |     el.scrollTop = 0;
  76  |     el.dispatchEvent(new Event("scroll", { bubbles: true }));
  77  |   });
  78  |   await page.getByRole("button", { name: "Append thought" }).click();
  79  |   expect(await full.evaluate((el) => el.scrollTop)).toBe(0);
  80  |   await page.getByRole("button", { name: "Hide thinking" }).click();
  81  |   await page.getByRole("button", { name: "Show thinking" }).click();
  82  |   await settle(page);
  83  |   await expect
  84  |     .poll(() =>
  85  |       full.evaluate((el) => el.scrollHeight - el.clientHeight - el.scrollTop),
  86  |     )
  87  |     .toBeLessThan(3);
  88  |   await page
  89  |     .getByRole("button", { name: "Preview Answer", exact: true })
  90  |     .click();
  91  |   await expect(
  92  |     page.getByRole("button", { name: "Thought for 12 s" }),
  93  |   ).toHaveAttribute("data-state", "closed");
  94  |   await expect(line(page)).toHaveCount(0);
  95  |   await expect(
  96  |     page.getByRole("region", { name: "Model reasoning" }),
  97  |   ).toHaveCount(0);
  98  |   await page.getByRole("button", { name: "Thought for 12 s" }).click();
  99  |   await expect(full).toContainText("Synthetic reasoning line 1:");
  100 |   await expect(full).toContainText("Newest synthetic reasoning");
  101 | });
  102 | 
  103 | for (const mode of ["always", "system"] as const)
  104 |   test(`indicator motion is static for ${mode}, while words still change`, async ({
  105 |     page,
  106 |   }) => {
  107 |     await page.clock.install();
  108 |     await page.emulateMedia({
  109 |       reducedMotion: mode === "system" ? "reduce" : "no-preference",
  110 |     });
  111 |     await preview(page);
  112 |     if (mode === "always")
  113 |       await page.getByRole("button", { name: "Reduce motion" }).click();
  114 |     const first = await word(page).textContent();
  115 |     await page.clock.runFor(2800);
  116 |     await expect(word(page)).not.toHaveText(first!);
  117 |     const styles = await line(page).evaluate((el) => {
  118 |       const mark = el.querySelector(".mark-a")!,
  119 |         dot = el.querySelector(".mark-dot")!,
  120 |         text = el.querySelector(".word-in")!;
  121 |       return [mark, dot, text].map((node) => ({
  122 |         animation: getComputedStyle(node).animationName,
  123 |         opacity: getComputedStyle(node).opacity,
  124 |         transform: getComputedStyle(node).transform,
  125 |       }));
  126 |     });
  127 |     for (const style of styles)
  128 |       expect(style).toMatchObject({
  129 |         animation: "none",
  130 |         opacity: "1",
  131 |         transform: "none",
  132 |       });
  133 |     await page
  134 |       .getByRole("button", { name: "Preview Thinking", exact: true })
  135 |       .click();
  136 |     expect(
  137 |       await page
  138 |         .locator(".mark-dot")
  139 |         .evaluate((el) => getComputedStyle(el).animationName),
  140 |     ).toBe("none");
  141 |   });
  142 | 
  143 | for (const width of [390, 1440])
  144 |   for (const theme of ["dark", "light"])
  145 |     test(`indicator production states ${width} ${theme}`, async ({ page }) => {
  146 |       await page.setViewportSize({ width, height: width === 390 ? 844 : 900 });
  147 |       await page.addInitScript(
  148 |         (value) => localStorage.setItem("workbench-theme", value),
  149 |         theme,
  150 |       );
  151 |       await preview(page);
  152 |       await mkdir(dir, { recursive: true });
  153 |       const checks: unknown[] = [];
  154 |       for (const state of [
  155 |         "Waiting",
  156 |         "Queued",
  157 |         "Loading",
  158 |         "Web search",
  159 |         "Reading pages",
  160 |         "Library search",
  161 |         "Thinking",
  162 |         "Answer",
```