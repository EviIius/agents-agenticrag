import {
  lazy,
  Suspense,
  useEffect,
  useMemo,
  useState,
  useRef,
  useLayoutEffect,
} from "react";
import type { Attachment, Model } from "@/lib/api";
import type { AttachmentLocal } from "@/hooks/useUploads";
import { useUI } from "@/stores/ui";
import { attachmentIssues } from "@/lib/attachment-issues";
import { useReducedMotion } from "@/hooks/useReducedMotion";
import { AttachmentTile } from "./AttachmentTile";
import { AudioChip, type AudioUpload } from "./AudioChip";
import { DocumentChip } from "./DocumentChip";
import type { ViewerPhoto } from "./ImageViewer";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from "@/components/ui/dropdown-menu";
const ImageViewer = lazy(() =>
  import("./ImageViewer").then((m) => ({ default: m.ImageViewer })),
);
const DocumentSheet = lazy(() => import("./DocumentSheet"));
const emptyLocal: Record<string, AttachmentLocal> = {};
type Item = {
  key: string;
  file?: Attachment;
  upload?: AudioUpload;
  local?: AttachmentLocal;
  closing?: boolean;
};
function Presence({
  item,
  children,
  paused,
  dismiss,
  index,
  onExited,
}: {
  item: Item;
  children: React.ReactNode;
  paused: boolean;
  dismiss: () => void;
  index: number;
  onExited: () => void;
}) {
  const reduced = useReducedMotion();
  const exitRef = useRef(onExited);
  exitRef.current = onExited;
  const dismissRef = useRef(dismiss);
  dismissRef.current = dismiss;
  const [fresh, setFresh] = useState(!!item.local);
  useEffect(() => {
    const timer = setTimeout(() => setFresh(false), 200 + index * 40);
    return () => clearTimeout(timer);
  }, [index]);
  useEffect(() => {
    if (!item.upload?.failed || paused || item.closing) return;
    const timer = setTimeout(() => dismissRef.current(), 8000);
    return () => clearTimeout(timer);
  }, [item.upload?.failed, item.closing, paused]);
  useEffect(() => {
    if (!item.closing) return;
    const timer = setTimeout(() => exitRef.current(), reduced ? 0 : 320);
    return () => clearTimeout(timer);
  }, [item.closing, reduced]);
  return (
    <div
      className="attachment-presence"
      data-photo={
        (item.file?.kind ?? item.upload?.kind) === "image" || undefined
      }
      data-fresh={fresh || undefined}
      data-closing={item.closing || undefined}
      inert={item.closing}
      aria-hidden={item.closing || undefined}
      style={
        {
          "--attachment-exit": reduced ? "0ms" : "200ms",
          "--attachment-index": index,
        } as React.CSSProperties
      }
    >
      {children}
    </div>
  );
}
export function AttachmentTray({
  files,
  uploads,
  local = emptyLocal,
  model,
  reserve,
  onRemove,
  onCancel,
  onRetry,
  onPreviewLoaded,
  visionModels = [],
  onChooseModel,
  contextWarning,
  fixtures,
}: {
  fixtures?: {
    transcripts?: Record<string, import("@/lib/api").Transcript>;
    text?: Record<string, string>;
  };
  files: Attachment[];
  uploads: AudioUpload[];
  local?: Record<string, AttachmentLocal>;
  model?: Model;
  reserve?: number;
  onRemove?: (id: string) => void;
  onCancel?: (id: string) => void;
  onRetry?: (id: string) => void;
  onPreviewLoaded?: (id: string) => void;
  visionModels?: Model[];
  onChooseModel?: (model: Model) => void;
  contextWarning?: string;
}) {
  const items = useMemo<Item[]>(
    () =>
      [
        ...files.map((file) => ({
          key: local[file.id]?.key ?? file.id,
          file,
          local: local[file.id],
        })),
        ...uploads.map((upload) => ({
          key: local[upload.id]?.key ?? upload.id,
          upload,
          local: local[upload.id],
        })),
      ].sort((a, b) => (a.local?.order ?? -1) - (b.local?.order ?? -1)),
    [files, uploads, local],
  );
  const [present, setPresent] = useState<Item[]>([]),
    [paused, setPaused] = useState(false);
  const [hovered, setHovered] = useState<string>();
  const tray = useRef<HTMLDivElement>(null);
  const seen = useRef(new Set<string>());
  const [overflow, setOverflow] = useState(false);
  useLayoutEffect(() => {
    const node = tray.current;
    if (!node) return;
    const firstNew = present.find((i) => i.local && !seen.current.has(i.key));
    if (firstNew) {
      const index = present.findIndex((i) => i.key === firstNew.key);
      const child = node.children[index] as HTMLElement;
      if (child) node.scrollLeft = child.offsetLeft - node.offsetLeft;
    }
    present.forEach((i) => seen.current.add(i.key));
    const measure = () =>
      setOverflow(node.scrollLeft + node.clientWidth < node.scrollWidth - 2);
    measure();
    const observer = new ResizeObserver(measure);
    observer.observe(node);
    node.addEventListener("scroll", measure);
    return () => {
      observer.disconnect();
      node.removeEventListener("scroll", measure);
    };
  }, [present]);
  useEffect(() => {
    setPresent((old) => {
      if (!items.length && !old.length) return old;
      const remaining = new Map(items.map((item) => [item.key, item]));
      const next = old.map((item) => {
        const current = remaining.get(item.key);
        remaining.delete(item.key);
        return current ?? { ...item, closing: true };
      });
      return [...next, ...remaining.values()];
    });
  }, [items]);
  const announced = useRef(new Set<string>());
  const [announcement, setAnnouncement] = useState("");
  useEffect(() => {
    const ready = files.filter(
      (file) => local[file.id] && !announced.current.has(local[file.id].key),
    );
    if (!ready.length) return;
    ready.forEach((file) => announced.current.add(local[file.id].key));
    setAnnouncement(
      ready.map((file) => `${file.filename} attached`).join(". "),
    );
  }, [files, local]);
  const issues = attachmentIssues(files, uploads, model, reserve);
  const selectedIssue =
    issues.find((issue) => issue.key === hovered) ?? issues[0];
  const warnings = issues.filter((issue) => issue.kind === "warning");
  const issue =
    selectedIssue ??
    (contextWarning
      ? {
          key: "context",
          kind: "warning" as const,
          text: contextWarning,
          action: "controls" as const,
        }
      : undefined);
  const [viewer, setViewer] = useState<{
    photo: ViewerPhoto;
    frame: HTMLElement;
  }>();
  const [text, setText] = useState<Attachment>();
  const count = files.length + uploads.filter((u) => !u.failed).length;
  const photoItems = items.filter(
    (item) => (item.file?.kind ?? item.upload?.kind) === "image",
  );
  const photos = photoItems.flatMap((row): ViewerPhoto[] => {
    const url =
      row.local?.url ??
      (row.file ? `/api/attachments/${row.file.id}` : undefined);
    return url
      ? [
          {
            id: row.key,
            prompt: row.file?.filename ?? row.upload!.filename,
            url,
          },
        ]
      : [];
  });
  const openPhoto = (item: Item, frame: HTMLElement) => {
    const photo = photos.find((p) => p.id === item.key);
    if (photo) setViewer({ photo, frame });
  };
  const remove = (item: Item) =>
    item.file ? onRemove?.(item.file.id) : onCancel?.(item.upload!.id);
  const grouped =
    issue?.action === "model"
      ? warnings.filter((i) => i.action === "model").length
      : 1;
  const others = issues.filter(
    (i) =>
      i.action !== issue?.action ||
      (i.action !== "model" && i.key !== issue?.key),
  ).length;
  const issueText =
    grouped > 1
      ? issue?.text.replace("the photo.", `the ${grouped} photos.`)
      : issue?.text;
  const sentenceEnd = issueText?.indexOf(". ") ?? -1;
  return (
    <>
      {!!present.length && (
        <section
          className="attachment-tray-host"
          aria-label="Attachments"
          onMouseEnter={() => setPaused(true)}
          onMouseLeave={() => {
            setPaused(false);
            setHovered(undefined);
          }}
          onFocusCapture={() => setPaused(true)}
          onBlurCapture={(e) => {
            if (!e.currentTarget.contains(e.relatedTarget)) {
              setPaused(false);
              setHovered(undefined);
            }
          }}
        >
          <div
            className="attachment-tray"
            role="list"
            ref={tray}
            data-overflow={overflow || undefined}
          >
            {present.map((item) => {
              const file = item.file,
                key = file?.id ?? item.upload!.id;
              const flagged = issues.find((issue) => issue.key === key);
              return (
                <div
                  key={item.key}
                  role="listitem"
                  onMouseEnter={() => setHovered(key)}
                  onFocusCapture={() => setHovered(key)}
                >
                  <Presence
                    item={item}
                    index={item.local?.stagger ?? 0}
                    onExited={() =>
                      setPresent((old) =>
                        old.filter((row) => row.key !== item.key),
                      )
                    }
                    paused={paused || !!viewer || !!text}
                    dismiss={() => onCancel?.(key)}
                  >
                    {file?.kind === "audio" ? (
                      <AudioChip
                        fixture={fixtures?.transcripts?.[file.id]}
                        compact
                        attachment={file}
                        model={model}
                        reserve={reserve}
                        onRemove={() => onRemove?.(file.id)}
                      />
                    ) : file?.document ? (
                      <DocumentChip
                        compact
                        fixture={
                          fixtures?.text?.[file.id]
                            ? { text: fixtures.text[file.id] }
                            : undefined
                        }
                        attachment={file}
                        model={model}
                        reserve={reserve}
                        onRemove={() => onRemove?.(file.id)}
                      />
                    ) : (
                      <AttachmentTile
                        preview={!!fixtures}
                        file={file}
                        upload={item.upload}
                        local={item.local}
                        issue={flagged?.kind}
                        onRemove={() => remove(item)}
                        onRetry={() => onRetry?.(key)}
                        onPreviewLoaded={() => onPreviewLoaded?.(key)}
                        onOpen={
                          (file?.kind ?? item.upload?.kind) === "image"
                            ? (frame) => openPhoto(item, frame)
                            : file
                              ? () => setText(file)
                              : undefined
                        }
                      />
                    )}
                  </Presence>
                </div>
              );
            })}
            {count >= 5 && (
              <span className="attachment-count">{count} of 8</span>
            )}
          </div>
          <div className="sr-only" role="status">
            {announcement}
          </div>
          <div className="sr-only" role="status">
            {uploads
              .filter((u) => !u.failed)
              .map(
                (u) =>
                  `${u.phase === "preparing" ? "Preparing" : "Uploading"} ${u.filename}`,
              )
              .join(". ")}
          </div>
          {issue && (
            <div
              className="attachment-status"
              role="status"
              data-kind={issue.kind}
            >
              <span title={issueText}>
                {sentenceEnd < 0 ? (
                  issueText
                ) : (
                  <>
                    {issueText!.slice(0, sentenceEnd + 1)}
                    <span className="attachment-status-detail">
                      {issueText!.slice(sentenceEnd + 1)}
                    </span>
                  </>
                )}
              </span>
              {issue.action === "model" ? (
                <DropdownMenu modal={false}>
                  <DropdownMenuTrigger asChild>
                    <button type="button">Switch model</button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent
                    side="top"
                    align="start"
                    aria-label="Models that can see images"
                  >
                    {visionModels
                      .filter((m) => m.vision === true && !m.hidden)
                      .map((m) => (
                        <DropdownMenuItem
                          key={`${m.connection_id}:${m.model_id}`}
                          onSelect={() => onChooseModel?.(m)}
                        >
                          {m.display_name}
                        </DropdownMenuItem>
                      ))}
                    {!visionModels.some(
                      (m) => m.vision === true && !m.hidden,
                    ) && (
                      <DropdownMenuItem disabled>
                        No vision models are available.
                      </DropdownMenuItem>
                    )}
                  </DropdownMenuContent>
                </DropdownMenu>
              ) : issue.action === "controls" ? (
                <button
                  type="button"
                  onClick={() =>
                    useUI.getState().set({ panel: true, settings: false })
                  }
                >
                  Chat controls
                </button>
              ) : issue.action === "settings" ? (
                <button
                  type="button"
                  onClick={() =>
                    useUI.getState().set({
                      settings: true,
                      settingsPane: "Transcription",
                      panel: false,
                      sidebar: false,
                    })
                  }
                >
                  Settings
                </button>
              ) : issue.action === "retry" ? (
                <button type="button" onClick={() => onRetry?.(issue.key)}>
                  Retry
                </button>
              ) : (
                <button
                  type="button"
                  onClick={() => {
                    const item = items.find(
                      (i) =>
                        i.upload?.id === issue.key || i.file?.id === issue.key,
                    );
                    if (item) remove(item);
                  }}
                >
                  Remove
                </button>
              )}
              {others > 0 && <small>+{others} more</small>}
            </div>
          )}
        </section>
      )}
      {viewer && (
        <Suspense fallback={null}>
          <ImageViewer
            job={
              photos.find((photo) => photo.id === viewer.photo.id) ??
              viewer.photo
            }
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
