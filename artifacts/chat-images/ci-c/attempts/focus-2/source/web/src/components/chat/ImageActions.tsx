import { useState } from "react";
import {
  Download,
  Copy,
  Info,
  MoreHorizontal,
  Sparkles,
  Pencil,
} from "lucide-react";
import { api } from "@/lib/api";
import { type ImageJob, receiveImages } from "@/lib/image-events";
import { useCopyFeedback } from "@/hooks/useCopyFeedback";
import { CopyFeedback } from "./CopyFeedback";
import { Button } from "@/components/ui/button";
import { IconButton } from "@/components/app/IconButton";
import { FileSaveDialog } from "@/components/app/FileSaveDialog";
import {
  Dialog,
  DialogContent,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from "@/components/ui/dropdown-menu";
import { toast } from "sonner";
export type ImageIteration = (
  job: ImageJob,
  action: "more" | "refine" | "ask",
  position: number,
) => void;
export function ImageActions({
  job,
  position = 1,
  onIteration,
  vision = false,
  viewer = false,
  preview = false,
}: {
  job: ImageJob;
  position?: number;
  onIteration?: ImageIteration;
  vision?: boolean;
  viewer?: boolean;
  preview?: boolean;
}) {
  const [saving, setSaving] = useState(false),
    [details, setDetails] = useState(false),
    [removing, setRemoving] = useState(false),
    [busy, setBusy] = useState(false);
  const copy = useCopyFeedback();
  return (
    <>
      <div className={viewer ? "image-viewer-actions" : "image-frame-actions"}>
        <IconButton label="Save image" onClick={() => setSaving(true)}>
          <Download />
          {viewer && <span>Save</span>}
        </IconButton>
        <IconButton
          label="More like this"
          disabled={!onIteration}
          onClick={() => onIteration?.(job, "more", position)}
        >
          <Sparkles />
          {viewer && <span>More like this</span>}
        </IconButton>
        <IconButton
          label="Refine image"
          disabled={!onIteration}
          onClick={() => onIteration?.(job, "refine", position)}
        >
          <Pencil />
          {viewer && <span>Refine</span>}
        </IconButton>
        <IconButton
          label="Copy image prompt"
          onClick={() => void copy.copy(job.prompt)}
        >
          {!copy.copied && <Copy />}
          <CopyFeedback {...copy} />
          {viewer && <span>Copy prompt</span>}
        </IconButton>
        <IconButton label="Image details" onClick={() => setDetails(true)}>
          <Info />
          {viewer && <span>Details</span>}
        </IconButton>
        {!viewer && (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <IconButton label="More image actions">
                <MoreHorizontal />
              </IconButton>
            </DropdownMenuTrigger>
            <DropdownMenuContent>
              {vision && onIteration && (
                <DropdownMenuItem
                  onSelect={() => onIteration(job, "ask", position)}
                >
                  Ask about it
                </DropdownMenuItem>
              )}
              <DropdownMenuItem onSelect={() => setRemoving(true)}>
                Remove image
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        )}
      </div>
      {saving && (
        <FileSaveDialog
          title="Save image"
          closeLabel="Close image save"
          initial="png"
          options={[
            {
              format: "png",
              label: "Image (.png)",
              url: `/api/images/jobs/${job.id}/output/png`,
              filename: `Atelier-${job.id.slice(0, 8)}.png`,
            },
            {
              format: "json",
              label: "Details (.json)",
              url: `/api/images/jobs/${job.id}/output/json`,
              filename: `Atelier-${job.id.slice(0, 8)}.json`,
            },
          ]}
          onClose={() => setSaving(false)}
          preview={preview ? "ready" : undefined}
        />
      )}
      <Dialog open={details} onOpenChange={setDetails}>
        <DialogContent>
          <DialogTitle>Image details</DialogTitle>
          <DialogDescription>Exact inputs and saved output.</DialogDescription>
          <p className="break-words whitespace-pre-wrap text-sm">
            {job.prompt}
          </p>
          <dl className="space-y-2 text-sm">
            {[
              ["Seed", job.seed],
              ["Model", "FLUX.2 klein 4B"],
              ["Size", "1024 × 1024"],
              ["Steps", job.steps],
              [
                "Time",
                job.elapsed_seconds == null
                  ? "Unavailable"
                  : `${job.elapsed_seconds.toFixed(1)} s`,
              ],
              ["File size", `${(job.image_bytes / 1e6).toFixed(2)} MB`],
              ["Created", new Date(job.created_at).toLocaleString()],
            ].map(([label, value]) => (
              <div key={label} className="flex gap-3">
                <dt className="text-fg-3">{label}</dt>
                <dd className="break-words">{value}</dd>
              </div>
            ))}
          </dl>
        </DialogContent>
      </Dialog>
      <Dialog
        open={removing}
        onOpenChange={(open) => !busy && setRemoving(open)}
      >
        <DialogContent>
          <DialogTitle>Remove this image?</DialogTitle>
          <DialogDescription>
            This removes the image from your Mac and every chat that shows it.
            Its prompt, job history and existing backups are kept.
          </DialogDescription>
          <div className="flex justify-end gap-2">
            <Button
              variant="outline"
              disabled={busy}
              onClick={() => setRemoving(false)}
            >
              Keep
            </Button>
            <Button
              disabled={busy}
              onClick={async () => {
                if (preview) {
                  setRemoving(false);
                  return;
                }
                setBusy(true);
                try {
                  await api(
                    `/images/jobs/${job.id}/output`,
                    undefined,
                    "DELETE",
                  );
                  receiveImages([
                    await api<ImageJob>(`/images/jobs/${job.id}`),
                  ]);
                  setRemoving(false);
                } catch {
                  toast.error("Couldn't remove this image. Try again.");
                } finally {
                  setBusy(false);
                }
              }}
            >
              Remove
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}
