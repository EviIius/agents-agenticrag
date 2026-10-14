import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { components } from "@/lib/api-types";
import type { Workflow } from "./WorkflowsPage";

type Snapshot = components["schemas"]["WorkflowSnapshot"];
type Change = components["schemas"]["WorkflowChange"];

export function useWorkflowRuns() {
  const [runs, setRuns] = useState<Workflow[]>([]);
  const [loading, setLoading] = useState(true);
  const [notice, setNotice] = useState("");
  const [connection, setConnection] = useState("Connecting…");
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    let mounted = true;
    let streamed = false;
    let frame = 0;
    setLoading(true);
    setNotice("");
    void api<Snapshot>("/workflows").then(
      (snapshot) => {
        if (!mounted) return;
        // An older initial HTTP response must not replace a newer stream snapshot.
        if (!streamed) setRuns(snapshot.runs);
        setLoading(false);
      },
      () => {
        if (mounted && !streamed) {
          setLoading(false);
          setNotice("Saved runs could not be loaded.");
        }
      },
    );
    const source = new EventSource("/api/workflows/events");
    const pending: (
      { kind: "snapshot"; data: Snapshot } | { kind: "change"; data: Change }
    )[] = [];
    function enqueue(kind: "snapshot" | "change", event: MessageEvent) {
      try {
        pending.push(
          kind === "snapshot"
            ? { kind, data: JSON.parse(event.data) as Snapshot }
            : { kind, data: JSON.parse(event.data) as Change },
        );
        streamed = true;
        if (!frame)
          frame = requestAnimationFrame(() => {
            frame = 0;
            if (!mounted) return;
            const batch = pending.splice(0);
            setRuns((current) => {
              let next = current;
              for (const item of batch)
                next =
                  item.kind === "snapshot"
                    ? item.data.runs
                    : [
                        item.data.run,
                        ...next.filter((run) => run.id !== item.data.run.id),
                      ].sort((a, b) =>
                        b.created_at.localeCompare(a.created_at),
                      );
              return next;
            });
            setLoading(false);
          });
      } catch {
        if (mounted)
          setNotice("An update could not be read. Reload to reconnect.");
      }
    }
    source.addEventListener("workflow.snapshot", (event) =>
      enqueue("snapshot", event as MessageEvent),
    );
    source.addEventListener("workflow.updated", (event) =>
      enqueue("change", event as MessageEvent),
    );
    source.onopen = () => {
      if (mounted) setConnection("Connected");
    };
    source.onerror = () => {
      if (mounted)
        setConnection("Reconnecting — accepted work continues on your Mac");
    };
    return () => {
      mounted = false;
      source.close();
      cancelAnimationFrame(frame);
    };
  }, [attempt]);
  return {
    runs,
    setRuns,
    loading,
    notice,
    setNotice,
    connection,
    attempt,
    retry: () => setAttempt((value) => value + 1),
  };
}
