import { useEffect, useState } from "react";
import {
  Collapsible,
  CollapsibleTrigger,
  CollapsibleContent,
} from "@/components/ui/collapsible";
import { Globe, ChevronDown } from "lucide-react";
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
  const info = message.web;
  const live =
    message.status === "streaming" &&
    !(steps ?? []).some((step) =>
      ["done", "failed", "skipped"].includes(step.label),
    );
  const [open, setOpen] = useState(live);
  useEffect(() => setOpen(live), [live]);
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
  if (info?.notice?.code === "search_blocked_recording")
    return (
      <p
        role="status"
        className="mb-3 rounded-lg border border-line p-3 text-xs text-fg-2"
      >
        Web search is off in chats with a recording, so nothing from it leaves
        this Mac.
      </p>
    );
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
    <div className="mb-4 text-xs text-fg-2" data-testid="search-activity">
      {info?.notice && info.notice.code !== "uncited" && (
        <div className="mb-2 rounded-lg border border-line p-3" role="status">
          <p>{notices[info.notice.code] ?? info.notice.message}</p>
          <Button variant="link" className="px-0 text-xs" onClick={onRetry}>
            Retry with search
          </Button>
        </div>
      )}
      <Collapsible open={open} onOpenChange={setOpen} className="py-1">
        <CollapsibleTrigger className="flex min-h-11 w-full cursor-pointer flex-wrap items-center gap-2 text-left">
          {!domains.length && <Globe className="size-4" />}
          <span className="flex gap-1">
            {domains.map((domain, index) => (
              <span
                key={domain}
                data-slot="activity-favicon"
                data-stagger={index}
              >
                <Favicon domain={domain} />
              </span>
            ))}
          </span>
          <span data-slot="activity-label" data-live={live || undefined}>
            {live
              ? "Searching the web…"
              : `Searched the web · ${sources.length} sources · ${(Object.values(info?.timings ?? {}).reduce((a, b) => a + b, 0) / 1000).toFixed(1)} s`}
          </span>
          <ChevronDown className="ml-auto size-3" />
        </CollapsibleTrigger>
        <CollapsibleContent>
          <ul className="space-y-2 border-t border-line pt-3">
            {(steps ?? []).map((s, i) => (
              <li
                key={i}
                data-slot="search-step"
                data-live={live || undefined}
                className="break-words"
              >
                {activityCopy(s)}
              </li>
            ))}
            {!steps?.length &&
              info?.queries?.map((q) => (
                <li key={q} className="break-words">
                  {q}
                </li>
              ))}
          </ul>
        </CollapsibleContent>
      </Collapsible>
    </div>
  );
}

function activityCopy(step: { label: string; detail: string; status: string }) {
  if (step.label === "read" || step.label === "reading") {
    let site = step.detail;
    try {
      site = new URL(step.detail).hostname;
    } catch {
      /* Keep the supplied detail. */
    }
    return `${step.status === "failed" ? "Couldn't read" : "Read"} ${site}`;
  }
  if (step.label === "query" || step.label === "search")
    return `Searched: ${step.detail}`;
  if (step.label === "plan") return step.detail || "Planning the search";
  if (step.label === "done") return "Search complete";
  return step.detail || step.label.replaceAll("_", " ");
}
