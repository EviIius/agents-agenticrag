import { test, expect } from "@playwright/test";
import { mkdir } from "node:fs/promises";
import { settle } from "./helpers";

for (const width of [390, 1440])
  for (const theme of ["light", "dark"]) {
    test(`image memory handoff status ${width} ${theme}`, async ({
      page,
      browserName,
    }) => {
      await page.setViewportSize({ width, height: 900 });
      await page.goto("/design?chat-images");
      // The synthetic route uses the actual image turn and status renderer.
      await page.getByRole("button", { name: theme, exact: true }).click();
      await page
        .getByRole("button", { name: "Preview making-room", exact: true })
        .click();
      const status = page.getByRole("status").filter({
        hasText: "Making room for images",
      });
      await expect(status).toBeVisible();
      await expect(
        page.getByRole("button", { name: "Cancel", exact: true }),
      ).toBeEnabled();
      expect(
        await page.evaluate(
          () => document.documentElement.scrollWidth <= innerWidth,
        ),
      ).toBeTruthy();
      await settle(page);
      const dir = "../artifacts/image-memory-recovery/browser";
      await mkdir(dir, { recursive: true });
      await page.screenshot({
        path: `${dir}/chat-making-room-${width}-${theme}-${browserName}-synthetic.png`,
        fullPage: true,
      });
      await page.goto("/design?images");
      await page.getByRole("button", { name: theme, exact: true }).click();
      await page
        .getByRole("button", { name: "making-room", exact: true })
        .click();
      await expect(
        page.getByText("Making room for images", { exact: true }),
      ).toBeVisible();
      await settle(page);
      await page.screenshot({
        path: `${dir}/gallery-making-room-${width}-${theme}-${browserName}-synthetic.png`,
        fullPage: true,
      });
    });
  }
