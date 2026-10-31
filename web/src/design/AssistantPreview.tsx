import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  TaskCard,
  type DesktopTask,
} from "@/components/chat/assistant/TaskCard";
import type { components } from "@/lib/api-types";

const observation: components["schemas"]["DesktopObservation"] = {
  app_id: "fake.messages",
  app_name: "Fake Messages",
  window_id: "fake-window",
  revision: 1,
  frame: {
    bounds: { x: 0, y: 0, width: 800, height: 600 },
    scale: 2,
    capture_width: 1600,
    capture_height: 1200,
    crop: { x: 0, y: 0, width: 1600, height: 1200 },
    image_width: 800,
    image_height: 600,
  },
  elements: [],
  conversation: {
    id: "synthetic-thread",
    latest_id: "synthetic-incoming",
    incoming: "Can we meet at 3 pm?",
    participants: [
      {
        id: "synthetic-alex",
        name: "Alex (synthetic)",
        address: "alex@example.invalid",
      },
    ],
  },
};
const stages = {
  queued: "Queued",
  running: "Reading the fake window",
  awaiting_approval: "Review the fake reply",
  needs_input:
    "Choose the correct conversation in Messages, then start a new task.",
  complete: "Fake action complete",
  cancelled: "Stopped",
  failed: "Computer access is unavailable or revoked.",
  interrupted: "Interrupted. Review the app before starting another task.",
  outcome_unknown:
    "Could not confirm the action. Check the app before trying again.",
} as const;
export function previewTask(state: DesktopTask["state"]): DesktopTask {
  return {
    id: "synthetic-desktop",
    chat_id: "design",
    text: "Read the latest message from Alex and prepare a reply.",
    fixture: "messages",
    state,
    revision: 1,
    stage: stages[state],
    observation,
    approval:
      state === "awaiting_approval"
        ? {
            id: "synthetic-approval",
            expires_at: 9999999999,
            action: {
              kind: "send_reply",
              app_id: observation.app_id,
              window_id: observation.window_id,
              observation: "a".repeat(64),
              target_id: "synthetic-thread",
              text: "I can meet at 3 pm.",
              delta: 0,
            },
          }
        : null,
    steps: [{ label: "Read selected conversation", state: "complete" }],
    created_at: "2026-10-30",
    fake: true,
  };
}
export default function AssistantPreview() {
  const requested = new URLSearchParams(location.search).get("state") as
    DesktopTask["state"] | null;
  const [task, setTask] = useState(() =>
    previewTask(
      requested && requested in stages ? requested : "awaiting_approval",
    ),
  );
  const [saved, setSaved] = useState("");
  return (
    <div className="mx-auto max-w-3xl p-4">
      <h1 className="text-xl font-medium">Computer use · Fake desktop</h1>
      <p className="mt-2 text-sm text-fg-2">
        Synthetic design states. No apps, messages or models are accessed.
      </p>
      <div className="mt-4 flex flex-wrap gap-2" aria-label="Preview states">
        {Object.keys(stages).map((state) => (
          <Button
            key={state}
            className="min-h-11"
            variant={task.state === state ? "default" : "outline"}
            onClick={() => {
              setTask(previewTask(state as DesktopTask["state"]));
              setSaved("");
            }}
          >
            {state.replaceAll("_", " ")}
          </Button>
        ))}
      </div>
      <TaskCard
        task={task}
        onDecision={async (body) => {
          setSaved(body.text ?? "");
          setTask(previewTask("complete"));
        }}
        onStop={async () => setTask(previewTask("cancelled"))}
      />
      {saved && (
        <p role="status" className="break-words text-sm">
          Fake submitted text: {saved}
        </p>
      )}
    </div>
  );
}
