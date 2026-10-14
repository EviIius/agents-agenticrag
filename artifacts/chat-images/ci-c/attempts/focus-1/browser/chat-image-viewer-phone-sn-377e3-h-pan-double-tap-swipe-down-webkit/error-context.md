# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: chat-image-viewer.spec.ts >> phone snap dots and viewer pinch, pan, double tap, swipe down
- Location: tests/chat-image-viewer.spec.ts:149:1

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
> 80  |   await expect(stage.locator(".image-viewer-pan")).not.toHaveCSS(
      |                                                        ^ Error: expect(locator).not.toHaveCSS(expected) failed
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
  142 |   await expect(viewer(page)).not.toBeVisible();
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
```