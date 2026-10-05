import { test, expect } from "@playwright/test";
import { settle } from "./helpers";

test.beforeEach(async ({ request, page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await request.patch("/api/settings", {
    data: { "appearance.reduce_motion": "system", auto_title: false },
  });
  await page.emulateMedia({ reducedMotion: "no-preference" });
});

test.afterEach(async ({ request }) => {
  await request.patch("/api/settings", {
    data: { "appearance.reduce_motion": "system" },
  });
});

for (const mode of ["normal", "always", "system"] as const) {
  for (const restored of [false, true]) {
    test(`app entrance ${mode}, restored chat ${restored}`, async ({
      page,
      request,
    }) => {
      await request.patch("/api/settings", {
        data: {
          "appearance.reduce_motion": mode === "always" ? "always" : "system",
        },
      });
      if (mode === "system")
        await page.emulateMedia({ reducedMotion: "reduce" });
      let path = "/";
      if (restored) {
        const [connection] = await (
          await request.get("/api/connections")
        ).json();
        const chat = await (
          await request.post("/api/chats", {
            data: { connection_id: connection.id, model_id: "fake-chat" },
          })
        ).json();
        path = `/c/${chat.id}`;
      }
      await page.addInitScript(() => {
        const entrances: number[] = [];
        Object.defineProperty(window, "appEntrances", { value: entrances });
        document.addEventListener("animationstart", (event) => {
          if (event.animationName === "app-in")
            entrances.push(performance.now());
        });
      });
      await page.goto(path);
      await expect(page.locator(".app-shell")).toHaveAttribute(
        "data-app-entry",
        "true",
      );
      await settle(page);
      const count = await page.evaluate(
        () =>
          (window as unknown as { appEntrances: number[] }).appEntrances.length,
      );
      expect(count).toBe(mode === "normal" ? 1 : 0);
      await expect(page.locator(".app-shell")).not.toHaveAttribute(
        "data-app-entry",
        "true",
      );
      await page
        .locator(".composer textarea")
        .fill("Synthetic entrance typing");
      await expect(page.locator(".composer textarea")).toHaveValue(
        "Synthetic entrance typing",
      );
      await page.keyboard.press("Control+Shift+O");
      await settle(page);
      expect(
        await page.evaluate(
          () =>
            (window as unknown as { appEntrances: number[] }).appEntrances
              .length,
        ),
      ).toBe(count);
    });
  }
}

test("changing to Always closes the selector and leaves Settings usable", async ({
  page,
}) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Choose model", exact: true }).click();
  await page
    .getByRole("button", { name: "Manage models…", exact: true })
    .click();
  const settings = page.getByRole("dialog", { name: "Settings", exact: true });
  await settings
    .getByRole("button", { name: "Appearance", exact: true })
    .click();
  await settle(page);
  const selector = settings.getByRole("combobox", { name: "Reduce motion" });
  await selector.click();
  await page.getByRole("option", { name: "Always", exact: true }).click();
  await expect(page.getByRole("listbox")).toHaveCount(0);
  await expect(selector).toHaveText("Always");
  await expect(page.locator("html")).toHaveAttribute(
    "data-reduce-motion",
    "always",
  );
  await settings.getByRole("button", { name: "Close settings" }).click();
  await expect(settings).toHaveCount(0);
  await page.getByRole("button", { name: "Choose model", exact: true }).click();
  const picker = page.getByRole("dialog", {
    name: "Choose model",
    exact: true,
  });
  await expect(picker).toBeVisible();
  expect(
    await picker.evaluate((el) => getComputedStyle(el).animationName),
  ).toBe("none");
  await page.keyboard.press("Escape");
  await expect(picker).toHaveCount(0);
});
