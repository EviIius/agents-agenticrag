import { failureCopy } from "@/lib/errors";
import { useEffect, useRef, useState, useMemo } from "react";
import { useQuery, type QueryClient } from "@tanstack/react-query";
import { api, type Attachment, type Bootstrap, type Model } from "@/lib/api";
import { useTranscripts } from "@/stores/transcripts";
import { attachTranscription } from "@/lib/sse";
import type { AudioUpload } from "@/components/chat/AudioChip";
import { prepareImage, uploadWithProgress } from "@/lib/attachments";
import { fileKind, fileLimit } from "@/lib/file-kinds";
import {
  useAudioExtensions,
  transcriptionStatusQuery,
} from "./useAudioExtensions";

export type AttachmentLocal = {
  key: string;
  url?: string;
  order: number;
  stagger?: number;
  characters?: number;
};
const noRetainedPreviews: string[] = [];
export function useUploads({
  query,
  bootstrap,
  retainedPreviewIds = noRetainedPreviews,
}: {
  query: QueryClient;
  bootstrap: { data?: Bootstrap };
  current?: Model;
  retainedPreviewIds?: string[];
}) {
  const [files, setFiles] = useState<Attachment[]>([]);
  const [attachmentVersion, setAttachmentVersion] = useState(0);
  const audioExtensions = useAudioExtensions(Boolean(bootstrap.data));
  const [uploads, setUploads] = useState<AudioUpload[]>([]);
  const [local, setLocal] = useState<Record<string, AttachmentLocal>>({});
  const resources = useRef(new Map<string, string>());
  const previews = useRef(new Map<string, HTMLImageElement>());
  const completed = useRef(new Map<string, string>());
  const originals = useRef(new Map<string, File>());
  const slots = useRef(new Set<string>());
  const uploadControllers = useRef(new Map<string, AbortController>());
  const queue = useRef(Promise.resolve());
  const serial = useRef(0);
  const mounted = useRef(true);
  const [dragging, setDragging] = useState(false);
  const dragDepth = useRef(0);
  const transcriptState = useTranscripts((state) => state.attachments);
  const effectiveFiles = useMemo(
    () =>
      files.map((file) =>
        file.kind === "audio" ? (transcriptState[file.id] ?? file) : file,
      ),
    [files, transcriptState],
  );
  const waitingForTranscript =
    uploads.some((item) => !item.failed) ||
    effectiveFiles.some(
      (file) => file.kind === "audio" && file.transcript?.status !== "ready",
    );
  const releasePreview = (id: string) => {
    const image = previews.current.get(id);
    if (image) image.onload = image.onerror = null;
    previews.current.delete(id);
    const url = resources.current.get(id);
    if (url) URL.revokeObjectURL(url);
    resources.current.delete(id);
    setLocal((old) =>
      old[id]?.url ? { ...old, [id]: { ...old[id], url: undefined } } : old,
    );
  };
  useEffect(() => {
    mounted.current = true;
    const controllers = uploadControllers.current,
      urls = resources.current,
      images = previews.current;
    return () => {
      mounted.current = false;
      controllers.forEach((controller) => controller.abort());
      urls.forEach((url) => URL.revokeObjectURL(url));
      controllers.clear();
      urls.clear();
      images.forEach((image) => {
        image.onload = image.onerror = null;
      });
      images.clear();
      completed.current.clear();
      originals.current.clear();
    };
  }, []);
  useEffect(() => {
    const ids = new Set([
      ...files.map((f) => f.id),
      ...uploads.map((u) => u.id),
      ...retainedPreviewIds,
    ]);
    for (const [id, url] of resources.current)
      if (!ids.has(id) && !previews.current.has(id)) {
        URL.revokeObjectURL(url);
        resources.current.delete(id);
      }
    for (const id of slots.current) if (!ids.has(id)) slots.current.delete(id);
    setLocal((old) => {
      const entries = Object.entries(old).filter(
        ([id]) => ids.has(id) || previews.current.has(id),
      );
      return entries.length === Object.keys(old).length
        ? old
        : Object.fromEntries(entries);
    });
    for (const [key, id] of completed.current)
      if (!ids.has(id) && !previews.current.has(id))
        completed.current.delete(key);
  }, [files, uploads, retainedPreviewIds, local]);
  const restored = useRef(false);
  const pendingRecordings = useQuery({
    queryKey: ["pending-recordings"],
    queryFn: () => api<Attachment[]>("/attachments/pending"),
    refetchOnWindowFocus: false,
  });
  useEffect(() => {
    if (!pendingRecordings.data || restored.current) return;
    restored.current = true;
    const pending = pendingRecordings.data.slice(
      0,
      Math.max(0, 8 - slots.current.size),
    );
    pending.forEach((file) => slots.current.add(file.id));
    setFiles((old) => [
      ...old,
      ...pending.filter((f) => !old.some((item) => item.id === f.id)),
    ]);
    pending.forEach(attachTranscription);
  }, [pendingRecordings.data]);
  const cancelUpload = (id: string) => {
    uploadControllers.current.get(id)?.abort();
    uploadControllers.current.delete(id);
    originals.current.delete(id);
    slots.current.delete(id);
    releasePreview(id);
    setUploads((old) => old.filter((item) => item.id !== id));
  };
  const execute = async (
    id: string,
    file: File,
    controller: AbortController,
  ) => {
    const update = (patch: Partial<AudioUpload>) => {
      if (mounted.current && !controller.signal.aborted)
        setUploads((old) =>
          old.map((item) => (item.id === id ? { ...item, ...patch } : item)),
        );
    };
    try {
      if (controller.signal.aborted) return;
      const status = await query.ensureQueryData(transcriptionStatusQuery);
      const extensions = bootstrap.data?.attachment_extensions ?? {
        text: [],
        document: [],
      };
      const kind = fileKind(file, extensions, status.audio_extensions ?? []);
      update({ kind });
      if (kind === "unsupported")
        throw new Error(
          `Can't attach ${file.name.includes(".") ? file.name.slice(file.name.lastIndexOf(".")) : "this type of"} files. Images, PDF, Word, text and recordings work.`,
        );
      if (kind === "audio" && !bootstrap.data?.features.transcription)
        throw new Error("Recordings need the transcription engine.");
      const limit = fileLimit(kind);
      if (file.size > limit.bytes)
        throw new Error(`‘${file.name}’ is over ${limit.label}.`);
      let prepared = file;
      if (kind === "image") prepared = await prepareImage(file);
      if (controller.signal.aborted) return;
      update({
        phase: "uploading",
        format: prepared.type === "image/heic" ? "HEIC" : undefined,
      });
      const attachment = await uploadWithProgress(
        prepared,
        (percent) => {
          update({
            percent,
            phase:
              percent === 100 && kind === "document" ? "reading" : "uploading",
          });
        },
        controller.signal,
      );
      if (controller.signal.aborted || !mounted.current) return;
      const url = resources.current.get(id);
      if (url) {
        resources.current.delete(id);
        resources.current.set(attachment.id, url);
      }
      setLocal((old) => {
        const next = { ...old, [attachment.id]: old[id] };
        delete next[id];
        return next;
      });
      slots.current.delete(id);
      slots.current.add(attachment.id);
      completed.current.set(id, attachment.id);
      setFiles((old) => [...old, attachment]);
      if (url) {
        const image = new Image();
        previews.current.set(attachment.id, image);
        image.onload = () => {
          if (mounted.current) releasePreview(attachment.id);
        };
        image.onerror = () => previews.current.delete(attachment.id);
        image.src = `/api/attachments/${attachment.id}`;
      }
      setAttachmentVersion((version) => version + 1);
      if (kind === "audio") attachTranscription(attachment);
      setUploads((old) => old.filter((item) => item.id !== id));
      originals.current.delete(id);
    } catch (error) {
      if (controller.signal.aborted) return;
      slots.current.delete(id);
      update({
        failed: true,
        phase: "error",
        reason:
          error instanceof Error && error.message === "Upload didn't finish"
            ? `‘${file.name}’ didn't finish uploading.`
            : failureCopy(error) === "Something went wrong. Try again." &&
                error instanceof Error
              ? error.message
              : failureCopy(error),
        retryable:
          error instanceof TypeError ||
          (error instanceof Error && error.message === "Upload didn't finish"),
      });
    } finally {
      uploadControllers.current.delete(id);
    }
  };
  const enqueue = (id: string, file: File) => {
    const controller = new AbortController();
    uploadControllers.current.set(id, controller);
    queue.current = queue.current.then(() => execute(id, file, controller));
  };
  const upload = (incoming: File[], pasted?: { characters: number }) => {
    const ids: string[] = [];
    for (const [stagger, file] of incoming.entries()) {
      const id = crypto.randomUUID();
      ids.push(id);
      const kind = fileKind(
        file,
        bootstrap.data?.attachment_extensions ?? { text: [], document: [] },
        audioExtensions,
      );
      const url = kind === "image" ? URL.createObjectURL(file) : undefined;
      if (url) resources.current.set(id, url);
      const limit = slots.current.size >= 8;
      if (!limit) slots.current.add(id);
      originals.current.set(id, file);
      const order = ++serial.current;
      setLocal((old) => ({
        ...old,
        [id]: { key: id, url, order, stagger, characters: pasted?.characters },
      }));
      setUploads((old) => [
        ...old,
        {
          id,
          filename: file.name,
          kind,
          percent: 0,
          phase: limit ? "error" : "preparing",
          failed: limit,
          reason: limit ? "8 files is the limit for one message." : undefined,
        },
      ]);
      // A user pick reveals its tray immediately, including inline failures.
      // Restored durable recordings never go through this path.
      setAttachmentVersion((version) => version + 1);
      if (!limit) enqueue(id, file);
    }
    return ids;
  };
  const discardPasted = (key: string) => {
    const id = completed.current.get(key);
    if (!id) {
      cancelUpload(key);
      return;
    }
    completed.current.delete(key);
    slots.current.delete(id);
    setFiles((old) => old.filter((f) => f.id !== id));
    releasePreview(id);
    // Only the unsubmitted text upload created by this paste is discarded.
    void api(`/attachments/${id}`, undefined, "DELETE").catch(() => undefined);
  };
  const retryUpload = (id: string) => {
    const file = originals.current.get(id);
    if (!file || slots.current.size >= 8 || uploadControllers.current.has(id))
      return;
    slots.current.add(id);
    setUploads((old) =>
      old.map((item) =>
        item.id === id
          ? {
              ...item,
              failed: false,
              reason: undefined,
              phase: "preparing",
              percent: 0,
            }
          : item,
      ),
    );
    enqueue(id, file);
  };
  return {
    files,
    attachmentVersion,
    setFiles,
    effectiveFiles,
    waitingForTranscript,
    uploads,
    setUploads,
    uploadControllers,
    dragging,
    setDragging,
    dragDepth,
    audioExtensions,
    upload,
    local,
    releasePreview,
    cancelUpload,
    retryUpload,
    discardPasted,
  };
}
