import { test, expect, type Page } from "@playwright/test";
import { mkdir } from "node:fs/promises";
import AxeBuilder from "@axe-core/playwright";
import {
  configureStudioBlock,
  chooseStudioModel,
  openStudioRun,
} from "./studio-helpers";
import { settle } from "./helpers";
import { workspaceLink } from "./workspace-helpers";

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
    if (
      request.method() === "POST" &&
      (new URL(request.url()).pathname.endsWith("/api/chats") ||
        /\/api\/chats\/[^/]+\/messages$/.test(new URL(request.url()).pathname))
    )
      chatCalls++;
  });
  await page.route("**/api/chats/*/images", async (route) => {
    if (route.request().method() !== "POST") return route.continue();
    bodies.push(route.request().postDataJSON());
    if (bodies.length === 1) {
      await route.fetch();
      await route.abort("failed");
    } else await route.continue();
  });
  const createImage = page.getByRole("button", {
    name: "Create image",
    exact: true,
  });
  const target = await createImage.boundingBox();
  expect(target?.width).toBeGreaterThanOrEqual(44);
  expect(target?.height).toBeGreaterThanOrEqual(44);
  await createImage.click();
  await expect(message).not.toBeVisible();
  await expect(
    page.getByRole("textbox", { name: "Seed", exact: true }),
  ).not.toBeVisible();
  await page
    .getByRole("textbox", { name: "Image prompt", exact: true })
    .fill("Synthetic composer circle");
  await page.getByRole("button", { name: "Create image", exact: true }).click();
  await expect(
    page
      .getByRole("alert")
      .filter({ hasText: /Failed to fetch|Load failed|NetworkError/ }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Create image", exact: true }).click();
  await expect.poll(() => bodies.length).toBe(2);
  expect(bodies[1]).toEqual(bodies[0]);
  expect(Number.isInteger((bodies[0].seeds as number[])[0])).toBe(true);
  expect((bodies[0].seeds as number[])[0]).toBeGreaterThanOrEqual(0);
  expect((bodies[0].seeds as number[])[0]).toBeLessThanOrEqual(4294967295);
  const job = page
    .getByRole("article")
    .filter({ hasText: "Synthetic composer circle" })
    .first();
  await expect(
    job.getByRole("button", { name: "Save image", exact: true }),
  ).toBeVisible();
  const scan = await new AxeBuilder({ page }).analyze();
  expect(
    scan.violations.filter((v) =>
      ["critical", "serious"].includes(v.impact ?? ""),
    ),
  ).toEqual([]);
  await job.getByRole("button", { name: "Save image", exact: true }).click();
  await expect(
    page.getByRole("dialog", { name: "Save image", exact: true }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Close image save", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Leave image mode", exact: true })
    .click();
  await expect(message).toHaveValue("Synthetic unsent chat draft");
  await expect(message).toBeFocused();
  expect(chatCalls).toBe(1); // Approved: the image is now a saved chat turn.
  await workspaceLink(page, "Workflows");
  await page
    .getByRole("button", { name: "Use Brief to images template", exact: true })
    .click();
  await configureStudioBlock(page, "Draft image prompt");
  await expect(
    page.getByRole("combobox", { name: "Model", exact: true }),
  ).toContainText("fake-chat");
  await page.goBack();
  await page.goBack();
  await expect(message).toHaveValue("Synthetic unsent chat draft");
});

test("Workflow count uses automatic seeds and repeats uncertain acceptance exactly", async ({
  page,
}) => {
  await page.goto("/workflows/new?template=brief_images");
  await configureStudioBlock(page, "Draft image prompt");
  await chooseStudioModel(page);
  await configureStudioBlock(page, "Create images");
  await expect(
    page.getByRole("spinbutton", { name: "Seed 1", exact: true }),
  ).not.toBeVisible();
  await page.getByRole("button", { name: "3", exact: true }).click();
  await openStudioRun(page);
  await page
    .getByRole("textbox", { name: "Image brief", exact: true })
    .fill("Synthetic automatic variants");
  const bodies: { request_key: string; inputs: Record<string, unknown> }[] = [];
  const accepted: {
    id: string;
    graph: {
      nodes: {
        kind: string;
        config: {
          count?: number;
          seeds?: number[];
          params?: Record<string, unknown>;
        };
      }[];
    };
  }[] = [];
  await page.route("**/api/workflows/defs/*/runs", async (route) => {
    bodies.push(route.request().postDataJSON());
    if (bodies.length === 1) {
      const response = await route.fetch();
      accepted.push(await response.json());
      await route.abort("failed");
    } else {
      const response = await route.fetch();
      accepted.push(await response.json());
      await route.fulfill({ response });
    }
  });
  await page.getByRole("button", { name: "Run workflow", exact: true }).click();
  await expect(
    page
      .getByRole("alert")
      .filter({ hasText: /Failed to fetch|Load failed|NetworkError/ }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Run workflow", exact: true }).click();
  await expect.poll(() => bodies.length).toBe(2);
  expect(bodies[1]).toEqual(bodies[0]);
  await expect.poll(() => accepted.length).toBe(2);
  expect(accepted[1].id).toBe(accepted[0].id);
  const images = accepted[0].graph.nodes.find(
    (n) => n.kind === "generate_image",
  )!;
  expect(images.config.seeds).toHaveLength(3);
  expect(
    accepted[1].graph.nodes.find((n) => n.kind === "generate_image")!.config
      .seeds,
  ).toEqual(images.config.seeds);
  for (const seed of images.config.seeds!) {
    expect(Number.isInteger(seed)).toBe(true);
    expect(seed).toBeGreaterThanOrEqual(0);
    expect(seed).toBeLessThanOrEqual(4294967295);
  }
  const params = accepted[0].graph.nodes.find((n) => n.kind === "generate")!
    .config.params!;
  expect(Object.values(params).every((v) => v == null)).toBe(true);
  await expect(
    page
      .getByRole("article", { name: "Brief to images run" })
      .first()
      .getByRole("textbox", { name: "Review result" }),
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
  await workspaceLink(page, "Workflows");
  await page.goBack();
  await expect(page).toHaveURL(new RegExp(`/c/${chat.id}$`));
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
    await page.goto("/design?studio");
    for (const theme of ["light", "dark"]) {
      await page.getByRole("button", { name: theme, exact: true }).click();
      await configureStudioBlock(page, "Draft image prompt");
      await expect(
        page.getByRole("combobox", { name: "Model", exact: true }),
      ).toBeVisible();
      if (width < 768)
        await expect(
          page.locator(".wf-outline-row[data-selected=true]"),
        ).toContainText("Draft image prompt");
      else
        await expect(
          page.locator(".wf-block[data-selected=true]"),
        ).toContainText("Draft image prompt");
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
      await configureStudioBlock(page, "Create images");
      await expect(
        page.getByRole("group", { name: "Images", exact: true }),
      ).toBeVisible();
      await configureStudioBlock(page, "Check the prompt");
      await expect(
        page.getByRole("switch", { name: "Allow editing", exact: true }),
      ).toBeVisible();
      await configureStudioBlock(page, "Start");
      await expect(
        page.getByRole("textbox", { name: "Input label", exact: true }),
      ).toHaveValue("Image brief");
      await page
        .getByRole("button", { name: "Close Inspector", exact: true })
        .click();
      await settle(page);
    }
  }
});
