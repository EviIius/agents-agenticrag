import { settle } from "./helpers";
import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { mkdir } from "node:fs/promises";
for (const width of [320, 390, 1440])
  for (const theme of ["light", "dark"]) {
    test(`palette actions and keyboard ${width} ${theme}`, async ({
      page,
      request,
    }) => {
      await page.setViewportSize({ width, height: width < 640 ? 844 : 900 });
      const connection = (
        await (await request.get("/api/connections")).json()
      )[0];
      const created = await (
        await request.post("/api/chats", {
          data: { connection_id: connection.id, model_id: "fake-chat" },
        })
      ).json();
      try {
        await request.post(`/api/chats/${created.id}/messages`, {
          data: { content: "Synthetic palette search phrase" },
        });
        await request.patch(`/api/chats/${created.id}`, {
          data: { title: "Synthetic palette chat" },
        });
        await request.patch("/api/settings", {
          data: {
            "appearance.theme": theme,
            default_connection_id: connection.id,
            default_model_id: "fake-chat",
          },
        });
        await page.goto("/");
        await expect(
          page.getByRole("button", { name: "Choose model" }),
        ).toContainText("fake-chat");
        await page.locator(".composer textarea").focus();
        await page.keyboard.press("Control+k");
        const dialog = page.getByRole("dialog", { name: "Command palette" });
        const input = dialog.getByRole("combobox", {
          name: "Search chats and actions",
        });
        await expect(input).toBeFocused();
        await expect(
          dialog.getByRole("option", { name: "Toggle theme", exact: true }),
        ).toBeVisible();
        await input.fill("palette search phrase");
        await expect(
          dialog.getByRole("option", { name: /Synthetic palette chat/ }),
        ).toBeVisible();
        await input.fill("");
        const close = dialog.getByRole("button", {
          name: "Close command palette",
        });
        if (await page.evaluate(() => matchMedia("(pointer: coarse)").matches))
          await expect(close).toBeInViewport({ ratio: 1 });
        else await expect(close).toHaveCount(0);
        await mkdir("../artifacts/phase-3", { recursive: true });
        await settle(page);
        await page.screenshot({
          animations: "disabled",
          path: `../artifacts/phase-3/palette-${width}-${theme}-fake.png`,
        });
        await settle(page);
        expect(
          (await new AxeBuilder({ page }).analyze()).violations.filter((v) =>
            ["serious", "critical"].includes(v.impact ?? ""),
          ),
        ).toEqual([]);
        await input.fill("toggle theme");
        await expect(
          dialog.getByRole("option", { name: "Toggle theme", exact: true }),
        ).toHaveAttribute("data-selected", "true");
        await page.keyboard.press("Enter");
        await expect(dialog).not.toBeVisible();
        await expect(page.locator("html")).toHaveAttribute(
          "data-theme",
          theme === "light" ? "dark" : "light",
        );
        await page.keyboard.press("Control+k");
        await dialog
          .getByRole("option", { name: "Switch model…", exact: true })
          .click();
        await expect(
          page.getByRole("option", { name: /fake-reasoning/ }),
        ).toBeVisible();
        await settle(page);
        await page.keyboard.press("Escape");
        await expect(
          page.getByRole("option", { name: /fake-reasoning/ }),
        ).not.toBeVisible();
        await settle(page);
        await page.keyboard.press("Control+/");
        await expect(
          page.getByRole("dialog", { name: "Settings" }),
        ).toBeVisible();
        await expect(
          page.getByRole("heading", { name: "Shortcuts", exact: true }),
        ).toBeVisible();
        await settle(page);
        await page.keyboard.press("Escape");
        await expect(
          page.getByRole("dialog", { name: "Settings" }),
        ).toHaveCount(0);
        await page.keyboard.press("Control+k");
        await expect(input).toBeFocused();
        await input.fill("palette search phrase");
        await dialog
          .getByRole("option", { name: /Synthetic palette chat/ })
          .click();
        await expect(page).toHaveURL(new RegExp(`/c/${created.id}$`));
      } finally {
        await request.delete(`/api/chats/${created.id}`);
      }
    });
  }
test("palette error, empty, retry and import cancellation", async ({
  page,
}) => {
  await page.goto("/");
  await expect(
    page.getByRole("button", { name: "Choose model" }),
  ).toContainText("fake-chat");
  await page.route("**/api/chats?q=*", (route) =>
    route.fulfill({ status: 503, body: "Synthetic error" }),
  );
  await page.keyboard.press("Control+k");
  const dialog = page.getByRole("dialog", { name: "Command palette" });
  await expect(dialog.getByRole("alert")).toContainText(
    "Couldn't search chats",
  );
  await page.unroute("**/api/chats?q=*");
  await dialog.getByRole("button", { name: "Retry", exact: true }).click();
  await dialog.getByRole("combobox").fill("nonexistent-unique-synthetic");
  await expect(dialog.getByText("No chats or actions found")).toBeVisible();
  await page.keyboard.press("Escape");
  await page.route("**/api/chats/legacy-import", (route) =>
    route.fulfill({ json: { available: true } }),
  );
  await page.keyboard.press("Control+,");
  await page.getByRole("button", { name: "Data", exact: true }).click();
  await page.getByRole("button", { name: "Import old chats" }).click();
  await expect(
    page.getByRole("alertdialog", { name: "Import old chats?" }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Cancel", exact: true }).click();
  await expect(page.getByRole("alertdialog")).not.toBeVisible();
});
