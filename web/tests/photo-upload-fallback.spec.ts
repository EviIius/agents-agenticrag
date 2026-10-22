import { test, expect, type Page } from "@playwright/test";
import { readFile } from "node:fs/promises";
import { openTools } from "./helpers";

const original = await readFile(
  "../server/tests/fixtures/images/fake-synthetic.png",
);
const file = {
  name: "Synthetic-camera-photo.png",
  mimeType: "image/png",
  buffer: original,
};
const endpoint = "**/api/chats/*/image-references";
const unreadable = {
  status: 422,
  contentType: "application/json",
  body: JSON.stringify({
    error: { code: "image_unreadable", message: "Synthetic codec failure" },
  }),
};

async function choose(page: Page) {
  await page.goto("/");
  await openTools(page);
  const chooser = page.waitForEvent("filechooser");
  await page.getByRole("menuitem", { name: "Edit photo", exact: true }).click();
  await (await chooser).setFiles(file);
}

test("an unreadable camera upload converts automatically and preserves its original", async ({
  page,
}) => {
  await page.addInitScript(() => {
    const state = window as unknown as {
      photoUploads: {
        original: number[];
        preview?: number[];
        width: number;
        height: number;
      }[];
    };
    state.photoUploads = [];
    const fetch = window.fetch;
    window.fetch = async (...args) => {
      const form = args[1]?.body;
      if (
        String(args[0]).endsWith("/image-references") &&
        form instanceof FormData
      ) {
        const file = form.get("file") as File;
        const preview = form.get("browser_preview") as File | null;
        state.photoUploads.push({
          original: Array.from(new Uint8Array(await file.arrayBuffer())),
          ...(preview
            ? {
                preview: Array.from(
                  new Uint8Array(await preview.arrayBuffer()),
                ),
              }
            : {}),
          width: Number(form.get("original_width")),
          height: Number(form.get("original_height")),
        });
      }
      return fetch(...args);
    };
  });
  let calls = 0;
  await page.route(endpoint, async (route) => {
    calls += 1;
    if (calls === 1) await route.fulfill(unreadable);
    else await route.continue();
  });
  await choose(page);
  await expect(page.locator('[data-slot="photo-reference"]')).toContainText(
    "Ready",
  );
  const uploads = await page.evaluate(
    () =>
      (
        window as unknown as {
          photoUploads: {
            original: number[];
            preview?: number[];
            width: number;
            height: number;
          }[];
        }
      ).photoUploads,
  );
  expect(calls).toBe(2);
  expect(uploads).toHaveLength(2);
  for (const upload of uploads)
    expect(Buffer.from(upload.original)).toEqual(original);
  expect(uploads[0].preview).toBeUndefined();
  const fallback = uploads[1];
  const bytes = Buffer.from(fallback.preview!);
  expect(bytes.subarray(0, 8).toString("hex")).toBe("89504e470d0a1a0a");
  expect(bytes.readUInt32BE(16)).toBeLessThanOrEqual(2048);
  expect(bytes.readUInt32BE(20)).toBeLessThanOrEqual(2048);
  expect(fallback.width).toBeGreaterThan(0);
  expect(fallback.height).toBeGreaterThan(0);
  await page.screenshot({
    path: `../artifacts/heic-preparation-20261021/ready-${test.info().project.name}.png`,
  });
  await page
    .getByRole("textbox", { name: "Photo edit instruction" })
    .fill("Synthetic instruction stays editable");
  await expect(
    page.getByRole("button", { name: "Edit photo", exact: true }),
  ).toBeEnabled();
});

test("a failed conversion is bounded to one retry and keeps the chosen photo", async ({
  page,
}) => {
  let calls = 0;
  await page.route(endpoint, (route) => {
    calls += 1;
    return route.fulfill(unreadable);
  });
  await choose(page);
  await expect(page.locator('[data-slot="photo-reference"]')).toContainText(
    "Synthetic codec failure",
  );
  expect(calls).toBe(2);
  await expect(
    page.getByRole("button", { name: "Retry photo upload" }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Edit photo", exact: true }),
  ).toBeDisabled();
});

test("WebKit decodes a real HEIC for the automatic fallback", async ({
  page,
  browserName,
}) => {
  test.skip(
    browserName !== "webkit",
    "Camera HEIC fallback uses Safari's image decoder",
  );
  let calls = 0;
  await page.route(endpoint, async (route) => {
    calls += 1;
    if (calls === 1) await route.fulfill(unreadable);
    else await route.continue();
  });
  await page.goto("/");
  await openTools(page);
  const chooser = page.waitForEvent("filechooser");
  await page.getByRole("menuitem", { name: "Edit photo", exact: true }).click();
  await (
    await chooser
  ).setFiles({
    name: "Synthetic-camera-photo.heic",
    mimeType: "image/heic",
    buffer: await readFile(
      "../server/tests/fixtures/images/fake-synthetic.heic",
    ),
  });
  await expect(page.locator('[data-slot="photo-reference"]')).toContainText(
    "Ready",
  );
  expect(calls).toBe(2);
});

test("permission errors do not trigger conversion or another upload", async ({
  page,
}) => {
  let calls = 0;
  await page.route(endpoint, (route) => {
    calls += 1;
    return route.fulfill({
      status: 404,
      contentType: "application/json",
      body: JSON.stringify({
        error: { code: "not_found", message: "Synthetic missing chat" },
      }),
    });
  });
  await choose(page);
  await expect(page.locator('[data-slot="photo-reference"]')).toContainText(
    "Synthetic missing chat",
  );
  expect(calls).toBe(1);
});

test("cancelling during browser conversion cannot submit or restore the removed photo", async ({
  page,
}) => {
  await page.addInitScript(() => {
    const decode = HTMLImageElement.prototype.decode;
    const state = window as unknown as {
      photoDecoded: boolean;
      releasePhoto: () => void;
    };
    HTMLImageElement.prototype.decode = async function () {
      await decode.call(this);
      state.photoDecoded = true;
      await new Promise<void>((resolve) => {
        state.releasePhoto = resolve;
      });
    };
  });
  let calls = 0;
  await page.route(endpoint, (route) => {
    calls += 1;
    return route.fulfill(unreadable);
  });
  await choose(page);
  await page.waitForFunction(
    () => (window as unknown as { photoDecoded: boolean }).photoDecoded,
  );
  await page
    .getByRole("button", { name: "Cancel photo upload", exact: true })
    .click();
  await page.evaluate(() =>
    (window as unknown as { releasePhoto: () => void }).releasePhoto(),
  );
  await expect(page.locator('[data-slot="photo-reference"]')).toContainText(
    "Choose one",
  );
  expect(calls).toBe(1);
  await expect(
    page.getByRole("button", { name: "Edit photo", exact: true }),
  ).toBeDisabled();
});
