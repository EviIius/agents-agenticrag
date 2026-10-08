import { BookOpen, Check, ChevronDown } from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import type { components } from "@/lib/api-types";

export type Scope = components["schemas"]["LibraryScope"] | null;
export function LibraryControl({
  enabled,
  reason,
  scope,
  collections,
  onToggle,
  onScope,
}: {
  enabled: boolean;
  reason?: string;
  scope: Scope;
  collections: components["schemas"]["LibraryCollectionInfo"][];
  onToggle: (enabled: boolean) => void;
  onScope: (scope: Scope) => void;
}) {
  const [tipOpen, setTipOpen] = useState(false);
  return (
    <div className="flex shrink-0 items-center">
      <Tooltip open={tipOpen} onOpenChange={setTipOpen}>
        <TooltipTrigger asChild>
          <Button
            type="button"
            variant="ghost"
            aria-label="Library"
            aria-pressed={enabled}
            aria-disabled={!enabled && !!reason}
            aria-description={reason}
            onFocus={() => {
              if (reason) setTipOpen(true);
            }}
            className={`h-11 min-w-11 gap-2 rounded-full px-2 ${enabled ? "bg-brand-soft text-brand" : ""}`}
            onClick={() => {
              if (enabled || !reason) onToggle(!enabled);
              else setTipOpen(true);
            }}
          >
            <BookOpen className="size-4" />
            <span className="hidden text-xs sm:inline">Library</span>
          </Button>
        </TooltipTrigger>
        <TooltipContent>
          {reason ?? "Answer using your Library files"}
        </TooltipContent>
      </Tooltip>
      <Popover>
        <PopoverTrigger asChild>
          <Button
            type="button"
            size="icon"
            variant="ghost"
            aria-label="Choose Library collections"
            className="h-11 w-11"
          >
            <ChevronDown className="size-3" />
          </Button>
        </PopoverTrigger>
        <PopoverContent
          className="max-h-[60dvh] w-[min(280px,calc(100vw-24px))] overflow-y-auto"
          aria-label="Library scope"
        >
          <p className="mb-2 text-sm font-medium">Search files in</p>
          {reason && (
            <p role="status" className="mb-3 text-xs text-fg-2">
              {reason}
            </p>
          )}
          <Button
            type="button"
            variant="ghost"
            className="min-h-11 w-full justify-start gap-2"
            aria-pressed={scope === null}
            onClick={() => onScope(null)}
          >
            {scope === null && <Check className="size-4" />}All files
          </Button>
          {collections.map((c) => (
            <label
              key={c.id}
              className="flex min-h-11 cursor-pointer items-center gap-3 text-sm"
            >
              <input
                type="checkbox"
                checked={scope?.collection_ids?.includes(c.id) ?? false}
                onChange={(e) =>
                  onScope({
                    collection_ids: e.target.checked
                      ? [...(scope?.collection_ids ?? []), c.id]
                      : (scope?.collection_ids ?? []).filter(
                          (id) => id !== c.id,
                        ),
                  })
                }
              />
              <span className="min-w-0 break-words">{c.name}</span>
            </label>
          ))}
          {scope && !scope.collection_ids?.length && (
            <p className="mt-2 text-xs text-fg-2">
              Choose a collection or All files.
            </p>
          )}
        </PopoverContent>
      </Popover>
    </div>
  );
}
