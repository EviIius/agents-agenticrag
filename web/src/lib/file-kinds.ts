import { isImageFile } from "./attachments";

export type FileKind = "image" | "document" | "text" | "audio" | "unsupported";
export type FileExtensions = { text?: string[]; document?: string[] };
export function suffix(name: string) {
  const match = name.match(/\.[^.]+$/);
  return match?.[0].toLowerCase() ?? "";
}
export function fileKind(
  file: File,
  extensions: FileExtensions,
  audio: string[],
): FileKind {
  const ext = suffix(file.name);
  if (audio.includes(ext)) return "audio";
  if (extensions.document?.includes(ext)) return "document";
  if (isImageFile(file)) return "image";
  return extensions.text?.includes(ext) ? "text" : "unsupported";
}
export function fileAccept(
  extensions?: FileExtensions,
  audio: string[] = [],
  transcription = false,
) {
  return [
    ...new Set([
      "image/*",
      ".heic",
      ".heif",
      ...(extensions?.document ?? []),
      ...(extensions?.text ?? []),
      ...(transcription ? audio : []),
    ]),
  ].join(",");
}
export function fileLimit(kind: FileKind) {
  return kind === "image"
    ? { bytes: 20 * 1024 ** 2, label: "20 MB" }
    : kind === "document"
      ? { bytes: 50 * 1024 ** 2, label: "50 MB" }
      : kind === "audio"
        ? { bytes: 4 * 1024 ** 3, label: "4 GB" }
        : { bytes: 512 * 1024, label: "512 KB" };
}
export function fileTone(name: string, kind: FileKind | "text" = "text") {
  const ext = suffix(name);
  return kind === "audio"
    ? "media"
    : ext === ".pdf"
      ? "review"
      : ext === ".docx"
        ? "ai"
        : [".csv", ".json"].includes(ext)
          ? "knowledge"
          : "input";
}
export function splitFilename(name: string): [string, string] {
  const dot = name.lastIndexOf(".");
  const end = dot > 0 ? dot : name.length;
  const tail = name.slice(Math.max(0, end - 10), end);
  const matches = [...tail.matchAll(/[\s\-_[(]/g)];
  const cut = matches.length
    ? Math.max(0, end - 10) + matches.at(-1)!.index!
    : Math.max(0, end - 4);
  return [name.slice(0, cut), name.slice(cut)];
}
export function fileSize(bytes: number) {
  return bytes < 1024
    ? `${bytes} B`
    : bytes < 1024 ** 2
      ? `${Math.ceil(bytes / 1024).toLocaleString()} KB`
      : `${(bytes / 1024 ** 2).toFixed(1)} MB`;
}
