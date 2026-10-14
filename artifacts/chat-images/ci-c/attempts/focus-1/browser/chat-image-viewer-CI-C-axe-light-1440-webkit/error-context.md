# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: chat-image-viewer.spec.ts >> CI-C axe light 1440
- Location: tests/chat-image-viewer.spec.ts:346:5

# Error details

```
Error: expect(received).toEqual(expected) // deep equality

- Expected  -  1
+ Received  + 64

- Array []
+ Array [
+   Object {
+     "description": "Ensure the contrast between foreground and background colors meets WCAG 2 AA minimum contrast ratio thresholds",
+     "help": "Elements must meet minimum color contrast ratio thresholds",
+     "helpUrl": "https://dequeuniversity.com/rules/axe/4.13/color-contrast?application=playwright",
+     "id": "color-contrast",
+     "impact": "serious",
+     "nodes": Array [
+       Object {
+         "all": Array [],
+         "any": Array [
+           Object {
+             "data": Object {
+               "bgColor": "#b3b2b0",
+               "contrastRatio": 3.56,
+               "expectedContrastRatio": "4.5:1",
+               "fgColor": "#57544e",
+               "fontSize": "9.0pt (12px)",
+               "fontWeight": "normal",
+               "messageKey": null,
+             },
+             "id": "color-contrast",
+             "impact": "serious",
+             "message": "Element has insufficient color contrast of 3.56 (foreground color: #57544e, background color: #b3b2b0, font size: 9.0pt (12px), font weight: normal). Expected contrast ratio of 4.5:1",
+             "relatedNodes": Array [
+               Object {
+                 "html": "<div data-state=\"open\" data-slot=\"dialog-overlay\" class=\"fixed inset-0 z-50 bg-overlay image-viewer-overlay\" style=\"pointer-events: auto;\" data-aria-hidden=\"true\" aria-hidden=\"true\"></div>",
+                 "target": Array [
+                   ".fixed",
+                 ],
+               },
+               Object {
+                 "html": "<body data-scroll-locked=\"1\" style=\"pointer-events: none;\">",
+                 "target": Array [
+                   "body",
+                 ],
+               },
+             ],
+           },
+         ],
+         "failureSummary": "Fix any of the following:
+   Element has insufficient color contrast of 3.56 (foreground color: #57544e, background color: #b3b2b0, font size: 9.0pt (12px), font weight: normal). Expected contrast ratio of 4.5:1",
+         "html": "<span class=\"text-xs text-fg-2 whitespace-nowrap\" aria-live=\"polite\">1 / 3</span>",
+         "impact": "serious",
+         "none": Array [],
+         "target": Array [
+           ".text-fg-2.text-xs[aria-live=\"polite\"]",
+         ],
+       },
+     ],
+     "tags": Array [
+       "cat.color",
+       "wcag2aa",
+       "wcag143",
+       "TTv5",
+       "TT13.c",
+       "EN-301-549",
+       "EN-9.1.4.3",
+       "ACT",
+       "RGAAv4",
+       "RGAA-3.2.1",
+     ],
+   },
+ ]
```

# Page snapshot

```yaml
- generic:
  - generic:
    - generic:
      - complementary [aria-hidden]:
        - generic:
          - generic:
            - button
            - generic: Atelier
            - link:
              - /url: /
          - navigation:
            - generic:
              - textbox:
                - /placeholder: Search chats…
              - generic: ⌘K
            - navigation:
              - generic:
                - link:
                  - /url: /workflows
                  - text: Workflows
              - generic:
                - link:
                  - /url: /images
                  - text: Images
            - region:
              - generic:
                - heading [level=2]: Folders
                - button
              - paragraph: No folders yet
            - generic:
              - paragraph: Today
              - generic:
                - link:
                  - /url: /c/cdd6481253b74324843606cbf01b0146
                  - text: Synthetic cobalt mountains
                - button
            - generic:
              - generic:
                - link:
                  - /url: /c/b034d235210c4588b16d8098f33fdfbf
                  - text: Synthetic cobalt mountains
                - button
            - generic:
              - generic:
                - link:
                  - /url: /c/cdf78fd0d51e477bb77aba84aa595f4d
                  - text: Synthetic cobalt mountains
                - button
            - generic:
              - generic:
                - link:
                  - /url: /c/cedb288557404210a86c4cb986098e4a
                  - text: Synthetic cobalt mountains
                - button
            - generic:
              - generic:
                - link:
                  - /url: /c/46fb061bfe7940709ff9ecffdbf02caf
                  - text: Synthetic cobalt mountains
                - button
            - generic:
              - generic:
                - link:
                  - /url: /c/c739d7f3d89a417996ef8711bab8fdbe
                  - text: Synthetic cobalt mountains
                - button
            - generic:
              - generic:
                - link:
                  - /url: /c/25f34b6dbcc0460aab266dd916631d37
                  - text: Synthetic cobalt mountains
                - button
            - generic:
              - generic:
                - link:
                  - /url: /c/7d985dcd88df48f38fe770ccebcecd21
                  - text: Synthetic cobalt mountains
                - button
            - generic:
              - generic:
                - link:
                  - /url: /c/bd62367796644027823dba998bda7f78
                  - text: Synthetic cobalt mountains
                - button
            - generic:
              - generic:
                - link:
                  - /url: /c/892831376ea04417a30a4597518db4cf
                  - text: Synthetic cobalt mountains
                - button
            - generic:
              - generic:
                - link:
                  - /url: /c/918b9e3236f54a64a78f3b23ada79092
                  - text: Synthetic cobalt mountains
                - button
            - generic:
              - generic:
                - link:
                  - /url: /c/a0539299014b4941a1e4ae029907591a
                  - text: Synthetic cobalt mountains
                - button
            - generic:
              - generic:
                - link:
                  - /url: /c/30a062d1391048b4ba03125e796cc5b5
                  - text: Synthetic cobalt mountains
                - button
            - generic:
              - generic:
                - link:
                  - /url: /c/885e452b2d044907badc9f23347007bd
                  - text: Synthetic cobalt mountains
                - button
            - generic:
              - generic:
                - link:
                  - /url: /c/4585e74c58d149ae922510e92d1d16c1
                  - text: Synthetic cobalt mountains
                - button
            - generic:
              - generic:
                - link:
                  - /url: /c/0053a15aad894fb58607351892ae4204
                  - text: Synthetic cobalt mountains
                - button
            - generic:
              - generic:
                - link:
                  - /url: /c/6d2fdd8a7cd34db2a34c0305ce3ba8ee
                  - text: Synthetic cobalt mountains
                - button
            - generic:
              - generic:
                - link:
                  - /url: /c/042c9dc2290b4b549d634e9bcb856683
                  - text: Synthetic cobalt mountains
                - button
            - generic:
              - generic:
                - link:
                  - /url: /c/ada6e540bd25462db1008a2ff1bf7a8a
                  - text: Synthetic cobalt mountains
                - button
            - generic:
              - generic:
                - link:
                  - /url: /c/a107b0c8fc9f403f8317d9a7c81d9fd8
                  - text: Synthetic cobalt mountains
                - button
          - generic:
            - button: Settings
      - main:
        - generic [aria-hidden]:
          - generic:
            - button:
              - generic [aria-hidden]: ●
              - generic: fake-chat
              - generic: Fake runtime
          - generic: Synthetic cobalt mountains
          - button
          - button
        - status [aria-hidden]
        - log "Conversation":
          - generic:
            - article "user message":
              - heading "You said" [level=2]
              - generic:
                - paragraph: Image · 3 images
                - paragraph: Synthetic cobalt mountains
              - generic:
                - generic:
                  - generic:
                    - button "Copy message":
                      - status
            - article "assistant message":
              - heading "Assistant replied" [level=2]
              - generic:
                - paragraph: FLUX.2 klein 4B
                - group "Images in this turn":
                  - generic:
                    - button "Open image 1":
                      - img "Synthetic cobalt mountains"
                    - generic:
                      - button "Save image"
                      - button "More like this"
                      - button "Refine image"
                      - button "Copy image prompt":
                        - status
                      - button "Image details"
                      - button "More image actions"
                  - generic:
                    - button "Open image 2":
                      - img "Synthetic cobalt mountains"
                    - generic:
                      - button "Save image"
                      - button "More like this"
                      - button "Refine image"
                      - button "Copy image prompt":
                        - status
                      - button "Image details"
                      - button "More image actions"
                  - generic:
                    - button "Open image 3":
                      - img "Synthetic cobalt mountains"
                    - generic:
                      - button "Save image"
                      - button "More like this"
                      - button "Refine image"
                      - button "Copy image prompt":
                        - status
                      - button "Image details"
                      - button "More image actions"
                - status:
                  - generic: 3 images · 1 s
                - generic:
                  - button "Try again"
                  - button "Copy prompt":
                    - status
                    - text: Copy prompt
        - generic [aria-hidden]:
          - button [aria-hidden]
          - form:
            - textbox:
              - /placeholder: Message fake-chat…
            - generic:
              - button
              - button:
                - generic: Search
              - generic:
                - button:
                  - generic: Image
              - generic:
                - button [disabled]:
                  - generic: Library
                - button
              - generic:
                - generic:
                  - button [disabled]
    - region "Notifications alt+T"
  - dialog [ref=e2]:
    - heading "Image viewer" [level=2] [ref=e3]
    - paragraph [ref=e4]: Use arrow keys or swipe to view the images in this conversation. Double tap or use Zoom to see actual size.
    - banner [ref=e5]:
      - button "Expand image prompt" [ref=e6] [cursor=pointer]: Synthetic cobalt mountains
      - generic [ref=e7]: 1 / 3
      - button "Close image viewer" [ref=e8] [cursor=pointer]
    - generic [active] [ref=e9]:
      - generic:
        - generic:
          - img "Synthetic cobalt mountains"
      - button "Previous image" [ref=e10] [cursor=pointer]
      - button "Next image" [ref=e11] [cursor=pointer]
    - contentinfo [ref=e12]:
      - generic [ref=e13]:
        - button "Save image" [ref=e14] [cursor=pointer]:
          - generic [ref=e15]: Save
        - button "More like this" [ref=e16] [cursor=pointer]
        - button "Refine image" [ref=e18] [cursor=pointer]:
          - generic [ref=e19]: Refine
        - button "Copy image prompt" [ref=e20] [cursor=pointer]:
          - status [ref=e21]
          - generic [ref=e22]: Copy prompt
        - button "Image details" [ref=e23] [cursor=pointer]:
          - generic [ref=e24]: Details
      - button "Zoom to actual size" [ref=e25] [cursor=pointer]
```

# Test source

```ts
  259 |     source_job_id: data.assistant.images[0].id,
  260 |     count: 1,
  261 |   });
  262 |   await page.unroute("**/api/chats/*/images");
  263 |   await expect(page.locator('[data-slot="image-turn"]')).toHaveCount(2);
  264 |   await page.getByRole("button", { name: "Leave image mode" }).click();
  265 |   await expect(text).toHaveValue("Synthetic saved text draft");
  266 |   const newest = page.locator('[data-slot="image-turn"]').last();
  267 |   await expect(newest.locator("img")).toBeVisible();
  268 |   const source = await newest
  269 |     .locator("[data-job-id]")
  270 |     .getAttribute("data-job-id");
  271 |   await newest
  272 |     .getByRole("button", { name: "More like this", exact: true })
  273 |     .click();
  274 |   await expect(page.locator('[data-slot="image-turn"]')).toHaveCount(3);
  275 |   const detail = await request
  276 |     .get(`/api/chats/${chat.id}`)
  277 |     .then((r) => r.json());
  278 |   expect(detail.messages.at(-1).images[0]).toMatchObject({
  279 |     parent_id: source,
  280 |     prompt: "Synthetic refined cobalt shapes",
  281 |   });
  282 |   const last = page.locator('[data-slot="image-turn"]').last();
  283 |   await expect(last.locator("img")).toBeVisible();
  284 |   await last.getByRole("button", { name: "Refine image" }).click();
  285 |   await page.getByRole("button", { name: "Remove refinement source" }).click();
  286 |   await expect(page.locator('[data-slot="image-refinement"]')).toHaveCount(0);
  287 |   await expect(field).toHaveValue("Synthetic refined cobalt shapes");
  288 | });
  289 | test("Ask about it is metadata gated and uses the existing image upload without sending", async ({
  290 |   page,
  291 |   request,
  292 | }) => {
  293 |   const { chat } = await seed(request, 1);
  294 |   await page.goto(`/c/${chat.id}`);
  295 |   const turn = page.locator('[data-slot="image-turn"]');
  296 |   await expect(turn.locator("img")).toBeVisible();
  297 |   await turn.getByRole("button", { name: "More image actions" }).click();
  298 |   await expect(
  299 |     page.getByRole("menuitem", { name: "Ask about it" }),
  300 |   ).toHaveCount(0);
  301 |   await page.keyboard.press("Escape");
  302 |   const detail = await request
  303 |     .get(`/api/chats/${chat.id}`)
  304 |     .then((r) => r.json());
  305 |   await request.patch(`/api/chats/${chat.id}`, {
  306 |     data: { connection_id: detail.chat.connection_id, model_id: "fake-vision" },
  307 |   });
  308 |   await page.reload();
  309 |   await turn.getByRole("button", { name: "More image actions" }).click();
  310 |   await expect(
  311 |     page.getByRole("menuitem", { name: "Ask about it" }),
  312 |   ).toBeVisible();
  313 |   let sends = 0;
  314 |   page.on("request", (r) => {
  315 |     if (r.method() === "POST" && r.url().endsWith("/messages")) sends++;
  316 |   });
  317 |   await page.getByRole("menuitem", { name: "Ask about it" }).click();
  318 |   await expect(
  319 |     page.locator('.composer [data-slot="attachment-chip"]'),
  320 |   ).toBeVisible();
  321 |   await expect(page.locator(".composer textarea")).toHaveAttribute(
  322 |     "aria-label",
  323 |     /^Message /,
  324 |   );
  325 |   expect(sends).toBe(0);
  326 | });
  327 | for (const mode of ["system", "always"])
  328 |   test(`viewer respects ${mode} reduced motion`, async ({ page, request }) => {
  329 |     if (mode === "system") await page.emulateMedia({ reducedMotion: "reduce" });
  330 |     else
  331 |       await request.patch("/api/settings", {
  332 |         data: { "appearance.reduce_motion": "always" },
  333 |       });
  334 |     await open(page, request, 1);
  335 |     await expect(viewer(page).locator(".image-viewer-fit")).toHaveCSS(
  336 |       "transition-duration",
  337 |       "0s",
  338 |     );
  339 |     await viewer(page)
  340 |       .getByRole("button", { name: "Close image viewer" })
  341 |       .click();
  342 |     await expect(viewer(page)).not.toBeVisible();
  343 |   });
  344 | for (const width of [390, 1440])
  345 |   for (const theme of ["dark", "light"])
  346 |     test(`CI-C axe ${theme} ${width}`, async ({ page, request }, info) => {
  347 |       await page.setViewportSize({ width, height: 900 });
  348 |       await page.emulateMedia({ colorScheme: theme as "dark" | "light" });
  349 |       await request.patch("/api/settings", {
  350 |         data: { "appearance.theme": theme },
  351 |       });
  352 |       await open(page, request, 3);
  353 |       await settle(page);
  354 |       const results = await new AxeBuilder({ page }).analyze();
  355 |       expect(
  356 |         results.violations.filter((v) =>
  357 |           ["serious", "critical"].includes(v.impact ?? ""),
  358 |         ),
> 359 |       ).toEqual([]);
      |         ^ Error: expect(received).toEqual(expected) // deep equality
  360 |       await mkdir(dir, { recursive: true });
  361 |       await writeFile(
  362 |         `${dir}/viewer-axe-${theme}-${width}-${info.project.name}-fake.json`,
  363 |         JSON.stringify(results, null, 2),
  364 |       );
  365 |       await page.screenshot({
  366 |         path: `${dir}/viewer-${theme}-${width}-${info.project.name}-fake.png`,
  367 |       });
  368 |       await viewer(page).getByRole("button", { name: "Refine image" }).click();
  369 |       await expect(
  370 |         page.locator('[data-slot="image-refinement"]'),
  371 |       ).toBeVisible();
  372 |       await settle(page);
  373 |       const refine = await new AxeBuilder({ page }).analyze();
  374 |       expect(
  375 |         refine.violations.filter((v) =>
  376 |           ["serious", "critical"].includes(v.impact ?? ""),
  377 |         ),
  378 |       ).toEqual([]);
  379 |       await writeFile(
  380 |         `${dir}/refine-axe-${theme}-${width}-${info.project.name}-fake.json`,
  381 |         JSON.stringify(refine, null, 2),
  382 |       );
  383 |       await page.screenshot({
  384 |         path: `${dir}/refine-${theme}-${width}-${info.project.name}-fake.png`,
  385 |       });
  386 |     });
  387 | 
```