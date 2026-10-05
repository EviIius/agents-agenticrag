import { AudioChip, UploadChip, type AudioUpload } from "./AudioChip";
import { useRef, useState, useLayoutEffect, useEffect } from "react";
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
  optimistic = false,
  running = false,
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
  transcriptionReady = false,
  uploads = [],
  audioExtensions = [],
  onCancelUpload,
  webBlocked = false,
}: {
  optimistic?: boolean;
  transcriptionReady?: boolean;
  audioExtensions?: string[];
  uploads?: AudioUpload[];
  onCancelUpload?: (id: string) => void;
  webBlocked?: boolean;
  starter?: string;
  suggestions?: boolean;
  running?: boolean;
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
  const revision = useRef(0),
    mounted = useRef(true);
  useEffect(() => {
    mounted.current = true;
    return () => {
      mounted.current = false;
    };
  }, []);
  const updateDraft = (text: string) => {
    revision.current++;
    setValue(text);
  };
  const fileInput = useRef<HTMLInputElement>(null);
  const textarea = useRef<HTMLTextAreaElement>(null);
  useLayoutEffect(() => {
    if (textarea.current) {
      textarea.current.style.height = "auto";
      textarea.current.style.height = `${Math.min(textarea.current.scrollHeight, window.innerHeight * 0.4)}px`;
    }
  }, [value]);
  const waiting =
    uploads.some((u) => !u.failed) ||
    files.some(
      (file) => file.kind === "audio" && file.transcript?.status !== "ready",
    );
  const recordingReady = files.some(
    (file) => file.kind === "audio" && file.transcript?.status === "ready",
  );
  const send = async () => {
    if (!running && !disabled && !waiting && value.trim()) {
      const submitted = value;
      const version = revision.current;
      if (optimistic) setValue("");
      const accepted = await onSend?.(submitted);
      if (!mounted.current || revision.current !== version) return;
      if (accepted === false && optimistic) setValue(submitted);
      else if (accepted !== false)
        setValue((draft) => (draft === submitted ? "" : draft));
    }
  };
  return (
    <>
      <form
        data-slot="composer"
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
        {uploads.map((upload) => (
          <UploadChip
            key={upload.id}
            upload={upload}
            onCancel={() => onCancelUpload?.(upload.id)}
          />
        ))}
        {files.map((file) =>
          file.kind === "audio" ? (
            <AudioChip
              key={file.id}
              attachment={file}
              model={model}
              onRemove={() => onRemove?.(file.id)}
            />
          ) : (
            <div
              key={file.id}
              data-slot="attachment-chip"
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
          ),
        )}
        <textarea
          ref={textarea}
          autoFocus={autoFocus}
          aria-label={model ? `Message ${model.display_name}` : "Message"}
          placeholder={
            model
              ? `Message ${model.display_name}…`
              : disabled
                ? "Choose a model to begin…"
                : "Message…"
          }
          value={value}
          onChange={(event) => updateDraft(event.target.value)}
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
                onSelect={() => {
                  if (fileInput.current) {
                    fileInput.current.accept = "image/*";
                    fileInput.current.click();
                  }
                }}
              >
                <span>
                  Add image
                  {!model?.vision && (
                    <span className="block text-xs text-fg-3">
                      Images need a vision model
                    </span>
                  )}
                </span>
              </DropdownMenuItem>
              <DropdownMenuItem
                onSelect={() => {
                  if (fileInput.current) {
                    fileInput.current.accept =
                      ".txt,.md,.csv,.json,.yaml,.yml,.py,.js,.ts,.tsx,.html,.css,.sql,.sh,.log";
                    fileInput.current.click();
                  }
                }}
              >
                Add text file
              </DropdownMenuItem>
              <DropdownMenuItem
                disabled={!transcriptionReady}
                onSelect={() => {
                  if (fileInput.current) {
                    fileInput.current.accept = audioExtensions.join(",");
                    fileInput.current.click();
                  }
                }}
              >
                {transcriptionReady
                  ? "Add recording"
                  : "Recordings need the transcription engine"}
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
          {onWebChange && (
            <Button
              type="button"
              variant="ghost"
              aria-label="Web search"
              aria-pressed={web && !webBlocked}
              aria-disabled={webBlocked}
              title={
                webBlocked
                  ? "Search is off in chats with a recording"
                  : undefined
              }
              className={`h-11 gap-2 px-2 rounded-full ${web && !webBlocked ? "bg-brand-soft text-brand" : ""}`}
              onClick={() => {
                if (!webBlocked) onWebChange(!web);
              }}
            >
              <Globe className="size-4" />
              <span className="hidden text-xs sm:inline">Search</span>
            </Button>
          )}
          {model?.reasoning && (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  type="button"
                  variant="ghost"
                  className="h-11 gap-2 px-2"
                  aria-label={`Think: ${thinkValue ?? "Model default"}`}
                >
                  <Brain className="size-4" />
                  <span className="hidden text-xs sm:inline">Think</span>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent>
                {["Model default", ...(model.reasoning?.options ?? [])].map(
                  (level) => (
                    <DropdownMenuItem
                      key={level}
                      onSelect={() => {
                        onThinkChange?.(
                          level === "Model default" ? null : level,
                        );
                      }}
                    >
                      {level[0].toUpperCase() + level.slice(1)}
                    </DropdownMenuItem>
                  ),
                )}
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
                      : "Context usage unavailable"
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
                      data-slot="context-ring"
                      strokeDasharray={
                        context
                          ? `${Math.min(1, (context.used_tokens + value.length * 0.3) / context.context_length) * 51} 51`
                          : "0 51"
                      }
                      transform="rotate(-90 10 10)"
                    />
                  </svg>
                </span>
              </TooltipTrigger>
              <TooltipContent>
                {context
                  ? `${Math.round(context.used_tokens + value.length * 0.3)} of ${context.context_length} tokens`
                  : "Choose a model to see context usage"}
              </TooltipContent>
            </Tooltip>
            <Tooltip>
              <TooltipTrigger asChild>
                <span
                  className="inline-flex"
                  tabIndex={waiting ? 0 : undefined}
                >
                  <Button
                    type={running ? "button" : "submit"}
                    size="icon"
                    aria-label={running ? "Stop generating" : "Send message"}
                    disabled={
                      !running && (disabled || waiting || !value.trim())
                    }
                    onClick={running ? onStop : undefined}
                    className={`size-11 rounded-full disabled:bg-surface-3 disabled:text-fg-2 disabled:opacity-100 ${running ? "bg-surface-3 text-fg" : "bg-brand text-on-brand"}`}
                  >
                    <span key={running ? "stop" : "send"} data-slot="send-icon">
                      {running ? <Square /> : <ArrowUp />}
                    </span>
                  </Button>
                </span>
              </TooltipTrigger>
              <TooltipContent>
                {waiting
                  ? "Waiting for the transcript"
                  : running
                    ? "Stop generating"
                    : "Send message"}
              </TooltipContent>
            </Tooltip>
          </div>
        </div>
      </form>
      {(suggestions || recordingReady) && (!recordingReady || !value) && (
        <div
          data-slot="suggestion-chips"
          className="mt-4 flex flex-wrap justify-center gap-2"
        >
          {(recordingReady
            ? ["Summarize", "Action items", "Decisions"]
            : [
                "Explain",
                "Write",
                "Code",
                ...(onWebChange ? ["Search the web"] : []),
              ]
          ).map((label) => (
            <Button
              key={label}
              variant="outline"
              className="min-h-11 rounded-full bg-surface text-sm"
              onClick={() => {
                updateDraft(
                  recordingReady
                    ? ({
                        Summarize: "Summarize this recording.",
                        "Action items":
                          "List action items from this recording.",
                        Decisions: "List the decisions from this recording.",
                      }[label] ?? "")
                    : label === "Search the web"
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
