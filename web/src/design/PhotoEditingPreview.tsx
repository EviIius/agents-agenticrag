import { useState } from "react";
import { Composer } from "@/components/chat/Composer";
import ImageTurn from "@/components/chat/ImageTurn";
import { Button } from "@/components/ui/button";
import type {
  PhotoDraft,
  PhotoEditor,
  PhotoSelection,
} from "@/hooks/usePhotoEdit";
import type { ImageJob } from "@/lib/image-events";
import type { Message } from "@/lib/api";
import { useUI } from "@/stores/ui";

import { photoStates } from "@/lib/photo-edit-states";
export default function PhotoEditingPreview() {
  const [state, setState] = useState(
    new URLSearchParams(location.search).get("state") ?? "ready",
  );
  const [text, setText] = useState(
    "Change the synthetic background to cobalt.",
  );
  const [active, setActive] = useState(true);
  const [selection, setSelection] = useState<PhotoSelection>();
  const ui = useUI();
  const ref = {
    id: "c".repeat(32),
    chat_id: "d".repeat(32),
    available: state !== "unavailable-reference",
    original_bytes: 2000,
    working_bytes: 1800,
    width: 720,
    height: 900,
    original_format: "PNG",
    created_at: "2026-10-20T12:00:00Z",
  };
  const draft: PhotoDraft = {
    active,
    text,
    version: 1,
    input: {
      token: "fake",
      reference: ref,
      selection:
        selection ??
        (state.startsWith("selection") && state !== "selection-load-error"
          ? {
              version: 1,
              strokes: [
                { radius: 0.15, points: [[0.5, 0.3]] },
                ...(state === "selection-protected" ||
                state === "selection-empty"
                  ? [
                      {
                        operation: "erase" as const,
                        radius: state === "selection-empty" ? 0.15 : 0.06,
                        points: [[0.5, 0.3] as [number, number]],
                      },
                    ]
                  : []),
              ],
            }
          : undefined),
      phase:
        state === "preparing"
          ? "preparing"
          : state === "upload-error"
            ? "error"
            : state === "unavailable-reference"
              ? "unavailable"
              : "ready",
      error:
        state === "upload-error"
          ? "Synthetic connection failure. Retry this photo."
          : undefined,
    },
  };
  const editor: PhotoEditor = {
    key: "design-photo",
    draft,
    previewURL:
      state === "selection-load-error"
        ? "/synthetic-missing-photo.png"
        : "/icons/apple-touch-icon.png",
    setText,
    setActive,
    setSelection,
    attach: async () => {
      setActive(true);
      setState("ready");
    },
    remove: () => setState("unavailable-reference"),
    retry: () => setState("ready"),
    previewLoaded: () => {},
    submission: () => ({
      reference: ref,
      accepted: () => {},
      rejected: () => {},
    }),
  };
  const job: ImageJob = {
    id: "a".repeat(32),
    mode: "edit",
    width: 720,
    height: 900,
    prompt: text,
    seed: 42,
    reference: ref,
    export_bytes: 1200,
    state:
      state === "running"
        ? "running"
        : state === "cancelled"
          ? "cancelled"
          : "complete",
    stage: "Generating image",
    completed_steps: state === "running" ? 2 : 4,
    steps: 4,
    created_at: ref.created_at,
    updated_at: ref.created_at,
    image_bytes: state === "running" || state === "cancelled" ? 0 : 1500,
    metadata_bytes: 100,
  };
  const reply: Message = {
    id: "synthetic-photo-reply",
    chat_id: "design",
    role: "assistant",
    kind: "image",
    content: "",
    status: "complete",
    created_at: ref.created_at,
    images: [job],
  };
  return (
    <main className="mx-auto max-w-5xl p-4">
      <h1 className="mb-4 text-xl font-semibold">
        Photo editing · synthetic states
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
        {photoStates.map((value) => (
          <Button
            key={value}
            aria-pressed={state === value}
            onClick={() => {
              setState(value);
              setActive(true);
            }}
          >
            Preview {value}
          </Button>
        ))}
      </div>
      <section
        className="mx-auto max-w-[var(--thread-w)]"
        aria-label="Photo editing preview"
      >
        {[
          "running",
          "cancelled",
          "complete",
          "comparison",
          "unavailable-reference",
        ].includes(state) && (
          <ImageTurn
            message={reply}
            all={[reply]}
            preview
            onBranch={() => {}}
            onAction={() => setState("running")}
          />
        )}
        <div className="mt-6">
          <Composer
            images
            previewImages
            photoEdit={editor}
            onPhotoFile={() => setState("ready")}
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
            error={
              state === "rejected-send"
                ? "Synthetic rejected send. Your photo and instruction are kept."
                : undefined
            }
            onImageSend={async () => {
              setState("running");
              return false;
            }}
          />
        </div>
      </section>
    </main>
  );
}
