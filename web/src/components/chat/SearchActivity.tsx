import { Globe } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { Message, Source } from "@/lib/api";
import { Favicon } from "./CitationPill";
export function SearchActivity({
  message,
  sources,
  steps,
  onRetry,
}: {
  message: Message;
  sources: Source[];
  steps?: { label: string; detail: string; status: string }[];
  onRetry: () => void;
}) {
  const info = message.web,
    live = message.status === "streaming";
  const domains = Array.from(
    new Set([
      ...sources.map((source) => source.domain),
      ...(steps ?? [])
        .filter((step) => step.label === "read" && step.status === "ok")
        .flatMap((step) => {
          try {
            return [new URL(step.detail).hostname];
          } catch {
            return [];
          }
        }),
    ]),
  ).slice(0, 4);
  if (!info && !steps?.length) return null;
  if (info?.status === "skipped")
    return (
      <p className="mb-3 text-xs text-fg-3">
        No web search needed ·{" "}
        <Button variant="link" className="px-1 text-xs" onClick={onRetry}>
          Search anyway
        </Button>
      </p>
    );
  const notices: Record<string, string> = {
    search_failed: `Web search failed (${info?.notice?.message}). This answer uses the model's own knowledge.`,
    search_no_results: `The web search found nothing for “${info?.notice?.message}”. This answer uses the model's own knowledge.`,
    pages_unreadable: `Couldn't read any of the search results (${info?.notice?.message}). This answer uses the model's own knowledge.`,
  };
  return (
    <div className="mb-4 text-xs text-fg-2">
      {info?.notice && info.notice.code !== "uncited" && (
        <div className="mb-2 rounded-lg border border-line p-3" role="status">
          <p>{notices[info.notice.code] ?? info.notice.message}</p>
          <Button variant="link" className="px-0 text-xs" onClick={onRetry}>
            Retry with search
          </Button>
        </div>
      )}
      <details
        key={live ? "live" : "finished"}
        open={live}
        className="rounded-lg border border-line p-3"
      >
        <summary className="flex min-h-11 cursor-pointer flex-wrap items-center gap-2">
          <Globe className="size-4" />
          {live
            ? "Searching the web…"
            : `Searched the web · ${sources.length} sources · ${(Object.values(info?.timings ?? {}).reduce((a, b) => a + b, 0) / 1000).toFixed(1)}s`}
          <span className="flex gap-1">
            {domains.map((domain) => (
              <Favicon key={domain} domain={domain} />
            ))}
          </span>
        </summary>
        <ul className="space-y-2 border-t border-line pt-3">
          {(steps ?? []).map((s, i) => (
            <li key={i} className="break-words">
              {s.label} · {s.detail}
            </li>
          ))}
          {!steps?.length &&
            info?.queries?.map((q) => (
              <li key={q} className="break-words">
                {q}
              </li>
            ))}
        </ul>
      </details>
    </div>
  );
}
