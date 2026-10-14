# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: chat-image-viewer.spec.ts >> iteration preserves text draft, source lineage, removable chip and uncertain submission
- Location: tests/chat-image-viewer.spec.ts:227:1

# Error details

```
Test timeout of 45000ms exceeded.
```

```
Error: locator.click: Test timeout of 45000ms exceeded.
Call log:
  - waiting for getByRole('link', { name: 'Back to chat', exact: true })

```

# Page snapshot

```yaml
- generic [ref=f1e2]:
  - main [ref=f1e4]:
    - generic [ref=f1e5]:
      - button "Open sidebar" [ref=f1e6] [cursor=pointer]
      - link "Workflows" [ref=f1e7]:
        - /url: /workflows
    - region "Workflows" [ref=f1e8]:
      - generic [ref=f1e9]:
        - generic [ref=f1e10]:
          - heading "Workflows" [level=1] [ref=f1e11]
          - paragraph [ref=f1e12]: Chain models, search, images and recordings into repeatable steps.Runs keep going on your Mac when you close the app.
        - generic [ref=f1e13]:
          - button "New workflow" [ref=f1e14] [cursor=pointer]
          - button "New workflow options" [ref=f1e15] [cursor=pointer]
      - button "Import workflow JSON" [ref=f1e16]
      - generic [ref=f1e17]:
        - heading "Build your first workflow" [level=2] [ref=f1e18]
        - paragraph [ref=f1e19]: Pick a template or start blank. You can change every step.
      - region "Workflow templates" [ref=f1e20]:
        - heading "START FROM A TEMPLATE" [level=2] [ref=f1e21]
        - generic [ref=f1e22]:
          - button "Use Brief to images template" [ref=f1e23] [cursor=pointer]: Brief to images
          - button "Use Recording to meeting pack template" [ref=f1e24] [cursor=pointer]: Recording to meeting pack
          - button "Start blank" [ref=f1e25] [cursor=pointer]
      - region "Recent workflow runs" [ref=f1e26]:
        - generic [ref=f1e27]:
          - heading "RECENT RUNS" [level=2] [ref=f1e28]
          - link "View all runs" [ref=f1e29]:
            - /url: /workflows/runs
        - paragraph [ref=f1e30]: No runs yet. Choose a template to get started.
  - region "Notifications alt+T"
```

# Test source

```ts
  174 |       clientX: px,
  175 |       clientY: y,
  176 |     });
  177 |   await stage.dispatchEvent("pointermove", {
  178 |     pointerId: 52,
  179 |     pointerType: "touch",
  180 |     clientX: x + 120,
  181 |     clientY: y,
  182 |   });
  183 |   await expect(stage).toHaveAttribute("data-zoom", "2.00");
  184 |   for (const id of [51, 52])
  185 |     await stage.dispatchEvent("pointerup", {
  186 |       pointerId: id,
  187 |       pointerType: "touch",
  188 |       clientX: x,
  189 |       clientY: y,
  190 |     });
  191 |   await viewer(page).getByRole("button", { name: "Fit image" }).click();
  192 |   // A pair of touch taps on the actual image toggles actual size.
  193 |   const output = viewer(page).locator(".image-viewer-output");
  194 |   for (let n = 0; n < 2; n++) {
  195 |     await output.dispatchEvent("pointerdown", {
  196 |       pointerId: 61,
  197 |       pointerType: "touch",
  198 |       clientX: x,
  199 |       clientY: y,
  200 |     });
  201 |     await output.dispatchEvent("pointerup", {
  202 |       pointerId: 61,
  203 |       pointerType: "touch",
  204 |       clientX: x,
  205 |       clientY: y,
  206 |     });
  207 |   }
  208 |   await expect(stage).not.toHaveAttribute("data-zoom", "1.00");
  209 |   await swipe(page, 40, 0);
  210 |   await expect(viewer(page).getByText("1 / 3", { exact: true })).toBeVisible();
  211 |   await viewer(page).getByRole("button", { name: "Fit image" }).click();
  212 |   await swipe(page, 0, 110);
  213 |   await expect(viewer(page)).not.toBeVisible();
  214 |   const row = page.locator(".image-frames");
  215 |   await expect(row).toHaveCSS("scroll-snap-type", "x mandatory");
  216 |   await page.getByRole("button", { name: "Show image 3" }).click();
  217 |   await expect(
  218 |     page.getByRole("button", { name: "Show image 3" }),
  219 |   ).toHaveAttribute("aria-current", "true");
  220 |   await expect(
  221 |     page
  222 |       .locator(".image-frame-actions")
  223 |       .last()
  224 |       .getByRole("button", { name: "Refine image" }),
  225 |   ).toBeVisible();
  226 | });
  227 | test("iteration preserves text draft, source lineage, removable chip and uncertain submission", async ({
  228 |   page,
  229 |   request,
  230 | }) => {
  231 |   const { chat, data } = await open(page, request, 1);
  232 |   await viewer(page).getByRole("button", { name: "Refine image" }).click();
  233 |   await expect(viewer(page)).not.toBeVisible();
  234 |   const field = page.getByRole("textbox", {
  235 |     name: "Image prompt",
  236 |     exact: true,
  237 |   });
  238 |   await expect(field).toHaveValue("Synthetic cobalt mountains");
  239 |   await expect(field).toBeFocused();
  240 |   expect(
  241 |     await field.evaluate((el: HTMLTextAreaElement) => el.selectionStart),
  242 |   ).toBe("Synthetic cobalt mountains".length);
  243 |   await expect(page.locator('[data-slot="image-refinement"]')).toContainText(
  244 |     "seed 101",
  245 |   );
  246 |   await page.getByRole("button", { name: "Leave image mode" }).click();
  247 |   const text = page.locator(".composer textarea");
  248 |   await text.fill("Synthetic saved text draft");
  249 |   await page.getByRole("button", { name: "Create image", exact: true }).click();
  250 |   await field.fill("Synthetic refined cobalt shapes");
  251 |   const bodies: unknown[] = [];
  252 |   await page.route("**/api/chats/*/images", async (route) => {
  253 |     bodies.push(route.request().postDataJSON());
  254 |     if (bodies.length === 1) {
  255 |       await route.fetch();
  256 |       await route.abort("failed");
  257 |     } else await route.continue();
  258 |   });
  259 |   await page.getByRole("button", { name: "Create image", exact: true }).click();
  260 |   await expect(page.getByRole("alert")).toBeVisible();
  261 |   await expect(page.locator('[data-slot="image-refinement"]')).toBeVisible();
  262 |   await page.getByRole("button", { name: "Create image", exact: true }).click();
  263 |   await expect(field).toHaveValue("");
  264 |   expect(bodies[1]).toEqual(bodies[0]);
  265 |   expect(bodies[0]).toMatchObject({
  266 |     source_job_id: data.assistant.images[0].id,
  267 |     count: 1,
  268 |   });
  269 |   await page.unroute("**/api/chats/*/images");
  270 |   await expect(page.locator('[data-slot="image-turn"]')).toHaveCount(2);
  271 |   await page.getByRole("button", { name: "Leave image mode" }).click();
  272 |   await expect(text).toHaveValue("Synthetic saved text draft");
  273 |   await page.goto("/workflows");
> 274 |   await page.getByRole("link", { name: "Back to chat", exact: true }).click();
      |                                                                       ^ Error: locator.click: Test timeout of 45000ms exceeded.
  275 |   await expect(text).toHaveAttribute("aria-label", "Message");
  276 |   await expect(text).toHaveValue("Synthetic saved text draft");
  277 |   const newest = page.locator('[data-slot="image-turn"]').last();
  278 |   await expect(newest.locator("img")).toBeVisible();
  279 |   const source = await newest
  280 |     .locator("[data-job-id]")
  281 |     .getAttribute("data-job-id");
  282 |   await newest
  283 |     .getByRole("button", { name: "More like this", exact: true })
  284 |     .click();
  285 |   await expect(page.locator('[data-slot="image-turn"]')).toHaveCount(3);
  286 |   const detail = await request
  287 |     .get(`/api/chats/${chat.id}`)
  288 |     .then((r) => r.json());
  289 |   expect(detail.messages.at(-1).images[0]).toMatchObject({
  290 |     parent_id: source,
  291 |     prompt: "Synthetic refined cobalt shapes",
  292 |   });
  293 |   const last = page.locator('[data-slot="image-turn"]').last();
  294 |   await expect(last.locator("img")).toBeVisible();
  295 |   await last.getByRole("button", { name: "Refine image" }).click();
  296 |   await page.getByRole("button", { name: "Remove refinement source" }).click();
  297 |   await expect(page.locator('[data-slot="image-refinement"]')).toHaveCount(0);
  298 |   await expect(field).toHaveValue("Synthetic refined cobalt shapes");
  299 | });
  300 | test("Ask about it is metadata gated and uses the existing image upload without sending", async ({
  301 |   page,
  302 |   request,
  303 | }) => {
  304 |   const { chat } = await seed(request, 1);
  305 |   await page.goto(`/c/${chat.id}`);
  306 |   const turn = page.locator('[data-slot="image-turn"]');
  307 |   await expect(turn.locator("img")).toBeVisible();
  308 |   await turn.getByRole("button", { name: "More image actions" }).click();
  309 |   await expect(
  310 |     page.getByRole("menuitem", { name: "Ask about it" }),
  311 |   ).toHaveCount(0);
  312 |   await page.keyboard.press("Escape");
  313 |   const detail = await request
  314 |     .get(`/api/chats/${chat.id}`)
  315 |     .then((r) => r.json());
  316 |   await request.patch(`/api/chats/${chat.id}`, {
  317 |     data: { connection_id: detail.chat.connection_id, model_id: "fake-vision" },
  318 |   });
  319 |   await page.reload();
  320 |   await turn.getByRole("button", { name: "More image actions" }).click();
  321 |   await expect(
  322 |     page.getByRole("menuitem", { name: "Ask about it" }),
  323 |   ).toBeVisible();
  324 |   let sends = 0;
  325 |   page.on("request", (r) => {
  326 |     if (r.method() === "POST" && r.url().endsWith("/messages")) sends++;
  327 |   });
  328 |   await page.getByRole("menuitem", { name: "Ask about it" }).click();
  329 |   await expect(
  330 |     page.locator('.composer [data-slot="attachment-chip"]'),
  331 |   ).toBeVisible();
  332 |   await expect(page.locator(".composer textarea")).toHaveAttribute(
  333 |     "aria-label",
  334 |     /^Message /,
  335 |   );
  336 |   expect(sends).toBe(0);
  337 | });
  338 | for (const mode of ["system", "always"])
  339 |   test(`viewer respects ${mode} reduced motion`, async ({ page, request }) => {
  340 |     if (mode === "system") await page.emulateMedia({ reducedMotion: "reduce" });
  341 |     else
  342 |       await request.patch("/api/settings", {
  343 |         data: { "appearance.reduce_motion": "always" },
  344 |       });
  345 |     await open(page, request, 1);
  346 |     await expect(viewer(page).locator(".image-viewer-fit")).toHaveCSS(
  347 |       "transition-duration",
  348 |       "0s",
  349 |     );
  350 |     await viewer(page)
  351 |       .getByRole("button", { name: "Close image viewer" })
  352 |       .click();
  353 |     await expect(viewer(page)).not.toBeVisible();
  354 |   });
  355 | for (const width of [390, 1440])
  356 |   for (const theme of ["dark", "light"])
  357 |     test(`CI-C axe ${theme} ${width}`, async ({ page, request }, info) => {
  358 |       await page.setViewportSize({ width, height: 900 });
  359 |       await page.emulateMedia({ colorScheme: theme as "dark" | "light" });
  360 |       await request.patch("/api/settings", {
  361 |         data: { "appearance.theme": theme },
  362 |       });
  363 |       await open(page, request, 3);
  364 |       await settle(page);
  365 |       const results = await new AxeBuilder({ page }).analyze();
  366 |       expect(
  367 |         results.violations.filter((v) =>
  368 |           ["serious", "critical"].includes(v.impact ?? ""),
  369 |         ),
  370 |       ).toEqual([]);
  371 |       await mkdir(dir, { recursive: true });
  372 |       await writeFile(
  373 |         `${dir}/viewer-axe-${theme}-${width}-${info.project.name}-fake.json`,
  374 |         JSON.stringify(results, null, 2),
```