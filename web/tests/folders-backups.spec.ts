import { test, expect } from "@playwright/test";
for (const width of [390, 1440]) {
  test(`5C folders create move collapse search rename and delete preserve chat ${width}`, async ({
    page,
    request,
    browserName,
  }) => {
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
    const text = `Invented folder conversation ${width} ${browserName}`,
      name = `Invented orchard ${width} ${browserName}`,
      renamed = `Invented meadow ${width} ${browserName}`;
    await page.goto("/");
    await page.locator(".composer textarea").fill(text);
    await page
      .getByRole("button", { name: "Send message", exact: true })
      .click();
    await expect(page).toHaveURL(/\/c\//);
    const id = page.url().split("/c/")[1];
    await expect(
      page.getByRole("article", { name: "assistant message" }),
    ).toContainText("Fake runtime reply.");
    const open = async () => {
      if (width < 640)
        await page
          .getByRole("button", { name: "Open sidebar", exact: true })
          .click();
    };
    const nav = page.getByRole("navigation", { name: "Chat history" });
    await open();
    await nav.getByRole("button", { name: "New folder", exact: true }).click();
    const dialog = page.getByRole("dialog", {
      name: "New folder",
      exact: true,
    });
    await expect(
      dialog.getByRole("button", { name: "Save folder", exact: true }),
    ).toBeDisabled();
    await dialog.getByRole("textbox", { name: "Folder name" }).fill(name);
    await dialog
      .getByRole("button", { name: "Save folder", exact: true })
      .click();
    await expect(dialog).toBeHidden();
    await open();
    const row = nav.getByRole("button", {
      name: `Folder ${name}, 0 chats`,
      exact: true,
    });
    await expect(row).toBeVisible();
    await nav
      .getByRole("button", { name: `Actions for ${text}`, exact: true })
      .click();
    await page
      .getByRole("menuitem", { name: "Move to folder", exact: true })
      .click();
    await page.getByRole("menuitem", { name, exact: true }).click();
    const folder = (await (await request.get("/api/folders")).json()).find(
      (f: { name: string }) => f.name === name,
    );
    await expect
      .poll(
        async () =>
          (await (await request.get(`/api/chats/${id}`)).json()).chat.folder_id,
      )
      .toBe(folder.id);
    await expect(
      nav.getByRole("link", { name: text, exact: true }),
    ).toBeHidden();
    const toggle = nav.getByRole("button", {
      name: `Folder ${name}, 1 chats`,
      exact: true,
    });
    await toggle.click();
    await expect(
      nav.getByRole("link", { name: text, exact: true }),
    ).toBeVisible();
    await toggle.click();
    await expect(
      nav.getByRole("link", { name: text, exact: true }),
    ).toBeHidden();
    await nav.getByRole("textbox", { name: "Search history" }).fill(text);
    await expect(
      nav.getByRole("link", { name: text, exact: true }),
    ).toContainText(name);
    await nav.getByRole("textbox", { name: "Search history" }).fill("");
    await nav
      .getByRole("button", { name: `Actions for folder ${name}`, exact: true })
      .click();
    await page
      .getByRole("menuitem", { name: "Rename folder", exact: true })
      .click();
    const rename = page.getByRole("dialog", {
      name: "Rename folder",
      exact: true,
    });
    await rename.getByRole("textbox", { name: "Folder name" }).fill(renamed);
    await rename
      .getByRole("button", { name: "Save folder", exact: true })
      .click();
    await expect(rename).toBeHidden();
    await open();
    await nav
      .getByRole("button", {
        name: `Actions for folder ${renamed}`,
        exact: true,
      })
      .click();
    await page
      .getByRole("menuitem", { name: "Delete folder", exact: true })
      .click();
    const remove = page.getByRole("dialog", {
      name: "Delete folder?",
      exact: true,
    });
    await expect(remove).toContainText("No chats are deleted.");
    await remove.getByRole("button", { name: "Cancel", exact: true }).click();
    await open();
    await expect(
      nav.getByRole("button", {
        name: `Folder ${renamed}, 1 chats`,
        exact: true,
      }),
    ).toBeVisible();
    await nav
      .getByRole("button", {
        name: `Actions for folder ${renamed}`,
        exact: true,
      })
      .click();
    await page
      .getByRole("menuitem", { name: "Delete folder", exact: true })
      .click();
    await page
      .getByRole("dialog", { name: "Delete folder?", exact: true })
      .getByRole("button", { name: "Delete folder", exact: true })
      .click();
    await expect(
      page.getByRole("dialog", { name: "Delete folder?", exact: true }),
    ).toBeHidden();
    await open();
    await expect(
      nav.getByRole("link", { name: text, exact: true }),
    ).toBeVisible();
    const detail = await (await request.get(`/api/chats/${id}`)).json();
    expect(detail.chat.folder_id).toBeNull();
    expect(detail.messages).toHaveLength(2);
    await request.delete(`/api/chats/${id}`);
  });
  test(`5C backup status manual backup and failure remains usable ${width}`, async ({
    page,
  }) => {
    await page.setViewportSize({ width, height: 900 });
    await page.goto("/");
    if (width < 640)
      await page
        .getByRole("button", { name: "Open sidebar", exact: true })
        .click();
    await page.getByRole("button", { name: "Settings", exact: true }).click();
    await page.getByRole("button", { name: "Data", exact: true }).click();
    const section = page.getByRole("region", { name: "Database backups" });
    await expect(section).toContainText(/Last backup:/);
    await expect(section).toContainText("Attachment files are not included");
    let release: () => void = () => {};
    const gate = new Promise<void>((resolve) => {
      release = resolve;
    });
    await page.route("**/api/backup", async (route) => {
      if (route.request().method() === "POST") {
        await gate;
        await route.continue();
      } else await route.continue();
    });
    await section
      .getByRole("button", { name: "Back up now", exact: true })
      .click();
    await expect(
      section.getByRole("button", { name: "Backing up…", exact: true }),
    ).toBeDisabled();
    release();
    await expect(
      section.getByRole("button", { name: "Back up now", exact: true }),
    ).toBeEnabled();
    await page.unroute("**/api/backup");
    await page.route("**/api/backup", async (route) => {
      if (route.request().method() === "POST")
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            last_at: null,
            count: 0,
            bytes: 0,
            warning:
              "Backup skipped: not enough free disk space. Free space and try again.",
          }),
        });
      else await route.continue();
    });
    await section
      .getByRole("button", { name: "Back up now", exact: true })
      .click();
    await expect(section.getByRole("alert")).toContainText(
      "not enough free disk space",
    );
    await expect(
      section.getByRole("button", { name: "Back up now", exact: true }),
    ).toBeEnabled();
  });
}
