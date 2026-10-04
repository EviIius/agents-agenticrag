import { test, expect } from "@playwright/test";
import { mkdir, writeFile } from "node:fs/promises";

test.use({ hasTouch: true, viewport: { width: 390, height: 844 } });

test.beforeAll(async ({ request }) => {
  const connections = await (await request.get("/api/connections")).json();
  expect(
    connections.every(
      (c: { name: string; base_url: string }) =>
        c.name === "Fake runtime" && c.base_url === "http://127.0.0.1:18080",
    ),
  ).toBe(true);
  // Full-suite history exposed a route handoff race hidden by empty-db reruns.
  for (let i = 0; i < 45; i++) {
    const chat = await (
      await request.post("/api/chats", {
        data: {
          connection_id: connections[0].id,
          model_id: "fake-chat",
          web_enabled: false,
        },
      })
    ).json();
    expect(
      (
        await request.post(`http://127.0.0.1:8787/tests/long-chat/${chat.id}`)
      ).ok(),
    ).toBe(true);
    await request.patch(`/api/chats/${chat.id}`, {
      data: { title: `Synthetic handoff history ${i}` },
    });
  }
});

test.beforeEach(async ({ request }) => {
  const connections = await (await request.get("/api/connections")).json();
  await request.patch("/api/settings", {
    data: {
      default_connection_id: connections[0].id,
      default_model_id: "fake-chat",
      auto_title: false,
      "web.default_on": false,
    },
  });
});

test("cold new-chat handoff preserves a completed SSE answer before and after a late fetch", async ({
  page,
}) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Search off", exact: true }).click();
  let captured = false;
  let release!: () => void;
  const hold = new Promise<void>((resolve) => {
    release = resolve;
  });
  await page.route(/\/api\/chats\/[a-f0-9]+$/, async (route) => {
    if (route.request().method() !== "GET" || captured) return route.continue();
    const response = await route.fetch();
    const detail = await response.json();
    const assistant = detail.messages.find(
      (m: { role: string }) => m.role === "assistant",
    );
    if (!assistant) return route.fulfill({ response });
    captured = true;
    assistant.status = "streaming";
    assistant.content = "";
    assistant.web = null;
    detail.sources = {};
    await hold;
    await route.fulfill({ response, json: detail });
  });
  await page
    .locator(".composer textarea")
    .fill("Who lost the 2021 NBA Finals? Show a table.");
  await page.evaluate(() => {
    const state = window as unknown as { activityMs: Promise<number> };
    state.activityMs = new Promise((resolve) => {
      document
        .querySelector('button[aria-label="Send message"]')!
        .addEventListener(
          "click",
          () => {
            const started = performance.now();
            const observer = new MutationObserver(() => {
              if (document.querySelector('[data-testid="search-activity"]')) {
                observer.disconnect();
                resolve(performance.now() - started);
              }
            });
            observer.observe(document.body, { childList: true, subtree: true });
          },
          { once: true },
        );
    });
  });
  await page.getByRole("button", { name: "Send message", exact: true }).click();
  await expect(
    page.getByText("Synthetic web answer", { exact: false }),
  ).toBeVisible();
  expect(captured).toBe(true);
  const elapsed = await page.evaluate(
    () => (window as unknown as { activityMs: Promise<number> }).activityMs,
  );
  expect(elapsed).toBeLessThanOrEqual(300);
  release();
  await expect(
    page.getByRole("button", { name: "Stop generating", exact: true }),
  ).toHaveCount(0);
  await expect(
    page.getByText("Synthetic web answer", { exact: false }),
  ).toBeVisible();
  await expect(
    page
      .getByRole("button", { name: /View source: Synthetic NBA Finals/ })
      .first(),
  ).toBeVisible();
  await page.reload();
  await expect(
    page.getByText("Synthetic web answer", { exact: false }),
  ).toBeVisible();
  await mkdir("../artifacts/phase-4/4c", { recursive: true });
  await writeFile(
    `../artifacts/phase-4/4c/cold-handoff-${test.info().project.name}-fake.json`,
    JSON.stringify(
      {
        history_chats: 45,
        activity_ms: elapsed,
        limit_ms: 300,
        completed_answer_preserved: true,
      },
      null,
      2,
    ),
  );
});

test("cold phone send finishes mounting before the next touch draft", async ({
  page,
}) => {
  await page.goto("/");
  const composer = page.locator(".composer textarea");
  await expect(
    page.getByRole("button", { name: "Choose model", exact: true }),
  ).toContainText("fake-chat");
  await composer.tap();
  await page.keyboard.type("Synthetic mobile handoff request");
  await page.getByRole("button", { name: "Send message", exact: true }).tap();
  await expect(page).toHaveURL(/\/c\/[^/]+$/);
  await expect(
    page.getByRole("button", { name: "Stop generating", exact: true }),
  ).toHaveCount(0);
  await composer.tap();
  await expect(composer).toBeFocused();
  await page.keyboard.type("Synthetic next draft");
  await expect(composer).toHaveValue("Synthetic next draft");
  await expect(
    page.getByText("Fake runtime reply.", { exact: false }),
  ).toBeVisible();
  await expect(composer).toHaveValue("Synthetic next draft");
});
