import { test, expect, type Page } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { mkdir, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { fakeAppURL } from "../test-runtime";
import { settle } from "./helpers";
import { measureMaterialContrast } from "./material-contrast";

const evidence = resolve("../artifacts/aero-blur-fix/browser");
// A production service worker otherwise owns fetches before Playwright routes.
test.use({ serviceWorkers: "block" });
// A deliberately busy, high-contrast image. No private photograph is loaded.
const picture = `<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024"><defs><pattern id="p" width="100" height="100" patternUnits="userSpaceOnUse"><rect width="100" height="100" fill="white"/><rect width="50" height="50" fill="black"/><rect x="50" y="50" width="50" height="50" fill="black"/><circle cx="50" cy="50" r="30" fill="#ff3b30"/></pattern></defs><rect width="1024" height="1024" fill="url(#p)"/></svg>`;

async function assertGlass(page: Page, selector: string, overlay = false) {
  const panel = page.locator(selector).filter({ visible: true }).first();
  await expect(panel).toBeVisible();
  const result = await panel.evaluate((el) => {
    const style = getComputedStyle(el);
    const canvas = document.createElement("canvas");
    canvas.width = canvas.height = 1;
    const ctx = canvas.getContext("2d")!;
    ctx.fillStyle = style.backgroundColor;
    ctx.fillRect(0, 0, 1, 1);
    return {
      filter: style.backdropFilter,
      background: style.backgroundColor,
      alpha: ctx.getImageData(0, 0, 1, 1).data[3] / 255,
    };
  });
  expect(result.filter).toContain("blur(18px)");
  if (overlay) expect(result.alpha).toBeGreaterThanOrEqual(0.92);
  return result;
}

async function audit(page: Page, name: string) {
  await settle(page);
  const scan = await new AxeBuilder({ page }).analyze();
  expect(
    scan.violations.filter((v) =>
      ["serious", "critical"].includes(v.impact ?? ""),
    ),
  ).toEqual([]);
  const measured = await measureMaterialContrast(page, evidence, name);
  expect(measured.sampled_text_runs).toBeGreaterThanOrEqual(3);
  expect(measured.failures).toEqual([]);
  return {
    sampled_text_runs: measured.sampled_text_runs,
    minimum: Math.min(...measured.runs.map((row) => row.minimum)),
    failures: measured.failures,
  };
}

for (const width of [390, 1440]) {
  for (const theme of ["light", "dark"] as const) {
    test(`Aero production CSS ${theme} ${width}: glass and contrast over an image`, async ({
      page,
      browserName,
    }) => {
      await mkdir(evidence, { recursive: true });
      const saved = await (
        await page.request.get(fakeAppURL + "/api/settings")
      ).json();
      let chatId: string | undefined;
      let syntheticImageResponses = 0;
      const syntheticPrompt = `Synthetic glass background ${browserName} ${theme} ${width}`;
      try {
        await page.clock.install();
        await page.setViewportSize({
          width,
          height: width === 390 ? 844 : 1000,
        });
        await page.emulateMedia({
          colorScheme: theme,
          reducedMotion: "reduce",
        });
        await page.request.patch(fakeAppURL + "/api/settings", {
          data: { "appearance.palette": "aero", "appearance.theme": theme },
        });
        await page.route("**/api/images/jobs/*/output/png", (route) => {
          syntheticImageResponses++;
          return route.fulfill({ contentType: "image/svg+xml", body: picture });
        });
        // Serve the actual minified release, bypassing the Vite development server.
        await page.goto(fakeAppURL + "/?image=1");
        await expect(page.locator("html")).toHaveAttribute(
          "data-palette",
          "aero",
        );
        const styles = await page
          .locator('link[rel="stylesheet"]')
          .evaluateAll((links) =>
            links.map((link) => (link as HTMLLinkElement).href),
          );
        expect(
          styles.some((href) => /\/assets\/index-[^/]+\.css$/.test(href)),
        ).toBe(true);
        expect(styles.every((href) => !href.includes("/src/"))).toBe(true);
        const composer = await assertGlass(page, ".composer");
        const topbar = await assertGlass(page, ".topbar");
        if (width === 1440) await assertGlass(page, ".bg-sidebar-bg");
        await page
          .getByRole("textbox", { name: "Image prompt", exact: true })
          .fill(syntheticPrompt);
        await page
          .getByRole("button", { name: "Create image", exact: true })
          .click();
        await expect(page).toHaveURL(/\/c\//);
        chatId = new URL(page.url()).pathname.split("/").at(-1);
        await expect(
          page.locator('[data-slot="image-turn"] img'),
        ).toBeVisible();
        await expect(
          page.locator('[data-slot="image-turn"] img'),
        ).toHaveJSProperty("naturalWidth", 1024);
        expect(syntheticImageResponses).toBeGreaterThan(0);
        await page.getByRole("button", { name: "Leave image mode" }).click();
        await page.getByRole("button", { name: "Tools", exact: true }).click();
        const tools = await assertGlass(
          page,
          '[data-slot="dropdown-menu-content"]',
          true,
        );
        const prefix = `${browserName}-${theme}-${width}`;
        const toolsContrast = await audit(page, `${prefix}-tools-fake`);
        await page.keyboard.press("Escape");
        await page.goto(fakeAppURL + "/images");
        await expect(
          page
            .getByRole("article")
            .filter({ hasText: syntheticPrompt })
            .locator("img"),
        ).toBeVisible();
        if (width === 390)
          await page
            .getByRole("button", { name: "Open sidebar", exact: true })
            .click();
        await page
          .getByRole("button", { name: "Settings", exact: true })
          .click();
        const dialog = page.getByRole("dialog", {
          name: "Settings",
          exact: true,
        });
        await dialog
          .getByRole("button", { name: "Appearance", exact: true })
          .click();
        const settings = await assertGlass(
          page,
          '[data-slot="dialog-content"]',
          true,
        );
        const settingsContrast = await audit(page, `${prefix}-settings-fake`);
        // Legible backing remains even on browsers/devices without backdrop blur.
        await page.addStyleTag({
          content:
            "* { -webkit-backdrop-filter: none !important; backdrop-filter: none !important; }",
        });
        const fallbackContrast = await audit(page, `${prefix}-fallback-fake`);
        await writeFile(
          resolve(evidence, `${prefix}-result.json`),
          JSON.stringify(
            {
              styles,
              composer,
              topbar,
              tools,
              settings,
              toolsContrast,
              settingsContrast,
              fallbackContrast,
            },
            null,
            2,
          ) + "\n",
        );
      } finally {
        if (!page.isClosed()) await page.goto("about:blank");
        if (chatId)
          await page.request.delete(fakeAppURL + `/api/chats/${chatId}`);
        await page.request.patch(fakeAppURL + "/api/settings", {
          data: {
            "appearance.palette": saved["appearance.palette"] ?? "cobalt",
            "appearance.theme": saved["appearance.theme"] ?? "system",
          },
        });
      }
    });
  }
}
