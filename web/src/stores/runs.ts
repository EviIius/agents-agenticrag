import { create } from "zustand";
import type { Message, Source } from "@/lib/api";
type LiveRun = {
  chatId: string;
  message: Message;
  stage: string;
  sources?: Source[];
  position?: number;
  steps: { label: string; detail: string; status: string }[];
};
export const useRuns = create<{
  runs: Record<string, LiveRun>;
  put: (id: string, run: LiveRun) => void;
  patch: (id: string, update: Partial<LiveRun>) => void;
  remove: (id: string) => void;
}>((set) => ({
  runs: {},
  put: (id, run) => set((s) => ({ runs: { ...s.runs, [id]: run } })),
  patch: (id, update) =>
    set((s) => ({ runs: { ...s.runs, [id]: { ...s.runs[id]!, ...update } } })),
  remove: (id) =>
    set((s) => {
      const runs = { ...s.runs };
      delete runs[id];
      return { runs };
    }),
}));
