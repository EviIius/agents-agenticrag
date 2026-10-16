import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { mkdir, writeFile } from "node:fs/promises";
import { settle } from "./helpers";
const dir = "../artifacts/attachments/at-b/browser";
for (const width of [390, 1440])
  for (const theme of ["light", "dark"] as const)
    test(`AT-B sent/drop/paste states axe and screenshots ${width} ${theme}`, async ({
      page,
    }, info) => {
      await page.setViewportSize({ width, height: 1100 });
      await page.emulateMedia({ colorScheme: theme });
      const results = [];
      await mkdir(dir, { recursive: true });
      for (const state of [
        "sent-1",
        "sent-2",
        "sent-3",
        "sent-7",
        "mixed",
        "optimistic",
        "history",
        "missing-photo",
        "drop",
        "drop-target",
        "paste",
        "viewer",
        "pdf",
        "text",
        "transcript",
      ]) {
        await page.goto(`/design?attachment-thread&state=${state}`);
        await expect(
          page.locator(".attachment-thread-preview h1"),
        ).toBeAttached();
        if (["viewer", "pdf", "text", "transcript"].includes(state))
          await expect(page.getByRole("dialog")).toBeVisible();
        else
          await page
            .locator(".attachment-thread-surface")
            .scrollIntoViewIfNeeded();
        if (state === "paste")
          await expect(
            page.getByRole("button", { name: "Keep as text", exact: true }),
          ).toBeVisible();
        if (state === "missing-photo")
          await expect(page.locator(".message-photo-error")).toBeVisible();
        await settle(page);
        const axe = await new AxeBuilder({ page }).analyze();
        expect(
          axe.violations.filter((v) =>
            ["serious", "critical"].includes(v.impact ?? ""),
          ),
          state,
        ).toEqual([]);
        expect(
          await page.evaluate(
            () => document.documentElement.scrollWidth <= innerWidth,
          ),
          state,
        ).toBe(true);
        results.push({ state, violations: axe.violations });
        if (["viewer", "pdf", "text", "transcript"].includes(state))
          await page.screenshot({
            path: `${dir}/${state}-${width}-${theme}-${info.project.name}-fake.png`,
          });
        else
          await page.locator(".attachment-thread-surface").screenshot({
            path: `${dir}/${state}-${width}-${theme}-${info.project.name}-fake.png`,
          });
      }
      await writeFile(
        `${dir}/axe-${width}-${theme}-${info.project.name}-fake.json`,
        JSON.stringify(results, null, 2),
      );
    });
