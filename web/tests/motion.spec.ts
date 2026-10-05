import {
  test,
  expect,
  type Page,
  type Locator,
  type ElementHandle,
} from "@playwright/test";
import { settle } from "./helpers";
import { mkdir, writeFile } from "node:fs/promises";

const cases = [
  ["Motion settings", "dialog-content", "Settings"],
  ["Motion dialog", "dialog-content", "Synthetic dialog"],
  ["Motion alert", "alert-dialog-content", "Synthetic confirmation"],
  ["Motion popover", "popover-content", ""],
  ["Motion menu", "dropdown-menu-content", ""],
  ["Motion select", "select-content", ""],
  ...["left", "right", "top", "bottom"].map((side) => [
    `Motion sheet ${side}`,
    "sheet-content",
    `Synthetic ${side} sheet`,
  ]),
  ["Motion drawer", "drawer-content", "Synthetic drawer"],
] as const;

async function setup(page: Page, width: number) {
  await page.setViewportSize({ width, height: 900 });
  await page.emulateMedia({ reducedMotion: "no-preference" });
  await page.goto("/design");
  await expect(
    page.getByRole("region", { name: "Motion foundation" }),
  ).toBeVisible();
  await settle(page);
}
async function trigger(page: Page, name: string) {
  const control =
    name === "Motion select"
      ? page.getByRole("combobox", { name })
      : page.getByRole("button", { name, exact: true });
  await control.click();
}
async function style(surface: Locator) {
  return surface.evaluate((element) => {
    const css = getComputedStyle(element);
    return {
      name: css.animationName,
      duration: css.animationDuration,
      transition: css.transitionDuration,
      pointers: css.pointerEvents,
    };
  });
}
async function close(page: Page, slot: string) {
  if (slot === "alert-dialog-content")
    await page
      .getByRole("button", { name: "Cancel", exact: true })
      .evaluate((el) => (el as HTMLElement).click());
  else if (slot === "drawer-content")
    await page
      .getByRole("button", { name: "Close motion drawer", exact: true })
      .evaluate((el) => (el as HTMLElement).click());
  else await page.keyboard.press("Escape");
}
type ExitTiming = { closedAt: number | null; detachedAt: number | null };
async function watchExit(handle: ElementHandle<HTMLElement | SVGElement>) {
  await handle.evaluate((element) => {
    const timing: ExitTiming = { closedAt: null, detachedAt: null };
    (window as unknown as { motionExit: ExitTiming }).motionExit = timing;
    const observer = new MutationObserver(() => {
      if (
        element.getAttribute("data-state") === "closed" &&
        timing.closedAt === null
      )
        timing.closedAt = performance.now();
      if (!element.isConnected) {
        timing.detachedAt = performance.now();
        observer.disconnect();
      }
    });
    observer.observe(document.body, {
      attributes: true,
      attributeFilter: ["data-state"],
      childList: true,
      subtree: true,
    });
  });
}
async function assertExit(
  page: Page,
  handle: ElementHandle<HTMLElement | SVGElement>,
) {
  // Driver polling has transport/trace overhead. Measure the actual DOM lifetime in the page.
  await page.waitForFunction(
    () =>
      (window as unknown as { motionExit: ExitTiming }).motionExit
        .detachedAt !== null,
  );
  const timing = await page.evaluate(
    () => (window as unknown as { motionExit: ExitTiming }).motionExit,
  );
  expect(timing.closedAt).not.toBeNull();
  const elapsed = timing.detachedAt! - timing.closedAt!;
  expect(elapsed).toBeGreaterThanOrEqual(0);
  expect(elapsed).toBeLessThanOrEqual(400);
  expect(await handle.evaluate((element) => element.isConnected)).toBe(false);
  return elapsed;
}
for (const width of [390, 1440]) {
  test(`overlay entrances and exits ${width}`, async ({ page }) => {
    await setup(page, width);
    const evidence = [];
    for (const [name, slot] of cases) {
      await trigger(page, name);
      const surface = page
        .locator(`[data-slot="${slot}"][data-state="open"]`)
        .last();
      await expect(surface).toBeVisible();
      const css = await style(surface);
      expect(css.name).not.toBe("none");
      expect(
        Math.max(...css.duration.split(",").map(parseFloat)),
      ).toBeLessThanOrEqual(0.32);
      expect(css.pointers).not.toBe("none");
      await settle(page);
      const handle = await surface.elementHandle();
      await watchExit(handle!);
      await close(page, slot);
      const closing = await handle!.evaluate((element) => ({
        attached: element.isConnected,
        name: getComputedStyle(element).animationName,
        state: element.getAttribute("data-state"),
      }));
      expect(closing.attached).toBe(true);
      expect(closing.state).toBe("closed");
      expect(closing.name).not.toBe("none");
      const exit_ms = await assertExit(page, handle!);
      evidence.push({
        name,
        enter: css,
        exit: closing,
        exit_ms,
        exit_budget_ms: 400,
      });
    }
    // The submenu uses the same production menu primitives and must also animate.
    await trigger(page, "Motion menu");
    await page
      .getByRole("menuitem", { name: "Example submenu", exact: true })
      .focus();
    await page.keyboard.press("ArrowRight");
    const submenu = page.locator('[data-slot="dropdown-menu-sub-content"]');
    await expect(submenu).toBeVisible();
    expect((await style(submenu)).name).toBe("floating-in");
    await page.keyboard.press("Escape");
    await page.keyboard.press("Escape");
    // Tooltip's Radix states are instant-open/delayed-open, rather than open.
    const tooltipTrigger = page.getByRole("button", {
      name: "Motion tooltip",
      exact: true,
    });
    await tooltipTrigger.focus();
    const tooltip = page.locator('[data-slot="tooltip-content"]');
    await expect(tooltip).toHaveCount(1);
    const hiddenForTouch =
      width < 640 ||
      (await page.evaluate(
        () => matchMedia("(hover: none), (pointer: coarse)").matches,
      ));
    if (hiddenForTouch) await expect(tooltip).toBeHidden();
    else await expect(tooltip).toBeVisible();
    expect((await style(tooltip)).name).toBe("tooltip-in");
    await page.keyboard.press("Escape");
    await expect(tooltip).toHaveCount(0);
    await mkdir("../artifacts/phase-4/4b", { recursive: true });
    await writeFile(
      `../artifacts/phase-4/4b/overlay-${width}-${test.info().project.name}-fake.json`,
      JSON.stringify(evidence, null, 2),
    );
  });
  for (const mode of ["system", "always"])
    test(`all motion removed ${mode} ${width}`, async ({ page }) => {
      await setup(page, width);
      if (mode === "system")
        await page.emulateMedia({ reducedMotion: "reduce" });
      else
        await page
          .getByRole("button", { name: "Always reduce motion", exact: true })
          .click();
      for (const [name, slot] of cases) {
        await trigger(page, name);
        const surface = page
          .locator(`[data-slot="${slot}"][data-state="open"]`)
          .last();
        await expect(surface).toBeVisible();
        const css = await style(surface);
        expect(css.name).toBe("none");
        expect(css.transition).toBe("0s");
        const handle = await surface.elementHandle();
        await close(page, slot);
        await page.evaluate(() => new Promise(requestAnimationFrame));
        expect(await handle!.evaluate((el) => el.isConnected)).toBe(false);
      }
      await trigger(page, "Motion menu");
      await page
        .getByRole("menuitem", { name: "Example submenu", exact: true })
        .focus();
      await page.keyboard.press("ArrowRight");
      const submenu = page.locator('[data-slot="dropdown-menu-sub-content"]');
      await expect(submenu).toBeVisible();
      expect((await style(submenu)).name).toBe("none");
      expect((await style(submenu)).transition).toBe("0s");
      await page.keyboard.press("Escape");
      await page.keyboard.press("Escape");
      await page
        .getByRole("button", { name: "Motion tooltip", exact: true })
        .focus();
      const tooltip = page.locator('[data-slot="tooltip-content"]');
      await expect(tooltip).toHaveCount(1);
      expect((await style(tooltip)).name).toBe("none");
      expect((await style(tooltip)).transition).toBe("0s");
      await page.keyboard.press("Escape");
      await expect(tooltip).toHaveCount(0);
      const moving = await page.evaluate(
        () =>
          [document.documentElement, ...document.querySelectorAll("*")]
            .flatMap((el) =>
              [undefined, "::before", "::after"].map((pseudo) =>
                getComputedStyle(el, pseudo),
              ),
            )
            .filter(
              (css) =>
                css.animationName !== "none" ||
                css.transitionDuration
                  .split(",")
                  .some((duration) => parseFloat(duration) !== 0),
            ).length,
      );
      expect(moving).toBe(0);
      expect(
        await page.evaluate(
          () =>
            document
              .getAnimations()
              .filter((animation) => animation.playState === "running").length,
        ),
      ).toBe(0);
    });
}

for (const width of [390, 1440])
  for (const mode of ["normal", "system", "always"]) {
    test(`production action and recording dialogs retain exits ${mode} ${width}`, async ({
      page,
    }) => {
      await setup(page, width);
      if (mode === "system")
        await page.emulateMedia({ reducedMotion: "reduce" });
      if (mode === "always")
        await page
          .getByRole("button", { name: "Always reduce motion", exact: true })
          .click();
      const reduced = mode !== "normal";
      const verifyExit = async (
        surface: Locator,
        action: () => Promise<unknown>,
      ) => {
        await expect(surface).toBeVisible();
        await settle(page);
        const handle = await surface.elementHandle();
        if (!reduced) await watchExit(handle!);
        await action();
        if (!reduced) {
          const retained = await handle!.evaluate((element) => ({
            attached: element.isConnected,
            state: element.getAttribute("data-state"),
            inert: (element as HTMLElement).inert,
          }));
          expect(retained).toEqual({
            attached: true,
            state: "closed",
            inert: true,
          });
        } else {
          await page.evaluate(() => new Promise(requestAnimationFrame));
          expect(await handle!.evaluate((element) => element.isConnected)).toBe(
            false,
          );
        }
        if (!reduced) await assertExit(page, handle!);
      };
      for (const [button, title] of [
        ["Motion rename", "Rename chat"],
        ["Motion delete", "Delete chat?"],
        ["Motion export", "Export chat"],
      ]) {
        await page.getByRole("button", { name: button, exact: true }).click();
        const surface = page.getByRole(
          button === "Motion delete" ? "alertdialog" : "dialog",
          { name: title, exact: true },
        );
        if (button === "Motion rename")
          await page
            .getByRole("textbox", { name: "Chat title", exact: true })
            .fill("Edited synthetic title");
        await verifyExit(surface, () =>
          button === "Motion delete"
            ? page
                .getByRole("button", { name: "Cancel", exact: true })
                .evaluate((el) => (el as HTMLElement).click())
            : page.keyboard.press("Escape"),
        );
      }
      await page
        .getByRole("button", { name: "Motion rename", exact: true })
        .click();
      await expect(
        page.getByRole("textbox", { name: "Chat title", exact: true }),
      ).toHaveValue("Synthetic motion chat");
      await page.keyboard.press("Escape");
      await settle(page);
      const recordingActions = page.getByRole("button", {
        name: "Recording actions for fake-motion.wav",
        exact: true,
      });
      for (const format of ["Download text", "Download details (.json)"]) {
        await recordingActions.click();
        await page.getByRole("menuitem", { name: format, exact: true }).click();
        const surface = page.getByRole("dialog", {
          name: "Save recording",
          exact: true,
        });
        await expect(
          surface.getByRole("button", {
            name: format.includes("json") ? "Details (.json)" : "Text (.txt)",
            exact: true,
          }),
        ).toHaveAttribute("aria-pressed", "true");
        await verifyExit(surface, () =>
          page
            .getByRole("button", {
              name: "Close recording download",
              exact: true,
            })
            .evaluate((el) => (el as HTMLElement).click()),
        );
      }
      await recordingActions.click();
      await page
        .getByRole("menuitem", { name: "Open transcript", exact: true })
        .click();
      const transcript = page.getByRole("dialog", {
        name: "fake-motion.wav",
        exact: true,
      });
      await expect(transcript).toBeVisible();
      await transcript
        .getByRole("button", { name: "Download", exact: true })
        .click();
      await verifyExit(
        page.getByRole("dialog", { name: "Save recording", exact: true }),
        () =>
          page
            .getByRole("button", {
              name: "Close recording download",
              exact: true,
            })
            .evaluate((el) => (el as HTMLElement).click()),
      );
      await page
        .getByRole("button", { name: "Close transcript", exact: true })
        .click();
      await expect(transcript).toHaveCount(0);
    });
  }
