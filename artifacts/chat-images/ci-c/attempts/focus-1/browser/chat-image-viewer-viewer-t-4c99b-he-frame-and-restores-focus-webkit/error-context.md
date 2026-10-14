# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: chat-image-viewer.spec.ts >> viewer traverses the conversation, zooms from/to the frame and restores focus
- Location: tests/chat-image-viewer.spec.ts:92:1

# Error details

```
Error: expect(locator).not.toBeVisible() failed

Locator:  getByRole('dialog', { name: 'Image viewer', exact: true })
Expected: not visible
Received: visible
Timeout:  5000ms

Call log:
  - Expect "not toBeVisible" getByRole('dialog', { name: 'Image viewer', exact: true }) with timeout 5000ms
  - waiting for getByRole('dialog', { name: 'Image viewer', exact: true })
    14 × locator resolved to <div role="dialog" tabindex="-1" id="radix-_r_2u_" data-state="open" class="image-viewer" data-slot="image-viewer" aria-labelledby="radix-_r_2v_" aria-describedby="radix-_r_30_">…</div>
       - unexpected value "visible"

```

```yaml
- dialog "Image viewer":
  - heading "Image viewer" [level=2]
  - paragraph: Use arrow keys or swipe to view the images in this conversation. Double tap or use Zoom to see actual size.
  - banner
  - img "Synthetic cobalt mountains"
  - contentinfo
```

# Test source

```ts
  42  |         seeds: [101, 102, 103].slice(0, count),
  43  |       },
  44  |     })
  45  |     .then((r) => r.json());
  46  |   return { chat, data };
  47  | }
  48  | async function open(page: Page, request: APIRequestContext, count = 3) {
  49  |   const seeded = await seed(request, count);
  50  |   await page.goto(`/c/${seeded.chat.id}`);
  51  |   await expect(frames(page)).toHaveCount(count);
  52  |   await expect(
  53  |     page.locator('[data-slot="image-turn"] .image-output').last(),
  54  |   ).toHaveClass(/is-loaded/);
  55  |   await frames(page).first().scrollIntoViewIfNeeded();
  56  |   await frames(page).first().click();
  57  |   await expect(viewer(page)).toBeVisible();
  58  |   await settle(page);
  59  |   return seeded;
  60  | }
  61  | async function swipe(page: Page, x: number, y: number) {
  62  |   const stage = viewer(page).locator(".image-viewer-stage"),
  63  |     box = await stage.boundingBox();
  64  |   const cx = box!.x + box!.width / 2,
  65  |     cy = box!.y + box!.height / 2;
  66  |   await stage.dispatchEvent("pointerdown", {
  67  |     pointerId: 31,
  68  |     pointerType: "touch",
  69  |     clientX: cx,
  70  |     clientY: cy,
  71  |     bubbles: true,
  72  |   });
  73  |   await stage.dispatchEvent("pointermove", {
  74  |     pointerId: 31,
  75  |     pointerType: "touch",
  76  |     clientX: cx + x,
  77  |     clientY: cy + y,
  78  |     bubbles: true,
  79  |   });
  80  |   await expect(stage.locator(".image-viewer-pan")).not.toHaveCSS(
  81  |     "transform",
  82  |     "none",
  83  |   );
  84  |   await stage.dispatchEvent("pointerup", {
  85  |     pointerId: 31,
  86  |     pointerType: "touch",
  87  |     clientX: cx + x,
  88  |     clientY: cy + y,
  89  |     bubbles: true,
  90  |   });
  91  | }
  92  | test("viewer traverses the conversation, zooms from/to the frame and restores focus", async ({
  93  |   page,
  94  |   request,
  95  | }, info) => {
  96  |   await page.emulateMedia({ reducedMotion: "no-preference" });
  97  |   const { chat } = await seed(request, 2);
  98  |   await request.post(`/api/chats/${chat.id}/images`, {
  99  |     data: {
  100 |       request_key: crypto.randomUUID(),
  101 |       prompt: "Synthetic warm shapes",
  102 |       count: 1,
  103 |       seeds: [201],
  104 |     },
  105 |   });
  106 |   await page.goto(`/c/${chat.id}`);
  107 |   await expect(frames(page)).toHaveCount(3);
  108 |   const opening = frames(page).first();
  109 |   await opening.scrollIntoViewIfNeeded();
  110 |   await opening.focus();
  111 |   await page.keyboard.press("Enter");
  112 |   await expect(viewer(page)).toBeVisible();
  113 |   await expect(viewer(page).getByText("1 / 3", { exact: true })).toBeVisible();
  114 |   expect(
  115 |     await viewer(page)
  116 |       .locator(".image-viewer-fit")
  117 |       .evaluate((el) => getComputedStyle(el).transitionDuration),
  118 |   ).toBe("0.32s");
  119 |   await settle(page);
  120 |   await page.keyboard.press("ArrowRight");
  121 |   await expect(viewer(page).getByText("2 / 3", { exact: true })).toBeVisible();
  122 |   await page.keyboard.press("ArrowRight");
  123 |   await expect(viewer(page).getByText("3 / 3", { exact: true })).toBeVisible();
  124 |   await page.keyboard.press("ArrowRight");
  125 |   await expect(viewer(page).getByText("1 / 3", { exact: true })).toBeVisible();
  126 |   await swipe(page, -100, 0);
  127 |   await expect(viewer(page).getByText("2 / 3", { exact: true })).toBeVisible();
  128 |   await viewer(page)
  129 |     .getByRole("button", { name: "Save image", exact: true })
  130 |     .click();
  131 |   await page
  132 |     .getByRole("dialog", { name: "Save image", exact: true })
  133 |     .getByRole("button", { name: "Close image save" })
  134 |     .click();
  135 |   await expect(viewer(page)).toBeVisible();
  136 |   await viewer(page).getByRole("button", { name: "Image details" }).click();
  137 |   await page
  138 |     .getByRole("dialog", { name: "Image details", exact: true })
  139 |     .getByRole("button", { name: "Close", exact: true })
  140 |     .click();
  141 |   await page.keyboard.press("Escape");
> 142 |   await expect(viewer(page)).not.toBeVisible();
      |                                  ^ Error: expect(locator).not.toBeVisible() failed
  143 |   await expect(opening).toBeFocused();
  144 |   await mkdir(dir, { recursive: true });
  145 |   await page.screenshot({
  146 |     path: `${dir}/conversation-${info.project.name}-fake.png`,
  147 |   });
  148 | });
  149 | test("phone snap dots and viewer pinch, pan, double tap, swipe down", async ({
  150 |   page,
  151 |   request,
  152 | }) => {
  153 |   await page.setViewportSize({ width: 390, height: 844 });
  154 |   await page.emulateMedia({ reducedMotion: "no-preference" });
  155 |   await open(page, request);
  156 |   const stage = viewer(page).locator(".image-viewer-stage");
  157 |   const box = await stage.boundingBox();
  158 |   const x = box!.x + box!.width / 2,
  159 |     y = box!.y + box!.height / 2;
  160 |   for (const [id, px] of [
  161 |     [51, x - 40],
  162 |     [52, x + 40],
  163 |   ])
  164 |     await stage.dispatchEvent("pointerdown", {
  165 |       pointerId: id,
  166 |       pointerType: "touch",
  167 |       clientX: px,
  168 |       clientY: y,
  169 |     });
  170 |   await stage.dispatchEvent("pointermove", {
  171 |     pointerId: 52,
  172 |     pointerType: "touch",
  173 |     clientX: x + 120,
  174 |     clientY: y,
  175 |   });
  176 |   await expect(stage).toHaveAttribute("data-zoom", "2.00");
  177 |   for (const id of [51, 52])
  178 |     await stage.dispatchEvent("pointerup", {
  179 |       pointerId: id,
  180 |       pointerType: "touch",
  181 |       clientX: x,
  182 |       clientY: y,
  183 |     });
  184 |   await viewer(page).getByRole("button", { name: "Fit image" }).click();
  185 |   // A pair of touch taps on the actual image toggles actual size.
  186 |   const output = viewer(page).locator(".image-viewer-output");
  187 |   for (let n = 0; n < 2; n++) {
  188 |     await output.dispatchEvent("pointerdown", {
  189 |       pointerId: 61,
  190 |       pointerType: "touch",
  191 |       clientX: x,
  192 |       clientY: y,
  193 |     });
  194 |     await output.dispatchEvent("pointerup", {
  195 |       pointerId: 61,
  196 |       pointerType: "touch",
  197 |       clientX: x,
  198 |       clientY: y,
  199 |     });
  200 |   }
  201 |   await expect(stage).not.toHaveAttribute("data-zoom", "1.00");
  202 |   await swipe(page, 40, 0);
  203 |   await expect(viewer(page).getByText("1 / 3", { exact: true })).toBeVisible();
  204 |   await viewer(page).getByRole("button", { name: "Fit image" }).click();
  205 |   await swipe(page, 0, 110);
  206 |   await expect(viewer(page)).not.toBeVisible();
  207 |   const row = page.locator(".image-frames");
  208 |   await expect(row).toHaveCSS("scroll-snap-type", "x mandatory");
  209 |   await page.getByRole("button", { name: "Show image 3" }).click();
  210 |   await expect(
  211 |     page.getByRole("button", { name: "Show image 3" }),
  212 |   ).toHaveAttribute("aria-current", "true");
  213 |   await expect(
  214 |     page
  215 |       .locator(".image-frame-actions")
  216 |       .last()
  217 |       .getByRole("button", { name: "Refine image" }),
  218 |   ).toBeVisible();
  219 | });
  220 | test("iteration preserves text draft, source lineage, removable chip and uncertain submission", async ({
  221 |   page,
  222 |   request,
  223 | }) => {
  224 |   const { chat, data } = await open(page, request, 1);
  225 |   await viewer(page).getByRole("button", { name: "Refine image" }).click();
  226 |   await expect(viewer(page)).not.toBeVisible();
  227 |   const field = page.getByRole("textbox", {
  228 |     name: "Image prompt",
  229 |     exact: true,
  230 |   });
  231 |   await expect(field).toHaveValue("Synthetic cobalt mountains");
  232 |   await expect(field).toBeFocused();
  233 |   expect(
  234 |     await field.evaluate((el: HTMLTextAreaElement) => el.selectionStart),
  235 |   ).toBe("Synthetic cobalt mountains".length);
  236 |   await expect(page.locator('[data-slot="image-refinement"]')).toContainText(
  237 |     "seed 101",
  238 |   );
  239 |   await page.getByRole("button", { name: "Leave image mode" }).click();
  240 |   const text = page.locator(".composer textarea");
  241 |   await text.fill("Synthetic saved text draft");
  242 |   await page.getByRole("button", { name: "Create image", exact: true }).click();
```