import { create } from "zustand";
export type ActiveWorkflow = {
  id: string;
  name: string;
  defId: string | null;
  state: string;
};
export const useWorkflowActivity = create<{
  active: ActiveWorkflow[];
  pausedCount: number;
  set: (active: ActiveWorkflow[], pausedCount: number) => void;
}>((set) => ({
  active: [],
  pausedCount: 0,
  set: (active, pausedCount) => set({ active, pausedCount }),
}));
