import { failureCopy, failureDetail } from "@/lib/errors";
import {
  useEffect,
  useLayoutEffect,
  useRef,
  useState,
  type Dispatch,
  type SetStateAction,
  type RefObject,
} from "react";
import type { NavigateFunction } from "react-router";
import type { QueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import {
  api,
  ApiError,
  type Attachment,
  type Bootstrap,
  type Chat,
  type Detail,
  type Message,
  type Model,
  type Params,
  type RunResponse,
} from "@/lib/api";
import { errorCopy } from "@/lib/errors";
import { attachRun } from "@/lib/sse";
import { useFreshRows } from "@/stores/fresh";
export function useSendState(chatId?: string) {
  const [busy, setBusy] = useState(false),
    [pending, setPending] = useState<Message | null>(null);
  const currentChat = useRef(chatId);
  currentChat.current = chatId;
  const [sendError, setSendError] = useState("");
  const stopRequested = useRef(false);
  const restoreComposerFocus = useRef(false);
  useLayoutEffect(() => {
    if (restoreComposerFocus.current) {
      restoreComposerFocus.current = false;
      document
        .querySelector<HTMLTextAreaElement>(".composer textarea")
        ?.focus();
    }
  }, [chatId]);
  useEffect(() => {
    setPending(null);
    setSendError("");
  }, [chatId]);
  return {
    currentChat,
    busy,
    setBusy,
    pending,
    setPending,
    sendError,
    setSendError,
    stopRequested,
    restoreComposerFocus,
  };
}
export function useSend({
  query,
  navigate,
  chatId,
  current,
  running,
  modelOperation,
  waitingForTranscript,
  detail,
  web,
  library = false,
  libraryScope = null,
  draftParams,
  draftPrompt,
  draftOverridden = false,
  effectiveFiles,
  setFiles,
  bootstrap,
  runEntry,
  refresh,
  busy,
  setBusy,
  setPending,
  setSendError,
  stopRequested,
  restoreComposerFocus,
  currentChat,
}: {
  query: QueryClient;
  navigate: NavigateFunction;
  chatId?: string;
  current?: Model;
  running: boolean;
  modelOperation: RefObject<boolean>;
  waitingForTranscript: boolean;
  detail: { data?: Detail };
  web: boolean;
  library?: boolean;
  libraryScope?: import("@/components/chat/LibraryControl").Scope;
  draftParams: Params;
  draftPrompt: string | null;
  draftOverridden?: boolean;
  effectiveFiles: Attachment[];
  setFiles: Dispatch<SetStateAction<Attachment[]>>;
  bootstrap: { data?: Bootstrap };
  runEntry?: [string, { stage: string; message: Message }];
  refresh: () => void;
} & ReturnType<typeof useSendState>) {
  const onSend = async (text: string, parent?: string | null) => {
    if (
      !current ||
      busy ||
      running ||
      modelOperation.current ||
      waitingForTranscript
    )
      return false;
    setSendError("");
    stopRequested.current = false;
    setBusy(true);
    const optimisticId = "pending-" + crypto.randomUUID();
    if (chatId && parent === undefined) {
      useFreshRows.getState().add(optimisticId);
      setPending({
        id: optimisticId,
        chat_id: chatId,
        role: "user",
        content: text,
        status: "complete",
        attachments: effectiveFiles,
        created_at: new Date().toISOString(),
      });
    }
    try {
      let id = chatId;
      let chat = detail.data?.chat;
      if (!id) {
        chat = await api<Chat>("/chats", {
          connection_id: current.connection_id,
          model_id: current.model_id,
          web_enabled: web,
          ...(draftOverridden ? { preset_id: null } : {}),
        });
        id = chat.id;
        if (library || libraryScope !== null)
          await api(
            "/chats/" + id,
            { library_enabled: library, library_scope: libraryScope },
            "PATCH",
          );
        if (draftOverridden)
          await api(
            "/chats/" + id,
            { params: draftParams, system_prompt: draftPrompt },
            "PATCH",
          );
      }
      const response = await api<RunResponse>("/chats/" + id + "/messages", {
        content: text,
        parent_id:
          parent === undefined ? (chat?.current_leaf_id ?? null) : parent,
        attachment_ids: effectiveFiles.map((f) => f.id),
        web: library ? false : (chat?.web_enabled ?? web),
        ...(library ? { library: true } : {}),
      });
      // Commit the confirmed rows atomically before removing the optimistic row.
      const rows = [response.user_message, response.assistant_message].filter(
        (row): row is Message => Boolean(row),
      );
      if (response.user_message && (!chatId || parent !== undefined))
        useFreshRows.getState().add(response.user_message.id);
      useFreshRows.getState().add(response.assistant_message.id);
      // Existing chats need an atomic optimistic replacement. New chats retain
      // their original authoritative-fetch timing and composer handoff.
      if (chatId)
        query.setQueryData<Detail>(["chat", id], (previous) => {
          const confirmed =
            previous ?? (chat ? { chat, messages: [] } : undefined);
          if (!confirmed) return confirmed;
          return {
            ...confirmed,
            chat: {
              ...confirmed.chat,
              current_leaf_id: response.assistant_message.id,
            },
            messages: [
              ...confirmed.messages.filter(
                (message) => !rows.some((row) => row.id === message.id),
              ),
              ...rows,
            ],
          };
        });
      if (!chatId && currentChat.current === chatId) {
        restoreComposerFocus.current =
          document.activeElement?.matches(".composer textarea") ?? false;
        // Mount the new-chat composer/query before a fast SSE run can finish.
        // A deferred route left the old composer accepting a draft that was
        // then discarded by its handoff, and could detach the run too early.
        navigate("/c/" + id, { flushSync: true });
      }
      if (
        currentChat.current === chatId ||
        (!chatId && currentChat.current === id)
      )
        setFiles((files) =>
          files.filter(
            (file) => !effectiveFiles.some((sent) => sent.id === file.id),
          ),
        );
      void query.invalidateQueries({ queryKey: ["pending-recordings"] });
      setPending(null);
      attachRun(response.run_id, id, response.assistant_message, query);
      if (stopRequested.current) {
        await api(`/runs/${response.run_id}/cancel`, {});
        stopRequested.current = false;
      }
      void query.invalidateQueries({ queryKey: ["chat", id] });
      void query.invalidateQueries({ queryKey: ["chats"] });
      if (bootstrap.data?.settings["new_chat_model"] !== "fixed")
        void api(
          "/settings",
          {
            default_connection_id: current.connection_id,
            default_model_id: current.model_id,
          },
          "PATCH",
        );
      return true;
    } catch (e) {
      if (currentChat.current === chatId)
        setSendError(
          errorCopy(
            e instanceof ApiError ? e.code : "unknown",
            e instanceof Error ? e.message : String(e),
            current,
            bootstrap.data?.connections.find(
              (c) => c.id === current.connection_id,
            ),
          ),
        );
      setPending(null);
      return false;
    } finally {
      useFreshRows.getState().clear(optimisticId);
      setBusy(false);
    }
  };
  const regenerate = async (message: Message, force = false, model?: Model) => {
    if (running) return;
    stopRequested.current = false;
    setBusy(true);
    try {
      const response = await api<RunResponse>(
        "/messages/" + message.id + "/regenerate",
        {
          force_web: force,
          ...(model
            ? { connection_id: model.connection_id, model_id: model.model_id }
            : {}),
        },
      );
      useFreshRows.getState().add(response.assistant_message.id);
      attachRun(
        response.run_id,
        message.chat_id,
        response.assistant_message,
        query,
      );
      if (stopRequested.current) {
        await api(`/runs/${response.run_id}/cancel`, {});
        stopRequested.current = false;
      }
      refresh();
    } catch (e) {
      toast.error(failureCopy(e), { description: failureDetail(e) });
    } finally {
      setBusy(false);
    }
  };
  const stop = () => {
    document.querySelector<HTMLTextAreaElement>(".composer textarea")?.focus();
    if (runEntry && runEntry[1].stage !== "done")
      void api("/runs/" + runEntry[0] + "/cancel", {}).catch(() =>
        toast.error("Couldn’t stop the response. Try again."),
      );
    else if (busy) stopRequested.current = true;
  };
  return { onSend, regenerate, stop };
}
