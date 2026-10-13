# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: actions.spec.ts >> branches and history actions 390
- Location: tests/actions.spec.ts:5:3

# Error details

```
Error: expect(locator).toContainText(expected) failed

Locator: getByRole('button', { name: 'Choose model' })
Expected substring: "fake-chat"
Received string:    "Choose model"
Timeout: 5000ms

Call log:
  - Expect "toContainText" getByRole('button', { name: 'Choose model' }) with timeout 5000ms
  - waiting for getByRole('button', { name: 'Choose model' })
    14 × locator resolved to <button data-slot="button" data-size="default" data-variant="ghost" aria-label="Choose model" class="inline-flex shrink-0 items-center justify-center rounded-md text-sm font-medium whitespace-nowrap outline-none disabled:pointer-events-none disabled:opacity-50 aria-invalid:border-destructive aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-4 hover:bg-accent hover:text-accent-foreground dark:hover:bg-a…>…</button>
       - unexpected value "Choose model"

```

```yaml
- button "Choose model"
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
> 37  |     ).toContainText("fake-chat");
      |       ^ Error: expect(locator).toContainText(expected) failed
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
  73  |       .click();
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
```