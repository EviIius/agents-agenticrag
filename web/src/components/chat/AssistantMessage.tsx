import { lazy, Suspense } from "react";
import {
  Copy,
  RotateCcw,
  Info,
  ChevronLeft,
  ChevronRight,
  TriangleAlert,
  LoaderCircle,
} from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { IconButton } from "@/components/app/IconButton";
import { ReasoningBlock } from "./ReasoningBlock";
import { fixtureAnswer } from "@/design/fixtures";
const Markdown = lazy(() => import("./Markdown"));
export type AssistantState =
  | "queued"
  | "loading-model"
  | "waiting"
  | "reasoning"
  | "streaming"
  | "complete"
  | "stopped"
  | "error"
  | "interrupted";
export function AssistantMessage({
  state = "complete",
  text = fixtureAnswer,
}: {
  state?: AssistantState;
  text?: string;
}) {
  const early = ["queued", "loading-model", "waiting"].includes(state);
  const failed = state === "error" || state === "interrupted";
  return (
    <article
      aria-busy={state === "streaming" || state === "reasoning"}
      aria-label={`Assistant message: ${state}`}
      className="min-w-0 py-4"
    >
      <h2 className="sr-only">Fake runtime replied</h2>
      <div className="mb-4 flex items-center gap-2 text-xs text-fg-3">
        <span className="size-2 rounded-full bg-brand" />
        Fake runtime · fake-chat · {state}
      </div>
      {early ? (
        <p className="flex min-h-12 items-center gap-2 text-fg-2" role="status">
          {state === "queued" ? (
            "Waiting for fake-chat… (#2 in line)"
          ) : state === "loading-model" ? (
            <>
              <LoaderCircle className="size-4 animate-spin" />
              Loading fake-chat… 8 s
            </>
          ) : (
            <span
              className="animate-pulse"
              aria-label="Waiting for first token"
            >
              ● ● ●
            </span>
          )}
        </p>
      ) : (
        <>
          {(state === "reasoning" || state === "complete") && (
            <ReasoningBlock live={state === "reasoning"} />
          )}
          {state !== "reasoning" && (
            <Suspense
              fallback={
                <div
                  className="skeleton h-24"
                  aria-label="Loading formatted answer"
                />
              }
            >
              <Markdown text={text} streaming={state === "streaming"} />
            </Suspense>
          )}
          {state === "streaming" && (
            <span aria-hidden className="animate-pulse text-fg-3">
              ▍
            </span>
          )}
          {failed && (
            <div
              className="mt-4 rounded-lg border border-line p-4"
              role="alert"
            >
              <p className="flex gap-2 text-danger">
                <TriangleAlert className="size-4 shrink-0" />
                {state === "interrupted"
                  ? "The connection was interrupted. Your partial answer is kept."
                  : "Couldn’t reach the model. Check the connection and try again."}
              </p>
              <Button
                variant="outline"
                className="mt-3"
                onClick={() => toast("Fake runtime · retry preview")}
              >
                Retry
              </Button>
            </div>
          )}
          {!["streaming", "reasoning"].includes(state) && (
            <footer className="mt-5 flex flex-wrap items-center justify-between gap-2">
              <div className="flex items-center">
                <IconButton
                  label="Copy answer"
                  onClick={() => {
                    void navigator.clipboard
                      .writeText(text)
                      .then(() => toast("Copied"));
                  }}
                >
                  <Copy />
                </IconButton>
                <IconButton
                  label="Regenerate answer"
                  onClick={() => toast("Fake runtime · regenerate preview")}
                >
                  <RotateCcw />
                </IconButton>
                <IconButton
                  label="Previous branch"
                  onClick={() => toast("Fake runtime · branch preview")}
                >
                  <ChevronLeft />
                </IconButton>
                <span className="meta">1 / 2</span>
                <IconButton
                  label="Next branch"
                  onClick={() => toast("Fake runtime · branch preview")}
                >
                  <ChevronRight />
                </IconButton>
                <Popover>
                  <PopoverTrigger asChild>
                    <IconButton label="Message info">
                      <Info />
                    </IconButton>
                  </PopoverTrigger>
                  <PopoverContent className="text-sm">
                    <p className="font-medium">
                      Fake runtime · fixture statistics
                    </p>
                    <dl className="mt-3 space-y-2">
                      <div>
                        <dt>Parameters sent</dt>
                        <dd>Model defaults</dd>
                      </div>
                      <div>
                        <dt>Tokens</dt>
                        <dd>512 · 61.2 tok/s</dd>
                      </div>
                      <div>
                        <dt>Time to first token</dt>
                        <dd>0.8 seconds</dd>
                      </div>
                    </dl>
                  </PopoverContent>
                </Popover>
              </div>
              <p className="meta">
                61.2 tok/s · 512 tokens · 0.8 s
                {state === "stopped" ? " · Stopped" : ""}
              </p>
            </footer>
          )}
        </>
      )}
    </article>
  );
}
