import { useSend, useSendState } from "@/hooks/useSend";
import { useUploads } from "@/hooks/useUploads";
import { useModelOps } from "@/hooks/useModelOps";
import { useShortcuts } from "@/hooks/useShortcuts";
import { ChatMenu } from "./ChatMenu";
import { HistoryList } from "./HistoryList";
import { EmptyState } from "./EmptyState";
import { Panels } from "./Panels";
import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router";
import {
  useQuery,
  useQueryClient,
  useInfiniteQuery,
  keepPreviousData,
} from "@tanstack/react-query";
import { ArrowDown, PanelLeftOpen, SlidersHorizontal } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { CommandPalette } from "./CommandPalette";
import { resolvedTheme } from "@/lib/theme";
import { ChatActionDialog } from "./ChatActionDialog";
import { ModelPicker } from "./ModelPicker";
import { Welcome } from "./Welcome";
import { Sidebar } from "./Sidebar";
import { IconButton } from "./IconButton";
import { Composer } from "@/components/chat/Composer";
import { LiveThread } from "@/components/chat/LiveThread";
import { SettingsDialog } from "@/components/settings/SettingsDialog";
import { LiveSettingsPane } from "@/components/settings/LiveSettings";
import { LiveChatSettings } from "@/components/settings/LiveChatSettings";
import { useUI } from "@/stores/ui";
import { useRuns } from "@/stores/runs";
import { useMediaQuery } from "@/hooks/useMediaQuery";
import {
  api,
  type Bootstrap,
  type Chat,
  type Detail,
  type Model,
  type Params,
} from "@/lib/api";
import type { components } from "@/lib/api-types";
import { detachTranscription, attachRun } from "@/lib/sse";
import { latestLeaf, visiblePath } from "@/lib/tree";
import { useTranscripts } from "@/stores/transcripts";
import { usePreferenceSync } from "@/hooks/usePreferenceSync";
export function LiveAppShell() {
  const ui = useUI(),
    navigate = useNavigate(),
    { chatId } = useParams();
  const query = useQueryClient();
  const sendState = useSendState(chatId);
  const { busy, pending, sendError } = sendState;
  const desktop = useMediaQuery("(min-width:1024px)"),
    wide = useMediaQuery("(min-width:1280px)"),
    phone = useMediaQuery("(max-width:639px)");
  const [selected, setSelected] = useState<Model>(),
    [web, setWeb] = useState(false),
    [draftParams, setDraftParams] = useState<Params>({}),
    [search, setSearch] = useState(""),
    [debounced, setDebounced] = useState(""),
    [above, setAbove] = useState(false);
  const { modelOperation, loadingModel, operateModel, changeModel } =
    useModelOps({ query, chatId, setSelected });
  const [draftPrompt, setDraftPrompt] = useState<string | null>(null);
  const [action, setAction] = useState<{
    chat: Chat;
    kind: "rename" | "delete" | "export-md" | "export-json";
  } | null>(null);
  const scroll = useRef<HTMLDivElement>(null);
  const previousChat = useRef(chatId);
  const bootstrap = useQuery({
    queryKey: ["bootstrap"],
    queryFn: () => api<Bootstrap>("/bootstrap"),
    refetchInterval: () => (document.hidden ? false : 30000),
  });
  usePreferenceSync(bootstrap.data?.settings);
  const models = useQuery({
    queryKey: ["models"],
    queryFn: () => api<Model[]>("/models"),
    enabled: !!bootstrap.data?.connections.length,
    refetchInterval: () => (document.hidden ? false : 30000),
  });
  useEffect(() => {
    if (
      !bootstrap.data ||
      (bootstrap.data.connections.length && models.isPending)
    )
      return;
    if (performance.getEntriesByName("workbench:interactive").length) return;
    performance.mark("workbench:interactive");
    performance.measure("workbench:time-to-interactive", {
      start: 0,
      end: performance.now(),
    });
  }, [bootstrap.data, models.isPending]);
  const detail = useQuery({
    queryKey: ["chat", chatId],
    queryFn: () => api<Detail>("/chats/" + chatId),
    enabled: !!chatId,
  });
  const history = useInfiniteQuery({
    queryKey: ["chats", debounced],
    initialPageParam: "",
    placeholderData: keepPreviousData,
    queryFn: ({ pageParam }) =>
      api<components["schemas"]["ChatList"]>(
        "/chats?q=" +
          encodeURIComponent(debounced) +
          (pageParam ? "&cursor=" + encodeURIComponent(pageParam) : ""),
      ),
    getNextPageParam: (last) => last.next_cursor ?? undefined,
  });
  const historyItems = history.data?.pages.flatMap((page) => page.items) ?? [];
  const detect = useQuery({
    queryKey: ["detect"],
    queryFn: () =>
      api<components["schemas"]["Detection"][]>("/connections/detect", {}),
    enabled: bootstrap.data?.connections.length === 0,
  });
  const active = useQuery({
    queryKey: ["active"],
    queryFn: () => api<components["schemas"]["ActiveRun"][]>("/runs/active"),
  });
  const context = useQuery({
    queryKey: ["context", chatId, detail.data?.chat.current_leaf_id],
    queryFn: () =>
      api<components["schemas"]["ContextInfo"]>(
        "/chats/" + chatId + "/context",
      ),
    enabled: !!detail.data?.chat.model_id,
  });
  const runs = useRuns((s) => s.runs),
    chatRuns = Object.entries(runs).filter(([, r]) => r.chatId === chatId),
    runEntry = chatRuns.find(([, r]) => r.stage !== "done") ?? chatRuns.at(-1),
    running = Boolean(runEntry && runEntry[1].stage !== "done") || busy;
  const current: Model | undefined =
    models.data?.find(
      (m) =>
        m.connection_id ===
          (detail.data?.chat.connection_id ?? selected?.connection_id) &&
        m.model_id === (detail.data?.chat.model_id ?? selected?.model_id),
    ) ??
    (detail.data?.chat.connection_id && detail.data.chat.model_id
      ? {
          connection_id: detail.data.chat.connection_id,
          model_id: detail.data.chat.model_id,
          display_name:
            detail.data.messages
              .slice()
              .reverse()
              .find(
                (message) =>
                  message.model?.model_id === detail.data?.chat.model_id,
              )?.model?.display_name ?? detail.data.chat.model_id,
          loaded: null,
          params_defaults: {},
          chat_capable: true,
          hidden: false,
          embedding: false,
        }
      : selected
        ? { ...selected, loaded: null }
        : undefined);
  const {
    setFiles,
    effectiveFiles,
    waitingForTranscript,
    uploads,
    setUploads,
    uploadControllers,
    dragging,
    setDragging,
    dragDepth,
    audioExtensions,
    upload,
  } = useUploads({ query, bootstrap, current });
  useEffect(() => {
    if (models.data?.length) void import("@/components/chat/Markdown");
  }, [models.data]);
  useEffect(() => {
    const timer = setTimeout(() => setDebounced(search), 200);
    return () => clearTimeout(timer);
  }, [search]);
  useEffect(() => {
    if (models.data?.length && !selected) {
      setSelected(
        models.data.find(
          (m) =>
            m.model_id === bootstrap.data?.settings["default_model_id"] &&
            m.connection_id ===
              bootstrap.data?.settings["default_connection_id"],
        ) ?? models.data[0],
      );
      setWeb(Boolean(bootstrap.data?.settings["web.default_on"]));
    }
  }, [models.data, selected, bootstrap.data]);
  useEffect(() => {
    if (previousChat.current !== chatId && !chatId) {
      const choice = models.data?.find(
        (model) =>
          model.model_id === bootstrap.data?.settings.default_model_id &&
          model.connection_id ===
            bootstrap.data?.settings.default_connection_id,
      );
      if (choice) setSelected(choice);
      setDraftParams({});
      setDraftPrompt(null);
      setWeb(Boolean(bootstrap.data?.settings["web.default_on"]));
    }
    previousChat.current = chatId;
  }, [chatId, models.data, bootstrap.data]);
  useEffect(() => {
    if (!detail.data) return;
    for (const run of active.data ?? []) {
      if (run.chat_id === chatId) {
        const snapshot = detail.data.messages.find(
          (m) => m.id === run.assistant_message_id,
        );
        if (snapshot) attachRun(run.run_id, run.chat_id, snapshot, query);
      }
    }
  }, [active.data, detail.data, chatId, query]);
  useShortcuts({ navigate, ui, desktop });
  const refresh = () => {
    void query.invalidateQueries({ queryKey: ["chat", chatId] });
    void query.invalidateQueries({ queryKey: ["chats"] });
    void query.invalidateQueries({ queryKey: ["bootstrap"] });
    void query.invalidateQueries({ queryKey: ["models"] });
  };
  const mutate = async (url: string, body: unknown, method?: string) => {
    try {
      await api(url, body, method);
      refresh();
      return true;
    } catch (e) {
      toast.error(String(e));
      return false;
    }
  };
  const { onSend, regenerate, stop } = useSend({
    query,
    navigate,
    chatId,
    current,
    running,
    modelOperation,
    waitingForTranscript,
    detail,
    web,
    draftParams,
    draftPrompt,
    effectiveFiles,
    setFiles,
    bootstrap,
    runEntry,
    refresh,
    ...sendState,
  });
  const chatParams = detail.data?.chat.params ?? draftParams;
  const saveParams = (prompt: string | null, params: Params) => {
    if (chatId)
      void mutate(
        "/chats/" + chatId,
        { system_prompt: prompt, params },
        "PATCH",
      );
    else {
      setDraftParams(params);
      setDraftPrompt(prompt);
    }
  };
  const webBlocked =
    bootstrap.data?.settings["transcription.block_web"] !== false &&
    (effectiveFiles.some((file) => file.kind === "audio") ||
      uploads.some((upload) => !upload.failed) ||
      visiblePath(
        detail.data?.messages ?? [],
        detail.data?.chat.current_leaf_id ?? null,
      ).some((message) =>
        message.attachments?.some((file) => file.kind === "audio"),
      ));
  const composer = (
    <Composer
      suggestions={!chatId}
      audioExtensions={audioExtensions}
      model={current}
      disabled={!current || busy || !!loadingModel}
      running={running}
      onStop={stop}
      onSend={(text) => onSend(text)}
      error={sendError}
      files={effectiveFiles}
      uploads={uploads}
      transcriptionReady={Boolean(bootstrap.data?.features.transcription)}
      webBlocked={webBlocked}
      onCancelUpload={(id) => {
        uploadControllers.current.get(id)?.abort();
        setUploads((uploads) => uploads.filter((upload) => upload.id !== id));
      }}
      onAttach={(incoming) => void upload(incoming)}
      onRemove={(id) => {
        const remove = () => {
          setFiles((files) => files.filter((file) => file.id !== id));
          detachTranscription(id);
          useTranscripts.getState().remove(id);
        };
        if (effectiveFiles.find((file) => file.id === id)?.kind === "audio")
          void api(`/attachments/${id}`, undefined, "DELETE").then(
            remove,
            (error) => toast.error(String(error)),
          );
        else remove();
      }}
      context={
        current
          ? {
              used_tokens:
                (context.data?.used_tokens ?? 0) +
                effectiveFiles.reduce(
                  (total, a) =>
                    total +
                    (a.kind === "image"
                      ? 800
                      : a.kind === "audio"
                        ? (a.transcript?.token_estimate ?? 0)
                        : Math.round(a.bytes * 0.3)),
                  0,
                ),
              context_length: current.context_length ?? 8192,
            }
          : undefined
      }
      thinkValue={chatParams.reasoning as string | undefined}
      onThinkChange={(value) => {
        const p = { ...chatParams, reasoning: value };
        if (chatId) void mutate("/chats/" + chatId, { params: p }, "PATCH");
        else setDraftParams(p);
      }}
      web={detail.data?.chat.web_enabled ?? web}
      onWebChange={
        bootstrap.data?.features.web_search
          ? (value) => {
              setWeb(value);
              if (chatId)
                void mutate(
                  "/chats/" + chatId,
                  { web_enabled: value },
                  "PATCH",
                );
            }
          : undefined
      }
    />
  );
  const panel = (
    <LiveChatSettings
      drawer={phone && !wide}
      key={`${chatId ?? "new"}:${current?.connection_id}:${current?.model_id}`}
      chat={detail.data?.chat}
      draftParams={draftParams}
      draftPrompt={draftPrompt}
      model={current}
      onSave={saveParams}
      onDefaults={(params) => {
        if (current)
          void mutate(
            "/models/prefs",
            {
              connection_id: current.connection_id,
              model_id: current.model_id,
              params,
            },
            "PUT",
          );
      }}
      onContext={(length) => {
        if (current)
          void mutate(
            "/models/prefs",
            {
              connection_id: current.connection_id,
              model_id: current.model_id,
              context_length: length,
            },
            "PUT",
          );
      }}
    />
  );
  const menu = (chat: Chat) => (
    <ChatMenu chat={chat} ui={ui} mutate={mutate} setAction={setAction} />
  );
  const list = (
    <HistoryList
      search={search}
      setSearch={setSearch}
      history={history}
      historyItems={historyItems}
      chatId={chatId}
      menu={menu}
      ui={ui}
    />
  );
  let visible = visiblePath(
    detail.data?.messages ?? [],
    detail.data?.chat.current_leaf_id ?? null,
  );
  if (runEntry) {
    const live = runEntry[1].message;
    visible = visible.map((m) => (m.id === live.id ? live : m));
    if (!visible.some((m) => m.id === live.id)) visible.push(live);
  }
  const runId = runEntry?.[1].message.id;
  const all = useMemo(() => {
    const rows = [...(detail.data?.messages ?? [])];
    if (runId && !rows.some((m) => m.id === runId))
      rows.push({
        id: runId,
        chat_id: chatId!,
        role: "assistant",
        content: "",
        status: "streaming",
        created_at: "",
      });
    return rows;
  }, [detail.data?.messages, runId, chatId]);
  return (
    <div className="app-shell">
      <aside className="sidebar-desktop" data-collapsed={ui.collapsed}>
        <Sidebar collapsed={ui.collapsed} history={list} />
      </aside>
      <main
        className="app-main"
        onDragOver={(e) => e.preventDefault()}
        onDragEnter={(e) => {
          if (e.dataTransfer.types.includes("Files")) {
            dragDepth.current++;
            setDragging(true);
          }
        }}
        onDragLeave={() => {
          if (--dragDepth.current <= 0) {
            dragDepth.current = 0;
            setDragging(false);
          }
        }}
        onDrop={(e) => {
          e.preventDefault();
          dragDepth.current = 0;
          setDragging(false);
          void upload(Array.from(e.dataTransfer.files));
        }}
      >
        {dragging && (
          <div
            role="status"
            className="pointer-events-none absolute inset-4 z-40 flex items-center justify-center rounded-xl border border-brand bg-surface text-sm"
          >
            Drop images, text files or recordings
          </div>
        )}
        <header className="topbar">
          <div className="flex min-w-0 flex-1 items-center">
            {(!desktop || ui.collapsed) && (
              <IconButton
                label="Open sidebar"
                onClick={() =>
                  ui.set(desktop ? { collapsed: false } : { sidebar: true })
                }
              >
                <PanelLeftOpen />
              </IconButton>
            )}
            <ModelPicker
              state={models.isLoading ? "loading" : "ready"}
              models={models.data ?? []}
              connections={bootstrap.data?.connections}
              current={current}
              onChoose={(model) => {
                void changeModel(model);
              }}
              loadingModel={loadingModel}
              onModelAction={(model) =>
                model.loaded ? operateModel(model, true) : changeModel(model)
              }
            />
          </div>
          <span className="hidden max-w-64 truncate text-xs text-fg-3 md:block">
            {detail.data?.chat.title ?? ""}
          </span>
          <IconButton
            label="Chat settings"
            onClick={() => ui.set({ panel: !ui.panel })}
          >
            <SlidersHorizontal />
          </IconButton>
          {detail.data && menu(detail.data.chat)}
        </header>
        {bootstrap.isError ? (
          <div role="alert" className="m-auto max-w-md p-6">
            <h1 className="text-lg font-medium">Can't reach Workbench</h1>
            <p className="my-4 text-sm text-fg-2">{String(bootstrap.error)}</p>
            <Button onClick={() => void bootstrap.refetch()}>Try again</Button>
          </div>
        ) : bootstrap.data?.connections.length === 0 ? (
          <Welcome
            detections={detect.data}
            error={detect.isError}
            onAdd={(base_url) =>
              void mutate("/connections", { kind: "ollama", base_url })
            }
            onRetry={() => void detect.refetch()}
            onSettings={() =>
              ui.set({
                settings: true,
                settingsPane: "Connections",
                sidebar: false,
              })
            }
          />
        ) : !chatId ? (
          <EmptyState ui={ui} composer={composer} />
        ) : (
          <>
            <LiveThread
              selectedModel={current}
              messages={visible}
              all={all}
              stage={runEntry?.[1].stage}
              steps={runEntry?.[1].steps}
              scrollRef={scroll}
              onAboveBottomChange={setAbove}
              onRegenerate={(m, force) => void regenerate(m, force)}
              onRegenerateWith={(m, model) => void regenerate(m, false, model)}
              models={models.data ?? []}
              connections={bootstrap.data?.connections ?? []}
              onSettings={(pane) =>
                ui.set({
                  settings: true,
                  ...(pane ? { settingsPane: pane } : {}),
                })
              }
              onChatSettings={() => ui.set({ panel: true })}
              onNew={() => navigate("/")}
              onEdit={(m, text) => onSend(text, m.parent_id ?? null)}
              onBranch={(id) =>
                void mutate(
                  "/chats/" + chatId,
                  { current_leaf_id: latestLeaf(all, id) },
                  "PATCH",
                )
              }
              sources={{
                ...detail.data?.sources,
                ...(runEntry
                  ? {
                      [runEntry[1].message.id]:
                        runEntry[1].sources ??
                        detail.data?.sources?.[runEntry[1].message.id] ??
                        [],
                    }
                  : {}),
              }}
              reads={detail.data?.reads}
            />
            {pending && <p className="mx-6 text-sm text-fg-2">{pending}</p>}
            <div className="composer-row relative" data-testid="composer-row">
              {above && (
                <Button
                  aria-label="Scroll to bottom"
                  className="absolute -top-12 right-6 size-11 rounded-full border border-line bg-surface text-fg"
                  onClick={() =>
                    scroll.current?.scrollTo({
                      top: scroll.current.scrollHeight,
                      behavior: "smooth",
                    })
                  }
                >
                  <ArrowDown />
                </Button>
              )}
              {composer}
            </div>
          </>
        )}
      </main>
      <Panels ui={ui} wide={wide} phone={phone} panel={panel} list={list} />
      <SettingsDialog
        searchEnabled={Boolean(bootstrap.data?.features.web_search)}
        renderPane={(pane) => (
          <LiveSettingsPane
            pane={pane}
            bootstrap={bootstrap.data}
            models={models.data ?? []}
            onModelAction={(model) =>
              model.loaded ? operateModel(model, true) : changeModel(model)
            }
          />
        )}
      />
      <CommandPalette
        open={ui.command}
        onOpenChange={(command) => ui.set({ command })}
        onChat={(chat) => navigate("/c/" + chat.id)}
        searchDisabled={webBlocked || !bootstrap.data?.features.web_search}
        actions={{
          newChat: () => navigate("/"),
          switchModel: () =>
            window.dispatchEvent(new Event("workbench:choose-model")),
          toggleSearch: () => {
            if (webBlocked || !bootstrap.data?.features.web_search) return;
            const next = !(detail.data?.chat.web_enabled ?? web);
            setWeb(next);
            if (chatId)
              void mutate("/chats/" + chatId, { web_enabled: next }, "PATCH");
          },
          chatSettings: () => ui.set({ panel: true }),
          settings: () => ui.set({ settings: true }),
          shortcuts: () =>
            ui.set({ settings: true, settingsPane: "Shortcuts" }),
          toggleTheme: () =>
            ui.set({
              theme:
                resolvedTheme(
                  ui.theme,
                  matchMedia("(prefers-color-scheme: dark)").matches,
                ) === "dark"
                  ? "light"
                  : "dark",
            }),
        }}
      />
      <ChatActionDialog
        key={String(action?.chat.id) + String(action?.kind)}
        action={action}
        onClose={() => setAction(null)}
        onApply={(title) => {
          if (action) {
            if (action.kind === "delete") {
              void mutate("/chats/" + action.chat.id, undefined, "DELETE");
              if (chatId === action.chat.id) navigate("/");
            } else void mutate("/chats/" + action.chat.id, { title }, "PATCH");
            setAction(null);
          }
        }}
      />
    </div>
  );
}
