import { useEffect, useState } from "react";

/** Enter once per app load, after server preferences and the restored chat arrive. */
export function useAppEntrance(ready: boolean) {
  const [started, setStarted] = useState(false);
  const [finished, setFinished] = useState(false);
  useEffect(() => {
    if (ready) setStarted(true);
  }, [ready]);
  useEffect(() => {
    if (!started) return;
    const timer = setTimeout(() => setFinished(true), 200);
    return () => clearTimeout(timer);
  }, [started]);
  return started && !finished;
}
