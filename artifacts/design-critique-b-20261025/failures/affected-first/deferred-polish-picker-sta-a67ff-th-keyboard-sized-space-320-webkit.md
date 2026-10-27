# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: deferred-polish.spec.ts >> picker stays usable with keyboard-sized space 320
- Location: tests/deferred-polish.spec.ts:225:3

# Error details

```
Error: expect(locator).toBeInViewport() failed

Locator:  getByRole('dialog', { name: 'Choose model', exact: true }).getByRole('gridcell', { name: /^fake-vision/ })
Expected: in viewport
Received: viewport ratio 0.296875
Timeout:  5000ms

Call log:
  - Expect "toBeInViewport" getByRole('dialog', { name: 'Choose model', exact: true }).getByRole('gridcell', { name: /^fake-vision/ }) with timeout 5000ms
  - waiting for getByRole('dialog', { name: 'Choose model', exact: true }).getByRole('gridcell', { name: /^fake-vision/ })
    14 × locator resolved to <div cmdk-item="" role="gridcell" id="radix-_r_10_" aria-selected="true" data-selected="true" aria-disabled="false" data-disabled="false" data-slot="model-choice" data-active-model="false" data-value="fake-vision fake-vision design" class="relative flex cursor-default items-center rounded-sm px-2 py-1.5 text-sm outline-hidden select-none data-[disabled=true]:pointer-events-none data-[disabled=true]:opacity-50 data-[selected=true]:bg-accent data-[selected=true]:text-accent-foreground [&_svg]:pointer…>…</div>
       - unexpected value "viewport ratio 0.296875"

```

```yaml
- gridcell "fake-vision Sees 16K context · Not loaded" [selected]:
  - text: fake-vision Sees
  - paragraph: 16K context · Not loaded
```

# Test source

```ts
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
  172 |       page.getByRole("gridcell", { name: /^fake-chat/ }),
  173 |     ).toHaveAttribute("data-active-model", "true");
  174 |     await filters.getByRole("button", { name: "Vision", exact: true }).click();
  175 |     await expect(page.locator('[data-slot="model-choice"]')).toHaveCount(1);
  176 |     await expect(page.locator('[data-slot="model-choice"]')).toContainText(
  177 |       "fake-vision",
  178 |     );
  179 |     await expect(
  180 |       filters.getByRole("button", { name: "Vision", exact: true }),
  181 |     ).toHaveAttribute("aria-pressed", "true");
  182 |     await filters
  183 |       .getByRole("button", { name: "Reasoning", exact: true })
  184 |       .click();
  185 |     await expect(page.locator('[data-slot="model-choice"]')).toHaveCount(1);
  186 |     await expect(page.locator('[data-slot="model-choice"]')).toContainText(
  187 |       "fake-reasoning",
  188 |     );
  189 |     await filters.getByRole("button", { name: "Tools", exact: true }).click();
  190 |     await expect(page.locator('[data-slot="model-choice"]')).toHaveCount(0);
  191 |     await expect(
  192 |       page.getByText("No matching models.", { exact: true }),
  193 |     ).toBeVisible();
  194 |     await filters.getByRole("button", { name: "Loaded", exact: true }).click();
  195 |     await expect(page.locator('[data-slot="model-choice"]')).toHaveCount(1);
  196 |     await expect(page.locator('[data-slot="model-choice"]')).toContainText(
  197 |       "fake-chat",
  198 |     );
  199 |     await filters.getByRole("button", { name: "All", exact: true }).click();
  200 |     await expect(page.locator('[data-slot="model-choice"]')).toHaveCount(3);
  201 |     await page
  202 |       .getByRole("combobox", { name: "Search models", exact: true })
  203 |       .fill("fake-vision");
  204 |     await expect(page.locator('[data-slot="model-choice"]')).toHaveCount(1);
  205 |     await page
  206 |       .getByRole("combobox", { name: "Search models", exact: true })
  207 |       .fill("");
  208 |     await settle(page);
  209 |     await page.screenshot({
  210 |       path: `../artifacts/deferred-polish/picker-${width}-${browserName}-fake.png`,
  211 |     });
  212 |     const { default: AxeBuilder } = await import("@axe-core/playwright");
  213 |     const audit = await new AxeBuilder({ page })
  214 |       .include('[data-slot="command"]')
  215 |       .analyze();
  216 |     expect(
  217 |       audit.violations.filter((v) =>
  218 |         ["serious", "critical"].includes(v.impact ?? ""),
  219 |       ),
  220 |     ).toEqual([]);
  221 |   });
  222 | }
  223 | 
  224 | for (const width of [320, 390]) {
  225 |   test(`picker stays usable with keyboard-sized space ${width}`, async ({
  226 |     page,
  227 |     browserName,
  228 |   }) => {
  229 |     await page.setViewportSize({ width, height: 360 });
  230 |     await page.goto("/design/chat");
  231 |     await page.addStyleTag({
  232 |       content: ":root {--safe-area-top:44px;--safe-area-bottom:34px;}",
  233 |     });
  234 |     await page
  235 |       .getByRole("button", { name: "Choose model", exact: true })
  236 |       .click();
  237 |     const drawer = page.getByRole("dialog", {
  238 |       name: "Choose model",
  239 |       exact: true,
  240 |     });
  241 |     await expect(drawer).toBeVisible();
  242 |     const search = drawer.getByRole("combobox", {
  243 |       name: "Search models",
  244 |       exact: true,
  245 |     });
  246 |     await search.fill("fake-vision");
  247 |     const option = drawer.getByRole("gridcell", { name: /^fake-vision/ });
  248 |     await option.scrollIntoViewIfNeeded();
> 249 |     await expect(option).toBeInViewport({ ratio: 0.99 });
      |                          ^ Error: expect(locator).toBeInViewport() failed
  250 |     const command = await drawer.locator('[data-slot="command"]').boundingBox();
  251 |     const row = await option.boundingBox();
  252 |     expect(row!.y).toBeGreaterThanOrEqual(command!.y + 56);
  253 |     expect(row!.y + row!.height).toBeLessThanOrEqual(
  254 |       command!.y + command!.height + 1,
  255 |     );
  256 |     await expect(search).toBeInViewport({ ratio: 0.99 });
  257 |     const close = drawer.getByRole("button", {
  258 |       name: "Close model picker",
  259 |       exact: true,
  260 |     });
  261 |     await expect(close).toBeInViewport({ ratio: 0.99 });
  262 |     const { default: AxeBuilder } = await import("@axe-core/playwright");
  263 |     const audit = await new AxeBuilder({ page })
  264 |       .include('[data-slot="drawer-content"]')
  265 |       .analyze();
  266 |     expect(
  267 |       audit.violations.filter((v) =>
  268 |         ["serious", "critical"].includes(v.impact ?? ""),
  269 |       ),
  270 |     ).toEqual([]);
  271 |     await settle(page);
  272 |     await page.screenshot({
  273 |       path: `../artifacts/deferred-polish/picker-short-${width}x360-${browserName}-fake.png`,
  274 |     });
  275 |     await close.click();
  276 |     await expect(drawer).toHaveCount(0);
  277 |   });
  278 | }
  279 | 
```