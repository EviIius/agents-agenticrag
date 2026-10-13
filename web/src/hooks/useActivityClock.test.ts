import { afterEach, expect, it, vi } from "vitest";
import { subscribeActivityClock } from "./useActivityClock";
afterEach(() => vi.useRealTimers());
it("shares one presentation timer and releases it after the last subscriber", () => {
  vi.useFakeTimers();
  const first = vi.fn(),
    second = vi.fn();
  const stopFirst = subscribeActivityClock(first);
  const stopSecond = subscribeActivityClock(second);
  expect(vi.getTimerCount()).toBe(1);
  vi.advanceTimersByTime(2400);
  expect(first).toHaveBeenCalledTimes(12);
  expect(second).toHaveBeenCalledTimes(12);
  stopFirst();
  vi.advanceTimersByTime(1000);
  expect(first).toHaveBeenCalledTimes(12);
  expect(second).toHaveBeenCalledTimes(17);
  stopSecond();
  expect(vi.getTimerCount()).toBe(0);
});
