import type { Model } from "./api";

// This is an input estimate, not a sampling value sent to the runtime.
export function contextBudget(model?: Model, override?: number) {
  const maximum = model?.context_length ?? 8192;
  const chosen = override ?? model?.params_defaults?.max_tokens;
  const reserve =
    typeof chosen === "number" && chosen > 0
      ? Math.trunc(chosen)
      : Math.trunc(Math.max(1024, Math.min(8192, maximum * 0.25)));
  return { maximum, reserve, available: Math.max(0, maximum - reserve - 256) };
}
