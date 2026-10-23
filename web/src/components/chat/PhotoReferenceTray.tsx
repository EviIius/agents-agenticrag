import { lazy, Suspense, useState } from "react";
import { ImagePlus, X, RotateCcw } from "lucide-react";
import type { PhotoEditor } from "@/hooks/usePhotoEdit";
import { IconButton } from "@/components/app/IconButton";
import { Button } from "@/components/ui/button";
import { ImageViewer } from "./ImageViewer";
import { AtelierMark } from "./AtelierMark";
const PhotoMaskEditor = lazy(() => import("./PhotoMaskEditor"));

export default function PhotoReferenceTray({
  editor,
  choose,
}: {
  editor: PhotoEditor;
  choose: () => void;
}) {
  const [frame, setFrame] = useState<HTMLElement>();
  const [selecting, setSelecting] = useState<string>();
  const input = editor.draft.input,
    ref = input?.reference;
  const url =
    editor.previewURL ??
    (ref?.available
      ? `/api/chats/${ref.chat_id}/image-references/${ref.id}/preview`
      : input?.preview);
  const photo = {
    id: ref?.id ?? "local-photo",
    prompt: "Photo reference · normalized preview",
    url: url ?? "",
  };
  return (
    <div
      className="mb-3 rounded-xl border border-line bg-surface-2 p-3"
      data-slot="photo-reference"
    >
      <div className="flex items-center gap-3">
        {url && input?.phase !== "unavailable" && (
          <button
            type="button"
            className="size-14 shrink-0 overflow-hidden rounded-lg"
            aria-label="Preview photo reference"
            onClick={(event) => setFrame(event.currentTarget)}
          >
            <img
              src={url}
              alt="Photo reference"
              className="size-full object-contain"
              onLoad={editor.previewLoaded}
            />
          </button>
        )}
        <div className="min-w-0 flex-1 text-sm">
          <p className="font-medium">Photo reference</p>
          {input?.phase === "preparing" && (
            <p role="status" className="text-fg-2">
              <span className="inline-flex items-center gap-2">
                <AtelierMark />
                Preparing photo…
              </span>
            </p>
          )}
          {input?.phase === "ready" && (
            <p className="text-fg-2">
              Ready · {ref?.width} × {ref?.height}
            </p>
          )}
          {input?.phase === "error" && (
            <p role="alert" className="text-danger">
              {input.error}
            </p>
          )}
          {input?.phase === "unavailable" && (
            <p role="alert" className="text-fg-2">
              Photo input unavailable. Attach it again to edit.
            </p>
          )}
          {!input && (
            <p className="text-fg-2">Choose one PNG, JPEG or HEIC photo.</p>
          )}
        </div>
        {input && (
          <IconButton
            label={
              input.phase === "preparing"
                ? "Cancel photo upload"
                : "Remove photo reference"
            }
            type="button"
            onClick={editor.remove}
          >
            <X />
          </IconButton>
        )}
      </div>
      {input?.phase === "error" && (
        <Button type="button" variant="ghost" onClick={editor.retry}>
          <RotateCcw />
          Retry photo upload
        </Button>
      )}
      {(!input || input.phase === "unavailable") && (
        <Button type="button" variant="ghost" onClick={choose}>
          <ImagePlus />
          Attach photo
        </Button>
      )}
      {input?.phase === "ready" && ref && url && (
        <div className="mt-2 flex flex-wrap gap-2">
          <Button
            type="button"
            variant="outline"
            onClick={() => setSelecting(input.token)}
          >
            {input.selection ? "Change selection" : "Select edit area"}
          </Button>
          {input.selection && (
            <Button
              type="button"
              variant="ghost"
              onClick={() => editor.setSelection(undefined, input.token)}
            >
              Clear selection
            </Button>
          )}
        </div>
      )}
      <p className="mt-2 text-xs text-fg-2">
        {input?.selection
          ? "Only selected areas change. Photo proportions and unselected pixels are preserved."
          : "Select an area to protect the rest. Without a selection, the whole photo can change."}{" "}
        Your original stays private.
      </p>
      {selecting && selecting === input?.token && ref && url && (
        <Suspense fallback={<p role="status">Opening selection…</p>}>
          <PhotoMaskEditor
            key={selecting}
            url={url}
            width={ref.width}
            height={ref.height}
            selection={input.selection}
            onApply={(selection) => {
              editor.setSelection(selection, selecting);
              setSelecting(undefined);
            }}
            onClose={() => setSelecting(undefined)}
          />
        </Suspense>
      )}
      {frame && url && (
        <ImageViewer
          job={photo}
          jobs={[photo]}
          frame={frame}
          onClose={() => setFrame(undefined)}
        />
      )}
    </div>
  );
}
