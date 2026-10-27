import type { Chat, Message, Model } from "./api";
import type { ImageJob } from "./image-events";

// Explicit display alias from the reviewed B4 example; never capability metadata.
const displayAliases: Record<string, string> = {
  "qwen3.8:27b-atelier-eval-32k": "Qwen 3.8 27B · Atelier eval · 32K",
};
export function modelLabel(model?: Pick<Model, "model_id" | "display_name">) {
  if (!model) return "Choose model";
  return model.display_name && model.display_name !== model.model_id
    ? model.display_name
    : (displayAliases[model.model_id] ?? model.display_name ?? model.model_id);
}
export function thinkingLabel(level: string) {
  return level === "xhigh" ? "Max" : level[0].toUpperCase() + level.slice(1);
}
export function followupImage(path: Message[]): ImageJob | undefined {
  const last = path.at(-1);
  if (last?.role !== "assistant" || last.kind !== "image") return;
  if (
    last.images?.some(
      (job) =>
        !["complete", "cancelled", "failed", "interrupted"].includes(job.state),
    )
  )
    return;
  return last.images
    ?.slice()
    .reverse()
    .find((job) => job.state === "complete" && job.image_bytes > 0);
}
export function replyState(message: Message) {
  if (
    message.role !== "assistant" ||
    message.kind === "image" ||
    message.status === "streaming"
  )
    return;
  if (message.status === "stopped") return "Stopped";
  if (!message.error && !message.content.trim()) return "No answer";
}

/** History is pinned-first; starter recency must use activity dates instead. */
export function recentChats(chats: Chat[]) {
  return chats
    .filter((chat) => chat.current_leaf_id)
    .sort((a, b) => (b.updated_at ?? "").localeCompare(a.updated_at ?? ""))
    .slice(0, 2);
}
