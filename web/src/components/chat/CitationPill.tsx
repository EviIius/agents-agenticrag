import { useState } from "react";
import {
  Popover,
  PopoverTrigger,
  PopoverContent,
} from "@/components/ui/popover";
import { bestPassage } from "@/lib/citations";
import type { Source } from "@/lib/api";
export function Favicon({ domain }: { domain: string }) {
  const [failed, setFailed] = useState(false);
  return (
    <span
      className="inline-flex size-5 shrink-0 items-center justify-center rounded bg-surface-3 text-xs text-fg-2"
      aria-hidden="true"
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
  if (!sources.length) return null;
  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <button
          className="mx-0.5 inline-flex min-h-11 max-w-full items-center rounded-md bg-cite-bg px-2 align-baseline font-sans text-xs font-medium text-cite-text break-all hover:bg-cite-bg-hover focus-visible:outline-brand"
          onClick={(e) => {
            e.preventDefault();
            setOpen(true);
          }}
          aria-label={"View source: " + sources.map((s) => s.title).join("; ")}
          onPointerEnter={(e) => {
            if (e.pointerType === "mouse") setOpen(true);
          }}
        >
          {sources[0]!.domain}
          {sources.length > 1 ? ` +${sources.length - 1}` : ""}
        </button>
      </PopoverTrigger>
      <PopoverContent
        aria-label="Citation sources"
        className="max-h-[70dvh] w-[min(360px,calc(100vw-24px))] overflow-y-auto p-4"
      >
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
            <p className="text-xs leading-5 text-fg-2">
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
