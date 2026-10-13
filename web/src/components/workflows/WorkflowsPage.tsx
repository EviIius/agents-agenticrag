import { useEffect, useRef, useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router";
import { api, type Model } from "@/lib/api";
import type { components } from "@/lib/api-types";
import { Button } from "@/components/ui/button";
import { useWorkspace } from "@/components/app/WorkspaceNavigation";
import { WorkflowsHome, RunsList } from "./home/WorkflowsHome";
import { useGraphRuns } from "./studio/useGraphRuns";
import { RunCard } from "./studio/RunCard";
import { WorkflowCard, type Workflow } from "./LegacyRun";
import type { Definition } from "./studio/types";
import { blankDoc } from "./studio/graph";
export { WorkflowList, WorkflowCard } from "./LegacyRun";
export type { Workflow } from "./LegacyRun";
export type Choice = Pick<
  Model,
  "connection_id" | "model_id" | "display_name" | "context_length"
> & { imageCompatible?: boolean };
export function WorkflowsPage() {
  const { pathname } = useLocation();
  return pathname === "/workflows/new" ? (
    <CreateWorkflow />
  ) : pathname === "/workflows" ? (
    <WorkflowsHome />
  ) : (
    <RunHistory />
  );
}
function CreateWorkflow() {
  const location = useLocation(),
    navigate = useNavigate(),
    navigation = useWorkspace();
  const promise = useRef<Promise<Definition> | undefined>(undefined);
  const [error, setError] = useState("");
  useEffect(() => {
    let mounted = true;
    if (!promise.current)
      promise.current = (async () => {
        const template = new URLSearchParams(location.search).get("template");
        const model =
          navigation.modelKey &&
          (await api<Model[]>("/models")).find(
            (m) => `${m.connection_id}/${m.model_id}` === navigation.modelKey,
          );
        return api<Definition>("/workflows/defs", {
          ...(template
            ? {
                template_id: template,
                name:
                  template === "meeting_pack"
                    ? "Recording to meeting pack"
                    : "Brief to images",
              }
            : { graph: blankDoc() }),
          ...(model
            ? {
                default_model: {
                  connection_id: model.connection_id,
                  model_id: model.model_id,
                },
              }
            : {}),
        });
      })();
    void promise.current.then(
      (def) => {
        if (mounted)
          navigate(`/workflows/${def.id}`, {
            replace: true,
            state: navigation,
          });
      },
      () => {
        if (mounted)
          setError(
            "This template couldn't be opened. Return to Workflows and try again.",
          );
      },
    );
    return () => {
      mounted = false;
    };
  }, [location.search, navigate, navigation]);
  return (
    <p role="status" className="p-6 text-sm text-fg-2">
      {error || "Creating your workflow…"}
    </p>
  );
}
function RunHistory() {
  const { runId } = useParams();
  const { runs, error } = useGraphRuns(runId);
  const [legacy, setLegacy] = useState<Workflow>();
  const run = runs.find((r) => r.id === runId);
  useEffect(() => {
    if (run?.kind !== "template") return;
    let mounted = true;
    void api<Workflow>(`/workflows/runs/${run.id}`).then((v) => {
      if (mounted) setLegacy(v);
    });
    return () => {
      mounted = false;
    };
  }, [run]);
  const act = async (
    id: string,
    operation: "cancel" | "resume",
    body?: components["schemas"]["WorkflowResume"],
  ) => {
    await api(
      `/workflows/runs/${id}/${operation}`,
      operation === "resume" ? (body ?? {}) : {},
      "POST",
    );
  };
  return (
    <section className="wf-home" aria-label="Workflow runs">
      <div>
        <h1 className="mb-6 text-2xl font-semibold">
          {runId ? "Workflow run" : "Workflow runs"}
        </h1>
        {error && (
          <p role="alert" className="text-danger">
            {error}
          </p>
        )}
        {runId ? (
          run ? (
            run.kind === "graph" ? (
              <RunCard run={run} />
            ) : legacy ? (
              <WorkflowCard run={legacy} preview={false} onAction={act} />
            ) : (
              <p role="status">Loading run…</p>
            )
          ) : (
            <p role="status">Loading run…</p>
          )
        ) : (
          <RunsList runs={runs} />
        )}
        <Button variant="ghost" asChild>
          <a href="/workflows">Workflows</a>
        </Button>
      </div>
    </section>
  );
}
