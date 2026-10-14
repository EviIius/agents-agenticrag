import {
  test,
  expect,
  type Page,
  type APIRequestContext,
} from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { mkdir, writeFile } from "node:fs/promises";
import { settle } from "./helpers";
const dir = "../artifacts/chat-images/ci-c/browser";
test.use({ video: { mode: "on" } });
test.beforeEach(async ({ request }) => {
  await request.patch("/api/settings", {
    data: {
      "appearance.theme": "system",
      "appearance.reduce_motion": "system",
    },
  });
});
test.afterEach(async ({ request }) => {
  await request.patch("/api/settings", {
    data: {
      "appearance.theme": "system",
      "appearance.reduce_motion": "system",
    },
  });
});
const viewer = (page: Page) =>
  page.getByRole("dialog", { name: "Image viewer", exact: true });
const frames = (page: Page) =>
  page.locator('[data-slot="image-turn"] .image-frame');
async function seed(request: APIRequestContext, count = 3) {
  const chat = await request
    .post("/api/chats", { data: {} })
    .then((r) => r.json());
  const data = await request
    .post(`/api/chats/${chat.id}/images`, {
      data: {
        request_key: crypto.randomUUID(),
        prompt: "Synthetic cobalt mountains",
        count,
        seeds: [101, 102, 103].slice(0, count),
      },
    })
    .then((r) => r.json());
  return { chat, data };
}
async function open(page: Page, request: APIRequestContext, count = 3) {
  const seeded = await seed(request, count);
  await page.goto(`/c/${seeded.chat.id}`);
  await expect(frames(page)).toHaveCount(count);
  await expect(
    page.locator('[data-slot="image-turn"] .image-output').last(),
  ).toHaveClass(/is-loaded/);
  await frames(page).first().scrollIntoViewIfNeeded();
  await frames(page).first().click();
  await expect(viewer(page)).toBeVisible();
  await settle(page);
  return seeded;
}
async function swipe(page: Page, x: number, y: number) {
  const stage = viewer(page).locator(".image-viewer-stage"),
    box = await stage.boundingBox();
  const cx = box!.x + box!.width / 2,
    cy = box!.y + box!.height / 2;
  await stage.dispatchEvent("pointerdown", {
    pointerId: 31,
    pointerType: "touch",
    clientX: cx,
    clientY: cy,
    bubbles: true,
  });
  await stage.dispatchEvent("pointermove", {
    pointerId: 31,
    pointerType: "touch",
    clientX: cx + x,
    clientY: cy + y,
    bubbles: true,
  });
  console.log(
    "Gesture CSS",
    await stage.locator(".image-viewer-pan").evaluate((el) => ({
      style: el.getAttribute("style"),
      zoom: el.closest(".image-viewer-stage")?.getAttribute("data-zoom"),
      transform: getComputedStyle(el).transform,
      vars: getComputedStyle(el).getPropertyValue("--viewer-zoom"),
    })),
  );
  await expect(stage.locator(".image-viewer-pan")).not.toHaveCSS(
    "transform",
    "none",
  );
  await stage.dispatchEvent("pointerup", {
    pointerId: 31,
    pointerType: "touch",
    clientX: cx + x,
    clientY: cy + y,
    bubbles: true,
  });
}
test("viewer traverses the conversation, zooms from/to the frame and restores focus", async ({
  page,
  request,
}, info) => {
  await page.emulateMedia({ reducedMotion: "no-preference" });
  const { chat } = await seed(request, 2);
  await request.post(`/api/chats/${chat.id}/images`, {
    data: {
      request_key: crypto.randomUUID(),
      prompt: "Synthetic warm shapes",
      count: 1,
      seeds: [201],
    },
  });
  await page.goto(`/c/${chat.id}`);
  await expect(frames(page)).toHaveCount(3);
  const opening = frames(page).first();
  await opening.scrollIntoViewIfNeeded();
  await opening.focus();
  await page.keyboard.press("Enter");
  await expect(viewer(page)).toBeVisible();
  await expect(viewer(page).getByText("1 / 3", { exact: true })).toBeVisible();
  expect(
    await viewer(page)
      .locator(".image-viewer-fit")
      .evaluate((el) => getComputedStyle(el).transitionDuration),
  ).toBe("0.32s");
  await settle(page);
  await page.keyboard.press("ArrowRight");
  await expect(viewer(page).getByText("2 / 3", { exact: true })).toBeVisible();
  await page.keyboard.press("ArrowRight");
  await expect(viewer(page).getByText("3 / 3", { exact: true })).toBeVisible();
  await page.keyboard.press("ArrowRight");
  await expect(viewer(page).getByText("1 / 3", { exact: true })).toBeVisible();
  await swipe(page, -100, 0);
  await expect(viewer(page).getByText("2 / 3", { exact: true })).toBeVisible();
  await viewer(page)
    .getByRole("button", { name: "Save image", exact: true })
    .click();
  await page
    .getByRole("dialog", { name: "Save image", exact: true })
    .getByRole("button", { name: "Close image save" })
    .click();
  await expect(viewer(page)).toBeVisible();
  await viewer(page).getByRole("button", { name: "Image details" }).click();
  await page
    .getByRole("dialog", { name: "Image details", exact: true })
    .getByRole("button", { name: "Close", exact: true })
    .click();
  await expect(
    page.getByRole("dialog", { name: "Image details", exact: true }),
  ).not.toBeVisible();
  await settle(page);
  await page.keyboard.press("Escape");
  await expect(viewer(page)).not.toBeVisible();
  await expect(opening).toBeFocused();
  await mkdir(dir, { recursive: true });
  await page.screenshot({
    path: `${dir}/conversation-${info.project.name}-fake.png`,
  });
});
test("phone snap dots and viewer pinch, pan, double tap, swipe down", async ({
  page,
  request,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.emulateMedia({ reducedMotion: "no-preference" });
  await open(page, request);
  const stage = viewer(page).locator(".image-viewer-stage");
  const box = await stage.boundingBox();
  const x = box!.x + box!.width / 2,
    y = box!.y + box!.height / 2;
  for (const [id, px] of [
    [51, x - 40],
    [52, x + 40],
  ])
    await stage.dispatchEvent("pointerdown", {
      pointerId: id,
      pointerType: "touch",
      clientX: px,
      clientY: y,
    });
  await stage.dispatchEvent("pointermove", {
    pointerId: 52,
    pointerType: "touch",
    clientX: x + 120,
    clientY: y,
  });
  await expect(stage).toHaveAttribute("data-zoom", "2.00");
  for (const id of [51, 52])
    await stage.dispatchEvent("pointerup", {
      pointerId: id,
      pointerType: "touch",
      clientX: x,
      clientY: y,
    });
  await viewer(page).getByRole("button", { name: "Fit image" }).click();
  // A pair of touch taps on the actual image toggles actual size.
  const output = viewer(page).locator(".image-viewer-output");
  for (let n = 0; n < 2; n++) {
    await output.dispatchEvent("pointerdown", {
      pointerId: 61,
      pointerType: "touch",
      clientX: x,
      clientY: y,
    });
    await output.dispatchEvent("pointerup", {
      pointerId: 61,
      pointerType: "touch",
      clientX: x,
      clientY: y,
    });
  }
  await expect(stage).not.toHaveAttribute("data-zoom", "1.00");
  await swipe(page, 40, 0);
  await expect(viewer(page).getByText("1 / 3", { exact: true })).toBeVisible();
  await viewer(page).getByRole("button", { name: "Fit image" }).click();
  await swipe(page, 0, 110);
  await expect(viewer(page)).not.toBeVisible();
  const row = page.locator(".image-frames");
  await expect(row).toHaveCSS("scroll-snap-type", "x mandatory");
  await page.getByRole("button", { name: "Show image 3" }).click();
  await expect(
    page.getByRole("button", { name: "Show image 3" }),
  ).toHaveAttribute("aria-current", "true");
  await expect(
    page
      .locator(".image-frame-actions")
      .last()
      .getByRole("button", { name: "Refine image" }),
  ).toBeVisible();
});
test("iteration preserves text draft, source lineage, removable chip and uncertain submission", async ({
  page,
  request,
}) => {
  const { chat, data } = await open(page, request, 1);
  await viewer(page).getByRole("button", { name: "Refine image" }).click();
  await expect(viewer(page)).not.toBeVisible();
  const field = page.getByRole("textbox", {
    name: "Image prompt",
    exact: true,
  });
  await expect(field).toHaveValue("Synthetic cobalt mountains");
  await expect(field).toBeFocused();
  expect(
    await field.evaluate((el: HTMLTextAreaElement) => el.selectionStart),
  ).toBe("Synthetic cobalt mountains".length);
  await expect(page.locator('[data-slot="image-refinement"]')).toContainText(
    "seed 101",
  );
  await page.getByRole("button", { name: "Leave image mode" }).click();
  const text = page.locator(".composer textarea");
  await text.fill("Synthetic saved text draft");
  await page.getByRole("button", { name: "Create image", exact: true }).click();
  await field.fill("Synthetic refined cobalt shapes");
  const bodies: unknown[] = [];
  await page.route("**/api/chats/*/images", async (route) => {
    bodies.push(route.request().postDataJSON());
    if (bodies.length === 1) {
      await route.fetch();
      await route.abort("failed");
    } else await route.continue();
  });
  await page.getByRole("button", { name: "Create image", exact: true }).click();
  await expect(page.getByRole("alert")).toBeVisible();
  await expect(page.locator('[data-slot="image-refinement"]')).toBeVisible();
  await page.getByRole("button", { name: "Create image", exact: true }).click();
  await expect(field).toHaveValue("");
  expect(bodies[1]).toEqual(bodies[0]);
  expect(bodies[0]).toMatchObject({
    source_job_id: data.assistant.images[0].id,
    count: 1,
  });
  await page.unroute("**/api/chats/*/images");
  await expect(page.locator('[data-slot="image-turn"]')).toHaveCount(2);
  await page.getByRole("button", { name: "Leave image mode" }).click();
  await expect(text).toHaveValue("Synthetic saved text draft");
  const newest = page.locator('[data-slot="image-turn"]').last();
  await expect(newest.locator("img")).toBeVisible();
  const source = await newest
    .locator("[data-job-id]")
    .getAttribute("data-job-id");
  await newest
    .getByRole("button", { name: "More like this", exact: true })
    .click();
  await expect(page.locator('[data-slot="image-turn"]')).toHaveCount(3);
  const detail = await request
    .get(`/api/chats/${chat.id}`)
    .then((r) => r.json());
  expect(detail.messages.at(-1).images[0]).toMatchObject({
    parent_id: source,
    prompt: "Synthetic refined cobalt shapes",
  });
  const last = page.locator('[data-slot="image-turn"]').last();
  await expect(last.locator("img")).toBeVisible();
  await last.getByRole("button", { name: "Refine image" }).click();
  await page.getByRole("button", { name: "Remove refinement source" }).click();
  await expect(page.locator('[data-slot="image-refinement"]')).toHaveCount(0);
  await expect(field).toHaveValue("Synthetic refined cobalt shapes");
});
test("Ask about it is metadata gated and uses the existing image upload without sending", async ({
  page,
  request,
}) => {
  const { chat } = await seed(request, 1);
  await page.goto(`/c/${chat.id}`);
  const turn = page.locator('[data-slot="image-turn"]');
  await expect(turn.locator("img")).toBeVisible();
  await turn.getByRole("button", { name: "More image actions" }).click();
  await expect(
    page.getByRole("menuitem", { name: "Ask about it" }),
  ).toHaveCount(0);
  await page.keyboard.press("Escape");
  const detail = await request
    .get(`/api/chats/${chat.id}`)
    .then((r) => r.json());
  await request.patch(`/api/chats/${chat.id}`, {
    data: { connection_id: detail.chat.connection_id, model_id: "fake-vision" },
  });
  await page.reload();
  await turn.getByRole("button", { name: "More image actions" }).click();
  await expect(
    page.getByRole("menuitem", { name: "Ask about it" }),
  ).toBeVisible();
  let sends = 0;
  page.on("request", (r) => {
    if (r.method() === "POST" && r.url().endsWith("/messages")) sends++;
  });
  await page.getByRole("menuitem", { name: "Ask about it" }).click();
  await expect(
    page.locator('.composer [data-slot="attachment-chip"]'),
  ).toBeVisible();
  await expect(page.locator(".composer textarea")).toHaveAttribute(
    "aria-label",
    /^Message /,
  );
  expect(sends).toBe(0);
});
for (const mode of ["system", "always"])
  test(`viewer respects ${mode} reduced motion`, async ({ page, request }) => {
    if (mode === "system") await page.emulateMedia({ reducedMotion: "reduce" });
    else
      await request.patch("/api/settings", {
        data: { "appearance.reduce_motion": "always" },
      });
    await open(page, request, 1);
    await expect(viewer(page).locator(".image-viewer-fit")).toHaveCSS(
      "transition-duration",
      "0s",
    );
    await viewer(page)
      .getByRole("button", { name: "Close image viewer" })
      .click();
    await expect(viewer(page)).not.toBeVisible();
  });
for (const width of [390, 1440])
  for (const theme of ["dark", "light"])
    test(`CI-C axe ${theme} ${width}`, async ({ page, request }, info) => {
      await page.setViewportSize({ width, height: 900 });
      await page.emulateMedia({ colorScheme: theme as "dark" | "light" });
      await request.patch("/api/settings", {
        data: { "appearance.theme": theme },
      });
      await open(page, request, 3);
      await settle(page);
      const results = await new AxeBuilder({ page }).analyze();
      expect(
        results.violations.filter((v) =>
          ["serious", "critical"].includes(v.impact ?? ""),
        ),
      ).toEqual([]);
      await mkdir(dir, { recursive: true });
      await writeFile(
        `${dir}/viewer-axe-${theme}-${width}-${info.project.name}-fake.json`,
        JSON.stringify(results, null, 2),
      );
      await page.screenshot({
        path: `${dir}/viewer-${theme}-${width}-${info.project.name}-fake.png`,
      });
      await viewer(page).getByRole("button", { name: "Refine image" }).click();
      await expect(
        page.locator('[data-slot="image-refinement"]'),
      ).toBeVisible();
      await settle(page);
      const refine = await new AxeBuilder({ page }).analyze();
      expect(
        refine.violations.filter((v) =>
          ["serious", "critical"].includes(v.impact ?? ""),
        ),
      ).toEqual([]);
      await writeFile(
        `${dir}/refine-axe-${theme}-${width}-${info.project.name}-fake.json`,
        JSON.stringify(refine, null, 2),
      );
      await page.screenshot({
        path: `${dir}/refine-${theme}-${width}-${info.project.name}-fake.png`,
      });
    });
