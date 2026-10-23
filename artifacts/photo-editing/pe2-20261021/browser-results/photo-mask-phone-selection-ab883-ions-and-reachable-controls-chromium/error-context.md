# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: photo-mask.spec.ts >> phone selection layout dark preserves canvas proportions and reachable controls
- Location: tests/photo-mask.spec.ts:137:3

# Error details

```
Error: expect(locator).toBeEnabled() failed

Locator:  getByRole('dialog', { name: 'Select edit area', exact: true }).getByRole('button', { name: 'Use selection' })
Expected: enabled
Received: disabled
Timeout:  5000ms

Call log:
  - Expect "toBeEnabled" getByRole('dialog', { name: 'Select edit area', exact: true }).getByRole('button', { name: 'Use selection' }) with timeout 5000ms
  - waiting for getByRole('dialog', { name: 'Select edit area', exact: true }).getByRole('button', { name: 'Use selection' })
    10 × locator resolved to <button disabled data-slot="button" data-size="default" data-variant="default" class="inline-flex shrink-0 items-center justify-center gap-2 rounded-md text-sm font-medium whitespace-nowrap outline-none disabled:pointer-events-none disabled:opacity-50 aria-invalid:border-destructive aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-4 bg-primary text-primary-foreground hover:bg-primary/90 h-9 px-4 py-2 …>Use selection</button>
       - unexpected value "disabled"

```

```yaml
- button "Use selection" [disabled]
```

# Test source

```ts
  54  |     "unselected pixels are preserved",
  55  |   );
  56  |   await page
  57  |     .getByRole("textbox", { name: "Photo edit instruction" })
  58  |     .fill("Synthetic selected change");
  59  |   const bodies: Record<string, unknown>[] = [];
  60  |   await page.route("**/api/chats/*/images", async (route) => {
  61  |     bodies.push(route.request().postDataJSON());
  62  |     if (bodies.length === 1)
  63  |       await route.fulfill({
  64  |         status: 409,
  65  |         contentType: "application/json",
  66  |         body: JSON.stringify({
  67  |           error: { code: "image_capacity", message: "Synthetic rejection" },
  68  |         }),
  69  |       });
  70  |     else await route.continue();
  71  |   });
  72  |   await page.getByRole("button", { name: "Edit photo", exact: true }).click();
  73  |   await expect(page.getByRole("alert")).toContainText("Synthetic rejection");
  74  |   await expect(
  75  |     page.getByRole("button", { name: "Change selection", exact: true }),
  76  |   ).toBeVisible();
  77  |   await page.getByRole("button", { name: "Edit photo", exact: true }).click();
  78  |   await expect(
  79  |     page.getByRole("button", { name: "Open image 1", exact: true }),
  80  |   ).toBeVisible();
  81  |   expect(bodies).toHaveLength(2);
  82  |   expect(bodies[0]).toEqual(bodies[1]);
  83  |   const selection = bodies[0].selection as {
  84  |     version: number;
  85  |     strokes: { points: number[][] }[];
  86  |   };
  87  |   expect(selection.version).toBe(1);
  88  |   expect(selection.strokes[0].points.length).toBeGreaterThan(1);
  89  |   const retry = page.waitForResponse((r) => r.url().endsWith("/images/retry"));
  90  |   await page.getByRole("button", { name: "Try again", exact: true }).click();
  91  |   expect((await (await retry).json()).assistant.images[0].selection).toEqual(
  92  |     selection,
  93  |   );
  94  | });
  95  | 
  96  | test("Undo, Clear, Cancel and keyboard selection keep the intended draft", async ({
  97  |   page,
  98  | }) => {
  99  |   await ready(page);
  100 |   await page
  101 |     .getByRole("button", { name: "Select edit area", exact: true })
  102 |     .click();
  103 |   let dialog = page.getByRole("dialog", {
  104 |     name: "Select edit area",
  105 |     exact: true,
  106 |   });
  107 |   await expect(
  108 |     dialog.getByRole("button", { name: "Use selection" }),
  109 |   ).toBeDisabled();
  110 |   await brush(page);
  111 |   await dialog.getByRole("button", { name: "Undo", exact: true }).click();
  112 |   await expect(dialog).toContainText("No area selected");
  113 |   const canvas = dialog.getByRole("img", { name: /^Photo selection canvas/ });
  114 |   await canvas.focus();
  115 |   await page.keyboard.press("ArrowRight");
  116 |   await page.keyboard.press("Space");
  117 |   await expect(dialog).toContainText("1 brush strokes");
  118 |   await dialog.getByRole("button", { name: "Clear", exact: true }).click();
  119 |   await expect(
  120 |     dialog.getByRole("button", { name: "Use selection" }),
  121 |   ).toBeDisabled();
  122 |   await brush(page);
  123 |   await dialog.getByRole("button", { name: "Cancel", exact: true }).click();
  124 |   await expect(
  125 |     page.getByRole("button", { name: "Select edit area", exact: true }),
  126 |   ).toBeVisible();
  127 |   await page
  128 |     .getByRole("button", { name: "Select edit area", exact: true })
  129 |     .click();
  130 |   dialog = page.getByRole("dialog", { name: "Select edit area", exact: true });
  131 |   await expect(dialog).toContainText("No area selected");
  132 |   await page.keyboard.press("Escape");
  133 |   await expect(dialog).toHaveCount(0);
  134 | });
  135 | 
  136 | for (const theme of ["light", "dark"])
  137 |   test(`phone selection layout ${theme} preserves canvas proportions and reachable controls`, async ({
  138 |     page,
  139 |     browserName,
  140 |   }) => {
  141 |     await page.setViewportSize({ width: 390, height: 750 });
  142 |     await page.goto("/design?photo-edit&state=selection");
  143 |     await page.getByRole("button", { name: theme, exact: true }).click();
  144 |     await page
  145 |       .getByRole("button", { name: "Change selection", exact: true })
  146 |       .click();
  147 |     const dialog = page.getByRole("dialog", {
  148 |       name: "Select edit area",
  149 |       exact: true,
  150 |     });
  151 |     const canvas = dialog.getByRole("img", { name: /^Photo selection canvas/ });
  152 |     await expect(
  153 |       dialog.getByRole("button", { name: "Use selection" }),
> 154 |     ).toBeEnabled();
      |       ^ Error: expect(locator).toBeEnabled() failed
  155 |     const bounds = (await canvas.boundingBox())!;
  156 |     expect(bounds.width / bounds.height).toBeCloseTo(720 / 900, 2);
  157 |     for (const label of ["Undo", "Clear", "Cancel", "Use selection"]) {
  158 |       const button = dialog.getByRole("button", { name: label, exact: true });
  159 |       await button.scrollIntoViewIfNeeded();
  160 |       const box = (await button.boundingBox())!;
  161 |       expect(box.x).toBeGreaterThanOrEqual(0);
  162 |       expect(box.x + box.width).toBeLessThanOrEqual(390);
  163 |       expect(box.y + box.height).toBeLessThanOrEqual(750);
  164 |     }
  165 |     await mkdir(directory, { recursive: true });
  166 |     await page.screenshot({
  167 |       path: `${directory}/mask-390-${theme}-${browserName}.png`,
  168 |     });
  169 |   });
  170 | 
```