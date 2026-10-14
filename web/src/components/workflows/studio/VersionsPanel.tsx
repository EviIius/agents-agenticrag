import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { api } from "@/lib/api";
import type { components } from "@/lib/api-types";
import { Button } from "@/components/ui/button";
import { IconButton } from "@/components/app/IconButton";
import { X } from "lucide-react";
import { TextField } from "./fields";
import { useStudio } from "./store";
import type { Doc } from "./types";
export function VersionsPanel({
  close,
  previewSnapshots,
}: {
  close: () => void;
  previewSnapshots?: components["schemas"]["Snapshot"][];
}) {
  const id = useStudio((s) => s.id),
    edit = useStudio((s) => s.edit);
  const q = useQuery({
    queryKey: ["workflow-versions", id],
    enabled: previewSnapshots === undefined,
    queryFn: () =>
      api<components["schemas"]["Snapshot"][]>(
        `/workflows/defs/${id}/snapshots`,
      ),
  });
  const [names, setNames] = useState<Record<string, string>>({}),
    [error, setError] = useState("");
  const snapshots = previewSnapshots ?? q.data;
  const loading = previewSnapshots === undefined && q.isPending;
  return (
    <div className="wf-inspector">
      <header className="wf-panel-head">
        <h2>Versions</h2>
        <IconButton label="Close Versions" onClick={close}>
          <X />
        </IconButton>
      </header>
      <div className="wf-panel-body wf-field-stack">
        {loading && <p role="status">Loading saved versions…</p>}
        {previewSnapshots === undefined && q.isError && (
          <p role="alert">
            Versions couldn't be loaded.{" "}
            <Button variant="ghost" onClick={() => void q.refetch()}>
              Try again
            </Button>
          </p>
        )}
        {!loading && !snapshots?.length && (
          <p className="wf-help">
            Run this workflow to save its first version.
          </p>
        )}
        {snapshots?.map((snapshot) => (
          <section key={snapshot.id} className="wf-version">
            <h3>
              {snapshot.label || new Date(snapshot.created_at).toLocaleString()}
            </h3>
            <p className="wf-help">
              {snapshot.run_count} run{snapshot.run_count === 1 ? "" : "s"}
            </p>
            <TextField
              label="Version name"
              value={names[snapshot.id] ?? snapshot.label ?? ""}
              maxLength={80}
              onChange={(v) => setNames((n) => ({ ...n, [snapshot.id]: v }))}
            />
            <div className="flex gap-2">
              <Button
                variant="outline"
                onClick={async () => {
                  if (previewSnapshots) return;
                  try {
                    await api(
                      `/workflows/defs/${id}/snapshots/${snapshot.id}`,
                      { label: names[snapshot.id] ?? snapshot.label },
                      "PATCH",
                    );
                    void q.refetch();
                  } catch {
                    setError("The version name couldn't be saved.");
                  }
                }}
              >
                Save name
              </Button>
              <Button
                onClick={() => {
                  edit((d) => ({
                    ...d,
                    graph: structuredClone(snapshot.graph) as Doc,
                  }));
                  close();
                }}
              >
                Restore
              </Button>
            </div>
          </section>
        ))}
        {error && (
          <p role="alert" className="text-danger">
            {error}
          </p>
        )}
      </div>
    </div>
  );
}
