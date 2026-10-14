import { useState } from "react";
import { Button } from "@/components/ui/button";
import { WorkflowHomeContent } from "@/components/workflows/home/WorkflowsHome";
import cases from "../../../shared/workflow_graph_cases.json";
import type {
  Definition,
  Doc,
  Run,
  Template,
} from "@/components/workflows/studio/types";
import {
  WorkflowStatus,
  WorkflowRunUnavailable,
} from "@/components/workflows/WorkflowStatus";
import { useUI } from "@/stores/ui";

export default function WorkflowHomePreview() {
  const [state, setState] = useState("populated");
  const ui = useUI();
  const definitions: Definition[] = cases.slice(0, 2).map((c, i) => ({
    id: "synthetic-home-" + i,
    name: i ? "Recording to meeting pack" : "Brief to images",
    description: "Synthetic editable workflow",
    icon: i ? "audio" : "image",
    graph: c.graph as Doc,
    version: 1,
    template_id: null,
    graph_hash: "fake",
    archived_at: null,
    created_at: "2026-10-12",
    updated_at: "2026-10-12",
  }));
  const templates: Template[] = definitions.map((d, i) => ({
    id: i ? "meeting_pack" : "brief_images",
    name: d.name,
    description: d.description,
    icon: i ? "audio" : "image",
    graph: d.graph,
  }));
  const runs = [
    "paused",
    "running",
    "queued",
    "complete",
    "failed",
    "interrupted",
    "cancelled",
    "cancelling",
  ].map(
    (status, i) =>
      ({
        id: "fake-home-run-" + i,
        def_name: definitions[i % 2].name,
        state: status,
        stage: "Synthetic saved run",
        created_at: "2026-10-12T12:00:00Z",
        updated_at: "2026-10-12T12:01:00Z",
        def_id: definitions[i % 2].id,
      }) as Run,
  );
  return (
    <div className="mx-auto max-w-[1120px] space-y-6 p-4 lg:p-8">
      <p className="text-sm text-fg-3">Workflows home · synthetic states</p>
      <div className="flex flex-wrap gap-2">
        {["light", "dark"].map((theme) => (
          <Button
            key={theme}
            onClick={() => ui.set({ theme: theme as "light" | "dark" })}
          >
            {theme}
          </Button>
        ))}
        {[
          "empty",
          "loading",
          "populated",
          "error",
          "reconnecting",
          "run-loading",
          "run-unavailable",
        ].map((value) => (
          <Button
            key={value}
            variant={value === state ? "default" : "outline"}
            onClick={() => setState(value)}
          >
            {value}
          </Button>
        ))}
      </div>
      <WorkflowStatus
        connection={
          state === "reconnecting"
            ? "Reconnecting — accepted work continues on your Mac"
            : "Connected"
        }
        notice={
          state === "error" ? "Saved runs could not be loaded." : undefined
        }
        retry={() => setState("populated")}
      />
      {state.startsWith("run-") ? (
        <WorkflowRunUnavailable failed={state === "run-unavailable"} />
      ) : (
        <WorkflowHomeContent
          definitions={{
            data: state === "populated" ? definitions : [],
            isLoading: state === "loading",
            isError: state === "error",
            refetch: () => setState("populated"),
          }}
          templates={{ data: templates }}
          runs={state === "populated" ? runs : []}
          connection="Connected"
          error=""
          notice=""
          setNotice={() => {}}
          busy={false}
          create={async () => {}}
          refresh={() => {}}
        />
      )}
    </div>
  );
}
