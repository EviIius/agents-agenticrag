import { FileBadge, FileName } from "./AttachmentTile";
import { failureCopy, failureDetail } from "@/lib/errors";
import { contextBudget } from "@/lib/context-budget";
import { useCleanup } from "@/hooks/useCleanup";
import { useOverlaySession } from "@/hooks/useOverlaySession";
import { useEffect, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import {
  AudioLines,
  FileText,
  Ellipsis,
  Square,
  Trash2,
  X,
} from "lucide-react";
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
  kind?: import("@/lib/file-kinds").FileKind;
  failed?: boolean;
  reason?: string;
  phase?: "preparing" | "uploading" | "reading" | "error";
  retryable?: boolean;
  format?: string;
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
      {upload.kind === "document" ? (
        <FileText className="size-4 shrink-0" />
      ) : (
        <AudioLines className="size-4 shrink-0" />
      )}
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
            : upload.kind === "document" && upload.percent === 100
              ? "Reading document…"
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
  reserve,
  compact = false,
}: {
  attachment: Attachment;
  model?: Model;
  onRemove?: () => void;
  fixture?: Transcript;
  reserve?: number;
  compact?: boolean;
}) {
  const live = useTranscripts((state) => state.attachments[attachment.id]);
  const item = fixture ? attachment : (live ?? attachment);
  const meta = item.transcript;
  const cleanup = useCleanup(item, model, !!fixture);
  const cleaning = meta?.cleanup?.status === "running";
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
  const budget = contextBudget(model, reserve);
  const tooLarge = (meta?.token_estimate ?? 0) > budget.available;
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
  if (cleaning)
    label = `Cleaning up… ${meta?.cleanup?.done ?? 0} of ${meta?.cleanup?.chunks ?? 0}`;
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
      toast.error(failureCopy(error), { description: failureDetail(error) });
    }
  };
  const cancel = () => {
    if (!fixture)
      void api(`/attachments/${item.id}/cancel`, {}).catch((error) =>
        toast.error(failureCopy(error), { description: failureDetail(error) }),
      );
  };
  return (
    <>
      <div
        data-slot="audio-chip"
        data-live={meta?.status === "transcribing" || cleaning || undefined}
        data-testid="audio-chip"
        className={
          compact
            ? "attachment-file-card attachment-audio-card"
            : `mb-2 flex max-w-full flex-wrap items-center gap-2 rounded-lg border p-2 ${tooLarge && ready ? "border-warning text-warning" : "border-line bg-surface-2"}`
        }
        data-attachment-tile={compact || undefined}
        data-issue={tooLarge && ready ? "warning" : undefined}
      >
        {compact ? (
          <FileBadge name={item.filename} kind="audio" />
        ) : (
          <AudioLines className="size-4 shrink-0" aria-hidden />
        )}
        <button
          type="button"
          className={
            compact
              ? "attachment-audio-open"
              : "min-h-11 min-w-0 flex-1 text-left text-xs"
          }
          disabled={!ready}
          aria-label={
            ready ? `Open transcript for ${item.filename}` : item.filename
          }
          onClick={() => setOpen(true)}
          aria-describedby={compact ? `audio-meta-${item.id}` : undefined}
          title={label}
        >
          {compact ? (
            <FileName name={item.filename} />
          ) : (
            <span className="block truncate font-medium">{item.filename}</span>
          )}
          <span
            data-slot="activity-label"
            data-live={meta?.status === "transcribing" || cleaning || undefined}
            className={
              compact ? "attachment-meta" : "block break-words text-fg-2"
            }
            role="status"
          >
            {compact && ready && !!meta?.word_count && !cleaning
              ? `${meta?.cleanup?.status === "ready" ? "Cleaned" : "Ready"} · ${duration(meta?.duration_seconds ?? 0)}`
              : label}
          </span>
          {compact && (
            <span id={`audio-meta-${item.id}`} className="sr-only">
              {label}
            </span>
          )}
          {item.audio_available === false && (
            <span className={compact ? "sr-only" : "block text-fg-3"}>
              {ready
                ? "Transcript saved · audio removed"
                : "Audio removed · upload again to retry"}
            </span>
          )}
        </button>
        {cleaning && !compact ? (
          <IconButton
            type="button"
            label="Cancel clean-up"
            disabled={cleanup.busy}
            onClick={cleanup.cancel}
          >
            <Square />
          </IconButton>
        ) : !compact &&
          meta &&
          ["queued", "transcribing"].includes(meta.status) ? (
          <IconButton
            type="button"
            label="Cancel transcription"
            onClick={cancel}
          >
            <Square />
          </IconButton>
        ) : !compact && !ready && item.audio_available !== false ? (
          <Button type="button" variant="outline" onClick={() => void retry()}>
            Retry
          </Button>
        ) : ready || compact ? (
          <DropdownMenu modal={false}>
            <DropdownMenuTrigger asChild>
              <IconButton
                type="button"
                label={`Recording actions for ${item.filename}`}
                className={compact ? "attachment-card-menu" : undefined}
              >
                <Ellipsis />
              </IconButton>
            </DropdownMenuTrigger>
            <DropdownMenuContent
              align="end"
              className="max-w-[calc(100vw-2rem)]"
            >
              {cleaning && (
                <DropdownMenuItem onSelect={cleanup.cancel}>
                  Cancel clean-up
                </DropdownMenuItem>
              )}
              {meta && ["queued", "transcribing"].includes(meta.status) && (
                <DropdownMenuItem onSelect={cancel}>
                  Cancel transcription
                </DropdownMenuItem>
              )}
              {compact &&
                !ready &&
                meta &&
                ["failed", "cancelled"].includes(meta.status) &&
                item.audio_available !== false && (
                  <DropdownMenuItem onSelect={() => void retry()}>
                    Retry
                  </DropdownMenuItem>
                )}
              <DropdownMenuItem
                disabled={!ready}
                onSelect={() => setOpen(true)}
              >
                Open transcript
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              {(ready
                ? [
                    "txt",
                    "srt",
                    "json",
                    ...(item.audio_available !== false ? ["audio"] : []),
                  ]
                : []
              ).map((format) => (
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
              {ready && model && !!meta?.word_count && (
                <DropdownMenuItem
                  disabled={cleanup.busy}
                  onSelect={cleanup.start}
                >
                  Clean up with {model.display_name}
                </DropdownMenuItem>
              )}
              <DropdownMenuItem
                disabled={
                  item.audio_available === false ||
                  cleaning ||
                  meta?.status === "queued" ||
                  meta?.status === "transcribing"
                }
                onSelect={() => void retry("mix")}
              >
                Transcribe again
              </DropdownMenuItem>
              <DropdownMenuItem
                className="whitespace-normal"
                disabled={
                  item.audio_available === false ||
                  cleaning ||
                  meta?.status === "queued" ||
                  meta?.status === "transcribing"
                }
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
        {!compact && ready && tooLarge && (
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
        {!compact && !ready && onRemove && (
          <IconButton
            label={`Remove ${item.filename}`}
            type="button"
            onClick={onRemove}
          >
            <Trash2 />
          </IconButton>
        )}
        {!compact && ready && tooLarge && (
          <p className="w-full break-words text-xs text-warning">
            About {meta?.token_estimate?.toLocaleString()} input tokens exceeds
            the {budget.available.toLocaleString()}-token input allowance.{" "}
            {budget.reserve.toLocaleString()} tokens are reserved for the
            response. Choose a model with a larger context or lower Max output
            tokens in Chat controls.
          </p>
        )}
        {compact && onRemove && (
          <button
            type="button"
            className="attachment-remove"
            aria-label={`Remove ${item.filename}`}
            onClick={onRemove}
          >
            <X />
          </button>
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
        model={model}
      />
    </>
  );
}
