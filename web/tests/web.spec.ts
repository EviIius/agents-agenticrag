import { settle } from "./helpers";
import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { mkdir } from "node:fs/promises";
for (const width of [390, 1440])
  for (const theme of ["light", "dark"])
    test(`web citations ${width} ${theme}`, async ({ page, request }) => {
      await request.patch("/api/settings", {
        data: { "appearance.theme": theme },
      });
      await page.setViewportSize({ width, height: width < 640 ? 844 : 900 });
      await page.addInitScript(
        (value) => localStorage.setItem("workbench-theme", value),
        theme,
      );
      await page.goto("/");
      await expect(
        page.getByRole("button", { name: "Web search", exact: true }),
      ).toBeVisible();
      await page
        .getByRole("button", { name: "Web search", exact: true })
        .click();
      await page
        .locator(".composer textarea")
        .fill("Who lost the 2021 NBA Finals? Show a table.");
      await page.getByRole("button", { name: "Send message" }).click();
      await expect(
        page.getByText("Synthetic web answer", { exact: false }),
      ).toBeVisible();
      await mkdir("../artifacts/phase-2", { recursive: true });
      await settle(page);
      await page.screenshot({
        path: `../artifacts/phase-2/web-chat-${width}-${theme}-fake-web.png`,
      });
      const pill = page
        .getByRole("button", { name: /View source: Synthetic NBA Finals/ })
        .first();
      await expect(pill).toBeVisible();
      expect((await pill.boundingBox())!.height).toBeLessThanOrEqual(20);
      await pill.click();
      await expect(
        page.getByText("Open page ↗", { exact: true }).first(),
      ).toBeVisible();
      await expect(
        page.getByRole("dialog", { name: "Citation sources" }),
      ).toBeInViewport({ ratio: 1 });
      await settle(page);
      await page.screenshot({
        path: `../artifacts/phase-2/citation-card-${width}-${theme}-fake-web.png`,
      });
      await settle(page);
      const cardAudit = await new AxeBuilder({ page }).analyze();
      expect(
        cardAudit.violations.filter((v) =>
          ["critical", "serious"].includes(v.impact ?? ""),
        ),
      ).toEqual([]);
      await page
        .getByRole("button", { name: "Close citation", exact: true })
        .click();
      await expect(
        page.getByRole("dialog", { name: "Citation sources" }),
      ).toHaveCount(0);
      await page
        .getByRole("button", { name: "2 sources", exact: true })
        .click();
      const dialog = page.getByRole("dialog").last();
      await expect(
        dialog.getByText("via DuckDuckGo", { exact: true }),
      ).toBeVisible();
      await dialog
        .getByText("What the model saw", { exact: true })
        .first()
        .click();
      await expect(
        dialog.getByText(/synthetic fixture says/, { exact: false }).first(),
      ).toBeVisible();
      expect(
        await page.evaluate(
          () => document.documentElement.scrollWidth <= innerWidth,
        ),
      ).toBeTruthy();
      await settle(page);
      const a11y = await new AxeBuilder({ page }).analyze();
      expect(
        a11y.violations.filter((v) =>
          ["critical", "serious"].includes(v.impact ?? ""),
        ),
      ).toEqual([]);
      await mkdir("../artifacts/phase-2", { recursive: true });
      await settle(page);
      await page.screenshot({
        path: `../artifacts/phase-2/sources-${width}-${theme}-fake-web.png`,
      });
      await page.keyboard.press("Escape");
      await page.reload();
      await expect(pill).toBeVisible();
      const before = await (
        await page.request.get("http://127.0.0.1:18080/tests/state")
      ).json();
      await page.locator(".composer textarea").fill("thanks!");
      await page.getByRole("button", { name: "Send message" }).click();
      await expect(
        page.getByText("No web search needed", { exact: false }),
      ).toBeVisible();
      const after = await (
        await page.request.get("http://127.0.0.1:18080/tests/state")
      ).json();
      expect(after.captures.length).toBeGreaterThan(before.captures.length);
      await page
        .getByRole("button", { name: "Search anyway", exact: true })
        .click();
      await expect(
        page.getByText("Synthetic web answer", { exact: false }).last(),
      ).toBeVisible();
    });

test("search activity appears within 300ms and collapses after completion", async ({
  page,
  request,
}) => {
  const connection = (await (await request.get("/api/connections")).json())[0];
  await request.patch("/api/settings", {
    data: {
      default_connection_id: connection.id,
      default_model_id: "fake-chat",
      auto_title: false,
    },
  });
  await page.goto("/");
  await page.getByRole("button", { name: "Web search", exact: true }).click();
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
  await page.getByRole("button", { name: "Send message" }).click();
  const elapsed = await page.evaluate(
    () => (window as unknown as { activityMs: Promise<number> }).activityMs,
  );
  expect(elapsed).toBeLessThanOrEqual(300);
  const activity = page.getByTestId("search-activity");
  await expect(
    activity.locator('[data-slot="collapsible-trigger"]'),
  ).toContainText("Searched the web");
  await expect(
    activity.locator('[data-slot="collapsible-trigger"]'),
  ).toHaveAttribute("data-state", "closed");
  await expect(activity.locator('[data-domain="example.org"]')).toBeVisible();
  await mkdir("../artifacts/phase-2", { recursive: true });
  await import("node:fs/promises").then(({ writeFile }) =>
    writeFile(
      `../artifacts/phase-2/activity-latency-${test.info().project.name}.json`,
      JSON.stringify(
        { runtime: "fake", elapsed_ms: elapsed, target_ms: 300 },
        null,
        2,
      ),
    ),
  );
});

test("a late streaming chat snapshot cannot erase the completed SSE answer", async ({
  page,
  request,
}) => {
  const connection = (await (await request.get("/api/connections")).json())[0];
  await request.patch("/api/settings", {
    data: {
      default_connection_id: connection.id,
      default_model_id: "fake-chat",
      auto_title: false,
    },
  });
  await page.goto("/");
  await page.getByRole("button", { name: "Web search", exact: true }).click();
  let intercepted = false;
  let release!: () => void;
  const hold = new Promise<void>((resolve) => {
    release = resolve;
  });
  await page.route(/\/api\/chats\/[a-f0-9]+$/, async (route) => {
    if (route.request().method() !== "GET" || intercepted)
      return route.continue();
    const response = await route.fetch();
    const detail = await response.json();
    const assistant = detail.messages.find(
      (message: { role: string }) => message.role === "assistant",
    );
    if (!assistant) return route.fulfill({ response });
    intercepted = true;
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
  await page.getByRole("button", { name: "Send message" }).click();
  await expect(
    page.getByText("Synthetic web answer", { exact: false }),
  ).toBeVisible();
  expect(intercepted).toBeTruthy();
  release();
  await expect(
    page.getByRole("button", { name: "Stop generating" }),
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
});
