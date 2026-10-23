import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Composer } from "@/components/chat/Composer";
import ImageTurn from "@/components/chat/ImageTurn";
import type { Message } from "@/lib/api";
import type { ImageComposerCommand } from "@/lib/composer-drafts";
import type { ImageJob } from "@/lib/image-events";
import { useUI } from "@/stores/ui";

export const frameStates = [
  "queued",
  "preparing",
  "making-room",
  "step 0",
  "step 1",
  "step 2",
  "step 3",
  "step 4",
  "decoding",
  "complete",
  "cancelling",
  "cancelled",
  "failed",
  "interrupted",
  "removed",
];
export default function ChatImagesPreview() {
  const [state, setState] = useState("step 2"),
    [count, setCount] = useState(2);
  const [command, setCommand] = useState<ImageComposerCommand>();
  const ui = useUI();
  const jobs: ImageJob[] = Array.from({ length: count }, (_, i) => ({
    id: String(i + 1).repeat(32),
    prompt: "Synthetic cobalt harbor with warm paper lanterns.",
    seed: 42 + i,
    mode: "generate",
    width: 1024,
    height: 1024,
    export_bytes: 0,
    state:
      state.startsWith("step") || state === "decoding"
        ? "running"
        : state === "removed"
          ? "complete"
          : state === "making-room"
            ? "preparing"
            : (state as ImageJob["state"]),
    stage:
      state === "making-room"
        ? "Making room for images"
        : state === "decoding"
          ? "Decoding image"
          : "Generating image",
    completed_steps: state.startsWith("step")
      ? Number(state.slice(-1))
      : ["complete", "decoding"].includes(state)
        ? 4
        : 0,
    steps: 4,
    created_at: "2026-10-13T15:00:00Z",
    updated_at: "2026-10-13T15:00:20Z",
    image_bytes: state === "complete" ? 1114190 : 0,
    metadata_bytes: state === "complete" ? 1400 : 0,
    error:
      state === "failed"
        ? "Synthetic worker failure. Retry is available."
        : null,
  }));
  const user: Message = {
    id: "synthetic-image-user",
    chat_id: "design",
    role: "user",
    content: jobs[0].prompt,
    kind: "image",
    status: "complete",
    created_at: jobs[0].created_at,
  };
  const reply: Message = {
    ...user,
    id: "synthetic-image-reply",
    parent_id: user.id,
    role: "assistant",
    content: "",
    images: jobs,
  };
  return (
    <main className="mx-auto max-w-5xl p-4">
      <h1 className="mb-4 text-xl font-semibold">
        Chat images · synthetic states
      </h1>
      <div className="mb-5 flex flex-wrap gap-2">
        {["light", "dark"].map((theme) => (
          <Button
            key={theme}
            onClick={() => ui.set({ theme: theme as "light" | "dark" })}
          >
            {theme}
          </Button>
        ))}
        <Button
          onClick={() =>
            ui.set({
              reduceMotion: ui.reduceMotion === "always" ? "system" : "always",
            })
          }
        >
          Reduce motion
        </Button>
        {[1, 2, 3].map((n) => (
          <Button
            key={n}
            aria-pressed={count === n}
            onClick={() => setCount(n)}
          >
            Preview {n} image{n > 1 ? "s" : ""}
          </Button>
        ))}
        {frameStates.map((value) => (
          <Button
            key={value}
            onClick={() => setState(value)}
            aria-pressed={state === value}
          >
            Preview {value}
          </Button>
        ))}
      </div>
      <section
        className="mx-auto max-w-[var(--thread-w)]"
        aria-label="Image conversation preview"
      >
        <div className="user-bubble ml-auto mb-5 w-fit">
          <p className="mb-1 text-xs text-fg-2">
            Image{count > 1 ? ` · ${count} images` : ""}
          </p>
          <p>{user.content}</p>
        </div>
        <ImageTurn
          key={`${state}-${count}`}
          message={reply}
          all={[user, reply]}
          preview
          vision
          onIteration={(job, action, position) => {
            if (action === "refine")
              setCommand({
                key: crypto.randomUUID(),
                mode: "image",
                refinement: { job, position },
              });
            else if (action === "ask")
              setCommand({ key: crypto.randomUUID(), mode: "chat" });
            else setState("queued");
          }}
          onBranch={() => {}}
          onAction={() => setState("queued")}
        />
        <div className="mt-6">
          <Composer
            images
            previewImages
            initialImageMode
            imageCommand={command}
          />
        </div>
      </section>
    </main>
  );
}
