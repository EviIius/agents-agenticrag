import { useEffect, useRef, useState } from "react";
import {
  Copy,
  RotateCcw,
  Square,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { type Message } from "@/lib/api";
import {
  imageActive,
  claimImageReveal,
  type ImageJob,
  useImageJobs,
} from "@/lib/image-events";
import { imageTurnStatus } from "@/lib/image-state";
import { siblings } from "@/lib/tree";
import { useCopyFeedback } from "@/hooks/useCopyFeedback";
import { useReducedMotion } from "@/hooks/useReducedMotion";
import { CopyFeedback } from "./CopyFeedback";
import { AtelierMark } from "./AtelierMark";
import { Button } from "@/components/ui/button";
import { IconButton } from "@/components/app/IconButton";
import { ImageActions, type ImageIteration } from "./ImageActions";
import { ImageViewer } from "./ImageViewer";

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
  threadImages,
  onIteration,
  vision = false,
}: {
  threadImages?: ImageJob[];
  onIteration?: ImageIteration;
  vision?: boolean;
  message: Message;
  all: Message[];
  onBranch: (id: string) => void;
  onAction?: (message: Message, action: "retry" | "cancel") => void;
  preview?: boolean;
}) {
  const [viewer, setViewer] = useState<{
    job: ImageJob;
    frame: HTMLElement;
  } | null>(null);
  const [position, setPosition] = useState(0);
  const frames = useRef<HTMLDivElement>(null);
  const reduced = useReducedMotion();
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
        ref={frames}
        onScroll={() => {
          const row = frames.current;
          if (row && row.firstElementChild)
            setPosition(
              Math.round(
                row.scrollLeft /
                  ((row.firstElementChild as HTMLElement).offsetWidth + 8),
              ),
            );
        }}
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
            position={i + 1}
            vision={vision}
            onIteration={onIteration}
            onOpen={(frame) => setViewer({ job, frame })}
            onRetry={() => onAction?.(message, "retry")}
          />
        ))}
      </div>
      {jobs.length === 3 && (
        <div className="image-position-dots" aria-label="Image position">
          {jobs.map((job, i) => (
            <button
              key={job.id}
              aria-label={`Show image ${i + 1}`}
              aria-current={position === i ? "true" : undefined}
              onClick={() => {
                const row = frames.current,
                  target = row?.children[i] as HTMLElement | undefined;
                if (row && target)
                  row.scrollTo({
                    left: target.offsetLeft - row.offsetLeft,
                    behavior: reduced ? "instant" : "smooth",
                  });
              }}
            >
              <span />
            </button>
          ))}
        </div>
      )}
      {viewer && (
        <ImageViewer
          job={viewer.job}
          frame={viewer.frame}
          jobs={threadImages ?? jobs}
          onClose={() => setViewer(null)}
          onIteration={onIteration}
          vision={vision}
          preview={preview}
        />
      )}
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
  position = 1,
  onIteration,
  onOpen,
  vision = false,
}: {
  position?: number;
  onIteration?: ImageIteration;
  onOpen?: (frame: HTMLElement) => void;
  vision?: boolean;
  job: ImageJob;
  next?: boolean;
  onRetry?: () => void;
  preview?: boolean;
}) {
  const [loaded, setLoaded] = useState(false),
    [failed, setFailed] = useState(false),
    [reveal, setReveal] = useState(false),
    [loadAttempt, setLoadAttempt] = useState(0);
  const reduced = useReducedMotion();
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
        role={saved && !failed ? "button" : undefined}
        tabIndex={saved && !failed ? 0 : undefined}
        aria-label={saved && !failed ? `Open image ${position}` : undefined}
        onClick={(event) => {
          if (saved && !(event.target as Element).closest("button"))
            onOpen?.(event.currentTarget);
        }}
        onKeyDown={(event) => {
          if (
            saved &&
            event.target === event.currentTarget &&
            (event.key === "Enter" || event.key === " ")
          ) {
            event.preventDefault();
            onOpen?.(event.currentTarget);
          }
        }}
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
        <ImageActions
          job={job}
          position={position}
          onIteration={onIteration}
          vision={vision}
          preview={preview}
        />
      )}
    </div>
  );
}
