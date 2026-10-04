import { useOverlaySession } from "@/hooks/useOverlaySession";
import { useEffect, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { AudioLines, Ellipsis, Square, Trash2, X } from "lucide-react";
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
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { TranscriptSheet, duration } from "./TranscriptSheet";
import { RecordingDownloadDialog } from "./RecordingDownloadDialog";
import type {
  RecordingDownload,
  RecordingFormat,
} from "@/lib/recording-download";

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
      data-slot="attachment-chip"
      role="status"
      className="mb-2 flex max-w-full items-center gap-2 rounded-lg border border-line bg-surface-2 p-2 text-xs"
    >
      <AudioLines className="size-4 shrink-0" />
      <div className="min-w-0 flex-1">
        <p className="truncate">{upload.filename}</p>
        <div
          data-slot="upload-progress"
          role="progressbar"
          aria-label="Upload progress"
          aria-valuenow={upload.percent}
          aria-valuemin={0}
          aria-valuemax={100}
        >
          <span
            style={{ width: `${Math.min(100, Math.max(0, upload.percent))}%` }}
          />
        </div>
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
  const [download, setDownload] = useState<RecordingDownload | null>(null);
  const downloadSession = useOverlaySession(download);
  const [open, setOpen] = useState(false),
    [clock, setClock] = useState(Date.now());
  useEffect(() => {
    if (!fixture) attachTranscription(attachment);
  }, [attachment, fixture]);
  useEffect(() => {
    if (fixture) return;
    const refresh = () => {
      detachTranscription(item.id);
      void api<Attachment>(`/attachments/${item.id}/info`).then(
        attachTranscription,
        () => undefined,
      );
    };
    window.addEventListener("workbench:audio-cleared", refresh);
    return () => window.removeEventListener("workbench:audio-cleared", refresh);
  }, [attachment, fixture, item.id]);
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
        data-slot="audio-chip"
        data-live={meta?.status === "transcribing" || undefined}
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
          <span
            data-slot="activity-label"
            data-live={meta?.status === "transcribing" || undefined}
            className="block break-words text-fg-2"
            role="status"
          >
            {label}
          </span>
          {item.audio_available === false && (
            <span className="block text-fg-3">
              {ready
                ? "Transcript saved · audio removed"
                : "Audio removed · upload again to retry"}
            </span>
          )}
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
            <Square />
          </IconButton>
        ) : !ready && item.audio_available !== false ? (
          <Button type="button" variant="outline" onClick={() => void retry()}>
            Retry
          </Button>
        ) : ready ? (
          <DropdownMenu modal={false}>
            <DropdownMenuTrigger asChild>
              <IconButton
                type="button"
                label={`Recording actions for ${item.filename}`}
              >
                <Ellipsis />
              </IconButton>
            </DropdownMenuTrigger>
            <DropdownMenuContent
              align="end"
              className="max-w-[calc(100vw-2rem)]"
            >
              <DropdownMenuItem onSelect={() => setOpen(true)}>
                Open transcript
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              {[
                "txt",
                "srt",
                "json",
                ...(item.audio_available !== false ? ["audio"] : []),
              ].map((format) => (
                <DropdownMenuItem
                  key={format}
                  onSelect={() =>
                    setDownload({ format: format as RecordingFormat })
                  }
                >
                  {format === "txt"
                    ? "Download text"
                    : format === "srt"
                      ? "Download subtitles (.srt)"
                      : format === "json"
                        ? "Download details (.json)"
                        : "Download audio"}
                </DropdownMenuItem>
              ))}
              <DropdownMenuSeparator />
              <DropdownMenuItem
                disabled={item.audio_available === false}
                onSelect={() => void retry("mix")}
              >
                Transcribe again
              </DropdownMenuItem>
              <DropdownMenuItem
                className="whitespace-normal"
                disabled={item.audio_available === false}
                onSelect={() => void retry("split")}
              >
                Transcribe again, one speaker per channel
              </DropdownMenuItem>
              {item.audio_available === false && (
                <p className="max-w-64 px-2 py-2 text-xs text-fg-2">
                  Audio removed to save space. Upload it again to transcribe.
                </p>
              )}
              {onRemove && (
                <>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem variant="destructive" onSelect={onRemove}>
                    Remove
                  </DropdownMenuItem>
                </>
              )}
            </DropdownMenuContent>
          </DropdownMenu>
        ) : null}
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
            <Trash2 />
          </IconButton>
        )}
      </div>
      {downloadSession.value && (
        <RecordingDownloadDialog
          open={downloadSession.open}
          key={downloadSession.sequence}
          attachment={item}
          initial={downloadSession.value}
          includeAudio={item.audio_available !== false}
          preview={fixture ? "ready" : undefined}
          onClose={() => setDownload(null)}
        />
      )}
      <TranscriptSheet
        attachment={item}
        open={open}
        onOpenChange={setOpen}
        fixture={fixture}
      />
    </>
  );
}
