# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: chat-images.spec.ts >> chat image frame states, counts and axe 390 light
- Location: tests/chat-images.spec.ts:196:5

# Error details

```
Error: expect(received).toEqual(expected) // deep equality

- Expected  -  1
+ Received  + 52

- Array []
+ Array [
+   Object {
+     "description": "Ensure elements that have scrollable content are accessible by keyboard in Safari",
+     "help": "Scrollable region must have keyboard access",
+     "helpUrl": "https://dequeuniversity.com/rules/axe/4.13/scrollable-region-focusable?application=playwright",
+     "id": "scrollable-region-focusable",
+     "impact": "serious",
+     "nodes": Array [
+       Object {
+         "all": Array [],
+         "any": Array [
+           Object {
+             "data": null,
+             "id": "focusable-content",
+             "impact": "serious",
+             "message": "Element should have focusable content",
+             "relatedNodes": Array [],
+           },
+           Object {
+             "data": null,
+             "id": "focusable-element",
+             "impact": "serious",
+             "message": "Element should be focusable",
+             "relatedNodes": Array [],
+           },
+         ],
+         "failureSummary": "Fix any of the following:
+   Element should have focusable content
+   Element should be focusable",
+         "html": "<div class=\"image-frames image-count-3\">",
+         "impact": "serious",
+         "none": Array [],
+         "target": Array [
+           ".image-frames",
+         ],
+       },
+     ],
+     "tags": Array [
+       "cat.keyboard",
+       "wcag2a",
+       "wcag211",
+       "wcag213",
+       "TTv5",
+       "TT4.a",
+       "EN-301-549",
+       "EN-9.2.1.1",
+       "EN-9.2.1.3",
+       "RGAAv4",
+       "RGAA-7.3.2",
+     ],
+   },
+ ]
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
      - heading "Chat images · synthetic states" [level=1] [ref=e17]
      - generic [ref=e18]:
        - button "light" [ref=e19] [cursor=pointer]
        - button "dark" [ref=e20] [cursor=pointer]
        - button "Reduce motion" [ref=e21] [cursor=pointer]
        - button "Preview 1 image" [ref=e22] [cursor=pointer]
        - button "Preview 2 images" [ref=e23] [cursor=pointer]
        - button "Preview 3 images" [active] [pressed] [ref=e24] [cursor=pointer]
        - button "Preview queued" [pressed] [ref=e25] [cursor=pointer]
        - button "Preview preparing" [ref=e26] [cursor=pointer]
        - button "Preview step 0" [ref=e27] [cursor=pointer]
        - button "Preview step 1" [ref=e28] [cursor=pointer]
        - button "Preview step 2" [ref=e29] [cursor=pointer]
        - button "Preview step 3" [ref=e30] [cursor=pointer]
        - button "Preview step 4" [ref=e31] [cursor=pointer]
        - button "Preview decoding" [ref=e32] [cursor=pointer]
        - button "Preview complete" [ref=e33] [cursor=pointer]
        - button "Preview cancelling" [ref=e34] [cursor=pointer]
        - button "Preview cancelled" [ref=e35] [cursor=pointer]
        - button "Preview failed" [ref=e36] [cursor=pointer]
        - button "Preview interrupted" [ref=e37] [cursor=pointer]
        - button "Preview removed" [ref=e38] [cursor=pointer]
      - region "Image conversation preview" [ref=e39]:
        - generic [ref=e40]:
          - paragraph [ref=e41]: Image · 3 images
          - paragraph [ref=e42]: Synthetic cobalt harbor with warm paper lanterns.
        - generic [ref=e43]:
          - paragraph [ref=e44]: FLUX.2 klein 4B
          - generic [ref=e45]:
            - generic [ref=e48]: Next
            - generic [ref=e52]: Next
          - status [ref=e56]:
            - generic [ref=e62]: Waiting for your Mac
          - generic [ref=e63]:
            - button "Cancel" [ref=e64] [cursor=pointer]
            - button "Copy prompt" [ref=e65] [cursor=pointer]:
              - status [ref=e66]
              - text: Copy prompt
        - form "Message" [ref=e68]:
          - textbox "Image prompt" [ref=e69]:
            - /placeholder: Describe an image…
          - generic [ref=e70]:
            - button "Leave image mode" [pressed] [ref=e71] [cursor=pointer]:
              - generic [ref=e72]: Image
            - button "Image count" [ref=e73] [cursor=pointer]: 1 image
            - button "Image options" [ref=e74] [cursor=pointer]
            - generic [ref=e76]:
              - button "Create image" [disabled]
  - region "Notifications alt+T"
```

# Test source

```ts
  143 |     "data-job-id",
  144 |     jobIds[0]!,
  145 |   );
  146 | });
  147 | 
  148 | test("image command, independent drafts, cancellation, removed outputs and failed load retry", async ({
  149 |   page,
  150 |   request,
  151 | }) => {
  152 |   await page.goto("/");
  153 |   await expect(
  154 |     page.getByRole("button", { name: "Create image", exact: true }),
  155 |   ).toBeEnabled();
  156 |   await page
  157 |     .locator(".composer textarea")
  158 |     .fill("/image Synthetic cancel circle #slow");
  159 |   await expect(prompt(page)).toHaveValue("Synthetic cancel circle #slow");
  160 |   await page.getByRole("button", { name: "Leave image mode" }).click();
  161 |   await page.locator(".composer textarea").fill("Synthetic separate text");
  162 |   await page.getByRole("button", { name: "Create image", exact: true }).click();
  163 |   await expect(prompt(page)).toHaveValue("Synthetic cancel circle #slow");
  164 |   await page.getByRole("button", { name: "Create image", exact: true }).click();
  165 |   await turn(page).getByRole("button", { name: "Cancel", exact: true }).click();
  166 |   await expect(turn(page).getByRole("status")).toHaveText("Cancelled");
  167 |   await turn(page)
  168 |     .getByRole("button", { name: "Try again", exact: true })
  169 |     .click();
  170 |   await expect(turn(page).locator("img")).toBeVisible();
  171 |   await page.route("**/api/images/jobs/*/output/png", (route) =>
  172 |     route.fulfill({ status: 404, body: "Synthetic load failure" }),
  173 |   );
  174 |   await page.reload();
  175 |   await expect(turn(page)).toContainText("Couldn't load the image");
  176 |   await page.unroute("**/api/images/jobs/*/output/png");
  177 |   await turn(page).getByRole("button", { name: "Retry", exact: true }).click();
  178 |   await expect(turn(page).locator("img.is-loaded")).toBeVisible();
  179 |   await turn(page).getByRole("button", { name: "More image actions" }).click();
  180 |   await page
  181 |     .getByRole("menuitem", { name: "Remove image", exact: true })
  182 |     .click();
  183 |   await page
  184 |     .getByRole("dialog")
  185 |     .getByRole("button", { name: "Remove", exact: true })
  186 |     .click();
  187 |   await expect(turn(page)).toContainText("Image removed");
  188 |   const chatId = new URL(page.url()).pathname.split("/").at(-1);
  189 |   await request.delete(`/api/chats/${chatId}`);
  190 |   await page.goto("/images");
  191 |   await expect(page.getByText("From a deleted chat").first()).toBeVisible();
  192 | });
  193 | 
  194 | for (const width of [390, 1440])
  195 |   for (const theme of ["light", "dark"])
  196 |     test(`chat image frame states, counts and axe ${width} ${theme}`, async ({
  197 |       page,
  198 |       browserName,
  199 |     }) => {
  200 |       await page.setViewportSize({ width, height: 900 });
  201 |       await page.goto("/design?chat-images");
  202 |       await page.getByRole("button", { name: theme, exact: true }).click();
  203 |       await mkdir(dir, { recursive: true });
  204 |       const results = [];
  205 |       for (const state of [
  206 |         "queued",
  207 |         "preparing",
  208 |         "step 0",
  209 |         "step 1",
  210 |         "step 2",
  211 |         "step 3",
  212 |         "step 4",
  213 |         "decoding",
  214 |         "complete",
  215 |         "cancelling",
  216 |         "cancelled",
  217 |         "failed",
  218 |         "interrupted",
  219 |         "removed",
  220 |       ]) {
  221 |         await page
  222 |           .getByRole("button", { name: `Preview ${state}`, exact: true })
  223 |           .click();
  224 |         for (const count of [1, 2, 3]) {
  225 |           await page
  226 |             .getByRole("button", {
  227 |               name: `Preview ${count} image${count > 1 ? "s" : ""}`,
  228 |               exact: true,
  229 |             })
  230 |             .click();
  231 |           await expect(page.locator(".image-frame")).toHaveCount(count);
  232 |         }
  233 |         await settle(page);
  234 |         expect(
  235 |           await page.evaluate(
  236 |             () => document.documentElement.scrollWidth <= innerWidth,
  237 |           ),
  238 |         ).toBe(true);
  239 |         const scan = await new AxeBuilder({ page }).analyze();
  240 |         const violations = scan.violations.filter((v) =>
  241 |           ["critical", "serious"].includes(v.impact ?? ""),
  242 |         );
> 243 |         expect(violations).toEqual([]);
      |                            ^ Error: expect(received).toEqual(expected) // deep equality
  244 |         results.push({ state, count: 3, violations });
  245 |         await page.screenshot({
  246 |           path: `${dir}/${state.replace(" ", "-")}-${width}-${theme}-${browserName}-fake.png`,
  247 |           fullPage: true,
  248 |         });
  249 |       }
  250 |       await writeFile(
  251 |         `${dir}/axe-${width}-${theme}-${browserName}.json`,
  252 |         JSON.stringify(results, null, 2),
  253 |       );
  254 |     });
  255 | 
  256 | for (const mode of ["always", "system"] as const)
  257 |   test(`image develop and progress motion respects ${mode}`, async ({
  258 |     page,
  259 |   }) => {
  260 |     await page.emulateMedia({
  261 |       reducedMotion: mode === "system" ? "reduce" : "no-preference",
  262 |     });
  263 |     await page.goto("/design?chat-images");
  264 |     if (mode === "always")
  265 |       await page.getByRole("button", { name: "Reduce motion" }).click();
  266 |     await expect(page.locator(".image-progress")).toHaveCount(2);
  267 |     expect(
  268 |       await page
  269 |         .locator(".image-develop i,.image-progress i")
  270 |         .evaluateAll((nodes) =>
  271 |           nodes.every((node) => {
  272 |             const css = getComputedStyle(node);
  273 |             return (
  274 |               css.animationName === "none" &&
  275 |               css.transitionDuration
  276 |                 .split(",")
  277 |                 .every((n) => parseFloat(n) === 0)
  278 |             );
  279 |           }),
  280 |         ),
  281 |     ).toBe(true);
  282 |     await page
  283 |       .getByRole("button", { name: "Preview step 4", exact: true })
  284 |       .click();
  285 |     await expect(page.getByRole("progressbar").first()).toHaveAttribute(
  286 |       "aria-valuenow",
  287 |       "4",
  288 |     );
  289 |   });
  290 | 
```