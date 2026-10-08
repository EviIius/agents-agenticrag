import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { mkdir, writeFile } from "node:fs/promises";
import { settle } from "./helpers";
for (const width of [390, 1440])
  for (const theme of ["light", "dark"])
    test(`5A production design states ${width} ${theme}`, async ({
      page,
      browserName,
    }) => {
      await page.setViewportSize({ width, height: 900 });
      await page.goto("/design?everyday");
      await page.getByRole("button", { name: theme, exact: true }).click();
      const out = "../artifacts/phase-5/5a";
      await mkdir(out, { recursive: true });
      const results: { state: string; seriousCritical: number }[] = [];
      const capture = async (state: string) => {
        await settle(page);
        await page.screenshot({
          path: `${out}/${state}-${width}-${theme}-${browserName}-fake.png`,
          fullPage: true,
        });
        const scan = await new AxeBuilder({ page }).analyze();
        const violations = scan.violations.filter((v) =>
          ["serious", "critical"].includes(v.impact!),
        );
        expect(violations, state).toEqual([]);
        results.push({ state, seriousCritical: violations.length });
      };
      await expect(
        page.getByRole("region", { name: "Chat controls" }),
      ).toBeVisible();
      await capture("controls-pristine");
      const panel = page.getByRole("region", { name: "Chat controls" });
      await panel
        .getByRole("switch", { name: "Use model default for Temperature" })
        .click();
      await panel
        .getByRole("spinbutton", { name: "Temperature", exact: true })
        .fill("3");
      await capture("controls-invalid");
      await panel
        .getByRole("spinbutton", { name: "Temperature", exact: true })
        .fill(".7");
      await capture("controls-dirty");
      await panel
        .getByRole("button", { name: "Save settings", exact: true })
        .click();
      await expect(
        panel.getByRole("button", { name: "Save settings", exact: true }),
      ).toContainText("Saved");
      await capture("controls-saved");
      await panel
        .getByRole("spinbutton", { name: "Context length" })
        .fill("65536");
      await capture("context-invalid");
      await panel
        .getByRole("spinbutton", { name: "Context length" })
        .fill("8192");
      await capture("context-apply");
      await panel
        .getByRole("combobox", { name: "Preset", exact: true })
        .click();
      await capture("preset-select");
      await page.keyboard.press("Escape");
      await page.getByRole("button", { name: "Presets", exact: true }).click();
      await expect(
        page.getByRole("heading", { name: "Synthetic Focus", exact: true }),
      ).toBeVisible();
      await capture("presets-list");
      await page
        .getByRole("switch", { name: "Use Synthetic Focus for new chats" })
        .click();
      await capture("presets-default");
      await page
        .getByRole("button", { name: "New preset", exact: true })
        .click();
      const editor = page.getByRole("dialog", {
        name: "Save as preset",
        exact: true,
      });
      await expect(editor).toBeVisible();
      await capture("preset-editor");
      await editor
        .getByRole("textbox", { name: "Preset name" })
        .fill("Synthetic Focus");
      await editor
        .getByRole("button", { name: "Save preset", exact: true })
        .click();
      await expect(editor.getByRole("alert")).toContainText("already exists");
      await expect(editor.getByRole("alert")).toBeInViewport();
      await capture("preset-collision");
      await editor.getByRole("button", { name: "Cancel", exact: true }).click();
      await page.getByRole("button", { name: "Delete", exact: true }).click();
      await capture("preset-delete");
      await page.getByRole("button", { name: "Cancel", exact: true }).click();
      for (const [area, state, text] of [
        ["Controls loading", "controls-loading", "Loading chat controls…"],
        ["Controls error", "controls-error", "Couldn't load chat controls."],
        ["Empty presets", "presets-empty", "No presets yet."],
        ["Preset error", "presets-error", "Couldn't load presets."],
        ["Preset loading", "presets-loading", "Loading presets…"],
      ]) {
        await page.getByRole("button", { name: area!, exact: true }).click();
        await expect(page.getByText(text!, { exact: false })).toBeVisible();
        await capture(state!);
      }
      await page
        .getByRole("button", { name: "Model rename", exact: true })
        .click();
      await page
        .getByRole("button", { name: "Rename Synthetic Display" })
        .click();
      await capture("model-rename");
      await page.getByRole("button", { name: "Cancel", exact: true }).click();
      await page
        .getByRole("region", { name: "Everyday preview" })
        .getByRole("button", { name: "Choose model" })
        .click();
      await capture("model-picker-renamed");
      await writeFile(
        `${out}/design-axe-${width}-${theme}-${browserName}-fake.json`,
        JSON.stringify(results, null, 2),
      );
    });
