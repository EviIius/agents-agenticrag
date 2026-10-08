import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { mkdir, writeFile } from "node:fs/promises";
import { settle } from "./helpers";
const states = [
  "Folders",
  "Empty folders",
  "Loading folders",
  "Folder error",
  "Empty folder",
  "Loading chats",
  "Chat error",
  "Folder menu",
  "Search result",
  "Move menu",
  "Create folder",
  "Rename folder",
  "Delete folder",
  "Save error",
  "Saving",
  "Backup ready",
  "No backup",
  "Backup warning",
  "Backup loading",
  "Backup error",
  "Backing up",
];
for (const width of [390, 1440])
  for (const theme of ["light", "dark"])
    test(`5C organization design ${width} ${theme}`, async ({
      page,
      browserName,
    }) => {
      await page.setViewportSize({ width, height: 900 });
      await page.goto("/design?organize");
      await page.getByRole("button", { name: theme, exact: true }).click();
      const dir = "../artifacts/phase-5/5c";
      await mkdir(dir, { recursive: true });
      const results = [];
      for (const state of states) {
        await page.getByRole("button", { name: state, exact: true }).click();
        if (
          ["Folders", "Empty folder", "Loading chats", "Chat error"].includes(
            state,
          )
        )
          await page
            .getByRole("button", {
              name: "Folder Invented Orchard, 1 chats",
              exact: true,
            })
            .click();
        if (state === "Folder menu")
          await page
            .getByRole("button", {
              name: "Actions for folder Invented Orchard",
              exact: true,
            })
            .click();
        if (state === "Move menu") {
          await page
            .getByRole("button", {
              name: "Actions for Invented lantern chat",
              exact: true,
            })
            .click();
          await page
            .getByRole("menuitem", { name: "Move to folder", exact: true })
            .click();
        }
        if (
          ![
            "Folder menu",
            "Move menu",
            "Create folder",
            "Rename folder",
            "Delete folder",
            "Save error",
            "Saving",
          ].includes(state)
        )
          await page
            .locator('[data-slot="organization-fixture"]')
            .scrollIntoViewIfNeeded();
        await settle(page);
        const scan = await new AxeBuilder({ page }).analyze();
        const bad = scan.violations.filter((v) =>
          ["serious", "critical"].includes(v.impact!),
        );
        expect(bad, state).toEqual([]);
        await page.screenshot({
          path: `${dir}/organization-${state.toLowerCase().replaceAll(/[^a-z0-9]+/g, "-")}-${width}-${theme}-${browserName}-fake.png`,
          fullPage: true,
        });
        results.push({ state, seriousCritical: bad.length });
        if (["Folder menu", "Move menu"].includes(state)) {
          await page.keyboard.press("Escape");
          await page.keyboard.press("Escape");
        }
        if (
          [
            "Create folder",
            "Rename folder",
            "Delete folder",
            "Save error",
          ].includes(state)
        )
          await page
            .getByRole("button", { name: "Cancel", exact: true })
            .click();
        if (state === "Saving")
          await page
            .goto("/design?organize")
            .then(() =>
              page.getByRole("button", { name: theme, exact: true }).click(),
            );
      }
      await writeFile(
        `${dir}/organization-axe-${width}-${theme}-${browserName}-fake.json`,
        JSON.stringify(results, null, 2),
      );
    });
