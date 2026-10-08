import { failureCopy, failureDetail } from "@/lib/errors";
import { useEffect, useRef, useState } from "react";
import { useQuery, type QueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { api, type Attachment, type Bootstrap, type Model } from "@/lib/api";
import { useTranscripts } from "@/stores/transcripts";
import { attachTranscription } from "@/lib/sse";
import type { AudioUpload } from "@/components/chat/AudioChip";
import { prepareImage, uploadWithProgress } from "@/lib/attachments";
import {
  useAudioExtensions,
  transcriptionStatusQuery,
} from "./useAudioExtensions";
export function useUploads({
  query,
  bootstrap,
  current,
}: {
  query: QueryClient;
  bootstrap: { data?: Bootstrap };
  current?: Model;
}) {
  const [files, setFiles] = useState<Attachment[]>([]);
  const audioExtensions = useAudioExtensions(Boolean(bootstrap.data));
  const [uploads, setUploads] = useState<AudioUpload[]>([]);
  const uploadControllers = useRef(new Map<string, AbortController>());
  const [dragging, setDragging] = useState(false);
  const dragDepth = useRef(0);
  const transcriptState = useTranscripts((state) => state.attachments);
  const effectiveFiles = files.map((file) =>
    file.kind === "audio" ? (transcriptState[file.id] ?? file) : file,
  );
  const waitingForTranscript =
    uploads.some((upload) => !upload.failed) ||
    effectiveFiles.some(
      (file) => file.kind === "audio" && file.transcript?.status !== "ready",
    );
  const restored = useRef(false);
  const pendingRecordings = useQuery({
    queryKey: ["pending-recordings"],
    queryFn: () => api<Attachment[]>("/attachments/pending"),
    refetchOnWindowFocus: false,
  });
  useEffect(() => {
    if (!pendingRecordings.data || restored.current) return;
    restored.current = true;
    setFiles((files) => [
      ...files,
      ...pendingRecordings.data.filter(
        (item) => !files.some((file) => file.id === item.id),
      ),
    ]);
    pendingRecordings.data.forEach(attachTranscription);
  }, [pendingRecordings.data]);
  const upload = async (incoming: File[]) => {
    for (let file of incoming) {
      try {
        const suffix = "." + file.name.split(".").at(-1)?.toLowerCase();
        const extensions = await query.ensureQueryData(
          transcriptionStatusQuery,
        );
        const audio = (extensions.audio_extensions ?? []).includes(suffix);
        const document =
          bootstrap.data?.attachment_extensions?.document?.includes(suffix);
        if (audio || document) {
          if (audio && !bootstrap.data?.features.transcription)
            throw new Error("Recordings need the transcription engine");
          if (file.size > 4 * 1024 ** 3)
            throw new Error("Recordings can be up to 4 GB.");
          if (document && file.size > 50 * 1024 ** 2)
            throw new Error("Documents can be up to 50 MB and 1,500 pages.");
          const id = crypto.randomUUID(),
            controller = new AbortController();
          uploadControllers.current.set(id, controller);
          setUploads((uploads) => [
            ...uploads,
            {
              id,
              filename: file.name,
              percent: 0,
              ...(document ? { kind: "document" as const } : {}),
            },
          ]);
          try {
            const attachment = await uploadWithProgress(
              file,
              (percent) =>
                setUploads((uploads) =>
                  uploads.map((upload) =>
                    upload.id === id ? { ...upload, percent } : upload,
                  ),
                ),
              controller.signal,
            );
            setFiles((files) => [...files, attachment]);
            if (audio) attachTranscription(attachment);
            setUploads((uploads) =>
              uploads.filter((upload) => upload.id !== id),
            );
          } catch (error) {
            if (error instanceof DOMException && error.name === "AbortError")
              setUploads((uploads) =>
                uploads.filter((upload) => upload.id !== id),
              );
            else
              setUploads((uploads) =>
                uploads.map((upload) =>
                  upload.id === id
                    ? { ...upload, failed: true, reason: failureCopy(error) }
                    : upload,
                ),
              );
          } finally {
            uploadControllers.current.delete(id);
          }
          continue;
        }
        if (file.type.startsWith("image/")) {
          if (current?.vision !== true)
            throw new Error("Images need a vision model.");
          if (file.size > 20 * 1024 * 1024)
            throw new Error("Image limit is 20 MB.");
          file = await prepareImage(file);
        }
        const form = new FormData();
        form.append("file", file);
        const a = await api<Attachment>("/attachments", form);
        setFiles((f) => [...f, a]);
      } catch (e) {
        toast.error(failureCopy(e), { description: failureDetail(e) });
      }
    }
  };
  return {
    files,
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
  };
}
