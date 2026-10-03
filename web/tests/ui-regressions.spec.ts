import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { mkdir } from "node:fs/promises";

for (const width of [320, 390, 768, 1440]) {
  for (const theme of ["light", "dark"]) {
    test(`settings, picker focus and context constraints ${width} ${theme}`, async ({
      page,
      request,
    }) => {
      const connection = (
        await (await request.get("/api/connections")).json()
      )[0];
      await request.patch("/api/settings", {
        data: {
          default_connection_id: connection.id,
          default_model_id: "fake-chat",
          "appearance.theme": theme,
        },
      });
      await request.put("/api/models/prefs", {
        data: {
          connection_id: connection.id,
          model_id: "fake-chat",
          context_length: 16384,
        },
      });
      await page.setViewportSize({ width, height: 844 });
      await page.goto("/");
      if (width < 640)
        await page.evaluate(() => {
          document.documentElement.style.setProperty("--safe-area-top", "47px");
          document.documentElement.style.setProperty(
            "--safe-area-bottom",
            "34px",
          );
        });
      await page.getByRole("button", { name: "Choose model" }).click();
      await expect(
        page.getByRole("option", { name: /fake-chat/ }),
      ).toBeVisible();
      await page
        .locator('[data-slot="drawer-content"]')
        .evaluateAll(async (elements) => {
          await Promise.all(
            elements.flatMap((element) =>
              element
                .getAnimations()
                .map((animation) => animation.finished.catch(() => {})),
            ),
          );
        });
      if (width < 640)
        await expect(
          page.getByRole("button", { name: "Close", exact: true }),
        ).toBeInViewport({ ratio: 1 });
      const search = page.getByRole("combobox", { name: "Search models" });
      await search.focus();
      // Compare one layout snapshot; a bottom sheet can move between separate reads.
      const bounds = await search.evaluate((input) => {
        const wrapper = input.closest('[data-slot="command-input-wrapper"]')!;
        const list = wrapper.parentElement!.querySelector(
          '[data-slot="command-list"]',
        )!;
        const a = input.getBoundingClientRect(),
          b = wrapper.getBoundingClientRect(),
          c = list.getBoundingClientRect();
        return {
          inputTop: a.top,
          inputBottom: a.bottom,
          wrapperTop: b.top,
          wrapperBottom: b.bottom,
          listTop: c.top,
        };
      });
      expect(bounds.inputTop).toBeGreaterThanOrEqual(bounds.wrapperTop);
      expect(bounds.inputBottom).toBeLessThanOrEqual(bounds.wrapperBottom);
      expect(bounds.wrapperBottom).toBeLessThanOrEqual(bounds.listTop + 1);
      await mkdir("../artifacts/phase-2", { recursive: true });
      await page.screenshot({
        path: `../artifacts/phase-2/review-picker-${width}-${theme}.png`,
      });
      if (width < 640)
        await page.getByRole("button", { name: "Close", exact: true }).click();
      else await page.keyboard.press("Escape");
      await page
        .getByRole("button", { name: "Chat settings", exact: true })
        .click();
      const controls = page.getByRole("region", {
        name: "Chat settings controls",
      });
      await expect(
        controls.getByRole("button", { name: "64K", exact: true }),
      ).toHaveCount(0);
      await expect(
        controls.getByRole("button", { name: "32K", exact: true }),
      ).toHaveCount(0);
      const context = controls.getByRole("spinbutton", {
        name: "Context length",
      });
      await expect(context).toHaveAttribute("max", "16384");
      await context.fill("65536");
      await expect(
        controls.getByRole("button", { name: "Save settings", exact: true }),
      ).toBeDisabled();
      await expect(context).toHaveAttribute("aria-invalid", "true");
      await context.fill("16384");
      await expect(
        controls.getByRole("button", { name: "Save settings", exact: true }),
      ).toBeEnabled();
      await page.getByRole("button", { name: "Close chat settings" }).click();
      await page.keyboard.press("Control+,");
      const settings = page.getByRole("dialog", {
        name: "Settings",
        exact: true,
      });
      const close = settings.getByRole("button", { name: "Close settings" });
      for (const pane of [
        "Connections",
        "Models",
        "Search",
        "Appearance",
        "Data",
        "Shortcuts",
        "About",
      ]) {
        await settings.getByRole("button", { name: pane, exact: true }).click();
        await expect(
          settings.getByRole("button", { name: pane, exact: true }),
        ).toHaveAttribute("aria-current", "page");
        await settings
          .getByRole("navigation", { name: "Settings sections" })
          .evaluate(async (element) => {
            await Promise.all(
              element
                .getAnimations({ subtree: true })
                .map((animation) => animation.finished.catch(() => {})),
            );
          });
        await expect(close).toBeInViewport({ ratio: 1 });
        const bounds = await close.boundingBox();
        expect(bounds!.y).toBeGreaterThanOrEqual(width < 640 ? 47 : 0);
        expect(bounds!.y + bounds!.height).toBeLessThan(844);
        const section = settings.locator(`section[aria-label="${pane}"]`);
        expect(
          await section.evaluate((el) => el.scrollWidth <= el.clientWidth),
        ).toBeTruthy();
        if ([390, 1440].includes(width))
          await page.screenshot({
            path: `../artifacts/phase-2/review-settings-${pane.toLowerCase()}-${width}-${theme}.png`,
          });
      }
      const audit = await new AxeBuilder({ page }).analyze();
      expect(
        audit.violations.filter((item) =>
          ["serious", "critical"].includes(item.impact ?? ""),
        ),
      ).toEqual([]);
      await close.click();
      await expect(settings).toHaveCount(0);
    });
  }
}

for (const width of [390, 1440]) {
  test(`switching an existing chat loads and reports the selected model ${width}`, async ({
    page,
    request,
  }) => {
    const connection = (
      await (await request.get("/api/connections")).json()
    )[0];
    await request.post("/api/models/unload", {
      data: { connection_id: connection.id, model_id: "fake-reasoning" },
    });
    const chat = await (
      await request.post("/api/chats", {
        data: { connection_id: connection.id, model_id: "fake-chat" },
      })
    ).json();
    await page.setViewportSize({ width, height: 844 });
    await page.route("**/api/models/load", async (route) => {
      const response = await route.fetch();
      // Hold the control response to make the real loading state observable.
      await new Promise((resolve) => setTimeout(resolve, 1000));
      await route.fulfill({ response });
    });
    await page.goto("/c/" + chat.id);
    await page.getByRole("button", { name: "Choose model" }).click();
    await page.getByRole("option", { name: /fake-reasoning/ }).click();
    await expect(
      page.getByRole("button", { name: "Choose model" }),
    ).toContainText("fake-reasoning");
    await expect(
      page.getByRole("status").filter({ hasText: "Loading…" }),
    ).toBeVisible();
    await expect(
      page.getByText("fake-reasoning loaded", { exact: true }),
    ).toBeVisible();
    await page.reload();
    await expect(
      page.getByRole("button", { name: "Choose model" }),
    ).toContainText("fake-reasoning");
    await page.getByRole("button", { name: "Choose model" }).click();
    const selected = page.getByRole("option", { name: /fake-reasoning/ });
    await expect(selected).toContainText("Loaded");
    if (width < 640)
      await page.getByRole("button", { name: "Close", exact: true }).click();
    else await page.keyboard.press("Escape");
    await page.getByRole("button", { name: /Think:/ }).click();
    await expect(
      page.getByRole("menuitem", { name: "On", exact: true }),
    ).toBeVisible();
    await expect(
      page.getByRole("menuitem", { name: "Off", exact: true }),
    ).toBeVisible();
    await page.getByRole("menuitem", { name: "Off", exact: true }).click();
  });
}
