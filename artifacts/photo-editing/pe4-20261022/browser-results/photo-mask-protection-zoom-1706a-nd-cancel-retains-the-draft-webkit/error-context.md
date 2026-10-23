# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: photo-mask-protection.spec.ts >> zoom and move retain pointer coordinates and cancel retains the draft
- Location: tests/photo-mask-protection.spec.ts:155:1

# Error details

```
Error: expect(received).toBeCloseTo(expected, precision)

Expected: 0.27359375
Received: 0.27333

Expected precision:    4
Expected difference: < 0.00005
Received difference:   0.00026375000000000703
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
      - button "Chat controls" [ref=e12] [cursor=pointer]
      - button "Actions for Synthetic protected change" [ref=e13] [cursor=pointer]
    - status [ref=e14]
    - log "Conversation" [ref=e15]:
      - generic [ref=e16]:
        - article "user message" [ref=e17]:
          - heading "You said" [level=2] [ref=e18]
          - generic [ref=e19]:
            - paragraph [ref=e20]: Image
            - paragraph [ref=e25]: Synthetic protected change
          - button "Copy message" [ref=e29] [cursor=pointer]:
            - status [ref=e30]
        - article "assistant message" [ref=e31]:
          - heading "Assistant replied" [level=2] [ref=e32]
          - generic [ref=e33]:
            - paragraph [ref=e34]: FLUX.2 klein 4B · Photo edit
            - group "Images in this turn" [ref=e35]:
              - generic [ref=e36]:
                - button "Open image 1" [ref=e37] [cursor=pointer]:
                  - img "Synthetic protected change" [ref=e38]
                - generic [ref=e39]:
                  - button "Save image" [ref=e40] [cursor=pointer]
                  - button "More like this" [ref=e41] [cursor=pointer]
                  - button "Refine image" [ref=e42] [cursor=pointer]
                  - button "Copy image prompt" [ref=e43] [cursor=pointer]:
                    - status [ref=e44]
                  - button "Image details" [ref=e45] [cursor=pointer]
                  - button "More image actions" [ref=e46] [cursor=pointer]
            - status [ref=e47]:
              - generic [ref=e48]: 1 image · 0 s
            - generic [ref=e49]:
              - button "Try again" [ref=e50] [cursor=pointer]
              - button "Copy prompt" [ref=e51] [cursor=pointer]:
                - status [ref=e52]
                - text: Copy prompt
    - generic [ref=e53]:
      - button [aria-hidden] [ref=e54] [cursor=pointer]
      - form "Message" [ref=e55]:
        - generic [ref=e56]:
          - generic [ref=e58]:
            - paragraph [ref=e59]: Photo reference
            - paragraph [ref=e60]: Choose one PNG, JPEG or HEIC photo.
          - button "Attach photo" [ref=e61] [cursor=pointer]
          - paragraph [ref=e62]: Select an area to protect the rest. Without a selection, the whole photo can change. Your original stays private.
        - textbox "Photo edit instruction" [ref=e63]:
          - /placeholder: Describe what to change…
        - generic [ref=e64]:
          - button "Replace photo" [ref=e65] [cursor=pointer]
          - button "Leave photo edit mode" [ref=e66] [cursor=pointer]: Edit photo
          - generic [ref=e68]:
            - button "Edit photo" [disabled]
  - region "Notifications alt+T"
```

# Test source

```ts
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
  148 |     .toBeGreaterThan(selected[0] * 2);
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
> 192 |   expect(sent!.selection.strokes[0].points[0][1]).toBeCloseTo(expected[1], 4);
      |                                                   ^ Error: expect(received).toBeCloseTo(expected, precision)
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
  249 |   });
  250 | 
```