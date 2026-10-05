import config from "../../../shared/config.json";
/** Synthetic data and event bindings for production components; no duplicate UI. */
import { useState, type RefObject } from "react";
import { MessageRow, LiveThread } from "@/components/chat/LiveThread";
import { LiveChatSettings } from "@/components/settings/LiveChatSettings";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { LiveSettingsPane, DataPane } from "@/components/settings/LiveSettings";
import { TranscriptionSettings } from "@/components/settings/TranscriptionSettings";
import { api, type Bootstrap } from "@/lib/api";
import type { Message, Model } from "@/lib/api";
import { fixtureAnswer } from "./fixtures";

export const fixtureModels: Model[] = [
  {
    connection_id: "design",
    model_id: "fake-chat",
    display_name: "fake-chat",
    loaded: true,
    chat_capable: true,
    embedding: false,
    hidden: false,
    vision: false,
    params_defaults: {},
    context_length: 16384,
    context_limit: 16384,
  },
  {
    connection_id: "design",
    model_id: "fake-reasoning",
    display_name: "fake-reasoning",
    loaded: false,
    chat_capable: true,
    embedding: false,
    hidden: false,
    vision: false,
    params_defaults: {},
    context_length: 16384,
    context_limit: 16384,
    reasoning: { options: ["off", "on"] },
  },
  {
    connection_id: "design",
    model_id: "fake-vision",
    display_name: "fake-vision",
    loaded: false,
    chat_capable: true,
    embedding: false,
    hidden: false,
    vision: true,
    params_defaults: {},
    context_length: 16384,
    context_limit: 16384,
  },
];
export type PreviewState =
  | "queued"
  | "loading-model"
  | "waiting"
  | "reasoning"
  | "streaming"
  | "complete"
  | "stopped"
  | "error"
  | "interrupted";
export function fixtureMessage(
  role: "user" | "assistant",
  state: PreviewState = "complete",
  text?: string,
): Message {
  const early = ["queued", "loading-model", "waiting", "reasoning"].includes(
    state,
  );
  return {
    id: `fake-${role}-${state}`,
    chat_id: "design",
    role,
    content: early
      ? ""
      : (text ??
        (role === "user"
          ? "Explain a useful way to learn something new."
          : fixtureAnswer)),
    status: ["queued", "loading-model", "waiting", "reasoning"].includes(state)
      ? "streaming"
      : state === "streaming"
        ? "streaming"
        : state === "complete"
          ? "complete"
          : state === "stopped"
            ? "stopped"
            : state === "interrupted"
              ? "interrupted"
              : "error",
    created_at: "2026-10-03T12:00:00Z",
    model:
      role === "assistant"
        ? {
            connection_id: "design",
            model_id: "fake-chat",
            display_name: "Fake runtime · fake-chat",
          }
        : undefined,
    reasoning:
      role === "assistant" && (state === "reasoning" || state === "complete")
        ? "Synthetic reasoning. Compare one small change with your starting point."
        : null,
    error:
      state === "error"
        ? {
            code: "runtime_unreachable",
            message: "Synthetic runtime unavailable",
          }
        : state === "interrupted"
          ? { code: "interrupted", message: "Synthetic interruption" }
          : null,
    attachments: [],
  };
}
export function MessagePreview({
  role = "assistant",
  state = "complete",
  text,
  editing = false,
  attachment = false,
}: {
  role?: "user" | "assistant";
  state?: PreviewState;
  text?: string;
  editing?: boolean;
  attachment?: boolean;
}) {
  const message = fixtureMessage(role, state, text);
  if (attachment)
    message.attachments = [
      {
        id: "fake-note",
        kind: "text",
        filename: "fake-notes.md",
        mime_type: "text/markdown",
        bytes: 64,
        audio_available: true,
      },
    ];
  const [edit, setEditing] = useState<string | null>(
    editing ? message.id : null,
  );
  const [draft, setDraft] = useState(message.content);
  return (
    <MessageRow
      message={message}
      all={[message]}
      stage={state}
      selectedModel={fixtureModels[0]}
      models={fixtureModels}
      editing={edit}
      draft={draft}
      setEditing={setEditing}
      setDraft={setDraft}
      onRegenerate={() => {}}
      onBranch={() => {}}
      onEdit={async () => true}
    />
  );
}
export function FixtureThread({
  message,
  scrollRef,
  onAboveBottomChange,
}: {
  message?: string;
  scrollRef: RefObject<HTMLDivElement | null>;
  onAboveBottomChange: (above: boolean) => void;
}) {
  const messages = [
    fixtureMessage("user", "complete", message),
    fixtureMessage("assistant"),
  ];
  return (
    <LiveThread
      messages={messages}
      all={messages}
      scrollRef={scrollRef}
      onAboveBottomChange={onAboveBottomChange}
      onRegenerate={() => {}}
      onBranch={() => {}}
      onEdit={async () => true}
      selectedModel={fixtureModels[0]}
      models={fixtureModels}
    />
  );
}
export function FixtureChatSettings({ drawer = false }: { drawer?: boolean }) {
  return (
    <LiveChatSettings
      drawer={drawer}
      model={fixtureModels[1]}
      onSave={() => {}}
      onDefaults={() => {}}
      onContext={() => {}}
    />
  );
}

const fixtureBootstrap: Bootstrap = {
  app_name: config.APP_NAME,
  version: "1.0.0-alpha.0",
  data_dir: "Synthetic preview · no saved data",
  settings: {
    "web.provider_order": ["searxng", "ddgs"],
    "web.max_sources": 6,
    "web.page_cache_days": 7,
  },
  connections: [
    {
      id: "design",
      kind: "ollama",
      name: "Fake runtime",
      base_url: "http://127.0.0.1:18080",
      enabled: true,
      max_concurrent: 1,
      keep_alive: "30m",
      has_api_key: false,
      reachable: true,
      model_count: 3,
      latency_ms: 20,
    },
  ],
  features: { web_search: true, transcription: true },
};
const fixtureRequest: typeof api = async <T,>(url: string): Promise<T> => {
  const value = url.startsWith("/models")
    ? fixtureModels
    : url === "/search/status"
      ? []
      : url === "/search/test"
        ? { ok: true, results: [], ms: 20 }
        : undefined;
  return value as T;
};
export function FixtureSettingsPane({ pane }: { pane: string }) {
  const [client] = useState(() => new QueryClient());
  if (pane === "Data") return <DataPane preview />;
  if (pane === "Transcription")
    return (
      <TranscriptionSettings
        bootstrap={fixtureBootstrap}
        fixture={{
          configured: true,
          ready: true,
          version: "fake-engine",
          glossary_terms: 0,
          audio_extensions: [".wav"],
          checks: [],
        }}
      />
    );
  return (
    <QueryClientProvider client={client}>
      <LiveSettingsPane
        pane={pane}
        bootstrap={fixtureBootstrap}
        models={fixtureModels}
        request={fixtureRequest}
        queryScope={["design"]}
        onModelAction={async () => {}}
      />
    </QueryClientProvider>
  );
}
