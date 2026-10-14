import { useState } from "react";
import { RunInputs } from "@/components/workflows/studio/RunInputs";
import type { Doc } from "@/components/workflows/studio/types";
import { Button } from "@/components/ui/button";
import { useUI } from "@/stores/ui";
import {
  WorkflowList,
  type Workflow,
} from "@/components/workflows/WorkflowsPage";

const states = [
  "empty",
  "queued",
  "running",
  "paused",
  "complete",
  "failed",
  "cancelling",
  "cancelled",
  "interrupted",
  "cleanup-failed",
  "meeting-running",
  "meeting-complete",
  "uploading",
  "upload-failed",
];
export default function WorkflowsPreview() {
  const [state, setState] = useState("paused");
  const ui = useUI();
  const meeting = [
    "cleanup-failed",
    "meeting-running",
    "meeting-complete",
  ].includes(state);
  const status =
    state === "meeting-complete"
      ? "complete"
      : state === "meeting-running"
        ? "running"
        : state;
  const run: Workflow = {
    id: "b".repeat(32),
    version: 1,
    input: {
      request_key: "synthetic-workflow",
      template: meeting ? "meeting_pack" : "brief_images",
      model: { connection_id: "fake", model_id: "fake-chat", params: {} },
      brief: meeting ? "" : "Synthetic blue circle",
      attachment_id: meeting ? "synthetic" : null,
      cleanup_model: meeting
        ? { connection_id: "fake", model_id: "fake-chat", params: {} }
        : null,
      review_prompt: true,
      seeds: [42],
    },
    state: state === "cleanup-failed" ? "failed" : status,
    stage:
      state === "paused"
        ? "Review the image prompt"
        : state === "cleanup-failed"
          ? "Guarded clean-up rejected"
          : state,
    source_available: meeting,
    error:
      state === "failed" || state === "cleanup-failed"
        ? "Synthetic failure — earlier outputs are saved."
        : null,
    created_at: "2026-10-12T12:00:00Z",
    updated_at: "2026-10-12T12:01:00Z",
    edited_prompt: null,
    steps: [
      {
        position: 0,
        kind: meeting ? "transcribe" : "prompt",
        label: meeting ? "Save original transcript" : "Draft image prompt",
        state:
          state === "queued"
            ? "pending"
            : state === "running"
              ? "running"
              : "complete",
        attempt: state === "queued" ? 0 : 1,
        output: {
          text: meeting
            ? "Original transcript saved"
            : "Fake runtime: one blue circle on a white background.",
        },
        error: null,
      },
      {
        position: 1,
        kind:
          state === "cleanup-failed" ? "cleanup" : meeting ? "pack" : "image",
        label:
          state === "cleanup-failed"
            ? "Guarded transcript clean-up"
            : meeting
              ? "Draft meeting pack"
              : "Generate image 1",
        state:
          status === "complete"
            ? "complete"
            : state === "failed" || state === "cleanup-failed"
              ? "failed"
              : state === "meeting-running"
                ? "running"
                : "pending",
        attempt: 1,
        output:
          state === "meeting-complete" || state === "meeting-running"
            ? {
                text: "Fake runtime draft\n\nSummary: the team discussed a cover.\nDecisions: blue cover.\nAction items: review budget; owner and due date not stated.\nUnclear or unstated: no logo decision.",
              }
            : state === "complete"
              ? { image_job_id: "a".repeat(32), sha256: "a".repeat(64) }
              : null,
        error: null,
      },
    ],
  };
  return (
    <div className="p-4">
      <h1 className="mb-4 text-xl font-semibold">
        Workflows · synthetic states
      </h1>
      <div className="mb-4 flex flex-wrap gap-2">
        {["light", "dark"].map((theme) => (
          <Button
            key={theme}
            onClick={() => ui.set({ theme: theme as "light" | "dark" })}
          >
            {theme}
          </Button>
        ))}
        {states.map((value) => (
          <Button
            key={value}
            variant={state === value ? "default" : "outline"}
            onClick={() => setState(value)}
          >
            {value}
          </Button>
        ))}
      </div>
      <RunInputs
        preview
        defId="fake"
        beforeRun={async () => true}
        accepted={() => {}}
        doc={
          {
            schema: "atelier.workflow/1",
            nodes: [
              {
                id: "n_start",
                key: "start",
                kind: "start",
                title: "Start",
                position: { x: 0, y: 0 },
                disabled: false,
                config: {
                  fields: [
                    {
                      name: "brief",
                      label: "Synthetic input",
                      type: "long_text",
                      required: false,
                      default: "",
                      help: "Fake runtime preview",
                      choices: [],
                    },
                  ],
                },
              },
            ],
            edges: [],
            notes: [],
            viewport: null,
            settings: { default_model: null, keep_test_runs_days: 7 },
          } satisfies Doc
        }
      />
      {state === "upload-failed" && (
        <p role="status">Fake upload interrupted. Try the recording again.</p>
      )}
      <WorkflowList
        preview
        runs={
          ["empty", "uploading", "upload-failed"].includes(state) ? [] : [run]
        }
      />
    </div>
  );
}
