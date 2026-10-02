import { test, expect } from "@playwright/test";
import { mkdir } from "node:fs/promises";

for (const width of [320, 390, 768, 1440]) {
  test(`safe areas and reachable panels ${width}`, async ({
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
      },
    });
    await page.setViewportSize({ width, height: 844 });
    await page.goto("/");
    const phone = width < 640;
    if (phone) {
      // Browser emulation reports zero env() insets. Exercise the actual layout
      // with the status bar and home indicator dimensions from the phone report.
      await page.evaluate(() => {
        document.documentElement.style.setProperty("--safe-area-top", "47px");
        document.documentElement.style.setProperty(
          "--safe-area-bottom",
          "34px",
        );
      });
    }
    await expect(
      page.getByRole("button", { name: "Choose model" }),
    ).toBeVisible();
    if (width < 1024) {
      await page.getByRole("button", { name: "Open sidebar" }).click();
      const history = page.getByRole("dialog", { name: "Chat history" });
      const header = await history.locator("header").boundingBox();
      const footer = await history.locator("footer").boundingBox();
      expect(header!.y).toBeGreaterThanOrEqual(phone ? 47 : 0);
      expect(footer!.y + footer!.height).toBeLessThanOrEqual(phone ? 810 : 844);
      await history.getByRole("button", { name: "Collapse sidebar" }).click();
    }
    await page
      .getByRole("button", { name: "Chat settings", exact: true })
      .click();
    const controls = page.getByRole("region", {
      name: "Chat settings controls",
    });
    await expect(controls).toBeVisible();
    await page
      .locator('[data-slot="drawer-content"]')
      .evaluateAll(async (els) => {
        await Promise.all(
          els.flatMap((el) =>
            el.getAnimations().map((a) => a.finished.catch(() => {})),
          ),
        );
      });
    if (phone) {
      await expect(
        page.getByRole("heading", { name: "Chat settings", exact: true }),
      ).toHaveCount(1);
    }
    const toggle = controls.getByRole("switch").first();
    const target = await toggle.boundingBox();
    const track = await toggle
      .locator('[data-slot="switch-track"]')
      .boundingBox();
    expect(target!.width).toBeGreaterThanOrEqual(44);
    expect(target!.height).toBeGreaterThanOrEqual(44);
    expect(track!.width).toBe(32);
    expect(track!.height).toBeLessThanOrEqual(20);
    await controls
      .getByRole("switch", { name: "Use model default for Temperature" })
      .click();
    const input = controls.getByRole("spinbutton", {
      name: "Temperature",
      exact: true,
    });
    await input.fill("0.55");
    if (phone)
      expect(
        await input.evaluate((el) => parseFloat(getComputedStyle(el).fontSize)),
      ).toBeGreaterThanOrEqual(16);
    const save = controls.getByRole("button", {
      name: "Save settings",
      exact: true,
    });
    await save.scrollIntoViewIfNeeded();
    const bounds = await save.boundingBox();
    expect(bounds!.y + bounds!.height).toBeLessThanOrEqual(phone ? 810 : 844);
    await mkdir("../artifacts/phase-2", { recursive: true });
    await page.screenshot({
      path: `../artifacts/phase-2/panel-safe-${width}-fake-runtime.png`,
    });
    await page.getByRole("button", { name: "Close chat settings" }).click();
    await page.getByRole("button", { name: "Choose model" }).click();
    if (phone) {
      const search = page.getByRole("combobox", { name: "Search models" });
      await expect(search).not.toBeFocused();
      await page.setViewportSize({ width, height: 480 });
      await search.focus();
      const close = page.getByRole("button", { name: "Close", exact: true });
      await expect(close).toBeInViewport({ ratio: 1 });
      await page
        .locator('[data-slot="drawer-content"]')
        .evaluateAll(async (els) => {
          await Promise.all(
            els.flatMap((el) =>
              el.getAnimations().map((a) => a.finished.catch(() => {})),
            ),
          );
        });
      const closeBounds = await close.boundingBox();
      expect(closeBounds!.y + closeBounds!.height).toBeLessThanOrEqual(446);
      await expect(
        page.getByRole("option", { name: /fake-chat/ }),
      ).toBeVisible();
      await page.screenshot({
        path: `../artifacts/phase-2/model-keyboard-${width}-fake-runtime.png`,
      });
      await close.click();
    } else await page.keyboard.press("Escape");
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    ).toBeTruthy();
  });
}

test("drawer follows the panned visual viewport above the keyboard", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  await page.evaluate(() => {
    document.documentElement.style.setProperty("--safe-area-top", "47px");
    document.documentElement.style.setProperty("--safe-area-bottom", "34px");
  });
  await page.getByRole("button", { name: "Choose model" }).click();
  await page.evaluate(() => {
    const viewport = window.visualViewport!;
    // Safari keeps the layout viewport while the keyboard shrinks and pans
    // the visible area. Resizing the browser alone does not exercise this.
    Object.defineProperty(viewport, "height", {
      configurable: true,
      value: 480,
    });
    Object.defineProperty(viewport, "offsetTop", {
      configurable: true,
      value: 96,
    });
    viewport.dispatchEvent(new Event("resize"));
    viewport.dispatchEvent(new Event("scroll"));
  });
  await page
    .locator('[data-slot="drawer-content"]')
    .evaluateAll(async (els) => {
      await Promise.all(
        els.flatMap((el) =>
          el.getAnimations().map((a) => a.finished.catch(() => {})),
        ),
      );
    });
  const drawer = page.locator('[data-slot="drawer-content"]');
  await expect
    .poll(async () => (await drawer.boundingBox())!.y)
    .toBeGreaterThanOrEqual(143);
  const close = page.getByRole("button", { name: "Close", exact: true });
  const bounds = await close.boundingBox();
  expect(bounds!.y + bounds!.height).toBeLessThanOrEqual(542);
  await expect(
    page.getByRole("combobox", { name: "Search models" }),
  ).toBeVisible();
  await close.click();
});

test("tablet model picker keeps its footer above a reduced viewport", async ({
  page,
}) => {
  await page.route("**/api/models*", async (route) => {
    const response = await route.fetch();
    const models = await response.json();
    await route.fulfill({
      response,
      json: Array.from({ length: 30 }, (_, index) => ({
        ...models[0],
        model_id: `test-model-${index}`,
        display_name: `Test model ${index}`,
      })),
    });
  });
  await page.setViewportSize({ width: 768, height: 844 });
  await page.goto("/");
  await page.getByRole("button", { name: "Choose model" }).click();
  await page.setViewportSize({ width: 768, height: 320 });
  const popover = page.locator('[data-slot="popover-content"]');
  await expect(popover).toBeInViewport({ ratio: 1 });
  const footer = popover.getByText(
    "30 models · capabilities reported by Ollama",
  );
  await expect(footer).toBeInViewport({ ratio: 1 });
  const list = popover.locator('[data-slot="command-list"]');
  expect(
    await list.evaluate((el) => el.scrollHeight > el.clientHeight),
  ).toBeTruthy();
  await popover
    .getByRole("combobox", { name: "Search models" })
    .fill("Test model 29");
  await expect(
    popover.getByRole("option", { name: /Test model 29/ }),
  ).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(popover).not.toBeVisible();
});
