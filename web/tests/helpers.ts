import { expect, type Page } from "@playwright/test";

/** Settle finite motion only: activity loops must never block evidence or axe. */
export async function settle(page: Page) {
  const result = await page.evaluate(
    () =>
      new Promise<{
        settled: boolean;
        elapsed: number;
        animations: unknown[];
      }>((resolve) => {
        const started = performance.now();
        let clearFrames = 0;
        const frame = () => {
          const animations = document.getAnimations().filter((animation) => {
            const timing = animation.effect?.getComputedTiming();
            return (
              animation.playState === "running" &&
              timing &&
              Number.isFinite(timing.endTime)
            );
          });
          clearFrames = animations.length ? 0 : clearFrames + 1;
          const elapsed = performance.now() - started;
          if (clearFrames >= 2 || elapsed >= 1000) {
            resolve({
              settled: clearFrames >= 2 && elapsed <= 1000,
              elapsed,
              animations: animations.map((animation) => ({
                name:
                  animation instanceof CSSAnimation
                    ? animation.animationName
                    : null,
                property:
                  animation instanceof CSSTransition
                    ? animation.transitionProperty
                    : null,
                timing: animation.effect?.getComputedTiming(),
                currentTime: animation.currentTime,
                tag: (animation.effect as KeyframeEffect)?.target?.tagName,
                slot: (
                  (animation.effect as KeyframeEffect)?.target as HTMLElement
                )?.dataset?.slot,
              })),
            });
          } else requestAnimationFrame(frame);
        };
        requestAnimationFrame(frame);
      }),
  );
  expect(
    result,
    "Finite motion must settle within the unchanged 1,000 ms deadline",
  ).toMatchObject({ settled: true });
}

/** Composer tools now live in one persistent menu. Uses the real controls. */
export async function openTools(page: Page) {
  if (
    !(await page.getByRole("menu", { name: "Tools", exact: true }).isVisible())
  ) {
    await settle(page);
    await page
      .locator(".composer")
      .getByRole("button", { name: "Tools", exact: true })
      .click();
  }
}
export async function enterImageMode(page: Page) {
  await openTools(page);
  await page
    .getByRole("menuitem", { name: "Create image", exact: true })
    .click();
}
export async function openAttachmentPicker(page: Page) {
  const chooser = page.waitForEvent("filechooser");
  const input = page.locator("input.composer-file-input");
  if (await input.isVisible()) await input.click();
  else
    await page
      .getByRole("button", { name: "Attach files", exact: true })
      .click();
  return chooser;
}
export async function webTool(page: Page) {
  await openTools(page);
  return page.getByRole("menuitemcheckbox", {
    name: "Search the web",
    exact: true,
  });
}
export async function libraryTool(page: Page) {
  await openTools(page);
  return page.getByRole("menuitemcheckbox", { name: "Library", exact: true });
}
export async function recordingAction(page: Page, name: string) {
  await settle(page);
  await page.getByRole("button", { name: /^Recording actions for/ }).click();
  return page.getByRole("menuitem", { name, exact: true });
}
