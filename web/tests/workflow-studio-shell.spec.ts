import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { mkdir, writeFile } from "node:fs/promises";
import { settle } from "./helpers";
import { openSidebar, workspaceLink } from "./workspace-helpers";

const dir = "../artifacts/workflow-studio/ws-a/browser";
for (const width of [390, 1440])
  for (const theme of ["light", "dark"]) {
    test(`Workflow home design states ${width} ${theme}`, async ({
      page,
      browserName,
    }) => {
      await page.setViewportSize({ width, height: 900 });
      await page.goto("/design?workflow-home");
      await page.getByRole("button", { name: theme, exact: true }).click();
      await mkdir(dir, { recursive: true });
      const results = [];
      for (const state of [
        "empty",
        "loading",
        "populated",
        "error",
        "reconnecting",
        "run-loading",
        "run-unavailable",
      ]) {
        await page.getByRole("button", { name: state, exact: true }).click();
        await settle(page);
        const scan = await new AxeBuilder({ page }).analyze();
        expect(
          scan.violations.filter((v) =>
            ["serious", "critical"].includes(v.impact ?? ""),
          ),
          state,
        ).toEqual([]);
        expect(
          await page.evaluate(
            () => document.documentElement.scrollWidth <= innerWidth,
          ),
        ).toBeTruthy();
        results.push({ state, seriousCritical: 0 });
        await page.screenshot({
          path: `${dir}/home-${state}-${width}-${theme}-${browserName}-fake.png`,
          fullPage: true,
        });
      }
      await writeFile(
        `${dir}/axe-home-${width}-${theme}-${browserName}.json`,
        JSON.stringify(results, null, 2),
      );
    });
  }

test("Shared sidebar, rail and palette navigate real workspaces without tabs", async ({
  page,
  browserName,
}) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto("/");
  await workspaceLink(page, "Workflows");
  await expect(
    page.getByRole("heading", { name: "Workflows", exact: true }),
  ).toBeVisible();
  await expect(
    page
      .getByRole("navigation", { name: "Workspace", exact: true })
      .getByRole("link", { name: "Workflows", exact: true }),
  ).toHaveAttribute("aria-current", "page");
  await expect(
    page.getByRole("link", { name: "Chat", exact: true }),
  ).toHaveCount(0);
  await expect(page.getByRole("link", { name: /Use .* template/ })).toHaveCount(
    2,
  );
  await page
    .getByRole("button", { name: "Collapse sidebar", exact: true })
    .click();
  await workspaceLink(page, "Images");
  await expect(
    page.getByRole("heading", { name: "Images", exact: true }),
  ).toBeVisible();
  await expect(page.locator(".sidebar-desktop")).toHaveAttribute(
    "data-collapsed",
    "true",
  );
  await expect(
    page
      .getByRole("navigation", { name: "Workspace", exact: true })
      .getByRole("link", { name: "Images", exact: true }),
  ).toHaveAttribute("aria-current", "page");
  await page.keyboard.press("ControlOrMeta+k");
  await page
    .getByRole("combobox", { name: "Search chats and actions" })
    .fill("Workflows");
  await page.getByRole("option", { name: "Workflows", exact: true }).click();
  await expect(page).toHaveURL(/\/workflows$/);
  await page.setViewportSize({ width: 390, height: 844 });
  await openSidebar(page);
  await expect(
    page
      .getByRole("navigation", { name: "Workspace", exact: true })
      .getByRole("link", { name: "Images", exact: true }),
  ).toBeVisible();
  await page
    .getByRole("navigation", { name: "Workspace", exact: true })
    .getByRole("link", { name: "Images", exact: true })
    .click();
  await expect(page).toHaveURL(/\/images$/);
  await expect(
    page.getByRole("dialog", { name: "Chat history", exact: true }),
  ).not.toBeVisible();
  await settle(page);
  await mkdir(dir, { recursive: true });
  await page.screenshot({
    path: `${dir}/images-shared-shell-390-${browserName}-fake.png`,
    fullPage: true,
  });
});

test("Home opens template and persisted run detail, reconnects through existing SSE", async ({
  page,
  request,
}) => {
  const connection = (await (await request.get("/api/connections")).json())[0];
  const response = await request.post("/api/workflows/runs", {
    data: {
      request_key: crypto.randomUUID(),
      template: "brief_images",
      model: {
        connection_id: connection.id,
        model_id: "fake-chat",
        params: {},
      },
      brief: "Synthetic shell workflow",
      review_prompt: true,
      seeds: [19],
    },
  });
  expect(response.status()).toBe(202);
  const run = await response.json();
  await page.goto("/workflows");
  const recent = page.getByRole("region", {
    name: "Recent workflow runs",
    exact: true,
  });
  const row = recent.locator(`a[href='/workflows/runs/${run.id}']`);
  await expect(row).toContainText("Waiting for you");
  await row.click();
  const card = page.getByRole("article", {
    name: "Brief to images run",
    exact: true,
  });
  await expect(
    card.getByRole("textbox", { name: "Review image prompt" }),
  ).toBeVisible();
  await page.reload();
  await expect(
    card.getByRole("textbox", { name: "Review image prompt" }),
  ).toBeVisible();
  await workspaceLink(page, "Workflows");
  await page
    .getByRole("link", {
      name: "Use Recording to meeting pack template",
      exact: true,
    })
    .click();
  await expect(page).toHaveURL(/\/workflows\/new\?template=meeting_pack$/);
  await expect(
    page.getByRole("combobox", { name: "Saved recording" }),
  ).toBeVisible();
});
