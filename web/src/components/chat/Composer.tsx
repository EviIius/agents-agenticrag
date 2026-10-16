import { attachmentIssues } from "@/lib/attachment-issues";
import { ToolsMenu } from "./ToolsMenu";
import { ToolChips } from "./ToolChips";
import { fileAccept } from "@/lib/file-kinds";
import { useMediaQuery } from "@/hooks/useMediaQuery";
import type { AttachmentLocal } from "@/hooks/useUploads";
import { contextBudget } from "@/lib/context-budget";
import { LibraryControl } from "./LibraryControl";
import { type AudioUpload } from "./AudioChip";
import {
  lazy,
  Suspense,
  useRef,
  useState,
  useLayoutEffect,
  useEffect,
} from "react";
import {
  ArrowUp,
  Plus,
  X,
  Square,
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
const AttachmentTray = lazy(() =>
  import("./AttachmentTray").then((m) => ({ default: m.AttachmentTray })),
);
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
  attachmentFixtures,
  attachmentLocal,
  onPreviewLoaded,
  onRetryUpload,
  visionModels,
  onChooseModel,
  onDiscardPasted,
}: {
  attachmentFixtures?: React.ComponentProps<typeof AttachmentTray>["fixtures"];
  attachmentLocal?: Record<string, AttachmentLocal>;
  onPreviewLoaded?: (id: string) => void;
  onRetryUpload?: (id: string) => void;
  visionModels?: import("@/lib/api").Model[];
  onChooseModel?: (model: import("@/lib/api").Model) => void;
  onDiscardPasted?: (key: string) => void;
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
  onAttach?: (
    files: File[],
    pasted?: { characters: number },
  ) => string[] | void;
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
  const [toolsOpen, setToolsOpen] = useState(false);
  const toolsButton = useRef<HTMLButtonElement>(null);
  const coarse = useMediaQuery("(pointer: coarse)");
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
  const hasFiles = files.length > 0 || uploads.length > 0;
  const [showTray, setShowTray] = useState(hasFiles);
  useEffect(() => {
    if (hasFiles) setShowTray(true);
  }, [hasFiles]);
  const pasteSerial = useRef({ image: 0, text: 0 });
  const [pasted, setPasted] = useState<{
    key: string;
    text: string;
    before: string;
    start: number;
    end: number;
  }>();
  useEffect(() => {
    if (!pasted || disabled) return;
    const timer = setTimeout(() => setPasted(undefined), 10000);
    return () => clearTimeout(timer);
  }, [pasted, disabled]);
  const keepPastedText = () => {
    if (!pasted || disabled) return;
    const field = textarea.current;
    const unchanged = value === pasted.before;
    const start = unchanged
      ? pasted.start
      : (field?.selectionStart ?? value.length);
    const end = unchanged ? pasted.end : (field?.selectionEnd ?? start);
    onDiscardPasted?.(pasted.key);
    updateDraft(value.slice(0, start) + pasted.text + value.slice(end));
    setPasted(undefined);
    requestAnimationFrame(() => {
      field?.focus();
      field?.setSelectionRange(
        start + pasted.text.length,
        start + pasted.text.length,
      );
    });
  };
  useLayoutEffect(() => {
    if (textarea.current) {
      textarea.current.style.height = "auto";
      textarea.current.style.height = `${Math.min(textarea.current.scrollHeight, 200, window.innerHeight * 0.4)}px`;
    }
  }, [visibleValue]);
  const waiting =
    uploads.some((u) => !u.failed) ||
    files.some(
      (file) => file.kind === "audio" && file.transcript?.status !== "ready",
    );
  const fileCount = files.length + uploads.filter((u) => !u.failed).length;
  const waitingCount =
    uploads.filter((u) => !u.failed).length +
    files.filter((f) => f.kind === "audio" && f.transcript?.status !== "ready")
      .length;
  const uploadProgress = Math.round(
    (uploads.filter((u) => !u.failed).reduce((sum, u) => sum + u.percent, 0) +
      files.length * 100) /
      Math.max(1, fileCount),
  );
  const indeterminate =
    files.some((f) => f.kind === "audio" && f.transcript?.status !== "ready") ||
    uploads.some(
      (u) => !u.failed && ["preparing", "reading"].includes(u.phase ?? ""),
    );
  useEffect(() => {
    if (imageMode || coarse || fileCount >= 8) return;
    const listener = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "u") {
        event.preventDefault();
        fileInput.current?.click();
      }
    };
    window.addEventListener("keydown", listener);
    return () => window.removeEventListener("keydown", listener);
  }, [imageMode, coarse, fileCount]);
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
  const contextWarning =
    files.some((f) => f.document || f.kind === "audio") &&
    context &&
    estimatedInput > budget.available
      ? `This message and its attachments may exceed the input allowance (${budget.available.toLocaleString()} tokens after reserving ${budget.reserve.toLocaleString()} for the response and 256 for safety). Lower Max output tokens in Chat controls, choose a larger context or remove an attachment.`
      : undefined;
  const warned =
    !!contextWarning ||
    attachmentIssues(files, uploads, model, context?.reserve).some(
      (issue) => issue.kind === "warning",
    );
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
    if (!running && !disabled && !waiting && !warned && value.trim()) {
      const submitted = value;
      const version = revision.current;
      const pasteKey = pasted?.key;
      if (optimistic) setValue("");
      const accepted = await onSend?.(submitted);
      if (accepted !== false)
        uploads.filter((u) => u.failed).forEach((u) => onCancelUpload?.(u.id));
      if (accepted !== false && mounted.current)
        setPasted((old) => (old?.key === pasteKey ? undefined : old));
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
        {imageMode && (
          <input
            type="file"
            multiple
            hidden
            ref={fileInput}
            accept={fileAccept(
              attachmentExtensions,
              audioExtensions,
              transcriptionReady,
            )}
            onChange={(e) => {
              onAttach?.(Array.from(e.target.files ?? []));
              e.target.value = "";
            }}
          />
        )}
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
        {!imageMode && (showTray || hasFiles) && (
          <Suspense
            fallback={
              <div className="attachment-tray-loading" role="status">
                Preparing files…
              </div>
            }
          >
            <AttachmentTray
              fixtures={attachmentFixtures}
              files={files}
              uploads={uploads}
              local={attachmentLocal}
              model={model}
              reserve={context?.reserve}
              contextWarning={contextWarning}
              onRemove={onRemove}
              onCancel={onCancelUpload}
              onRetry={onRetryUpload}
              onPreviewLoaded={onPreviewLoaded}
              visionModels={visionModels}
              onChooseModel={onChooseModel}
            />
          </Suspense>
        )}
        {!imageMode && pasted && (
          <p className="composer-paste-note" role="status">
            Long paste attached as a file.{" "}
            <button type="button" disabled={disabled} onClick={keepPastedText}>
              Keep as text
            </button>
            {!value.trim() && <span> Add a message to send it.</span>}
          </p>
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
            const incoming = Array.from(event.clipboardData.files);
            if (incoming.length && onAttach) {
              event.preventDefault();
              setImageMode(false);
              onAttach(
                incoming.map((file) => {
                  if (
                    !file.type.startsWith("image/") &&
                    !/\.(png|jpe?g|gif|webp|avif|heic|heif)$/i.test(file.name)
                  )
                    return file;
                  const ext =
                    file.name.match(
                      /\.(png|jpe?g|gif|webp|avif|heic|heif)$/i,
                    )?.[1] ?? "png";
                  return new File(
                    [file],
                    `Pasted image ${++pasteSerial.current.image}.${ext}`,
                    { type: file.type, lastModified: file.lastModified },
                  );
                }),
              );
              return;
            }
            const text = event.clipboardData.getData("text/plain");
            if (
              imageMode ||
              text.length <= 4000 ||
              !onAttach ||
              !onDiscardPasted
            )
              return;
            event.preventDefault();
            const key = onAttach(
              [
                new File(
                  [text],
                  `Pasted text ${++pasteSerial.current.text}.txt`,
                  { type: "text/plain" },
                ),
              ],
              { characters: text.length },
            )?.[0];
            if (key)
              setPasted({
                key,
                text,
                before: value,
                start: event.currentTarget.selectionStart,
                end: event.currentTarget.selectionEnd,
              });
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
          rows={1}
        />
        <div className="composer-tool-row-main">
          {!imageMode && (
            <>
              <Tooltip>
                <TooltipTrigger asChild>
                  <span
                    className="composer-attach"
                    title={
                      fileCount >= 8
                        ? "8 files is the limit for one message"
                        : "Attach files · ⌘U"
                    }
                  >
                    <Button
                      type="button"
                      variant="outline"
                      aria-label="Attach files"
                      aria-hidden={coarse || undefined}
                      tabIndex={coarse ? -1 : 0}
                      disabled={fileCount >= 8}
                      onClick={() => {
                        if (!coarse) fileInput.current?.click();
                      }}
                    >
                      <Plus />
                    </Button>
                    <input
                      type="file"
                      multiple
                      ref={fileInput}
                      aria-label="Attach files"
                      className="composer-file-input"
                      disabled={fileCount >= 8}
                      accept={fileAccept(
                        attachmentExtensions,
                        audioExtensions,
                        transcriptionReady,
                      )}
                      onChange={(e) => {
                        onAttach?.(Array.from(e.target.files ?? []));
                        e.target.value = "";
                      }}
                    />
                  </span>
                </TooltipTrigger>
                <TooltipContent>
                  {fileCount >= 8
                    ? "8 files is the limit for one message"
                    : "Attach files · ⌘U"}
                </TooltipContent>
              </Tooltip>
              <ToolsMenu
                open={toolsOpen}
                onOpenChange={setToolsOpen}
                buttonRef={toolsButton}
                web={web}
                onWebChange={onWebChange}
                webBlocked={webBlocked}
                library={libraryControl}
                images={images}
                imageAvailable={imageAvailable}
                imageReason={imageStatus?.reason ?? undefined}
                onImage={() => {
                  setToolsOpen(false);
                  toggleImage();
                }}
                model={model}
                thinkValue={thinkValue}
                onThinkChange={onThinkChange}
              />
              <ToolChips
                web={web && !webBlocked}
                library={libraryControl}
                thinkValue={model?.reasoning ? thinkValue : undefined}
                onWebChange={onWebChange}
                onThinkChange={onThinkChange}
                openTools={() => setToolsOpen(true)}
                focusTools={() => toolsButton.current?.focus()}
              />
            </>
          )}
          {imageMode && (
            <Button
              type="button"
              variant="ghost"
              className="h-11 rounded-full gap-2 bg-brand-soft text-brand"
              aria-label="Leave image mode"
              aria-pressed
              onClick={toggleImage}
            >
              <ImageIcon className="size-4" />
              Image
              <X className="size-3" />
            </Button>
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
          <div className="composer-send-tools">
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
                      className="composer-context"
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
                  className="composer-send-wrap"
                  tabIndex={waiting ? 0 : undefined}
                >
                  {waiting && !imageMode && (
                    <svg
                      className="composer-send-ring"
                      data-indeterminate={indeterminate || undefined}
                      viewBox="0 0 48 48"
                      role="progressbar"
                      aria-label={`Waiting for ${waitingCount} ${waitingCount === 1 ? "file" : "files"}`}
                      aria-valuenow={indeterminate ? undefined : uploadProgress}
                      aria-valuemin={0}
                      aria-valuemax={100}
                    >
                      <circle
                        cx="24"
                        cy="24"
                        r="21"
                        pathLength="100"
                        strokeDasharray={`${indeterminate ? 24 : uploadProgress} 100`}
                      />
                    </svg>
                  )}
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
                        : disabled || waiting || warned || !value.trim())
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
                    ? `Waiting for ${waitingCount} ${waitingCount === 1 ? "file" : "files"}`
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
