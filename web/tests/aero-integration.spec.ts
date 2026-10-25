import AxeBuilder from "@axe-core/playwright";
import { test, expect, type Page } from "@playwright/test";
import { mkdir, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { fakeAppURL } from "../test-runtime";
import { settle } from "./helpers";
import { measureMaterialContrast } from "./material-contrast";

const evidence = resolve("../artifacts/themes/aero-integration-20261024");
const measureContrast = (page: Page, name: string) =>
  measureMaterialContrast(page, evidence, name);
async function audit(page: Page, name: string) {
  await settle(page);
  const violations = (await new AxeBuilder({ page }).analyze()).violations;
  expect(
    violations.filter((v) => ["serious", "critical"].includes(v.impact ?? "")),
  ).toEqual([]);
  const result = await measureContrast(page, name);
  expect(result.sampled_text_runs).toBeGreaterThanOrEqual(3);
  expect(result.failures).toEqual([]);
}

for (const width of [390, 1440]) {
  for (const theme of ["light", "dark"] as const) {
    test(`Aero saved app ${theme} ${width}: actual scene, send, overlays and rendered contrast`, async ({
      page,
      browserName,
    }) => {
      await mkdir(evidence, { recursive: true });
      const saved = await (
        await page.request.get(fakeAppURL + "/api/settings")
      ).json();
      let chatId: string | undefined;
      try {
        await page.clock.install();
        await page.setViewportSize({
          width,
          height: width === 390 ? 844 : 1000,
        });
        await page.emulateMedia({
          reducedMotion: "reduce",
          colorScheme: theme,
        });
        await page.goto("/");
        await expect(page.locator(".composer")).toBeVisible();
        await page.evaluate(async (theme) => {
          const path = "/src/stores/ui.ts";
          const { useUI } = await import(path);
          useUI
            .getState()
            .set({ settings: true, settingsPane: "Appearance", theme });
        }, theme);
        const dialog = page.getByRole("dialog", {
          name: "Settings",
          exact: true,
        });
        await dialog.locator('[data-palette-option="aero"]').click();
        await expect
          .poll(
            async () =>
              (
                await (
                  await page.request.get(fakeAppURL + "/api/settings")
                ).json()
              )["appearance.palette"],
          )
          .toBe("aero");
        await audit(page, `${browserName}-${theme}-${width}-settings-fake`);
        await page.keyboard.press("Escape");
        await page.reload();
        await expect(page.locator("html")).toHaveAttribute(
          "data-palette",
          "aero",
        );
        await expect(page.locator("html")).toHaveAttribute("data-theme", theme);
        await expect(page.locator(".empty-chat .aero-scene")).toBeVisible();
        await audit(page, `${browserName}-${theme}-${width}-new-fake`);
        await page.emulateMedia({ reducedMotion: "no-preference" });
        await page.evaluate(() =>
          document
            .querySelector(".aero-scene")!
            .getAnimations({ subtree: true })
            .forEach((a) => {
              a.currentTime = 15000;
              a.pause();
            }),
        );
        await audit(page, `${browserName}-${theme}-${width}-scene-middle-fake`);
        await page.emulateMedia({ reducedMotion: "reduce" });
        await page.getByRole("button", { name: "Tools", exact: true }).click();
        await audit(page, `${browserName}-${theme}-${width}-tools-fake`);
        await page.keyboard.press("Escape");
        await page
          .locator(".composer textarea")
          .fill("Synthetic Aero integration check");
        await page
          .getByRole("button", { name: "Send message", exact: true })
          .click();
        await expect(page.getByRole("article")).toHaveCount(2);
        await expect(
          page.getByText("tokens", { exact: false }).last(),
        ).toBeVisible();
        chatId = new URL(page.url()).pathname.split("/").at(-1);
        await expect(page.locator(".aero-scene")).toHaveCount(0);
        await audit(page, `${browserName}-${theme}-${width}-thread-fake`);
        await page.goto("/workflows");
        await expect(
          page.getByRole("heading", { name: "Workflows", exact: true }),
        ).toBeVisible();
        await audit(page, `${browserName}-${theme}-${width}-workflows-fake`);
        await page.goto("/images");
        await expect(
          page.getByRole("heading", { name: "Images", exact: true }),
        ).toBeVisible();
        await audit(page, `${browserName}-${theme}-${width}-images-fake`);
        await page.goto("/design?themes");
        await expect(page.locator(".theme-lab-window")).toBeVisible();
        await audit(page, `${browserName}-${theme}-${width}-gel-controls-fake`);
      } finally {
        if (!page.isClosed()) await page.goto("about:blank");
        if (chatId) await page.request.delete(`/api/chats/${chatId}`);
        const data = Object.fromEntries(
          ["appearance.palette", "appearance.theme"].map((key) => [
            key,
            saved[key] ?? (key.endsWith("palette") ? "cobalt" : "system"),
          ]),
        );
        expect(
          (
            await page.request.patch(fakeAppURL + "/api/settings", { data })
          ).ok(),
        ).toBe(true);
      }
    });
  }
}

test("Aero animated new-chat frame diagnostic", async ({
  page,
  browserName,
}) => {
  await page.emulateMedia({ reducedMotion: "no-preference" });
  await page.goto("/design?themes");
  await page
    .getByRole("region", { name: "Controls" })
    .getByRole("button", { name: "Aero", exact: true })
    .click();
  await settle(page);
  const result = await page.evaluate(async () => {
    const frames: number[] = [];
    let previous = 0;
    for (let i = 0; i < 180; i++)
      await new Promise<void>((resolve) =>
        requestAnimationFrame((now) => {
          if (previous) frames.push(now - previous);
          previous = now;
          resolve();
        }),
      );
    frames.sort((a, b) => a - b);
    return {
      samples: frames.length,
      median_ms: frames[Math.floor(frames.length * 0.5)],
      p95_ms: frames[Math.floor(frames.length * 0.95)],
      running_animations: document
        .querySelector(".theme-lab-window .aero-scene")!
        .getAnimations({ subtree: true })
        .filter((a) => a.playState === "running").length,
      scope:
        "Desktop browser rAF diagnostic; not physical phone GPU certification",
    };
  });
  await mkdir(evidence, { recursive: true });
  await writeFile(
    resolve(evidence, `scene-frames-${browserName}.json`),
    JSON.stringify(result, null, 2),
  );
  expect(result.samples).toBe(179);
  expect(result.running_animations).toBeGreaterThan(0);
  expect(result.median_ms).toBeLessThan(20);
});

test("Rendered contrast ignores covered glyphs but rejects exposed low-contrast text", async ({
  page,
  browserName,
}) => {
  await mkdir(evidence, { recursive: true });
  await page.clock.install();
  await page.setContent(`<!doctype html><meta name="viewport" content="width=device-width, initial-scale=1"><title>Synthetic contrast control</title>
    <style>body{margin:16px;background:white;color:black;font:18px Arial}
    .covered{position:relative;width:320px;height:44px}button{width:320px;height:44px;background:#0a6fc0;color:white;border:0;font:18px Arial}
    aside{position:absolute;inset:0 0 auto;height:21.25px;background:white;color:black;font:14px Arial}
    .low{color:#eeeeee}</style>
    <h1>Contrast measurement control</h1>
    <div class="covered"><button>Partially covered</button><aside>Overlay</aside></div>
    <p class="low">Exposed low contrast</p><p>Readable control text</p>
    <p id="expiring">Readable expiring notification</p>`);
  await page.evaluate(() => {
    const notification = document.querySelector("#expiring")!;
    const observer = new MutationObserver(() => {
      if (!notification.hasAttribute("data-contrast-id")) return;
      observer.disconnect();
      setTimeout(() => notification.remove(), 10);
    });
    observer.observe(notification, { attributes: true });
  });
  const result = await measureContrast(
    page,
    `${browserName}-contrast-negative-control-fake`,
  );
  expect(result.runs.some((r) => r.text === "Partially covered")).toBe(true);
  expect(result.failures.map((r) => r.text)).toEqual(["Exposed low contrast"]);
  expect(result.failures[0].minimum).toBeLessThan(4.5);
  expect(
    result.runs.some((r) => r.text === "Readable expiring notification"),
  ).toBe(true);
  await expect(page.locator("#expiring")).toHaveCount(0);
});
