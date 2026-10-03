import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { toast } from "sonner";
import { X, ChevronDown } from "lucide-react";
import { api, type Attachment, type Transcript } from "@/lib/api";
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
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

export function duration(seconds: number) {
  const s = Math.max(0, Math.floor(seconds));
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
}
export function transcriptDownload(
  id: string,
  format: string,
  variant = "best",
) {
  return `/api/attachments/${id}/transcript/download?format=${format}&variant=${variant}`;
}
export function TranscriptSheet({
  attachment,
  open,
  onOpenChange,
  fixture,
}: {
  attachment: Attachment;
  open: boolean;
  onOpenChange: (value: boolean) => void;
  fixture?: Transcript;
}) {
  const phone = useMediaQuery("(max-width:639px)");
  const [view, setView] = useState("Text"),
    [version, setVersion] = useState("original");
  const fetched = useQuery({
    queryKey: ["transcript", attachment.id, attachment.transcript?.started_at],
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
        ? data?.cleaned_text
        : data?.text;
  const title = phone ? DrawerTitle : SheetTitle;
  const description = phone ? DrawerDescription : SheetDescription;
  const Title = title,
    Description = description;
  const header = (
    <div className="relative shrink-0 border-b border-line p-5 pr-16">
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
        onClick={() => onOpenChange(false)}
      >
        <X />
      </IconButton>
    </div>
  );
  const body = (
    <>
      <div className="min-h-0 flex-1 space-y-4 overflow-y-auto p-5">
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
          onClick={() => {
            void navigator.clipboard.writeText(text ?? "").then(
              () => toast.success("Transcript copied"),
              () => toast.error("Couldn't copy transcript"),
            );
          }}
        >
          Copy
        </Button>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" disabled={!data}>
              Download <ChevronDown className="size-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent>
            {["txt", "srt", "json"].map((format) => (
              <DropdownMenuItem key={format} asChild>
                <a
                  download
                  href={
                    fixture
                      ? undefined
                      : transcriptDownload(
                          attachment.id,
                          format,
                          format === "srt" && version === "best"
                            ? "original"
                            : version,
                        )
                  }
                >
                  Download{" "}
                  {format === "txt"
                    ? "text"
                    : format === "srt"
                      ? "subtitles (.srt)"
                      : "details (.json)"}
                </a>
              </DropdownMenuItem>
            ))}
          </DropdownMenuContent>
        </DropdownMenu>
      </footer>
    </>
  );
  const setOpen = (value: boolean) => {
    if (value && phone) useUI.getState().set({ sidebar: false, panel: false });
    onOpenChange(value);
  };
  return phone ? (
    <Drawer open={open} onOpenChange={setOpen}>
      <DrawerContent className="h-[85dvh] overflow-hidden">
        <DrawerHeader className="p-0">{header}</DrawerHeader>
        {body}
      </DrawerContent>
    </Drawer>
  ) : (
    <Sheet open={open} onOpenChange={setOpen}>
      <SheetContent
        className="flex w-full flex-col gap-0 overflow-hidden p-0 sm:max-w-xl"
        showCloseButton={false}
      >
        {header}
        {body}
      </SheetContent>
    </Sheet>
  );
}
