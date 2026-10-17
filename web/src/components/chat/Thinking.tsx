import { useEffect, useId, useRef, useState } from "react";
import { Brain, ChevronDown } from "lucide-react";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { WorkingLine } from "./WorkingLine";
import type { WorkingPhase } from "@/lib/status-words";

export function Thinking({
  id,
  text,
  live,
  duration,
  phase,
  onStop,
  startedAt,
}: {
  id: string;
  text: string;
  live: boolean;
  duration?: number | null;
  phase?: WorkingPhase;
  onStop?: () => void;
  startedAt?: number;
}) {
  const [open, setOpen] = useState(false),
    [began] = useState(() => startedAt ?? Date.now());
  const contentId = useId(),
    content = useRef<HTMLDivElement>(null),
    following = useRef(true),
    sawLive = useRef(live);
  const [observedDuration, setObservedDuration] = useState<number>();
  useEffect(() => {
    if (live) sawLive.current = true;
    else {
      setOpen(false);
      if (sawLive.current) setObservedDuration(Date.now() - began);
    }
  }, [live, began]);
  useEffect(() => {
    if (open && following.current && content.current)
      content.current.scrollTop = content.current.scrollHeight;
  }, [text, open]);
  return (
    <Collapsible
      open={open}
      onOpenChange={setOpen}
      className={
        live
          ? "thinking-live mb-4"
          : "thinking-complete mb-4 w-fit max-w-full rounded-lg border border-line"
      }
    >
      <WorkingLine
        id={id}
        began={began}
        phase={
          live
            ? (phase ?? {
                kind: "thinking",
                label: "Thinking",
                announcement: "Thinking",
              })
            : null
        }
        reasoning={!phase || phase.kind === "thinking" ? text : undefined}
        open={open}
        controls={contentId}
        onToggle={() => {
          following.current = true;
          setOpen(!open);
        }}
        onStop={onStop}
      />
      {!live && (
        <CollapsibleTrigger className="flex min-h-11 w-full items-center gap-2 px-3 text-sm text-fg-2">
          <Brain className="size-4" />
          <span>
            {(duration ?? observedDuration) == null
              ? "Thought process"
              : `Thought for ${Math.round((duration ?? observedDuration!) / 1000)} s`}
          </span>
          <ChevronDown className="ml-auto size-4" />
        </CollapsibleTrigger>
      )}
      <CollapsibleContent
        id={contentId}
        ref={content}
        tabIndex={0}
        role="region"
        aria-label="Model reasoning"
        onScroll={(event) => {
          const el = event.currentTarget;
          following.current =
            el.scrollHeight - el.clientHeight - el.scrollTop < 40;
        }}
        className="max-h-72 overflow-y-auto whitespace-pre-wrap px-4 pb-4 text-sm leading-6 text-fg-2"
      >
        {text}
      </CollapsibleContent>
    </Collapsible>
  );
}
