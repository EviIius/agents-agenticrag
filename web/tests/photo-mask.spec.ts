import { test, expect, type Page } from "@playwright/test";
import { readFile, mkdir } from "node:fs/promises";
import { openTools } from "./helpers";

const directory = "../artifacts/photo-editing/pe2-20261021/browser";
const file = {
  name: "Synthetic-mask-photo.png",
  mimeType: "image/png",
  buffer: await readFile("../server/tests/fixtures/images/fake-synthetic.png"),
};

async function ready(page: Page) {
  await page.goto("/");
  await openTools(page);
  const chooser = page.waitForEvent("filechooser");
  await page.getByRole("menuitem", { name: "Edit photo", exact: true }).click();
  await (await chooser).setFiles(file);
  await expect(page.locator('[data-slot="photo-reference"]')).toContainText(
    "Ready",
  );
}
async function brush(page: Page) {
  const canvas = page.getByRole("img", { name: /^Photo selection canvas/ });
  const bounds = (await canvas.boundingBox())!;
  await page.mouse.move(
    bounds.x + bounds.width * 0.25,
    bounds.y + bounds.height * 0.25,
  );
  await page.mouse.down();
  await page.mouse.move(
    bounds.x + bounds.width * 0.4,
    bounds.y + bounds.height * 0.3,
    { steps: 8 },
  );
  await page.mouse.up();
}

test("brush selection survives a rejected send and binds the accepted edit and retry", async ({
  page,
}) => {
  await ready(page);
  await page
    .getByRole("textbox", { name: "Photo edit instruction" })
    .fill("Synthetic selected change");
  await page
    .getByRole("button", { name: "Select edit area", exact: true })
    .click();
  const dialog = page.getByRole("dialog", {
    name: "Select edit area",
    exact: true,
  });
  await brush(page);
  await expect(dialog).toContainText("1 brush stroke");
  await dialog.getByRole("button", { name: "Use selection" }).click();
  await expect(dialog).toHaveCount(0);
  await expect(page.locator('[data-slot="photo-reference"]')).toContainText(
    "unselected pixels are preserved",
  );
  await page
    .getByRole("textbox", { name: "Photo edit instruction" })
    .fill("Synthetic selected change");
  const bodies: Record<string, unknown>[] = [];
  await page.route("**/api/chats/*/images", async (route) => {
    bodies.push(route.request().postDataJSON());
    if (bodies.length === 1)
      await route.fulfill({
        status: 409,
        contentType: "application/json",
        body: JSON.stringify({
          error: { code: "image_capacity", message: "Synthetic rejection" },
        }),
      });
    else await route.continue();
  });
  await page.getByRole("button", { name: "Edit photo", exact: true }).click();
  await expect(page.getByRole("alert")).toContainText("Synthetic rejection");
  await expect(
    page.getByRole("button", { name: "Change selection", exact: true }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Edit photo", exact: true }).click();
  await expect(
    page.getByRole("button", { name: "Open image 1", exact: true }),
  ).toBeVisible();
  expect(bodies).toHaveLength(2);
  expect(bodies[0]).toEqual(bodies[1]);
  const selection = bodies[0].selection as {
    version: number;
    strokes: { points: number[][] }[];
  };
  expect(selection.version).toBe(1);
  expect(selection.strokes[0].points.length).toBeGreaterThan(1);
  const retry = page.waitForResponse((r) => r.url().endsWith("/images/retry"));
  await page.getByRole("button", { name: "Try again", exact: true }).click();
  expect((await (await retry).json()).assistant.images[0].selection).toEqual(
    selection,
  );
});

test("Undo, Clear, Cancel and keyboard selection keep the intended draft", async ({
  page,
}) => {
  await ready(page);
  await page
    .getByRole("button", { name: "Select edit area", exact: true })
    .click();
  let dialog = page.getByRole("dialog", {
    name: "Select edit area",
    exact: true,
  });
  await expect(
    dialog.getByRole("button", { name: "Use selection" }),
  ).toBeDisabled();
  await brush(page);
  await dialog.getByRole("button", { name: "Undo", exact: true }).click();
  await expect(dialog).toContainText("No area selected");
  const canvas = dialog.getByRole("img", { name: /^Photo selection canvas/ });
  await canvas.focus();
  await page.keyboard.press("ArrowRight");
  await page.keyboard.press("Space");
  await expect(dialog).toContainText("1 brush stroke");
  await dialog.getByRole("button", { name: "Clear", exact: true }).click();
  await expect(
    dialog.getByRole("button", { name: "Use selection" }),
  ).toBeDisabled();
  await brush(page);
  await dialog.getByRole("button", { name: "Cancel", exact: true }).click();
  await expect(
    page.getByRole("button", { name: "Select edit area", exact: true }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Select edit area", exact: true })
    .click();
  dialog = page.getByRole("dialog", { name: "Select edit area", exact: true });
  await expect(dialog).toContainText("No area selected");
  await page.keyboard.press("Escape");
  await expect(dialog).toHaveCount(0);
});

test("an unreadable preview cannot apply a blind selection", async ({
  page,
}) => {
  await page.goto("/design?photo-edit&state=selection-load-error");
  await page
    .getByRole("button", { name: "Select edit area", exact: true })
    .click();
  const dialog = page.getByRole("dialog", {
    name: "Select edit area",
    exact: true,
  });
  await expect(dialog.getByRole("alert")).toContainText(
    "Couldn't load this photo",
  );
  await brush(page);
  await expect(
    dialog.getByRole("button", { name: "Use selection" }),
  ).toBeDisabled();
  await dialog.getByRole("button", { name: "Cancel", exact: true }).click();
  await expect(dialog).toHaveCount(0);
});

for (const theme of ["light", "dark"])
  test(`phone selection layout ${theme} preserves canvas proportions and reachable controls`, async ({
    page,
    browserName,
  }) => {
    await page.setViewportSize({ width: 390, height: 750 });
    await page.goto("/design?photo-edit&state=selection");
    await page.getByRole("button", { name: theme, exact: true }).click();
    await page
      .getByRole("button", { name: "Change selection", exact: true })
      .click();
    const dialog = page.getByRole("dialog", {
      name: "Select edit area",
      exact: true,
    });
    const canvas = dialog.getByRole("img", { name: /^Photo selection canvas/ });
    await expect(
      dialog.getByRole("button", { name: "Use selection" }),
    ).toBeEnabled();
    const bounds = (await canvas.boundingBox())!;
    expect(bounds.width / bounds.height).toBeCloseTo(720 / 900, 2);
    for (const label of ["Undo", "Clear", "Cancel", "Use selection"]) {
      const button = dialog.getByRole("button", { name: label, exact: true });
      await button.scrollIntoViewIfNeeded();
      const box = (await button.boundingBox())!;
      expect(box.x).toBeGreaterThanOrEqual(0);
      expect(box.x + box.width).toBeLessThanOrEqual(390);
      expect(box.y + box.height).toBeLessThanOrEqual(750);
    }
    await mkdir(directory, { recursive: true });
    await page.screenshot({
      path: `${directory}/mask-390-${theme}-${browserName}.png`,
    });
  });
