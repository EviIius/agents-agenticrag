import { test, expect } from "@playwright/test";
import { readFile, writeFile } from "node:fs/promises";
const host = "http://127.0.0.1:8787";
test("built PWA installs and never caches APIs", async ({ page, request }) => {
  const manifest = await (
    await request.get(host + "/manifest.webmanifest")
  ).json();
  expect(manifest.display).toBe("standalone");
  expect(manifest.icons.map((i: { sizes: string }) => i.sizes)).toContain(
    "512x512",
  );
  await page.goto(host + "/");
  await page.evaluate(async () => {
    await navigator.serviceWorker.ready;
  });
  await expect
    .poll(() =>
      page.evaluate(() => Boolean(navigator.serviceWorker.controller)),
    )
    .toBe(true);
  await page.reload(); // Exercise a document loaded under the activated worker.
  await page.evaluate(async () => {
    await fetch("/api/bootstrap");
    await fetch("/api/attachments/pending");
  });
  const cached = await page.evaluate(async () => {
    const paths = [];
    for (const name of await caches.keys())
      for (const req of await (await caches.open(name)).keys())
        paths.push(new URL(req.url).pathname);
    return paths;
  });
  expect(cached).toContain("/index.html");
  expect(cached.some((p) => p.startsWith("/api"))).toBe(false);
});
test("a waiting PWA update prompts before reload", async ({ page }) => {
  const path = "../server/app/static/sw.js";
  const original = await readFile(path, "utf8");
  try {
    await page.goto(host + "/");
    await page.evaluate(async () => {
      await navigator.serviceWorker.ready;
    });
    await expect
      .poll(() =>
        page.evaluate(() => Boolean(navigator.serviceWorker.controller)),
      )
      .toBe(true);
    await writeFile(
      path,
      original.replace("workbench-shell-", "workbench-shell-test-update-"),
    );
    await page.evaluate(async () => {
      const registration = await navigator.serviceWorker.getRegistration();
      await registration!.update();
    });
    await expect(
      page.getByText("A new version is available", { exact: true }),
    ).toBeVisible();
    const navigation = page.waitForEvent("load");
    await page.getByRole("button", { name: "Reload", exact: true }).click();
    await navigation;
    expect(
      await page.evaluate(async () =>
        (await caches.keys()).every((key) => key.includes("test-update")),
      ),
    ).toBe(true);
  } finally {
    await writeFile(path, original);
  }
});

test("offline PWA navigation", async ({ page, context, browserName }) => {
  test.skip(
    browserName === "webkit",
    "Playwright WebKit offline reload returns an internal navigation error; physical Safari check is required.",
  );
  await page.goto(host + "/");
  await page.evaluate(() => navigator.serviceWorker.ready);
  await expect
    .poll(() =>
      page.evaluate(() => Boolean(navigator.serviceWorker.controller)),
    )
    .toBe(true);
  await page.reload();
  await context.setOffline(true);
  await page.reload();
  await expect(
    page.getByRole("heading", { name: "Can't reach Atelier" }),
  ).toBeVisible({ timeout: 15000 });
  await context.setOffline(false);
});
