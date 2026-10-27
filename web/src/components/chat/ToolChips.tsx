import { Brain, Globe, X } from "lucide-react";
import { LibraryControl } from "./LibraryControl";
import type { LibraryTools } from "./ToolsMenu";
import { thinkingLabel } from "@/lib/chat-presentation";
export function ToolChips({
  web,
  library,
  thinkValue,
  onWebChange,
  onThinkChange,
  openTools,
  focusTools,
}: {
  web: boolean;
  library?: LibraryTools;
  thinkValue?: string;
  onWebChange?: (value: boolean) => void;
  onThinkChange?: (value: string | null) => void;
  openTools: () => void;
  focusTools: () => void;
}) {
  const chip = (
    kind: string,
    label: string,
    icon: React.ReactNode,
    remove: () => void,
  ) => (
    <span className="composer-tool-chip" key={kind} data-slot="tool-chip">
      <button type="button" onClick={openTools} aria-label={label}>
        {icon}
        <span className="chip-label">{label}</span>
      </button>
      <button
        type="button"
        aria-label={
          kind === "Thinking"
            ? "Use model default thinking"
            : `Turn ${kind} off`
        }
        onClick={() => {
          remove();
          focusTools();
        }}
      >
        <X />
      </button>
    </span>
  );
  return (
    <div className="composer-active-tools">
      {web && chip("Search", "Search", <Globe />, () => onWebChange?.(false))}
      {library?.enabled && (
        <LibraryControl {...library} compact onDisabled={focusTools} />
      )}
      {thinkValue &&
        chip(
          "Thinking",
          thinkValue === "off"
            ? "No thinking"
            : `Think · ${thinkingLabel(thinkValue)}`,
          <Brain />,
          () => onThinkChange?.(null),
        )}
    </div>
  );
}
