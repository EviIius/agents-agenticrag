import { useEffect, useRef, useState, type PointerEvent } from "react";
import type { PhotoSelection } from "@/hooks/usePhotoEdit";
import { maskCoverage, photoMask, type PhotoStroke } from "@/lib/photo-mask";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogTitle,
} from "@/components/ui/dialog";

type Point = [number, number];
type Tool = "paint" | "erase" | "move";
type View = "overlay" | "selected" | "protected";

export default function PhotoMaskEditor({
  url,
  width,
  height,
  selection,
  onApply,
  onClose,
}: {
  url: string;
  width: number;
  height: number;
  selection?: PhotoSelection;
  onApply: (selection: PhotoSelection) => void;
  onClose: () => void;
}) {
  const canvas = useRef<HTMLCanvasElement>(null);
  const viewport = useRef<HTMLDivElement>(null);
  const image = useRef<HTMLImageElement>(undefined);
  const mask = useRef<HTMLCanvasElement>(undefined);
  const active = useRef<{
    id: number;
    tool: Tool;
    x: number;
    y: number;
    left: number;
    top: number;
  }>(undefined);
  const [strokes, setStrokes] = useState<PhotoStroke[]>(
    selection?.strokes ?? [],
  );
  const [past, setPast] = useState<PhotoStroke[][]>([]);
  const [future, setFuture] = useState<PhotoStroke[][]>([]);
  const [tool, setTool] = useState<Tool>("paint");
  const [view, setView] = useState<View>("overlay");
  const [radius, setRadius] = useState(0.035);
  const [zoom, setZoom] = useState(1);
  const [frame, setFrame] = useState({ width: 320, height: 300 });
  const [cursor, setCursor] = useState<Point>();
  const [coverage, setCoverage] = useState({ selected: 0, percent: 0 });
  const [ready, setReady] = useState(false);
  const [reviewing, setReviewing] = useState(false);
  const [error, setError] = useState("");
  const scale = Math.min(frame.width / width, frame.height / height) * zoom;
  const displayWidth = width * scale,
    displayHeight = height * scale;

  useEffect(() => {
    const photo = new Image();
    let current = true;
    photo.onload = () => {
      if (current) {
        image.current = photo;
        setReady(true);
      }
    };
    photo.onerror = () => {
      if (current) setError("Couldn't load this photo. Close and try again.");
    };
    photo.src = url;
    return () => {
      current = false;
      photo.src = "";
      image.current = undefined;
    };
  }, [url]);
  useEffect(() => {
    const node = viewport.current;
    if (!node) return;
    const measure = () =>
      setFrame({ width: node.clientWidth, height: node.clientHeight });
    const observer = new ResizeObserver(measure);
    observer.observe(node);
    measure();
    return () => observer.disconnect();
  }, []);
  useEffect(() => {
    mask.current = photoMask(width, height, strokes);
    setCoverage(maskCoverage(mask.current));
  }, [width, height, strokes]);
  useEffect(() => {
    const context = canvas.current?.getContext("2d");
    if (!context || !ready || !image.current || !mask.current) return;
    const brand = getComputedStyle(canvas.current!)
      .getPropertyValue("--brand")
      .trim();
    context.clearRect(0, 0, width, height);
    context.globalAlpha = view === "overlay" ? 1 : 0.18;
    context.drawImage(image.current, 0, 0, width, height);
    context.globalAlpha = 1;
    const visible = document.createElement("canvas");
    visible.width = width;
    visible.height = height;
    const layer = visible.getContext("2d")!;
    if (view === "protected") {
      layer.fillStyle = "white";
      layer.fillRect(0, 0, width, height);
      layer.globalCompositeOperation = "destination-out";
      layer.drawImage(mask.current, 0, 0);
    } else layer.drawImage(mask.current, 0, 0);
    layer.globalCompositeOperation = "source-in";
    if (view === "overlay") {
      layer.fillStyle = brand;
      layer.fillRect(0, 0, width, height);
      context.globalAlpha = 0.42;
    } else layer.drawImage(image.current, 0, 0, width, height);
    context.drawImage(visible, 0, 0);
    context.globalAlpha = 1;
    if (cursor && tool !== "move") {
      context.strokeStyle = brand;
      context.lineWidth = Math.max(1, 2 / scale);
      context.setLineDash(tool === "erase" ? [5 / scale, 4 / scale] : []);
      context.beginPath();
      context.arc(
        cursor[0] * (width - 1),
        cursor[1] * (height - 1),
        Math.max(1, Math.round(radius * Math.min(width, height))),
        0,
        2 * Math.PI,
      );
      context.stroke();
      context.setLineDash([]);
    }
  }, [width, height, strokes, ready, view, cursor, tool, radius, scale]);

  function commit(next: PhotoStroke[]) {
    active.current = undefined;
    setPast((p) => [...p.slice(-39), strokes]);
    setFuture([]);
    setStrokes(next);
    setError("");
  }
  function undo() {
    if (!past.length) return;
    active.current = undefined;
    setFuture([strokes, ...future]);
    setStrokes(past.at(-1)!);
    setPast(past.slice(0, -1));
    setError("");
  }
  function redo() {
    if (!future.length) return;
    active.current = undefined;
    setPast([...past, strokes]);
    setStrokes(future[0]);
    setFuture(future.slice(1));
    setError("");
  }
  function point(event: PointerEvent<HTMLCanvasElement>): Point {
    const box = event.currentTarget.getBoundingClientRect();
    return [event.clientX - box.left, event.clientY - box.top].map((n, i) =>
      Number(
        Math.min(1, Math.max(0, n / (i ? box.height : box.width))).toFixed(5),
      ),
    ) as Point;
  }
  function begin(position: Point) {
    if (reviewing || tool === "move") return false;
    if (tool === "erase" && !coverage.selected) {
      setError("Paint an area first, then protect details within it.");
      return false;
    }
    if (
      strokes.length >= 32 ||
      strokes.reduce((n, s) => n + s.points.length, 0) >= 512
    ) {
      setError(
        "Selection limit reached. Undo a stroke or clear it to continue.",
      );
      return false;
    }
    commit([
      ...strokes,
      {
        ...(tool === "erase" ? { operation: "erase" as const } : {}),
        radius,
        points: [position],
      },
    ]);
    return true;
  }
  function move(position: Point) {
    setStrokes((old) => {
      const last = old.at(-1);
      if (
        !last ||
        last.points.length >= 128 ||
        old.reduce((n, s) => n + s.points.length, 0) >= 512
      )
        return old;
      const previous = last.points.at(-1)!;
      if (
        Math.hypot(position[0] - previous[0], position[1] - previous[1]) < 0.002
      )
        return old;
      return [
        ...old.slice(0, -1),
        { ...last, points: [...last.points, position] },
      ];
    });
  }
  function fit() {
    active.current = undefined;
    setZoom(1);
    viewport.current?.scrollTo(0, 0);
  }
  const controls: [Tool, string][] = [
    ["paint", "Paint"],
    ["erase", "Protect"],
    ["move", "Move"],
  ];
  const views: [View, string][] = [
    ["overlay", "Overlay"],
    ["selected", "Selected"],
    ["protected", "Protected"],
  ];
  return (
    <Dialog
      open
      onOpenChange={(open) => {
        if (!open) onClose();
      }}
    >
      <DialogContent className="max-h-[calc(100svh-2rem)] gap-3 overflow-y-auto p-4 sm:max-w-2xl">
        <DialogTitle>Select edit area</DialogTitle>
        <DialogDescription>
          {reviewing
            ? "Check where the addition can overlap the original. Only unselected pixels stay unchanged."
            : "Paint the area to replace, including the existing details an addition will cover. Protect removes paint."}
        </DialogDescription>
        <div
          role="group"
          aria-label="Selection tool"
          className="grid grid-cols-3 gap-2"
        >
          {controls.map(([value, label]) => (
            <Button
              key={value}
              type="button"
              variant={tool === value ? "default" : "outline"}
              aria-pressed={tool === value}
              disabled={reviewing}
              onClick={() => {
                active.current = undefined;
                setTool(value);
                setError("");
              }}
            >
              {label}
            </Button>
          ))}
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <div
            role="group"
            aria-label="Photo zoom"
            className="flex items-center gap-1"
          >
            <Button
              type="button"
              variant="outline"
              size="sm"
              aria-label="Zoom out"
              disabled={zoom <= 1}
              onClick={() => setZoom((n) => Math.max(1, n - 0.5))}
            >
              −
            </Button>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              aria-label="Fit photo"
              onClick={fit}
            >
              {zoom}×
            </Button>
            <Button
              type="button"
              variant="outline"
              size="sm"
              aria-label="Zoom in"
              disabled={zoom >= 4}
              onClick={() => setZoom((n) => Math.min(4, n + 0.5))}
            >
              +
            </Button>
          </div>
          <div
            role="group"
            aria-label="Mask view"
            className="flex flex-wrap gap-1"
          >
            {views.map(([value, label]) => (
              <Button
                key={value}
                type="button"
                variant={view === value ? "secondary" : "ghost"}
                size="sm"
                aria-pressed={view === value}
                onClick={() => {
                  setCursor(undefined);
                  setView(value);
                }}
              >
                {label}
              </Button>
            ))}
          </div>
        </div>
        <div
          ref={viewport}
          data-slot="mask-viewport"
          className="h-[42svh] min-h-40 overflow-auto overscroll-contain rounded-lg border border-line bg-surface-2"
        >
          <div
            className="flex items-center justify-center"
            style={{
              width: Math.max(frame.width, displayWidth),
              height: Math.max(frame.height, displayHeight),
            }}
          >
            <canvas
              ref={canvas}
              width={width}
              height={height}
              tabIndex={0}
              role="img"
              aria-label={
                reviewing
                  ? "Photo selection canvas. Review only. Drag or use arrow keys to pan. Choose Adjust selection to paint."
                  : "Photo selection canvas. Paint or protect with a pointer, or use arrow keys and Space. Choose Move to pan."
              }
              className={`block shrink-0 touch-none outline-brand ${tool === "move" ? "cursor-grab" : "cursor-crosshair"}`}
              style={{ width: displayWidth, height: displayHeight }}
              onPointerDown={(event) => {
                if (
                  !ready ||
                  active.current ||
                  (event.pointerType === "mouse" && event.button !== 0)
                )
                  return;
                event.preventDefault();
                const position = point(event);
                setCursor(position);
                if (tool !== "move" && !begin(position)) return;
                event.currentTarget.setPointerCapture(event.pointerId);
                active.current = {
                  id: event.pointerId,
                  tool,
                  x: event.clientX,
                  y: event.clientY,
                  left: viewport.current!.scrollLeft,
                  top: viewport.current!.scrollTop,
                };
              }}
              onPointerMove={(event) => {
                const state = active.current;
                if (state && state.id !== event.pointerId) return;
                if (state?.tool === "move") {
                  viewport.current!.scrollLeft =
                    state.left - (event.clientX - state.x);
                  viewport.current!.scrollTop =
                    state.top - (event.clientY - state.y);
                } else {
                  const position = point(event);
                  setCursor(position);
                  if (state) move(position);
                }
              }}
              onPointerUp={(event) => {
                if (active.current?.id === event.pointerId)
                  active.current = undefined;
              }}
              onPointerCancel={(event) => {
                if (active.current?.id === event.pointerId)
                  active.current = undefined;
              }}
              onLostPointerCapture={(event) => {
                if (active.current?.id === event.pointerId)
                  active.current = undefined;
              }}
              onPointerLeave={() => {
                if (!active.current) setCursor(undefined);
              }}
              onKeyDown={(event) => {
                if (!ready) return;
                if (
                  (event.metaKey || event.ctrlKey) &&
                  event.key.toLowerCase() === "z"
                ) {
                  event.preventDefault();
                  if (reviewing) return;
                  if (event.shiftKey) redo();
                  else undo();
                  return;
                }
                const arrows: Record<string, Point> = {
                  ArrowLeft: [-0.01, 0],
                  ArrowRight: [0.01, 0],
                  ArrowUp: [0, -0.01],
                  ArrowDown: [0, 0.01],
                };
                if (arrows[event.key]) {
                  event.preventDefault();
                  const [x, y] = arrows[event.key];
                  if (tool === "move")
                    viewport.current?.scrollBy(x * 3000, y * 3000);
                  else {
                    const [cx, cy] = cursor ?? [0.5, 0.5];
                    setCursor([
                      Math.max(0, Math.min(1, cx + x)),
                      Math.max(0, Math.min(1, cy + y)),
                    ]);
                  }
                } else if (event.key === " " && tool !== "move") {
                  event.preventDefault();
                  begin(cursor ?? [0.5, 0.5]);
                }
              }}
            />
          </div>
        </div>
        <p className="text-xs text-fg-2">
          {view === "overlay"
            ? "Painted areas may change. The rest stays protected."
            : view === "selected"
              ? "Bright areas may change. Dim areas stay protected."
              : "Bright areas stay protected. Dim areas may change."}
          {tool === "move"
            ? " Drag to move the zoomed photo."
            : " Zoom in for details; choose Move to pan."}
        </p>
        <div className="flex items-center gap-3">
          <span className="shrink-0 text-sm">Brush size</span>
          <Slider
            aria-label="Brush size"
            min={0.005}
            max={0.15}
            step={0.005}
            value={[radius]}
            disabled={reviewing}
            onValueChange={([n]) => setRadius(n)}
          />
        </div>
        {error && (
          <p role="alert" className="text-sm text-danger">
            {error}
          </p>
        )}
        <p role="status" className="text-xs text-fg-2">
          {coverage.selected
            ? `${strokes.length} brush ${strokes.length === 1 ? "stroke" : "strokes"} · ${coverage.percent < 1 ? "less than 1" : `about ${Math.round(coverage.percent)}`}% selected`
            : "No area selected"}
        </p>
        <p className="text-xs text-fg-2">
          {reviewing
            ? "A brim may cover hair or forehead. Those pixels need paint too. Protect the eyes and other details that must remain visible. Adjust the selection if the addition would be cut off."
            : "Include room for the new object and the surface it will cover. Review the overlap before applying."}
        </p>
        <div className="flex flex-wrap gap-2">
          {reviewing ? (
            <Button
              type="button"
              variant="outline"
              onClick={() => {
                active.current = undefined;
                setReviewing(false);
                setTool("paint");
                setView("overlay");
              }}
            >
              Adjust selection
            </Button>
          ) : (
            <>
              <Button
                type="button"
                variant="outline"
                disabled={!past.length}
                onClick={undo}
              >
                Undo
              </Button>
              <Button
                type="button"
                variant="outline"
                disabled={!future.length}
                onClick={redo}
              >
                Redo
              </Button>
              <Button
                type="button"
                variant="outline"
                disabled={!strokes.length}
                onClick={() => commit([])}
              >
                Clear
              </Button>
            </>
          )}
          <Button
            type="button"
            variant="ghost"
            className="ml-auto"
            onClick={onClose}
          >
            Cancel
          </Button>
          <Button
            type="button"
            disabled={!ready || !coverage.selected}
            onClick={() => {
              if (reviewing) onApply({ version: 1, strokes });
              else {
                active.current = undefined;
                setCursor(undefined);
                setError("");
                setTool("move");
                setView("selected");
                setReviewing(true);
              }
            }}
          >
            {reviewing ? "Use selection" : "Review selection"}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
