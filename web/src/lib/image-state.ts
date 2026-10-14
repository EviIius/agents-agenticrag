import { imageActive, type ImageJob } from "./image-events";

export function imageTurnStatus(jobs: ImageJob[], queue: ImageJob[] = []) {
  const index = jobs.findIndex(imageActive),
    current = jobs[index];
  if (current) {
    if (current.state === "cancelling") return "Cancelling…";
    if (current.state === "queued") {
      const ahead = queue.filter(
        (job) =>
          imageActive(job) &&
          !jobs.some((own) => own.id === job.id) &&
          job.created_at < current.created_at,
      ).length;
      return `Waiting for your Mac${ahead ? ` · after ${ahead} image${ahead > 1 ? "s" : ""}` : ""}`;
    }
    if (current.state === "preparing") return "Loading the image model";
    if (current.stage === "Decoding image") return "Finishing";
    return `${jobs.length > 1 ? `Creating image ${index + 1} of ${jobs.length}` : "Creating"} · step ${Math.min(current.completed_steps + 1, current.steps)} of ${current.steps}`;
  }
  if (jobs.some((job) => job.state === "failed"))
    return "Couldn't create this image";
  if (jobs.some((job) => job.state === "interrupted"))
    return "Interrupted — retry available";
  if (jobs.some((job) => job.state === "cancelled")) return "Cancelled";
  const saved = jobs.filter((job) => job.image_bytes > 0).length;
  if (!saved) return "Image removed";
  const seconds = jobs.reduce(
    (sum, job) => sum + (job.elapsed_seconds ?? 0),
    0,
  );
  return `${saved} image${saved > 1 ? "s" : ""} · ${Math.round(seconds)} s`;
}
