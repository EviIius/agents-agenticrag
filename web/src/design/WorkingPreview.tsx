import { useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { LiveThread } from "@/components/chat/LiveThread";
import { useUI } from "@/stores/ui";
import { fixtureMessage, fixtureModels } from "./ProductionFixtures";

const states = [
  "Waiting",
  "Queued",
  "Loading",
  "Web search",
  "Reading pages",
  "Unreadable pages",
  "Library search",
  "Thinking",
  "Long thinking",
  "Answer",
  "Complete",
  "Stopped",
  "Error",
] as const;
type State = (typeof states)[number];
const initialThought = Array.from(
  { length: 40 },
  (_, i) =>
    `Synthetic reasoning line ${i + 1}: preserve the source and inspect the context.`,
).join("\n");
export default function WorkingPreview() {
  const ui = useUI(),
    scrollRef = useRef<HTMLDivElement>(null);
  const [state, setState] = useState<State>("Waiting"),
    [began, setBegan] = useState(Date.now),
    [thought, setThought] = useState(initialThought);
  const message = fixtureMessage("assistant", "waiting");
  message.id = "synthetic-working-indicator";
  message.created_at = new Date(began).toISOString();
  if (["Thinking", "Long thinking", "Answer", "Complete"].includes(state))
    message.reasoning = thought;
  if (state === "Long thinking") {
    message.created_at = new Date(began - 61000).toISOString();
    message.stats = {
      ttft_ms: 0,
      total_ms: 0,
      completion_tokens: 0,
      tokens_per_sec: 0,
      tokens_estimated: true,
      finish_reason: "stop",
      context_length: 16384,
      dropped_message_count: 0,
    };
  }
  if (["Answer", "Complete"].includes(state)) {
    message.content = "A synthetic answer, using the existing streaming row.";
    message.stats = {
      reasoning_ms: 12000,
      total_ms: 14000,
      completion_tokens: 12,
      tokens_per_sec: 6,
      tokens_estimated: true,
      finish_reason: "stop",
      context_length: 16384,
      dropped_message_count: 0,
    };
  }
  if (["Complete", "Stopped", "Error"].includes(state))
    message.status =
      state === "Complete"
        ? "complete"
        : state === "Stopped"
          ? "stopped"
          : "error";
  if (state === "Error")
    message.error = {
      code: "provider_error",
      message: "Synthetic runtime error",
    };
  if (state === "Library search")
    message.library = {
      status: "used",
      source_count: 0,
    } as typeof message.library;
  const stage =
    state === "Queued"
      ? "queued"
      : state === "Loading"
        ? "loading-model"
        : [
              "Web search",
              "Reading pages",
              "Unreadable pages",
              "Library search",
            ].includes(state)
          ? "search"
          : "waiting";
  const steps =
    state === "Reading pages"
      ? [1, 2, 3, 4].map((n) => ({
          label: "reading",
          detail: `https://example.org/page-${n}`,
          status: "ok",
        }))
      : state === "Unreadable pages"
        ? [
            {
              label: "reading",
              detail: "https://example.org/unreadable",
              status: "ok",
            },
            {
              label: "read",
              detail: "https://example.org/unreadable",
              status: "failed",
            },
          ]
        : [];
  return (
    <main className="design-page">
      <h1 className="font-serif text-3xl">Working indicator</h1>
      <p className="my-4 text-fg-2">
        Synthetic states, rendered by the production chat components. No model
        requests.
      </p>
      <div className="mb-4 flex flex-wrap gap-2">
        {states.map((value) => (
          <Button
            key={value}
            variant={state === value ? "default" : "outline"}
            onClick={() => {
              setState(value);
              setBegan(Date.now());
            }}
          >
            Preview {value}
          </Button>
        ))}
        <Button
          variant="outline"
          onClick={() =>
            setThought(
              (text) =>
                text +
                "\nNewest synthetic reasoning: compare the original evidence and preserve its wording.",
            )
          }
        >
          Append thought
        </Button>
        <Button
          variant="outline"
          onClick={() => {
            setThought(initialThought);
            setBegan(Date.now());
          }}
        >
          Restart clock
        </Button>
      </div>
      <div
        className="mb-4 flex flex-wrap gap-2"
        aria-label="Preview preferences"
      >
        <Button
          variant="outline"
          onClick={() =>
            ui.set({ theme: ui.theme === "dark" ? "light" : "dark" })
          }
        >
          Toggle theme
        </Button>
        <Button
          variant="outline"
          aria-pressed={ui.statusWords === "plain"}
          onClick={() =>
            ui.set({
              statusWords: ui.statusWords === "plain" ? "playful" : "plain",
            })
          }
        >
          Plain status
        </Button>
        <Button
          variant="outline"
          aria-pressed={ui.reduceMotion === "always"}
          onClick={() =>
            ui.set({
              reduceMotion: ui.reduceMotion === "always" ? "system" : "always",
            })
          }
        >
          Reduce motion
        </Button>
      </div>
      <div className="relative flex h-96 flex-col overflow-hidden rounded-lg border border-line">
        <LiveThread
          messages={[message]}
          all={[message]}
          models={fixtureModels}
          selectedModel={fixtureModels[0]}
          stage={stage}
          position={2}
          steps={steps}
          scrollRef={scrollRef}
          onAboveBottomChange={() => {}}
          onRegenerate={() => {}}
          onStop={() => setState("Stopped")}
          onEdit={async () => true}
          onBranch={() => {}}
        />
      </div>
    </main>
  );
}
