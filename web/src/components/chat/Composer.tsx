import { AudioChip, UploadChip, type AudioUpload } from "./AudioChip";
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
  transcriptionReady = false,
  uploads = [],
  onCancelUpload,
  webBlocked = false,
}: {
  transcriptionReady?: boolean;
  uploads?: AudioUpload[];
  onCancelUpload?: (id: string) => void;
  webBlocked?: boolean;
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
                onSelect={() => {
                  if (fileInput.current) {
                    fileInput.current.accept = "image/*";
                    fileInput.current.click();
                  }
                }}
              >
                {model?.vision ? "Add image" : "Images need a vision model"}
              </DropdownMenuItem>
              <DropdownMenuItem
                onSelect={() =>
                  onAttach
                    ? (() => {
                        if (fileInput.current) {
                          fileInput.current.accept =
                            ".txt,.md,.csv,.json,.yaml,.yml,.py,.js,.ts,.tsx,.html,.css,.sql,.sh,.log";
                          fileInput.current.click();
                        }
                      })()
                    : setAttachment(true)
                }
              >
                {onAttach ? "Add text file" : "Add text file (fixture)"}
              </DropdownMenuItem>
              <DropdownMenuItem
                disabled={!transcriptionReady}
                onSelect={() => {
                  if (fileInput.current) {
                    fileInput.current.accept =
                      ".wav,.mp3,.m4a,.flac,.aif,.aiff,.aac,.amr,.caf,.mka,.mov,.mp4,.oga,.ogg,.opus,.webm,.wma";
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
            <IconButton
              label={
                webBlocked
                  ? "Search is off in chats with a recording"
                  : web
                    ? "Search on"
                    : "Search off"
              }
              type="button"
              aria-pressed={web && !webBlocked}
              aria-disabled={webBlocked}
              className={web && !webBlocked ? "bg-brand-soft text-brand" : ""}
              onClick={() => {
                if (!webBlocked) onWebChange(!web);
              }}
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
                    {running ? <Square /> : <ArrowUp />}
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
        <div className="mt-4 flex flex-wrap justify-center gap-2">
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
                setValue(
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
