import {
  lazy,
  Suspense,
  useEffect,
  useRef,
  useState,
  type RefObject,
} from "react";
import { Brain, ChevronDown, LoaderCircle, TriangleAlert } from "lucide-react";
import {
  Collapsible,
  CollapsibleTrigger,
  CollapsibleContent,
} from "@/components/ui/collapsible";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import type { Message, Source, WebRead, Model, Bootstrap } from "@/lib/api";
import { MessageActions } from "./MessageActions";
import { StatsLine } from "./StatsLine";
import { SearchActivity } from "./SearchActivity";
import { messageError } from "@/lib/errors";
import { SourcesSheet } from "./SourcesSheet";
const Markdown = lazy(() => import("./Markdown"));
function Thinking({
  text,
  live,
  duration,
}: {
  text: string;
  live: boolean;
  duration?: number | null;
}) {
  const [open, setOpen] = useState(live),
    [elapsed, setElapsed] = useState(0);
  const began = useRef(Date.now());
  useEffect(() => {
    setOpen(live);
    if (!live) return;
    const timer = setInterval(
      () => setElapsed(Math.floor((Date.now() - began.current) / 1000)),
      1000,
    );
    return () => clearInterval(timer);
  }, [live]);
  return (
    <Collapsible
      open={open}
      onOpenChange={setOpen}
      className="mb-4 rounded-lg border border-line"
    >
      <CollapsibleTrigger className="flex min-h-11 w-full items-center gap-2 px-3 text-sm text-fg-2">
        <Brain className="size-4" />
        {live
          ? `Thinking… ${elapsed}s`
          : `Thought for ${Math.round((duration ?? elapsed * 1000) / 1000)}s`}
        <ChevronDown className="ml-auto size-4" />
      </CollapsibleTrigger>
      <CollapsibleContent className="max-h-72 overflow-y-auto whitespace-pre-wrap px-4 pb-4 text-sm leading-6 text-fg-2">
        {text}
      </CollapsibleContent>
    </Collapsible>
  );
}
export function LiveThread({
  messages,
  all,
  stage,
  steps,
  scrollRef,
  onAboveBottomChange,
  onRegenerate,
  onEdit,
  onBranch,
  sources,
  reads,
  renderSources,
  models = [],
  connections = [],
  onSettings,
  onChatSettings,
  onNew,
  onRegenerateWith,
}: {
  onRegenerateWith?: (message: Message, model: Model) => void;
  models?: Model[];
  connections?: Bootstrap["connections"];
  onSettings?: (pane?: string) => void;
  onChatSettings?: () => void;
  onNew?: () => void;
  messages: Message[];
  all: Message[];
  stage?: string;
  steps?: { label: string; detail: string; status: string }[];
  scrollRef: RefObject<HTMLDivElement | null>;
  onAboveBottomChange: (above: boolean) => void;
  onRegenerate: (message: Message, force?: boolean) => void;
  onEdit: (message: Message, text: string) => Promise<boolean>;
  onBranch: (id: string) => void;
  sources?: Record<string, Source[]>;
  reads?: Record<string, WebRead[]>;
  renderSources?: (
    message: Message,
    sources: Source[],
    reads: WebRead[],
  ) => React.ReactNode;
}) {
  const [editing, setEditing] = useState<string | null>(null),
    [draft, setDraft] = useState("");
  const stick = useRef(true);
  useEffect(() => {
    const listener = () => {
      const last = [...messages].reverse().find((m) => m.role === "user");
      if (last) {
        setEditing(last.id);
        setDraft(last.content);
      }
    };
    window.addEventListener("workbench:edit-last", listener);
    return () => window.removeEventListener("workbench:edit-last", listener);
  }, [messages]);
  useEffect(() => {
    if (stick.current && scrollRef.current)
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [messages, steps, scrollRef]);
  return (
    <div
      ref={scrollRef}
      className="thread-scroll"
      data-testid="thread"
      role="log"
      aria-live="off"
      aria-label="Conversation"
      onScroll={() => {
        const e = scrollRef.current;
        if (e) {
          stick.current = e.scrollHeight - e.clientHeight - e.scrollTop < 80;
          onAboveBottomChange(!stick.current);
        }
      }}
    >
      <div className="thread-column">
        {messages.map((message) => (
          <article
            key={message.id}
            aria-label={`${message.role} message`}
            className="min-w-0 py-4"
            aria-busy={message.status === "streaming"}
          >
            {message.role === "user" ? (
              editing === message.id ? (
                <div>
                  <Textarea
                    aria-label="Edit message"
                    value={draft}
                    onChange={(e) => setDraft(e.target.value)}
                  />
                  <div className="mt-2 flex gap-2">
                    <Button variant="outline" onClick={() => setEditing(null)}>
                      Cancel
                    </Button>
                    <Button
                      disabled={!draft.trim()}
                      onClick={async () => {
                        if (await onEdit(message, draft)) setEditing(null);
                      }}
                    >
                      Save & submit
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="ml-auto w-fit max-w-full rounded-2xl border border-line bg-surface-2 px-4 py-3">
                  <p className="whitespace-pre-wrap break-words">
                    {message.content}
                  </p>
                  {(message.attachments ?? []).map((a) => (
                    <a
                      className="block text-xs text-brand"
                      key={a.id}
                      href={"/api/attachments/" + a.id}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      {a.filename}
                    </a>
                  ))}
                </div>
              )
            ) : (
              <>
                {message.stats?.dropped_message_count ? (
                  <p className="mb-4 border-b border-line pb-3 text-xs text-fg-3">
                    Earlier messages are outside the model's context window
                  </p>
                ) : null}
                <p className="mb-4 text-xs text-fg-3 break-all">
                  {message.model?.display_name}
                </p>
                {message.status === "streaming" &&
                  stage !== "search" &&
                  !message.content &&
                  !message.reasoning && (
                    <p
                      className="flex min-h-12 items-center gap-2 text-sm text-fg-2"
                      role="status"
                    >
                      <LoaderCircle className="size-4 animate-spin" />
                      {stage === "queued"
                        ? "Waiting in line…"
                        : stage === "loading-model"
                          ? "Loading model…"
                          : stage === "search"
                            ? "Searching the web…"
                            : "Waiting for first token…"}
                    </p>
                  )}
                <SearchActivity
                  message={message}
                  sources={sources?.[message.id] ?? []}
                  steps={message.status === "streaming" ? steps : undefined}
                  onRetry={() => onRegenerate(message, true)}
                />
                {message.reasoning && (
                  <Thinking
                    text={message.reasoning}
                    duration={message.stats?.reasoning_ms}
                    live={message.status === "streaming" && !message.content}
                  />
                )}
                <Suspense
                  fallback={
                    <p className="text-fg-2">Loading formatted answer…</p>
                  }
                >
                  <Markdown
                    text={message.content}
                    sources={sources?.[message.id]}
                    streaming={message.status === "streaming"}
                  />
                </Suspense>
                {message.error && (
                  <div
                    role="alert"
                    className="mt-4 rounded-lg border border-line p-4"
                  >
                    <p className="flex items-start gap-2 text-sm text-danger">
                      <TriangleAlert className="size-4 shrink-0" />
                      {messageError(message, models, connections)}
                    </p>
                    <div className="mt-3 flex flex-wrap gap-2">
                      {message.error.code !== "context_overflow" &&
                        message.error.code !== "model_not_found" && (
                          <Button
                            variant="outline"
                            onClick={() => onRegenerate(message)}
                          >
                            Retry
                          </Button>
                        )}
                      {message.error.code === "runtime_unreachable" && (
                        <Button
                          variant="outline"
                          onClick={() => onSettings?.("Connections")}
                        >
                          Open settings
                        </Button>
                      )}
                      {message.error.code === "model_not_found" && (
                        <Button
                          variant="outline"
                          onClick={() => onSettings?.("Models")}
                        >
                          Choose model
                        </Button>
                      )}
                      {message.error.code === "model_load_failed" && (
                        <Button
                          variant="outline"
                          onClick={() => onSettings?.("Models")}
                        >
                          Models
                        </Button>
                      )}
                      {message.error.code === "context_overflow" && (
                        <>
                          <Button variant="outline" onClick={onNew}>
                            Start new chat
                          </Button>
                          <Button variant="outline" onClick={onChatSettings}>
                            Chat settings
                          </Button>
                        </>
                      )}
                    </div>
                  </div>
                )}
                {!renderSources && message.web?.status === "used" && (
                  <>
                    <SourcesSheet
                      message={message}
                      sources={sources?.[message.id] ?? []}
                      reads={reads?.[message.id] ?? []}
                    />
                    {message.web.notice?.code === "uncited" && (
                      <p className="mb-3 text-xs text-fg-3">
                        This answer doesn't cite specific sources.
                      </p>
                    )}
                  </>
                )}
                {renderSources?.(
                  message,
                  sources?.[message.id] ?? [],
                  reads?.[message.id] ?? [],
                )}
                {message.status !== "streaming" && (
                  <StatsLine message={message} />
                )}
              </>
            )}
            {message.status !== "streaming" && (
              <MessageActions
                message={message}
                models={models}
                onRegenerateWith={(m) => onRegenerateWith?.(message, m)}
                messages={all}
                onEdit={() => {
                  setEditing(message.id);
                  setDraft(message.content);
                }}
                onRegenerate={() => onRegenerate(message)}
                onBranch={onBranch}
              />
            )}
          </article>
        ))}
      </div>
    </div>
  );
}
