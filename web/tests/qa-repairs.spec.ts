import { test, expect } from "@playwright/test";
import { mkdir } from "node:fs/promises";

test("rejected send preserves both source and new-chat drafts across remounts", async ({
  page,
  request,
}) => {
  const connection = (await (await request.get("/api/connections")).json())[0];
  await request.patch("/api/settings", {
    data: {
      default_connection_id: connection.id,
      default_model_id: "fake-chat",
      auto_title: false,
      "web.default_on": false,
    },
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
  const field = page.locator(".composer textarea");
  await expect(
    page.getByRole("button", { name: "Choose model", exact: true }),
  ).toContainText("fake-chat");
  let release!: () => void;
  const pending = new Promise<void>((resolve) => {
    release = resolve;
  });
  await page.route(`**/api/chats/${chat.id}/messages`, async (route) => {
    await pending;
    await route.fulfill({
      status: 422,
      contentType: "application/json",
      body: JSON.stringify({
        error: { code: "context_overflow", message: "Synthetic rejection" },
      }),
    });
  });
  await field.fill("Synthetic rejected source draft");
  await page.getByRole("button", { name: "Send message", exact: true }).click();
  await expect(page.getByTestId("optimistic-send")).toBeVisible();
  await page.evaluate(() => {
    history.pushState({}, "", "/");
    dispatchEvent(new PopStateEvent("popstate"));
  });
  await expect(page).toHaveURL(/\/$/);
  await field.fill("Synthetic untouched new-chat draft");
  release();
  await expect(page.getByTestId("optimistic-send")).toHaveCount(0);
  await expect(field).toHaveValue("Synthetic untouched new-chat draft");
  await expect(page.getByRole("alert")).toHaveCount(0);
  await page.evaluate((url) => {
    history.pushState({}, "", url);
    dispatchEvent(new PopStateEvent("popstate"));
  }, `/c/${chat.id}`);
  await expect(field).toHaveValue("Synthetic rejected source draft");
  await page.evaluate(() => {
    history.pushState({}, "", "/");
    dispatchEvent(new PopStateEvent("popstate"));
  });
  await expect(field).toHaveValue("Synthetic untouched new-chat draft");
  await mkdir("../artifacts/qa-roadmap/repair-1/browser", { recursive: true });
  await page.screenshot({
    path: `../artifacts/qa-roadmap/repair-1/browser/restored-draft-${test.info().project.name}-fake.png`,
  });
});

test("a loaded Library embedding model can be explicitly ejected without changing the chat model", async ({
  page,
  request,
}) => {
  const connection = (await (await request.get("/api/connections")).json())[0];
  const regular = await (await request.get("/api/models")).json();
  const embedding = {
    ...regular[0],
    model_id: "fake-embedding",
    display_name: "Synthetic Library embedding",
    chat_capable: false,
    embedding: true,
    reasoning: null,
    vision: false,
    loaded: true,
    hidden: true,
  };
  let loaded = true;
  const ejected: string[] = [];
  await page.route("**/api/models?include_hidden=true", (route) =>
    route.fulfill({ json: [...regular, { ...embedding, loaded }] }),
  );
  await page.route("**/api/models/unload", async (route) => {
    ejected.push(route.request().postDataJSON().model_id);
    loaded = false;
    await route.fulfill({ json: { ok: true } });
  });
  await request.patch("/api/settings", {
    data: {
      default_connection_id: connection.id,
      default_model_id: "fake-chat",
    },
  });
  await page.goto("/");
  await page.keyboard.press("Control+Comma");
  // Open the actual app settings through the sidebar on both desktop and phone.
  if (
    !(await page
      .getByRole("dialog", { name: "Settings", exact: true })
      .isVisible())
  ) {
    const open = page.getByRole("button", {
      name: "Open sidebar",
      exact: true,
    });
    if (await open.isVisible()) await open.click();
    await page.getByRole("button", { name: "Settings", exact: true }).click();
  }
  const dialog = page.getByRole("dialog", { name: "Settings", exact: true });
  await dialog.getByRole("button", { name: "Models", exact: true }).click();
  const card = dialog.locator("div.rounded-lg").filter({
    has: page.getByRole("heading", {
      name: "Synthetic Library embedding",
      exact: true,
    }),
  });
  await expect(
    card.getByRole("button", { name: "Eject", exact: true }),
  ).toBeEnabled();
  expect(ejected).toEqual([]);
  await card.getByRole("button", { name: "Eject", exact: true }).click();
  await expect(card).toContainText("Not loaded");
  expect(ejected).toEqual(["fake-embedding"]);
  await mkdir("../artifacts/qa-roadmap/repair-1/browser", { recursive: true });
  await page.screenshot({
    path: `../artifacts/qa-roadmap/repair-1/browser/embedding-ejected-${test.info().project.name}-fake.png`,
  });
});

test("long-thinking guidance starts at a minute and Stop reply uses cancellation without an answer claim", async ({
  page,
}) => {
  await page.clock.install();
  await page.goto("/design?indicator");
  await page
    .getByRole("button", { name: "Preview Thinking", exact: true })
    .click();
  const warning = page.getByTestId("long-thinking");
  await expect(warning).toHaveCount(0);
  await page.clock.fastForward(59000);
  await expect(warning).toHaveCount(0);
  await page.clock.fastForward(2000);
  await expect(warning).toBeVisible();
  await expect(warning).toContainText("does not guarantee a better answer");
  await mkdir("../artifacts/qa-roadmap/repair-1/browser", { recursive: true });
  await page.screenshot({
    path: `../artifacts/qa-roadmap/repair-1/browser/long-thinking-${test.info().project.name}-fake.png`,
  });
  await warning
    .getByRole("button", { name: "Stop reply", exact: true })
    .click();
  await expect(warning).toHaveCount(0);
  await expect(page.locator('[data-streaming="true"]')).toHaveCount(0);
});

test("thinking menu says Model default and exposes only reported options", async ({
  page,
  request,
}) => {
  const connection = (await (await request.get("/api/connections")).json())[0];
  await request.patch("/api/settings", {
    data: {
      default_connection_id: connection.id,
      default_model_id: "fake-reasoning",
      auto_title: false,
    },
  });
  await page.goto("/");
  await expect(
    page.getByRole("button", { name: "Choose model", exact: true }),
  ).toContainText("fake-reasoning");
  await page.getByRole("button", { name: "Tools", exact: true }).click();
  const option = page.getByRole("menuitemradio", {
    name: "Model default",
    exact: true,
  });
  await expect(option).toHaveText("Default");
  await expect(option).toHaveAttribute("title", "Model default");
  await expect(option).toHaveAttribute("aria-checked", "true");
  await expect(
    page.getByRole("menuitemradio", { name: "High", exact: true }),
  ).toHaveCount(0);
  await page.getByRole("menuitemradio", { name: "On", exact: true }).click();
  await expect(
    page.getByRole("menuitemradio", { name: "On", exact: true }),
  ).toHaveAttribute("aria-checked", "true");
  await option.click();
  await expect(option).toHaveAttribute("aria-checked", "true");
});

test("thinking elapsed excludes retrieval and its Stop reply cancels the active run once", async ({
  page,
  request,
}) => {
  await page.clock.install();
  const connection = (await (await request.get("/api/connections")).json())[0];
  await request.patch("/api/settings", {
    data: { auto_title: false, "web.default_on": false },
  });
  const chat = await (
    await request.post("/api/chats", {
      data: {
        connection_id: connection.id,
        model_id: "fake-reasoning",
        web_enabled: false,
      },
    })
  ).json();
  await page.addInitScript(() => {
    const Native = window.EventSource;
    window.EventSource = class extends EventTarget {
      constructor(url: string | URL, options?: EventSourceInit) {
        super();
        if (!/^\/api\/runs\/[^/]+\/events$/.test(String(url)))
          return new Native(url, options);
        Object.assign(window, { qaRunEvents: this });
      }
      close() {}
    } as unknown as typeof EventSource;
  });
  await page.route(`**/api/chats/${chat.id}/messages`, async (route) => {
    const response = await route.fetch();
    const body = await response.json();
    body.assistant_message.created_at = new Date(
      Date.now() - 120000,
    ).toISOString();
    body.assistant_message.stats = {
      ...body.assistant_message.stats,
      ttft_ms: 120000,
    };
    await route.fulfill({ response, json: body });
  });
  let runId: string | undefined;
  let cancels = 0;
  page.on("request", (r) => {
    if (r.method() === "POST" && /\/api\/runs\/[^/]+\/cancel$/.test(r.url()))
      cancels++;
  });
  try {
    await page.goto(`/c/${chat.id}`);
    await page
      .locator(".composer textarea")
      .fill("#think #long:100 #slow:1 #stall:120 Synthetic cancellation");
    const accepted = page.waitForResponse(
      (r) =>
        r.request().method() === "POST" &&
        r.url().endsWith(`/api/chats/${chat.id}/messages`),
    );
    await page
      .getByRole("button", { name: "Send message", exact: true })
      .click();
    runId = (await (await accepted).json()).run_id;
    await expect
      .poll(() =>
        page.evaluate(() =>
          Boolean(
            (window as unknown as { qaRunEvents?: EventTarget }).qaRunEvents,
          ),
        ),
      )
      .toBe(true);
    await page.evaluate(() => {
      (
        window as unknown as { qaRunEvents: EventTarget }
      ).qaRunEvents.dispatchEvent(
        new MessageEvent("reasoning.delta", {
          data: JSON.stringify({ text: "Synthetic ongoing reasoning." }),
        }),
      );
    });
    await expect(page.locator(".thought-ticker")).toBeVisible();
    await expect(page.getByTestId("long-thinking")).toHaveCount(0);
    await page.clock.fastForward(61000);
    const warning = page.getByTestId("long-thinking");
    await expect(warning).toBeVisible();
    const stopped = page.waitForResponse(
      (r) =>
        r.url().endsWith(`/runs/${runId}/cancel`) &&
        r.request().method() === "POST",
    );
    await warning
      .getByRole("button", { name: "Stop reply", exact: true })
      .click();
    expect((await stopped).ok()).toBe(true);
    expect(cancels).toBe(1);
  } finally {
    if (runId) await request.post(`/api/runs/${runId}/cancel`, { data: {} });
  }
});

test("switching to a non-thinking model leaves a visible way to clear an unsupported saved level", async ({
  page,
  request,
}) => {
  const connection = (await (await request.get("/api/connections")).json())[0];
  await request.patch("/api/settings", {
    data: { auto_title: false, "web.default_on": false },
  });
  const chat = await (
    await request.post("/api/chats", {
      data: {
        connection_id: connection.id,
        model_id: "fake-reasoning",
        web_enabled: false,
      },
    })
  ).json();
  await request.patch(`/api/chats/${chat.id}`, {
    data: { params: { reasoning: "on" } },
  });
  await request.patch(`/api/chats/${chat.id}`, {
    data: { model_id: "fake-chat" },
  });
  await page.goto(`/c/${chat.id}`);
  const field = page.locator(".composer textarea");
  await field.fill("Synthetic question after model switch");
  await page.getByRole("button", { name: "Send message", exact: true }).click();
  await expect(page.getByRole("alert")).toContainText("thinking level");
  await expect(field).toHaveValue("Synthetic question after model switch");
  await page.getByRole("button", { name: "Tools", exact: true }).click();
  const reset = page.getByRole("menuitemradio", {
    name: "Model default",
    exact: true,
  });
  await expect(reset).toBeVisible();
  await expect(page.getByRole("menuitemradio")).toHaveCount(1);
  await reset.click();
  await page.keyboard.press("Escape");
  await expect
    .poll(
      async () =>
        (await (await request.get(`/api/chats/${chat.id}`)).json()).chat.params
          .reasoning,
    )
    .toBeNull();
  await page.getByRole("button", { name: "Send message", exact: true }).click();
  await expect(
    page.getByText("Fake runtime reply.", { exact: false }),
  ).toBeVisible();
});
