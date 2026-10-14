# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: chat-image-viewer.spec.ts >> phone snap dots and viewer pinch, pan, double tap, swipe down
- Location: tests/chat-image-viewer.spec.ts:164:1

# Error details

```
Error: expect(locator).not.toHaveCSS(expected) failed

Locator:  getByRole('dialog', { name: 'Image viewer', exact: true }).locator('.image-viewer-stage').locator('.image-viewer-pan')
Expected: not "none"
Received: "none"
Timeout:  5000ms

Call log:
  - Expect "not toHaveCSS" getByRole('dialog', { name: 'Image viewer', exact: true }).locator('.image-viewer-stage').locator('.image-viewer-pan') with timeout 5000ms
  - waiting for getByRole('dialog', { name: 'Image viewer', exact: true }).locator('.image-viewer-stage').locator('.image-viewer-pan')
    14 × locator resolved to <div class="image-viewer-pan">…</div>
       - unexpected value "none"

```

```yaml
- main:
  - log "Conversation":
    - article "user message":
      - heading "You said" [level=2]
      - paragraph: Image · 3 images
      - paragraph: Synthetic cobalt mountains
      - button "Copy message":
        - status
    - article "assistant message":
      - heading "Assistant replied" [level=2]
      - paragraph: FLUX.2 klein 4B
      - group "Images in this turn":
        - button "Open image 1":
          - img "Synthetic cobalt mountains"
        - button "Save image"
        - button "More like this"
        - button "Refine image"
        - button "Copy image prompt":
          - status
        - button "Image details"
        - button "More image actions"
        - button "Open image 2":
          - img "Synthetic cobalt mountains"
        - button "Save image"
        - button "More like this"
        - button "Refine image"
        - button "Copy image prompt":
          - status
        - button "Image details"
        - button "More image actions"
        - button "Open image 3":
          - img "Synthetic cobalt mountains"
        - button "Save image"
        - button "More like this"
        - button "Refine image"
        - button "Copy image prompt":
          - status
        - button "Image details"
        - button "More image actions"
      - button "Show image 1"
      - button "Show image 2"
      - button "Show image 3"
      - status: 3 images · 1 s
      - button "Try again"
      - button "Copy prompt":
        - status
        - text: Copy prompt
- region "Notifications alt+T"
- dialog "Image viewer":
  - heading "Image viewer" [level=2]
  - paragraph: Use arrow keys or swipe to view the images in this conversation. Double tap or use Zoom to see actual size.
  - banner:
    - button "Expand image prompt": Synthetic cobalt mountains
    - text: 1 / 3
    - button "Close image viewer"
  - img "Synthetic cobalt mountains"
  - contentinfo:
    - button "Save image"
    - button "More like this"
    - button "Refine image"
    - button "Copy image prompt"
    - button "Image details"
    - button "Fit image"
```

# Test source

```ts
  1   | import {
  2   |   test,
  3   |   expect,
  4   |   type Page,
  5   |   type APIRequestContext,
  6   | } from "@playwright/test";
  7   | import AxeBuilder from "@axe-core/playwright";
  8   | import { mkdir, writeFile } from "node:fs/promises";
  9   | import { settle } from "./helpers";
  10  | const dir = "../artifacts/chat-images/ci-c/browser";
  11  | test.use({ video: { mode: "on" } });
  12  | test.beforeEach(async ({ request }) => {
  13  |   await request.patch("/api/settings", {
  14  |     data: {
  15  |       "appearance.theme": "system",
  16  |       "appearance.reduce_motion": "system",
  17  |     },
  18  |   });
  19  | });
  20  | test.afterEach(async ({ request }) => {
  21  |   await request.patch("/api/settings", {
  22  |     data: {
  23  |       "appearance.theme": "system",
  24  |       "appearance.reduce_motion": "system",
  25  |     },
  26  |   });
  27  | });
  28  | const viewer = (page: Page) =>
  29  |   page.getByRole("dialog", { name: "Image viewer", exact: true });
  30  | const frames = (page: Page) =>
  31  |   page.locator('[data-slot="image-turn"] .image-frame');
  32  | async function seed(request: APIRequestContext, count = 3) {
  33  |   const chat = await request
  34  |     .post("/api/chats", { data: {} })
  35  |     .then((r) => r.json());
  36  |   const data = await request
  37  |     .post(`/api/chats/${chat.id}/images`, {
  38  |       data: {
  39  |         request_key: crypto.randomUUID(),
  40  |         prompt: "Synthetic cobalt mountains",
  41  |         count,
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
  80  |   console.log(
  81  |     "Gesture CSS",
  82  |     await stage
  83  |       .locator(".image-viewer-pan")
  84  |       .evaluate((el) => ({
  85  |         style: el.getAttribute("style"),
  86  |         zoom: el.closest(".image-viewer-stage")?.getAttribute("data-zoom"),
  87  |         transform: getComputedStyle(el).transform,
  88  |         vars: getComputedStyle(el).getPropertyValue("--viewer-zoom"),
  89  |       })),
  90  |   );
> 91  |   await expect(stage.locator(".image-viewer-pan")).not.toHaveCSS(
      |                                                        ^ Error: expect(locator).not.toHaveCSS(expected) failed
  92  |     "transform",
  93  |     "none",
  94  |   );
  95  |   await stage.dispatchEvent("pointerup", {
  96  |     pointerId: 31,
  97  |     pointerType: "touch",
  98  |     clientX: cx + x,
  99  |     clientY: cy + y,
  100 |     bubbles: true,
  101 |   });
  102 | }
  103 | test("viewer traverses the conversation, zooms from/to the frame and restores focus", async ({
  104 |   page,
  105 |   request,
  106 | }, info) => {
  107 |   await page.emulateMedia({ reducedMotion: "no-preference" });
  108 |   const { chat } = await seed(request, 2);
  109 |   await request.post(`/api/chats/${chat.id}/images`, {
  110 |     data: {
  111 |       request_key: crypto.randomUUID(),
  112 |       prompt: "Synthetic warm shapes",
  113 |       count: 1,
  114 |       seeds: [201],
  115 |     },
  116 |   });
  117 |   await page.goto(`/c/${chat.id}`);
  118 |   await expect(frames(page)).toHaveCount(3);
  119 |   const opening = frames(page).first();
  120 |   await opening.scrollIntoViewIfNeeded();
  121 |   await opening.focus();
  122 |   await page.keyboard.press("Enter");
  123 |   await expect(viewer(page)).toBeVisible();
  124 |   await expect(viewer(page).getByText("1 / 3", { exact: true })).toBeVisible();
  125 |   expect(
  126 |     await viewer(page)
  127 |       .locator(".image-viewer-fit")
  128 |       .evaluate((el) => getComputedStyle(el).transitionDuration),
  129 |   ).toBe("0.32s");
  130 |   await settle(page);
  131 |   await page.keyboard.press("ArrowRight");
  132 |   await expect(viewer(page).getByText("2 / 3", { exact: true })).toBeVisible();
  133 |   await page.keyboard.press("ArrowRight");
  134 |   await expect(viewer(page).getByText("3 / 3", { exact: true })).toBeVisible();
  135 |   await page.keyboard.press("ArrowRight");
  136 |   await expect(viewer(page).getByText("1 / 3", { exact: true })).toBeVisible();
  137 |   await swipe(page, -100, 0);
  138 |   await expect(viewer(page).getByText("2 / 3", { exact: true })).toBeVisible();
  139 |   await viewer(page)
  140 |     .getByRole("button", { name: "Save image", exact: true })
  141 |     .click();
  142 |   await page
  143 |     .getByRole("dialog", { name: "Save image", exact: true })
  144 |     .getByRole("button", { name: "Close image save" })
  145 |     .click();
  146 |   await expect(viewer(page)).toBeVisible();
  147 |   await viewer(page).getByRole("button", { name: "Image details" }).click();
  148 |   await page
  149 |     .getByRole("dialog", { name: "Image details", exact: true })
  150 |     .getByRole("button", { name: "Close", exact: true })
  151 |     .click();
  152 |   await expect(
  153 |     page.getByRole("dialog", { name: "Image details", exact: true }),
  154 |   ).not.toBeVisible();
  155 |   await settle(page);
  156 |   await page.keyboard.press("Escape");
  157 |   await expect(viewer(page)).not.toBeVisible();
  158 |   await expect(opening).toBeFocused();
  159 |   await mkdir(dir, { recursive: true });
  160 |   await page.screenshot({
  161 |     path: `${dir}/conversation-${info.project.name}-fake.png`,
  162 |   });
  163 | });
  164 | test("phone snap dots and viewer pinch, pan, double tap, swipe down", async ({
  165 |   page,
  166 |   request,
  167 | }) => {
  168 |   await page.setViewportSize({ width: 390, height: 844 });
  169 |   await page.emulateMedia({ reducedMotion: "no-preference" });
  170 |   await open(page, request);
  171 |   const stage = viewer(page).locator(".image-viewer-stage");
  172 |   const box = await stage.boundingBox();
  173 |   const x = box!.x + box!.width / 2,
  174 |     y = box!.y + box!.height / 2;
  175 |   for (const [id, px] of [
  176 |     [51, x - 40],
  177 |     [52, x + 40],
  178 |   ])
  179 |     await stage.dispatchEvent("pointerdown", {
  180 |       pointerId: id,
  181 |       pointerType: "touch",
  182 |       clientX: px,
  183 |       clientY: y,
  184 |     });
  185 |   await stage.dispatchEvent("pointermove", {
  186 |     pointerId: 52,
  187 |     pointerType: "touch",
  188 |     clientX: x + 120,
  189 |     clientY: y,
  190 |   });
  191 |   await expect(stage).toHaveAttribute("data-zoom", "2.00");
```