import {
  test,
  expect,
  type Page,
  type APIRequestContext,
} from "@playwright/test";
async function setup(page: Page, request: APIRequestContext, width = 390) {
  await page.setViewportSize({ width, height: 900 });
  const conn = (await (await request.get("/api/connections")).json())[0];
  await request.patch("/api/settings", {
    data: {
      default_connection_id: conn.id,
      default_model_id: "fake-chat",
      default_preset_id: null,
      auto_title: false,
    },
  });
  await request.put("/api/models/prefs", {
    data: {
      connection_id: conn.id,
      model_id: "fake-chat",
      params: {},
      context_length: 16384,
      display_name: null,
    },
  });
  await page.goto("/");
  await expect(
    page.getByRole("button", { name: "Choose model" }),
  ).toContainText("fake-chat");
  return conn;
}
const open = (page: Page) =>
  page.getByRole("button", { name: "Chat controls", exact: true }).click();
const controls = (page: Page) =>
  page.getByRole("region", { name: "Chat controls", exact: true });
const close = (page: Page) =>
  page.getByRole("button", { name: "Close chat controls" }).click();
for (const width of [390, 1440]) {
  test(`5A preset from panel, exact payload and independent copy ${width}`, async ({
    page,
    request,
    browserName,
  }) => {
    await setup(page, request, width);
    await open(page);
    const panel = controls(page);
    await expect(
      panel.getByRole("button", { name: "Save settings", exact: true }),
    ).toBeDisabled();
    await panel
      .getByRole("switch", { name: "Use model default for Temperature" })
      .click();
    await panel
      .getByRole("spinbutton", { name: "Temperature", exact: true })
      .fill(".65");
    await panel
      .getByRole("switch", { name: "Use default system prompt" })
      .click();
    await panel
      .getByRole("textbox", { name: "System prompt", exact: true })
      .fill("Synthetic preset instruction.");
    await panel.getByRole("combobox", { name: "Preset", exact: true }).click();
    await page
      .getByRole("option", { name: "Save as preset…", exact: true })
      .click();
    const editor = page.getByRole("dialog", {
        name: "Save as preset",
        exact: true,
      }),
      name = `Synthetic ${width} ${browserName}`;
    await editor.getByRole("textbox", { name: "Preset name" }).fill(name);
    await editor
      .getByRole("button", { name: "Save preset", exact: true })
      .click();
    await expect(editor).not.toBeVisible();
    await panel.getByRole("combobox", { name: "Preset", exact: true }).click();
    await page.getByRole("option", { name, exact: true }).click();
    await panel
      .getByRole("button", { name: "Save settings", exact: true })
      .click();
    await expect(
      panel.getByRole("button", { name: "Save settings", exact: true }),
    ).toContainText("Saved");
    await close(page);
    const question = `Synthetic preset request ${width} ${browserName}`;
    await page.locator(".composer textarea").fill(question);
    await page.getByRole("button", { name: "Send message" }).click();
    await expect(page).toHaveURL(/\/c\//);
    const id = page.url().split("/c/")[1];
    const detail = async () =>
      await (await request.get(`/api/chats/${id}`)).json();
    await expect
      .poll(async () => (await detail()).messages.at(-1).status)
      .toBe("complete");
    const captures = (
      await (await request.get("http://127.0.0.1:18080/tests/state")).json()
    ).captures;
    const sent = captures.findLast(
      (r: { messages?: { content: string }[] }) =>
        r.messages?.at(-1)?.content === question,
    );
    expect(sent.options).toEqual({ temperature: 0.65, num_ctx: 16384 });
    expect(sent.messages[0].content).toContain("Synthetic preset instruction.");
    const before = (await detail()).chat;
    const preset = (await (await request.get("/api/presets")).json()).find(
      (p: { name: string }) => p.name === name,
    );
    await request.patch(`/api/presets/${preset.id}`, {
      data: {
        params: { top_k: 19 },
        system_prompt: "A different synthetic instruction.",
      },
    });
    expect((await detail()).chat).toEqual(before);
    await request.delete(`/api/presets/${preset.id}`);
    expect((await detail()).chat).toEqual(before);
  });
  test(`5A retained edits, validation and separate context Apply ${width}`, async ({
    page,
    request,
  }) => {
    await setup(page, request, width);
    await open(page);
    const panel = controls(page),
      save = panel.getByRole("button", { name: "Save settings", exact: true });
    await expect(save).toBeDisabled();
    await panel
      .getByRole("switch", { name: "Use model default for Temperature" })
      .click();
    await panel
      .getByRole("spinbutton", { name: "Temperature", exact: true })
      .fill("3");
    await expect(save).toBeDisabled();
    await expect(panel.getByText("Choose a value from 0 to 2.")).toBeVisible();
    await close(page);
    await expect(
      page
        .getByRole("button", { name: "Chat controls", exact: true })
        .locator(".bg-brand"),
    ).toBeVisible();
    await open(page);
    await expect(
      panel.getByRole("spinbutton", { name: "Temperature", exact: true }),
    ).toHaveValue("3");
    await panel
      .getByRole("spinbutton", { name: "Temperature", exact: true })
      .fill(".55");
    const chatPatches: string[] = [];
    page.on("request", (r) => {
      if (
        r.method() === "PATCH" &&
        new URL(r.url()).pathname.startsWith("/api/chats/")
      )
        chatPatches.push(r.url());
    });
    await panel
      .getByRole("spinbutton", { name: "Context length" })
      .fill("8192");
    await panel.getByRole("button", { name: "Apply context length" }).click();
    await expect(
      panel.getByRole("button", { name: "Apply context length" }),
    ).toBeDisabled();
    expect(chatPatches).toEqual([]);
    await expect(save).toBeEnabled();
    await save.click();
    await expect(save).toContainText("Saved");
    await close(page);
    await expect(
      page
        .getByRole("button", { name: "Chat controls", exact: true })
        .locator(".bg-brand"),
    ).toHaveCount(0);
    await open(page);
    await expect(
      panel.getByRole("spinbutton", { name: "Temperature", exact: true }),
    ).toHaveValue("0.55");
    await expect(save).toBeDisabled();
    await close(page);
  });
}
test("5A default preset can be explicitly cleared before first send", async ({
  page,
  request,
}) => {
  const conn = await setup(page, request);
  const preset = await (
    await request.post("/api/presets", {
      data: {
        name: "Synthetic Default",
        params: { top_k: 31 },
        system_prompt: "Synthetic default prompt.",
      },
    })
  ).json();
  await request.patch("/api/settings", {
    data: { default_preset_id: preset.id },
  });
  await page.reload();
  await open(page);
  const panel = controls(page);
  await expect(
    panel.getByRole("spinbutton", { name: "Top K", exact: true }),
  ).toHaveValue("31");
  await panel.getByRole("combobox", { name: "Preset", exact: true }).click();
  await page.getByRole("option", { name: "None", exact: true }).click();
  await panel
    .getByRole("button", { name: "Save settings", exact: true })
    .click();
  await close(page);
  await page.locator(".composer textarea").fill("Synthetic explicit None");
  await page.getByRole("button", { name: "Send message" }).click();
  await expect(page).toHaveURL(/\/c\//);
  const chat = (
    await (await request.get("/api/chats/" + page.url().split("/c/")[1])).json()
  ).chat;
  expect(chat.params).toEqual({});
  expect(chat.system_prompt).toBeNull();
  expect(chat.connection_id).toBe(conn.id);
  await request.delete(`/api/presets/${preset.id}`);
});
test("5A model name dialog, dual-name picker search and reset", async ({
  page,
  request,
}) => {
  await setup(page, request);
  await page.keyboard.press("Control+,");
  const settings = page.getByRole("dialog", { name: "Settings", exact: true });
  await settings.getByRole("button", { name: "Models", exact: true }).click();
  await settings
    .getByRole("button", { name: "Rename fake-chat", exact: true })
    .click();
  let editor = page.getByRole("dialog", { name: "Rename model", exact: true });
  await editor
    .getByRole("textbox", { name: "Display name for fake-chat", exact: true })
    .fill("Synthetic Display");
  await editor.getByRole("button", { name: "Save name" }).click();
  await expect(editor).not.toBeVisible();
  await settings.getByRole("button", { name: "Close settings" }).click();
  await expect(
    page.getByRole("button", { name: "Choose model" }),
  ).toContainText("Synthetic Display");
  await page.getByRole("button", { name: "Choose model" }).click();
  await page.getByPlaceholder("Search models…").fill("fake-chat");
  await expect(
    page.getByRole("option").filter({ hasText: "Synthetic Display" }),
  ).toBeVisible();
  await expect(
    page.getByRole("option").filter({ hasText: "Synthetic Display" }),
  ).toContainText("fake-chat");
  await page.getByPlaceholder("Search models…").fill("Synthetic Display");
  await expect(
    page.getByRole("option").filter({ hasText: "Synthetic Display" }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Close", exact: true }).click();
  await page.keyboard.press("Control+,");
  await settings.getByRole("button", { name: "Models", exact: true }).click();
  await settings
    .getByRole("button", { name: "Rename Synthetic Display", exact: true })
    .click();
  editor = page.getByRole("dialog", { name: "Rename model", exact: true });
  await editor
    .getByRole("textbox", { name: "Display name for fake-chat" })
    .fill("");
  await editor.getByRole("button", { name: "Save name" }).click();
  await expect(editor).not.toBeVisible();
  await settings.getByRole("button", { name: "Close settings" }).click();
  await expect(
    page.getByRole("button", { name: "Choose model" }),
  ).toContainText("fake-chat");
});
test("5A palette opens the preset list", async ({ page, request }) => {
  await setup(page, request);
  await page.keyboard.press("Control+k");
  await page.getByRole("option", { name: "Apply preset…" }).click();
  await expect(page.getByRole("listbox")).toBeVisible();
  await expect(
    page.getByRole("option", { name: "None", exact: true }),
  ).toBeVisible();
});

test("5A pristine new chat uses the server default without a second patch", async ({
  page,
  request,
}) => {
  await setup(page, request);
  const preset = await (
    await request.post("/api/presets", {
      data: {
        name: "Synthetic Server Default",
        params: { top_k: 29 },
        system_prompt: "Synthetic server-default prompt.",
      },
    })
  ).json();
  await request.patch("/api/settings", {
    data: { default_preset_id: preset.id },
  });
  await page.reload();
  const patches: string[] = [];
  page.on("request", (r) => {
    if (
      r.method() === "PATCH" &&
      new URL(r.url()).pathname.startsWith("/api/chats/")
    )
      patches.push(r.url());
  });
  await page
    .locator(".composer textarea")
    .fill("Synthetic server-default request");
  await page.getByRole("button", { name: "Send message" }).click();
  await expect(page).toHaveURL(/\/c\//);
  const id = page.url().split("/c/")[1];
  const detail = async () =>
    await (await request.get(`/api/chats/${id}`)).json();
  await expect
    .poll(async () => (await detail()).messages.at(-1).status)
    .toBe("complete");
  expect((await detail()).chat.params).toEqual({ top_k: 29 });
  expect(patches).toEqual([]);
  await request.delete(`/api/presets/${preset.id}`);
});

test("5A unfinished controls are isolated between chats and models", async ({
  page,
  request,
}) => {
  const conn = await setup(page, request);
  const chat = await (
    await request.post("/api/chats", {
      data: { connection_id: conn.id, model_id: "fake-chat" },
    })
  ).json();
  const other = await (
    await request.post("/api/chats", {
      data: { connection_id: conn.id, model_id: "fake-chat" },
    })
  ).json();
  await page.goto("/c/" + chat.id);
  await open(page);
  let panel = controls(page);
  await panel
    .getByRole("switch", { name: "Use model default for Top K" })
    .click();
  await panel
    .getByRole("spinbutton", { name: "Top K", exact: true })
    .fill("47");
  await close(page);
  // SPA navigation keeps the control draft store alive; both chats are synthetic.
  await page.evaluate((id) => {
    history.pushState({}, "", `/c/${id}`);
    window.dispatchEvent(new PopStateEvent("popstate"));
  }, other.id);
  await expect(page).toHaveURL("/c/" + other.id);
  await open(page);
  panel = controls(page);
  await expect(
    panel.getByRole("spinbutton", { name: "Top K", exact: true }),
  ).toHaveCount(0);
  await close(page);
  await page.evaluate((id) => {
    history.pushState({}, "", `/c/${id}`);
    window.dispatchEvent(new PopStateEvent("popstate"));
  }, chat.id);
  await open(page);
  panel = controls(page);
  await expect(
    panel.getByRole("spinbutton", { name: "Top K", exact: true }),
  ).toHaveValue("47");
  await close(page);
  const unchanged = (await (await request.get("/api/chats/" + chat.id)).json())
    .chat;
  expect(unchanged.params).toEqual({});
  await page.getByRole("button", { name: "Choose model" }).click();
  await page.getByRole("option").filter({ hasText: "fake-vision" }).click();
  await expect(
    page.getByRole("button", { name: "Choose model" }),
  ).toContainText("fake-vision");
  await open(page);
  await expect(
    controls(page).getByRole("spinbutton", { name: "Top K", exact: true }),
  ).toHaveCount(0);
});

test("5A Settings presets rename, order, default and deletion keep chat copies", async ({
  page,
  request,
}) => {
  const conn = await setup(page, request);
  const first = await (
    await request.post("/api/presets", {
      data: { name: "Synthetic One", params: { top_k: 21 } },
    })
  ).json();
  const second = await (
    await request.post("/api/presets", { data: { name: "Synthetic Two" } })
  ).json();
  const chat = await (
    await request.post("/api/chats", {
      data: {
        connection_id: conn.id,
        model_id: "fake-chat",
        preset_id: first.id,
      },
    })
  ).json();
  await page.keyboard.press("Control+,");
  const settings = page.getByRole("dialog", { name: "Settings", exact: true });
  await settings.getByRole("button", { name: "Presets", exact: true }).click();
  const one = settings.getByRole("article", { name: "Preset Synthetic One" });
  await one.getByRole("button", { name: "Move Synthetic One down" }).click();
  await expect
    .poll(async () =>
      (await (await request.get("/api/presets")).json()).map(
        (p: { id: string }) => p.id,
      ),
    )
    .toEqual([second.id, first.id]);
  await one.getByRole("button", { name: "Edit / rename" }).click();
  const editor = page.getByRole("dialog", { name: "Edit preset", exact: true });
  await editor
    .getByRole("textbox", { name: "Preset name" })
    .fill("Synthetic Renamed");
  await editor.getByRole("button", { name: "Save preset" }).click();
  await expect(editor).not.toBeVisible();
  const renamed = settings.getByRole("article", {
    name: "Preset Synthetic Renamed",
  });
  await renamed
    .getByRole("switch", { name: "Use Synthetic Renamed for new chats" })
    .click();
  await expect
    .poll(
      async () =>
        (await (await request.get("/api/settings")).json()).default_preset_id,
    )
    .toBe(first.id);
  await renamed.getByRole("button", { name: "Delete", exact: true }).click();
  const confirmation = page.getByRole("alertdialog", {
    name: "Delete preset?",
  });
  await expect(confirmation).toContainText(
    "Existing chats keep their copied settings.",
  );
  await confirmation
    .getByRole("button", { name: "Delete preset", exact: true })
    .click();
  await expect(confirmation).not.toBeVisible();
  await expect(renamed).toHaveCount(0);
  expect(
    (await (await request.get("/api/settings")).json()).default_preset_id,
  ).toBeNull();
  expect(
    (await (await request.get("/api/chats/" + chat.id)).json()).chat,
  ).toEqual(chat);
  await request.delete(`/api/presets/${second.id}`);
});

test("5A controls wait for the requested chat instead of exposing an empty draft", async ({
  page,
  request,
}) => {
  const conn = await setup(page, request);
  const chat = await (
    await request.post("/api/chats", {
      data: { connection_id: conn.id, model_id: "fake-chat" },
    })
  ).json();
  await request.patch(`/api/chats/${chat.id}`, {
    data: { params: { top_k: 42 } },
  });
  let release: () => void = () => {};
  const loaded = new Promise<void>((resolve) => {
    release = resolve;
  });
  await page.route(`**/api/chats/${chat.id}`, async (route) => {
    await loaded;
    await route.continue();
  });
  await page.goto("/c/" + chat.id);
  await open(page);
  const panel = controls(page);
  await expect(panel.getByRole("status")).toHaveText("Loading chat controls…");
  await expect(
    panel.getByRole("button", { name: "Save settings", exact: true }),
  ).toHaveCount(0);
  release();
  await expect(
    panel.getByRole("spinbutton", { name: "Top K", exact: true }),
  ).toHaveValue("42");
  await expect(
    panel.getByRole("button", { name: "Save settings", exact: true }),
  ).toBeDisabled();
});
