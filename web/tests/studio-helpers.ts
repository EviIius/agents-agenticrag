import { expect, type Page } from "@playwright/test";
import { settle } from "./helpers";
export async function configureStudioBlock(page: Page, title: string) {
  await expect(page.locator(".wf-studio")).toBeVisible();
  await settle(page);
  const close = page.getByRole("button", {
    name: "Close Inspector",
    exact: true,
  });
  if (await close.isVisible()) {
    await close.click();
    await settle(page);
  }
  const outline = page.getByRole("button", {
    name: `Configure ${title}`,
    exact: true,
  });
  if (await outline.isVisible()) await outline.click();
  else {
    const node = page.locator(".react-flow__node-block").filter({
      has: page
        .locator(".wf-block-title")
        .filter({ hasText: new RegExp("^" + title + "$") }),
    });
    await node.focus();
    await expect(node).toBeFocused();
    await page.keyboard.press("Enter");
  }
  await expect(
    page.getByRole("textbox", { name: "Block name", exact: true }),
  ).toHaveValue(title);
}
export async function chooseStudioModel(page: Page) {
  await page.getByRole("combobox", { name: "Model", exact: true }).click();
  await page
    .getByRole("option")
    .filter({ hasText: "fake-chat" })
    .first()
    .click();
}
export async function openStudioRun(page: Page) {
  const close = page.getByRole("button", {
    name: "Close Inspector",
    exact: true,
  });
  if (await close.isVisible()) {
    await close.click();
    await settle(page);
  }
  await expect(page.locator(".wf-save-status")).toHaveText("Saved");
  await page.getByRole("button", { name: "Run", exact: true }).click();
  await expect(
    page.getByRole("button", { name: "Run workflow", exact: true }),
  ).toBeVisible();
}
