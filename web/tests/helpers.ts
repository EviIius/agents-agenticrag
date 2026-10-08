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
