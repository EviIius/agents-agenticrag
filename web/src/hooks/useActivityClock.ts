import { useCallback, useSyncExternalStore } from "react";

// A shared presentation clock. It never requests work or advances engine progress.
let now = Date.now();
let timer: ReturnType<typeof setInterval> | undefined;
const listeners = new Set<() => void>();
export function subscribeActivityClock(listener: () => void) {
  listeners.add(listener);
  if (!timer) {
    now = Date.now();
    timer = setInterval(() => {
      now = Date.now();
      for (const update of listeners) update();
    }, 200);
  }
  return () => {
    listeners.delete(listener);
    if (!listeners.size) {
      clearInterval(timer);
      timer = undefined;
    }
  };
}
export function useActivityClock(
  active: boolean,
  began: number,
  words = false,
) {
  const subscribe = useCallback(
    (update: () => void) =>
      active ? subscribeActivityClock(update) : () => {},
    [active],
  );
  const snapshot = useCallback(() => {
    const age = Math.max(0, (timer ? now : Date.now()) - began);
    return active
      ? `${Math.floor(age / 1000)}:${words ? Math.floor(age / 2400) : 0}`
      : "0:0";
  }, [active, began, words]);
  const value = useSyncExternalStore(subscribe, snapshot, () => "0:0");
  const [elapsed, index] = value.split(":").map(Number);
  return { elapsed, index };
}
