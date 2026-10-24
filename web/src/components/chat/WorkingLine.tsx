import { useEffect, useMemo, useRef, useState } from "react";
import { ChevronDown } from "lucide-react";
import { useUI } from "@/stores/ui";
import { useActivityClock } from "@/hooks/useActivityClock";
import {
  statusSequence,
  thoughtTail,
  type WorkingPhase,
} from "@/lib/status-words";
import { AtelierMark } from "./AtelierMark";
import { paletteById } from "@/lib/palettes";
import { Button } from "@/components/ui/button";

function WorkingLabel({ text, live }: { text: string; live: boolean }) {
  const previous = useRef(text);
  const [outgoing, setOutgoing] = useState<string>();
  useEffect(() => {
    if (previous.current === text) return;
    setOutgoing(previous.current);
    previous.current = text;
    const timer = setTimeout(() => setOutgoing(undefined), 120);
    return () => clearTimeout(timer);
  }, [text]);
  return (
    <span
      className="working-word"
      data-slot="activity-label"
      data-live={live || undefined}
      aria-hidden="true"
    >
      {outgoing && outgoing !== text && (
        <span className="word-out">{outgoing}</span>
      )}
      <span className="word-in" key={text}>
        {text}
      </span>
    </span>
  );
}

export function WorkingLine({
  id,
  phase,
  began,
  reasoning,
  open,
  controls,
  onToggle,
  onStop,
}: {
  id: string;
  phase: WorkingPhase | null;
  began: number;
  reasoning?: string;
  open?: boolean;
  controls?: string;
  onToggle?: () => void;
  onStop?: () => void;
}) {
  const playful = useUI((s) => s.statusWords === "playful");
  const clock = useActivityClock(
    !!phase,
    began,
    phase?.kind === "working" && playful,
  );
  const paletteWords = useUI((s) => paletteById(s.palette).words);
  const words = useMemo(
    () => statusSequence(id, paletteWords ?? undefined),
    [id, paletteWords],
  );
  const label =
    phase?.kind === "working" && playful
      ? `${words[clock.index % words.length]}…`
      : phase?.label;
  const [last, setLast] = useState(
    phase ? { phase, label: label!, elapsed: clock.elapsed } : null,
  );
  useEffect(() => {
    if (phase && label) {
      setLast({ phase, label, elapsed: clock.elapsed });
      return;
    }
    const timer = setTimeout(() => setLast(null), 200);
    return () => clearTimeout(timer);
  }, [phase, label, clock.elapsed]);
  const shown = phase ? { phase, label: label!, elapsed: clock.elapsed } : last;
  if (!shown) return null;
  const header = (
    <>
      <AtelierMark think={shown.phase.kind === "thinking"} />
      <WorkingLabel text={shown.label} live={!!phase} />
      <span className="working-time" aria-hidden="true">
        {shown.elapsed >= 3 ? `${shown.elapsed} s` : ""}
      </span>
      {onToggle && (
        <ChevronDown className="ml-auto size-3.5 shrink-0" aria-hidden="true" />
      )}
    </>
  );
  return (
    <div
      className="working-line"
      data-slot="working-line"
      data-phase={shown.phase.kind}
      data-state={phase ? "open" : "closed"}
      aria-hidden={!phase || undefined}
      inert={!phase}
    >
      <span role="status" className="sr-only">
        {phase?.announcement ?? ""}
      </span>
      {onToggle ? (
        <button
          className="thinking-toggle"
          onClick={onToggle}
          aria-label={open ? "Hide thinking" : "Show thinking"}
          aria-expanded={!!open}
          aria-controls={controls}
        >
          <span className="working-header">{header}</span>
          {!open && reasoning && (
            <span className="thought-ticker" aria-hidden="true">
              <span>…{thoughtTail(reasoning)}</span>
            </span>
          )}
        </button>
      ) : (
        <div className="working-header">{header}</div>
      )}
      {phase?.kind === "thinking" && clock.elapsed >= 60 && (
        <div className="mt-3 text-sm text-fg-2" data-testid="long-thinking">
          <p role="status">
            Still thinking after a minute. More thinking does not guarantee a
            better answer. You can stop this reply and choose a lower level in
            Tools for your next message.
          </p>
          {onStop && (
            <Button variant="outline" onClick={onStop}>
              Stop reply
            </Button>
          )}
        </div>
      )}
    </div>
  );
}
