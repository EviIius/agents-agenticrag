# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: photo-mask-protection.spec.ts >> selected and protected views show an erased detail without changing the mask
- Location: tests/photo-mask-protection.spec.ts:109:1

# Error details

```
Error: expect(received).toBeGreaterThan(expected)

Expected: > 1494
Received:   745

Call Log:
- Timeout 5000ms exceeded while waiting on the predicate
```

# Page snapshot

```yaml
- generic:
  - generic:
    - generic [aria-hidden]:
      - complementary:
        - generic:
          - generic:
            - button
            - generic: Aether
            - link:
              - /url: /design/chat
          - navigation:
            - navigation:
              - generic:
                - link:
                  - /url: /workflows
                  - text: Workflows
              - generic:
                - link:
                  - /url: /images
                  - text: Images
            - paragraph: TODAY
            - generic:
              - link:
                - /url: /design/chat/fixture
                - text: A clearer way to learn
            - generic:
              - link:
                - /url: /design/chat/fixture
                - text: Planning a weekend
            - generic:
              - link:
                - /url: /design/chat/fixture
                - text: Understanding a short function
            - generic:
              - link:
                - /url: /design/chat/fixture
                - text: Making a useful checklist
            - paragraph: YESTERDAY
            - link:
              - /url: /design/chat/fixture
              - text: A fresh perspective
          - generic:
            - button: Settings
      - main:
        - generic:
          - generic:
            - button:
              - generic [aria-hidden]: ●
              - generic: fake-chat
          - generic: A clearer way to learn
          - generic:
            - button
            - button
        - generic:
          - main:
            - heading [level=1]: Photo editing · synthetic states
            - generic:
              - button: light
              - button: dark
              - button: Reduce motion
              - button: Preview ready
              - button: Preview selection
              - button [pressed]: Preview selection-protected
              - button: Preview selection-empty
              - button: Preview selection-load-error
              - button: Preview preparing
              - button: Preview upload-error
              - button: Preview unavailable-reference
              - button: Preview running
              - button: Preview cancelled
              - button: Preview complete
              - button: Preview comparison
              - button: Preview rejected-send
            - region:
              - generic:
                - form:
                  - generic:
                    - generic:
                      - button
                      - generic:
                        - paragraph: Photo reference
                        - paragraph: Ready · 720 × 900
                      - button
                    - generic:
                      - button: Change selection
                      - button: Clear selection
                    - paragraph: Only selected areas change. Photo proportions and unselected pixels are preserved. Your original stays private.
                  - textbox:
                    - /placeholder: Describe what to change…
                    - text: Change the synthetic background to cobalt.
                  - generic:
                    - button
                    - button: Edit photo
                    - generic:
                      - generic:
                        - button
    - region "Notifications alt+T"
  - dialog [ref=e2]:
    - heading "Select edit area" [level=2] [ref=e3]
    - paragraph [ref=e4]: Paint the existing area to replace and room for additions. Protect removes paint; those pixels stay unchanged.
    - group "Selection tool" [ref=e5]:
      - button "Paint" [pressed] [ref=e6] [cursor=pointer]
      - button "Protect" [ref=e7] [cursor=pointer]
      - button "Move" [ref=e8] [cursor=pointer]
    - generic [ref=e9]:
      - group "Photo zoom" [ref=e10]:
        - button "Zoom out" [disabled]: −
        - button "Fit photo" [ref=e11] [cursor=pointer]: 1×
        - button "Zoom in" [ref=e12] [cursor=pointer]: +
      - group "Mask view" [ref=e13]:
        - button "Overlay" [ref=e14] [cursor=pointer]
        - button "Selected" [ref=e15] [cursor=pointer]
        - button "Protected" [active] [pressed] [ref=e16] [cursor=pointer]
    - img "Photo selection canvas. Paint or protect with a pointer, or use arrow keys and Space. Choose Move to pan." [ref=e19]
    - paragraph [ref=e20]: Bright areas stay protected. Dim areas may change. Zoom in for details; choose Move to pan.
    - generic [ref=e21]:
      - generic [ref=e22]: Brush size
      - generic "Brush size" [ref=e23]:
        - slider "Brush size" [ref=e27]
    - status [ref=e28]: 2 brush strokes · about 5% selected
    - paragraph [ref=e29]: "Check coverage before applying: include the surface beneath each addition, not just the empty space around it."
    - generic [ref=e30]:
      - button "Undo" [disabled]
      - button "Redo" [disabled]
      - button "Clear" [ref=e31] [cursor=pointer]
      - button "Cancel" [ref=e32] [cursor=pointer]
      - button "Use selection" [ref=e33] [cursor=pointer]
    - button "Close" [ref=e34] [cursor=pointer]
```

# Test source

```ts
  48  |     dialog.getByRole("button", { name: "Use selection" }),
  49  |   ).toBeEnabled();
  50  |   await dialog.getByRole("button", { name: "Redo", exact: true }).click();
  51  |   await expect(
  52  |     dialog.getByRole("button", { name: "Use selection" }),
  53  |   ).toBeDisabled();
  54  |   await dialog.getByRole("button", { name: "Paint", exact: true }).click();
  55  |   await canvas.focus();
  56  |   await page.keyboard.press("Space");
  57  |   await dialog.getByRole("button", { name: "Clear", exact: true }).click();
  58  |   await expect(
  59  |     dialog.getByRole("button", { name: "Use selection" }),
  60  |   ).toBeDisabled();
  61  |   await dialog.getByRole("button", { name: "Undo", exact: true }).click();
  62  |   await expect(dialog.getByRole("status")).toContainText("3 brush strokes");
  63  |   await dialog.getByRole("button", { name: "Use selection" }).click();
  64  |   const requests: Record<string, unknown>[] = [];
  65  |   await page.route("**/api/chats/*/images", async (route) => {
  66  |     requests.push(route.request().postDataJSON());
  67  |     if (requests.length === 1)
  68  |       await route.fulfill({
  69  |         status: 409,
  70  |         contentType: "application/json",
  71  |         body: JSON.stringify({
  72  |           error: {
  73  |             code: "image_capacity",
  74  |             message: "Synthetic protection rejection",
  75  |           },
  76  |         }),
  77  |       });
  78  |     else await route.continue();
  79  |   });
  80  |   await page.getByRole("button", { name: "Edit photo", exact: true }).click();
  81  |   await expect(page.getByRole("alert")).toContainText(
  82  |     "Synthetic protection rejection",
  83  |   );
  84  |   await page
  85  |     .getByRole("button", { name: "Change selection", exact: true })
  86  |     .click();
  87  |   await expect(dialog.getByRole("status")).toContainText("3 brush strokes");
  88  |   await dialog.getByRole("button", { name: "Cancel", exact: true }).click();
  89  |   await page.getByRole("button", { name: "Edit photo", exact: true }).click();
  90  |   await expect(
  91  |     page.getByRole("button", { name: "Open image 1", exact: true }),
  92  |   ).toBeVisible();
  93  |   expect(requests[0]).toEqual(requests[1]);
  94  |   const selection = requests[0].selection as {
  95  |     strokes: { operation?: string }[];
  96  |   };
  97  |   expect(selection.strokes.map((s) => s.operation)).toEqual([
  98  |     undefined,
  99  |     "erase",
  100 |     undefined,
  101 |   ]);
  102 |   const retry = page.waitForResponse((r) => r.url().endsWith("/images/retry"));
  103 |   await page.getByRole("button", { name: "Try again", exact: true }).click();
  104 |   expect((await (await retry).json()).assistant.images[0].selection).toEqual(
  105 |     selection,
  106 |   );
  107 | });
  108 | 
  109 | test("selected and protected views show an erased detail without changing the mask", async ({
  110 |   page,
  111 | }) => {
  112 |   await page.goto("/design?photo-edit&state=selection-protected");
  113 |   await page
  114 |     .getByRole("button", { name: "Change selection", exact: true })
  115 |     .click();
  116 |   const dialog = page.getByRole("dialog", {
  117 |     name: "Select edit area",
  118 |     exact: true,
  119 |   });
  120 |   const canvas = dialog.getByRole("img", { name: /^Photo selection canvas/ });
  121 |   await expect(
  122 |     dialog.getByRole("button", { name: "Use selection" }),
  123 |   ).toBeEnabled();
  124 |   async function pixels() {
  125 |     return canvas.evaluate((c: HTMLCanvasElement) => {
  126 |       const ctx = c.getContext("2d")!;
  127 |       const brightness = (x: number, y: number) =>
  128 |         [
  129 |           ...ctx.getImageData(
  130 |             Math.round(c.width * x),
  131 |             Math.round(c.height * y),
  132 |             1,
  133 |             1,
  134 |           ).data,
  135 |         ]
  136 |           .slice(0, 3)
  137 |           .reduce((a, b) => a + b, 0);
  138 |       return [brightness(0.5, 0.3), brightness(0.61, 0.3)];
  139 |     });
  140 |   }
  141 |   await dialog.getByRole("button", { name: "Selected", exact: true }).click();
  142 |   await expect(dialog).toContainText("Bright areas may change");
  143 |   const selected = await pixels();
  144 |   await dialog.getByRole("button", { name: "Protected", exact: true }).click();
  145 |   await expect(dialog).toContainText("Bright areas stay protected");
  146 |   await expect
  147 |     .poll(async () => (await pixels())[0])
> 148 |     .toBeGreaterThan(selected[0] * 2);
      |      ^ Error: expect(received).toBeGreaterThan(expected)
  149 |   const protectedView = await pixels();
  150 |   expect(selected[1]).toBeGreaterThan(protectedView[1] * 2);
  151 |   await dialog.getByRole("button", { name: "Overlay", exact: true }).click();
  152 |   await expect(dialog.getByRole("status")).toContainText("2 brush strokes");
  153 | });
  154 | 
  155 | test("zoom and move retain pointer coordinates and cancel retains the draft", async ({
  156 |   page,
  157 | }) => {
  158 |   const dialog = await open(page);
  159 |   const canvas = dialog.getByRole("img", { name: /^Photo selection canvas/ });
  160 |   const viewport = dialog.locator('[data-slot="mask-viewport"]');
  161 |   for (let i = 0; i < 4; i++)
  162 |     await dialog.getByRole("button", { name: "Zoom in", exact: true }).click();
  163 |   await dialog.getByRole("button", { name: "Move", exact: true }).click();
  164 |   await viewport.scrollIntoViewIfNeeded();
  165 |   const frame = (await viewport.boundingBox())!;
  166 |   const cx = frame.x + frame.width / 2,
  167 |     cy = frame.y + frame.height / 2;
  168 |   await page.mouse.move(cx, cy);
  169 |   await page.mouse.down();
  170 |   await page.mouse.move(cx - 80, cy - 70, { steps: 5 });
  171 |   await page.mouse.up();
  172 |   expect(await viewport.evaluate((v) => v.scrollTop)).toBeGreaterThan(0);
  173 |   await dialog.getByRole("button", { name: "Paint", exact: true }).click();
  174 |   await viewport.scrollIntoViewIfNeeded();
  175 |   const visible = (await viewport.boundingBox())!,
  176 |     photo = (await canvas.boundingBox())!;
  177 |   const x = visible.x + visible.width / 2,
  178 |     y = visible.y + visible.height / 2;
  179 |   const expected = [(x - photo.x) / photo.width, (y - photo.y) / photo.height];
  180 |   await page.mouse.click(x, y);
  181 |   await dialog.getByRole("button", { name: "Use selection" }).click();
  182 |   let sent: { selection: { strokes: { points: number[][] }[] } } | undefined;
  183 |   await page.route("**/api/chats/*/images", async (route) => {
  184 |     sent = route.request().postDataJSON();
  185 |     await route.continue();
  186 |   });
  187 |   await page.getByRole("button", { name: "Edit photo", exact: true }).click();
  188 |   await expect(
  189 |     page.getByRole("button", { name: "Open image 1", exact: true }),
  190 |   ).toBeVisible();
  191 |   expect(sent!.selection.strokes[0].points[0][0]).toBeCloseTo(expected[0], 4);
  192 |   expect(sent!.selection.strokes[0].points[0][1]).toBeCloseTo(expected[1], 4);
  193 | });
  194 | 
  195 | test("an erased-empty design state cannot be applied", async ({ page }) => {
  196 |   await page.goto("/design?photo-edit&state=selection-empty");
  197 |   await page
  198 |     .getByRole("button", { name: "Change selection", exact: true })
  199 |     .click();
  200 |   const dialog = page.getByRole("dialog", {
  201 |     name: "Select edit area",
  202 |     exact: true,
  203 |   });
  204 |   await expect(dialog.getByRole("status")).toContainText("No area selected");
  205 |   await expect(
  206 |     dialog.getByRole("button", { name: "Use selection" }),
  207 |   ).toBeDisabled();
  208 | });
  209 | 
  210 | for (const theme of ["light", "dark"])
  211 |   test(`phone precision tools ${theme} are reachable in a short viewport`, async ({
  212 |     page,
  213 |     browserName,
  214 |   }) => {
  215 |     await page.setViewportSize({ width: 390, height: 600 });
  216 |     await page.goto("/design?photo-edit&state=selection-protected");
  217 |     await page.getByRole("button", { name: theme, exact: true }).click();
  218 |     await page
  219 |       .getByRole("button", { name: "Change selection", exact: true })
  220 |       .click();
  221 |     const dialog = page.getByRole("dialog", {
  222 |       name: "Select edit area",
  223 |       exact: true,
  224 |     });
  225 |     for (const label of [
  226 |       "Paint",
  227 |       "Protect",
  228 |       "Move",
  229 |       "Zoom in",
  230 |       "Protected",
  231 |       "Undo",
  232 |       "Redo",
  233 |       "Clear",
  234 |       "Cancel",
  235 |       "Use selection",
  236 |     ]) {
  237 |       const button = dialog.getByRole("button", { name: label, exact: true });
  238 |       await button.scrollIntoViewIfNeeded();
  239 |       const box = (await button.boundingBox())!;
  240 |       expect(box.x).toBeGreaterThanOrEqual(0);
  241 |       expect(box.x + box.width).toBeLessThanOrEqual(390);
  242 |       expect(box.y).toBeGreaterThanOrEqual(0);
  243 |       expect(box.y + box.height).toBeLessThanOrEqual(600);
  244 |     }
  245 |     await mkdir(directory, { recursive: true });
  246 |     await page.screenshot({
  247 |       path: `${directory}/precision-fake-390-${theme}-${browserName}.png`,
  248 |     });
```