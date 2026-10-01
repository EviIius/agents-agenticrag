import { useRef, useState, useLayoutEffect } from "react";
import { ArrowUp, Plus, Brain, X, Square } from "lucide-react";
import { Button } from "@/components/ui/button";
import { IconButton } from "@/components/app/IconButton";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
export function Composer({
  starter = "",
  running = false,
  attached = false,
  reasoning = false,
  autoFocus = false,
  onSend,
}: {
  starter?: string;
  running?: boolean;
  attached?: boolean;
  reasoning?: boolean;
  autoFocus?: boolean;
  onSend?: (text: string) => void;
}) {
  const [value, setValue] = useState(starter);
  const [attachment, setAttachment] = useState(attached);
  const [think, setThink] = useState("Off");
  const textarea = useRef<HTMLTextAreaElement>(null);
  useLayoutEffect(() => {
    if (textarea.current) {
      textarea.current.style.height = "auto";
      textarea.current.style.height = `${Math.min(textarea.current.scrollHeight, window.innerHeight * 0.4)}px`;
    }
  }, [value]);
  const send = () => {
    if (value.trim()) {
      onSend?.(value);
      setValue("");
    }
  };
  return (
    <form
      className="composer"
      aria-label="Message"
      onSubmit={(event) => {
        event.preventDefault();
        send();
      }}
    >
      {attachment && (
        <div className="mb-3 inline-flex max-w-full items-center rounded-md border border-line px-2 text-xs">
          <span className="truncate">notes.md · fixture</span>
          <IconButton
            label="Remove attachment"
            onClick={() => setAttachment(false)}
            type="button"
          >
            <X />
          </IconButton>
        </div>
      )}
      <textarea
        ref={textarea}
        autoFocus={autoFocus}
        aria-label="Message fake-chat"
        placeholder="Message fake-chat…"
        value={value}
        onChange={(event) => setValue(event.target.value)}
        onKeyDown={(event) => {
          if (
            event.key === "Enter" &&
            !event.shiftKey &&
            !event.nativeEvent.isComposing &&
            (!matchMedia("(pointer: coarse)").matches ||
              event.metaKey ||
              event.ctrlKey)
          ) {
            event.preventDefault();
            send();
          }
        }}
        rows={2}
      />
      <div className="flex min-w-0 items-center gap-1">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <IconButton label="Add attachment" type="button">
              <Plus />
            </IconButton>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start">
            <DropdownMenuItem disabled>
              Add image · this fixture model is text only
            </DropdownMenuItem>
            <DropdownMenuItem onSelect={() => setAttachment(true)}>
              Add text file (fixture)
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
        {reasoning && (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                type="button"
                variant="ghost"
                className="h-11 gap-2 px-2"
                aria-label={`Think: ${think}`}
              >
                <Brain className="size-4" />
                <span className="text-xs">Think {think}</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent>
              {["Off", "On", "Low", "Medium", "High"].map((level) => (
                <DropdownMenuItem key={level} onSelect={() => setThink(level)}>
                  {level}
                </DropdownMenuItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>
        )}
        <div className="ml-auto flex items-center gap-2">
          <Tooltip>
            <TooltipTrigger asChild>
              <span
                tabIndex={0}
                role="img"
                aria-label="6.2K of 16K tokens"
                className="flex size-11 items-center justify-center"
              >
                <svg viewBox="0 0 20 20" className="size-[18px]" aria-hidden>
                  <circle
                    cx="10"
                    cy="10"
                    r="8"
                    fill="none"
                    stroke="var(--line)"
                    strokeWidth="2"
                  />
                  <circle
                    cx="10"
                    cy="10"
                    r="8"
                    fill="none"
                    stroke="var(--text-3)"
                    strokeWidth="2"
                    strokeDasharray="19 51"
                    transform="rotate(-90 10 10)"
                  />
                </svg>
              </span>
            </TooltipTrigger>
            <TooltipContent>6.2K of 16K tokens · fixture</TooltipContent>
          </Tooltip>
          <Button
            type={running ? "button" : "submit"}
            size="icon"
            aria-label={running ? "Stop generating" : "Send message"}
            disabled={!running && !value.trim()}
            className={`size-11 rounded-full disabled:bg-surface-3 disabled:text-fg-2 disabled:opacity-100 ${running ? "bg-surface-3 text-fg" : "bg-brand text-on-brand"}`}
          >
            {running ? <Square /> : <ArrowUp />}
          </Button>
        </div>
      </div>
    </form>
  );
}
