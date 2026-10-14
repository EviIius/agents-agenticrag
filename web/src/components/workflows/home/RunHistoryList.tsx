import { useInfiniteQuery, useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Choice } from "../studio/fields";
import { useGraphRuns } from "../studio/useGraphRuns";
import type { Definition, RunPage } from "../studio/types";
import { RunsList } from "./WorkflowsHome";
export function RunHistoryList() {
  const [definition, setDefinition] = useState("all"),
    [state, setState] = useState("all");
  const defs = useQuery({
    queryKey: ["workflow-definitions"],
    queryFn: () => api<Definition[]>("/workflows/defs"),
  });
  const q = useInfiniteQuery({
    queryKey: ["workflow-history", definition, state],
    initialPageParam: "",
    queryFn: ({ pageParam }) => {
      const params = new URLSearchParams({ limit: "50" });
      if (definition !== "all") params.set("def_id", definition);
      if (state !== "all") params.set("state", state);
      if (pageParam) params.set("cursor", pageParam);
      return api<RunPage>(`/workflows/runs?${params}`);
    },
    getNextPageParam: (page) => page.next_cursor ?? undefined,
  });
  const { runs, error, connection } = useGraphRuns();
  const saved = q.data?.pages.flatMap((page) => page.items) ?? [];
  const merged = [
    ...saved.map((run) => runs.find((r) => r.id === run.id) ?? run),
    ...runs.filter((run) => !saved.some((r) => r.id === run.id)),
  ]
    .filter(
      (run) =>
        run.mode !== "test" &&
        (definition === "all" || run.def_id === definition) &&
        (state === "all" || run.state === state),
    )
    .sort((a, b) => b.created_at.localeCompare(a.created_at));
  return (
    <section className="wf-home" aria-label="Workflow runs">
      <header className="wf-home-header">
        <h1>Workflow runs</h1>
      </header>
      <div className="mb-6 flex flex-wrap gap-4">
        <Choice
          label="Workflow"
          value={definition}
          onChange={setDefinition}
          choices={[
            { value: "all", label: "All workflows" },
            ...(defs.data ?? []).map((def) => ({
              value: def.id,
              label: def.name,
            })),
          ]}
        />
        <Choice
          label="Run state"
          value={state}
          onChange={setState}
          choices={[
            { value: "all", label: "All states" },
            ...[
              "queued",
              "running",
              "paused",
              "complete",
              "failed",
              "interrupted",
              "cancelled",
            ].map((value) => ({
              value,
              label: value === "paused" ? "Waiting for you" : value,
            })),
          ]}
        />
      </div>
      {connection !== "Connected" && (
        <p role="status" className="wf-help">
          {connection}
        </p>
      )}
      {(q.isError || error) && (
        <p role="alert">
          {error || "Runs couldn't be loaded."}
          <Button onClick={() => void q.refetch()}>Try again</Button>
        </p>
      )}
      {q.isPending ? (
        <p role="status">Loading runs…</p>
      ) : (
        <RunsList runs={merged} />
      )}
      {q.hasNextPage && (
        <Button
          className="mt-6"
          disabled={q.isFetchingNextPage}
          onClick={() => void q.fetchNextPage()}
        >
          {q.isFetchingNextPage ? "Loading…" : "Load more runs"}
        </Button>
      )}
    </section>
  );
}
