import { create } from "zustand";
/** Presentation only: IDs originate from this session's send/edit/regenerate. */
export const useFreshRows = create<{
  ids: Record<string, true>;
  add: (id: string) => void;
  clear: (id: string) => void;
}>((set) => ({
  ids: {},
  add: (id) => {
    set((state) => ({ ids: { ...state.ids, [id]: true } }));
    setTimeout(() => useFreshRows.getState().clear(id), 400);
  },
  clear: (id) =>
    set((state) => {
      const ids = { ...state.ids };
      delete ids[id];
      return { ids };
    }),
}));
