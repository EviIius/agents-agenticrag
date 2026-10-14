import type { components } from "@/lib/api-types";
// Pydantic response documents include defaults. OpenAPI marks defaults optional
// for requests; derive a filled response view, keeping sampling keys optional.
type Filled<T> = T extends (infer V)[]
  ? Filled<V>[]
  : T extends object
    ? {
        [K in keyof T]-?: K extends "params"
          ? NonNullable<T[K]>
          : Filled<Exclude<T[K], undefined>>;
      }
    : T;
export type Doc = Filled<components["schemas"]["GraphDoc"]>;
export type Block = Doc["nodes"][number];
export type Kind = Block["kind"];
export type Edge = Doc["edges"][number];
export type Note = Doc["notes"][number];
export type Definition = Omit<components["schemas"]["Definition"], "graph"> & {
  graph: Doc;
};
export type Draft = Pick<Definition, "name" | "description" | "icon" | "graph">;
export type Issue = components["schemas"]["Issue"];
export type Catalog = components["schemas"]["BlockCatalog"];
export type Template = Omit<components["schemas"]["Template"], "graph"> & {
  graph: Doc;
};
export type Run = Omit<components["schemas"]["RunV2"], "graph"> & {
  graph: Doc;
};
export type RunPage = Omit<components["schemas"]["RunPage"], "items"> & {
  items: Run[];
};
export type ModelChoice =
  components["schemas"]["ModelRef"] | "workflow_default";
export type Point = { x: number; y: number };
