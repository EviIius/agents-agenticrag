import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { mkdir, writeFile } from "node:fs/promises";
import { settle } from "./helpers";
const dir = "../artifacts/attachments/at-a/browser";
for (const width of [390, 1440])
  for (const theme of ["light", "dark"] as const)
    test(`remaining attachment states axe and screenshots ${width} ${theme}`, async ({
      page,
    }, info) => {
      await page.setViewportSize({ width, height: 1000 });
      await page.emulateMedia({ colorScheme: theme });
      await page.goto("/design?attachments");
      const results = [];
      for (const state of [
        "preparing",
        "HEIC",
        "no vision model",
        "too large",
        "unreadable",
        "unavailable",
        "transcribing",
        "cleaning",
        "1 file",
        "4 files",
        "Word",
        "JSON",
        "Markdown",
        "queued",
        "cancelled",
        "failed",
        "cleaned",
      ]) {
        await page
          .getByRole("button", { name: `Preview ${state}`, exact: true })
          .click();
        await page.locator(".composer").scrollIntoViewIfNeeded();
        await settle(page);
        const axe = await new AxeBuilder({ page }).analyze();
        expect(
          axe.violations.filter((v) =>
            ["serious", "critical"].includes(v.impact ?? ""),
          ),
          state,
        ).toEqual([]);
        results.push({ state, violations: axe.violations });
        await mkdir(dir, { recursive: true });
        await page.locator(".composer").screenshot({
          path: `${dir}/${state.replaceAll(" ", "-")}-${width}-${theme}-${info.project.name}-fake.png`,
        });
      }
      await writeFile(
        `${dir}/remaining-states-${width}-${theme}-${info.project.name}-fake.json`,
        JSON.stringify(results, null, 2),
      );
    });
test("preparation really animates and both reduced-motion triggers stop new tray motion", async ({
  page,
}) => {
  await page.emulateMedia({ reducedMotion: "no-preference" });
  await page.goto("/design?attachments&state=preparing");
  const spinner = page.locator(".attachment-preparing");
  await expect(spinner).toBeVisible();
  const samples = await spinner.evaluate(
    (el) =>
      new Promise<string[]>((resolve) => {
        const out: string[] = [],
          start = performance.now();
        function sample() {
          out.push(getComputedStyle(el).transform);
          if (performance.now() - start < 250) requestAnimationFrame(sample);
          else resolve(out);
        }
        sample();
      }),
  );
  expect(new Set(samples).size).toBeGreaterThan(3);
  for (const trigger of ["system", "always"]) {
    if (trigger === "system")
      await page.emulateMedia({ reducedMotion: "reduce" });
    else {
      await page.emulateMedia({ reducedMotion: "no-preference" });
      await page
        .getByRole("button", { name: "Reduce motion", exact: true })
        .click();
    }
    await expect(spinner).toHaveCSS("animation-name", "none");
    await expect(page.locator(".composer-send-ring")).toHaveCSS(
      "animation-name",
      "none",
    );
    await expect(page.locator(".composer")).toHaveCSS(
      "transition-duration",
      "0s",
    );
    expect(
      await page
        .locator(".composer")
        .evaluate(
          (el) =>
            el
              .getAnimations({ subtree: true })
              .filter((a) => a.playState === "running").length,
        ),
    ).toBe(0);
  }
});
test("error dismissal waits while focused and clears after the grace period", async ({
  page,
}) => {
  await page.clock.install();
  await page.goto("/design?attachments&state=network");
  const remove = page.getByRole("button", {
    name: "Remove Picked-photo-fake.png",
    exact: true,
  });
  await remove.focus();
  await page.clock.runFor(9000);
  await expect(remove).toBeVisible();
  await page.locator(".composer textarea").focus();
  await page.clock.runFor(8500);
  await expect(page.locator(".attachment-status")).toHaveCount(0);
});
