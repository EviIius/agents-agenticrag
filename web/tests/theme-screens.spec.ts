import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";
import { fakeAppURL } from "../test-runtime";
import { PALETTES } from "../src/lib/palettes";
import { settle } from "./helpers";

for (const width of [390, 1440]) {
  for (const palette of PALETTES) {
    for (const mode of palette.modes) {
      test(`${palette.id} ${mode} at ${width}: layout, contrast and evidence`, async ({
        page,
      }) => {
        await page.setViewportSize({ width, height: 1000 });
        await page.emulateMedia({ reducedMotion: "reduce", colorScheme: mode });
        await page.goto("/design?themes");
        await expect(page.locator(".theme-lab-window")).toBeVisible();
        await page.evaluate(
          async ({ id, mode }) => {
            const path = "/src/stores/ui.ts";
            const { useUI } = await import(path);
            useUI.getState().set({ palette: id, theme: mode });
          },
          { id: palette.id, mode },
        );
        await expect(page.locator("html")).toHaveAttribute(
          "data-palette",
          palette.id,
        );
        await expect(page.locator("html")).toHaveAttribute("data-theme", mode);
        await settle(page);
        expect(
          await page.evaluate(
            () => document.documentElement.scrollWidth > innerWidth,
          ),
        ).toBe(false);
        const findings = (
          await new AxeBuilder({ page }).analyze()
        ).violations.filter((item) =>
          ["serious", "critical"].includes(item.impact ?? ""),
        );
        expect(findings).toEqual([]);
        await page.locator(".theme-lab-window").screenshot({
          path: `../artifacts/themes/review-20261023/screens/${palette.id}-${mode}-${width}-${test.info().project.name}.png`,
        });
      });
    }
  }
}

for (const palette of ["lime", "ember"] as const) {
  test(`${palette}: complete greeting including name and glow fits 4.5 seconds`, async ({
    page,
  }) => {
    await page.emulateMedia({ reducedMotion: "no-preference" });
    await page.goto("/design?themes");
    await expect(page.locator("h1.greeting")).toBeVisible();
    await page.evaluate(async (palette) => {
      const path = "/src/stores/ui.ts";
      const { useUI } = await import(path);
      useUI.getState().set({ palette, name: "Taylor", greeting: "languages" });
    }, palette);
    await expect(page.locator("html")).toHaveAttribute("data-palette", palette);
    await settle(page);
    const elapsed = await page.evaluate(
      () =>
        new Promise<number>((resolve, reject) => {
          const button = [...document.querySelectorAll("button")].find(
            (button) => button.textContent === "Replay greeting",
          )!;
          const began = performance.now();
          let seenStart = false;
          button.click();
          const frame = () => {
            const heading = document.querySelector("h1.greeting")!;
            const lang = heading
              .querySelector(".greet-word")
              ?.getAttribute("lang");
            seenStart ||= lang === "es";
            const active = heading
              .getAnimations({ subtree: true })
              .filter(
                (animation) =>
                  animation.playState === "running" &&
                  Number.isFinite(
                    animation.effect?.getComputedTiming().endTime,
                  ),
              );
            if (
              seenStart &&
              lang === "en" &&
              heading.querySelector(".greeting-name") &&
              !active.length
            )
              resolve(performance.now() - began);
            else if (performance.now() - began > 5000)
              reject(new Error("Greeting did not finish"));
            else requestAnimationFrame(frame);
          };
          requestAnimationFrame(frame);
        }),
    );
    expect(elapsed).toBeLessThanOrEqual(4500);
    await test.info().attach("complete-greeting-duration-ms", {
      body: String(elapsed),
      contentType: "text/plain",
    });
  });
}

for (const [palette, wanted, bg] of [
  ["lime", "light", "rgb(249, 249, 244)"],
  ["midnight", "dark", "rgb(0, 0, 0)"],
]) {
  test(`${palette}: appearance is applied before the React entry executes`, async ({
    page,
  }) => {
    await page.addInitScript((palette) => {
      localStorage.setItem("workbench-palette", palette);
      localStorage.setItem("workbench-theme", "light");
    }, palette);
    await page.route("**/assets/index-*.js", (route) =>
      route.fulfill({
        contentType: "application/javascript",
        body: "window.beforeReact = {palette: document.documentElement.dataset.palette, theme: document.documentElement.dataset.theme};",
      }),
    );
    await page.goto(fakeAppURL);
    expect(
      await page.evaluate(
        () => (window as unknown as { beforeReact: unknown }).beforeReact,
      ),
    ).toEqual({ palette, theme: wanted });
    // CSS can finish loading after the module starts (notably in WebKit).
    // Assert actual resolved color without running React; minifiers may spell
    // a custom-property black as either #000 or #000000.
    await expect(page.locator("body")).toHaveCSS("background-color", bg);
  });
}
