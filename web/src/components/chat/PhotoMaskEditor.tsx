import { useEffect, useRef, useState, type PointerEvent } from "react";
import type { PhotoSelection } from "@/hooks/usePhotoEdit";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogTitle,
} from "@/components/ui/dialog";

type Stroke = PhotoSelection["strokes"][number];
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
  const image = useRef<HTMLImageElement>(undefined);
  const drawing = useRef(false);
  const [strokes, setStrokes] = useState<Stroke[]>(selection?.strokes ?? []);
  const [radius, setRadius] = useState(0.035);
  const [ready, setReady] = useState(false);
  const [error, setError] = useState("");
  const cursor = useRef<[number, number]>([0.5, 0.5]);
  useEffect(() => {
    const photo = new Image();
    let active = true;
    photo.onload = () => {
      if (active) {
        image.current = photo;
        setReady(true);
      }
    };
    photo.onerror = () => {
      if (active) setError("Couldn't load this photo. Close and try again.");
    };
    photo.src = url;
    return () => {
      active = false;
      photo.src = "";
      image.current = undefined;
    };
  }, [url]);
  useEffect(() => {
    const context = canvas.current?.getContext("2d");
    if (!context || !ready || !image.current) return;
    context.clearRect(0, 0, width, height);
    context.drawImage(image.current, 0, 0, width, height);
    const brand = getComputedStyle(canvas.current!)
      .getPropertyValue("--brand")
      .trim();
    context.strokeStyle = context.fillStyle = brand;
    context.globalAlpha = 0.5;
    context.lineCap = context.lineJoin = "round";
    for (const stroke of strokes) {
      const r = Math.max(
        1,
        Math.round(stroke.radius * Math.min(width, height)),
      );
      context.lineWidth = 2 * r + 1;
      context.beginPath();
      stroke.points.forEach(([x, y], i) => {
        const px = Math.round(x * (width - 1)),
          py = Math.round(y * (height - 1));
        if (i) context.lineTo(px, py);
        else context.moveTo(px, py);
      });
      context.stroke();
      for (const [x, y] of stroke.points) {
        context.beginPath();
        context.arc(
          Math.round(x * (width - 1)),
          Math.round(y * (height - 1)),
          r,
          0,
          2 * Math.PI,
        );
        context.fill();
      }
    }
    context.globalAlpha = 1;
  }, [width, height, strokes, ready]);
  function point(event: PointerEvent<HTMLCanvasElement>): [number, number] {
    const box = event.currentTarget.getBoundingClientRect();
    return [event.clientX - box.left, event.clientY - box.top].map((n, i) =>
      Number(
        Math.min(1, Math.max(0, n / (i ? box.height : box.width))).toFixed(5),
      ),
    ) as [number, number];
  }
  function begin(position: [number, number]) {
    if (
      strokes.length >= 32 ||
      strokes.reduce((n, s) => n + s.points.length, 0) >= 512
    ) {
      setError(
        "Selection limit reached. Undo a stroke or clear it to continue.",
      );
      return;
    }
    setStrokes((old) => {
      if (
        old.length >= 32 ||
        old.reduce((n, s) => n + s.points.length, 0) >= 512
      ) {
        return old;
      }
      return [...old, { radius, points: [position] }];
    });
  }
  function move(position: [number, number]) {
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
        Math.hypot(position[0] - previous[0], position[1] - previous[1]) < 0.004
      )
        return old;
      return [
        ...old.slice(0, -1),
        { ...last, points: [...last.points, position] },
      ];
    });
  }
  return (
    <Dialog
      open
      onOpenChange={(open) => {
        if (!open) onClose();
      }}
    >
      <DialogContent className="max-h-[calc(100svh-2rem)] overflow-y-auto sm:max-w-2xl">
        <DialogTitle>Select edit area</DialogTitle>
        <DialogDescription>
          Brush over everything you want to change, including space for
          additions. Unselected pixels stay unchanged. Keep faces outside the
          selection.
        </DialogDescription>
        <div className="flex justify-center overflow-hidden rounded-lg bg-surface-2">
          <canvas
            ref={canvas}
            width={width}
            height={height}
            tabIndex={0}
            role="img"
            aria-label="Photo selection canvas. Brush with a pointer, or use arrow keys and Space to add a spot."
            className="max-h-[50svh] max-w-full touch-none cursor-crosshair outline-brand"
            onPointerDown={(event) => {
              if (
                !ready ||
                (event.pointerType === "mouse" && event.button !== 0)
              )
                return;
              event.preventDefault();
              event.currentTarget.setPointerCapture(event.pointerId);
              drawing.current = true;
              cursor.current = point(event);
              begin(cursor.current);
            }}
            onPointerMove={(event) => {
              if (drawing.current) {
                cursor.current = point(event);
                move(cursor.current);
              }
            }}
            onPointerUp={() => {
              drawing.current = false;
            }}
            onPointerCancel={() => {
              drawing.current = false;
            }}
            onLostPointerCapture={() => {
              drawing.current = false;
            }}
            onKeyDown={(event) => {
              if (!ready) return;
              const arrows: Record<string, [number, number]> = {
                ArrowLeft: [-0.02, 0],
                ArrowRight: [0.02, 0],
                ArrowUp: [0, -0.02],
                ArrowDown: [0, 0.02],
              };
              if (arrows[event.key]) {
                event.preventDefault();
                const [x, y] = arrows[event.key];
                cursor.current = [
                  Math.max(0, Math.min(1, cursor.current[0] + x)),
                  Math.max(0, Math.min(1, cursor.current[1] + y)),
                ];
              } else if (event.key === " ") {
                event.preventDefault();
                begin(cursor.current);
              }
            }}
          />
        </div>
        <div className="flex items-center gap-3">
          <span className="shrink-0 text-sm">Brush size</span>
          <Slider
            aria-label="Brush size"
            min={0.005}
            max={0.15}
            step={0.005}
            value={[radius]}
            onValueChange={([n]) => setRadius(n)}
          />
        </div>
        {error && (
          <p role="alert" className="text-sm text-danger">
            {error}
          </p>
        )}
        <p className="text-xs text-fg-2">
          {strokes.length
            ? `${strokes.length} brush ${strokes.length === 1 ? "stroke" : "strokes"} · only selected areas will change`
            : "No area selected"}
        </p>
        <div className="flex flex-wrap gap-2">
          <Button
            variant="outline"
            disabled={!strokes.length}
            onClick={() => {
              setStrokes((s) => s.slice(0, -1));
              setError("");
            }}
          >
            Undo
          </Button>
          <Button
            variant="outline"
            disabled={!strokes.length}
            onClick={() => {
              setStrokes([]);
              setError("");
            }}
          >
            Clear
          </Button>
          <Button variant="ghost" className="ml-auto" onClick={onClose}>
            Cancel
          </Button>
          <Button
            disabled={!ready || !strokes.length}
            onClick={() => onApply({ version: 1, strokes })}
          >
            Use selection
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
