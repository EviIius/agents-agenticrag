# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: workflow-studio-shell.spec.ts >> Workflow home design states 390 dark
- Location: tests/workflow-studio-shell.spec.ts:10:5

# Error details

```
Error: page.evaluate: Test ended.
```

# Test source

```ts
  1  | import { expect, type Page } from "@playwright/test";
  2  | 
  3  | /** Settle finite motion only: activity loops must never block evidence or axe. */
  4  | export async function settle(page: Page) {
> 5  |   const result = await page.evaluate(
     |                             ^ Error: page.evaluate: Test ended.
  6  |     () =>
  7  |       new Promise<{
  8  |         settled: boolean;
  9  |         elapsed: number;
  10 |         animations: unknown[];
  11 |       }>((resolve) => {
  12 |         const started = performance.now();
  13 |         let clearFrames = 0;
  14 |         const frame = () => {
  15 |           const animations = document.getAnimations().filter((animation) => {
  16 |             const timing = animation.effect?.getComputedTiming();
  17 |             return (
  18 |               animation.playState === "running" &&
  19 |               timing &&
  20 |               Number.isFinite(timing.endTime)
  21 |             );
  22 |           });
  23 |           clearFrames = animations.length ? 0 : clearFrames + 1;
  24 |           const elapsed = performance.now() - started;
  25 |           if (clearFrames >= 2 || elapsed >= 1000) {
  26 |             resolve({
  27 |               settled: clearFrames >= 2 && elapsed <= 1000,
  28 |               elapsed,
  29 |               animations: animations.map((animation) => ({
  30 |                 name:
  31 |                   animation instanceof CSSAnimation
  32 |                     ? animation.animationName
  33 |                     : null,
  34 |                 property:
  35 |                   animation instanceof CSSTransition
  36 |                     ? animation.transitionProperty
  37 |                     : null,
  38 |                 timing: animation.effect?.getComputedTiming(),
  39 |                 currentTime: animation.currentTime,
  40 |                 tag: (animation.effect as KeyframeEffect)?.target?.tagName,
  41 |                 slot: (
  42 |                   (animation.effect as KeyframeEffect)?.target as HTMLElement
  43 |                 )?.dataset?.slot,
  44 |               })),
  45 |             });
  46 |           } else requestAnimationFrame(frame);
  47 |         };
  48 |         requestAnimationFrame(frame);
  49 |       }),
  50 |   );
  51 |   expect(
  52 |     result,
  53 |     "Finite motion must settle within the unchanged 1,000 ms deadline",
  54 |   ).toMatchObject({ settled: true });
  55 | }
  56 | 
```