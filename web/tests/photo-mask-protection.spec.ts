import { test, expect, type Page } from "@playwright/test";
import { readFile, mkdir } from "node:fs/promises";
import { openTools } from "./helpers";

const directory =
  process.env.WORKBENCH_PHOTO_ARTIFACT_DIR ??
  "../artifacts/photo-editing/pe4-20261022/browser";
const file = {
  name: "Synthetic-protection.png",
  mimeType: "image/png",
  buffer: await readFile("../server/tests/fixtures/images/fake-synthetic.png"),
};
async function open(page: Page) {
  await page.goto("/");
  await openTools(page);
  const chooser = page.waitForEvent("filechooser");
  await page.getByRole("menuitem", { name: "Edit photo", exact: true }).click();
  await (await chooser).setFiles(file);
  await expect(page.locator('[data-slot="photo-reference"]')).toContainText(
    "Ready",
  );
  await page
    .getByRole("textbox", { name: "Photo edit instruction" })
    .fill("Synthetic protected change");
  await page
    .getByRole("button", { name: "Select edit area", exact: true })
    .click();
  return page.getByRole("dialog", { name: "Select edit area", exact: true });
}

test("protect, undo, redo and clear preserve the exact accepted selection and retry", async ({
  page,
}) => {
  const dialog = await open(page);
  const canvas = dialog.getByRole("img", { name: /^Photo selection canvas/ });
  await canvas.focus();
  await page.keyboard.press("Space");
  await expect(
    dialog.getByRole("button", { name: "Review selection" }),
  ).toBeEnabled();
  await dialog.getByRole("button", { name: "Protect", exact: true }).click();
  await canvas.focus();
  await page.keyboard.press("Space");
  await expect(dialog.getByRole("status")).toContainText("No area selected");
  await expect(
    dialog.getByRole("button", { name: "Review selection" }),
  ).toBeDisabled();
  await dialog.getByRole("button", { name: "Undo", exact: true }).click();
  await expect(
    dialog.getByRole("button", { name: "Review selection" }),
  ).toBeEnabled();
  await dialog.getByRole("button", { name: "Redo", exact: true }).click();
  await expect(
    dialog.getByRole("button", { name: "Review selection" }),
  ).toBeDisabled();
  await dialog.getByRole("button", { name: "Paint", exact: true }).click();
  await canvas.focus();
  await page.keyboard.press("Space");
  await dialog.getByRole("button", { name: "Clear", exact: true }).click();
  await expect(
    dialog.getByRole("button", { name: "Review selection" }),
  ).toBeDisabled();
  await dialog.getByRole("button", { name: "Undo", exact: true }).click();
  await expect(dialog.getByRole("status")).toContainText("3 brush strokes");
  await dialog.getByRole("button", { name: "Review selection" }).click();
  await dialog.getByRole("button", { name: "Use selection" }).click();
  const requests: Record<string, unknown>[] = [];
  await page.route("**/api/chats/*/images", async (route) => {
    requests.push(route.request().postDataJSON());
    if (requests.length === 1)
      await route.fulfill({
        status: 409,
        contentType: "application/json",
        body: JSON.stringify({
          error: {
            code: "image_capacity",
            message: "Synthetic protection rejection",
          },
        }),
      });
    else await route.continue();
  });
  await page.getByRole("button", { name: "Edit photo", exact: true }).click();
  await expect(page.getByRole("alert")).toContainText(
    "Synthetic protection rejection",
  );
  await page
    .getByRole("button", { name: "Change selection", exact: true })
    .click();
  await expect(dialog.getByRole("status")).toContainText("3 brush strokes");
  await dialog.getByRole("button", { name: "Cancel", exact: true }).click();
  await page.getByRole("button", { name: "Edit photo", exact: true }).click();
  await expect(
    page.getByRole("button", { name: "Open image 1", exact: true }),
  ).toBeVisible();
  expect(requests[0]).toEqual(requests[1]);
  const selection = requests[0].selection as {
    strokes: { operation?: string }[];
  };
  expect(selection.strokes.map((s) => s.operation)).toEqual([
    undefined,
    "erase",
    undefined,
  ]);
  const retry = page.waitForResponse((r) => r.url().endsWith("/images/retry"));
  await page.getByRole("button", { name: "Try again", exact: true }).click();
  expect((await (await retry).json()).assistant.images[0].selection).toEqual(
    selection,
  );
});

test("selected and protected views show an erased detail without changing the mask", async ({
  page,
}) => {
  await page.goto("/design?photo-edit&state=selection-protected");
  await page
    .getByRole("button", { name: "Change selection", exact: true })
    .click();
  const dialog = page.getByRole("dialog", {
    name: "Select edit area",
    exact: true,
  });
  const canvas = dialog.getByRole("img", { name: /^Photo selection canvas/ });
  await expect(
    dialog.getByRole("button", { name: "Review selection" }),
  ).toBeEnabled();
  async function pixels() {
    return canvas.evaluate((c: HTMLCanvasElement) => {
      const ctx = c.getContext("2d")!;
      const opacity = (x: number, y: number) =>
        ctx.getImageData(
          Math.round(c.width * x),
          Math.round(c.height * y),
          1,
          1,
        ).data[3];
      return [opacity(0.5, 0.3), opacity(0.61, 0.3)];
    });
  }
  await dialog.getByRole("button", { name: "Selected", exact: true }).click();
  await expect(dialog).toContainText("Bright areas may change");
  await expect.poll(async () => (await pixels())[0]).toBeLessThan(100);
  const selected = await pixels();
  await dialog.getByRole("button", { name: "Protected", exact: true }).click();
  await expect(dialog).toContainText("Bright areas stay protected");
  await expect
    .poll(async () => (await pixels())[0])
    .toBeGreaterThan(selected[0] * 2);
  const protectedView = await pixels();
  expect(selected[1]).toBeGreaterThan(protectedView[1] * 2);
  await dialog.getByRole("button", { name: "Overlay", exact: true }).click();
  await expect(dialog.getByRole("status")).toContainText("2 brush strokes");
});

test("zoom and move retain submitted pointer coordinates", async ({ page }) => {
  const dialog = await open(page);
  const canvas = dialog.getByRole("img", { name: /^Photo selection canvas/ });
  const viewport = dialog.locator('[data-slot="mask-viewport"]');
  for (let i = 0; i < 4; i++)
    await dialog.getByRole("button", { name: "Zoom in", exact: true }).click();
  await dialog.getByRole("button", { name: "Move", exact: true }).click();
  await viewport.scrollIntoViewIfNeeded();
  const frame = (await viewport.boundingBox())!;
  const cx = frame.x + frame.width / 2,
    cy = frame.y + frame.height / 2;
  await page.mouse.move(cx, cy);
  await page.mouse.down();
  await page.mouse.move(cx - 80, cy - 70, { steps: 5 });
  await page.mouse.up();
  expect(await viewport.evaluate((v) => v.scrollTop)).toBeGreaterThan(0);
  await dialog.getByRole("button", { name: "Paint", exact: true }).click();
  await viewport.scrollIntoViewIfNeeded();
  const visible = (await viewport.boundingBox())!;
  const x = visible.x + visible.width / 2,
    y = visible.y + visible.height / 2;
  // WebKit rounds synthetic device coordinates. Measure the actual delivered
  // event independently; retain the same four-decimal payload assertion.
  await canvas.evaluate((c: HTMLCanvasElement) => {
    c.addEventListener(
      "pointerdown",
      (event) => {
        const bounds = c.getBoundingClientRect();
        c.dataset.deliveredPoint = JSON.stringify([
          (event.clientX - bounds.x) / bounds.width,
          (event.clientY - bounds.y) / bounds.height,
        ]);
      },
      { once: true },
    );
  });
  await page.mouse.click(x, y);
  const expected: number[] = await canvas.evaluate((c: HTMLCanvasElement) =>
    JSON.parse(c.dataset.deliveredPoint!),
  );
  await dialog.getByRole("button", { name: "Review selection" }).click();
  await dialog.getByRole("button", { name: "Use selection" }).click();
  let sent: { selection: { strokes: { points: number[][] }[] } } | undefined;
  await page.route("**/api/chats/*/images", async (route) => {
    sent = route.request().postDataJSON();
    await route.continue();
  });
  await page.getByRole("button", { name: "Edit photo", exact: true }).click();
  await expect(
    page.getByRole("button", { name: "Open image 1", exact: true }),
  ).toBeVisible();
  expect(sent!.selection.strokes[0].points[0][0]).toBeCloseTo(expected[0], 4);
  expect(sent!.selection.strokes[0].points[0][1]).toBeCloseTo(expected[1], 4);
});

test("an erased-empty design state cannot be applied", async ({ page }) => {
  await page.goto("/design?photo-edit&state=selection-empty");
  await page
    .getByRole("button", { name: "Change selection", exact: true })
    .click();
  const dialog = page.getByRole("dialog", {
    name: "Select edit area",
    exact: true,
  });
  await expect(dialog.getByRole("status")).toContainText("No area selected");
  await expect(
    dialog.getByRole("button", { name: "Review selection" }),
  ).toBeDisabled();
});

test("overlap review is read-only and Adjust or Cancel keeps the intended mask", async ({
  page,
}) => {
  await page.goto("/design?photo-edit&state=selection-review");
  await page
    .getByRole("button", { name: "Change selection", exact: true })
    .click();
  const dialog = page.getByRole("dialog", {
    name: "Select edit area",
    exact: true,
  });
  await expect(
    dialog.getByRole("button", { name: "Use selection" }),
  ).toHaveCount(0);
  const before = await dialog.getByRole("status").innerText();
  await dialog.getByRole("button", { name: "Review selection" }).click();
  await expect(dialog).toContainText("A brim may cover hair or forehead");
  await expect(
    dialog.getByRole("button", { name: "Paint", exact: true }),
  ).toBeDisabled();
  await expect(
    dialog.getByRole("button", { name: "Protect", exact: true }),
  ).toBeDisabled();
  const canvas = dialog.getByRole("img", { name: /^Photo selection canvas/ });
  await canvas.click();
  await canvas.focus();
  await page.keyboard.press("Space");
  await page.keyboard.press("Control+z");
  await expect(dialog.getByRole("status")).toHaveText(before);
  await dialog.getByRole("button", { name: "Adjust selection" }).click();
  await expect(
    dialog.getByRole("button", { name: "Paint", exact: true }),
  ).toBeEnabled();
  await expect(dialog.getByRole("status")).toHaveText(before);
  await canvas.focus();
  await page.keyboard.press("Space");
  await expect(dialog.getByRole("status")).toContainText("2 brush strokes");
  await dialog.getByRole("button", { name: "Review selection" }).click();
  await dialog.getByRole("button", { name: "Cancel", exact: true }).click();
  await page
    .getByRole("button", { name: "Change selection", exact: true })
    .click();
  await expect(dialog.getByRole("status")).toHaveText(before);
});

test("a refused stroke at the limit cannot extend an earlier brush stroke", async ({
  page,
}) => {
  const dialog = await open(page);
  const canvas = dialog.getByRole("img", { name: /^Photo selection canvas/ });
  await canvas.focus();
  for (let i = 0; i < 32; i++) await page.keyboard.press("Space");
  await expect(dialog.getByRole("status")).toContainText("32 brush strokes");
  await canvas.scrollIntoViewIfNeeded();
  const box = (await canvas.boundingBox())!;
  await page.mouse.move(box.x + box.width * 0.6, box.y + box.height * 0.5);
  await page.mouse.down();
  await page.mouse.move(box.x + box.width * 0.7, box.y + box.height * 0.5);
  await page.mouse.up();
  await expect(dialog.getByRole("alert")).toContainText(
    "Selection limit reached",
  );
  await dialog.getByRole("button", { name: "Review selection" }).click();
  await dialog.getByRole("button", { name: "Use selection" }).click();
  let sent: { selection: { strokes: { points: number[][] }[] } } | undefined;
  await page.route("**/api/chats/*/images", async (route) => {
    sent = route.request().postDataJSON();
    await route.continue();
  });
  await page.getByRole("button", { name: "Edit photo", exact: true }).click();
  await expect(
    page.getByRole("button", { name: "Open image 1", exact: true }),
  ).toBeVisible();
  expect(sent!.selection.strokes).toHaveLength(32);
  expect(
    sent!.selection.strokes.every((stroke) => stroke.points.length === 1),
  ).toBe(true);
});

for (const theme of ["light", "dark"])
  test(`phone precision tools ${theme} are reachable in a short viewport`, async ({
    page,
    browserName,
  }) => {
    await page.setViewportSize({ width: 390, height: 600 });
    await page.goto("/design?photo-edit&state=selection-protected");
    await page.getByRole("button", { name: theme, exact: true }).click();
    await page
      .getByRole("button", { name: "Change selection", exact: true })
      .click();
    const dialog = page.getByRole("dialog", {
      name: "Select edit area",
      exact: true,
    });
    for (const label of [
      "Paint",
      "Protect",
      "Move",
      "Zoom in",
      "Protected",
      "Undo",
      "Redo",
      "Clear",
      "Cancel",
      "Review selection",
    ]) {
      const button = dialog.getByRole("button", { name: label, exact: true });
      await button.scrollIntoViewIfNeeded();
      const box = (await button.boundingBox())!;
      expect(box.x).toBeGreaterThanOrEqual(0);
      expect(box.x + box.width).toBeLessThanOrEqual(390);
      expect(box.y).toBeGreaterThanOrEqual(0);
      expect(box.y + box.height).toBeLessThanOrEqual(600);
    }
    await mkdir(directory, { recursive: true });
    await page.screenshot({
      path: `${directory}/precision-fake-390-${theme}-${browserName}.png`,
    });
    await dialog.getByRole("button", { name: "Review selection" }).click();
    await expect(dialog).toContainText("Only unselected pixels stay unchanged");
    for (const label of ["Adjust selection", "Cancel", "Use selection"]) {
      const button = dialog.getByRole("button", { name: label, exact: true });
      await button.scrollIntoViewIfNeeded();
      const box = (await button.boundingBox())!;
      expect(box.x).toBeGreaterThanOrEqual(0);
      expect(box.x + box.width).toBeLessThanOrEqual(390);
      expect(box.y).toBeGreaterThanOrEqual(0);
      expect(box.y + box.height).toBeLessThanOrEqual(600);
    }
    await page.screenshot({
      path: `${directory}/overlap-review-390-${theme}-${browserName}.png`,
    });
  });
