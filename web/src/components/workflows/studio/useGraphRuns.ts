import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { Run, RunPage } from "./types";
export function useGraphRuns(requestedId?: string) {
  const [runs, setRuns] = useState<Run[]>([]),
    [connection, setConnection] = useState("Connecting…"),
    [error, setError] = useState("");
  useEffect(() => {
    let mounted = true,
      frame = 0;
    const seen = new Set<string>();
    let streamed = false;
    const pending: { snapshot?: Run[]; run?: Run }[] = [];
    const merge = (current: Run[], run: Run) =>
      [run, ...current.filter((r) => r.id !== run.id)].sort((a, b) =>
        b.created_at.localeCompare(a.created_at),
      );
    const source = new EventSource("/api/workflows/stream");
    const enqueue = (event: MessageEvent, snapshot: boolean) => {
      try {
        const value = JSON.parse(event.data) as RunPage & { run?: Run };
        streamed = true;
        if (value.run) seen.add(value.run.id);
        pending.push(snapshot ? { snapshot: value.items } : { run: value.run });
        if (!frame)
          frame = requestAnimationFrame(() => {
            frame = 0;
            if (!mounted) return;
            const batch = pending.splice(0);
            setRuns((old) =>
              batch.reduce(
                (current, item) =>
                  item.snapshot
                    ? [
                        ...item.snapshot,
                        ...current.filter(
                          (r) => !item.snapshot!.some((n) => n.id === r.id),
                        ),
                      ]
                    : item.run
                      ? merge(current, item.run)
                      : current,
                old,
              ),
            );
          });
      } catch {
        if (mounted)
          setError("An update couldn't be read. Reload to reconnect.");
      }
    };
    source.addEventListener("run.snapshot", (e) =>
      enqueue(e as MessageEvent, true),
    );
    source.addEventListener("run.updated", (e) =>
      enqueue(e as MessageEvent, false),
    );
    source.onopen = () => {
      if (mounted) setConnection("Connected");
    };
    source.onerror = () => {
      if (mounted)
        setConnection("Reconnecting — accepted work continues on your Mac");
    };
    void api<RunPage>("/workflows/runs").then(
      (page) => {
        if (mounted && !streamed) setRuns(page.items);
      },
      () => {
        if (mounted && !streamed) setError("Saved runs could not be loaded.");
      },
    );
    if (requestedId)
      void api<Run>(`/workflows/runs/${requestedId}/v2`).then(
        (run) => {
          if (mounted && !seen.has(run.id))
            setRuns((current) => merge(current, run));
        },
        () => {
          if (mounted) setError("This run could not be opened.");
        },
      );
    return () => {
      mounted = false;
      source.close();
      cancelAnimationFrame(frame);
    };
  }, [requestedId]);
  return {
    runs,
    connection,
    error,
    accepted: (run: Run) =>
      setRuns((current) =>
        current.some((r) => r.id === run.id) ? current : [run, ...current],
      ),
  };
}
