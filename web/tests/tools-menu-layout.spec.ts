import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { mkdir, writeFile } from "node:fs/promises";
import { settle } from "./helpers";

const directory = "../artifacts/mobile-tools-20261021";
const sizes = [
  { name: "phone", width: 390, height: 844 },
  { name: "small-phone", width: 320, height: 568 },
  { name: "landscape", width: 844, height: 390 },
  { name: "keyboard", width: 390, height: 360 },
  { name: "desktop", width: 1440, height: 900 },
];

for (const size of sizes)
  for (const theme of ["light", "dark"] as const)
    test(`Tools fits ${size.name} ${theme} without moving its thinking controls`, async ({
      page,
    }, info) => {
      await page.setViewportSize(size);
      await page.emulateMedia({ colorScheme: theme });
      await page.goto("/design?attachments");
      await page
        .getByRole("button", { name: "Preview empty", exact: true })
        .click();
      if (size.name === "keyboard")
        await page.evaluate(() => {
          // Exercise the existing visual-viewport/safe-area constraint, not a
          // claim that desktop automation opens a physical iPhone keyboard.
          const css = document.documentElement.style;
          css.setProperty("--viewport-h", "280px");
          css.setProperty("--safe-area-top", "32px");
          css.setProperty("--safe-area-bottom", "16px");
        });
      const tools = page.getByRole("button", { name: "Tools", exact: true });
      // The design catalogue is a long document. Place its composer at the
      // visible bottom like the app, rather than centring it during scrolling.
      await tools.evaluate((el) => el.scrollIntoView({ block: "end" }));
      await tools.click();
      await settle(page);
      const menu = page.getByRole("menu", { name: "Tools", exact: true });
      const actions = menu.locator(".composer-tools-actions");
      const thinking = menu.getByRole("group", {
        name: "Thinking",
        exact: true,
      });
      const modelDefault = menu.getByRole("menuitemradio", {
        name: "Model default",
        exact: true,
      });
      await expect(modelDefault).toHaveText("Default");
      await expect(
        menu.getByRole("menuitem", { name: "Edit photo", exact: true }),
      ).toHaveCount(1);
      const box = (await menu.boundingBox())!;
      const anchor = (await tools.boundingBox())!;
      expect(box.x).toBeGreaterThanOrEqual(7);
      expect(box.x + box.width).toBeLessThanOrEqual(size.width - 7);
      expect(box.y).toBeGreaterThanOrEqual(7);
      expect(box.y + box.height).toBeLessThanOrEqual(size.height - 7);
      expect(box.y + box.height).toBeLessThanOrEqual(anchor.y - 4);
      expect(box.height).toBeLessThanOrEqual(330);
      expect(await menu.evaluate((el) => el.scrollTop)).toBe(0);
      const levels = await thinking
        .getByRole("menuitemradio")
        .evaluateAll((items) =>
          items.map((item) => {
            const box = item.getBoundingClientRect();
            return {
              x: box.x,
              y: box.y,
              width: box.width,
              height: box.height,
              clipped: item.scrollWidth > item.clientWidth,
            };
          }),
        );
      expect(levels).toHaveLength(5);
      expect(
        Math.max(...levels.map((item) => item.y)) -
          Math.min(...levels.map((item) => item.y)),
      ).toBeLessThan(1);
      expect(levels.every((item) => !item.clipped && item.width >= 44)).toBe(
        true,
      );
      if (size.width <= 639 || info.project.name === "webkit")
        expect(levels.every((item) => item.height >= 44)).toBe(true);
      const thinkingBefore = (await thinking.boundingBox())!;
      const edit = menu.getByRole("menuitem", {
        name: "Edit photo",
        exact: true,
      });
      await edit.scrollIntoViewIfNeeded();
      const editBox = (await edit.boundingBox())!;
      const scrollBox = (await actions.boundingBox())!;
      expect(editBox.y).toBeGreaterThanOrEqual(scrollBox.y - 1);
      expect(editBox.y + editBox.height).toBeLessThanOrEqual(
        scrollBox.y + scrollBox.height + 1,
      );
      if (size.name === "keyboard")
        expect(
          await actions.evaluate((el) => el.scrollHeight > el.clientHeight),
        ).toBe(true);
      const thinkingAfter = (await thinking.boundingBox())!;
      expect(Math.abs(thinkingAfter.y - thinkingBefore.y)).toBeLessThan(1);
      expect(await menu.evaluate((el) => el.scrollTop)).toBe(0);
      await mkdir(directory, { recursive: true });
      await page.screenshot({
        path: `${directory}/tools-${size.name}-${theme}-${info.project.name}-synthetic.png`,
      });
      if (size.name === "phone") {
        const result = await new AxeBuilder({ page }).analyze();
        expect(
          result.violations.filter((v) =>
            ["serious", "critical"].includes(v.impact ?? ""),
          ),
        ).toEqual([]);
      }
      await modelDefault.focus();
      await page.keyboard.press("ArrowRight");
      await expect(
        menu.getByRole("menuitemradio", { name: "Off", exact: true }),
      ).toBeFocused();
      await menu
        .getByRole("menuitemradio", { name: "Max", exact: true })
        .click();
      await expect(
        menu.getByRole("menuitemradio", { name: "Max", exact: true }),
      ).toBeChecked();
      await page.keyboard.press("Escape");
      await expect(menu).toHaveCount(0);
      await expect(tools).toBeFocused();
      await writeFile(
        `${directory}/geometry-${size.name}-${theme}-${info.project.name}-synthetic.json`,
        JSON.stringify(
          {
            viewport: size,
            theme,
            menu: box,
            anchor,
            levels,
            thinkingBefore,
            thinkingAfter,
            outerScrollTop: 0,
            limits:
              "Synthetic design fixture; no physical iPhone keyboard or VoiceOver pass.",
          },
          null,
          2,
        ) + "\n",
      );
    });
