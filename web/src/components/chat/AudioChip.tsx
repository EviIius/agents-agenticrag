import { useEffect, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { AudioLines, Ellipsis, X } from "lucide-react";
import { toast } from "sonner";
import { api, type Attachment, type Model, type Transcript } from "@/lib/api";
import { attachTranscription, detachTranscription } from "@/lib/sse";
import { useTranscripts } from "@/stores/transcripts";
import { Button } from "@/components/ui/button";
import { IconButton } from "@/components/app/IconButton";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  TranscriptSheet,
  duration,
  transcriptDownload,
} from "./TranscriptSheet";

export type AudioUpload = {
  id: string;
  filename: string;
  percent: number;
  failed?: boolean;
  reason?: string;
};
export function UploadChip({
  upload,
  onCancel,
}: {
  upload: AudioUpload;
  onCancel: () => void;
}) {
  return (
    <div
      role="status"
      className="mb-2 flex max-w-full items-center gap-2 rounded-lg border border-line bg-surface-2 p-2 text-xs"
    >
      <AudioLines className="size-4 shrink-0" />
      <div className="min-w-0 flex-1">
        <p className="truncate">{upload.filename}</p>
        <p className="text-fg-2">
          {upload.failed
            ? "Upload didn't finish"
            : `Uploading ${upload.percent}%`}
        </p>
        {upload.failed && upload.reason && (
          <p className="break-words text-danger">{upload.reason}</p>
        )}
      </div>
      <IconButton
        label={upload.failed ? "Remove failed upload" : "Cancel upload"}
        type="button"
        onClick={onCancel}
      >
        <X />
      </IconButton>
    </div>
  );
}
export function AudioChip({
  attachment,
  model,
  onRemove,
  fixture,
}: {
  attachment: Attachment;
  model?: Model;
  onRemove?: () => void;
  fixture?: Transcript;
}) {
  const live = useTranscripts((state) => state.attachments[attachment.id]);
  const item = fixture ? attachment : (live ?? attachment);
  const meta = item.transcript;
  const query = useQueryClient();
  const [open, setOpen] = useState(false),
    [clock, setClock] = useState(Date.now());
  useEffect(() => {
    if (!fixture) attachTranscription(attachment);
  }, [attachment, fixture]);
  useEffect(() => {
    if (meta?.status !== "transcribing") return;
    const timer = setInterval(() => setClock(Date.now()), 1000);
    return () => clearInterval(timer);
  }, [meta?.status]);
  const maximum = model?.context_length ?? 8192;
  const tooLarge =
    (meta?.token_estimate ?? 0) >
    maximum - Math.max(1024, Math.min(8192, maximum * 0.25)) - 256;
  const ready = meta?.status === "ready";
  let label =
    meta?.status === "queued"
      ? "Waiting for another recording"
      : meta?.status === "transcribing"
        ? `Transcribing ${duration((clock - Date.parse(meta.started_at ?? "")) / 1000 || 0)}`
        : meta?.status === "cancelled"
          ? "Cancelled"
          : meta?.status === "failed"
            ? meta.error?.code === "transcription_interrupted"
              ? "Interrupted because the server restarted"
              : `Couldn't transcribe: ${meta.error?.message ?? "The engine failed."}`
            : ready && !meta.word_count
              ? "No speech found"
              : `${duration(meta?.duration_seconds ?? 0)} · ${meta?.word_count?.toLocaleString()} words · ≈${meta?.token_estimate?.toLocaleString()} tokens`;
  if (meta?.cleanup?.status === "ready") label += " · Cleaned";
  const retry = async (channels = meta?.channels ?? "mix") => {
    if (fixture) return;
    try {
      detachTranscription(item.id);
      const next = await api<Attachment>(`/attachments/${item.id}/transcribe`, {
        channels,
      });
      attachTranscription(next);
      void query.invalidateQueries({ queryKey: ["transcript", item.id] });
    } catch (error) {
      toast.error(String(error));
    }
  };
  const cancel = () => {
    if (!fixture)
      void api(`/attachments/${item.id}/cancel`, {}).catch((error) =>
        toast.error(String(error)),
      );
  };
  return (
    <>
      <div
        data-testid="audio-chip"
        className={`mb-2 flex max-w-full items-center gap-2 rounded-lg border p-2 ${tooLarge && ready ? "border-warning text-warning" : "border-line bg-surface-2"}`}
      >
        <AudioLines className="size-4 shrink-0" aria-hidden />
        <button
          type="button"
          className="min-h-11 min-w-0 flex-1 text-left text-xs"
          disabled={!ready}
          aria-label={
            ready ? `Open transcript for ${item.filename}` : item.filename
          }
          onClick={() => setOpen(true)}
        >
          <span className="block truncate font-medium">{item.filename}</span>
          <span className="block break-words text-fg-2" role="status">
            {label}
          </span>
          {ready && tooLarge && (
            <span className="block break-words text-warning">
              About {meta?.token_estimate?.toLocaleString()} tokens: more than{" "}
              {model?.display_name ?? "this model"} can take (
              {maximum.toLocaleString()}). Choose a model with a larger context.
            </span>
          )}
        </button>
        {meta && ["queued", "transcribing"].includes(meta.status) ? (
          <IconButton
            type="button"
            label="Cancel transcription"
            onClick={cancel}
          >
            <X />
          </IconButton>
        ) : !ready ? (
          <Button type="button" variant="outline" onClick={() => void retry()}>
            Retry
          </Button>
        ) : (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <IconButton
                type="button"
                label={`Recording actions for ${item.filename}`}
              >
                <Ellipsis />
              </IconButton>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onSelect={() => setOpen(true)}>
                Open transcript
              </DropdownMenuItem>
              {["txt", "srt", "json"].map((format) => (
                <DropdownMenuItem asChild key={format}>
                  <a
                    download
                    href={
                      fixture ? undefined : transcriptDownload(item.id, format)
                    }
                  >
                    {format === "txt"
                      ? "Download text"
                      : format === "srt"
                        ? "Download subtitles (.srt)"
                        : "Download details (.json)"}
                  </a>
                </DropdownMenuItem>
              ))}
              <DropdownMenuItem asChild>
                <a
                  download
                  href={fixture ? undefined : `/api/attachments/${item.id}`}
                >
                  Download audio
                </a>
              </DropdownMenuItem>
              <DropdownMenuItem onSelect={() => void retry("mix")}>
                Transcribe again
              </DropdownMenuItem>
              <DropdownMenuItem onSelect={() => void retry("split")}>
                Transcribe again, one speaker per channel
              </DropdownMenuItem>
              {onRemove && (
                <DropdownMenuItem onSelect={onRemove}>Remove</DropdownMenuItem>
              )}
            </DropdownMenuContent>
          </DropdownMenu>
        )}
        {ready && tooLarge && (
          <Button
            type="button"
            variant="outline"
            onClick={() =>
              !fixture &&
              window.dispatchEvent(new Event("workbench:choose-model"))
            }
          >
            Choose model
          </Button>
        )}
        {!ready && onRemove && (
          <IconButton
            label={`Remove ${item.filename}`}
            type="button"
            onClick={onRemove}
          >
            <X />
          </IconButton>
        )}
      </div>
      <TranscriptSheet
        attachment={item}
        open={open}
        onOpenChange={setOpen}
        fixture={fixture}
      />
    </>
  );
}
