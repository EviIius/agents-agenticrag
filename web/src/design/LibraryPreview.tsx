import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  LibraryView,
  LibraryFeedback,
  type LibraryDialog,
} from "@/components/settings/LibraryPane";
import { useUI } from "@/stores/ui";
import type { Model } from "@/lib/api";
import type { components } from "@/lib/api-types";
export const libraryStates = [
  "Loading",
  "Load failed",
  "Disconnected",
  "Empty",
  "No embedding model",
  "Unavailable",
  "Queued",
  "Extracting",
  "Embedding",
  "Ready",
  "Failed",
  "Stale",
  "Busy",
  "Error",
  "Change model",
  "New collection",
  "Rename collection",
  "Move file",
  "Delete file",
  "Delete collection",
  "Delete all",
  "File text",
  "Text loading",
  "Text failed",
];
const model: Model = {
  connection_id: "fake",
  model_id: "fake-embedding",
  display_name: "Invented embedding model",
  embedding: true,
  hidden: false,
  chat_capable: false,
  params_defaults: {},
};
const document: components["schemas"]["LibraryDocument"] = {
  id: "fake-document",
  filename: "Invented orchard handbook.md",
  mime_type: "text/markdown",
  bytes: 12340,
  status: "ready",
  chunk_count: 340,
  progress_done: 340,
  progress_total: 340,
  created_at: "2026-10-05T12:00:00Z",
  updated_at: "2026-10-05T12:00:00Z",
};
const collection = {
  id: "fake-collection",
  name: "Invented collection",
  created_at: document.created_at,
  updated_at: document.updated_at,
};
export function LibraryPreview() {
  const [state, setState] = useState("Ready");
  const ui = useUI();
  const status = [
    "Queued",
    "Extracting",
    "Embedding",
    "Failed",
    "Stale",
  ].includes(state)
    ? (state.toLowerCase() as typeof document.status)
    : "ready";
  const data: components["schemas"]["LibraryIndex"] = {
    available: state !== "Unavailable",
    embedding:
      state === "No embedding model"
        ? null
        : { connection_id: "fake", model_id: "fake-embedding", dim: 8 },
    requires_local: true,
    query_prefix: "",
    document_prefix: "",
    bytes: state === "Empty" ? 0 : document.bytes,
    event_id: 0,
    counts: { [status]: 1 },
    documents:
      state === "Empty"
        ? []
        : [
            {
              ...document,
              status,
              progress_done: 120,
              progress_total: 340,
              error:
                status === "failed"
                  ? {
                      code: "document_unreadable",
                      message: "Synthetic failed extraction. Retry this file.",
                    }
                  : null,
            },
          ],
    collections: [collection],
  };
  const dialogs: Record<string, LibraryDialog> = {
    "Change model": { kind: "model", model },
    "New collection": { kind: "collection" },
    "Rename collection": { kind: "collection", collection },
    "Move file": { kind: "move", document },
    "Delete file": { kind: "delete", document },
    "Delete collection": { kind: "remove-collection", collection },
    "Delete all": { kind: "clear" },
    "File text": { kind: "text", document },
    "Text loading": { kind: "text", document },
    "Text failed": { kind: "text", document },
  };
  return (
    <main className="mx-auto max-w-2xl p-4 space-y-5">
      <h1 className="text-xl font-medium">Library · Fake runtime preview</h1>
      <div className="flex flex-wrap gap-2">
        {["light", "dark"].map((theme) => (
          <Button
            key={theme}
            variant="outline"
            onClick={() => ui.set({ theme: theme as "light" | "dark" })}
          >
            {theme}
          </Button>
        ))}
      </div>
      <label className="block space-y-2">
        <span>Library preview state</span>
        <select
          className="min-h-11 w-full rounded-lg border border-line bg-bg px-3"
          aria-label="Library preview state"
          value={state}
          onChange={(e) => setState(e.target.value)}
        >
          {libraryStates.map((s) => (
            <option key={s}>{s}</option>
          ))}
        </select>
      </label>
      {["Loading", "Load failed", "Disconnected"].includes(state) ? (
        <LibraryFeedback
          kind={
            state === "Loading"
              ? "loading"
              : state === "Load failed"
                ? "error"
                : "disconnected"
          }
          retry={() => {}}
        />
      ) : (
        <LibraryView
          key={state}
          data={data}
          models={state === "No embedding model" ? [] : [model]}
          busy={state === "Busy"}
          error={
            state === "Error" ? "Synthetic file upload failed. Try again." : ""
          }
          initialDialog={dialogs[state]}
          readText={() =>
            state === "Text loading"
              ? new Promise(() => {})
              : state === "Text failed"
                ? Promise.reject(Error("Synthetic unavailable"))
                : Promise.resolve({
                    text: "Invented orchard notes. All displayed text is synthetic. <script>escaped text</script>",
                  })
          }
          mutate={async () => true}
          upload={async () => {}}
        />
      )}
    </main>
  );
}
