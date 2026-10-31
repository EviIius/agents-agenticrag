import type { components } from "./api-types";

export type DesktopTask = components["schemas"]["DesktopTask"];
export const terminalTask = (task: DesktopTask) =>
  !["queued", "running", "awaiting_approval"].includes(task.state);

/** Durable snapshots use SSE replay; paint only the newest revision per frame. */
export function attachDesktopTask(
  id: string,
  snapshot: (task: DesktopTask) => void,
  connection: (reconnecting: boolean) => void,
) {
  const source = new EventSource(`/api/assistant/tasks/${id}/events`);
  let frame = 0;
  let pending: DesktopTask | undefined;
  let revision = -1;
  source.addEventListener("assistant.snapshot", (event) => {
    const data = JSON.parse(
      (event as MessageEvent<string>).data,
    ) as components["schemas"]["TaskEvent"];
    const task = data.task;
    if (task.id !== id || task.revision <= revision) return;
    revision = task.revision;
    pending = task;
    if (!frame)
      frame = requestAnimationFrame(() => {
        frame = 0;
        if (pending) snapshot(pending);
        pending = undefined;
      });
    if (terminalTask(task)) {
      source.close();
      connection(false);
    }
  });
  source.onopen = () => connection(false);
  source.onerror = () => connection(true);
  return () => {
    source.close();
    cancelAnimationFrame(frame);
    pending = undefined;
  };
}
