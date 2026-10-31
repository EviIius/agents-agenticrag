import { expect, test, type Page } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { mkdir, writeFile } from "node:fs/promises";
import type { Chat } from "../src/lib/api";
import { fakeAppURL } from "../test-runtime";
import { settle } from "./helpers";

const generationCalls = (bodies: Record<string, unknown>[]) =>
  bodies.filter((body) => Object.keys(body).some((key) => key !== "model"));
const dir = "../artifacts/assistant-as0-20261030/browser";
const states = [
  "queued",
  "running",
  "awaiting_approval",
  "needs_input",
  "complete",
  "cancelled",
  "failed",
  "interrupted",
  "outcome_unknown",
];

for (const width of [390, 1440])
  for (const theme of ["light", "dark"] as const) {
    test(`AS0 all fake review states ${width} ${theme}`, async ({
      page,
      browserName,
    }) => {
      await page.setViewportSize({ width, height: 900 });
      await page.addInitScript(
        (value) => localStorage.setItem("workbench-theme", value),
        theme,
      );
      await page.goto("/design?assistant");
      await expect(
        page.getByRole("heading", { name: "Computer use · Fake desktop" }),
      ).toBeVisible();
      await mkdir(dir, { recursive: true });
      const results = [];
      for (const state of states) {
        await page
          .getByRole("button", {
            name: state.replaceAll("_", " "),
            exact: true,
          })
          .click();
        await settle(page);
        expect(
          await page.evaluate(
            () => document.documentElement.scrollWidth <= innerWidth,
          ),
        ).toBeTruthy();
        const scan = await new AxeBuilder({ page }).analyze();
        const serious = scan.violations.filter((v) =>
          ["serious", "critical"].includes(v.impact ?? ""),
        );
        expect(serious, state).toEqual([]);
        results.push({ state, seriousCritical: serious.length });
        await page.screenshot({
          path: `${dir}/${state}-${width}-${theme}-${browserName}-fake.png`,
          fullPage: true,
        });
      }
      await page
        .getByRole("button", { name: "awaiting approval", exact: true })
        .click();
      await page.getByRole("button", { name: "Edit", exact: true }).click();
      await page
        .getByRole("textbox", { name: "Proposed reply", exact: true })
        .fill("Edited in the preview.");
      await page
        .getByRole("button", { name: "Send (fake)", exact: true })
        .click();
      await expect(
        page.getByText("Fake submitted text: Edited in the preview.", {
          exact: true,
        }),
      ).toBeVisible();
      await writeFile(
        `${dir}/axe-${width}-${theme}-${browserName}.json`,
        JSON.stringify(results, null, 2),
      );
    });
  }

async function enter(page: Page) {
  await page.goto("/");
  await page.getByRole("button", { name: "Tools", exact: true }).click();
  await page.getByRole("menuitem", { name: /Use computer/ }).click();
  await expect(
    page.getByRole("heading", { name: "Computer use", exact: true }),
  ).toBeVisible();
}
async function requestTask(page: Page, text: string) {
  await page
    .getByRole("textbox", { name: "Message Fake desktop", exact: true })
    .fill(text);
  await page.getByRole("button", { name: "Send message", exact: true }).click();
  const card = page
    .getByRole("article", { name: "Computer task", exact: true })
    .filter({ hasText: text });
  await expect(
    card.getByRole("button", { name: /^(Send|Apply) \(fake\)$/ }),
  ).toBeVisible();
  return card;
}

test.describe("AS0 actual fake controller in chat", () => {
  let createdChats: Promise<Chat>[] = [];
  test.beforeEach(async ({ request, page }) => {
    createdChats = [];
    page.on("response", (response) => {
      if (
        response.request().method() === "POST" &&
        new URL(response.url()).pathname === "/api/chats" &&
        response.ok()
      ) {
        createdChats.push(response.json() as Promise<Chat>);
      }
    });
    await request.post(fakeAppURL + "/tests/assistant/setup");
  });
  test.afterEach(async ({ request }) => {
    await request.post(fakeAppURL + "/tests/assistant/setup?enabled=false");
    for (const chat of await Promise.all(createdChats)) {
      await request.delete(`/api/chats/${chat.id}`);
    }
  });

  test("same chat controller edits Messages then Notes, survives reload, calls no model", async ({
    page,
    request,
  }) => {
    const before = (
      await (await request.get("http://127.0.0.1:18080/tests/state")).json()
    ).captures;
    await enter(page);
    const card = await requestTask(page, "Prepare a synthetic reply to Alex.");
    await expect(card).toContainText("alex@example.invalid");
    await expect(card).toContainText("Can we meet at 3 pm?");
    await card.getByRole("button", { name: "Edit", exact: true }).click();
    await card
      .getByRole("textbox", { name: "Proposed reply", exact: true })
      .fill("Four o'clock works for me.");
    await card
      .getByRole("button", { name: "Send (fake)", exact: true })
      .click();
    await expect(card.getByRole("status")).toHaveText("Fake action complete");
    await expect(
      card.getByRole("region", { name: "Approved action" }),
    ).toContainText("Four o'clock works for me.");
    const url = page.url();
    await page.reload();
    await page.getByRole("button", { name: "Tools", exact: true }).click();
    await page.getByRole("menuitem", { name: /Use computer/ }).click();
    await expect(
      page.getByRole("article", { name: "Computer task", exact: true }),
    ).toContainText("Four o'clock works for me.");
    await page.getByRole("button", { name: "Notes demo", exact: true }).click();
    const note = await requestTask(page, "Write a synthetic note.");
    await note
      .getByRole("button", { name: "Apply (fake)", exact: true })
      .click();
    await expect(note.getByRole("status")).toHaveText("Fake action complete");
    expect(page.url()).toBe(url);
    const stats = await (
      await request.post(fakeAppURL + "/tests/assistant/state")
    ).json();
    expect(stats.executed).toBe(2);
    expect(stats.texts).toEqual([
      "Four o'clock works for me.",
      "A synthetic note from Aether.",
    ]);
    expect(
      generationCalls(
        (await (await request.get("http://127.0.0.1:18080/tests/state")).json())
          .captures,
      ),
    ).toEqual(generationCalls(before));
    const chatId = new URL(url).pathname.split("/").pop();
    const history = (await (await request.get("/api/chats")).json()).items;
    expect(history.some((chat: Chat) => chat.id === chatId)).toBe(true);
    expect(
      (await (await request.get(`/api/chats/${chatId}`)).json()).messages,
    ).toEqual([]);
  });

  for (const change of ["incoming", "revoke"])
    test(`changed ${change} blocks an approved action`, async ({
      page,
      request,
    }) => {
      await enter(page);
      const card = await requestTask(page, "Review a synthetic reply.");
      await request.post(
        fakeAppURL + "/tests/assistant/change?change=" + change,
      );
      await card
        .getByRole("button", { name: "Send (fake)", exact: true })
        .click();
      await expect(card.getByRole("status")).toContainText(
        change === "incoming" ? "changed" : "revoked",
      );
      await expect(
        card.getByRole("button", { name: "Send (fake)", exact: true }),
      ).toHaveCount(0);
      expect(
        (
          await (
            await request.post(fakeAppURL + "/tests/assistant/state")
          ).json()
        ).executed,
      ).toBe(0);
    });

  test("cancel while awaiting approval never sends; a stopped dispatch is visibly unconfirmed", async ({
    page,
    request,
  }) => {
    await enter(page);
    const first = await requestTask(page, "Do not send this synthetic draft.");
    await first.getByRole("button", { name: "Cancel", exact: true }).click();
    await expect(first.getByRole("status")).toHaveText("Stopped");
    await request.post(fakeAppURL + "/tests/assistant/change?change=hold");
    const second = await requestTask(page, "Stop this synthetic action.");
    await second
      .getByRole("button", { name: "Send (fake)", exact: true })
      .click();
    await expect(second.getByRole("status")).toHaveText(
      "Performing the fake action",
    );
    await second
      .getByRole("button", { name: "Stop task", exact: true })
      .click();
    await expect(second.getByRole("status")).toContainText("Check the app");
    const stats = await (
      await request.post(fakeAppURL + "/tests/assistant/state")
    ).json();
    expect(stats.executed).toBe(0);
    expect(stats.reaped).toBe(true);
  });

  test("a restart invalidates review instead of replaying it", async ({
    page,
    request,
  }) => {
    await enter(page);
    const card = await requestTask(page, "A synthetic task across restart.");
    await request.post(fakeAppURL + "/tests/restart-lifecycle");
    await page.reload();
    await page.getByRole("button", { name: "Tools", exact: true }).click();
    await page.getByRole("menuitem", { name: /Use computer/ }).click();
    await expect(card.getByRole("status")).toContainText("Interrupted");
    await expect(
      card.getByRole("button", { name: "Send (fake)", exact: true }),
    ).toHaveCount(0);
    expect(
      (await (await request.post(fakeAppURL + "/tests/assistant/state")).json())
        .executed,
    ).toBe(0);
  });
});

test("AS0 disabled by default has no chat entry and refuses task APIs", async ({
  page,
  request,
}) => {
  await request.post(fakeAppURL + "/tests/assistant/setup?enabled=false");
  await page.goto("/");
  await page.getByRole("button", { name: "Tools", exact: true }).click();
  await expect(
    page.getByRole("menuitem", { name: /Use computer/ }),
  ).toHaveCount(0);
  expect(
    (await request.get("/api/chats/synthetic/assistant-tasks")).status(),
  ).toBe(403);
  expect(
    (await (await request.get("/api/bootstrap")).json()).features.assistant,
  ).toBeUndefined();
});
