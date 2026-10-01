import { test, expect } from "@playwright/test";
import { readFile } from "node:fs/promises";
for (const width of [390, 1440]) {
  test(`branches and history actions ${width}`, async ({
    page,
    request,
    browserName,
  }) => {
    const original = `Original branch ${width} ${browserName}`;
    const edited = `Edited branch ${width} ${browserName}`;
    const renamed = `Reviewed branches ${width} ${browserName}`;
    await page.setViewportSize({ width, height: 900 });
    const connection = (
      await (await request.get("/api/connections")).json()
    )[0];
    await request.patch("/api/settings", {
      data: {
        default_connection_id: connection.id,
        default_model_id: "fake-chat",
        auto_title: false,
      },
    });
    await page.goto("/");
    await expect(
      page.getByRole("button", { name: "Choose model" }),
    ).toContainText("fake-chat");
    await page.locator(".composer textarea").fill(original);
    await page.getByRole("button", { name: "Send message" }).click();
    await expect(page).toHaveURL(/\/c\//);
    const id = page.url().split("/c/")[1]!;
    const detail = async () =>
      await (await request.get(`/api/chats/${id}`)).json();
    await expect
      .poll(
        async () =>
          (await detail()).messages.filter(
            (m: { role: string; status: string }) =>
              m.role === "assistant" && m.status === "complete",
          ).length,
      )
      .toBe(1);
    await page
      .getByRole("button", { name: "Regenerate answer", exact: true })
      .click();
    await expect
      .poll(
        async () =>
          (await detail()).messages.filter(
            (m: { role: string; status: string }) =>
              m.role === "assistant" && m.status === "complete",
          ).length,
      )
      .toBe(2);
    const assistant = page.getByRole("article", { name: "assistant message" });
    await expect(assistant).toContainText("2 / 2");
    await assistant.getByRole("button", { name: "Previous branch" }).click();
    await expect(assistant).toContainText("1 / 2");
    await page.reload();
    await expect(assistant).toContainText("1 / 2");
    await page
      .getByRole("button", { name: "Edit message", exact: true })
      .click();
    await page
      .getByRole("textbox", { name: "Edit message", exact: true })
      .fill(edited);
    await page.getByRole("button", { name: "Save & submit" }).click();
    await expect
      .poll(
        async () =>
          (await detail()).messages.filter(
            (m: { role: string; status: string }) =>
              m.role === "assistant" && m.status === "complete",
          ).length,
      )
      .toBe(3);
    const user = page.getByRole("article", { name: "user message" });
    await expect(user).toContainText(edited);
    await user.getByRole("button", { name: "Previous branch" }).click();
    await expect(user).toContainText(original);
    await page.reload();
    await expect(user).toContainText(original);
    if (width < 640)
      await page.getByRole("button", { name: "Open sidebar" }).click();
    await page.getByRole("textbox", { name: "Search history" }).fill(original);
    const row = page.getByRole("link", {
      name: original,
      exact: true,
    });
    await expect(row).toBeVisible();
    const history = page.getByRole("navigation", { name: "Chat history" });
    const actions = history.getByRole("button", {
      name: `Actions for ${original}`,
      exact: true,
    });
    await actions.click();
    await page.getByRole("menuitem", { name: "Pin", exact: true }).click();
    await expect(page.locator('[role="menu"]')).toHaveCount(0);
    await expect.poll(async () => (await detail()).chat.pinned).toBe(true);
    await actions.click();
    const downloadReady = page.waitForEvent("download");
    await page.getByRole("menuitem", { name: "Export JSON" }).focus();
    await page.keyboard.press("Enter");
    const download = await downloadReady;
    await page.bringToFront();
    await expect(page.locator('[role="menu"]')).toHaveCount(0);
    // Export uses the current branch; the edited sibling remains in the database.
    const exported = JSON.parse(
      await readFile((await download.path())!, "utf8"),
    );
    expect(JSON.stringify(exported)).toContain(original);
    expect(JSON.stringify(exported.messages)).not.toContain(edited);
    await actions.click();
    await page.getByRole("menuitem", { name: "Rename", exact: true }).focus();
    await page.keyboard.press("Enter");
    await page.getByRole("textbox", { name: "Chat title" }).fill(renamed);
    await page.getByRole("button", { name: "Save title" }).click();
    await expect.poll(async () => (await detail()).chat.title).toBe(renamed);
    if (width < 640)
      await page.getByRole("button", { name: "Open sidebar" }).click();
    await page.getByRole("textbox", { name: "Search history" }).fill(renamed);
    await history
      .getByRole("button", { name: `Actions for ${renamed}` })
      .click();
    await page.getByRole("menuitem", { name: "Delete", exact: true }).click();
    await page
      .getByRole("alertdialog")
      .getByRole("button", { name: "Delete", exact: true })
      .click();
    await expect
      .poll(async () => (await request.get(`/api/chats/${id}`)).status())
      .toBe(404);
    await expect(page).toHaveURL(/\/$/);
  });
}

test("data export, confirmation and About details", async ({
  page,
  request,
}) => {
  await request.post("/api/chats", { data: { model_id: "fake-chat" } });
  await page.goto("/");
  await page.keyboard.press("Control+,");
  const settings = page.getByRole("dialog", { name: "Settings" });
  await settings.getByRole("button", { name: "About", exact: true }).click();
  await expect(settings.getByText(/Data folder:/)).toBeVisible();
  await expect(settings.getByText(/Fake runtime ·/)).toBeVisible();
  await settings.getByRole("button", { name: "Data", exact: true }).click();
  const ready = page.waitForEvent("download");
  await settings.getByRole("link", { name: "Export all chats" }).click();
  const download = await ready;
  const exported = JSON.parse(await readFile((await download.path())!, "utf8"));
  expect(exported.format).toBe("workbench-chats");
  expect(exported.chats.length).toBeGreaterThan(0);
  await settings
    .getByRole("button", { name: "Delete all chats", exact: true })
    .click();
  const confirmation = page.getByRole("alertdialog");
  await expect(
    confirmation.getByRole("button", { name: "Delete chats", exact: true }),
  ).toBeDisabled();
  await confirmation
    .getByRole("textbox", { name: "Type DELETE to confirm" })
    .fill("delete");
  await expect(
    confirmation.getByRole("button", { name: "Delete chats", exact: true }),
  ).toBeDisabled();
  await confirmation
    .getByRole("textbox", { name: "Type DELETE to confirm" })
    .fill("DELETE");
  await confirmation
    .getByRole("button", { name: "Delete chats", exact: true })
    .click();
  await expect(settings).not.toBeVisible();
  await expect
    .poll(
      async () => (await (await request.get("/api/chats")).json()).items.length,
    )
    .toBe(0);
  await expect(
    page.getByRole("button", { name: "Choose model" }),
  ).toBeVisible();
});
