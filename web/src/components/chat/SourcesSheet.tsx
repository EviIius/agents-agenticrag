import {
  Collapsible,
  CollapsibleTrigger,
  CollapsibleContent,
} from "@/components/ui/collapsible";
import { useState } from "react";
import { Globe, ChevronDown, X, BookOpen } from "lucide-react";
import { IconButton } from "@/components/app/IconButton";
import { useUI } from "@/stores/ui";
import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetTitle,
  SheetDescription,
} from "@/components/ui/sheet";
import {
  Drawer,
  DrawerContent,
  DrawerHeader,
  DrawerTitle,
  DrawerDescription,
} from "@/components/ui/drawer";
import { useMediaQuery } from "@/hooks/useMediaQuery";
import type { Message, Source, WebRead } from "@/lib/api";
import { SourceIcon, sourcePages } from "./CitationPill";
export function SourcesSheet({
  message,
  sources,
  reads,
}: {
  message: Message;
  sources: Source[];
  reads: WebRead[];
}) {
  const [open, setOpen] = useState(false),
    phone = useMediaQuery("(max-width:639px)");
  const body = (
    <div className="space-y-5 p-5">
      <div className="space-y-2">
        <h3 className="text-sm font-medium">Queries</h3>
        {(message.library?.queries ?? message.web?.queries)?.map((q) => (
          <p key={q} className="text-xs text-fg-2 break-words">
            {q}
          </p>
        ))}
        <p className="text-xs text-fg-3">
          {message.library
            ? "Your Library · Local retrieval"
            : `via ${message.web?.providers?.join(", ") || "Unknown provider"}`}
          {Object.entries(message.web?.timings ?? {})
            .filter(([key]) =>
              ["plan", "search", "fetch", "read"].includes(key),
            )
            .map(
              ([key, ms]) =>
                ` · ${key === "fetch" ? "read" : key} ${(ms / 1000).toFixed(1)} s`,
            )
            .join("")}
          {message.web?.plan_fallback ? " · Planner fallback used" : ""}
        </p>
      </div>
      {sources.map((s) => (
        <section key={s.n} className="rounded-lg border border-line p-3">
          <div className="flex items-start gap-2">
            <SourceIcon source={s} />
            <div className="min-w-0 flex-1">
              <p className="text-xs text-fg-3 break-all">
                {s.n} ·{" "}
                {s.kind === "document" ? sourcePages(s) || "Library" : s.domain}{" "}
                · {s.cited ? "Cited" : "Read, not cited"}
                {s.kind === "snippet" ? " · Search snippet" : ""}
              </p>
              {s.url ? (
                <a
                  href={s.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block min-h-11 py-3 text-sm font-medium [overflow-wrap:anywhere]"
                >
                  {s.title} ↗
                </a>
              ) : (
                <p className="py-3 text-sm font-medium break-words">
                  {s.title}
                </p>
              )}
              <p className="text-xs text-fg-3">
                {s.kind === "document"
                  ? s.document_id
                    ? sourcePages(s)
                    : "Original file removed; saved passages retained"
                  : `Published: ${s.published_at ?? "Unknown"}`}
              </p>
            </div>
          </div>
          <Collapsible className="mt-2">
            <CollapsibleTrigger className="flex min-h-11 w-full items-center gap-2 cursor-pointer py-3 text-xs font-medium">
              What the model saw
              <ChevronDown className="ml-auto size-3" />
            </CollapsibleTrigger>
            <CollapsibleContent>
              {s.passages.map((p) => (
                <div key={p.ord} className="border-t border-line py-3">
                  <h4 className="text-xs font-medium">
                    {p.heading}
                    {p.page_start != null
                      ? ` · p. ${p.page_start}${p.page_end !== p.page_start ? `–${p.page_end}` : ""}`
                      : ""}
                  </h4>
                  <pre className="source-passage mt-2 whitespace-pre-wrap break-words text-[15px] leading-[23px] text-fg-2">
                    {p.text}
                  </pre>
                </div>
              ))}
            </CollapsibleContent>
          </Collapsible>
        </section>
      ))}
      {reads
        .filter((r) => !sources.some((s) => s.url === r.url))
        .map((r) => (
          <section
            key={r.url}
            className="rounded-lg border border-line p-3 text-xs"
          >
            <p className="font-medium">
              {r.status === "failed" ? "Couldn't read" : "Read, not cited"}
            </p>
            <p className="my-2 break-all text-fg-2">{r.title ?? r.url}</p>
            {r.reason && <p className="text-fg-3">{r.reason}</p>}
          </section>
        ))}
    </div>
  );
  return (
    <>
      <Button
        variant="ghost"
        className="my-3 max-w-full gap-2"
        onClick={() => {
          if (phone) useUI.getState().set({ sidebar: false, panel: false });
          setOpen(true);
        }}
      >
        <span className="flex -space-x-1">
          {sources.slice(0, 4).map((s) => (
            <SourceIcon key={s.n} source={s} />
          ))}
        </span>
        {message.library ? (
          <BookOpen className="size-4" />
        ) : (
          <Globe className="size-4" />
        )}
        {sources.length} sources
        <ChevronDown className="size-3" />
      </Button>
      {phone ? (
        <Drawer open={open} onOpenChange={setOpen}>
          <DrawerContent className="overflow-hidden">
            <DrawerHeader className="relative px-14">
              <IconButton
                label="Close sources"
                className="absolute right-3 top-2"
                onClick={() => setOpen(false)}
              >
                <X />
              </IconButton>
              <DrawerTitle>Sources</DrawerTitle>
              <DrawerDescription>
                The exact passages supplied for this answer.
              </DrawerDescription>
            </DrawerHeader>
            <div className="min-h-0 flex-1 overflow-y-auto">{body}</div>
          </DrawerContent>
        </Drawer>
      ) : (
        <Sheet open={open} onOpenChange={setOpen}>
          <SheetContent className="w-full overflow-y-auto sm:max-w-md">
            <div className="px-5 pt-5 pr-12">
              <SheetTitle>Sources</SheetTitle>
              <SheetDescription>
                The exact passages supplied for this answer.
              </SheetDescription>
            </div>
            {body}
          </SheetContent>
        </Sheet>
      )}
    </>
  );
}
