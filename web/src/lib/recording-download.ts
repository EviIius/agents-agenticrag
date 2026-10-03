import type { Attachment } from "./api";

export type RecordingFormat = "txt" | "srt" | "json" | "audio";
export type RecordingDownload = {
  format: RecordingFormat;
  variant?: string;
};
export const recordingFormats: Record<RecordingFormat, string> = {
  txt: "Text (.txt)",
  srt: "Subtitles (.srt)",
  json: "Details (.json)",
  audio: "Original audio",
};
export function recordingDownloadURL(
  id: string,
  format: RecordingFormat,
  variant = "best",
) {
  if (format === "audio") return `/api/attachments/${id}`;
  const selected =
    format === "srt" && variant === "best" ? "original" : variant;
  return `/api/attachments/${id}/transcript/download?format=${format}&variant=${selected}`;
}
export function recordingFilename(
  attachment: Attachment,
  format: RecordingFormat,
) {
  if (format === "audio") return attachment.filename;
  const stem = attachment.filename.replace(/\.[^.]+$/, "");
  const safe = Array.from(stem, (c) => (/[\p{L}\p{N} ._-]/u.test(c) ? c : "-"))
    .join("")
    .replace(/^[ .]+|[ .]+$/g, "");
  return (
    (Array.from(safe).slice(0, 120).join("") || "Transcript") + "." + format
  );
}
