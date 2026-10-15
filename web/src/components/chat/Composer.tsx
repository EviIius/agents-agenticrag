import { DocumentChip } from "./DocumentChip";
import { contextBudget } from "@/lib/context-budget";
import { LibraryControl } from "./LibraryControl";
import { AudioChip, UploadChip, type AudioUpload } from "./AudioChip";
import {
  useRef,
  useState,
  useLayoutEffect,
  useEffect,
  useCallback,
} from "react";
import {
  ArrowUp,
  Plus,
  Brain,
  X,
  Square,
  Globe,
  ImageIcon,
  MoreHorizontal,
  ChevronDown,
} from "lucide-react";
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
import {
  imageDrafts,
  drafts,
  imageRefinements,
  type ImageComposerCommand,
} from "@/lib/composer-drafts";
import { validImageSeed } from "@/lib/image-seeds";
export function Composer({
  draftKey,
  images = false,
  previewImages = false,
  imageStatus,
  initialImageMode = false,
  imageBusy = false,
  onImageSend,
  imageCommand,
  onImageCommandApplied,
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
  attachmentVersion = 0,
  onRemove,
  context,
  thinkValue,
  onThinkChange,
  error,
  suggestions = false,
  transcriptionReady = false,
  uploads = [],
  audioExtensions = [],
  attachmentExtensions,
  onCancelUpload,
  webBlocked = false,
  libraryControl,
}: {
  draftKey?: string;
  images?: boolean;
  previewImages?: boolean;
  imageStatus?: import("@/lib/api-types").components["schemas"]["ImageStatus"];
  initialImageMode?: boolean;
  imageBusy?: boolean;
  imageCommand?: ImageComposerCommand;
  onImageCommandApplied?: (key: string) => void;
  onImageSend?: (
    prompt: string,
    count: number,
    seeds?: number[],
    sourceJob?: string,
  ) => Promise<boolean>;
  optimistic?: boolean;
  libraryControl?: React.ComponentProps<typeof LibraryControl>;
  transcriptionReady?: boolean;
  audioExtensions?: string[];
  attachmentExtensions?: import("@/lib/api").Bootstrap["attachment_extensions"];
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
  attachmentVersion?: number;
  onRemove?: (id: string) => void;
  context?: { used_tokens: number; context_length: number; reserve?: number };
  thinkValue?: string;
  onThinkChange?: (value: string | null) => void;
}) {
  const [value, setValue] = useState(() =>
    draftKey ? (drafts.get(draftKey) ?? starter) : starter,
  );
  const [imageValue, setImageValue] = useState(() =>
    draftKey ? (imageDrafts.get(draftKey) ?? "") : "",
  );
  const [refinement, setRefinement] = useState(() =>
    draftKey ? imageRefinements.get(draftKey) : undefined,
  );
  const [imageMode, setImageMode] = useState(initialImageMode);
  const previousAttachmentVersion = useRef(attachmentVersion);
  useEffect(() => {
    const incoming = attachmentVersion !== previousAttachmentVersion.current;
    previousAttachmentVersion.current = attachmentVersion;
    if (incoming) setImageMode(false);
  }, [attachmentVersion]);
  const [count, setCount] = useState(1);
  const [seeds, setSeeds] = useState(["", "", ""]);
  const imageAvailable = previewImages || Boolean(imageStatus?.available);
  const visibleValue = imageMode ? imageValue : value;
  const validSeeds = seeds
    .slice(0, count)
    .every((seed) => !seed || validImageSeed(seed));
  const fixedSeeds = seeds.slice(0, count).some(Boolean);
  const completeSeeds = !fixedSeeds || seeds.slice(0, count).every(Boolean);
  useEffect(() => {
    if (draftKey) {
      drafts.set(draftKey, value);
      imageDrafts.set(draftKey, imageValue);
    }
  }, [draftKey, value, imageValue]);
  const [attachmentMenuOpen, setAttachmentMenuOpen] = useState(false);
  const restoreAttachmentBackground = useRef<() => void>(() => {});
  const bindAttachmentMenu = useCallback((node: HTMLDivElement | null) => {
    restoreAttachmentBackground.current();
    if (!node?.isConnected) return;
    const changed: HTMLElement[] = [];
    let current: HTMLElement | null = node;
    while (current && current !== document.body) {
      for (const sibling of current.parentElement?.children ?? []) {
        if (
          sibling instanceof HTMLElement &&
          sibling !== current &&
          !sibling.inert
        ) {
          sibling.inert = true;
          changed.push(sibling);
        }
      }
      current = current.parentElement;
    }
    restoreAttachmentBackground.current = () => {
      for (const sibling of changed) sibling.inert = false;
    };
  }, []);
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
    if (!imageMode && text.startsWith("/image ") && imageAvailable) {
      setImageMode(true);
      setImageValue(text.slice(7));
      setValue("");
    } else if (imageMode) setImageValue(text);
    else setValue(text);
  };
  const toggleImage = () => {
    setImageMode((mode) => !mode);
    requestAnimationFrame(() => textarea.current?.focus());
  };
  const fileInput = useRef<HTMLInputElement>(null);
  const textarea = useRef<HTMLTextAreaElement>(null);
  useLayoutEffect(() => {
    if (textarea.current) {
      textarea.current.style.height = "auto";
      textarea.current.style.height = `${Math.min(textarea.current.scrollHeight, window.innerHeight * 0.4)}px`;
    }
  }, [visibleValue]);
  const waiting =
    uploads.some((u) => !u.failed) ||
    files.some(
      (file) => file.kind === "audio" && file.transcript?.status !== "ready",
    );
  const recordingReady = files.some(
    (file) => file.kind === "audio" && file.transcript?.status === "ready",
  );
  const budget = contextBudget(model, context?.reserve);
  const estimatedInput = Math.round(
    (context?.used_tokens ?? 0) + value.length * 0.3,
  );
  const contextLabel = context
    ? `${estimatedInput.toLocaleString()} of ${context.context_length.toLocaleString()} total tokens; ${budget.available.toLocaleString()} input allowance; ${budget.reserve.toLocaleString()} reserved for response; 256 safety margin`
    : "Context usage unavailable";
  useLayoutEffect(() => {
    if (!imageCommand) return;
    revision.current++;
    setImageMode(imageCommand.mode === "image");
    if (imageCommand.refinement) {
      setRefinement(imageCommand.refinement);
      setImageValue(imageCommand.refinement.job.prompt);
      if (draftKey) imageRefinements.set(draftKey, imageCommand.refinement);
    }
    onImageCommandApplied?.(imageCommand.key);
    requestAnimationFrame(() => {
      const field = textarea.current;
      if (field) {
        field.focus();
        field.setSelectionRange(field.value.length, field.value.length);
      }
    });
  }, [imageCommand?.key]); // eslint-disable-line react-hooks/exhaustive-deps
  const send = async () => {
    if (imageMode) {
      if (
        running ||
        imageBusy ||
        !imageAvailable ||
        !imageValue.trim() ||
        !validSeeds ||
        !completeSeeds
      )
        return;
      const submitted = imageValue,
        version = revision.current;
      const accepted = await onImageSend?.(
        submitted,
        count,
        fixedSeeds ? seeds.slice(0, count).map(Number) : undefined,
        refinement?.job.id,
      );
      if (
        accepted !== false &&
        draftKey &&
        imageDrafts.get(draftKey) === submitted
      )
        imageDrafts.delete(draftKey);
      if (
        accepted !== false &&
        mounted.current &&
        revision.current === version
      ) {
        setImageValue("");
        setRefinement(undefined);
        if (draftKey) imageRefinements.delete(draftKey);
      }
      return;
    }
    if (!running && !disabled && !waiting && value.trim()) {
      const submitted = value;
      const version = revision.current;
      if (optimistic) setValue("");
      const accepted = await onSend?.(submitted);
      if (
        draftKey &&
        revision.current === version &&
        accepted !== false &&
        (drafts.get(draftKey) === submitted ||
          (optimistic && drafts.get(draftKey) === ""))
      )
        drafts.delete(draftKey);
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
        data-image-mode={imageMode || undefined}
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
        {imageMode && refinement && (
          <div
            className="mb-3 flex w-fit max-w-full items-center gap-2 rounded-lg border border-line bg-surface-2 px-2 py-1 text-sm text-fg-2"
            data-slot="image-refinement"
          >
            <img
              className="size-8 rounded object-cover"
              src={`/api/images/jobs/${refinement.job.id}/output/png`}
              alt=""
            />
            <span>
              Refining image {refinement.position} · seed {refinement.job.seed}
            </span>
            <IconButton
              label="Remove refinement source"
              type="button"
              onClick={() => {
                revision.current++;
                setRefinement(undefined);
                if (draftKey) imageRefinements.delete(draftKey);
                textarea.current?.focus();
              }}
            >
              <X />
            </IconButton>
          </div>
        )}
        {!imageMode && (
          <>
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
                  reserve={context?.reserve}
                  onRemove={() => onRemove?.(file.id)}
                />
              ) : file.document ? (
                <DocumentChip
                  key={file.id}
                  attachment={file}
                  model={model}
                  reserve={context?.reserve}
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
            {files.some(
              (file) =>
                file.document ||
                (file.kind === "audio" &&
                  (file.transcript?.token_estimate ?? 0) <= budget.available),
            ) &&
              context &&
              estimatedInput > budget.available && (
                <p role="status" className="mb-3 text-xs text-warning">
                  This message and its attachments may exceed the input
                  allowance ({budget.available.toLocaleString()} tokens after
                  reserving {budget.reserve.toLocaleString()} for the response
                  and 256 for safety). Lower Max output tokens in Chat controls,
                  choose a larger context or remove an attachment.
                </p>
              )}
          </>
        )}
        <textarea
          ref={textarea}
          autoFocus={autoFocus}
          aria-label={
            imageMode
              ? "Image prompt"
              : model
                ? `Message ${model.display_name}`
                : "Message"
          }
          placeholder={
            imageMode
              ? "Describe an image…"
              : model
                ? `Message ${model.display_name}…`
                : disabled
                  ? "Choose a model to begin…"
                  : "Message…"
          }
          value={visibleValue}
          onChange={(event) => updateDraft(event.target.value)}
          onPaste={(event) => {
            const files = Array.from(event.clipboardData.files);
            if (files.length) {
              event.preventDefault();
              setImageMode(false);
              onAttach?.(files);
            }
          }}
          onKeyDown={(event) => {
            if (!imageMode && event.key === "ArrowUp" && !value) {
              event.preventDefault();
              window.dispatchEvent(new Event("workbench:edit-last"));
            }
            if (event.key === "Escape" && imageMode && !imageValue) {
              event.preventDefault();
              toggleImage();
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
        <div className="flex min-w-0 flex-wrap items-center gap-1">
          {!imageMode && (
            <>
              <DropdownMenu
                open={attachmentMenuOpen}
                onOpenChange={setAttachmentMenuOpen}
              >
                <DropdownMenuTrigger asChild>
                  <IconButton label="Add attachment" type="button">
                    <Plus />
                  </IconButton>
                </DropdownMenuTrigger>
                <DropdownMenuContent
                  ref={bindAttachmentMenu}
                  onCloseAutoFocus={() => restoreAttachmentBackground.current()}
                  align="start"
                  onKeyDown={(event) => {
                    // Escape also works before Radix's document listener mounts.
                    if (event.key === "Escape") {
                      event.preventDefault();
                      setAttachmentMenuOpen(false);
                    }
                  }}
                >
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
                          attachmentExtensions?.text?.join(",") ?? "";
                        fileInput.current.click();
                      }
                    }}
                  >
                    Add text file
                  </DropdownMenuItem>
                  <DropdownMenuItem
                    onSelect={() => {
                      if (fileInput.current) {
                        fileInput.current.accept =
                          attachmentExtensions?.document?.join(",") ?? "";
                        fileInput.current.click();
                      }
                    }}
                  >
                    Add document (PDF, Word)
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
            </>
          )}
          {images && (
            <Tooltip>
              <TooltipTrigger asChild>
                <span
                  className="inline-flex"
                  tabIndex={!imageAvailable && !imageMode ? 0 : undefined}
                >
                  <Button
                    type="button"
                    variant="ghost"
                    className={`h-11 min-w-11 gap-2 rounded-full px-2 ${imageMode ? "bg-brand-soft text-brand" : ""}`}
                    aria-label={imageMode ? "Leave image mode" : "Create image"}
                    aria-pressed={imageMode}
                    disabled={!imageAvailable && !imageMode}
                    title={
                      !imageAvailable
                        ? (imageStatus?.reason ??
                          "Connecting to the image service…")
                        : undefined
                    }
                    onClick={toggleImage}
                  >
                    <ImageIcon className="size-4" />
                    <span
                      className={
                        imageMode ? "text-xs" : "hidden text-xs sm:inline"
                      }
                    >
                      Image
                    </span>
                    {imageMode && <X className="size-3" />}
                  </Button>
                </span>
              </TooltipTrigger>
              <TooltipContent>
                {!imageAvailable
                  ? (imageStatus?.reason ?? "Connecting to the image service…")
                  : imageMode
                    ? "Leave image mode"
                    : "Create images in this chat"}
              </TooltipContent>
            </Tooltip>
          )}
          {imageMode && (
            <>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button
                    type="button"
                    variant="outline"
                    className="h-11 rounded-full gap-1"
                    aria-label="Image count"
                  >
                    {count} image{count > 1 ? "s" : ""}
                    <ChevronDown className="size-3" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent>
                  {[1, 2, 3].map((n) => (
                    <DropdownMenuItem key={n} onSelect={() => setCount(n)}>
                      {n} image{n > 1 ? "s" : ""}
                    </DropdownMenuItem>
                  ))}
                </DropdownMenuContent>
              </DropdownMenu>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <IconButton label="Image options" type="button">
                    <MoreHorizontal />
                  </IconButton>
                </DropdownMenuTrigger>
                <DropdownMenuContent
                  className="p-3"
                  onCloseAutoFocus={(event) => {
                    event.preventDefault();
                    textarea.current?.focus();
                  }}
                >
                  <p className="mb-2 text-sm font-medium">
                    Seed · {fixedSeeds ? "Fixed" : "Automatic"}
                  </p>
                  <p className="mb-2 max-w-60 text-xs text-fg-2">
                    Leave every field empty for a new result. To repeat an
                    image, set one seed for each image.
                  </p>
                  {Array.from({ length: count }, (_, i) => (
                    <label key={i} className="mb-2 block text-xs">
                      Seed {i + 1}
                      <input
                        className="mt-1 block h-11 w-full rounded-md border border-line bg-surface-2 px-2 text-base"
                        aria-label={`Seed ${i + 1}`}
                        inputMode="numeric"
                        placeholder="Automatic"
                        value={seeds[i]}
                        onChange={(event) =>
                          setSeeds((old) =>
                            old.map((seed, n) =>
                              n === i ? event.target.value : seed,
                            ),
                          )
                        }
                      />
                    </label>
                  ))}
                  {(!validSeeds || !completeSeeds) && (
                    <p role="alert" className="text-xs text-danger">
                      Use 0–4,294,967,295 for every image, or leave all seeds
                      empty.
                    </p>
                  )}
                </DropdownMenuContent>
              </DropdownMenu>
            </>
          )}
          {!imageMode && (
            <>
              {libraryControl && <LibraryControl {...libraryControl} />}
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
            </>
          )}
          <div className="ml-auto flex items-center gap-2">
            {imageMode && (
              <span className="hidden text-xs text-fg-3 md:inline">
                {imageStatus?.model ?? "FLUX.2 klein"} ·{" "}
                {imageStatus?.width ?? 1024}²
              </span>
            )}
            {!imageMode && (
              <>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <span
                      tabIndex={0}
                      role="img"
                      aria-label={contextLabel}
                      className="flex size-11 items-center justify-center"
                    >
                      <svg
                        viewBox="0 0 20 20"
                        className="size-[18px]"
                        aria-hidden
                      >
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
                      ? contextLabel
                      : "Choose a model to see context usage"}
                  </TooltipContent>
                </Tooltip>
              </>
            )}
            <Tooltip>
              <TooltipTrigger asChild>
                <span
                  className="inline-flex"
                  tabIndex={waiting ? 0 : undefined}
                >
                  <Button
                    type={running ? "button" : "submit"}
                    size="icon"
                    aria-label={
                      running
                        ? "Stop generating"
                        : imageMode
                          ? "Create image"
                          : "Send message"
                    }
                    disabled={
                      !running &&
                      (imageMode
                        ? imageBusy ||
                          !imageAvailable ||
                          !imageValue.trim() ||
                          !validSeeds ||
                          !completeSeeds
                        : disabled || waiting || !value.trim())
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
                {imageMode
                  ? !validSeeds || !completeSeeds
                    ? "Set one valid seed for each image, or leave all empty"
                    : "Create image"
                  : waiting
                    ? uploads.some((u) => u.kind === "document" && !u.failed)
                      ? "Waiting for the document"
                      : "Waiting for the transcript"
                    : running
                      ? "Stop generating"
                      : imageMode
                        ? "Create image"
                        : "Send message"}
              </TooltipContent>
            </Tooltip>
          </div>
        </div>
      </form>
      {!imageMode &&
        (suggestions || recordingReady) &&
        (!recordingReady || !value) && (
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
