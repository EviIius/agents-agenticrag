import { create } from "zustand";
import type { SamplingDraft } from "@/components/settings/SamplingFields";
export type ControlDraft = {
  values: SamplingDraft;
  prompt: string;
  useDefault: boolean;
  reasoning: string;
  context: string;
  preset: string;
};
export type SavedControlDraft = {
  draft: ControlDraft;
  baseline: string;
  contextBaseline: string;
};
export function controlsKey(
  chat?: string,
  connection?: string,
  model?: string,
  defaultsOnly = false,
) {
  return `${defaultsOnly ? "defaults" : (chat ?? "new")}:${connection}:${model}`;
}
export const useControlDrafts = create<{
  drafts: Record<string, SavedControlDraft>;
  keep: (key: string, value?: SavedControlDraft) => void;
}>((set) => ({
  drafts: {},
  keep: (key, value) =>
    set((state) => {
      const drafts = { ...state.drafts };
      if (value) drafts[key] = value;
      else delete drafts[key];
      return { drafts };
    }),
}));
