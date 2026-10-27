import { useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { Composer } from "@/components/chat/Composer";
import { LiveThread } from "@/components/chat/LiveThread";
import { LiveChatSettings } from "@/components/settings/LiveChatSettings";
import { ModelPicker } from "@/components/app/ModelPicker";
import { fixtureModels } from "./ProductionFixtures";
import { useUI } from "@/stores/ui";
import type { ImageJob } from "@/lib/image-events";
import type { Message } from "@/lib/api";
const date = "2026-10-25T12:00:00Z";
const model = {
  ...fixtureModels[0],
  model_id: "qwen3.8:27b-atelier-eval-32k",
  display_name: "qwen3.8:27b-atelier-eval-32k",
  family: "synthetic-family",
  reasoning: { options: ["off", "low", "medium", "xhigh"] },
};
const job: ImageJob = {
  id: "a".repeat(32),
  mode: "edit",
  state: "complete",
  prompt: "Add a hat to the synthetic reference",
  seed: 42,
  steps: 4,
  completed_steps: 4,
  stage: "Done",
  created_at: date,
  updated_at: date,
  image_bytes: 1200,
  metadata_bytes: 10,
  export_bytes: 0,
  reference: {
    id: "b".repeat(32),
    chat_id: "design",
    available: true,
    original_bytes: 1200,
    working_bytes: 1000,
    width: 512,
    height: 512,
    original_format: "PNG",
    created_at: date,
  },
};
export default function ChatStatePreview() {
  const ui = useUI(),
    scroll = useRef<HTMLDivElement>(null);
  const [state, setState] = useState(
    new URLSearchParams(location.search).get("state") ?? "thread",
  );
  const [action, setAction] = useState("");
  const [think, setThink] = useState<string>();
  const base: Message = {
    id: "one",
    chat_id: "design",
    role: "user",
    content: "Add a hat to the synthetic reference",
    status: "complete",
    created_at: date,
  };
  const rows: Message[] = [
    { ...base, id: "image-user", kind: "image" },
    {
      ...base,
      id: "image-reply",
      parent_id: "image-user",
      role: "assistant",
      kind: "image",
      content: "",
      images: [
        {
          ...job,
          reference: { ...job.reference!, available: state !== "cleared" },
        },
      ],
    },
    {
      ...base,
      id: "create-user",
      parent_id: "image-reply",
      kind: "image",
      content: "Create a different synthetic scene",
    },
    {
      ...base,
      id: "create-reply",
      parent_id: "create-user",
      role: "assistant",
      kind: "image",
      content: "",
      images: [
        { ...job, id: "c".repeat(32), mode: "generate", reference: null },
      ],
    },
    {
      ...base,
      id: "stop-user",
      parent_id: "create-reply",
      kind: "text",
      content: "Explain the synthetic example",
    },
    {
      ...base,
      id: "stopped",
      parent_id: "stop-user",
      role: "assistant",
      model,
      content: "I'd begin by",
      status: "stopped",
    },
    {
      ...base,
      id: "empty",
      parent_id: "stopped",
      role: "assistant",
      model,
      content: "",
      reasoning: "Synthetic reasoning without an answer",
    },
  ];
  return (
    <main className="design-page">
      <h1 className="mb-3 text-xl">Part B · synthetic chat states</h1>
      <p className="mb-4 text-sm text-fg-2">
        Invented data only. Preview actions make no model calls.
      </p>
      <div className="mb-5 flex flex-wrap gap-2">
        <Button variant="outline" onClick={() => ui.set({ palette: "aero" })}>
          Aero
        </Button>
        {["light", "dark"].map((theme) => (
          <Button
            key={theme}
            variant="outline"
            onClick={() => ui.set({ theme: theme as "light" | "dark" })}
          >
            {theme}
          </Button>
        ))}
        {[
          "thread",
          "cleared",
          "controls",
          "image-controls",
          "followup",
          "variants",
          "starters",
        ].map((value) => (
          <Button
            key={value}
            variant="outline"
            aria-pressed={state === value}
            onClick={() => setState(value)}
          >
            {value}
          </Button>
        ))}
      </div>
      <p role="status" className="mb-3 text-sm">
        {action}
      </p>
      {["thread", "cleared"].includes(state) && (
        <div className="flex h-[650px] min-h-0 flex-col">
          <LiveThread
            imagePreview
            messages={rows}
            all={rows}
            scrollRef={scroll}
            onAboveBottomChange={() => {}}
            onRegenerate={() => setAction("Retry requested · preview only")}
            onContinue={() => setAction("Continue requested · preview only")}
            onEdit={async () => false}
            onBranch={() => {}}
          />
        </div>
      )}
      {["controls", "image-controls"].includes(state) && (
        <div className="max-w-md rounded-xl border border-line bg-surface">
          <LiveChatSettings
            key={state}
            model={model}
            imageOnly={state === "image-controls"}
            queryScope={["part-b-design"]}
            request={async <T,>() => [] as T}
            onSave={() => setAction("Chat settings saved · preview only")}
            onDefaults={() => setAction("Model defaults saved · preview only")}
            onContext={() => setAction("Context saved · preview only")}
          />
        </div>
      )}
      {state === "followup" && (
        <Composer
          images
          previewImages
          initialImageMode
          followupJob={job}
          model={model}
          onImageSend={async () => {
            setAction("Image requested · preview only");
            return true;
          }}
        />
      )}
      {state === "starters" && (
        <Composer
          suggestions
          images
          previewImages
          model={model}
          thinkValue={think}
          onThinkChange={(value) => {
            setThink(value ?? undefined);
            setAction(`Thinking value: ${value ?? "default"} · preview only`);
          }}
          imageStatus={{
            available: true,
            editing_available: true,
            model: "FLUX.2 klein 4B",
            width: 1024,
            height: 1024,
            steps: 4,
            quantization: 8,
            cache_limit_bytes: 1073741824,
          }}
          transcriptionReady
          audioExtensions={[".wav"]}
          onAttach={() => {
            setAction("Files chosen · preview only");
          }}
          onPhotoFile={() => setAction("Photo chosen · preview only")}
          recentPrompts={[
            "Plan a synthetic workshop.",
            "Compare two invented options.",
          ]}
          libraryControl={{
            enabled: false,
            onToggle: () => setAction("Library chosen · preview only"),
            scope: null,
            onScope: () => {},
            collections: [],
          }}
        />
      )}
      {state === "variants" && (
        <ModelPicker
          current={model}
          models={[
            model,
            {
              ...model,
              model_id: "synthetic-other",
              display_name: "Synthetic 16K variant",
              context_length: 16384,
              vision: true,
            },
            {
              ...model,
              family: "other-family",
              model_id: "other",
              display_name: "Synthetic second family",
            },
          ]}
          onChoose={() => setAction("Model selected · preview only")}
        />
      )}
    </main>
  );
}
