import { test, expect } from "@playwright/test";

test("rejected send preserves both source and new-chat drafts across remounts", async ({ page, request }) => {
  const connection = (await (await request.get("/api/connections")).json())[0];
  await request.patch("/api/settings", { data: { default_connection_id: connection.id, default_model_id: "fake-chat", auto_title: false, "web.default_on": false } });
  const chat = (await (await request.post("/api/chats", { data: { connection_id: connection.id, model_id: "fake-chat", web_enabled: false } })).json());
  await page.goto(`/c/${chat.id}`);
  const field = page.locator(".composer textarea");
  await expect(page.getByRole("button", { name: "Choose model", exact: true })).toContainText("fake-chat");
  let release!: () => void;
  const pending = new Promise<void>((resolve) => { release = resolve; });
  await page.route(`**/api/chats/${chat.id}/messages`, async (route) => {
    await pending;
    await route.fulfill({ status: 422, contentType: "application/json", body: JSON.stringify({ error: { code: "context_overflow", message: "Synthetic rejection" } }) });
  });
  await field.fill("Synthetic rejected source draft");
  await page.getByRole("button", { name: "Send message", exact: true }).click();
  await expect(page.getByTestId("optimistic-send")).toBeVisible();
  await page.evaluate(() => { history.pushState({}, "", "/"); dispatchEvent(new PopStateEvent("popstate")); });
  await expect(page).toHaveURL(/\/$/);
  await field.fill("Synthetic untouched new-chat draft");
  release();
  await expect(page.getByTestId("optimistic-send")).toHaveCount(0);
  await expect(field).toHaveValue("Synthetic untouched new-chat draft");
  await expect(page.getByRole("alert")).toHaveCount(0);
  await page.evaluate((url) => { history.pushState({}, "", url); dispatchEvent(new PopStateEvent("popstate")); }, `/c/${chat.id}`);
  await expect(field).toHaveValue("Synthetic rejected source draft");
});

test("a loaded Library embedding model can be explicitly ejected without changing the chat model", async ({ page, request }) => {
  const connection = (await (await request.get("/api/connections")).json())[0];
  const regular = await (await request.get("/api/models")).json();
  const embedding = { ...regular[0], model_id: "fake-embedding", display_name: "Synthetic Library embedding", chat_capable: false, embedding: true, reasoning: null, vision: false, loaded: true, hidden: true };
  let loaded = true;
  const ejected: string[] = [];
  await page.route("**/api/models?include_hidden=true", (route) => route.fulfill({ json: [...regular, { ...embedding, loaded }] }));
  await page.route("**/api/models/unload", async (route) => {
    ejected.push(route.request().postDataJSON().model_id);
    loaded = false;
    await route.fulfill({ json: { ok: true } });
  });
  await request.patch("/api/settings", { data: { default_connection_id: connection.id, default_model_id: "fake-chat" } });
  await page.goto("/");
  await page.keyboard.press("Control+Comma");
  // Open the actual app settings through the sidebar on both desktop and phone.
  if (!await page.getByRole("dialog", { name: "Settings", exact: true }).isVisible()) {
    const open = page.getByRole("button", { name: "Open sidebar", exact: true });
    if (await open.isVisible()) await open.click();
    await page.getByRole("button", { name: "Settings", exact: true }).click();
  }
  const dialog = page.getByRole("dialog", { name: "Settings", exact: true });
  await dialog.getByRole("tab", { name: "Models", exact: true }).click();
  const card = dialog.locator("div.rounded-lg").filter({ has: page.getByRole("heading", { name: "Synthetic Library embedding", exact: true }) });
  await expect(card.getByRole("button", { name: "Eject", exact: true })).toBeEnabled();
  expect(ejected).toEqual([]);
  await card.getByRole("button", { name: "Eject", exact: true }).click();
  await expect(card).toContainText("Not loaded");
  expect(ejected).toEqual(["fake-embedding"]);
});
