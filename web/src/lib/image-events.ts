import { create } from "zustand";
import type { components } from "./api-types";

export type ImageJob = components["schemas"]["ImageJob"];
export const imageActive = (job: ImageJob) =>
  ["queued", "preparing", "running", "cancelling"].includes(job.state);
const completed = new Set<string>();
const revealed = new Set<string>();
export const useImageJobs = create<{ jobs: Record<string, ImageJob> }>(() => ({
  jobs: {},
}));

export function receiveImages(jobs: ImageJob[]) {
  useImageJobs.setState((state) => {
    const next = { ...state.jobs };
    for (const job of jobs) {
      const previous = next[job.id];
      if (!previous || job.updated_at >= previous.updated_at) {
        if (previous && imageActive(previous) && job.state === "complete")
          completed.add(job.id);
        next[job.id] = job;
      }
    }
    return { jobs: next };
  });
}
export function claimImageReveal(id: string) {
  if (!completed.has(id) || revealed.has(id)) return false;
  revealed.add(id);
  return true;
}

/** Native EventSource reconnect/replay; presentation updates are one rAF batch. */
export function imageEvents() {
  const source = new EventSource("/api/images/events");
  let frame = 0;
  let pending: ImageJob[] = [];
  const enqueue = (event: Event, snapshot: boolean) => {
    try {
      const data = JSON.parse((event as MessageEvent).data);
      pending.push(...(snapshot ? data.jobs : [data.job]));
      if (!frame)
        frame = requestAnimationFrame(() => {
          frame = 0;
          receiveImages(pending);
          pending = [];
        });
    } catch {
      /* A subsequent snapshot repairs an invalid event. */
    }
  };
  source.addEventListener("image.snapshot", (event) => enqueue(event, true));
  source.addEventListener("image.updated", (event) => enqueue(event, false));
  return () => {
    source.close();
    cancelAnimationFrame(frame);
  };
}
