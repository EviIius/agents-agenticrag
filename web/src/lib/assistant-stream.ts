import type { components } from "./api-types";

export type DesktopTask = components["schemas"]["DesktopTask"];
export const terminalTask = (task: DesktopTask) =>
  !["queued", "running", "awaiting_approval"].includes(task.state);

/** Durable snapshots use SSE replay; paint only the newest revision per frame. */
export function attachDesktopTasks(
  ids: string[],
  snapshot: (task: DesktopTask) => void,
  connection: (reconnecting: boolean) => void,
) {
  const source = new EventSource(
    `/api/assistant/events?tasks=${encodeURIComponent(ids.join(","))}`,
  );
  const selected = new Set(ids);
  const finished = new Set<string>();
  let frame = 0;
  const pending = new Map<string, DesktopTask>();
  const revisions = new Map<string, number>();
  source.addEventListener("assistant.snapshot", (event) => {
    const data = JSON.parse(
      (event as MessageEvent<string>).data,
    ) as components["schemas"]["TaskEvent"];
    const task = data.task;
    if (
      !selected.has(task.id) ||
      task.revision <= (revisions.get(task.id) ?? -1)
    )
      return;
    revisions.set(task.id, task.revision);
    pending.set(task.id, task);
    if (!frame)
      frame = requestAnimationFrame(() => {
        frame = 0;
        pending.forEach((task) => snapshot(task));
        pending.clear();
      });
    if (terminalTask(task)) {
      finished.add(task.id);
      if (finished.size === selected.size) {
        source.close();
        connection(false);
      }
    }
  });
  source.onopen = () => connection(false);
  source.onerror = () => connection(true);
  return () => {
    source.close();
    cancelAnimationFrame(frame);
    pending.clear();
  };
}
