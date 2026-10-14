import { useRef, useState } from "react";
import { createRoot, type Root } from "react-dom/client";
import { flushSync } from "react-dom";
import { BlockCard } from "./BlockNode";
import { defaults } from "./registry";
import { useReducedMotion } from "@/hooks/useReducedMotion";
import { Search, StickyNote } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import {
  availability,
  categories,
  registry,
  type CatalogKind,
} from "./registry";
import type { Catalog, Kind, Block } from "./types";
export function BlocksPanel({
  catalog,
  add,
}: {
  catalog?: Catalog;
  add: (kind: CatalogKind) => void;
}) {
  const [query, setQuery] = useState("");
  const input = useRef<HTMLInputElement>(null);
  const ghost = useRef<{ element: HTMLElement; root: Root } | undefined>(
    undefined,
  );
  const reduced = useReducedMotion();
  return (
    <aside className="wf-blocks" aria-label="Blocks">
      <div className="wf-blocks-search">
        <Search />
        <Input
          ref={input}
          aria-label="Search blocks"
          placeholder="Search blocks"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
      </div>
      <div className="wf-blocks-list">
        {categories.map((category) => (
          <details key={category} open className="wf-category">
            <summary>{category}</summary>
            {(Object.keys(registry) as CatalogKind[])
              .filter(
                (k) =>
                  registry[k].category === category &&
                  registry[k].label.toLowerCase().includes(query.toLowerCase()),
              )
              .map((kind) => {
                const meta = registry[kind],
                  state = availability(kind, catalog);
                return (
                  <Tooltip key={kind} delayDuration={400}>
                    <TooltipTrigger asChild>
                      <Button
                        variant="ghost"
                        className="wf-palette-block"
                        draggable={state.available}
                        aria-disabled={!state.available}
                        aria-label={meta.label}
                        onClick={() => state.available && add(kind)}
                        onDragStart={(e) => {
                          if (!state.available) {
                            e.preventDefault();
                            return;
                          }
                          e.dataTransfer.setData(
                            "application/x-atelier-block",
                            kind,
                          );
                          e.dataTransfer.effectAllowed = "copy";
                          if (kind !== "note") {
                            const element = document.createElement("div");
                            element.className = "wf-drag-ghost";
                            element.dataset.reduced = String(reduced);
                            document.body.append(element);
                            const root = createRoot(element);
                            const block = {
                              id: "n_ghost",
                              kind,
                              key: kind,
                              title: meta.label,
                              position: { x: 0, y: 0 },
                              disabled: false,
                              config: defaults(kind as Kind),
                            } as Block;
                            flushSync(() =>
                              root.render(<BlockCard block={block} />),
                            );
                            e.dataTransfer.setDragImage(element, 144, 30);
                            ghost.current = { element, root };
                          }
                        }}
                        onDragEnd={() => {
                          ghost.current?.root.unmount();
                          ghost.current?.element.remove();
                          ghost.current = undefined;
                        }}
                      >
                        <span className="wf-tile" data-cat={meta.tone}>
                          <meta.Icon />
                        </span>
                        <span>{meta.label}</span>
                      </Button>
                    </TooltipTrigger>
                    <TooltipContent>
                      {state.available
                        ? meta.description
                        : (state.reason ?? "This block isn't available yet.")}
                    </TooltipContent>
                  </Tooltip>
                );
              })}
          </details>
        ))}
      </div>
      <footer>
        <Button
          variant="ghost"
          className="wf-palette-block"
          aria-label="Note"
          onClick={() => add("note")}
        >
          <span className="wf-tile" data-cat="logic">
            <StickyNote />
          </span>
          <span>Note</span>
        </Button>
      </footer>
    </aside>
  );
}
