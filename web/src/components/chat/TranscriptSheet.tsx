import { useOverlaySession } from "@/hooks/useOverlaySession";
import { useCopyFeedback } from "@/hooks/useCopyFeedback";
import { CopyFeedback } from "./CopyFeedback";
import { useCleanup } from "@/hooks/useCleanup";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { X, Download } from "lucide-react";
import { RecordingDownloadDialog } from "./RecordingDownloadDialog";
import type { RecordingDownload } from "@/lib/recording-download";
import { api, type Attachment, type Transcript, type Model } from "@/lib/api";
import { useMediaQuery } from "@/hooks/useMediaQuery";
import { useUI } from "@/stores/ui";
import { Button } from "@/components/ui/button";
import { IconButton } from "@/components/app/IconButton";
import {
  Sheet,
  SheetContent,
  SheetTitle,
  SheetDescription,
} from "@/components/ui/sheet";
import {
  Drawer,
  DrawerContent,
  DrawerHeader,
  DrawerTitle,
  DrawerDescription,
} from "@/components/ui/drawer";
export function duration(seconds: number) {
  const s = Math.max(0, Math.floor(seconds));
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
}
export function TranscriptSheet({
  attachment,
  open,
  onOpenChange,
  fixture,
  model,
}: {
  attachment: Attachment;
  open: boolean;
  onOpenChange: (value: boolean) => void;
  fixture?: Transcript;
  model?: Model;
}) {
  const cleanup = useCleanup(attachment, model, !!fixture);
  const feedback = useCopyFeedback();
  const phone = useMediaQuery("(max-width:639px)");
  const [download, setDownload] = useState<RecordingDownload | null>(null);
  const downloadSession = useOverlaySession(download);
  const [view, setView] = useState("Text"),
    [version, setVersion] = useState("best");
  const fetched = useQuery({
    queryKey: [
      "transcript",
      attachment.id,
      attachment.transcript?.started_at,
      attachment.transcript?.cleanup?.status,
      attachment.transcript?.cleanup?.elapsed_seconds,
    ],
    queryFn: () => api<Transcript>(`/attachments/${attachment.id}/transcript`),
    enabled: open && !fixture,
    staleTime: Infinity,
  });
  const data = fixture ?? fetched.data;
  const meta = attachment.transcript;
  const text =
    version === "raw"
      ? data?.raw_text
      : version === "best"
        ? (data?.cleaned_text ?? data?.text)
        : data?.text;
  const title = phone ? DrawerTitle : SheetTitle;
  const description = phone ? DrawerDescription : SheetDescription;
  const Title = title,
    Description = description;
  const header = (
    <div className="relative shrink-0 border-b border-line p-5 pr-16 text-left">
      <Title className="break-words text-base">{attachment.filename}</Title>
      <Description>
        {duration(meta?.duration_seconds ?? 0)} ·{" "}
        {meta?.word_count?.toLocaleString()} words ·{" "}
        {meta?.engine_model ?? "Whisper"} · transcribed in{" "}
        {Math.round(meta?.elapsed_seconds ?? 0)} s
      </Description>
      <IconButton
        label="Close transcript"
        className="absolute right-3 top-3"
        onClick={() => {
          setDownload(null);
          onOpenChange(false);
        }}
      >
        <X />
      </IconButton>
    </div>
  );
  const cleaning = meta?.cleanup?.status === "running";
  const body = (
    <>
      <div className="min-h-0 flex-1 space-y-4 overflow-y-auto p-5">
        {cleaning && (
          <p role="status" className="text-sm">
            Cleaning up… {meta.cleanup!.done} of {meta.cleanup!.chunks}
          </p>
        )}
        {meta?.cleanup?.status === "failed" && (
          <p role="alert" className="text-sm text-danger">
            {meta.cleanup.error?.message === "Cancelled"
              ? "Clean-up cancelled. The transcript is unchanged."
              : `Clean-up failed: ${meta.cleanup.error?.message ?? "The local model could not finish."}. The transcript is unchanged.`}
          </p>
        )}
        {meta?.cleanup?.status === "ready" &&
          meta.cleanup.kept_original > 0 && (
            <p role="status" className="text-sm text-warning">
              {meta.cleanup.kept_original} of {meta.cleanup.chunks} sections
              were left as transcribed because the clean-up changed their
              wording.
            </p>
          )}

        {fetched.isError && !fixture ? (
          <p role="alert">
            Couldn't open the transcript.{" "}
            <Button variant="link" onClick={() => void fetched.refetch()}>
              Retry
            </Button>
          </p>
        ) : !data ? (
          <p role="status">Opening transcript…</p>
        ) : (
          <>
            <div className="flex flex-wrap gap-2" aria-label="Transcript view">
              {["Text", "Timestamps"].map((label) => (
                <Button
                  key={label}
                  variant={view === label ? "secondary" : "outline"}
                  aria-pressed={view === label}
                  onClick={() => setView(label)}
                >
                  {label}
                </Button>
              ))}
            </div>
            {data.cleaned_text != null && (
              <div
                className="flex flex-wrap gap-2"
                aria-label="Transcript version"
              >
                {[
                  ["best", "Cleaned"],
                  ["original", "As transcribed"],
                  ["raw", "Raw Whisper"],
                ].map(([key, label]) => (
                  <Button
                    key={key}
                    variant={version === key ? "secondary" : "outline"}
                    aria-pressed={version === key}
                    onClick={() => setVersion(key)}
                  >
                    {label}
                  </Button>
                ))}
              </div>
            )}
            {view === "Text" ? (
              <pre className="whitespace-pre-wrap break-words font-sans text-sm leading-6">
                {text || "No speech found"}
              </pre>
            ) : (
              <>
                <p className="text-xs text-fg-2">
                  Timestamps use the original transcript.
                </p>
                <ol className="space-y-3 text-sm leading-6">
                  {data.segments.map((segment, i) => (
                    <li key={i} className="whitespace-pre-wrap break-words">
                      <span className="text-fg-3">
                        [{duration(segment.start)}]
                        {segment.speaker ? ` ${segment.speaker}` : ""}{" "}
                      </span>
                      {version === "raw" ? segment.raw_text : segment.text}
                    </li>
                  ))}
                </ol>
              </>
            )}
            {!!(
              meta?.warnings?.length ||
              data.corrections.length ||
              meta?.cleanup
            ) && (
              <details>
                <summary className="min-h-11 cursor-pointer py-3 text-sm">
                  Notes
                </summary>
                <ul className="space-y-2 text-sm text-fg-2">
                  {meta?.warnings?.map((warning) => (
                    <li key={warning}>{warning}</li>
                  ))}
                  {meta?.cleanup?.status === "ready" && (
                    <li>
                      Cleaned with {meta.cleanup.model?.display_name};{" "}
                      {meta.cleanup.chunks} sections,{" "}
                      {meta.cleanup.kept_original} kept as transcribed,{" "}
                      {meta.cleanup.changed_words} changed words
                      {meta.cleanup.elapsed_seconds != null
                        ? `, ${Math.round(meta.cleanup.elapsed_seconds)} s`
                        : ""}
                      .
                    </li>
                  )}
                  {data.corrections.map((correction, i) => (
                    <li key={i}>
                      {correction.found} → {correction.replaced_with} ×
                      {correction.count}
                    </li>
                  ))}
                </ul>
              </details>
            )}
          </>
        )}
      </div>
      <footer className="flex shrink-0 flex-wrap gap-2 border-t border-line p-4">
        <Button
          variant="outline"
          disabled={!data}
          aria-label="Copy"
          onClick={() => void feedback.copy(text ?? "")}
        >
          <CopyFeedback {...feedback} /> Copy
        </Button>
        <Button
          variant="outline"
          disabled={!data}
          onClick={() => setDownload({ format: "txt", variant: version })}
        >
          <Download className="size-4" /> Download
        </Button>
        {cleaning ? (
          <Button
            variant="outline"
            disabled={cleanup.busy}
            onClick={cleanup.cancel}
          >
            Cancel clean-up
          </Button>
        ) : model && !!meta?.word_count ? (
          <Button
            variant="outline"
            disabled={cleanup.busy || !data}
            onClick={cleanup.start}
          >
            Clean up with {model.display_name}
          </Button>
        ) : null}
        {data?.cleaned_text != null && !cleaning && (
          <Button
            variant="ghost"
            disabled={cleanup.busy}
            onClick={() => {
              setVersion("original");
              cleanup.discard();
            }}
          >
            Discard clean-up
          </Button>
        )}
      </footer>
      {downloadSession.value && (
        <RecordingDownloadDialog
          open={downloadSession.open}
          key={downloadSession.sequence}
          attachment={attachment}
          initial={downloadSession.value}
          preview={fixture ? "ready" : undefined}
          onClose={() => setDownload(null)}
        />
      )}
    </>
  );
  const setOpen = (value: boolean) => {
    if (value && phone) useUI.getState().set({ sidebar: false, panel: false });
    if (!value) setDownload(null);
    onOpenChange(value);
  };
  return phone ? (
    <Drawer open={open} onOpenChange={setOpen}>
      <DrawerContent className="h-[85dvh] overflow-clip">
        <DrawerHeader className="p-0">{header}</DrawerHeader>
        {body}
      </DrawerContent>
    </Drawer>
  ) : (
    <Sheet open={open} onOpenChange={setOpen}>
      <SheetContent
        className="flex w-full flex-col gap-0 overflow-clip p-0 sm:max-w-xl"
        showCloseButton={false}
      >
        {header}
        {body}
      </SheetContent>
    </Sheet>
  );
}
