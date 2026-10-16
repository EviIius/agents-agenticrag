import type { Attachment, Model } from "./api";
import type { AudioUpload } from "@/components/chat/AudioChip";
import { contextBudget } from "./context-budget";

export type AttachmentIssue = {
  key: string;
  kind: "warning" | "error";
  text: string;
  action?: "model" | "controls" | "settings" | "retry";
};
export function attachmentIssues(
  files: Attachment[],
  uploads: AudioUpload[],
  model?: Model,
  reserve?: number,
): AttachmentIssue[] {
  const budget = contextBudget(model, reserve);
  return [
    ...files.flatMap((file): AttachmentIssue[] => {
      if (file.kind === "image" && model?.vision !== true)
        return [
          {
            key: file.id,
            kind: "warning",
            text: `${model?.display_name ?? "This model"} can't see images. Switch to a model that can, or remove the photo.`,
            action: "model",
          },
        ];
      if (
        file.kind === "audio" &&
        ["failed", "cancelled"].includes(file.transcript?.status ?? "")
      )
        return [
          {
            key: file.id,
            kind: "warning",
            text: `‘${file.filename}’ isn't ready. Retry from its recording actions or remove it.`,
          },
        ];
      const tokens =
        file.document?.token_estimate ?? file.transcript?.token_estimate ?? 0;
      if (tokens > budget.available)
        return [
          {
            key: file.id,
            kind: "warning",
            text: `‘${file.filename}’ is about ${tokens.toLocaleString()} input tokens; this model takes ${budget.available.toLocaleString()} after reserving ${budget.reserve.toLocaleString()} for the answer.`,
            action: "controls",
          },
        ];
      return [];
    }),
    ...uploads.flatMap((upload): AttachmentIssue[] =>
      upload.failed
        ? [
            {
              key: upload.id,
              kind: "error",
              text: upload.reason ?? "Upload didn't finish.",
              action: upload.retryable
                ? "retry"
                : upload.reason?.includes("transcription engine")
                  ? "settings"
                  : undefined,
            },
          ]
        : [],
    ),
  ];
}
