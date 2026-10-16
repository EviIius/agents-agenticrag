import { Check, ImageIcon, X } from "lucide-react";
import { useEffect, useState } from "react";
import type { Attachment } from "@/lib/api";
import type { AttachmentLocal } from "@/hooks/useUploads";
import type { AudioUpload } from "./AudioChip";
import {
  fileSize,
  fileTone,
  splitFilename,
  suffix,
  type FileKind,
} from "@/lib/file-kinds";
export function FileName({ name }: { name: string }) {
  const [start, end] = splitFilename(name);
  return (
    <span className="attachment-name" title={name}>
      <span>{start}</span>
      <span>{end}</span>
    </span>
  );
}
export function FileBadge({ name, kind }: { name: string; kind?: FileKind }) {
  return (
    <span
      className="attachment-badge"
      data-tone={fileTone(name, kind)}
      aria-hidden
    >
      {suffix(name).slice(1, 6).toUpperCase() || "FILE"}
    </span>
  );
}
export function AttachmentTile({
  file,
  upload,
  local,
  issue,
  onRemove,
  onOpen,
  onPreviewLoaded,
  onRetry,
  preview = false,
}: {
  preview?: boolean;
  file?: Attachment;
  upload?: AudioUpload;
  local?: AttachmentLocal;
  issue?: "warning" | "error";
  onRemove: () => void;
  onOpen?: (element: HTMLElement) => void;
  onPreviewLoaded?: () => void;
  onRetry?: () => void;
}) {
  const name = file?.filename ?? upload!.filename;
  const photo = (file?.kind ?? upload?.kind) === "image";
  const server = file && !preview ? `/api/attachments/${file.id}` : undefined;
  const [showCheck, setShowCheck] = useState(false);
  useEffect(() => {
    if (!file || !local) return;
    setShowCheck(true);
    const timer = setTimeout(() => setShowCheck(false), 600);
    return () => clearTimeout(timer);
  }, [file?.id, local?.key]); // eslint-disable-line react-hooks/exhaustive-deps
  const [loaded, setLoaded] = useState(false),
    [broken, setBroken] = useState(false);
  useEffect(() => {
    if (!photo || !server || !local?.url) return;
    const image = new Image();
    image.onload = () => {
      setLoaded(true);
      setBroken(false);
      onPreviewLoaded?.();
    };
    image.src = server;
    return () => {
      image.onload = null;
    };
  }, [photo, server, local?.url, onPreviewLoaded]);
  const src = loaded ? server : (local?.url ?? server);
  const percent = upload?.percent ?? 100;
  const busy = upload && !upload.failed;
  const label = upload
    ? upload.failed
      ? upload.reason
      : upload.phase === "preparing"
        ? "Preparing…"
        : upload.phase === "reading"
          ? "Reading pages…"
          : `Uploading ${percent}%`
    : `${suffix(name).slice(1).toUpperCase() || "Text"} · ${fileSize(file?.bytes ?? 0)}`;
  return (
    <div
      className={`attachment-tile ${photo ? "attachment-photo" : "attachment-file-card"}`}
      data-issue={issue}
      data-slot="attachment-chip"
      data-phase={upload?.phase ?? "ready"}
      aria-description={upload?.reason}
    >
      <button
        className={photo ? "attachment-photo-open" : "attachment-file-open"}
        type="button"
        aria-label={photo ? `Open photo ${name}` : `Review file ${name}`}
        onClick={(e) => onOpen?.(e.currentTarget)}
        disabled={!onOpen}
      >
        {photo ? (
          <>
            <span className="sr-only">{name}</span>
            {src && !broken ? (
              <img
                src={src}
                alt=""
                decoding="async"
                onError={() => setBroken(true)}
              />
            ) : (
              <span className="attachment-photo-placeholder">
                <ImageIcon />
                <small>
                  {upload?.format ??
                    (/\.(heic|heif)$/i.test(name) ? "HEIC" : "Image")}
                </small>
              </span>
            )}
            {busy &&
              (upload.phase === "preparing" ? (
                <span
                  className="attachment-preparing"
                  data-slot="activity-spinner"
                  data-activity="spin"
                />
              ) : (
                <svg
                  className="attachment-upload-ring"
                  viewBox="0 0 28 28"
                  role="progressbar"
                  aria-label={`Uploading ${name}`}
                  aria-valuenow={percent}
                  aria-valuemin={0}
                  aria-valuemax={100}
                >
                  <circle
                    cx="14"
                    cy="14"
                    r="11"
                    pathLength="100"
                    strokeDasharray={`${percent} 100`}
                  />
                </svg>
              ))}
          </>
        ) : (
          <>
            <FileBadge name={name} kind={upload?.kind} />
            <span className="attachment-file-info">
              <FileName name={name} />
              <span
                className="attachment-meta"
                data-slot="activity-label"
                data-live={upload?.phase === "reading" || undefined}
              >
                {label}
              </span>
            </span>
          </>
        )}
      </button>
      {issue && (
        <span className="attachment-issue-badge" aria-label={issue}>
          !
        </span>
      )}
      <button
        type="button"
        className="attachment-remove"
        aria-label={
          upload && !upload.failed ? `Cancel upload ${name}` : `Remove ${name}`
        }
        onClick={onRemove}
      >
        <X />
      </button>
      {upload?.retryable && (
        <button type="button" className="attachment-retry" onClick={onRetry}>
          Retry
        </button>
      )}
      {!photo && busy && (
        <span
          className="attachment-upload-bar"
          role="progressbar"
          aria-label={`Uploading ${name}`}
          aria-valuenow={percent}
          aria-valuemin={0}
          aria-valuemax={100}
        >
          <span style={{ width: `${percent}%` }} />
        </span>
      )}
      {file && local && showCheck && (
        <span className="attachment-ready-check" key={local.key} aria-hidden>
          <Check />
        </span>
      )}
    </div>
  );
}
