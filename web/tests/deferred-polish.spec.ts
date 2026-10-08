import { test, expect } from "@playwright/test";
import { settle } from "./helpers";

for (const [width, height] of [
  [390, 844],
  [844, 390],
  [390, 360],
]) {
  for (const theme of ["light", "dark"]) {
    test(`long recording menu respects safe edges ${width}x${height} ${theme}`, async ({
      page,
      browserName,
    }) => {
      await page.setViewportSize({ width, height });
      await page.goto("/design?cleanup");
      await page
        .getByRole("button", { name: "Cleaned chip", exact: true })
        .click();
      await page.getByRole("button", { name: theme, exact: true }).click();
      // The small viewport also covers keyboard-sized visible space. Insets are
      // synthetic: Playwright's WebKit emulation does not supply an iPhone notch.
      await page.addStyleTag({
        content: `:root {--safe-area-top:44px;--safe-area-bottom:34px;--safe-area-left:16px;--safe-area-right:16px;} [data-slot="cleanup-fixture"] {position:fixed;bottom:50px;left:16px;right:16px;}`,
      });
      await page
        .getByRole("button", {
          name: "Recording actions for Invented lantern recording.wav",
        })
        .click();
      const menu = page.getByRole("menu");
      await expect(menu).toBeVisible();
      await settle(page);
      const box = (await menu.boundingBox())!;
      expect(box.y).toBeGreaterThanOrEqual(52);
      expect(box.y + box.height).toBeLessThanOrEqual(height - 42);
      expect(box.x).toBeGreaterThanOrEqual(24);
      expect(box.x + box.width).toBeLessThanOrEqual(width - 24);
      const first = menu.getByRole("menuitem", {
        name: "Open transcript",
        exact: true,
      });
      const last = menu.getByRole("menuitem", { name: "Remove", exact: true });
      await last.scrollIntoViewIfNeeded();
      await expect(last).toBeInViewport({ ratio: 0.99 });
      await first.scrollIntoViewIfNeeded();
      await expect(first).toBeInViewport({ ratio: 0.99 });
      await expect(
        menu.getByRole("menuitem", { name: "Transcribe again", exact: true }),
      ).toBeDisabled();
      await expect(
        menu.getByText(
          "Audio removed to save space. Upload it again to transcribe.",
        ),
      ).toBeVisible();
      await page.screenshot({
        path: `../artifacts/deferred-polish/recording-menu-${width}x${height}-${theme}-${browserName}-fake.png`,
      });
      await page.keyboard.press("Escape");
      await expect(menu).toHaveCount(0);
      await expect(
        page.getByRole("button", {
          name: "Recording actions for Invented lantern recording.wav",
        }),
      ).toBeFocused();
    });
  }
}

for (const mode of ["normal", "always", "system"] as const) {
  test(`phone sidebar motion and effective preference ${mode}`, async ({
    page,
    request,
    browserName,
  }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await request.patch("/api/settings", {
      data: {
        "appearance.reduce_motion": mode === "always" ? "always" : "system",
      },
    });
    await page.emulateMedia({
      reducedMotion: mode === "system" ? "reduce" : "no-preference",
    });
    await page.addInitScript(() => {
      Object.defineProperty(window, "sidebarAnimations", { value: [] });
      document.addEventListener("animationstart", (event) => {
        if (
          event.animationName === "sheet-in" ||
          event.animationName === "sheet-out"
        )
          (
            window as unknown as { sidebarAnimations: string[] }
          ).sidebarAnimations.push(event.animationName);
      });
    });
    await page.goto("/");
    await settle(page);
    await page
      .getByRole("button", { name: "Open sidebar", exact: true })
      .click();
    const sheet = page.getByRole("dialog", {
      name: "Chat history",
      exact: true,
    });
    await expect(sheet).toBeVisible();
    await settle(page);
    expect(
      await sheet.evaluate((el) => getComputedStyle(el).animationName),
    ).toBe(mode === "normal" ? "sheet-in" : "none");
    await sheet
      .getByRole("button", { name: "Collapse sidebar", exact: true })
      .click();
    await expect(sheet).toHaveCount(0);
    const animations = await page.evaluate(
      () =>
        (window as unknown as { sidebarAnimations: string[] })
          .sidebarAnimations,
    );
    expect(animations).toEqual(
      mode === "normal" ? ["sheet-in", "sheet-out"] : [],
    );
    await page.keyboard.press("Control+,");
    const settings = page.getByRole("dialog", {
      name: "Settings",
      exact: true,
    });
    await settings
      .getByRole("button", { name: "Appearance", exact: true })
      .click();
    await expect(
      settings.getByText(
        mode === "normal"
          ? "Brief animations are enabled."
          : mode === "always"
            ? "Animations are off. Choose Follow system to use your device’s preference."
            : "Animations are off because Reduce motion is enabled on this device.",
        { exact: true },
      ),
    ).toBeVisible();
    await settle(page);
    await page.screenshot({
      path: `../artifacts/deferred-polish/motion-${mode}-390-${browserName}-fake.png`,
    });
    await request.patch("/api/settings", {
      data: { "appearance.reduce_motion": "system" },
    });
  });
}

for (const width of [390, 1440]) {
  test(`picker filters reported capabilities and separates selection from loading ${width}`, async ({
    page,
    request,
    browserName,
  }) => {
    await page.setViewportSize({ width, height: 844 });
    await request.patch("/api/settings", {
      data: { "appearance.reduce_motion": "system" },
    });
    await page.goto("/design");
    const picker = page
      .locator(".design-card")
      .filter({
        has: page.getByRole("heading", { name: "ready", exact: true }),
      })
      .first();
    await picker
      .getByRole("button", { name: "Choose model", exact: true })
      .click();
    const filters = page.getByRole("group", { name: "Filter models" });
    await expect(
      page.getByRole("option", { name: /^fake-chat/ }),
    ).toContainText("Selected");
    await filters.getByRole("button", { name: "Images", exact: true }).click();
    await expect(page.getByRole("option")).toHaveCount(1);
    await expect(page.getByRole("option")).toContainText("fake-vision");
    await expect(
      filters.getByRole("button", { name: "Images", exact: true }),
    ).toHaveAttribute("aria-pressed", "true");
    await filters
      .getByRole("button", { name: "Reasoning", exact: true })
      .click();
    await expect(page.getByRole("option")).toHaveCount(1);
    await expect(page.getByRole("option")).toContainText("fake-reasoning");
    await filters.getByRole("button", { name: "Tools", exact: true }).click();
    await expect(page.getByRole("option")).toHaveCount(0);
    await expect(
      page.getByText("No matching models.", { exact: true }),
    ).toBeVisible();
    await filters.getByRole("button", { name: "Loaded", exact: true }).click();
    await expect(page.getByRole("option")).toHaveCount(1);
    await expect(page.getByRole("option")).toContainText("fake-chat");
    await filters.getByRole("button", { name: "All", exact: true }).click();
    await expect(page.getByRole("option")).toHaveCount(3);
    await page
      .getByRole("combobox", { name: "Search models", exact: true })
      .fill("fake-vision");
    await expect(page.getByRole("option")).toHaveCount(1);
    await page
      .getByRole("combobox", { name: "Search models", exact: true })
      .fill("");
    await settle(page);
    await page.screenshot({
      path: `../artifacts/deferred-polish/picker-${width}-${browserName}-fake.png`,
    });
    const { default: AxeBuilder } = await import("@axe-core/playwright");
    const audit = await new AxeBuilder({ page })
      .include('[data-slot="command"]')
      .analyze();
    expect(
      audit.violations.filter((v) =>
        ["serious", "critical"].includes(v.impact ?? ""),
      ),
    ).toEqual([]);
  });
}

for (const width of [320, 390]) {
  test(`picker stays usable with keyboard-sized space ${width}`, async ({
    page,
    browserName,
  }) => {
    await page.setViewportSize({ width, height: 360 });
    await page.goto("/design/chat");
    await page.addStyleTag({
      content: ":root {--safe-area-top:44px;--safe-area-bottom:34px;}",
    });
    await page
      .getByRole("button", { name: "Choose model", exact: true })
      .click();
    const drawer = page.getByRole("dialog", {
      name: "Choose model",
      exact: true,
    });
    await expect(drawer).toBeVisible();
    const search = drawer.getByRole("combobox", {
      name: "Search models",
      exact: true,
    });
    await search.fill("fake-vision");
    const option = drawer.getByRole("option", { name: /^fake-vision/ });
    await option.scrollIntoViewIfNeeded();
    await expect(option).toBeInViewport({ ratio: 0.99 });
    const command = await drawer.locator('[data-slot="command"]').boundingBox();
    const row = await option.boundingBox();
    expect(row!.y).toBeGreaterThanOrEqual(command!.y + 56);
    expect(row!.y + row!.height).toBeLessThanOrEqual(
      command!.y + command!.height + 1,
    );
    await expect(search).toBeInViewport({ ratio: 0.99 });
    const close = drawer.getByRole("button", {
      name: "Close model picker",
      exact: true,
    });
    await expect(close).toBeInViewport({ ratio: 0.99 });
    const { default: AxeBuilder } = await import("@axe-core/playwright");
    const audit = await new AxeBuilder({ page })
      .include('[data-slot="drawer-content"]')
      .analyze();
    expect(
      audit.violations.filter((v) =>
        ["serious", "critical"].includes(v.impact ?? ""),
      ),
    ).toEqual([]);
    await settle(page);
    await page.screenshot({
      path: `../artifacts/deferred-polish/picker-short-${width}x360-${browserName}-fake.png`,
    });
    await close.click();
    await expect(drawer).toHaveCount(0);
  });
}
