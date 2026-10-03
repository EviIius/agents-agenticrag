import { useRef, useState, useLayoutEffect } from "react";
import { ArrowUp, Plus, Brain, X, Square, Globe } from "lucide-react";
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
  model,
  disabled = false,
  onStop,
  web = false,
  onWebChange,
  onAttach,
  files = [],
  onRemove,
  context,
  thinkValue,
  onThinkChange,
  error,
  suggestions = false,
}: {
  starter?: string;
  suggestions?: boolean;
  running?: boolean;
  attached?: boolean;
  reasoning?: boolean;
  autoFocus?: boolean;
  onSend?: (text: string) => void | Promise<boolean | void>;
  error?: string;
  model?: import("@/lib/api").Model;
  disabled?: boolean;
  onStop?: () => void;
  web?: boolean;
  onWebChange?: (value: boolean) => void;
  onAttach?: (files: File[]) => void;
  files?: import("@/lib/api").Attachment[];
  onRemove?: (id: string) => void;
  context?: { used_tokens: number; context_length: number };
  thinkValue?: string;
  onThinkChange?: (value: string | null) => void;
}) {
  const [value, setValue] = useState(starter);
  const [attachment, setAttachment] = useState(attached);
  const [think, setThink] = useState("Off");
  const fileInput = useRef<HTMLInputElement>(null);
  const textarea = useRef<HTMLTextAreaElement>(null);
  useLayoutEffect(() => {
    if (textarea.current) {
      textarea.current.style.height = "auto";
      textarea.current.style.height = `${Math.min(textarea.current.scrollHeight, window.innerHeight * 0.4)}px`;
    }
  }, [value]);
  const send = async () => {
    if (!running && !disabled && value.trim()) {
      const submitted = value;
      const accepted = await onSend?.(submitted);
      if (accepted !== false) setValue((v) => (v === submitted ? "" : v));
    }
  };
  return (
    <>
      <form
        className="composer"
        aria-label="Message"
        onSubmit={(event) => {
          event.preventDefault();
          void send();
        }}
      >
        {error && (
          <p role="alert" className="mb-3 text-sm text-danger">
            {error}
          </p>
        )}
        <input
          type="file"
          multiple
          hidden
          ref={fileInput}
          onChange={(e) => {
            onAttach?.(Array.from(e.target.files ?? []));
            e.target.value = "";
          }}
        />
        {files.map((file) => (
          <div
            key={file.id}
            className="mb-2 inline-flex max-w-full items-center rounded-md border border-line px-2 text-xs"
          >
            <span className="truncate">{file.filename}</span>
            <IconButton
              label={`Remove ${file.filename}`}
              type="button"
              onClick={() => onRemove?.(file.id)}
            >
              <X />
            </IconButton>
          </div>
        ))}
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
          aria-label={
            model ? `Message ${model.display_name}` : "Message fake-chat"
          }
          placeholder={
            model
              ? `Message ${model.display_name}…`
              : disabled
                ? "Choose a model to begin…"
                : "Message fake-chat…"
          }
          value={value}
          onChange={(event) => setValue(event.target.value)}
          onPaste={(event) => {
            const files = Array.from(event.clipboardData.files);
            if (files.length) {
              event.preventDefault();
              onAttach?.(files);
            }
          }}
          onKeyDown={(event) => {
            if (event.key === "ArrowUp" && !value) {
              event.preventDefault();
              window.dispatchEvent(new Event("workbench:edit-last"));
            }
            if (event.key === "Escape" && running) {
              event.preventDefault();
              onStop?.();
            }
            if (
              event.key === "Enter" &&
              !event.shiftKey &&
              !event.nativeEvent.isComposing &&
              (!matchMedia("(pointer: coarse)").matches ||
                event.metaKey ||
                event.ctrlKey)
            ) {
              event.preventDefault();
              void send();
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
              <DropdownMenuItem
                disabled={model?.vision !== true}
                onSelect={() => fileInput.current?.click()}
              >
                {model?.vision ? "Add image" : "Images need a vision model"}
              </DropdownMenuItem>
              <DropdownMenuItem
                onSelect={() =>
                  onAttach ? fileInput.current?.click() : setAttachment(true)
                }
              >
                {onAttach ? "Add text file" : "Add text file (fixture)"}
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
          {onWebChange && (
            <IconButton
              label={web ? "Search on" : "Search off"}
              type="button"
              aria-pressed={web}
              className={web ? "bg-brand-soft text-brand" : ""}
              onClick={() => onWebChange(!web)}
            >
              <Globe />
            </IconButton>
          )}
          {(model?.reasoning || reasoning) && (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  type="button"
                  variant="ghost"
                  className="h-11 gap-2 px-2"
                  aria-label={`Think: ${thinkValue ?? (model ? "Model default" : think)}`}
                >
                  <Brain className="size-4" />
                  <span className="hidden text-xs sm:inline">Think</span>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent>
                {(model
                  ? ["Model default", ...(model.reasoning?.options ?? [])]
                  : ["Off", "On", "Low", "Medium", "High"]
                ).map((level) => (
                  <DropdownMenuItem
                    key={level}
                    onSelect={() => {
                      setThink(level);
                      onThinkChange?.(level === "Model default" ? null : level);
                    }}
                  >
                    {level[0].toUpperCase() + level.slice(1)}
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
                  aria-label={
                    context
                      ? `${Math.round(context.used_tokens + value.length * 0.3)} of ${context.context_length} tokens`
                      : "6.2K of 16K tokens"
                  }
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
                      strokeDasharray={
                        context
                          ? `${Math.min(1, (context.used_tokens + value.length * 0.3) / context.context_length) * 51} 51`
                          : "19 51"
                      }
                      transform="rotate(-90 10 10)"
                    />
                  </svg>
                </span>
              </TooltipTrigger>
              <TooltipContent>
                {context
                  ? `${Math.round(context.used_tokens + value.length * 0.3)} of ${context.context_length} tokens`
                  : "6.2K of 16K tokens · fixture"}
              </TooltipContent>
            </Tooltip>
            <Button
              type={running ? "button" : "submit"}
              size="icon"
              aria-label={running ? "Stop generating" : "Send message"}
              disabled={!running && (disabled || !value.trim())}
              onClick={running ? onStop : undefined}
              className={`size-11 rounded-full disabled:bg-surface-3 disabled:text-fg-2 disabled:opacity-100 ${running ? "bg-surface-3 text-fg" : "bg-brand text-on-brand"}`}
            >
              {running ? <Square /> : <ArrowUp />}
            </Button>
          </div>
        </div>
      </form>
      {suggestions && (
        <div className="mt-4 flex flex-wrap justify-center gap-2">
          {[
            "Explain",
            "Write",
            "Code",
            ...(onWebChange ? ["Search the web"] : []),
          ].map((label) => (
            <Button
              key={label}
              variant="outline"
              className="min-h-11 rounded-full bg-surface text-sm"
              onClick={() => {
                setValue(
                  label === "Search the web"
                    ? "Search the web for "
                    : label + " ",
                );
                if (label === "Search the web") onWebChange?.(true);
                textarea.current?.focus();
              }}
            >
              {label}
            </Button>
          ))}
        </div>
      )}
    </>
  );
}
