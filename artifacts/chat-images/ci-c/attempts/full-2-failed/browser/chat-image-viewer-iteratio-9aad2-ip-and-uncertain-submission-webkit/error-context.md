# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: chat-image-viewer.spec.ts >> iteration preserves text draft, source lineage, removable chip and uncertain submission
- Location: tests/chat-image-viewer.spec.ts:228:1

# Error details

```
Error: expect(locator).toBeFocused() failed

Locator:  getByRole('textbox', { name: 'Image prompt', exact: true })
Expected: focused
Received: inactive
Timeout:  5000ms

Call log:
  - Expect "toBeFocused" getByRole('textbox', { name: 'Image prompt', exact: true }) with timeout 5000ms
  - waiting for getByRole('textbox', { name: 'Image prompt', exact: true })
    14 × locator resolved to <textarea rows="2" aria-label="Image prompt" placeholder="Describe an image…">Synthetic cobalt mountains</textarea>
       - unexpected value "inactive"

```

```yaml
- textbox "Image prompt":
  - /placeholder: Describe an image…
  - text: Synthetic cobalt mountains
```

# Test source

```ts
  140 |   await viewer(page).getByRole("button", { name: "Image details" }).click();
  141 |   await page
  142 |     .getByRole("dialog", { name: "Image details", exact: true })
  143 |     .getByRole("button", { name: "Close", exact: true })
  144 |     .click();
  145 |   await expect(
  146 |     page.getByRole("dialog", { name: "Image details", exact: true }),
  147 |   ).not.toBeVisible();
  148 |   await settle(page);
  149 |   await page.keyboard.press("Escape");
  150 |   await expect(viewer(page)).not.toBeVisible();
  151 |   await expect(opening).toBeFocused();
  152 |   await mkdir(dir, { recursive: true });
  153 |   await page.screenshot({
  154 |     path: `${dir}/conversation-${info.project.name}-fake.png`,
  155 |   });
  156 | });
  157 | test("phone snap dots and viewer pinch, pan, double tap, swipe down", async ({
  158 |   page,
  159 |   request,
  160 | }) => {
  161 |   await page.setViewportSize({ width: 390, height: 844 });
  162 |   await page.emulateMedia({ reducedMotion: "no-preference" });
  163 |   await open(page, request);
  164 |   const stage = viewer(page).locator(".image-viewer-stage");
  165 |   const box = await stage.boundingBox();
  166 |   const x = box!.x + box!.width / 2,
  167 |     y = box!.y + box!.height / 2;
  168 |   for (const [id, px] of [
  169 |     [51, x - 40],
  170 |     [52, x + 40],
  171 |   ])
  172 |     await stage.dispatchEvent("pointerdown", {
  173 |       pointerId: id,
  174 |       pointerType: "touch",
  175 |       clientX: px,
  176 |       clientY: y,
  177 |     });
  178 |   await stage.dispatchEvent("pointermove", {
  179 |     pointerId: 52,
  180 |     pointerType: "touch",
  181 |     clientX: x + 120,
  182 |     clientY: y,
  183 |   });
  184 |   await expect(stage).toHaveAttribute("data-zoom", "2.00");
  185 |   for (const id of [51, 52])
  186 |     await stage.dispatchEvent("pointerup", {
  187 |       pointerId: id,
  188 |       pointerType: "touch",
  189 |       clientX: x,
  190 |       clientY: y,
  191 |     });
  192 |   await viewer(page).getByRole("button", { name: "Fit image" }).click();
  193 |   // A pair of touch taps on the actual image toggles actual size.
  194 |   const output = viewer(page).locator(".image-viewer-output");
  195 |   for (let n = 0; n < 2; n++) {
  196 |     await output.dispatchEvent("pointerdown", {
  197 |       pointerId: 61,
  198 |       pointerType: "touch",
  199 |       clientX: x,
  200 |       clientY: y,
  201 |     });
  202 |     await output.dispatchEvent("pointerup", {
  203 |       pointerId: 61,
  204 |       pointerType: "touch",
  205 |       clientX: x,
  206 |       clientY: y,
  207 |     });
  208 |   }
  209 |   await expect(stage).not.toHaveAttribute("data-zoom", "1.00");
  210 |   await swipe(page, 40, 0);
  211 |   await expect(viewer(page).getByText("1 / 3", { exact: true })).toBeVisible();
  212 |   await viewer(page).getByRole("button", { name: "Fit image" }).click();
  213 |   await swipe(page, 0, 110);
  214 |   await expect(viewer(page)).not.toBeVisible();
  215 |   const row = page.locator(".image-frames");
  216 |   await expect(row).toHaveCSS("scroll-snap-type", "x mandatory");
  217 |   await page.getByRole("button", { name: "Show image 3" }).click();
  218 |   await expect(
  219 |     page.getByRole("button", { name: "Show image 3" }),
  220 |   ).toHaveAttribute("aria-current", "true");
  221 |   await expect(
  222 |     page
  223 |       .locator(".image-frame-actions")
  224 |       .last()
  225 |       .getByRole("button", { name: "Refine image" }),
  226 |   ).toBeVisible();
  227 | });
  228 | test("iteration preserves text draft, source lineage, removable chip and uncertain submission", async ({
  229 |   page,
  230 |   request,
  231 | }) => {
  232 |   const { chat, data } = await open(page, request, 1);
  233 |   await viewer(page).getByRole("button", { name: "Refine image" }).click();
  234 |   await expect(viewer(page)).not.toBeVisible();
  235 |   const field = page.getByRole("textbox", {
  236 |     name: "Image prompt",
  237 |     exact: true,
  238 |   });
  239 |   await expect(field).toHaveValue("Synthetic cobalt mountains");
> 240 |   await expect(field).toBeFocused();
      |                       ^ Error: expect(locator).toBeFocused() failed
  241 |   expect(
  242 |     await field.evaluate((el: HTMLTextAreaElement) => el.selectionStart),
  243 |   ).toBe("Synthetic cobalt mountains".length);
  244 |   await expect(page.locator('[data-slot="image-refinement"]')).toContainText(
  245 |     "seed 101",
  246 |   );
  247 |   await page.getByRole("button", { name: "Leave image mode" }).click();
  248 |   const text = page.locator(".composer textarea");
  249 |   await text.fill("Synthetic saved text draft");
  250 |   await page.getByRole("button", { name: "Create image", exact: true }).click();
  251 |   await field.fill("Synthetic refined cobalt shapes");
  252 |   const bodies: unknown[] = [];
  253 |   await page.route("**/api/chats/*/images", async (route) => {
  254 |     bodies.push(route.request().postDataJSON());
  255 |     if (bodies.length === 1) {
  256 |       await route.fetch();
  257 |       await route.abort("failed");
  258 |     } else await route.continue();
  259 |   });
  260 |   await page.getByRole("button", { name: "Create image", exact: true }).click();
  261 |   await expect(page.getByRole("alert")).toBeVisible();
  262 |   await expect(page.locator('[data-slot="image-refinement"]')).toBeVisible();
  263 |   await page.getByRole("button", { name: "Create image", exact: true }).click();
  264 |   await expect(field).toHaveValue("");
  265 |   expect(bodies[1]).toEqual(bodies[0]);
  266 |   expect(bodies[0]).toMatchObject({
  267 |     source_job_id: data.assistant.images[0].id,
  268 |     count: 1,
  269 |   });
  270 |   await page.unroute("**/api/chats/*/images");
  271 |   await expect(page.locator('[data-slot="image-turn"]')).toHaveCount(2);
  272 |   await page.getByRole("button", { name: "Leave image mode" }).click();
  273 |   await expect(text).toHaveValue("Synthetic saved text draft");
  274 |   await workspaceLink(page, "Workflows");
  275 |   await page.goBack();
  276 |   await expect(text).toHaveAttribute("aria-label", "Message fake-chat");
  277 |   await expect(text).toHaveValue("Synthetic saved text draft");
  278 |   const newest = page.locator('[data-slot="image-turn"]').last();
  279 |   await expect(newest.locator("img")).toBeVisible();
  280 |   const source = await newest
  281 |     .locator("[data-job-id]")
  282 |     .getAttribute("data-job-id");
  283 |   await newest
  284 |     .getByRole("button", { name: "More like this", exact: true })
  285 |     .click();
  286 |   await expect(page.locator('[data-slot="image-turn"]')).toHaveCount(3);
  287 |   const detail = await request
  288 |     .get(`/api/chats/${chat.id}`)
  289 |     .then((r) => r.json());
  290 |   expect(detail.messages.at(-1).images[0]).toMatchObject({
  291 |     parent_id: source,
  292 |     prompt: "Synthetic refined cobalt shapes",
  293 |   });
  294 |   const last = page.locator('[data-slot="image-turn"]').last();
  295 |   await expect(last.locator("img")).toBeVisible();
  296 |   await last.getByRole("button", { name: "Refine image" }).click();
  297 |   await page.getByRole("button", { name: "Remove refinement source" }).click();
  298 |   await expect(page.locator('[data-slot="image-refinement"]')).toHaveCount(0);
  299 |   await expect(field).toHaveValue("Synthetic refined cobalt shapes");
  300 | });
  301 | test("Ask about it is metadata gated and uses the existing image upload without sending", async ({
  302 |   page,
  303 |   request,
  304 | }) => {
  305 |   const { chat } = await seed(request, 1);
  306 |   await page.goto(`/c/${chat.id}`);
  307 |   const turn = page.locator('[data-slot="image-turn"]');
  308 |   await expect(turn.locator("img")).toBeVisible();
  309 |   await turn.getByRole("button", { name: "More image actions" }).click();
  310 |   await expect(
  311 |     page.getByRole("menuitem", { name: "Ask about it" }),
  312 |   ).toHaveCount(0);
  313 |   await page.keyboard.press("Escape");
  314 |   const detail = await request
  315 |     .get(`/api/chats/${chat.id}`)
  316 |     .then((r) => r.json());
  317 |   await request.patch(`/api/chats/${chat.id}`, {
  318 |     data: { connection_id: detail.chat.connection_id, model_id: "fake-vision" },
  319 |   });
  320 |   await page.reload();
  321 |   await turn.getByRole("button", { name: "More image actions" }).click();
  322 |   await expect(
  323 |     page.getByRole("menuitem", { name: "Ask about it" }),
  324 |   ).toBeVisible();
  325 |   let sends = 0;
  326 |   page.on("request", (r) => {
  327 |     if (r.method() === "POST" && r.url().endsWith("/messages")) sends++;
  328 |   });
  329 |   await page.getByRole("menuitem", { name: "Ask about it" }).click();
  330 |   await expect(
  331 |     page.locator('.composer [data-slot="attachment-chip"]'),
  332 |   ).toBeVisible();
  333 |   await expect(page.locator(".composer textarea")).toHaveAttribute(
  334 |     "aria-label",
  335 |     /^Message /,
  336 |   );
  337 |   expect(sends).toBe(0);
  338 | });
  339 | for (const mode of ["system", "always"])
  340 |   test(`viewer respects ${mode} reduced motion`, async ({ page, request }) => {
```