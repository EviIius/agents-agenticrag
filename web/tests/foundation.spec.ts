import { settle } from "./helpers";
import { test, expect, type Page } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { mkdir } from "node:fs/promises";
import path from "node:path";
const evidence = path.resolve("../artifacts/phase-0");
async function setTheme(page: Page, theme: "light" | "dark") {
  await page.addInitScript(
    (value) => localStorage.setItem("workbench-theme", value),
    theme,
  );
}
async function noOverflow(page: Page) {
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
}
for (const theme of ["light", "dark"] as const) {
  for (const width of [390, 1440]) {
    test(`loads ${width} ${theme}, composer separate from thread`, async ({
      page,
    }) => {
      await page.setViewportSize({ width, height: width === 390 ? 844 : 900 });
      await setTheme(page, theme);
      const errors: string[] = [];
      page.on("pageerror", (error) => errors.push(error.message));
      page.on("console", (message) => {
        if (message.type() === "error") errors.push(message.text());
      });
      await page.goto("/design/chat/fixture");
      await expect(
        page.getByText("Start with a clear question", { exact: true }),
      ).toBeVisible();
      await noOverflow(page);
      expect(errors).toEqual([]);
      await expect(page.locator("html")).toHaveAttribute("data-theme", theme);
      const thread = await page.getByTestId("thread").boundingBox();
      const composer = await page.getByTestId("composer-row").boundingBox();
      expect(
        thread && composer && thread.y + thread.height <= composer.y + 1,
      ).toBe(true);
      await page
        .getByRole("button", { name: "Choose model", exact: true })
        .click();
      await expect(page.getByPlaceholder("Search models…")).toBeVisible();
      await page.getByPlaceholder("Search models…").fill("vision");
      await page.getByRole("option", { name: /fake-vision/ }).click();
      await expect(
        page.getByRole("button", { name: "Choose model", exact: true }),
      ).toContainText("fake-vision");
      await page.getByLabel("Chat controls", { exact: true }).click();
      await expect(
        page
          .getByRole("heading", { name: "Chat controls", exact: true })
          .last(),
      ).toBeVisible();
      await noOverflow(page);
      await page.getByLabel("Close chat controls").click();
      await expect(page.getByLabel("Message fake-chat")).toBeVisible();
    });
  }
  test(`design accessibility ${theme}`, async ({ page }) => {
    await setTheme(page, theme);
    await page.goto("/design");
    await expect(
      page.getByText("Start with a clear question", { exact: true }),
    ).toBeVisible();
    await noOverflow(page);
    await settle(page);
    const result = await new AxeBuilder({ page }).analyze();
    expect(
      result.violations.filter((item) =>
        ["serious", "critical"].includes(item.impact ?? ""),
      ),
      JSON.stringify(result.violations, null, 2),
    ).toEqual([]);
  });
  test(`settings keyboard and theme ${theme}`, async ({ page }) => {
    await setTheme(page, theme);
    await page.goto("/design/chat/fixture");
    await page.keyboard.press("Control+,");
    await expect(
      page.getByRole("dialog", { name: "Settings", exact: true }),
    ).toBeVisible();
    await page
      .getByRole("button", {
        name: theme === "light" ? "Dark" : "Light",
        exact: true,
      })
      .click();
    await expect(page.locator("html")).toHaveAttribute(
      "data-theme",
      theme === "light" ? "dark" : "light",
    );
    await page.keyboard.press("Escape");
    await expect(
      page.getByRole("dialog", { name: "Settings", exact: true }),
    ).not.toBeVisible();
  });
}
test("320px reflow and mobile navigation", async ({ page }) => {
  await page.setViewportSize({ width: 320, height: 740 });
  await page.goto("/design/chat/fixture");
  await noOverflow(page);
  await page.getByLabel("Open sidebar", { exact: true }).click();
  await expect(
    page.getByRole("dialog", { name: "Chat history" }),
  ).toBeVisible();
  await page
    .getByRole("dialog", { name: "Chat history" })
    .getByRole("button", { name: "Settings", exact: true })
    .click();
  await expect(
    page.getByRole("dialog", { name: "Settings", exact: true }),
  ).toBeVisible();
  await noOverflow(page);
});
test("new chat and editable fixture", async ({ page }) => {
  await page.goto("/design/chat");
  await expect(page.getByRole("heading", { name: /Good/ })).toBeVisible();
  await page.getByRole("button", { name: "Explain", exact: true }).click();
  await expect(page.getByLabel("Message fake-chat")).toHaveValue("Explain ");
  await page.getByLabel("Message fake-chat").fill("Explain a simple process.");
  await page.getByLabel("Send message", { exact: true }).click();
  await expect(page).toHaveURL(/\/design\/chat\/fixture/);
  await expect(
    page.getByText("Explain a simple process.", { exact: true }),
  ).toBeVisible();
});
test("fake runtime is explicitly named and serves both protocols", async ({
  request,
}) => {
  const models = await request.get("http://127.0.0.1:18080/v1/models");
  expect(
    (await models.json()).data.every((model: { id: string }) =>
      model.id.startsWith("fake-"),
    ),
  ).toBe(true);
  const response = await request.post("http://127.0.0.1:18080/api/chat", {
    data: {
      model: "fake-chat",
      messages: [{ role: "user", content: "#length" }],
      stream: true,
    },
  });
  expect(response.ok()).toBe(true);
  expect(await response.text()).toContain('"done_reason": "length"');
});
test("screenshots at all review sizes and themes (fake runtime)", async ({
  page,
}, testInfo) => {
  test.skip(
    testInfo.project.name !== "chromium",
    "Capture the review set once; WebKit runs the interaction checks.",
  );
  await mkdir(evidence, { recursive: true });
  for (const theme of ["light", "dark"] as const) {
    for (const [width, height] of [
      [390, 844],
      [768, 1024],
      [1440, 900],
    ]) {
      await page.setViewportSize({ width, height });
      for (const [route, name] of [
        ["/design", "design"],
        ["/design/chat/fixture", "chat"],
      ]) {
        await page.goto(route);
        await page.evaluate((value) => {
          localStorage.setItem("workbench-theme", value);
        }, theme);
        await page.reload();
        await expect(
          page.getByText("Start with a clear question", { exact: true }),
        ).toBeVisible();
        await noOverflow(page);
        await settle(page);
        await page.screenshot({
          path: path.join(
            evidence,
            `${name}-${width}-${theme}-fake-runtime.png`,
          ),
          fullPage: false,
          animations: "disabled",
        });
      }
    }
  }
});

test("untrusted Markdown does not create HTML or load remote images", async ({
  page,
}) => {
  const remoteRequests: string[] = [];
  page.on("request", (request) => {
    if (request.url().includes("example.invalid"))
      remoteRequests.push(request.url());
  });
  await page.goto("/design");
  await expect(
    page.getByRole("heading", { name: "Markdown safety" }),
  ).toBeAttached();
  await expect(
    page.getByRole("link", { name: "Remote example" }),
  ).toHaveAttribute("href", "https://example.invalid/picture.jpg");
  expect(await page.locator("[data-untrusted]").count()).toBe(0);
  expect(await page.locator('a[href^="javascript:"]').count()).toBe(0);
  expect(remoteRequests).toEqual([]);
});

test("keyboard-only fixture walkthrough", async ({ page }, testInfo) => {
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  async function tabTo(label: string) {
    for (let attempt = 0; attempt < 40; attempt++) {
      if (
        (await page.evaluate(() =>
          document.activeElement?.getAttribute("aria-label"),
        )) === label
      )
        return;
      await page.keyboard.press(
        testInfo.project.name === "webkit" ? "Alt+Tab" : "Tab",
      );
    }
    throw new Error(`Could not reach ${label} with the keyboard.`);
  }
  await page.goto("/design/chat");
  await tabTo("Message fake-chat");
  await page.keyboard.type("Explain a small experiment.");
  await page.keyboard.press("Control+Enter");
  await expect(
    page.getByText("Explain a small experiment.", { exact: true }),
  ).toBeVisible();
  await expect(page.getByLabel("Message fake-chat")).toBeFocused();
  await tabTo("Choose model");
  await page.keyboard.press("Enter");
  await expect(page.getByPlaceholder("Search models…")).toBeVisible();
  await tabTo("Search models");
  await page.keyboard.type("reasoning");
  await page.keyboard.press("ArrowDown");
  await page.keyboard.press("Enter");
  await expect(
    page.getByRole("button", { name: "Choose model", exact: true }),
  ).toContainText("fake-reasoning");
  await page.keyboard.press("Control+k");
  await page.keyboard.type("weekend");
  await page.keyboard.press("ArrowDown");
  await page.keyboard.press("Enter");
  await expect(
    page.getByRole("dialog", { name: "Search chats" }),
  ).not.toBeVisible();
  await page.keyboard.press("Control+,");
  await expect(page.getByRole("dialog", { name: "Settings" })).toBeVisible();
  await page.keyboard.press("Escape");
  await page.keyboard.press("Control+Shift+O");
  await expect(page.getByRole("heading", { name: /Good/ })).toBeVisible();
  expect(errors).toEqual([]);
});
