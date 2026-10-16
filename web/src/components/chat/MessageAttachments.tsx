import { lazy, Suspense, useState } from "react";
import type { Attachment, Model } from "@/lib/api";
import type { AttachmentLocal } from "@/hooks/useUploads";
import type { ViewerPhoto } from "./ImageViewer";
import type { AttachmentTray } from "./AttachmentTray";
import { AudioChip } from "./AudioChip";
import { DocumentChip } from "./DocumentChip";
import { FileBadge, FileName } from "./AttachmentTile";
import { fileSize, suffix } from "@/lib/file-kinds";
const ImageViewer = lazy(() =>
  import("./ImageViewer").then((m) => ({ default: m.ImageViewer })),
);
const DocumentSheet = lazy(() => import("./DocumentSheet"));

export default function MessageAttachments({
  attachments,
  local,
  model,
  fixtures,
}: {
  attachments: Attachment[];
  local?: Record<string, AttachmentLocal>;
  model?: Model;
  fixtures?: React.ComponentProps<typeof AttachmentTray>["fixtures"];
}) {
  const [viewer, setViewer] = useState<{
    photo: ViewerPhoto;
    frame: HTMLElement;
  }>();
  const [text, setText] = useState<Attachment>();
  const [broken, setBroken] = useState<Record<string, boolean>>({});
  const photos: ViewerPhoto[] = attachments
    .filter((f) => f.kind === "image")
    .map((f) => ({
      id: f.id,
      prompt: f.filename,
      url: local?.[f.id]?.url ?? `/api/attachments/${f.id}`,
    }));
  const files = attachments.filter((f) => f.kind !== "image");
  return (
    <>
      <div className="message-attachments" data-slot="message-attachments">
        {!!photos.length && (
          <div
            className="message-photos"
            data-count={Math.min(photos.length, 3)}
          >
            {photos.slice(0, 6).map((photo, index) => (
              <button
                type="button"
                key={photo.id}
                className="message-photo"
                data-attachment-id={photo.id}
                aria-label={`Open photo ${photo.prompt}`}
                onClick={(e) => setViewer({ photo, frame: e.currentTarget })}
              >
                <img
                  src={photo.url}
                  alt=""
                  loading="lazy"
                  decoding="async"
                  onError={() =>
                    setBroken((old) => ({ ...old, [photo.id]: true }))
                  }
                />
                {broken[photo.id] && (
                  <span className="message-photo-error">{photo.prompt}</span>
                )}
                {index === 5 && photos.length > 6 && (
                  <span className="message-photo-more">
                    +{photos.length - 6}
                  </span>
                )}
              </button>
            ))}
          </div>
        )}
        {!!files.length && (
          <div className="message-files">
            {files.map((file) =>
              file.kind === "audio" ? (
                <AudioChip
                  key={file.id}
                  attachment={file}
                  model={model}
                  compact
                  fixture={fixtures?.transcripts?.[file.id]}
                />
              ) : file.document ? (
                <DocumentChip
                  key={file.id}
                  attachment={file}
                  model={model}
                  compact
                  fixture={
                    fixtures?.text?.[file.id]
                      ? { text: fixtures.text[file.id] }
                      : undefined
                  }
                />
              ) : (
                <button
                  key={file.id}
                  type="button"
                  className="attachment-file-card message-text-file"
                  aria-label={`Review file ${file.filename}`}
                  onClick={() => setText(file)}
                >
                  <FileBadge name={file.filename} />
                  <span className="attachment-file-info">
                    <FileName name={file.filename} />
                    <span className="attachment-meta">
                      {suffix(file.filename) === ".md"
                        ? "Markdown"
                        : suffix(file.filename).slice(1).toUpperCase() ||
                          "Text"}{" "}
                      · {fileSize(file.bytes)}
                    </span>
                  </span>
                </button>
              ),
            )}
          </div>
        )}
      </div>
      {viewer && (
        <Suspense fallback={null}>
          <ImageViewer
            job={photos.find((p) => p.id === viewer.photo.id) ?? viewer.photo}
            jobs={photos}
            frame={viewer.frame}
            onClose={() => setViewer(undefined)}
          />
        </Suspense>
      )}
      {text && (
        <Suspense fallback={<p role="status">Opening file…</p>}>
          <DocumentSheet
            attachment={text}
            open
            onOpenChange={(open) => {
              if (!open) setText(undefined);
            }}
            textFile
            fixture={
              fixtures?.text?.[text.id]
                ? { text: fixtures.text[text.id] }
                : undefined
            }
          />
        </Suspense>
      )}
    </>
  );
}
