import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { mkdir, writeFile } from "node:fs/promises";
import { settle } from "./helpers";
const states = [
  "PDF",
  "Word",
  "Overflow",
  "Uploading",
  "Extracting",
  "Upload failure",
  "Review text",
  "Review loading",
  "Review error",
  "document_no_text",
  "document_encrypted",
  "document_unreadable",
  "document_too_large",
  "document_timeout",
];
for (const width of [390, 1440])
  for (const theme of ["light", "dark"])
    test(`5B document design states ${width} ${theme}`, async ({
      page,
      browserName,
    }) => {
      await page.setViewportSize({ width, height: 900 });
      await page.goto("/design?documents");
      await page.getByRole("button", { name: theme, exact: true }).click();
      const out = "../artifacts/phase-5/5b";
      await mkdir(out, { recursive: true });
      const results = [];
      for (const state of states) {
        await page.getByRole("button", { name: state, exact: true }).click();
        if (state.startsWith("Review"))
          await expect(
            page.getByRole("dialog", { name: "What the model received" }),
          ).toBeVisible();
        await settle(page);
        const scan = await new AxeBuilder({ page }).analyze();
        const violations = scan.violations.filter((v) =>
          ["serious", "critical"].includes(v.impact!),
        );
        expect(violations, state).toEqual([]);
        await page.screenshot({
          path: `${out}/document-${state.toLowerCase().replaceAll(/[^a-z0-9]+/g, "-")}-${width}-${theme}-${browserName}-fake.png`,
          fullPage: true,
        });
        results.push({ state, seriousCritical: violations.length });
        if (state.startsWith("Review"))
          await page.getByRole("button", { name: "Close document" }).click();
      }
      await page.getByRole("button", { name: "PDF", exact: true }).click();
      await page.getByRole("button", { name: "Add attachment" }).click();
      await settle(page);
      const menuScan = await new AxeBuilder({ page }).analyze();
      expect(
        menuScan.violations.filter((v) =>
          ["serious", "critical"].includes(v.impact!),
        ),
      ).toEqual([]);
      await page.screenshot({
        path: `${out}/document-add-menu-${width}-${theme}-${browserName}-fake.png`,
        fullPage: true,
      });
      results.push({ state: "Add menu", seriousCritical: 0 });
      await page.keyboard.press("Escape");
      await writeFile(
        `${out}/design-axe-${width}-${theme}-${browserName}-fake.json`,
        JSON.stringify(results, null, 2),
      );
    });
