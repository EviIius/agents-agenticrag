import type { Attachment } from "@/lib/api";
import {
  recordingDownloadURL,
  recordingFilename,
  recordingFormats,
  type RecordingDownload,
  type RecordingFormat,
} from "@/lib/recording-download";
import {
  FileSaveDialog,
  type DownloadPreview,
} from "@/components/app/FileSaveDialog";
export type { DownloadPreview } from "@/components/app/FileSaveDialog";
export function RecordingDownloadDialog({
  attachment,
  initial,
  open = true,
  onClose,
  includeAudio = false,
  preview,
}: {
  attachment: Attachment;
  initial: RecordingDownload;
  open?: boolean;
  onClose: () => void;
  includeAudio?: boolean;
  preview?: DownloadPreview;
}) {
  const formats: RecordingFormat[] = includeAudio
    ? ["txt", "srt", "json", "audio"]
    : ["txt", "srt", "json"];
  return (
    <FileSaveDialog
      open={open}
      initial={initial.format}
      onClose={onClose}
      preview={preview}
      title="Save recording"
      closeLabel="Close recording download"
      options={formats.map((format) => ({
        format,
        label: recordingFormats[format],
        url: recordingDownloadURL(attachment.id, format, initial.variant),
        filename: recordingFilename(attachment, format),
      }))}
    />
  );
}
