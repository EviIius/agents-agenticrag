import { createContext, useContext } from "react";
import { createStore } from "zustand/vanilla";
import { useStore } from "zustand";
import type { Block, Definition, Draft, Point } from "./types";
import { clone, remove, renameKey } from "./graph";
type History = { before: Draft; after: Draft; group?: string; time: number };
export type SaveState = "saved" | "saving" | "failed" | "conflict";
type State = {
  id: string;
  version: number;
  draft: Draft;
  saved: string;
  revision: number;
  selection: string[];
  past: History[];
  future: History[];
  dragging?: Draft;
  saveState: SaveState;
  conflict?: Definition;
  edit: (change: (draft: Draft) => Draft, group?: string) => void;
  block: (id: string, change: (block: Block) => Block, group?: string) => void;
  select: (ids: string[]) => void;
  undo: () => void;
  redo: () => void;
  beginDrag: () => void;
  drag: (positions: Record<string, Point>) => void;
  endDrag: () => void;
  remove: () => void;
  rename: (old: string, next: string) => void;
  loaded: (definition: Definition) => void;
  accepted: (definition: Definition, sent: Draft) => void;
  status: (state: SaveState, conflict?: Definition) => void;
};
export const asDraft = (d: Definition): Draft => ({
  name: d.name,
  description: d.description,
  icon: d.icon,
  graph: d.graph,
});
export function createStudioStore(definition: Definition) {
  return createStore<State>((set, get) => ({
    id: definition.id,
    version: definition.version,
    draft: clone(asDraft(definition)),
    saved: JSON.stringify(asDraft(definition)),
    revision: 0,
    selection: [],
    past: [],
    future: [],
    saveState: "saved",
    edit(change, group) {
      const s = get(),
        next = change(clone(s.draft));
      if (JSON.stringify(next) === JSON.stringify(s.draft)) return;
      const last = s.past.at(-1);
      const time = Date.now();
      const past =
        group && last?.group === group && time - last.time < 600
          ? [...s.past.slice(0, -1), { ...last, after: clone(next), time }]
          : [
              ...s.past,
              { before: clone(s.draft), after: clone(next), group, time },
            ].slice(-100);
      set({
        draft: next,
        past,
        future: [],
        revision: s.revision + 1,
        saveState: s.saveState === "conflict" ? "conflict" : "saving",
      });
    },
    block(id, change, group) {
      get().edit(
        (d) => ({
          ...d,
          graph: {
            ...d.graph,
            nodes: d.graph.nodes.map((n) => (n.id === id ? change(n) : n)),
          },
        }),
        group,
      );
    },
    select: (selection) => set({ selection }),
    undo() {
      const s = get(),
        h = s.past.at(-1);
      if (!h) return;
      set({
        draft: clone(h.before),
        past: s.past.slice(0, -1),
        future: [...s.future, h],
        revision: s.revision + 1,
        saveState: s.saveState === "conflict" ? "conflict" : "saving",
      });
    },
    redo() {
      const s = get(),
        h = s.future.at(-1);
      if (!h) return;
      set({
        draft: clone(h.after),
        past: [...s.past, h],
        future: s.future.slice(0, -1),
        revision: s.revision + 1,
        saveState: s.saveState === "conflict" ? "conflict" : "saving",
      });
    },
    beginDrag() {
      set({ dragging: clone(get().draft) });
    },
    drag(positions) {
      const s = get();
      set({
        draft: {
          ...s.draft,
          graph: {
            ...s.draft.graph,
            nodes: s.draft.graph.nodes.map((n) =>
              positions[n.id] ? { ...n, position: positions[n.id] } : n,
            ),
            notes: s.draft.graph.notes.map((n) =>
              positions[n.id] ? { ...n, position: positions[n.id] } : n,
            ),
          },
        },
      });
    },
    endDrag() {
      const s = get(),
        after = s.draft,
        before = s.dragging;
      if (!before) return;
      set({ draft: before, dragging: undefined });
      get().edit(() => after);
    },
    remove() {
      const s = get();
      s.edit((d) => ({ ...d, graph: remove(d.graph, s.selection) }));
      set({ selection: [] });
    },
    rename(old, next) {
      get().edit((d) => ({ ...d, graph: renameKey(d.graph, old, next) }));
    },
    loaded(d) {
      set({
        version: d.version,
        draft: clone(asDraft(d)),
        saved: JSON.stringify(asDraft(d)),
        past: [],
        future: [],
        selection: [],
        conflict: undefined,
        saveState: "saved",
        revision: get().revision + 1,
      });
    },
    accepted(d, sent) {
      const s = get();
      const unchanged = JSON.stringify(s.draft) === JSON.stringify(sent);
      const saved = JSON.stringify(unchanged ? asDraft(d) : sent);
      set({
        version: d.version,
        ...(unchanged ? { draft: clone(asDraft(d)) } : {}),
        saved,
        conflict: undefined,
        saveState:
          JSON.stringify(s.draft) === JSON.stringify(sent) ? "saved" : "saving",
      });
    },
    status: (saveState, conflict) => set({ saveState, conflict }),
  }));
}
export type StudioStore = ReturnType<typeof createStudioStore>;
export const StudioContext = createContext<StudioStore | null>(null);
export function useStudio<T>(selector: (s: State) => T) {
  const store = useContext(StudioContext);
  if (!store) throw new Error("Studio provider is missing");
  return useStore(store, selector);
}
