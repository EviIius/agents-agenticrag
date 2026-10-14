# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: deferred-polish.spec.ts >> phone sidebar motion and effective preference always
- Location: tests/deferred-polish.spec.ts:70:3

# Error details

```
Error: locator.click: Test ended.
Call log:
  - waiting for getByRole('dialog', { name: 'Settings', exact: true }).getByRole('button', { name: 'Appearance', exact: true })
    - locator resolved to <button data-slot="button" data-size="default" aria-current="page" data-variant="ghost" class="inline-flex items-center gap-2 rounded-md text-sm font-medium whitespace-nowrap outline-none disabled:pointer-events-none disabled:opacity-50 aria-invalid:border-destructive aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-4 hover:bg-accent hover:text-accent-foreground dark:hover:bg-accent/50 h-9 px-4 py-2 h…>Appearance</button>
  - attempting click action
    - waiting for element to be visible, enabled and stable

```

# Test source

```ts
  29  |         .click();
  30  |       const menu = page.getByRole("menu");
  31  |       await expect(menu).toBeVisible();
  32  |       await settle(page);
  33  |       const box = (await menu.boundingBox())!;
  34  |       expect(box.y).toBeGreaterThanOrEqual(52);
  35  |       expect(box.y + box.height).toBeLessThanOrEqual(height - 42);
  36  |       expect(box.x).toBeGreaterThanOrEqual(24);
  37  |       expect(box.x + box.width).toBeLessThanOrEqual(width - 24);
  38  |       const first = menu.getByRole("menuitem", {
  39  |         name: "Open transcript",
  40  |         exact: true,
  41  |       });
  42  |       const last = menu.getByRole("menuitem", { name: "Remove", exact: true });
  43  |       await last.scrollIntoViewIfNeeded();
  44  |       await expect(last).toBeInViewport({ ratio: 0.99 });
  45  |       await first.scrollIntoViewIfNeeded();
  46  |       await expect(first).toBeInViewport({ ratio: 0.99 });
  47  |       await expect(
  48  |         menu.getByRole("menuitem", { name: "Transcribe again", exact: true }),
  49  |       ).toBeDisabled();
  50  |       await expect(
  51  |         menu.getByText(
  52  |           "Audio removed to save space. Upload it again to transcribe.",
  53  |         ),
  54  |       ).toBeVisible();
  55  |       await page.screenshot({
  56  |         path: `../artifacts/deferred-polish/recording-menu-${width}x${height}-${theme}-${browserName}-fake.png`,
  57  |       });
  58  |       await page.keyboard.press("Escape");
  59  |       await expect(menu).toHaveCount(0);
  60  |       await expect(
  61  |         page.getByRole("button", {
  62  |           name: "Recording actions for Invented lantern recording.wav",
  63  |         }),
  64  |       ).toBeFocused();
  65  |     });
  66  |   }
  67  | }
  68  | 
  69  | for (const mode of ["normal", "always", "system"] as const) {
  70  |   test(`phone sidebar motion and effective preference ${mode}`, async ({
  71  |     page,
  72  |     request,
  73  |     browserName,
  74  |   }) => {
  75  |     await page.setViewportSize({ width: 390, height: 844 });
  76  |     await request.patch("/api/settings", {
  77  |       data: {
  78  |         "appearance.reduce_motion": mode === "always" ? "always" : "system",
  79  |       },
  80  |     });
  81  |     await page.emulateMedia({
  82  |       reducedMotion: mode === "system" ? "reduce" : "no-preference",
  83  |     });
  84  |     await page.addInitScript(() => {
  85  |       Object.defineProperty(window, "sidebarAnimations", { value: [] });
  86  |       document.addEventListener("animationstart", (event) => {
  87  |         if (
  88  |           event.animationName === "sheet-in" ||
  89  |           event.animationName === "sheet-out"
  90  |         )
  91  |           (
  92  |             window as unknown as { sidebarAnimations: string[] }
  93  |           ).sidebarAnimations.push(event.animationName);
  94  |       });
  95  |     });
  96  |     await page.goto("/");
  97  |     await settle(page);
  98  |     await page
  99  |       .getByRole("button", { name: "Open sidebar", exact: true })
  100 |       .click();
  101 |     const sheet = page.getByRole("dialog", {
  102 |       name: "Chat history",
  103 |       exact: true,
  104 |     });
  105 |     await expect(sheet).toBeVisible();
  106 |     await settle(page);
  107 |     expect(
  108 |       await sheet.evaluate((el) => getComputedStyle(el).animationName),
  109 |     ).toBe(mode === "normal" ? "sheet-in" : "none");
  110 |     await sheet
  111 |       .getByRole("button", { name: "Collapse sidebar", exact: true })
  112 |       .click();
  113 |     await expect(sheet).toHaveCount(0);
  114 |     const animations = await page.evaluate(
  115 |       () =>
  116 |         (window as unknown as { sidebarAnimations: string[] })
  117 |           .sidebarAnimations,
  118 |     );
  119 |     expect(animations).toEqual(
  120 |       mode === "normal" ? ["sheet-in", "sheet-out"] : [],
  121 |     );
  122 |     await page.keyboard.press("Control+,");
  123 |     const settings = page.getByRole("dialog", {
  124 |       name: "Settings",
  125 |       exact: true,
  126 |     });
  127 |     await settings
  128 |       .getByRole("button", { name: "Appearance", exact: true })
> 129 |       .click();
      |        ^ Error: locator.click: Test ended.
  130 |     await expect(
  131 |       settings.getByText(
  132 |         mode === "normal"
  133 |           ? "Brief animations are enabled."
  134 |           : mode === "always"
  135 |             ? "Animations are off. Choose Follow system to use your device’s preference."
  136 |             : "Animations are off because Reduce motion is enabled on this device.",
  137 |         { exact: true },
  138 |       ),
  139 |     ).toBeVisible();
  140 |     await settle(page);
  141 |     await page.screenshot({
  142 |       path: `../artifacts/deferred-polish/motion-${mode}-390-${browserName}-fake.png`,
  143 |     });
  144 |     await request.patch("/api/settings", {
  145 |       data: { "appearance.reduce_motion": "system" },
  146 |     });
  147 |   });
  148 | }
  149 | 
  150 | for (const width of [390, 1440]) {
  151 |   test(`picker filters reported capabilities and separates selection from loading ${width}`, async ({
  152 |     page,
  153 |     request,
  154 |     browserName,
  155 |   }) => {
  156 |     await page.setViewportSize({ width, height: 844 });
  157 |     await request.patch("/api/settings", {
  158 |       data: { "appearance.reduce_motion": "system" },
  159 |     });
  160 |     await page.goto("/design");
  161 |     const picker = page
  162 |       .locator(".design-card")
  163 |       .filter({
  164 |         has: page.getByRole("heading", { name: "ready", exact: true }),
  165 |       })
  166 |       .first();
  167 |     await picker
  168 |       .getByRole("button", { name: "Choose model", exact: true })
  169 |       .click();
  170 |     const filters = page.getByRole("group", { name: "Filter models" });
  171 |     await expect(
  172 |       page.getByRole("option", { name: /^fake-chat/ }),
  173 |     ).toContainText("Selected");
  174 |     await filters.getByRole("button", { name: "Images", exact: true }).click();
  175 |     await expect(page.getByRole("option")).toHaveCount(1);
  176 |     await expect(page.getByRole("option")).toContainText("fake-vision");
  177 |     await expect(
  178 |       filters.getByRole("button", { name: "Images", exact: true }),
  179 |     ).toHaveAttribute("aria-pressed", "true");
  180 |     await filters
  181 |       .getByRole("button", { name: "Reasoning", exact: true })
  182 |       .click();
  183 |     await expect(page.getByRole("option")).toHaveCount(1);
  184 |     await expect(page.getByRole("option")).toContainText("fake-reasoning");
  185 |     await filters.getByRole("button", { name: "Tools", exact: true }).click();
  186 |     await expect(page.getByRole("option")).toHaveCount(0);
  187 |     await expect(
  188 |       page.getByText("No matching models.", { exact: true }),
  189 |     ).toBeVisible();
  190 |     await filters.getByRole("button", { name: "Loaded", exact: true }).click();
  191 |     await expect(page.getByRole("option")).toHaveCount(1);
  192 |     await expect(page.getByRole("option")).toContainText("fake-chat");
  193 |     await filters.getByRole("button", { name: "All", exact: true }).click();
  194 |     await expect(page.getByRole("option")).toHaveCount(3);
  195 |     await page
  196 |       .getByRole("combobox", { name: "Search models", exact: true })
  197 |       .fill("fake-vision");
  198 |     await expect(page.getByRole("option")).toHaveCount(1);
  199 |     await page
  200 |       .getByRole("combobox", { name: "Search models", exact: true })
  201 |       .fill("");
  202 |     await settle(page);
  203 |     await page.screenshot({
  204 |       path: `../artifacts/deferred-polish/picker-${width}-${browserName}-fake.png`,
  205 |     });
  206 |     const { default: AxeBuilder } = await import("@axe-core/playwright");
  207 |     const audit = await new AxeBuilder({ page })
  208 |       .include('[data-slot="command"]')
  209 |       .analyze();
  210 |     expect(
  211 |       audit.violations.filter((v) =>
  212 |         ["serious", "critical"].includes(v.impact ?? ""),
  213 |       ),
  214 |     ).toEqual([]);
  215 |   });
  216 | }
  217 | 
  218 | for (const width of [320, 390]) {
  219 |   test(`picker stays usable with keyboard-sized space ${width}`, async ({
  220 |     page,
  221 |     browserName,
  222 |   }) => {
  223 |     await page.setViewportSize({ width, height: 360 });
  224 |     await page.goto("/design/chat");
  225 |     await page.addStyleTag({
  226 |       content: ":root {--safe-area-top:44px;--safe-area-bottom:34px;}",
  227 |     });
  228 |     await page
  229 |       .getByRole("button", { name: "Choose model", exact: true })
```