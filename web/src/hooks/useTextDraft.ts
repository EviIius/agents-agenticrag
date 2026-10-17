import { useCallback, useState, useSyncExternalStore } from "react";
import { drafts, subscribeDraft, writeDraft } from "@/lib/composer-drafts";

export function useTextDraft(key: string | undefined, starter: string) {
  const [local, setLocal] = useState(() => {
    if (key && !drafts.has(key)) drafts.set(key, starter);
    return starter;
  });
  const subscribe = useCallback(
    (listener: () => void) => (key ? subscribeDraft(key, listener) : () => {}),
    [key],
  );
  const snapshot = useCallback(
    () => (key ? (drafts.get(key) ?? "") : local),
    [key, local],
  );
  const value = useSyncExternalStore(subscribe, snapshot, () => "");
  const setValue = (next: string | ((value: string) => string)) => {
    const text =
      typeof next === "function"
        ? next(key ? (drafts.get(key) ?? "") : local)
        : next;
    if (key) writeDraft(key, text);
    else setLocal(text);
  };
  return [value, setValue] as const;
}
