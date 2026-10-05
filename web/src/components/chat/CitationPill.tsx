import { useState, useEffect, useRef } from "react";
import {
  Popover,
  PopoverTrigger,
  PopoverContent,
} from "@/components/ui/popover";
import { X } from "lucide-react";
import { IconButton } from "@/components/app/IconButton";
import { useMediaQuery } from "@/hooks/useMediaQuery";
import { bestPassage } from "@/lib/citations";
import type { Source } from "@/lib/api";
export function Favicon({ domain }: { domain: string }) {
  const [failed, setFailed] = useState(false);
  return (
    <span
      className="inline-flex size-5 shrink-0 items-center justify-center rounded bg-surface-3 text-xs text-fg-2"
      aria-hidden="true"
      data-domain={domain}
    >
      {failed ? (
        domain[0]?.toUpperCase()
      ) : (
        <img
          className="size-4"
          src={"/api/favicon/" + encodeURIComponent(domain)}
          alt=""
          onError={() => setFailed(true)}
        />
      )}
    </span>
  );
}
export function CitationPill({
  sources,
  sentence,
}: {
  sources: Source[];
  sentence: string;
}) {
  const [open, setOpen] = useState(false);
  const finePointer = useMediaQuery("(hover: hover) and (pointer: fine)");
  const timer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  const hover = useRef(false);
  const restoringFocus = useRef(false);
  useEffect(() => () => clearTimeout(timer.current), []);
  const enter = () => {
    clearTimeout(timer.current);
    hover.current = true;
    timer.current = setTimeout(() => setOpen(true), 150);
  };
  const leave = () => {
    clearTimeout(timer.current);
    if (hover.current) timer.current = setTimeout(() => setOpen(false), 200);
  };
  if (!sources.length) return null;
  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <button
          className="citation-pill mx-0.5 inline-flex items-center bg-cite font-sans text-xs font-medium text-cite-fg hover:bg-cite-hover focus-visible:outline-brand"
          onClick={() => {
            clearTimeout(timer.current);
            hover.current = false;
          }}
          aria-label={"View source: " + sources.map((s) => s.title).join("; ")}
          onPointerEnter={(e) => {
            if (finePointer && e.pointerType === "mouse") enter();
          }}
          onFocus={() => {
            if (restoringFocus.current) {
              restoringFocus.current = false;
              return;
            }
            if (finePointer) enter();
          }}
          onBlur={(event) => {
            if (
              !(event.relatedTarget instanceof HTMLElement) ||
              !event.relatedTarget.closest('[aria-label="Citation sources"]')
            )
              leave();
          }}
          onPointerLeave={leave}
        >
          {sources[0]!.n}
          {sources.length > 1 ? ` +${sources.length - 1}` : ""}
        </button>
      </PopoverTrigger>
      <PopoverContent
        aria-label="Citation sources"
        className="max-h-[min(70dvh,calc(var(--viewport-h,100dvh)-80px),var(--radix-popover-content-available-height))] w-[min(340px,calc(100vw-24px))] overflow-y-auto p-4"
        collisionPadding={12}
        onKeyDownCapture={(event) => {
          if (event.key === "Escape") {
            event.preventDefault();
            event.stopPropagation();
            clearTimeout(timer.current);
            hover.current = false;
            setOpen(false);
          }
        }}
        onCloseAutoFocus={() => {
          clearTimeout(timer.current);
          hover.current = false;
          restoringFocus.current = true;
        }}
        onOpenAutoFocus={(event) => {
          if (hover.current) event.preventDefault();
        }}
        onPointerEnter={() => clearTimeout(timer.current)}
        onPointerLeave={leave}
        onFocusCapture={() => {
          clearTimeout(timer.current);
          hover.current = false;
        }}
      >
        <div className="flex items-center justify-between gap-2">
          <p className="text-xs font-medium text-fg-2">
            Source {sources[0]!.n}
          </p>
          <IconButton
            label="Close citation"
            onClick={() => {
              clearTimeout(timer.current);
              hover.current = false;
              setOpen(false);
            }}
          >
            <X />
          </IconButton>
        </div>
        {sources.map((s) => (
          <div
            key={s.n}
            className="space-y-2 border-b border-line py-2 last:border-0"
          >
            <p className="flex items-center gap-2 text-xs text-fg-3">
              <Favicon domain={s.domain} />
              <span className="min-w-0 break-all">
                {s.domain} · {s.published_at ?? "Date unknown"}
              </span>
            </p>
            <p className="text-sm font-medium break-words">{s.title}</p>
            <p className="source-passage text-[14px] leading-[21px] text-fg-2">
              {bestPassage(s, sentence)}
            </p>
            {s.kind === "snippet" && (
              <p className="text-xs text-fg-3">Search snippet</p>
            )}
            <a
              className="inline-flex min-h-11 items-center text-xs text-brand"
              href={s.url}
              target="_blank"
              rel="noopener noreferrer"
            >
              Open page ↗
            </a>
          </div>
        ))}
      </PopoverContent>
    </Popover>
  );
}
