/** Synthetic event bindings to the production conversation components. */
import { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Composer } from "@/components/chat/Composer";
import { LiveThread } from "@/components/chat/LiveThread";
import { ModelPicker } from "@/components/app/ModelPicker";
import { ChatList } from "@/components/app/ChatList";
import { EmptyState } from "@/components/app/EmptyState";
import { useUI } from "@/stores/ui";
import { useFreshRows } from "@/stores/fresh";
import { fixtureMessage, fixtureModels } from "./ProductionFixtures";
import type { Chat, Message } from "@/lib/api";

export function ConversationMotionPreview() {
  const ui = useUI();
  const [rows, setRows] = useState<Message[]>([]);
  const [pending, setPending] = useState<Message | null>(null);
  const [stage, setStage] = useState("waiting");
  const [above, setAbove] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const [loaded, setLoaded] = useState(true);
  const [loadingModel, setLoadingModel] = useState<string | null>(null);
  const model = { ...fixtureModels[0], loaded };
  const [title, setTitle] = useState("Synthetic motion chat");
  const sample: Chat = {
    id: "conversation-motion-fake",
    title,
    title_source: "auto",
    pinned: false,
    params: {},
    web_enabled: false,
    library_enabled: false,
    research_enabled: false,
    created_at: "2026-10-04",
    updated_at: "2026-10-04",
  };
  const show = (
    state:
      | "waiting"
      | "reasoning"
      | "streaming"
      | "complete"
      | "search"
      | "optimistic",
  ) => {
    setPending(null);
    const user = fixtureMessage("user", "complete", "Synthetic motion request");
    const assistant = fixtureMessage(
      "assistant",
      state === "search" || state === "optimistic" ? "waiting" : state,
    );
    if (state === "complete")
      assistant.content =
        'Synthetic copy example.\n\n```python\nprint("fake")\n```';
    if (state === "optimistic") {
      setRows([]);
      setPending(user);
      useFreshRows.getState().add(user.id);
    } else {
      if (state === "search")
        assistant.web = {
          status: "used",
          source_count: 0,
          ranking: "keyword",
          plan_fallback: false,
        };
      useFreshRows.getState().add(assistant.id);
      setRows([user, assistant]);
    }
    setStage(state === "search" ? "search" : state);
  };
  return (
    <section className="design-card mb-8" aria-label="Conversation motion">
      <h2 className="mb-3 text-lg font-medium">
        Conversation motion · synthetic fixtures
      </h2>
      <div className="mb-4 flex flex-wrap gap-2">
        {(
          [
            "optimistic",
            "waiting",
            "reasoning",
            "streaming",
            "search",
            "complete",
          ] as const
        ).map((state) => (
          <Button key={state} variant="outline" onClick={() => show(state)}>
            Preview {state}
          </Button>
        ))}
        <Button
          variant="outline"
          onClick={() =>
            setTitle(
              title === "Synthetic motion chat"
                ? "Synthetic generated title"
                : "Synthetic motion chat",
            )
          }
        >
          Preview title change
        </Button>
      </div>
      <ChatList
        chats={[sample]}
        activeChats={[sample.id]}
        selected={sample.id}
        search=""
        menu={() => null}
        onOpen={() => {}}
        hasNext={false}
        onNext={() => {}}
      />
      <ModelPicker
        models={[model]}
        current={model}
        loadingModel={loadingModel}
        onModelAction={async () => {
          if (loaded) setLoaded(false);
          else {
            setLoadingModel(model.connection_id + model.model_id);
            await new Promise((resolve) => setTimeout(resolve, 500));
            setLoaded(true);
            setLoadingModel(null);
          }
        }}
      />
      <div className="relative flex h-96 flex-col overflow-hidden rounded-lg border border-line">
        <LiveThread
          messages={rows}
          all={rows}
          pending={pending}
          stage={stage}
          selectedModel={model}
          models={fixtureModels}
          scrollRef={scrollRef}
          onAboveBottomChange={setAbove}
          onRegenerate={() => show("streaming")}
          onEdit={async () => {
            show("complete");
            return true;
          }}
          onBranch={() => {}}
          steps={
            stage === "search"
              ? [
                  { label: "plan", detail: "Synthetic query", status: "ok" },
                  {
                    label: "read",
                    detail: "https://example.org/fake",
                    status: "ok",
                  },
                ]
              : undefined
          }
        />
        <Button
          data-slot="scroll-bottom"
          data-state={above ? "visible" : "hidden"}
          inert={!above}
          tabIndex={above ? 0 : -1}
          aria-hidden={!above}
          aria-label="Preview scroll to bottom"
          onClick={() =>
            scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight })
          }
        >
          ↓
        </Button>
      </div>
      <Composer
        optimistic
        model={model}
        context={{ used_tokens: 128, context_length: 16384 }}
        onSend={async (text) => {
          const user = fixtureMessage("user", "complete", text);
          useFreshRows.getState().add(user.id);
          setPending(user);
          await new Promise((resolve) => setTimeout(resolve, 500));
          show("streaming");
          return true;
        }}
      />
      <EmptyState ui={ui} composer={<Composer model={model} suggestions />} />
    </section>
  );
}
