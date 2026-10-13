import type { Run, Edge } from "./types";
export type LiveUpdate = {
  run_id: string;
  attempt?: number;
  node_id: string;
  text?: string;
  delta?: string;
  done?: number;
  total?: number;
  label?: string;
};
export function updateLive(
  runs: Run[],
  event: LiveUpdate,
  kind: "node.text" | "node.progress",
) {
  return runs.map((run) => {
    if (
      run.id !== event.run_id ||
      run.nodes[event.node_id]?.state !== "running"
    )
      return run;
    const step = run.nodes[event.node_id];
    if (event.attempt !== undefined && event.attempt !== step.attempt)
      return run;
    if (
      kind === "node.text" &&
      event.text !== undefined &&
      typeof step.output?.text === "string" &&
      event.text.length < step.output.text.length
    )
      return run;
    const next =
      kind === "node.text"
        ? {
            ...step,
            output: {
              ...step.output,
              text:
                event.text ??
                String(step.output?.text ?? "") + (event.delta ?? ""),
            },
          }
        : {
            ...step,
            progress: {
              done: event.done,
              total: event.total,
              label: event.label,
            },
          };
    return { ...run, nodes: { ...run.nodes, [event.node_id]: next } };
  });
}
export function runLabel(run: Run, id: string) {
  const step = run.nodes[id];
  if (!step) return "Waiting";
  if (step.reused_from)
    return step.reused_from === "sample"
      ? "Sample input"
      : "Reused from earlier run";
  if (step.state === "running") {
    if (step.progress?.label) {
      const { done, total, label } = step.progress;
      return `${label}${Number(total) > 0 ? ` · ${done} of ${total}` : ""}`;
    }
    return typeof step.output?.text === "string"
      ? `Writing · ${step.output.text.length} characters`
      : run.stage;
  }
  if (step.state === "complete")
    return step.started_at && step.finished_at
      ? `Done in ${Math.max(0, Math.round((Date.parse(step.finished_at) - Date.parse(step.started_at)) / 1000))} s`
      : "Done";
  return {
    pending: "Waiting",
    paused: "Waiting for you",
    failed: step.error ?? "Failed",
    skipped: "Skipped",
    cancelled: "Cancelled",
    interrupted: "Interrupted",
  }[step.state];
}
export function edgeState(run: Run, edge: Edge) {
  const source = run.nodes[edge.source],
    target = run.nodes[edge.target];
  if (
    target?.state === "running" &&
    source?.state === "complete" &&
    source.port === edge.source_port
  )
    return "active";
  if (
    source?.state === "complete" &&
    source.port === edge.source_port &&
    target?.state !== "skipped"
  )
    return "done";
  if (
    source?.state === "skipped" ||
    (source?.state === "complete" && source.port !== edge.source_port) ||
    target?.state === "skipped"
  )
    return "not-taken";
  return "waiting";
}
