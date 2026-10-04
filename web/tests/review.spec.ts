import { settle } from "./helpers";
import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { mkdir } from "node:fs/promises";
for (const width of [390, 1440])
  for (const theme of ["light", "dark"]) {
    test(`review screens ${width} ${theme}`, async ({ page, request }) => {
      await page.setViewportSize({ width, height: width < 640 ? 844 : 900 });
      const connection = (
        await (await request.get("/api/connections")).json()
      )[0];
      await request.patch("/api/settings", {
        data: {
          default_connection_id: connection.id,
          default_model_id: "fake-chat",
          new_chat_model: "last_used",
          "appearance.theme": theme,
          "appearance.font": "serif",
          user_name: "",
        },
      });
      await page.goto("/");
      await expect(
        page.getByRole("button", { name: "Choose model" }),
      ).toContainText("fake-chat");
      const dir = "../artifacts/phase-1";
      await mkdir(dir, { recursive: true });
      const shot = async (name: string) => {
        await settle(page);
        return page.screenshot({
          animations: "disabled",
          path: `${dir}/${name}-${width}-${theme}-fake-runtime.png`,
        });
      };
      await shot("new-chat");
      await page.getByRole("button", { name: "Choose model" }).click();
      await expect(
        page.getByRole("option", { name: /fake-reasoning/ }),
      ).toBeVisible();
      await shot("model-picker");
      await page.getByRole("option", { name: /fake-reasoning/ }).click();
      await page
        .locator(".composer textarea")
        .fill("#think Review this interface");
      await page.getByRole("button", { name: "Send message" }).click();
      await expect(
        page.getByText("Fake runtime reply.", { exact: false }),
      ).toBeVisible();
      await expect(
        page.getByRole("button", { name: /Thought for/ }),
      ).toBeVisible();
      await expect(
        page.getByRole("button", { name: "Stop generating" }),
      ).not.toBeVisible();
      await shot("reasoning-chat");
      await page
        .getByRole("button", { name: "Chat settings", exact: true })
        .click();
      await expect(
        page.getByRole("spinbutton", { name: "Context length" }),
      ).toBeVisible();
      await shot("chat-settings");
      await page.getByRole("button", { name: "Close chat settings" }).click();
      await expect(
        page.getByRole("dialog", { name: "Chat settings" }),
      ).not.toBeVisible();
      if (width < 640) {
        await page.getByRole("button", { name: "Open sidebar" }).click();
        await expect(
          page.getByRole("button", { name: "Settings", exact: true }).last(),
        ).toBeVisible();
        await shot("sidebar-drawer");
        await page
          .getByRole("dialog", { name: "Chat history" })
          .getByRole("button", { name: "Collapse sidebar" })
          .click();
        await expect(
          page.getByRole("dialog", { name: "Chat history" }),
        ).not.toBeVisible();
        await page.setViewportSize({ width, height: 480 });
        await page.locator(".composer textarea").focus();
        const bounds = await page.evaluate(() => {
          const thread = document
            .querySelector('[data-testid="thread"]')!
            .getBoundingClientRect();
          const composer = document
            .querySelector('[data-testid="composer-row"]')!
            .getBoundingClientRect();
          return {
            threadBottom: thread.bottom,
            composerTop: composer.top,
            composerBottom: composer.bottom,
            viewportHeight: innerHeight,
          };
        });
        expect(bounds.threadBottom).toBeLessThanOrEqual(bounds.composerTop + 1);
        expect(bounds.composerBottom).toBeLessThanOrEqual(
          bounds.viewportHeight + 1,
        );
        await shot("keyboard-simulated");
        await page.setViewportSize({ width, height: 844 });
      }
      await page.keyboard.press("Control+,");
      const dialog = page.getByRole("dialog", { name: "Settings" });
      await dialog
        .getByRole("button", { name: "Connections", exact: true })
        .click();
      await expect(dialog.getByText(/Connected/)).toBeVisible();
      await shot("settings-connections");
      await dialog.getByRole("button", { name: "Models", exact: true }).click();
      await shot("settings-models");
      expect(
        await dialog
          .locator('section[aria-label="Models"]')
          .evaluate((el) => el.scrollWidth <= el.clientWidth),
      ).toBeTruthy();
      await settle(page);
      const result = await new AxeBuilder({ page }).analyze();
      expect(
        result.violations.filter((item) =>
          ["serious", "critical"].includes(item.impact ?? ""),
        ),
      ).toEqual([]);
      await page.keyboard.press("Escape");
      await expect(dialog).not.toBeVisible();
      await page.locator(".composer textarea").fill("#error:500");
      await page.getByRole("button", { name: "Send message" }).click();
      await expect(page.getByRole("alert")).toContainText("returned an error");
      await shot("provider-error");
      expect(
        await page.evaluate(
          () => document.documentElement.scrollWidth <= innerWidth,
        ),
      ).toBeTruthy();
      await request.patch("/api/settings", {
        data: {
          default_connection_id: connection.id,
          default_model_id: "fake-chat",
        },
      });
    });
  }

for (const width of [390, 1440])
  for (const theme of ["light", "dark"])
    test(`first run screens ${width} ${theme}`, async ({ page, request }) => {
      let added = false;
      let found = false;
      await request.patch("/api/settings", {
        data: { "appearance.theme": theme },
      });
      await page.route("**/api/bootstrap", async (route) => {
        const response = await route.fetch();
        const body = await response.json();
        await route.fulfill({
          json: { ...body, connections: added ? body.connections : [] },
        });
      });
      await page.route("**/api/connections/detect", (route) =>
        route.fulfill({
          json: found
            ? [
                {
                  kind: "ollama",
                  base_url: "http://127.0.0.1:18080",
                  reachable: true,
                  model_count: 3,
                },
              ]
            : [],
        }),
      );
      await page.route("**/api/connections", async (route) => {
        if (route.request().method() !== "POST") return route.continue();
        const response = await route.fetch();
        added = response.ok();
        await route.fulfill({ response });
      });
      await page.setViewportSize({ width, height: width < 640 ? 844 : 900 });
      await page.goto("/");
      await expect(
        page.getByText("ollama serve", { exact: true }),
      ).toBeVisible();
      await settle(page);
      await page.screenshot({
        path: `../artifacts/phase-1/welcome-offline-${width}-${theme}-fake-runtime.png`,
      });
      found = true;
      await page
        .getByRole("button", { name: "Try again", exact: true })
        .click();
      await expect(
        page.getByRole("button", { name: "Add all", exact: true }),
      ).toBeVisible();
      await settle(page);
      await page.screenshot({
        path: `../artifacts/phase-1/welcome-detected-${width}-${theme}-fake-runtime.png`,
      });
      await settle(page);
      const audit = await new AxeBuilder({ page }).analyze();
      expect(
        audit.violations.filter((v) =>
          ["critical", "serious"].includes(v.impact ?? ""),
        ),
      ).toEqual([]);
      await page.getByRole("button", { name: "Add all", exact: true }).click();
      await expect(
        page.getByRole("heading", { name: "Welcome to Workbench" }),
      ).not.toBeVisible();
      await page.getByRole("button", { name: "Explain", exact: true }).click();
      await expect(page.locator(".composer textarea")).toHaveValue("Explain ");
      await expect(page.locator(".composer textarea")).toBeFocused();
      await page
        .getByRole("button", { name: "Search the web", exact: true })
        .click();
      await expect(
        page.getByRole("button", { name: "Search on", exact: true }),
      ).toBeVisible();
      await expect(page.locator(".composer textarea")).toHaveValue(
        "Search the web for ",
      );
    });
