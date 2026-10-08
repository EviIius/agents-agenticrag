import { lazy, Suspense, useState } from "react";
import { FileText, X } from "lucide-react";
import type { Attachment, Model } from "@/lib/api";
import { IconButton } from "@/components/app/IconButton";
const DocumentSheet = lazy(() => import("./DocumentSheet"));
export function DocumentChip({
  attachment,
  model,
  onRemove,
  fixture,
}: {
  attachment: Attachment;
  model?: Model;
  onRemove?: () => void;
  fixture?: { text: string } | "loading" | "error";
}) {
  const [open, setOpen] = useState(false);
  const meta = attachment.document;
  const maximum = model?.context_length ?? 8192;
  const tooLarge =
    (meta?.token_estimate ?? 0) >
    maximum - Math.max(1024, Math.min(8192, maximum * 0.25)) - 256;
  return (
    <>
      <div
        data-slot="document-chip"
        className={`mb-2 flex max-w-full items-center gap-2 rounded-lg border p-2 ${tooLarge ? "border-warning text-warning" : "border-line bg-surface-2"}`}
      >
        <FileText className="size-4 shrink-0" aria-hidden />
        <button
          type="button"
          className="min-h-11 min-w-0 flex-1 text-left text-xs"
          aria-label={`Review document ${attachment.filename}`}
          onClick={() => setOpen(true)}
        >
          <span className="block truncate font-medium">
            {attachment.filename}
          </span>
          <span className="block break-words text-fg-2">
            {meta?.pages != null
              ? `${meta.pages.toLocaleString()} ${meta.pages === 1 ? "page" : "pages"} · `
              : "Word document · "}
            ≈{meta?.token_estimate.toLocaleString()} tokens
          </span>
          {tooLarge && (
            <span className="block break-words text-warning">
              About {meta?.token_estimate.toLocaleString()} tokens: more than{" "}
              {model?.display_name ?? "this model"} can take (
              {maximum.toLocaleString()}). Choose a model with a larger context.
            </span>
          )}
        </button>
        {onRemove && (
          <IconButton
            type="button"
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
