import {
  useEffect,
  useLayoutEffect,
  useRef,
  useState,
  type CSSProperties,
} from "react";
import { Dialog as Primitive } from "radix-ui";
import { ChevronLeft, ChevronRight, X, ZoomIn, ZoomOut } from "lucide-react";
import {
  Dialog,
  DialogPortal,
  DialogOverlay,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { IconButton } from "@/components/app/IconButton";
import { useReducedMotion } from "@/hooks/useReducedMotion";
import type { ImageJob } from "@/lib/image-events";
import { ImageActions, type ImageIteration } from "./ImageActions";

type Point = { x: number; y: number };
export function ImageViewer({
  job: initial,
  jobs,
  frame,
  onClose,
  onIteration,
  vision,
  preview,
}: {
  job: ImageJob;
  jobs: ImageJob[];
  frame: HTMLElement;
  onClose: () => void;
  onIteration?: ImageIteration;
  vision?: boolean;
  preview?: boolean;
}) {
  const available = jobs.filter(
    (job) => job.state === "complete" && job.image_bytes > 0,
  );
  const [id, setId] = useState(initial.id),
    [closing, setClosing] = useState(false),
    [ready, setReady] = useState(false),
    [expanded, setExpanded] = useState(false),
    [failed, setFailed] = useState(false);
  const [fit, setFit] = useState({ size: 0, x: 0, y: 0 }),
    [flip, setFlip] = useState({ x: 0, y: 0, scale: 1 });
  const [zoom, setZoom] = useState(1),
    [offset, setOffset] = useState<Point>({ x: 0, y: 0 }),
    [direction, setDirection] = useState(0);
  const stage = useRef<HTMLDivElement>(null),
    img = useRef<HTMLImageElement>(null),
    after = useRef<(() => void) | undefined>(undefined),
    timer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  const pointers = useRef(new Map<number, Point>()),
    start = useRef<Point | null>(null),
    pan = useRef<Point>({ x: 0, y: 0 }),
    pinch = useRef({ distance: 0, zoom: 1, used: false }),
    lastTap = useRef(0);
  const reduced = useReducedMotion();
  const job = available.find((job) => job.id === id) ?? initial;
  const index = available.findIndex((job) => job.id === id);
  const position = jobs.findIndex((row) => row.id === job.id) + 1;
  function source() {
    return (
      document.querySelector<HTMLElement>(
        `[data-job-id="${id}"] .image-frame`,
      ) ?? frame
    );
  }
  function measure(target?: HTMLElement) {
    const box = stage.current?.getBoundingClientRect();
    if (!box) return;
    const margin = window.innerWidth < 768 ? 16 : 24,
      size = Math.max(1, Math.min(box.width, box.height) - 2 * margin);
    const rect = (target ?? source()).getBoundingClientRect();
    setFit({ size, x: (box.width - size) / 2, y: (box.height - size) / 2 });
    setFlip({
      x: rect.left - box.left - (box.width - size) / 2,
      y: rect.top - box.top - (box.height - size) / 2,
      scale: rect.width / size,
    });
  }
  useLayoutEffect(() => {
    measure();
    const observer = new ResizeObserver(() => measure());
    if (stage.current) observer.observe(stage.current);
    let second = 0;
    const raf = requestAnimationFrame(() => {
      second = requestAnimationFrame(() => setReady(true));
    });
    return () => {
      observer.disconnect();
      cancelAnimationFrame(raf);
      cancelAnimationFrame(second);
    };
    // Source geometry is captured on open and resized only by the actual viewport.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  useEffect(
    () => () => {
      clearTimeout(timer.current);
    },
    [],
  );
  function finish() {
    clearTimeout(timer.current);
    onClose();
    if (after.current) requestAnimationFrame(after.current);
  }
  useEffect(() => {
    if (closing && reduced) finish();
  }, [closing, reduced]); // eslint-disable-line react-hooks/exhaustive-deps
  function close(next?: () => void) {
    if (closing) return;
    after.current = next;
    frame.scrollIntoView({
      block: "nearest",
      inline: "nearest",
      behavior: "instant",
    });
    measure(frame);
    setClosing(true);
    setZoom(1);
    setOffset({ x: 0, y: 0 });
    if (reduced) finish();
    else timer.current = setTimeout(finish, 320);
  }
  function step(delta: number) {
    if (closing || available.length < 2) return;
    const next =
      available[(index + delta + available.length) % available.length]!;
    setId(next.id);
    setFailed(false);
    setExpanded(false);
    setZoom(1);
    setOffset({ x: 0, y: 0 });
    setDirection(delta);
    lastTap.current = 0;
  }
  function toggleZoom() {
    setZoom((old) =>
      old > 1 ? 1 : Math.max(1, (img.current?.naturalWidth ?? 1024) / fit.size),
    );
    setOffset({ x: 0, y: 0 });
  }
  const style = {
    width: fit.size,
    height: fit.size,
    left: fit.x,
    top: fit.y,
    "--viewer-x": `${flip.x}px`,
    "--viewer-y": `${flip.y}px`,
    "--viewer-scale": flip.scale,
    "--viewer-direction": direction,
    "--viewer-zoom": zoom,
    "--viewer-pan-x": `${offset.x}px`,
    "--viewer-pan-y": `${offset.y}px`,
  } as CSSProperties;
  return (
    <Dialog
      open
      onOpenChange={(open) => {
        if (!open) close();
      }}
    >
      <DialogPortal>
        <DialogOverlay
          className="image-viewer-overlay"
          data-closing={closing || undefined}
        />
        <Primitive.Content
          className="image-viewer"
          data-slot="image-viewer"
          data-closing={closing || undefined}
          onOpenAutoFocus={(event) => {
            event.preventDefault();
            stage.current?.focus();
          }}
          onCloseAutoFocus={(event) => {
            event.preventDefault();
            if (frame.isConnected) frame.focus({ preventScroll: true });
          }}
          onEscapeKeyDown={(event) => {
            event.preventDefault();
            close();
          }}
          onKeyDown={(event) => {
            if (
              !event.defaultPrevented &&
              (event.key === "ArrowLeft" || event.key === "ArrowRight")
            ) {
              event.preventDefault();
              step(event.key === "ArrowRight" ? 1 : -1);
            }
          }}
        >
          <DialogTitle className="sr-only">Image viewer</DialogTitle>
          <DialogDescription className="sr-only">
            Use arrow keys or swipe to view the images in this conversation.
            Double tap or use Zoom to see actual size.
          </DialogDescription>
          <header className="image-viewer-bar">
            <button
              className={`image-viewer-prompt ${expanded ? "is-expanded" : ""}`}
              aria-label="Expand image prompt"
              aria-expanded={expanded}
              onClick={() => setExpanded(!expanded)}
            >
              {job.prompt}
            </button>
            <span
              className="text-xs text-fg-2 whitespace-nowrap"
              aria-live="polite"
            >
              {index + 1} / {available.length}
            </span>
            <IconButton label="Close image viewer" onClick={() => close()}>
              <X />
            </IconButton>
          </header>
          <div
            ref={stage}
            tabIndex={-1}
            className="image-viewer-stage"
            data-zoom={zoom.toFixed(2)}
            onDoubleClick={() => toggleZoom()}
            onPointerDown={(event) => {
              if ((event.target as Element).closest("button")) return;
              pointers.current.set(event.pointerId, {
                x: event.clientX,
                y: event.clientY,
              });
              if (event.nativeEvent.isTrusted)
                event.currentTarget.setPointerCapture(event.pointerId);
              if (pointers.current.size === 1) {
                start.current = { x: event.clientX, y: event.clientY };
                pan.current = offset;
                pinch.current.used = false;
              }
              if (pointers.current.size === 2) {
                const [a, b] = [...pointers.current.values()];
                pinch.current = {
                  distance: Math.hypot(a!.x - b!.x, a!.y - b!.y),
                  zoom,
                  used: true,
                };
              }
            }}
            onPointerMove={(event) => {
              if (!pointers.current.has(event.pointerId)) return;
              pointers.current.set(event.pointerId, {
                x: event.clientX,
                y: event.clientY,
              });
              if (pointers.current.size === 2) {
                const [a, b] = [...pointers.current.values()];
                const distance = Math.hypot(a!.x - b!.x, a!.y - b!.y);
                if (pinch.current.distance)
                  setZoom(
                    Math.min(
                      6,
                      Math.max(
                        1,
                        (pinch.current.zoom * distance) /
                          pinch.current.distance,
                      ),
                    ),
                  );
              } else if (start.current) {
                const x = event.clientX - start.current.x,
                  y = event.clientY - start.current.y;
                const limit = (fit.size * Math.max(0, zoom - 1)) / 2;
                setOffset(
                  zoom > 1
                    ? {
                        x: Math.max(-limit, Math.min(limit, pan.current.x + x)),
                        y: Math.max(-limit, Math.min(limit, pan.current.y + y)),
                      }
                    : { x, y },
                );
              }
            }}
            onPointerUp={(event) => {
              pointers.current.delete(event.pointerId);
              if (pinch.current.used) {
                if (!pointers.current.size) start.current = null;
                return;
              }
              const origin = start.current;
              start.current = null;
              if (!origin) return;
              const x = event.clientX - origin.x,
                y = event.clientY - origin.y;
              if (zoom === 1) {
                setOffset({ x: 0, y: 0 });
                if (Math.abs(x) > 50 && Math.abs(x) > Math.abs(y))
                  step(x < 0 ? 1 : -1);
                else if (y > 80 && y > Math.abs(x)) close();
                else if (Math.hypot(x, y) < 6) {
                  if (event.target === stage.current) close();
                  else if (event.pointerType === "touch") {
                    const now = performance.now();
                    if (now - lastTap.current < 300) toggleZoom();
                    lastTap.current = now;
                  }
                }
              } else if (
                Math.hypot(x, y) < 6 &&
                event.pointerType === "touch"
              ) {
                const now = performance.now();
                if (now - lastTap.current < 300) toggleZoom();
                lastTap.current = now;
              }
            }}
            onPointerCancel={() => {
              pointers.current.clear();
              start.current = null;
              setOffset({ x: 0, y: 0 });
            }}
          >
            <div
              className="image-viewer-fit"
              style={style}
              data-ready={ready || undefined}
              data-closing={closing || undefined}
            >
              <div className="image-viewer-pan" style={style}>
                {failed ? (
                  <p role="alert" className="p-5">
                    Couldn't load this image.
                  </p>
                ) : preview ? (
                  <div
                    role="img"
                    aria-label={job.prompt}
                    className="size-full bg-brand-soft"
                  />
                ) : (
                  <img
                    ref={img}
                    key={id}
                    draggable={false}
                    src={`/api/images/jobs/${id}/output/png`}
                    alt={job.prompt}
                    onError={() => setFailed(true)}
                    className="image-viewer-output"
                    data-direction={direction}
                    onAnimationEnd={() => setDirection(0)}
                  />
                )}
              </div>
            </div>
            {available.length > 1 && (
              <>
                <IconButton
                  className="image-viewer-nav previous"
                  label="Previous image"
                  onClick={() => step(-1)}
                >
                  <ChevronLeft />
                </IconButton>
                <IconButton
                  className="image-viewer-nav next"
                  label="Next image"
                  onClick={() => step(1)}
                >
                  <ChevronRight />
                </IconButton>
              </>
            )}
          </div>
          <footer className="image-viewer-footer">
            <ImageActions
              key={id}
              job={job}
              position={position}
              viewer
              preview={preview}
              vision={vision}
              onIteration={
                onIteration
                  ? (job, action, n) => close(() => onIteration(job, action, n))
                  : undefined
              }
            />
            <IconButton
              label={zoom > 1 ? "Fit image" : "Zoom to actual size"}
              onClick={() => toggleZoom()}
            >
              {zoom > 1 ? <ZoomOut /> : <ZoomIn />}
            </IconButton>
          </footer>
        </Primitive.Content>
      </DialogPortal>
    </Dialog>
  );
}
