import { expect, type Page } from "@playwright/test";

export async function openSidebar(page: Page) {
  if (
    !(await page
      .getByRole("navigation", { name: "Workspace", exact: true })
      .isVisible())
  )
    await page
      .getByRole("button", { name: "Open sidebar", exact: true })
      .click();
}
export async function workspaceLink(page: Page, label: "Workflows" | "Images") {
  await openSidebar(page);
  await page
    .getByRole("navigation", { name: "Workspace", exact: true })
    .getByRole("link", { name: label, exact: true })
    .click();
  await expect(page).toHaveURL(
    label === "Workflows" ? /\/workflows$/ : /\/images$/,
  );
}
