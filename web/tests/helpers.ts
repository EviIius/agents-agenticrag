import { expect, type Page } from "@playwright/test";

/** Settle finite motion only: activity loops must never block evidence or axe. */
export async function settle(page: Page) {
  await expect
    .poll(
      () =>
        page.evaluate(
          () =>
            document.getAnimations().filter((animation) => {
              const timing = animation.effect?.getComputedTiming();
              return (
                animation.playState === "running" &&
                timing &&
                Number.isFinite(timing.endTime)
              );
            }).length,
        ),
      { timeout: 1000 },
    )
    .toBe(0);
}
