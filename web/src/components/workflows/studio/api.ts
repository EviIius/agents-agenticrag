import { useQuery } from "@tanstack/react-query";
import { api, type Model, type Bootstrap } from "@/lib/api";
import type { Catalog, Definition, Draft, Template, Run } from "./types";
import type { components } from "@/lib/api-types";
export function useResources() {
  const catalog = useQuery({
    queryKey: ["workflow-blocks"],
    queryFn: () => api<Catalog>("/workflows/blocks"),
  });
  const models = useQuery({
    queryKey: ["models"],
    queryFn: () => api<Model[]>("/models"),
  });
  const bootstrap = useQuery({
    queryKey: ["bootstrap"],
    queryFn: () => api<Bootstrap>("/bootstrap"),
  });
  const compatible = useQuery({
    queryKey: ["workflow-image-models"],
    queryFn: () =>
      api<components["schemas"]["WorkflowModel"][]>("/workflows/image-models"),
  });
  return {
    catalog: catalog.data,
    models: models.data ?? [],
    connections: bootstrap.data?.connections ?? [],
    compatible: compatible.data ?? [],
    loading: catalog.isLoading || models.isLoading,
    error: catalog.isError || models.isError,
  };
}
export class ConflictError extends Error {
  constructor(public current: Definition) {
    super("This workflow changed on another device.");
  }
}
export async function saveDefinition(
  id: string,
  draft: Draft,
  version: number,
  force = false,
): Promise<Definition> {
  const response = await fetch(`/api/workflows/defs/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ...draft, version, force }),
  });
  const value = await response.json();
  if (response.status === 409)
    throw new ConflictError(
      (
        value as Omit<components["schemas"]["DefConflict"], "current"> & {
          current: Definition;
        }
      ).current,
    );
  if (!response.ok)
    throw new Error(
      "Couldn't save. Check your connection and workflow settings, then retry.",
    );
  return value as Definition;
}
export const getTemplates = () => api<Template[]>("/workflows/templates");
export const getDefinitions = () => api<Definition[]>("/workflows/defs");
export const getRun = (id: string) => api<Run>(`/workflows/runs/${id}/v2`);
