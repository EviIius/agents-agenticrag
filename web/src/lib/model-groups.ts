import type { Model } from "./api";

/** Runtime family metadata groups presentation only; each variant retains its capabilities. */
export function modelRows(
  models: Model[],
  current?: Model,
  expanded: string[] = [],
  searching = false,
) {
  const groups = new Map<string, Model[]>();
  for (const model of models) {
    const key = JSON.stringify([
      model.connection_id,
      model.family || model.model_id,
    ]);
    groups.set(key, [...(groups.get(key) ?? []), model]);
  }
  return [...groups].flatMap(([key, variants]) => {
    const primary =
      variants.find(
        (model) =>
          model.connection_id === current?.connection_id &&
          model.model_id === current.model_id,
      ) ??
      variants.find((model) => model.loaded) ??
      variants[0];
    const rows =
      searching || expanded.includes(key)
        ? [primary, ...variants.filter((model) => model !== primary)]
        : [primary];
    return rows.map((model) => ({
      model,
      key,
      count: variants.length,
      primary: model === primary,
    }));
  });
}
