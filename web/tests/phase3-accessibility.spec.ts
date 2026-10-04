import { settle } from "./helpers";
import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { mkdir, writeFile } from "node:fs/promises";
for (const width of [390, 1440])
  for (const theme of ["light", "dark"]) {
    test(`Phase 3 design states accessible ${width} ${theme}`, async ({
      page,
    }) => {
      await page.setViewportSize({ width, height: 900 });
      await page.addInitScript(
        (value) => localStorage.setItem("workbench-theme", value),
        theme,
      );
      await page.goto("/design");
      const region = page.getByRole("region", { name: "Phase 3 previews" });
      await expect(region).toBeVisible();
      await mkdir("../artifacts/phase-3", { recursive: true });
      const audit = async (name: string) => {
        await settle(page);
        await page.screenshot({
          animations: "disabled",
          path: `../artifacts/phase-3/${name}-${width}-${theme}-${test.info().project.name}-fake.png`,
        });
        await settle(page);
        expect(
          (await new AxeBuilder({ page }).analyze()).violations.filter((v) =>
            ["serious", "critical"].includes(v.impact ?? ""),
          ),
        ).toEqual([]);
      };
      for (const state of ["ready", "empty", "loading", "error"]) {
        await region
          .getByRole("button", {
            name: `Preview palette ${state}`,
            exact: true,
          })
          .click();
        await expect(
          page.getByRole("dialog", { name: "Command palette" }),
        ).toBeVisible();
        if (state === "empty")
          await expect(
            page.getByText("No chats or actions found"),
          ).toBeVisible();
        await audit(`palette-${state}`);
        await page.keyboard.press("Escape");
      }
      for (const state of [
        "ready",
        "loading",
        "missing",
        "status-error",
        "importing",
        "failed",
      ]) {
        await region
          .getByRole("button", { name: `Import preview ${state}`, exact: true })
          .click();
        if (["ready", "importing", "failed"].includes(state)) {
          await region
            .getByRole("button", { name: "Import old chats", exact: true })
            .click();
          await expect(
            page.getByRole("alertdialog", { name: "Import old chats?" }),
          ).toBeVisible();
          await audit(`legacy-import-${state}`);
          await page.keyboard.press("Escape");
        } else await audit(`legacy-import-${state}`);
      }
      await region
        .getByRole("button", { name: "Preview app update", exact: true })
        .click();
      await expect(
        page.getByRole("button", { name: "Reload", exact: true }),
      ).toBeVisible();
      await audit("update-toast");
    });
  }
test("keyboard walkthrough send stop regenerate branch model switch citation", async ({
  page,
  request,
}) => {
  await request.patch("/api/settings", {
    data: {
      default_model_id: "fake-chat",
      "web.default_on": false,
      "transcription.block_web": true,
    },
  });
  await page.goto("/");
  const composer = page.locator(".composer textarea");
  await expect(
    page.getByRole("button", { name: "Choose model" }),
  ).toContainText("fake-chat");
  await composer.focus();
  await composer.fill("#long:50 #slow:10");
  await page.keyboard.press("Control+Enter");
  await expect(
    page.getByRole("button", { name: "Stop generating" }),
  ).toBeVisible();
  await expect(page.getByText(/token0 token1/)).toBeVisible();
  await composer.focus();
  await page.keyboard.press("Escape");
  await expect(
    page.getByRole("button", { name: "Stop generating" }),
  ).toHaveCount(0);
  await expect(composer).toBeFocused();
  await expect(
    page.locator(".meta").filter({ hasText: /stopped/i }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Regenerate answer", exact: true })
    .last()
    .focus();
  await page.keyboard.press("Enter");
  await expect(page.getByText(/token49/)).toBeVisible({ timeout: 15000 });
  await expect(
    page.getByRole("button", { name: "Stop generating" }),
  ).toHaveCount(0);
  await page
    .getByRole("button", { name: "Previous branch", exact: true })
    .last()
    .focus();
  await page.keyboard.press("Enter");
  await expect(
    page.getByRole("button", { name: "Next branch", exact: true }).last(),
  ).toBeEnabled();
  await page
    .getByRole("button", { name: "Next branch", exact: true })
    .last()
    .focus();
  await page.keyboard.press("Enter");
  await page.keyboard.press("Control+k");
  const dialog = page.getByRole("dialog", { name: "Command palette" });
  await dialog.getByRole("combobox").fill("switch model");
  await expect(
    dialog.getByRole("option", { name: "Switch model…", exact: true }),
  ).toHaveAttribute("data-selected", "true");
  await page.keyboard.press("Enter");
  await page
    .getByRole("combobox", { name: "Search models" })
    .fill("fake-reasoning");
  const model = page.getByRole("option", { name: /fake-reasoning/ });
  await expect(model).toHaveAttribute("data-selected", "true");
  await page.keyboard.press("Enter");
  await expect(
    page.getByRole("button", { name: "Choose model" }),
  ).toContainText("fake-reasoning");
  await page.keyboard.press("Escape");
  await page.keyboard.press("Control+Shift+o");
  await expect(page).toHaveURL("http://127.0.0.1:5173/");
  await expect(page.getByRole("heading", { name: /Good / })).toBeVisible();
  await settle(page);
  const toggle = page.getByRole("button", { name: "Search off", exact: true });
  await expect(toggle).toBeVisible();
  await toggle.focus();
  await expect(toggle).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(
    page.getByRole("button", { name: "Search on", exact: true }),
  ).toBeVisible();
  await composer.focus();
  await composer.fill("Who lost the 2021 NBA Finals? Show a table.");
  await page.keyboard.press("Control+Enter");
  await expect(
    page.getByText("Synthetic web answer", { exact: false }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Stop generating" }),
  ).toHaveCount(0);
  const pill = page
    .getByRole("button", { name: /View source: Synthetic NBA Finals/ })
    .first();
  await pill.focus();
  await page.keyboard.press("Enter");
  await expect(
    page.getByRole("dialog", { name: "Citation sources" }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Close citation", exact: true }),
  ).toBeFocused();
  await page.keyboard.press("Escape");
  await expect(
    page.getByRole("dialog", { name: "Citation sources" }),
  ).not.toBeVisible();
  await expect(pill).toBeFocused();
  await mkdir("../artifacts/phase-3", { recursive: true });
  await writeFile(
    `../artifacts/phase-3/keyboard-${test.info().project.name}.json`,
    JSON.stringify(
      {
        method:
          "automated keyboard activation, focused controls; no mouse click",
        send: true,
        stop_focus: true,
        regenerate: true,
        branch: true,
        model_switch: true,
        citation: true,
        citation_focus_restored: true,
      },
      null,
      2,
    ),
  );
});

test("Escape stops a send before the run response arrives", async ({
  page,
  request,
}) => {
  await request.patch("/api/settings", {
    data: { default_model_id: "fake-chat", "web.default_on": false },
  });
  await page.route("**/api/chats/*/messages", async (route) => {
    await new Promise((resolve) => setTimeout(resolve, 350));
    await route.continue();
  });
  await page.goto("/");
  const composer = page.locator(".composer textarea");
  await expect(
    page.getByRole("button", { name: "Choose model" }),
  ).toContainText("fake-chat");
  await composer.fill("#long:100 #slow:10");
  await composer.press("Control+Enter");
  await expect(
    page.getByRole("button", { name: "Stop generating" }),
  ).toBeVisible();
  await composer.press("Escape");
  await expect(
    page.locator(".meta").filter({ hasText: /stopped/i }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Stop generating" }),
  ).toHaveCount(0);
  await expect(composer).toBeFocused();
});
