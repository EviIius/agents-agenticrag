import { useState } from "react";
import { ImagesView } from "@/components/images/ImagesPage";
import { Button } from "@/components/ui/button";
import type { components } from "@/lib/api-types";
import { useUI } from "@/stores/ui";
import { Composer } from "@/components/chat/Composer";
const states = [
  "empty",
  "unavailable",
  "queued",
  "preparing",
  "making-room",
  "running",
  "cancelling",
  "cancelled",
  "complete",
  "failed",
  "interrupted",
  "removed",
] as const;
export default function ImagesPreview() {
  const [state, setState] = useState<(typeof states)[number]>("complete");
  const ui = useUI();
  const job: components["schemas"]["ImageJob"] = {
    id: "a".repeat(32),
    prompt: "Synthetic blue geometric circle on a cream background.",
    seed: 42,
    mode: "generate",
    width: 1024,
    height: 1024,
    export_bytes: 0,
    state:
      state === "removed" || state === "empty" || state === "unavailable"
        ? "complete"
        : state === "making-room"
          ? "preparing"
          : state,
    stage:
      state === "running"
        ? "Generating image"
        : state === "making-room"
          ? "Making room for images"
          : state === "preparing"
            ? "Initializing image model"
            : state === "complete"
              ? "Image saved"
              : state === "queued"
                ? "Waiting for capacity"
                : state,
    completed_steps: state === "complete" ? 4 : 2,
    steps: 4,
    created_at: "2026-10-10T15:00:00Z",
    updated_at: "2026-10-10T15:01:00Z",
    image_bytes: state === "complete" ? 1114190 : 0,
    metadata_bytes: state === "complete" ? 1400 : 0,
    error:
      state === "failed"
        ? "Synthetic failure: retry is available. No output was accepted."
        : null,
    sha256: state === "complete" ? "a".repeat(64) : null,
  };
  return (
    <div className="p-4">
      <h1 className="mb-4 text-xl font-semibold">Images · synthetic states</h1>
      <div className="mb-4 flex flex-wrap gap-2">
        <Button onClick={() => ui.set({ theme: "light" })}>light</Button>
        <Button onClick={() => ui.set({ theme: "dark" })}>dark</Button>
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
      <ImagesView
        key={state}
        preview
        jobs={state === "empty" || state === "unavailable" ? [] : [job]}
        status={{
          available: state !== "unavailable",
          editing_available: false,
          reason: "The local image worker is not installed.",
          model: "FLUX.2 klein 4B",
          width: 1024,
          height: 1024,
          steps: 4,
          quantization: 8,
          cache_limit_bytes: 1073741824,
        }}
        storage={{
          outputs: job.image_bytes ? 1 : 0,
          versions: 0,
          image_bytes: job.image_bytes,
          metadata_bytes: job.metadata_bytes,
          manifest_bytes: 120,
          database_bytes: 8192,
          backup_bytes: 1115590,
          free_bytes: 150e9,
          references: 0,
          reference_bytes: 0,
          reference_metadata_bytes: 0,
          export_bytes: 0,
          measurement_bytes: 0,
          native_bytes: 0,
        }}
      />
      <section className="mt-6" aria-label="Image composer preview">
        <h2 className="mb-3 font-medium">Image creation in chat</h2>
        <Composer images previewImages />
      </section>
    </div>
  );
}
