import config from "../../../../shared/config.json";
import { useEffect, useState, useRef } from "react";
import { Check, X } from "lucide-react";
import { useMediaQuery } from "@/hooks/useMediaQuery";
import { Button } from "@/components/ui/button";
import { IconButton } from "@/components/app/IconButton";
import {
  Dialog,
  DialogContent,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
export type DownloadPreview =
  | "ready"
  | "preparing"
  | "failed"
  | "sharing"
  | "cancelled"
  | "share-failed"
  | "returned";
export function FileSaveDialog({
  initial,
  options,
  title,
  description = "Choose a format before saving. You can cancel or change it here.",
  closeLabel,
  downloadLabel = "Download file",
  open = true,
  onClose,
  preview,
}: {
  initial: string;
  options: { format: string; label: string; url: string; filename: string }[];
  title: string;
  description?: string;
  closeLabel: string;
  downloadLabel?: string;
  open?: boolean;
  onClose: () => void;
  preview?: DownloadPreview;
}) {
  const choices = useRef<HTMLDivElement>(null);
  const phone = useMediaQuery("(max-width:639px)");
  const [format, setFormat] = useState(initial);
  const [prepared, setPrepared] = useState<{
    format: string;
    file?: File;
    error?: boolean;
  }>();
  const [attempt, setAttempt] = useState(0);
  const [sharing, setSharing] = useState(false);
  const busy = sharing || preview === "sharing";
  const [notice, setNotice] = useState("");
  const selectedOption = options.find((option) => option.format === format)!;
  const { url } = selectedOption;
  const selected = prepared?.format === format ? prepared : undefined;
  const filename = selected?.file?.name ?? selectedOption.filename;
  useEffect(() => {
    if (!open) return;
    const controller = new AbortController();
    setNotice("");
    setPrepared(undefined);
    // Original audio may be several GiB: leave it as a streamed browser download.
    if (format === "audio") return;
    if (preview) {
      if (preview !== "preparing" && preview !== "failed")
        setPrepared({
          format,
          file: new File(["Synthetic file preview."], selectedOption.filename, {
            type: "text/plain",
          }),
        });
      if (preview === "failed") setPrepared({ format, error: true });
      if (preview === "cancelled")
        setNotice("Save cancelled. You can choose another format or close.");
      if (preview === "share-failed")
        setNotice(
          "Couldn't open the save sheet. Try again or download separately.",
        );
      if (preview === "returned")
        setNotice(
          "Returned from the save sheet. You can choose another format or close.",
        );
      return;
    }
    void (async () => {
      try {
        const response = await fetch(url, { signal: controller.signal });
        if (!response.ok) throw new Error("Download unavailable");
        const blob = await response.blob();
        const encoded = response.headers
          .get("Content-Disposition")
          ?.match(/filename\*=UTF-8''([^;]+)/i)?.[1];
        const name = encoded
          ? decodeURIComponent(encoded)
          : selectedOption.filename;
        const file = new File([blob], name, { type: blob.type });
        if (!controller.signal.aborted) setPrepared({ format, file });
      } catch {
        if (!controller.signal.aborted) setPrepared({ format, error: true });
      }
    })();
    return () => controller.abort();
  }, [format, url, selectedOption.filename, attempt, preview, open]);
  let canShare = false;
  try {
    canShare = Boolean(
      phone &&
      selected?.file &&
      typeof navigator.share === "function" &&
      navigator.canShare?.({ files: [selected.file] }),
    );
  } catch {
    /* Some browsers reject unsupported file types in canShare. */
  }
  if (
    preview &&
    ["sharing", "cancelled", "share-failed", "returned"].includes(preview) &&
    format !== "audio"
  )
    canShare = true;
  const share = async () => {
    if (!selected?.file || preview) return;
    setSharing(true);
    setNotice("");
    try {
      // The file is already prepared: this call retains the button's activation.
      await navigator.share({ files: [selected.file] });
      setNotice(
        "Returned from the save sheet. You can choose another format or close.",
      );
    } catch (error) {
      setNotice(
        error instanceof DOMException && error.name === "AbortError"
          ? "Save cancelled. You can choose another format or close."
          : "Couldn't open the save sheet. Try again or download separately.",
      );
    } finally {
      setSharing(false);
    }
  };
  const available = format === "audio" || Boolean(selected?.file);
  const download = (
    <Button asChild variant={canShare ? "outline" : "default"}>
      <a
        href={url}
        download={filename}
        target="_blank"
        rel="noopener noreferrer"
        onClick={(event) => {
          if (preview) event.preventDefault();
          setNotice(
            `Download opened separately. ${config.APP_NAME} stays in this tab.`,
          );
        }}
      >
        {canShare ? "Download separately" : downloadLabel}
      </a>
    </Button>
  );
  return (
    <Dialog
      open={open}
      onOpenChange={(open) => {
        if (!open) onClose();
      }}
    >
      <DialogContent
        onOpenAutoFocus={(event) => {
          event.preventDefault();
          choices.current
            ?.querySelector<HTMLButtonElement>("button[aria-pressed=true]")
            ?.focus();
        }}
        inert={!open}
        showCloseButton={false}
        className="flex flex-col gap-0 overflow-clip p-0"
      >
        <header className="shrink-0 space-y-2 border-b border-line p-5 pr-16">
          <DialogTitle className="pr-12">{title}</DialogTitle>
          <DialogDescription>{description}</DialogDescription>
          <IconButton
            label={closeLabel}
            className="absolute right-3 top-3"
            onClick={onClose}
          >
            <X />
          </IconButton>
        </header>
        <div className="min-h-0 space-y-4 overflow-y-auto p-5">
          <div
            ref={choices}
            className="grid grid-cols-2 gap-2"
            aria-label="File format"
          >
            {options.map(({ format: choice, label }) => {
              return (
                <Button
                  key={choice}
                  variant={format === choice ? "default" : "outline"}
                  className="h-auto min-h-11 whitespace-normal px-3 py-2"
                  aria-pressed={format === choice}
                  disabled={busy}
                  onClick={() => setFormat(choice)}
                >
                  {format === choice && (
                    <Check aria-hidden="true" className="size-3.5" />
                  )}
                  <span className="min-w-0">{label}</span>
                </Button>
              );
            })}
          </div>
          <p
            className="break-words text-sm text-fg-2"
            aria-label="Download filename"
          >
            {filename}
          </p>
          {format === "audio" ? (
            <p className="text-sm text-fg-2">
              Original audio downloads separately to keep large recordings out
              of your phone's memory.
            </p>
          ) : selected?.error ? (
            <div role="alert" className="text-sm">
              <p>
                Couldn't prepare this file. You can retry, choose another format
                or cancel.
              </p>
              <Button
                variant="outline"
                onClick={() => setAttempt((value) => value + 1)}
              >
                Retry
              </Button>
            </div>
          ) : !available ? (
            <p role="status" className="text-sm text-fg-2">
              Preparing file…
            </p>
          ) : (
            <p className="text-sm text-fg-2">
              {canShare
                ? "Choose Save to Files in the share sheet, or cancel to return here."
                : phone
                  ? `The download opens separately. Keep this ${config.APP_NAME} tab open to return or choose another format.`
                  : "The download opens separately; this dialog stays available to change formats."}
            </p>
          )}
          {notice && (
            <p role="status" className="text-sm text-fg-2">
              {notice}
            </p>
          )}
        </div>
        <footer className="flex shrink-0 flex-wrap justify-end gap-2 border-t border-line p-4">
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          {canShare && (
            <Button disabled={busy} onClick={() => void share()}>
              {busy ? "Saving…" : "Save or share"}
            </Button>
          )}
          {available && !busy && download}
        </footer>
      </DialogContent>
    </Dialog>
  );
}
