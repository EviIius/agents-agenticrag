import { useState } from "react";
import { Button } from "@/components/ui/button";
import { WorkflowHome } from "@/components/workflows/WorkflowHome";
import type { Workflow } from "@/components/workflows/WorkflowsPage";
import {
  WorkflowStatus,
  WorkflowRunUnavailable,
} from "@/components/workflows/WorkflowStatus";
import { useUI } from "@/stores/ui";

export default function WorkflowHomePreview() {
  const [state, setState] = useState("populated");
  const ui = useUI();
  const runs: Workflow[] = [
    "paused",
    "running",
    "queued",
    "complete",
    "failed",
    "interrupted",
    "cancelled",
    "cancelling",
  ].map((status, index) => ({
    id: `fake-home-run-${index}`,
    version: 1,
    input: {
      request_key: `fake-home-${index}`,
      template: index % 2 ? "brief_images" : "meeting_pack",
      model: { connection_id: "fake", model_id: "fake-chat", params: {} },
      brief: "Synthetic brief",
      attachment_id: null,
      cleanup_model: null,
      review_prompt: true,
      seeds: [42],
    },
    state: status,
    stage: status === "paused" ? "Review the image prompt" : status,
    steps: [],
    source_available: false,
    error: null,
    edited_prompt: null,
    created_at: "2026-10-12T12:00:00Z",
    updated_at: "2026-10-12T12:01:00Z",
  }));
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
        <WorkflowHome
          runs={state === "populated" ? runs : []}
          loading={state === "loading"}
        />
      )}
    </div>
  );
}
