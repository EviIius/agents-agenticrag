import { test, expect, type Page } from "@playwright/test";

/** TH1 + TH2 on the theme lab (/design?themes) and Settings › Appearance. */
async function open(page: Page, reducedMotion: "reduce" | "no-preference") {
  await page.emulateMedia({ reducedMotion, colorScheme: "light" });
  await page.goto("/design?themes");
  await expect(page.locator(".theme-lab-window")).toBeVisible();
}
const controls = (page: Page) => page.getByRole("region", { name: "Controls" });
const token = (page: Page, name: string) =>
  page.evaluate(
    (name) =>
      getComputedStyle(document.documentElement)
        .getPropertyValue(`--${name}`)
        .trim(),
    name,
  );

test("a palette changes the tokens, survives a reload and sets its icons", async ({
  page,
}) => {
  await open(page, "reduce");
  await controls(page)
    .getByRole("button", { name: "Light", exact: true })
    .click();
  await controls(page)
    .getByRole("button", { name: "Lime", exact: true })
    .click();
  await expect(page.locator("html")).toHaveAttribute("data-palette", "lime");
  expect(await token(page, "brand-fill")).toBe("#84cc16");
  expect(await token(page, "brand")).toBe("#3d5f10");
  await page.reload();
  // theme-init.js applies the palette before React mounts.
  await expect(page.locator("html")).toHaveAttribute("data-palette", "lime");
  await expect(page.locator('link[rel="apple-touch-icon"]')).toHaveAttribute(
    "href",
    "/icons/lime/apple-touch-icon.png",
  );
  const icon = await page.request.get("/icons/lime/apple-touch-icon.png");
  expect(icon.ok()).toBe(true);
});

test("Midnight is dark only and gives the theme choice back", async ({
  page,
}) => {
  await open(page, "reduce");
  await controls(page)
    .getByRole("button", { name: "Light", exact: true })
    .click();
  await controls(page)
    .getByRole("button", { name: "Midnight", exact: true })
    .click();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
  expect(await token(page, "bg")).toBe("#000000");
  await expect(
    controls(page).getByRole("button", { name: "Light", exact: true }),
  ).toBeDisabled();
  await controls(page)
    .getByRole("button", { name: "Paper", exact: true })
    .click();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "light");
});

test("reduced motion shows the English greeting at once", async ({ page }) => {
  await open(page, "reduce");
  const greeting = page.locator("h1.greeting");
  await expect(greeting).not.toHaveAttribute("data-animate", /.*/);
  await expect(greeting).toHaveAttribute(
    "aria-label",
    /^Good (morning|afternoon|evening)/,
  );
  await expect(greeting.locator(".greet-word")).toHaveText(
    /^Good (morning|afternoon|evening)$/,
  );
});

test("the greeting plays five languages and lands on English inside 4.5 s", async ({
  page,
}) => {
  await open(page, "no-preference");
  await controls(page)
    .getByRole("button", { name: "Cobalt", exact: true })
    .click();
  const greeting = page.locator("h1.greeting");
  await expect(greeting).toHaveAttribute("data-animate", "true");
  const started = Date.now();
  const seen = new Set<string>();
  while (Date.now() - started < 6000) {
    const lang = await greeting
      .locator(".greet-word")
      .getAttribute("lang")
      .catch(() => null);
    if (lang) seen.add(lang);
    if (lang === "en") break;
    await page.waitForTimeout(60);
  }
  expect(Date.now() - started).toBeLessThan(4500);
  expect([...seen]).toEqual(["es", "fr", "ja", "ko", "it", "en"]);
  // Every greeting animation is opacity or transform only.
  const properties = await page.evaluate(() =>
    document
      .getAnimations()
      .flatMap((animation) =>
        (animation.effect as KeyframeEffect)
          .getKeyframes()
          .flatMap((frame) => Object.keys(frame)),
      )
      .filter(
        (key) =>
          !["offset", "computedOffset", "easing", "composite"].includes(key),
      ),
  );
  for (const property of properties)
    expect(["opacity", "transform", "strokeDasharray"]).toContain(property);
});

test("a theme change spreads from the tap point", async ({ page }) => {
  await open(page, "no-preference");
  const supported = await page.evaluate(
    () => "startViewTransition" in document,
  );
  if (!supported) {
    await controls(page)
      .getByRole("button", { name: "Ember", exact: true })
      .click();
    await expect(page.locator("html")).toHaveAttribute("data-palette", "ember");
    await expect(page.locator("html")).not.toHaveAttribute(
      "data-theme-reveal",
      /.*/,
    );
    return;
  }
  await page.evaluate(() => {
    const original = document.startViewTransition.bind(document);
    (window as unknown as { reveal: unknown[] }).reveal = [];
    document.startViewTransition = ((update: () => void) => {
      const root = document.documentElement;
      (window as unknown as { reveal: unknown[] }).reveal.push({
        style: root.dataset.themeReveal,
        x: root.style.getPropertyValue("--reveal-x"),
      });
      return original(update);
    }) as typeof document.startViewTransition;
  });
  const ember = controls(page).getByRole("button", {
    name: "Ember",
    exact: true,
  });
  const box = (await ember.boundingBox())!;
  await ember.click();
  const calls = await page.evaluate(
    () =>
      (window as unknown as { reveal: { style: string; x: string }[] }).reveal,
  );
  expect(calls).toHaveLength(1);
  expect(calls[0].style).toBe("circle");
  expect(
    Math.abs(parseFloat(calls[0].x) - (box.x + box.width / 2)),
  ).toBeLessThan(box.width);
  await expect(page.locator("html")).not.toHaveAttribute(
    "data-theme-reveal",
    /.*/,
  );
});

test("Settings › Appearance picks a palette from its own swatch", async ({
  page,
}) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("/design");
  await page.getByRole("button", { name: "Appearance", exact: true }).click();
  const option = page.locator('[data-palette-option="orchid"]');
  await expect(option.locator(".palette-sample")).toHaveAttribute(
    "data-palette",
    "orchid",
  );
  await option.click();
  await expect(option).toHaveAttribute("aria-pressed", "true");
  await expect(page.locator("html")).toHaveAttribute("data-palette", "orchid");
  await page.getByRole("button", { name: "English only", exact: true }).click();
  await expect(
    page.getByRole("button", { name: "English only", exact: true }),
  ).toHaveAttribute("aria-pressed", "true");
});
