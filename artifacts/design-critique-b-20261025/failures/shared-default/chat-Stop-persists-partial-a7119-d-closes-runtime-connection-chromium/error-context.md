# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: chat.spec.ts >> Stop persists partial text and closes runtime connection
- Location: tests/chat.spec.ts:61:1

# Error details

```
Error: expect(locator).toContainText(expected) failed

Locator: getByRole('button', { name: 'Choose model' })
Expected substring: "fake-chat"
Received string:    "○fake-reasoningFake runtime"
Timeout: 5000ms

Call log:
  - Expect "toContainText" getByRole('button', { name: 'Choose model' }) with timeout 5000ms
  - waiting for getByRole('button', { name: 'Choose model' })
    14 × locator resolved to <button type="button" data-size="default" data-state="closed" data-variant="ghost" aria-expanded="false" aria-haspopup="dialog" aria-label="Choose model" data-slot="popover-trigger" title="Not loaded · loads on send" class="inline-flex shrink-0 items-center justify-center rounded-md text-sm font-medium whitespace-nowrap outline-none disabled:pointer-events-none disabled:opacity-50 aria-invalid:border-destructive aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 [&_svg]:pointer-eve…>…</button>
       - unexpected value "○fake-reasoningFake runtime"

```

```yaml
- button "Choose model": fake-reasoning Fake runtime
```

# Test source

```ts
  1   | import { settle } from "./helpers";
  2   | import { test, expect } from "@playwright/test";
  3   | import AxeBuilder from "@axe-core/playwright";
  4   | import { mkdir, writeFile } from "node:fs/promises";
  5   | import { gzipSync } from "node:zlib";
  6   | const dir = "../artifacts/phase-1";
  7   | async function send(page: import("@playwright/test").Page, text: string) {
  8   |   await page.goto("/");
  9   |   await expect(
  10  |     page.getByRole("button", { name: "Choose model" }),
> 11  |   ).toContainText("fake-chat");
      |     ^ Error: expect(locator).toContainText(expected) failed
  12  |   await page.locator(".composer textarea").fill(text);
  13  |   await page.getByRole("button", { name: "Send message" }).click();
  14  |   await expect(page).toHaveURL(/\/c\//);
  15  | }
  16  | for (const width of [320, 390, 768, 1440])
  17  |   for (const theme of ["light", "dark"])
  18  |     test(`live chat ${width} ${theme}`, async ({ page, request }) => {
  19  |       await request.patch("/api/settings", {
  20  |         data: { "appearance.theme": theme },
  21  |       });
  22  |       await page.setViewportSize({ width, height: width < 640 ? 844 : 900 });
  23  |       await page.addInitScript(
  24  |         (value) => localStorage.setItem("workbench-theme", value),
  25  |         theme,
  26  |       );
  27  |       await send(page, "Hello from the browser");
  28  |       await expect(
  29  |         page.getByText("Fake runtime reply.", { exact: false }),
  30  |       ).toBeVisible();
  31  |       await expect(
  32  |         page.getByRole("button", { name: "Stop generating" }),
  33  |       ).not.toBeVisible();
  34  |       expect(
  35  |         await page.evaluate(
  36  |           () => document.documentElement.scrollWidth <= innerWidth,
  37  |         ),
  38  |       ).toBeTruthy();
  39  |       const thread = await page.getByTestId("thread").boundingBox(),
  40  |         composer = await page.getByTestId("composer-row").boundingBox();
  41  |       expect(thread!.y + thread!.height).toBeLessThanOrEqual(composer!.y + 1);
  42  |       await mkdir(dir, { recursive: true });
  43  |       await settle(page);
  44  |       await page.screenshot({
  45  |         path: `${dir}/chat-${width}-${theme}-fake-runtime.png`,
  46  |       });
  47  |       await settle(page);
  48  |       const result = await new AxeBuilder({ page }).analyze();
  49  |       expect(
  50  |         result.violations.filter((v) =>
  51  |           ["serious", "critical"].includes(v.impact ?? ""),
  52  |         ),
  53  |       ).toEqual([]);
  54  |       await page.reload();
  55  |       await expect(
  56  |         page
  57  |           .getByRole("article", { name: "user message" })
  58  |           .getByText("Hello from the browser", { exact: true }),
  59  |       ).toBeVisible();
  60  |     });
  61  | test("Stop persists partial text and closes runtime connection", async ({
  62  |   page,
  63  |   request,
  64  | }) => {
  65  |   const before = (
  66  |     await (await request.get("http://127.0.0.1:18080/tests/state")).json()
  67  |   ).disconnected;
  68  |   await send(page, "#long:500 #slow:50");
  69  |   await expect(page.getByText(/token0 token1/)).toBeVisible();
  70  |   await page.getByRole("button", { name: "Stop generating" }).click();
  71  |   await expect(
  72  |     page
  73  |       .locator('[data-slot="reply-outcome"]')
  74  |       .getByRole("status")
  75  |       .filter({ hasText: /^Stopped$/ }),
  76  |   ).toBeVisible();
  77  |   await expect
  78  |     .poll(
  79  |       async () =>
  80  |         (await (await request.get("http://127.0.0.1:18080/tests/state")).json())
  81  |           .disconnected,
  82  |     )
  83  |     .toBeGreaterThan(before);
  84  |   const text = await page.locator(".prose-answer").innerText();
  85  |   await page.reload();
  86  |   await expect(page.locator(".prose-answer")).toHaveText(text);
  87  | });
  88  | test("close tab and reopen after 20 seconds resumes exactly", async ({
  89  |   page,
  90  |   context,
  91  |   request,
  92  | }) => {
  93  |   test.setTimeout(65000);
  94  |   await send(page, "#long:350 #slow:10");
  95  |   await expect(page.getByText(/token0 token1/)).toBeVisible();
  96  |   const url = page.url();
  97  |   await page.close();
  98  |   await new Promise((resolve) => setTimeout(resolve, 20000));
  99  |   const reopened = await context.newPage();
  100 |   await reopened.goto(url);
  101 |   await expect(
  102 |     reopened.getByRole("button", { name: "Stop generating" }),
  103 |   ).toBeVisible();
  104 |   await expect(
  105 |     reopened.getByRole("button", { name: "Stop generating" }),
  106 |   ).not.toBeVisible({ timeout: 25000 });
  107 |   const data = await (
  108 |     await request.get("/api/chats/" + url.split("/").pop())
  109 |   ).json();
  110 |   expect(await reopened.locator(".prose-answer").innerText()).toBe(
  111 |     data.messages.findLast((m: { role: string }) => m.role === "assistant")
```