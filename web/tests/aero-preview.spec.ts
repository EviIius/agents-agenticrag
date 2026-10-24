import { test, expect, type Page } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { mkdir } from "node:fs/promises";
import { resolve } from "node:path";
import { settle } from "./helpers";

const evidence = resolve("../artifacts/themes/aero-preview-20261024/screens");
const controls = (page: Page) => page.getByRole("region", { name: "Controls" });
async function openAero(page: Page, mode: "Light" | "Dark") {
  await page.goto("/design?themes");
  await page.evaluate(async () => {
    const path = "/src/stores/ui.ts";
    const { useUI } = await import(path);
    useUI.getState().set({ name: "Taylor", greeting: "languages" });
  });
  await controls(page)
    .getByRole("button", { name: "Aero", exact: true })
    .click();
  await controls(page).getByRole("button", { name: mode, exact: true }).click();
  await expect(page.locator("html")).toHaveAttribute("data-palette", "aero");
  await expect(page.locator("html")).toHaveAttribute(
    "data-theme",
    mode.toLowerCase(),
  );
}
async function capture(page: Page, name: string) {
  const frame = page.locator(".theme-lab-window");
  await frame.evaluate((el) => el.scrollIntoView({ block: "end" }));
  await frame.screenshot({ path: resolve(evidence, name) });
}

for (const width of [390, 1440]) {
  for (const mode of ["Light", "Dark"] as const) {
    test(`Aero ${mode} at ${width}: scene, materials, input and conversation`, async ({
      page,
      browserName,
    }) => {
      await mkdir(evidence, { recursive: true });
      await page.setViewportSize({ width, height: width === 390 ? 844 : 900 });
      await page.emulateMedia({ reducedMotion: "reduce" });
      const apiCalls: string[] = [];
      await page.route("**/api/**", (route) => {
        apiCalls.push(route.request().url());
        return route.abort();
      });
      await openAero(page, mode);
      const frame = page.locator(".theme-lab-window");
      await expect(frame.locator(".aero-bubble")).toHaveCount(9);
      await expect(frame.locator(".aero-scene")).toHaveAttribute(
        "aria-hidden",
        "true",
      );
      await expect(frame.locator(".aero-aurora")).toHaveCSS(
        "display",
        mode === "Dark" ? "block" : "none",
      );
      const glass = await frame
        .locator(".composer")
        .evaluate((el) => getComputedStyle(el).backdropFilter);
      expect(glass).not.toBe("none");
      const input = frame.locator("textarea");
      await input.fill("A synthetic Aero preview message");
      await expect(input).toHaveValue("A synthetic Aero preview message");
      await input.fill("");
      await settle(page);
      const axe = await new AxeBuilder({ page }).analyze();
      expect(
        axe.violations.filter((v) =>
          ["serious", "critical"].includes(v.impact ?? ""),
        ),
      ).toEqual([]);
      expect(
        await frame.evaluate((el) => el.scrollWidth <= el.clientWidth),
      ).toBe(true);
      await capture(
        page,
        `aero-${mode.toLowerCase()}-${width}-${browserName}-new-fake.png`,
      );
      await page
        .getByRole("region", { name: "App preview" })
        .getByRole("button", { name: "Send a message", exact: true })
        .click();
      await expect(
        frame.getByText("Lisbon in spring is mild and bright", {
          exact: false,
        }),
      ).toBeVisible();
      await settle(page);
      await capture(
        page,
        `aero-${mode.toLowerCase()}-${width}-${browserName}-thread-fake.png`,
      );
      expect(apiCalls).toEqual([]);
      await controls(page)
        .getByRole("button", { name: "Cobalt", exact: true })
        .click();
      await page
        .getByRole("region", { name: "App preview" })
        .getByRole("button", { name: "New chat", exact: true })
        .click();
      await expect(frame.locator(".aero-scene")).toHaveCount(0);
      await expect(frame.locator(".composer")).toHaveCSS(
        "backdrop-filter",
        "none",
      );
    });
  }
}

test("Aero complete greeting stays within 4.5 seconds including name", async ({
  page,
}) => {
  await page.emulateMedia({ reducedMotion: "no-preference" });
  await openAero(page, "Light");
  const replay = page.getByRole("button", {
    name: "Replay greeting",
    exact: true,
  });
  await replay.scrollIntoViewIfNeeded();
  const elapsed = await replay.evaluate(
    (button) =>
      new Promise<number>((resolve, reject) => {
        const began = performance.now();
        let started = false;
        if (!(button instanceof HTMLButtonElement))
          throw new Error("Expected the greeting replay button");
        button.click();
        const frame = () => {
          const heading = document.querySelector(
            ".theme-lab-window h1.greeting",
          )!;
          const lang = heading
            .querySelector(".greet-word")
            ?.getAttribute("lang");
          started ||= lang === "es";
          const running = heading
            .getAnimations({ subtree: true })
            .some(
              (animation) =>
                animation.playState === "running" &&
                Number.isFinite(animation.effect?.getComputedTiming().endTime),
            );
          if (
            started &&
            lang === "en" &&
            heading.querySelector(".greeting-name") &&
            !running
          )
            resolve(performance.now() - began);
          else if (performance.now() - began > 5000)
            reject(new Error("Aero greeting did not finish"));
          else requestAnimationFrame(frame);
        };
        requestAnimationFrame(frame);
      }),
  );
  expect(elapsed).toBeLessThanOrEqual(4500);
});

test("Aero scene animates normally and both reduced-motion choices stop it", async ({
  page,
}) => {
  await page.emulateMedia({ reducedMotion: "no-preference" });
  await openAero(page, "Light");
  const scene = page.locator(".theme-lab-window .aero-scene");
  await expect
    .poll(() =>
      scene.evaluate(
        (el) =>
          el
            .getAnimations({ subtree: true })
            .filter((a) => a.playState === "running").length,
      ),
    )
    .toBeGreaterThan(0);
  await page.emulateMedia({ reducedMotion: "reduce" });
  await expect
    .poll(() =>
      scene.evaluate(
        (el) =>
          el
            .getAnimations({ subtree: true })
            .filter((a) => a.playState === "running").length,
      ),
    )
    .toBe(0);
  await page.emulateMedia({ reducedMotion: "no-preference" });
  await controls(page).getByRole("switch", { name: "Reduce motion" }).click();
  await expect
    .poll(() =>
      scene.evaluate(
        (el) =>
          el
            .getAnimations({ subtree: true })
            .filter((a) => a.playState === "running").length,
      ),
    )
    .toBe(0);
});
