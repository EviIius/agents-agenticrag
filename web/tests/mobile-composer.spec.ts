import { test, expect } from "@playwright/test";

test.use({ hasTouch: true, viewport: { width: 390, height: 844 } });

test("touch composer accepts typing before and after mobile overlays", async ({
  page,
  request,
}) => {
  const connection = (await (await request.get("/api/connections")).json())[0];
  await request.patch("/api/settings", {
    data: {
      default_connection_id: connection.id,
      default_model_id: "fake-chat",
      "web.default_on": false,
    },
  });
  await page.goto("/");
  await expect(
    page.getByRole("button", { name: "Choose model" }),
  ).toContainText("fake-chat");
  const composer = page.locator(".composer textarea");
  const typeByTouch = async () => {
    await composer.tap();
    await expect(composer).toBeFocused();
    await page.keyboard.type("Synthetic touch draft");
    await expect(composer).toHaveValue("Synthetic touch draft");
    await expect(
      page.getByRole("button", { name: "Send message" }),
    ).toBeEnabled();
    await composer.fill("");
  };
  await typeByTouch();
  await page.getByRole("button", { name: "Choose model" }).tap();
  await page.getByRole("button", { name: "Close", exact: true }).tap();
  await typeByTouch();
  await page.getByRole("button", { name: "Chat settings", exact: true }).tap();
  await page.getByRole("button", { name: "Close chat settings" }).tap();
  await typeByTouch();
  await page.getByRole("button", { name: "Add attachment" }).tap();
  await page.getByRole("menu", { name: "Add attachment", exact: true }).focus();
  await page.keyboard.press("Escape");
  await typeByTouch();
  await composer.tap();
  await page.keyboard.type("Synthetic mobile request");
  await page.getByRole("button", { name: "Send message" }).tap();
  await expect(page).toHaveURL(/\/c\/[^/]+$/);
  await expect(
    page.getByRole("button", { name: "Stop generating" }),
  ).toHaveCount(0);
  await typeByTouch();
});
