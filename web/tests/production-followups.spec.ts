import { expect, test } from "@playwright/test";
import { mkdir } from "node:fs/promises";
import { settle } from "./helpers";

const dir = "../artifacts/production-followups/browser";

test("user title survives the first send, completion and reload", async ({
  page,
  request,
  browserName,
}) => {
  const [connection] = await (await request.get("/api/connections")).json();
  await request.patch("/api/settings", {
    data: { auto_title: true, "web.default_on": false },
  });
  const chat = await (
    await request.post("/api/chats", {
      data: {
        connection_id: connection.id,
        model_id: "fake-chat",
        web_enabled: false,
      },
    })
  ).json();
  await page.goto(`/c/${chat.id}`);
  await page
    .getByRole("button", { name: `Actions for ${chat.title}`, exact: true })
    .click();
  await page.getByRole("menuitem", { name: "Rename", exact: true }).click();
  const dialog = page.getByRole("dialog", { name: "Rename chat", exact: true });
  const title = "Synthetic preserved title";
  await dialog.getByRole("textbox", { name: "Chat title" }).fill(title);
  await dialog.getByRole("button", { name: "Save title", exact: true }).click();
  await expect(dialog).not.toBeVisible();
  await expect(page.locator(".topbar-title")).toHaveText(title);
  await page
    .locator(".composer textarea")
    .fill("A different synthetic question");
  await page.getByRole("button", { name: "Send message", exact: true }).click();
  await expect(
    page.getByRole("button", { name: "Regenerate answer", exact: true }),
  ).toBeVisible();
  await expect(page.locator(".topbar-title")).toHaveText(title);
  await page.reload();
  await expect(page.locator(".topbar-title")).toHaveText(title);
  const detail = await (await request.get(`/api/chats/${chat.id}`)).json();
  expect(detail.chat.title_source).toBe("user");
  expect(detail.messages.at(-1).status).toBe("complete");
  expect(
    detail.messages.filter((m: { role: string }) => m.role === "user"),
  ).toHaveLength(1);
  await settle(page);
  await mkdir(dir, { recursive: true });
  await page.screenshot({
    path: `${dir}/preserved-title-${browserName}-fake.png`,
  });
  await request.patch("/api/settings", { data: { auto_title: false } });
});
