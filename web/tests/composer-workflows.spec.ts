import { test, expect, type Page } from "@playwright/test";
import { mkdir } from "node:fs/promises";
import AxeBuilder from "@axe-core/playwright";
import { settle } from "./helpers";

async function chatModel(page: Page) {
  await page.getByRole("button", { name: "Choose model", exact: true }).click();
  await page.getByPlaceholder("Search models…").fill("fake-chat");
  await page
    .getByRole("option")
    .filter({ hasText: "fake-chat" })
    .first()
    .click();
  await expect(
    page.getByRole("textbox", { name: "Message fake-chat", exact: true }),
  ).toBeEnabled();
}

test("Composer image acceptance retry preserves seed/key, saving and unsent chat", async ({
  page,
}) => {
  await page.goto("/");
  await chatModel(page);
  const message = page.getByRole("textbox", {
    name: "Message fake-chat",
    exact: true,
  });
  await message.fill("Synthetic unsent chat draft");
  const bodies: Record<string, unknown>[] = [];
  let chatCalls = 0;
  page.on("request", (request) => {
    if (request.method() === "POST" && request.url().endsWith("/api/runs"))
      chatCalls++;
  });
  await page.route("**/api/images/jobs", async (route) => {
    if (route.request().method() !== "POST") return route.continue();
    bodies.push(route.request().postDataJSON());
    if (bodies.length === 1) {
      await route.fetch();
      await route.abort("failed");
    } else await route.continue();
  });
  await page.getByRole("button", { name: "Create image", exact: true }).click();
  await expect(message).not.toBeVisible();
  await expect(
    page.getByRole("textbox", { name: "Seed", exact: true }),
  ).not.toBeVisible();
  await page
    .getByRole("textbox", { name: "Prompt", exact: true })
    .fill("Synthetic composer circle");
  await page.getByRole("button", { name: "Generate one image" }).click();
  await expect(
    page
      .getByRole("status")
      .filter({ hasText: /Failed to fetch|Load failed|NetworkError/ }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Generate one image" }).click();
  await expect.poll(() => bodies.length).toBe(2);
  expect(bodies[1]).toEqual(bodies[0]);
  expect(Number.isInteger(bodies[0].seed)).toBe(true);
  expect(bodies[0].seed as number).toBeGreaterThanOrEqual(0);
  expect(bodies[0].seed as number).toBeLessThanOrEqual(4294967295);
  const job = page
    .getByRole("article")
    .filter({ hasText: "Synthetic composer circle" })
    .first();
  await expect(
    job.getByRole("button", { name: "Save", exact: true }),
  ).toBeVisible();
  await job.getByRole("button", { name: "Save", exact: true }).click();
  await expect(
    page.getByRole("dialog", { name: "Save image", exact: true }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Close image save", exact: true })
    .click();
  await page.getByRole("button", { name: "Message", exact: true }).click();
  await expect(message).toHaveValue("Synthetic unsent chat draft");
  await expect(message).toBeFocused();
  expect(chatCalls).toBe(0);
  await page
    .getByRole("navigation", { name: "Workspace", exact: true })
    .getByRole("link", { name: "Workflows", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Configure Draft image prompt" })
    .click();
  await expect(
    page.getByRole("combobox", { name: "Prompt draft model" }),
  ).toContainText("fake-chat");
  await page.getByRole("link", { name: "Chat", exact: true }).click();
  await expect(message).toHaveValue("Synthetic unsent chat draft");
});

test("Workflow count uses automatic seeds and repeats uncertain acceptance exactly", async ({
  page,
}) => {
  await page.goto("/workflows");
  await page
    .getByRole("textbox", { name: "Image brief" })
    .fill("Synthetic automatic variants");
  await page
    .getByRole("button", { name: "Configure Draft image prompt" })
    .click();
  await page.getByRole("combobox", { name: "Prompt draft model" }).click();
  await page
    .getByRole("option")
    .filter({ hasText: "fake-chat" })
    .first()
    .click();
  await page.getByRole("button", { name: "Configure Generate images" }).click();
  await expect(
    page.getByRole("textbox", { name: "Image variant seeds" }),
  ).not.toBeVisible();
  await page.getByRole("button", { name: "3", exact: true }).click();
  const bodies: {
    seeds: number[];
    request_key: string;
    model: { params: unknown };
  }[] = [];
  await page.route("**/api/workflows/runs", async (route) => {
    bodies.push(route.request().postDataJSON());
    if (bodies.length === 1) {
      await route.fetch();
      await route.abort("failed");
    } else await route.continue();
  });
  await page
    .getByRole("button", { name: "Start workflow", exact: true })
    .click();
  await expect(
    page
      .getByRole("status")
      .filter({ hasText: /Failed to fetch|Load failed|NetworkError/ }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Start workflow", exact: true })
    .click();
  await expect.poll(() => bodies.length).toBe(2);
  expect(bodies[1]).toEqual(bodies[0]);
  expect(bodies[0].seeds).toHaveLength(3);
  expect(bodies[0].model.params).toEqual({});
  await expect(
    page
      .getByRole("article", { name: "Brief to images run" })
      .first()
      .getByRole("textbox", { name: "Review image prompt" }),
  ).toBeVisible();
});

test("Image cancellation stays in composer and Workflows returns to the same saved chat", async ({
  page,
  request,
  browserName,
}) => {
  const connection = (await (await request.get("/api/connections")).json())[0];
  const response = await request.post("/api/chats", {
    data: { connection_id: connection.id, model_id: "fake-chat" },
  });
  const chat = await response.json();
  await page.goto(`/c/${chat.id}`);
  const message = page.getByRole("textbox", {
    name: "Message fake-chat",
    exact: true,
  });
  await message.fill("Synthetic saved-chat draft");
  await page.getByRole("button", { name: "Create image", exact: true }).click();
  await page
    .getByRole("textbox", { name: "Prompt", exact: true })
    .fill("Synthetic cancellable composer #slow");
  await page.getByRole("button", { name: "Generate one image" }).click();
  const job = page
    .getByRole("article")
    .filter({ hasText: "Synthetic cancellable composer #slow" })
    .first();
  await job.getByRole("button", { name: "Cancel", exact: true }).click();
  await expect(
    job.getByText("cancelled", { exact: true }).first(),
  ).toBeVisible();
  await settle(page);
  const dir = "../artifacts/composer-workflows/browser/composer";
  await mkdir(dir, { recursive: true });
  await page.screenshot({
    path: `${dir}/cancel-${browserName}-fake.png`,
    fullPage: true,
  });
  await page.getByRole("button", { name: "Message", exact: true }).click();
  await page
    .getByRole("navigation", { name: "Workspace", exact: true })
    .getByRole("link", { name: "Workflows", exact: true })
    .click();
  await expect(
    page.getByRole("link", { name: "Chat", exact: true }),
  ).toHaveAttribute("href", `/c/${chat.id}`);
  await page.getByRole("link", { name: "Chat", exact: true }).click();
  await expect(message).toHaveValue("Synthetic saved-chat draft");
});

test("Visual builder reflows and every node opens its settings with keyboard", async ({
  page,
  browserName,
}) => {
  const dir = "../artifacts/composer-workflows/browser/builder";
  await mkdir(dir, { recursive: true });
  for (const width of [320, 390, 1440]) {
    await page.setViewportSize({ width, height: 900 });
    await page.goto("/design?workflows");
    for (const theme of ["light", "dark"]) {
      await page.getByRole("button", { name: theme, exact: true }).click();
      await page
        .getByRole("button", {
          name: "Configure Draft image prompt",
          exact: true,
        })
        .focus();
      await page.keyboard.press("Enter");
      await expect(
        page.getByRole("combobox", { name: "Prompt draft model" }),
      ).toBeVisible();
      await expect(
        page.getByRole("button", {
          name: "Configure Draft image prompt",
          exact: true,
        }),
      ).toHaveAttribute("aria-pressed", "true");
      await settle(page);
      expect(
        await page.evaluate(
          () => document.documentElement.scrollWidth <= innerWidth,
        ),
      ).toBe(true);
      const scan = await new AxeBuilder({ page }).analyze();
      expect(
        scan.violations.filter((v) =>
          ["critical", "serious"].includes(v.impact ?? ""),
        ),
      ).toEqual([]);
      await page.screenshot({
        path: `${dir}/model-${width}-${theme}-${browserName}-fake.png`,
        fullPage: true,
      });
      await page
        .getByRole("button", { name: "Configure Generate images", exact: true })
        .click();
      await expect(
        page.getByText("Choose how many images to compare.", { exact: true }),
      ).toBeVisible();
      await page
        .getByRole("button", { name: "Configure Review prompt", exact: true })
        .click();
      await expect(
        page.getByRole("checkbox", {
          name: "Pause to review the prompt before generating",
        }),
      ).toBeVisible();
      await page
        .getByRole("button", { name: "Configure Start", exact: true })
        .click();
      await expect(
        page.getByRole("textbox", { name: "Image brief" }),
      ).toBeVisible();
    }
  }
});
