import { FileBadge, FileName } from "./AttachmentTile";
import { lazy, Suspense, useState } from "react";
import { FileText, X } from "lucide-react";
import type { Attachment, Model } from "@/lib/api";
import { contextBudget } from "@/lib/context-budget";
import { IconButton } from "@/components/app/IconButton";
const DocumentSheet = lazy(() => import("./DocumentSheet"));
export function DocumentChip({
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
  fixture?: { text: string } | "loading" | "error";
  reserve?: number;
  compact?: boolean;
}) {
  const [open, setOpen] = useState(false);
  const meta = attachment.document;
  const budget = contextBudget(model, reserve);
  const tooLarge = (meta?.token_estimate ?? 0) > budget.available;
  return (
    <>
      <div
        data-slot="document-chip"
        className={
          compact
            ? "attachment-file-card attachment-document-card"
            : `mb-2 flex max-w-full items-center gap-2 rounded-lg border p-2 ${tooLarge ? "border-warning text-warning" : "border-line bg-surface-2"}`
        }
        data-attachment-tile={compact || undefined}
        data-issue={tooLarge ? "warning" : undefined}
      >
        {compact ? (
          <FileBadge name={attachment.filename} kind="document" />
        ) : (
          <FileText className="size-4 shrink-0" aria-hidden />
        )}
        <button
          type="button"
          className={
            compact
              ? "attachment-audio-open"
              : "min-h-11 min-w-0 flex-1 text-left text-xs"
          }
          aria-label={`Review document ${attachment.filename}`}
          onClick={() => setOpen(true)}
        >
          {compact ? (
            <FileName name={attachment.filename} />
          ) : (
            <span className="block truncate font-medium">
              {attachment.filename}
            </span>
          )}
          <span
            className={
              compact ? "attachment-meta" : "block break-words text-fg-2"
            }
          >
            {meta?.pages != null
              ? `${meta.pages.toLocaleString()} ${meta.pages === 1 ? "page" : "pages"} · `
              : "Word document · "}
            ≈{meta?.token_estimate.toLocaleString()} tokens
          </span>
          {!compact && tooLarge && (
            <span className="block break-words text-warning">
              About {meta?.token_estimate.toLocaleString()} input tokens exceeds
              the {budget.available.toLocaleString()}-token input allowance.{" "}
              {budget.reserve.toLocaleString()} tokens are reserved for the
              response. Choose a model with a larger context or lower Max output
              tokens in Chat controls.
            </span>
          )}
        </button>
        {onRemove && (
          <IconButton
            type="button"
            className={compact ? "attachment-remove" : undefined}
            label={`Remove ${attachment.filename}`}
            onClick={onRemove}
          >
            <X />
          </IconButton>
        )}
      </div>
      {open && (
        <Suspense fallback={<p role="status">Opening document…</p>}>
          <DocumentSheet
            attachment={attachment}
            open={open}
            onOpenChange={setOpen}
            fixture={fixture}
          />
        </Suspense>
      )}
    </>
  );
}
