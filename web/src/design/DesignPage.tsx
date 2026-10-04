import { ConversationMotionPreview } from "./ConversationMotionPreview";
import { MotionPreview } from "./MotionPreview";
import { PolishPreview } from "./PolishPreview";
import { TranscriptionPreview } from "./TranscriptionPreview";
import { lazy, Suspense, useState } from "react";
import { Link } from "react-router";
import { toast } from "sonner";
import { ChatActionDialog } from "@/components/app/ChatActionDialog";
import { ChatList } from "@/components/app/ChatList";
import { LiveChatSettings } from "@/components/settings/LiveChatSettings";
import { Button } from "@/components/ui/button";
import {
  MessagePreview,
  FixtureChatSettings,
  fixtureModels,
  type PreviewState,
} from "./ProductionFixtures";
import { Composer } from "@/components/chat/Composer";
import { Welcome } from "@/components/app/Welcome";
import { Sidebar, type SidebarState } from "@/components/app/Sidebar";
import { ModelPicker, type PickerState } from "@/components/app/ModelPicker";
import { SearchActivity } from "@/components/chat/SearchActivity";
import { SourcesSheet } from "@/components/chat/SourcesSheet";
import type { Source, Message, Chat, Model } from "@/lib/api";
import { errorCopy } from "@/lib/errors";
import { useUI } from "@/stores/ui";
import { DataPane } from "@/components/settings/LiveSettings";
import { OllamaSearchKey } from "@/components/settings/OllamaSearchKey";
const webSource: Source = {
  n: 1,
  url: "https://example.org",
  title: "Synthetic design source",
  site_name: "Example",
  domain: "example.org",
  published_at: "2026-10-01",
  fetched_at: "2026-10-01",
  kind: "page",
  cited: true,
  passages: [
    {
      source_url: "https://example.org",
      heading: "Example",
      ord: 0,
      selection_applied: false,
      text: "This is a synthetic source passage used to review the interface. It is not real research.",
    },
  ],
};
const webMessage: Message = {
  id: "design-web",
  chat_id: "design",
  role: "assistant",
  content: "A sample cited claim [1].",
  status: "complete",
  created_at: "2026-10-01",
  web: {
    status: "used",
    queries: ["Synthetic design query"],
    providers: ["Fake search provider"],
    timings: { plan: 150, search: 400, fetch: 500, rank: 10 },
    source_count: 1,
    plan_fallback: false,
    ranking: "keyword",
  },
};
const Markdown = lazy(() => import("@/components/chat/Markdown"));
export function DesignPage() {
  const ui = useUI();
  return (
    <div className="design-page">
      <header className="mb-10">
        <p className="mb-3 text-xs text-fg-3">WORKBENCH / FOUNDATION</p>
        <h1 className="font-serif text-3xl leading-10">
          A quieter place to think.
        </h1>
        <p className="mt-3 max-w-xl text-fg-2">
          The living component guide. Every answer and statistic here is a Fake
          runtime fixture. Switch themes to review the same states.
        </p>
        <div className="mt-5 flex flex-wrap gap-2">
          <Button
            variant={ui.theme === "light" ? "default" : "outline"}
            onClick={() => ui.set({ theme: "light" })}
          >
            Light
          </Button>
          <Button
            variant={ui.theme === "dark" ? "default" : "outline"}
            onClick={() => ui.set({ theme: "dark" })}
          >
            Dark
          </Button>
          <Button variant="outline" onClick={() => ui.set({ theme: "system" })}>
            System
          </Button>
          <Button asChild variant="outline">
            <Link to="/design/chat/fixture">Fixture chat</Link>
          </Button>
          <Button variant="outline" onClick={() => ui.set({ settings: true })}>
            Appearance
          </Button>
        </div>
      </header>
      <section className="design-card mb-8" aria-label="First run states">
        <h2 className="mb-5 text-lg font-medium">
          First run · synthetic runtime detection
        </h2>
        {[
          undefined,
          [],
          [
            {
              kind: "ollama" as const,
              base_url: "http://127.0.0.1:18080",
              reachable: true,
              model_count: 3,
            },
          ],
        ].map((detections, index) => (
          <Welcome
            key={index}
            detections={detections}
            onAdd={() => {}}
            onRetry={() => {}}
            onSettings={() => {}}
          />
        ))}
      </section>
      <section className="design-card mb-8" aria-label="Web search states">
        <h2 className="mb-5 text-lg font-medium">
          Web search · synthetic fixtures
        </h2>
        {[false, true].map((hasKey) => (
          <div
            key={String(hasKey)}
            className="mb-6 rounded-lg border border-line p-4"
          >
            <h3>
              Ollama Search · {hasKey ? "saved key" : "setup needed"} ·
              synthetic preview
            </h3>
            <OllamaSearchKey
              hasKey={hasKey}
              onSave={async () => true}
              onRemove={async () => true}
            />
          </div>
        ))}
        <SearchActivity
          message={webMessage}
          sources={[webSource]}
          onRetry={() => {}}
        />
        <Suspense fallback={<p>Loading preview…</p>}>
          <Markdown text={webMessage.content} sources={[webSource]} />
        </Suspense>
        <SourcesSheet
          message={webMessage}
          sources={[webSource]}
          reads={[
            {
              url: "https://example.net",
              title: "Synthetic failed page",
              status: "failed",
              reason: "HTTP 403",
            },
          ]}
        />
        {["search_failed", "search_no_results", "pages_unreadable"].map(
          (code) => (
            <SearchActivity
              key={code}
              message={{
                ...webMessage,
                web: {
                  ...webMessage.web!,
                  status: "failed",
                  notice: { code, message: "Synthetic test failure" },
                },
              }}
              sources={[]}
              onRetry={() => {}}
            />
          ),
        )}
        <SearchActivity
          message={{
            ...webMessage,
            web: { ...webMessage.web!, status: "skipped" },
          }}
          sources={[]}
          onRetry={() => {}}
        />
        <SearchActivity
          message={{ ...webMessage, status: "streaming" }}
          sources={[webSource]}
          steps={[
            { label: "reading", detail: "https://example.org", status: "ok" },
          ]}
          onRetry={() => {}}
        />
        <p className="text-xs text-fg-3">
          This answer doesn't cite specific sources.
        </p>
      </section>
      <section className="design-card mb-8" aria-label="Runtime error copy">
        <h2 className="mb-5 text-lg font-medium">
          Runtime errors · synthetic fixtures
        </h2>
        {[
          "runtime_unreachable",
          "model_not_found",
          "model_load_failed",
          "context_overflow",
          "idle_timeout",
          "provider_error",
          "interrupted",
        ].map((code) => (
          <p
            key={code}
            className="mb-3 rounded-lg border border-line p-3 text-sm text-danger"
          >
            {errorCopy(code, "Synthetic runtime error")}
          </p>
        ))}
      </section>
      <section aria-labelledby="typography" className="design-card mb-8">
        <h2 id="typography" className="mb-5 text-lg font-medium">
          Typography & surfaces
        </h2>
        <p className="font-serif text-2xl leading-8">
          Space for the answer to breathe.
        </p>
        <p className="mt-3 text-fg-2">
          Geist for controls. Newsreader for answers. Geist Mono for code.
        </p>
        <p className="meta mt-2">Metadata · 12 / 16 · tabular numbers</p>
        <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
          {Object.entries({
            bg: "bg-bg",
            surface: "bg-surface",
            "surface-2": "bg-surface-2",
            "surface-3": "bg-surface-3",
          }).map(([surface, surfaceClass]) => (
            <div
              key={surface}
              className={`rounded-md border border-line p-4 ${surfaceClass}`}
            >
              <span className="text-fg">{surface}</span>
            </div>
          ))}
        </div>
        <div className="mt-5 flex flex-wrap gap-3">
          <Button>Primary</Button>
          <Button variant="outline">Secondary</Button>
          <Button variant="ghost">Ghost</Button>
          <Button disabled>Disabled</Button>
        </div>
      </section>
      <section className="design-card mb-8" aria-label="Data controls preview">
        <h2 className="mb-5 text-lg font-medium">
          Data controls · safe preview
        </h2>
        <DataPane preview />
      </section>
      <MotionPreview />
      <ConversationMotionPreview />
      <PolishPreview />
      <TranscriptionPreview />
      <ReviewStates />
      <section aria-labelledby="models" className="mb-8">
        <h2 id="models" className="mb-4 text-lg font-medium">
          Model picker
        </h2>
        <div className="grid gap-4 sm:grid-cols-2">
          {(
            [
              "ready",
              "loading",
              "offline",
              "empty",
              "loading-model",
            ] as PickerState[]
          ).map((state) => (
            <div className="design-card" key={state}>
              <h3 className="mb-3 font-medium">{state}</h3>
              <ModelPicker
                state={state}
                models={
                  state === "offline" || state === "empty"
                    ? undefined
                    : fixtureModels
                }
                current={fixtureModels[0]}
              />
            </div>
          ))}
        </div>
      </section>
      <section aria-labelledby="sidebar-states" className="mb-8">
        <h2 id="sidebar-states" className="mb-4 text-lg font-medium">
          Sidebar states
        </h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {(
            ["ready", "loading", "empty", "search", "error"] as SidebarState[]
          ).map((state) => (
            <div
              className="overflow-hidden rounded-lg border border-line"
              key={state}
            >
              <h3 className="bg-surface px-4 py-3 font-medium">{state}</h3>
              <div className="h-80">
                <Sidebar state={state} />
              </div>
            </div>
          ))}
          <div className="overflow-hidden rounded-lg border border-line">
            <h3 className="bg-surface px-4 py-3 font-medium">Collapsed rail</h3>
            <div className="h-80 w-14">
              <Sidebar collapsed />
            </div>
          </div>
        </div>
      </section>
      <section aria-labelledby="messages" className="mb-8">
        <h2 id="messages" className="mb-4 text-lg font-medium">
          Messages
        </h2>
        <div className="design-card mb-4">
          <h3 className="mb-5 font-medium">User · text, attachment, edit</h3>
          <MessagePreview role="user" />
          <MessagePreview role="user" attachment />
          <MessagePreview role="user" editing />
        </div>
        <div className="design-card mb-4">
          <h3 className="mb-5 font-medium">Assistant · complete</h3>
          <MessagePreview />
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          {(
            [
              "queued",
              "loading-model",
              "waiting",
              "reasoning",
              "streaming",
              "stopped",
              "error",
              "interrupted",
            ] as PreviewState[]
          ).map((state) => (
            <div className="design-card" key={state}>
              <h3 className="mb-3 font-medium">{state}</h3>
              <MessagePreview
                state={state}
                text="A partial answer from the Fake runtime. **Formatting stays readable** while the rest arrives."
              />
            </div>
          ))}
        </div>
      </section>
      <section aria-labelledby="composer-states" className="mb-8">
        <h2 id="composer-states" className="mb-4 text-lg font-medium">
          Composer
        </h2>
        <div className="space-y-4">
          <Composer
            model={fixtureModels[0]}
            context={{ used_tokens: 6200, context_length: 16384 }}
            suggestions
            onWebChange={() => {}}
          />
          <Composer
            model={fixtureModels[1]}
            starter="An editable fixture message"
            files={[
              {
                id: "fake-note",
                kind: "text",
                filename: "fake-notes.md",
                mime_type: "text/markdown",
                bytes: 64,
                audio_available: true,
              },
            ]}
          />
          <Composer
            model={fixtureModels[0]}
            starter="A fixture message in progress"
            running
          />
        </div>
      </section>
      <section aria-labelledby="chat-settings" className="design-card mb-8">
        <h2 id="chat-settings" className="text-lg font-medium">
          Chat settings · model defaults
        </h2>
        <div className="max-w-sm">
          <FixtureChatSettings />
        </div>
      </section>
      <section aria-labelledby="markdown-safety" className="design-card mb-8">
        <h2 id="markdown-safety" className="mb-4 text-lg font-medium">
          Markdown safety
        </h2>
        <Suspense fallback={<p>Loading example…</p>}>
          <Markdown
            text={
              '[Unsafe link](javascript:alert(1))\n\n![Remote example](https://example.invalid/picture.jpg)\n\n<div data-untrusted="true">Raw HTML fixture</div>'
            }
          />
        </Suspense>
        <p className="mt-4 text-fg-2">
          Remote images appear as links. Raw HTML and unsafe links are disabled.
        </p>
      </section>
      <section aria-labelledby="screens" className="design-card">
        <h2 id="screens" className="mb-4 text-lg font-medium">
          Screen previews
        </h2>
        <div className="flex flex-wrap gap-3">
          <Button asChild variant="outline">
            <Link to="/">New chat</Link>
          </Button>
          <Button asChild variant="outline">
            <Link to="/design/chat/fixture">Completed chat</Link>
          </Button>
          <Button variant="outline" onClick={() => ui.set({ settings: true })}>
            Settings dialog
          </Button>
          <Button variant="outline" onClick={() => ui.set({ command: true })}>
            Chat search
          </Button>
        </div>
        <p className="mt-5 text-fg-2">
          Component fixtures are synthetic. Open New chat to use your configured
          Ollama connection and web search. This guide does not read your chats
          or perform searches.
        </p>
      </section>
    </div>
  );
}

const reviewChat: Chat = {
  id: "design-export",
  title_source: "user",
  title: "Perfect Thanksgiving Feast",
  created_at: "2026-10-02",
  updated_at: "2026-10-02",
  pinned: true,
  params: {},
  web_enabled: false,
};
const reviewModel: Model = {
  connection_id: "design",
  model_id: "fixture-16k",
  display_name: "Fixture model",
  context_limit: 16384,
  context_max: 131072,
  context_length: 16384,
  loaded: false,
  vision: false,
  tools: false,
  embedding: false,
  hidden: false,
  chat_capable: true,
  params_defaults: {},
  reasoning: { options: ["off", "on"] },
};
function ReviewStates() {
  const [kind, setKind] = useState<"export-md" | "export-json" | null>(null);
  const [reviewModels, setReviewModels] = useState<Model[]>([
    reviewModel,
    {
      ...reviewModel,
      model_id: "fixture-32k",
      display_name: "Fixture model · 32K",
      context_limit: 32768,
      context_length: 32768,
    },
  ]);
  const [chosen, setChosen] = useState(reviewModel.model_id);
  const selected = reviewModels.find((model) => model.model_id === chosen)!;
  const selectFixture = (model: Model) => {
    setChosen(model.model_id);
    setReviewModels((previous) =>
      previous.map((item) =>
        item.model_id === model.model_id ? { ...item, loaded: true } : item,
      ),
    );
  };
  return (
    <section
      className="design-card mb-8"
      aria-label="Reviewed actions and constraints"
    >
      <h2 className="mb-4 text-lg font-medium">
        Actions, notifications and configured limits
      </h2>
      <ChatList
        chats={[reviewChat]}
        search=""
        menu={() => null}
        onOpen={() => {}}
        hasNext={false}
        onNext={() => {}}
      />
      <div className="mt-4 flex flex-wrap gap-2">
        <Button variant="outline" onClick={() => setKind("export-md")}>
          Preview Markdown export
        </Button>
        <Button variant="outline" onClick={() => setKind("export-json")}>
          Preview JSON export
        </Button>
        <Button
          variant="outline"
          onClick={() =>
            toast.success("Chat pinned", { description: reviewChat.title })
          }
        >
          Pinned notification
        </Button>
        <Button
          variant="outline"
          onClick={() =>
            toast.loading("Loading fixture model…", { duration: 4500 })
          }
        >
          Loading notification
        </Button>
        <Button
          variant="outline"
          onClick={() =>
            toast.error("Couldn’t load fixture model", {
              description: "Synthetic runtime connection error.",
            })
          }
        >
          Error notification
        </Button>
      </div>
      <ChatActionDialog
        preview
        action={kind ? { chat: reviewChat, kind } : null}
        onClose={() => setKind(null)}
        onApply={() => setKind(null)}
      />
      <div className="mt-4 max-w-lg">
        <ModelPicker
          models={reviewModels}
          current={selected}
          onChoose={selectFixture}
          onModelAction={async (model) => {
            if (model.loaded)
              setReviewModels((previous) =>
                previous.map((item) =>
                  item.model_id === model.model_id
                    ? { ...item, loaded: false }
                    : item,
                ),
              );
            else selectFixture(model);
          }}
        />
        <LiveChatSettings
          key={selected.model_id}
          drawer
          model={selected}
          onSave={() => toast("Preview settings saved")}
          onDefaults={() => toast("Preview defaults saved")}
          onContext={() => {}}
        />
      </div>
    </section>
  );
}
