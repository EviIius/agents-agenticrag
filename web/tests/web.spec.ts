import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { mkdir } from "node:fs/promises";
for (const width of [390, 1440])
  for (const theme of ["light", "dark"])
    test(`web citations ${width} ${theme}`, async ({ page, request }) => {
      await request.patch("/api/settings", {
        data: { "appearance.theme": theme },
      });
      await page.setViewportSize({ width, height: width < 640 ? 844 : 900 });
      await page.addInitScript(
        (value) => localStorage.setItem("workbench-theme", value),
        theme,
      );
      await page.goto("/");
      await expect(
        page.getByRole("button", { name: "Search off", exact: true }),
      ).toBeVisible();
      await page
        .getByRole("button", { name: "Search off", exact: true })
        .click();
      await page
        .locator(".composer textarea")
        .fill("Who lost the 2021 NBA Finals? Show a table.");
      await page.getByRole("button", { name: "Send message" }).click();
      await expect(
        page.getByText("Synthetic web answer", { exact: false }),
      ).toBeVisible();
      await mkdir("../artifacts/phase-2", { recursive: true });
      await page.screenshot({
        path: `../artifacts/phase-2/web-chat-${width}-${theme}-fake-web.png`,
      });
      const pill = page
        .getByRole("button", { name: /View source: Synthetic NBA Finals/ })
        .first();
      await expect(pill).toBeVisible();
      await pill.click();
      await expect(
        page.getByText("Open page ↗", { exact: true }).first(),
      ).toBeVisible();
      await page.screenshot({
        path: `../artifacts/phase-2/citation-card-${width}-${theme}-fake-web.png`,
      });
      const cardAudit = await new AxeBuilder({ page }).analyze();
      expect(
        cardAudit.violations.filter((v) =>
          ["critical", "serious"].includes(v.impact ?? ""),
        ),
      ).toEqual([]);
      await page.keyboard.press("Escape");
      await page.getByRole("button", { name: /2 sources/ }).click();
      const dialog = page.getByRole("dialog").last();
      await expect(
        dialog.getByText("via DuckDuckGo", { exact: true }),
      ).toBeVisible();
      await dialog
        .getByText("What the model saw", { exact: true })
        .first()
        .click();
      await expect(
        dialog.getByText(/synthetic fixture says/, { exact: false }).first(),
      ).toBeVisible();
      expect(
        await page.evaluate(
          () => document.documentElement.scrollWidth <= innerWidth,
        ),
      ).toBeTruthy();
      const a11y = await new AxeBuilder({ page }).analyze();
      expect(
        a11y.violations.filter((v) =>
          ["critical", "serious"].includes(v.impact ?? ""),
        ),
      ).toEqual([]);
      await mkdir("../artifacts/phase-2", { recursive: true });
      await page.screenshot({
        path: `../artifacts/phase-2/sources-${width}-${theme}-fake-web.png`,
      });
      await page.keyboard.press("Escape");
      await page.reload();
      await expect(pill).toBeVisible();
      const before = await (
        await page.request.get("http://127.0.0.1:18080/tests/state")
      ).json();
      await page.locator(".composer textarea").fill("thanks!");
      await page.getByRole("button", { name: "Send message" }).click();
      await expect(
        page.getByText("No web search needed", { exact: false }),
      ).toBeVisible();
      const after = await (
        await page.request.get("http://127.0.0.1:18080/tests/state")
      ).json();
      expect(after.captures.length).toBeGreaterThan(before.captures.length);
      await page
        .getByRole("button", { name: "Search anyway", exact: true })
        .click();
      await expect(
        page.getByText("Synthetic web answer", { exact: false }).last(),
      ).toBeVisible();
    });
