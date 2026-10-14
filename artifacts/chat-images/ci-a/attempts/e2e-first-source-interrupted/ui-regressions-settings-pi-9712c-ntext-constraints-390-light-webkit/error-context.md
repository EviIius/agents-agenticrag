# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: ui-regressions.spec.ts >> settings, picker focus and context constraints 390 light
- Location: tests/ui-regressions.spec.ts:8:5

# Error details

```
Error: locator.click: Test ended.
Call log:
  - waiting for getByRole('button', { name: 'Choose model' })
    - locator resolved to <button data-slot="button" data-size="default" data-variant="ghost" aria-label="Choose model" class="inline-flex shrink-0 items-center justify-center rounded-md text-sm font-medium whitespace-nowrap outline-none disabled:pointer-events-none disabled:opacity-50 aria-invalid:border-destructive aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-4 hover:bg-accent hover:text-accent-foreground dark:hover:bg-a…>…</button>
  - attempting click action
    2 × waiting for element to be visible, enabled and stable
      - element is not stable
    - retrying click action
    - waiting 20ms
    - waiting for element to be visible, enabled and stable
    - element is not stable
  - retrying click action
    - waiting 100ms
    - waiting for element to be visible, enabled and stable
    - element is visible, enabled and stable
    - scrolling into view if needed
    - done scrolling
    - <li tabindex="0" data-index="0" class="font-sans" data-front="true" data-styled="true" data-mounted="true" data-swiped="false" data-visible="true" data-sonner-toast="" data-promise="false" data-removed="false" data-swiping="false" data-y-position="top" data-expanded="false" data-swipe-out="false" data-dismissible="true" data-x-position="center">…</li> from <section tabindex="-1" aria-live="polite" aria-atomic="false" aria-relevant="additions text" aria-label="Notifications alt+T" data-react-aria-top-layer="true">…</section> subtree intercepts pointer events
  - retrying click action
    - waiting 100ms

```

# Test source

```ts
  1   | import { settle } from "./helpers";
  2   | import { test, expect } from "@playwright/test";
  3   | import AxeBuilder from "@axe-core/playwright";
  4   | import { mkdir } from "node:fs/promises";
  5   | 
  6   | for (const width of [320, 390, 768, 1440]) {
  7   |   for (const theme of ["light", "dark"]) {
  8   |     test(`settings, picker focus and context constraints ${width} ${theme}`, async ({
  9   |       page,
  10  |       request,
  11  |     }) => {
  12  |       const connection = (
  13  |         await (await request.get("/api/connections")).json()
  14  |       )[0];
  15  |       await request.patch("/api/settings", {
  16  |         data: {
  17  |           default_connection_id: connection.id,
  18  |           default_model_id: "fake-chat",
  19  |           "appearance.theme": theme,
  20  |         },
  21  |       });
  22  |       await request.put("/api/models/prefs", {
  23  |         data: {
  24  |           connection_id: connection.id,
  25  |           model_id: "fake-chat",
  26  |           context_length: 16384,
  27  |         },
  28  |       });
  29  |       await page.setViewportSize({ width, height: 844 });
  30  |       await page.goto("/");
  31  |       if (width < 640)
  32  |         await page.evaluate(() => {
  33  |           document.documentElement.style.setProperty("--safe-area-top", "47px");
  34  |           document.documentElement.style.setProperty(
  35  |             "--safe-area-bottom",
  36  |             "34px",
  37  |           );
  38  |         });
> 39  |       await page.getByRole("button", { name: "Choose model" }).click();
      |                                                                ^ Error: locator.click: Test ended.
  40  |       await expect(
  41  |         page.getByRole("option", { name: /fake-chat/ }),
  42  |       ).toBeVisible();
  43  |       await page
  44  |         .locator('[data-slot="drawer-content"]')
  45  |         .evaluateAll(async (elements) => {
  46  |           await Promise.all(
  47  |             elements.flatMap((element) =>
  48  |               element
  49  |                 .getAnimations()
  50  |                 .map((animation) => animation.finished.catch(() => {})),
  51  |             ),
  52  |           );
  53  |         });
  54  |       if (width < 640)
  55  |         await expect(
  56  |           page.getByRole("button", { name: "Close", exact: true }),
  57  |         ).toBeInViewport({ ratio: 1 });
  58  |       const search = page.getByRole("combobox", { name: "Search models" });
  59  |       await search.focus();
  60  |       // Compare one layout snapshot; a bottom sheet can move between separate reads.
  61  |       const bounds = await search.evaluate((input) => {
  62  |         const wrapper = input.closest('[data-slot="command-input-wrapper"]')!;
  63  |         const list = wrapper.parentElement!.querySelector(
  64  |           '[data-slot="command-list"]',
  65  |         )!;
  66  |         const a = input.getBoundingClientRect(),
  67  |           b = wrapper.getBoundingClientRect(),
  68  |           c = list.getBoundingClientRect();
  69  |         return {
  70  |           inputTop: a.top,
  71  |           inputBottom: a.bottom,
  72  |           wrapperTop: b.top,
  73  |           wrapperBottom: b.bottom,
  74  |           listTop: c.top,
  75  |         };
  76  |       });
  77  |       expect(bounds.inputTop).toBeGreaterThanOrEqual(bounds.wrapperTop);
  78  |       expect(bounds.inputBottom).toBeLessThanOrEqual(bounds.wrapperBottom);
  79  |       expect(bounds.wrapperBottom).toBeLessThanOrEqual(bounds.listTop + 1);
  80  |       await mkdir("../artifacts/phase-2", { recursive: true });
  81  |       await settle(page);
  82  |       await page.screenshot({
  83  |         path: `../artifacts/phase-2/review-picker-${width}-${theme}.png`,
  84  |       });
  85  |       if (width < 640)
  86  |         await page.getByRole("button", { name: "Close", exact: true }).click();
  87  |       else await page.keyboard.press("Escape");
  88  |       await page
  89  |         .getByRole("button", { name: "Chat controls", exact: true })
  90  |         .click();
  91  |       const controls = page.getByRole("region", {
  92  |         name: "Chat controls",
  93  |       });
  94  |       await expect(
  95  |         controls.getByRole("button", { name: "64K", exact: true }),
  96  |       ).toHaveCount(0);
  97  |       await expect(
  98  |         controls.getByRole("button", { name: "32K", exact: true }),
  99  |       ).toHaveCount(0);
  100 |       const context = controls.getByRole("spinbutton", {
  101 |         name: "Context length",
  102 |       });
  103 |       await expect(context).toHaveAttribute("max", "16384");
  104 |       await context.fill("65536");
  105 |       await expect(
  106 |         controls.getByRole("button", { name: "Save settings", exact: true }),
  107 |       ).toBeDisabled();
  108 |       await expect(context).toHaveAttribute("aria-invalid", "true");
  109 |       await context.fill("16384");
  110 |       await expect(context).toHaveAttribute("aria-invalid", "false");
  111 |       await expect(
  112 |         controls.getByRole("button", { name: "Save settings", exact: true }),
  113 |       ).toBeDisabled();
  114 |       await context.fill("8192");
  115 |       await expect(
  116 |         controls.getByRole("button", { name: "Apply context length" }),
  117 |       ).toBeEnabled();
  118 |       await page.getByRole("button", { name: "Close chat controls" }).click();
  119 |       await page.keyboard.press("Control+,");
  120 |       const settings = page.getByRole("dialog", {
  121 |         name: "Settings",
  122 |         exact: true,
  123 |       });
  124 |       const close = settings.getByRole("button", { name: "Close settings" });
  125 |       await expect(
  126 |         settings.locator('nav [aria-current="page"]'),
  127 |       ).toBeInViewport({ ratio: 1 });
  128 |       for (const pane of [
  129 |         "Connections",
  130 |         "Models",
  131 |         "Web search",
  132 |         "Transcription",
  133 |         "Appearance",
  134 |         "Data",
  135 |         "Shortcuts",
  136 |         "About",
  137 |       ]) {
  138 |         await settings.getByRole("button", { name: pane, exact: true }).click();
  139 |         await expect(
```