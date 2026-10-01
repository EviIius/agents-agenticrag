import { Brain, ChevronDown } from "lucide-react";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
export function ReasoningBlock({ live = false }: { live?: boolean }) {
  return (
    <Collapsible
      defaultOpen={live}
      className="mb-6 rounded-lg border border-line"
    >
      <CollapsibleTrigger className="flex min-h-11 w-full items-center gap-2 px-3 text-sm text-fg-2">
        <Brain className="size-4" />
        {live ? "Thinking…" : "Thought for 2 seconds"}
        <ChevronDown className="ml-auto size-4" />
      </CollapsibleTrigger>
      <CollapsibleContent className="px-4 pb-4 text-sm leading-6 text-fg-2">
        Fake runtime reasoning: break the question into a few useful steps, then
        give a concise example. This text is a fixture.
      </CollapsibleContent>
    </Collapsible>
  );
}
