import { useEffect, useState } from "react";
import {
  Download,
  Copy,
  Info,
  MoreHorizontal,
  RotateCcw,
  Square,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { api, type Message } from "@/lib/api";
import {
  imageActive,
  claimImageReveal,
  type ImageJob,
  useImageJobs,
  receiveImages,
} from "@/lib/image-events";
import { imageTurnStatus } from "@/lib/image-state";
import { siblings } from "@/lib/tree";
import { useCopyFeedback } from "@/hooks/useCopyFeedback";
import { useReducedMotion } from "@/hooks/useReducedMotion";
import { CopyFeedback } from "./CopyFeedback";
import { AtelierMark } from "./AtelierMark";
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

export function ImageBranches({
  message,
  all,
  onBranch,
}: {
  message: Message;
  all: Message[];
  onBranch: (id: string) => void;
}) {
  const branches = siblings(all, message),
    index = branches.findIndex((row) => row.id === message.id);
  if (branches.length < 2) return null;
  return (
    <div className="flex items-center">
      <IconButton
        label="Previous branch"
        disabled={index === 0}
        onClick={() => onBranch(branches[index - 1]!.id)}
      >
        <ChevronLeft />
      </IconButton>
      <span className="meta">
        {index + 1} / {branches.length}
      </span>
      <IconButton
        label="Next branch"
        disabled={index === branches.length - 1}
        onClick={() => onBranch(branches[index + 1]!.id)}
      >
        <ChevronRight />
      </IconButton>
    </div>
  );
}

export default function ImageTurn({
  message,
  all,
  onBranch,
  onAction,
  preview = false,
}: {
  message: Message;
  all: Message[];
  onBranch: (id: string) => void;
  onAction?: (message: Message, action: "retry" | "cancel") => void;
  preview?: boolean;
}) {
  const jobs = message.images ?? [],
    active = jobs.some(imageActive);
  const queue = useImageJobs((state) => state.jobs);
  const copy = useCopyFeedback();
  const prompt =
    jobs[0]?.prompt ??
    all.find((row) => row.id === message.parent_id)?.content ??
    "";
  return (
    <div data-slot="image-turn">
      <p className="mb-3 text-xs text-fg-3">FLUX.2 klein 4B</p>
      <div
        className={`image-frames image-count-${jobs.length}`}
        tabIndex={jobs.length === 3 ? 0 : undefined}
        role="group"
        aria-label="Images in this turn"
      >
        {jobs.map((job, i) => (
          <ImageFrame
            key={job.id}
            job={job}
            next={job.state === "queued" && jobs.slice(0, i).some(imageActive)}
            preview={preview}
            onRetry={() => onAction?.(message, "retry")}
          />
        ))}
      </div>
      <div
        className="mt-3 flex min-h-8 items-center gap-2 text-sm text-fg-2"
        role="status"
      >
        {active && (
          <span
            className="text-brand"
            data-frozen={
              jobs.some((job) => job.state === "cancelling") || undefined
            }
          >
            <AtelierMark think={jobs.some((job) => job.state === "running")} />
          </span>
        )}
        <span>{imageTurnStatus(jobs, Object.values(queue))}</span>
      </div>
      <div className="mt-1 flex flex-wrap items-center gap-1">
        {active ? (
          <Button
            variant="ghost"
            className="h-11 text-fg-2"
            disabled={jobs.every(
              (job) => !imageActive(job) || job.state === "cancelling",
            )}
            onClick={() => onAction?.(message, "cancel")}
          >
            <Square className="size-4" />
            Cancel
          </Button>
        ) : (
          <Button
            variant="ghost"
            className="h-11 text-fg-2"
            onClick={() => onAction?.(message, "retry")}
          >
            <RotateCcw className="size-4" />
            Try again
          </Button>
        )}
        <Button
          variant="ghost"
          className="h-11 text-fg-2"
          onClick={() => void copy.copy(prompt)}
        >
          {!copy.copied && <Copy className="size-4" />}
          <CopyFeedback {...copy} />
          Copy prompt
        </Button>
        <ImageBranches message={message} all={all} onBranch={onBranch} />
      </div>
    </div>
  );
}

export function ImageFrame({
  job,
  next = false,
  onRetry,
  preview = false,
}: {
  job: ImageJob;
  next?: boolean;
  onRetry?: () => void;
  preview?: boolean;
}) {
  const [loaded, setLoaded] = useState(false),
    [failed, setFailed] = useState(false),
    [reveal, setReveal] = useState(false),
    [loadAttempt, setLoadAttempt] = useState(0);
  const [saving, setSaving] = useState(false),
    [details, setDetails] = useState(false),
    [removing, setRemoving] = useState(false),
    [busy, setBusy] = useState(false);
  const reduced = useReducedMotion(),
    copy = useCopyFeedback();
  useEffect(() => {
    if (reduced) setReveal(false);
  }, [reduced]);
  const working = ["preparing", "running", "cancelling"].includes(job.state);
  const saved = job.state === "complete" && job.image_bytes > 0;
  const retryable = ["failed", "interrupted", "cancelled"].includes(job.state);
  const decoded = saved && loaded && !failed;
  const label = failed
    ? "Couldn't load the image"
    : job.state === "complete" && !job.image_bytes
      ? "Image removed"
      : job.state === "failed"
        ? (job.error ?? "Couldn't create this image")
        : job.state === "interrupted"
          ? "Interrupted"
          : job.state === "cancelled"
            ? "Cancelled"
            : next
              ? "Next"
              : "";
  return (
    <div
      className="image-frame-shell"
      data-job-id={job.id}
      data-frame-state={
        failed
          ? "load-failed"
          : job.state === "complete" && !job.image_bytes
            ? "removed"
            : job.stage === "Decoding image"
              ? "decoding"
              : job.state
      }
    >
      <div
        className="image-frame"
        data-frozen={job.state === "cancelling" || undefined}
      >
        {(working || (saved && !decoded)) && (
          <div
            className="image-develop"
            data-decoding={job.stage === "Decoding image" || undefined}
            aria-hidden="true"
          >
            <i />
            <i />
            <i />
            {job.state === "preparing" && <b className="image-sheen" />}
          </div>
        )}
        {saved &&
          (preview ? (
            <div
              className="absolute inset-0 bg-brand-soft"
              role="img"
              aria-label="Synthetic image placeholder"
            />
          ) : (
            <img
              src={`/api/images/jobs/${job.id}/output/png${loadAttempt ? `?retry=${loadAttempt}` : ""}`}
              alt={job.prompt}
              decoding="async"
              className={`image-output ${decoded ? "is-loaded" : ""} ${reveal && !reduced ? "image-reveal" : ""}`}
              data-reveal={(reveal && !reduced) || undefined}
              onLoad={() => {
                setLoaded(true);
                setFailed(false);
                setReveal(claimImageReveal(job.id) && !reduced);
              }}
              onError={() => setFailed(true)}
              onAnimationEnd={() => setReveal(false)}
            />
          ))}
        {label && (
          <div
            className={`absolute inset-0 flex flex-col items-center justify-center gap-2 p-4 text-center text-sm text-fg-2`}
          >
            {next ? (
              <span className="absolute left-3 top-3 rounded-full bg-surface-3 px-2 py-1 text-xs">
                Next
              </span>
            ) : (
              <>
                <span>{label}</span>
                {(retryable || failed) && (
                  <Button
                    variant="outline"
                    className="h-11"
                    onClick={() =>
                      failed
                        ? (setFailed(false),
                          setLoaded(false),
                          setLoadAttempt((n) => n + 1))
                        : onRetry?.()
                    }
                  >
                    Retry
                  </Button>
                )}
              </>
            )}
          </div>
        )}
        {working && (
          <div
            className="image-progress"
            role="progressbar"
            aria-label="Image denoising steps"
            aria-valuemin={0}
            aria-valuemax={job.steps}
            aria-valuenow={job.completed_steps}
          >
            {Array.from({ length: job.steps }, (_, n) => (
              <span key={n}>
                <i data-filled={n < job.completed_steps} />
              </span>
            ))}
          </div>
        )}
      </div>
      {saved && (
        <div className="image-frame-actions">
          <IconButton label="Save image" onClick={() => setSaving(true)}>
            <Download />
          </IconButton>
          <IconButton
            label="Copy image prompt"
            onClick={() => void copy.copy(job.prompt)}
          >
            {!copy.copied && <Copy />}
            <CopyFeedback {...copy} />
          </IconButton>
          <IconButton label="Image details" onClick={() => setDetails(true)}>
            <Info />
          </IconButton>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <IconButton label="More image actions">
                <MoreHorizontal />
              </IconButton>
            </DropdownMenuTrigger>
            <DropdownMenuContent>
              <DropdownMenuItem onSelect={() => setRemoving(true)}>
                Remove image
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      )}
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
    </div>
  );
}
