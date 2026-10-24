import { expect, test } from "@playwright/test";
import { settle } from "./helpers";

test("English only takes effect during a greeting exit", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "no-preference" });
  await page.goto("/design?themes");
  const heading = page.locator("h1.greeting");
  await expect(heading.locator(".greet-word")).toHaveAttribute(
    "data-leaving",
    "true",
  );
  await page.evaluate(async () => {
    const path = "/src/stores/ui.ts";
    const { useUI } = await import(path);
    useUI.getState().set({ greeting: "english" });
  });
  await expect(heading).not.toHaveAttribute("data-animate", /.*/, {
    timeout: 1000,
  });
  await expect(heading.locator(".greet-word")).toHaveAttribute("lang", "en");
  await expect(heading.locator(".greet-word")).not.toHaveAttribute(
    "data-leaving",
    /.*/,
  );
});

test("an unrelated ambient label cannot bypass the one-second settle gate", async ({
  page,
}) => {
  await page.emulateMedia({ reducedMotion: "no-preference" });
  await page.goto("/design?themes");
  await expect(page.locator("h1.greeting")).toBeVisible();
  await page.evaluate(() => {
    const element = document.createElement("div");
    element.dataset.motion = "ambient";
    element.textContent = "Synthetic unrelated surface";
    document.body.append(element);
    element.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 5000 });
  });
  await expect(settle(page)).rejects.toThrow("1,000 ms");
});

test("turning reduced motion off does not resume an abandoned greeting", async ({
  page,
}) => {
  await page.emulateMedia({ reducedMotion: "no-preference" });
  await page.goto("/design?themes");
  const heading = page.locator("h1.greeting");
  await expect(heading).toHaveAttribute("data-animate", "true");
  await page
    .getByRole("switch", { name: "Reduce motion", exact: true })
    .check();
  await expect(heading).not.toHaveAttribute("data-animate", /.*/);
  await expect(heading.locator(".greet-word")).toHaveAttribute("lang", "en");
  await page
    .getByRole("switch", { name: "Reduce motion", exact: true })
    .uncheck();
  await expect(heading).not.toHaveAttribute("data-animate", /.*/, {
    timeout: 1000,
  });
  await expect(heading.locator(".greet-word")).toHaveAttribute("lang", "en");
});
