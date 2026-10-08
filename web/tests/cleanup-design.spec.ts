import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { mkdir, writeFile } from "node:fs/promises";
import { settle } from "./helpers";
const states = [
  "Cleaning chip",
  "Cleaned chip",
  "Ready to clean",
  "Cleaning transcript",
  "Cleaned transcript",
  "Partial clean-up",
  "Clean-up failed",
  "Clean-up cancelled",
  "Glossary ready",
  "Glossary empty",
  "Glossary loading",
  "Glossary failed",
  "Glossary invalid",
  "Glossary saving",
  "Glossary saved",
  "As transcribed",
  "Raw Whisper",
  "Timestamps",
];
for (const width of [390, 1440])
  for (const theme of ["light", "dark"])
    test(`6A design ${width} ${theme}`, async ({ page, browserName }) => {
      await page.setViewportSize({ width, height: 900 });
      const dir = "../artifacts/phase-6/6a";
      await mkdir(dir, { recursive: true });
      const results = [];
      for (const state of states) {
        await page.goto("/design?cleanup");
        await page.getByRole("button", { name: theme, exact: true }).click();
        const version = [
          "As transcribed",
          "Raw Whisper",
          "Timestamps",
        ].includes(state);
        await page
          .getByRole("button", {
            name: version ? "Cleaned transcript" : state,
            exact: true,
          })
          .click();
        if (version)
          await page.getByRole("button", { name: state, exact: true }).click();
        if (state.includes("chip") || state.startsWith("Glossary"))
          await page
            .locator('[data-slot="cleanup-fixture"]')
            .scrollIntoViewIfNeeded();
        await settle(page);
        const scan = await new AxeBuilder({ page }).analyze();
        const bad = scan.violations.filter((v) =>
          ["serious", "critical"].includes(v.impact!),
        );
        expect(bad, state).toEqual([]);
        await page.screenshot({
          path: `${dir}/cleanup-${state.toLowerCase().replaceAll(/[^a-z0-9]+/g, "-")}-${width}-${theme}-${browserName}-fake.png`,
          fullPage: true,
        });
        results.push({ state, seriousCritical: bad.length });
      }
      await writeFile(
        `${dir}/cleanup-axe-${width}-${theme}-${browserName}-fake.json`,
        JSON.stringify(results, null, 2),
      );
    });
