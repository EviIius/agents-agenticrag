import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { mkdir, writeFile } from "node:fs/promises";
import { settle } from "./helpers";
import { openSidebar } from "./workspace-helpers";
const dir = "../artifacts/composer-workflows/browser/images";
for (const width of [390, 1440])
  for (const theme of ["light", "dark"]) {
    test(`Images synthetic states ${width} ${theme}`, async ({
      page,
      browserName,
    }) => {
      await page.setViewportSize({ width, height: 900 });
      await page.goto("/design?images");
      await page.getByRole("button", { name: theme, exact: true }).click();
      await mkdir(dir, { recursive: true });
      const results = [];
      for (const state of [
        "empty",
        "unavailable",
        "queued",
        "preparing",
        "running",
        "cancelling",
        "cancelled",
        "complete",
        "failed",
        "interrupted",
        "removed",
      ]) {
        await page.getByRole("button", { name: state, exact: true }).click();
        await settle(page);
        expect(
          await page.evaluate(
            () => document.documentElement.scrollWidth <= innerWidth,
          ),
        ).toBeTruthy();
        const scan = await new AxeBuilder({ page }).analyze();
        const serious = scan.violations.filter((v) =>
          ["serious", "critical"].includes(v.impact ?? ""),
        );
        expect(serious, state).toEqual([]);
        results.push({ state, seriousCritical: serious.length });
        await page.screenshot({
          path: `${dir}/${state}-${width}-${theme}-${browserName}-fake.png`,
          fullPage: true,
        });
      }
      await page.getByRole("button", { name: "complete", exact: true }).click();
      await page.getByRole("button", { name: "Save", exact: true }).click();
      const dialog = page.getByRole("dialog", {
        name: "Save image",
        exact: true,
      });
      await expect(dialog).toBeVisible();
      await dialog
        .getByRole("button", { name: "Details (.json)", exact: true })
        .click();
      await expect(
        dialog.getByRole("button", { name: "Details (.json)", exact: true }),
      ).toHaveAttribute("aria-pressed", "true");
      await settle(page);
      await page.screenshot({
        path: `${dir}/save-json-${width}-${theme}-${browserName}-fake.png`,
        fullPage: true,
      });
      await page.keyboard.press("Escape");
      await page.getByRole("button", { name: "Details", exact: true }).click();
      await settle(page);
      await page.screenshot({
        path: `${dir}/details-${width}-${theme}-${browserName}-fake.png`,
        fullPage: true,
      });
      await page.keyboard.press("Escape");
      await page
        .getByRole("button", {
          name: "Remove all saved image files",
          exact: true,
        })
        .click();
      await settle(page);
      await page.screenshot({
        path: `${dir}/remove-${width}-${theme}-${browserName}-fake.png`,
        fullPage: true,
      });
      await expect(page.getByRole("dialog")).toContainText("Job history");
      const scan = await new AxeBuilder({ page }).analyze();
      expect(
        scan.violations.filter((v) =>
          ["serious", "critical"].includes(v.impact ?? ""),
        ),
      ).toEqual([]);
      await writeFile(
        `${dir}/axe-${width}-${theme}-${browserName}.json`,
        JSON.stringify(results, null, 2),
      );
    });
  }

test("Durable Images: close, reconnect, version, exports and removal", async ({
  page,
  request,
}) => {
  await request.post("/api/images/clear", { data: { confirm: true } });
  await page.goto("/images");
  await expect(
    page.getByRole("button", { name: "Generate one image" }),
  ).toBeDisabled();
  await page
    .getByRole("textbox", { name: "Prompt", exact: true })
    .fill("Synthetic browser image #slow");
  await page.getByRole("button", { name: "Generate one image" }).click();
  await expect(
    page.getByRole("status").filter({ hasText: "Image accepted" }),
  ).toBeVisible();
  await openSidebar(page);
  await page.getByRole("link", { name: "New chat", exact: true }).click();
  await page.goto("/images");
  const job = page
    .getByRole("article")
    .filter({ hasText: "Synthetic browser image #slow" })
    .first();
  await expect(
    job.getByRole("button", { name: "Save", exact: true }),
  ).toBeVisible();
  await job.getByRole("button", { name: "Details", exact: true }).click();
  await page
    .getByRole("button", { name: "Use prompt for new version" })
    .click();
  await page.getByText("Advanced", { exact: true }).click();
  await page.getByRole("textbox", { name: "Seed", exact: true }).fill("1337");
  await page.getByRole("button", { name: "Generate one image" }).click();
  const version = page
    .getByRole("article")
    .filter({ hasText: "Additional version" })
    .first();
  await expect(
    version.getByRole("button", { name: "Save", exact: true }),
  ).toBeVisible();
  await expect(
    page.getByRole("region", { name: "Image storage" }),
  ).toContainText("2 saved images");
  await version.getByRole("button", { name: "Save", exact: true }).click();
  const dialog = page.getByRole("dialog", { name: "Save image", exact: true });
  await expect(
    dialog.getByRole("button", { name: "Image (.png)", exact: true }),
  ).toHaveAttribute("aria-pressed", "true");
  await dialog
    .getByRole("button", { name: "Details (.json)", exact: true })
    .click();
  await expect(
    dialog.getByRole("button", { name: "Details (.json)", exact: true }),
  ).toHaveAttribute("aria-pressed", "true");
  let downloads = 0;
  page.on("download", () => downloads++);
  await page
    .getByRole("button", { name: "Close image save", exact: true })
    .click();
  expect(downloads).toBe(0);
  await version.getByRole("button", { name: "Details", exact: true }).click();
  await page
    .getByRole("button", { name: "Remove image files", exact: true })
    .click();
  await page.getByRole("button", { name: "Remove files", exact: true }).click();
  await expect(
    page.getByRole("region", { name: "Image storage" }),
  ).toContainText("1 saved images");
  await page.reload();
  await expect(
    page.getByRole("region", { name: "Image storage" }),
  ).toContainText("1 saved images");
});
